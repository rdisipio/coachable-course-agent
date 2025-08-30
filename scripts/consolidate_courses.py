#!/usr/bin/env python3
"""
Course Consolidation and ESCO Skills Matching

This script:
1. Loads all raw scraped course data
2. Deduplicates across platforms 
3. Matches course descriptions to ESCO skills
4. Generates a consolidated course catalog with ESCO-linked skills
5. Optionally processes with LLM for enhanced descriptions
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

from tqdm import tqdm
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from coachable_course_agent.esco_matcher import match_to_esco
from coachable_course_agent.utils import clean_provider_name


class CourseConsolidator:
    """Consolidates scraped courses and matches ESCO skills"""
    
    def __init__(self, raw_data_dir="data/scraped_courses/raw_data"):
        self.raw_data_dir = Path(raw_data_dir)
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.esco_vectorstore = None
        self.load_esco_vectorstore()
        
    def load_esco_vectorstore(self):
        """Load ESCO skills vectorstore for skill matching"""
        try:
            self.esco_vectorstore = Chroma(
                persist_directory="data/esco_chroma",
                embedding_function=self.embedding_model
            )
            print("✅ Loaded ESCO skills vectorstore")
        except Exception as e:
            print(f"❌ Failed to load ESCO vectorstore: {e}")
            print("   Make sure you've run: pipenv run python scripts/load_esco.py")
            
    def load_all_raw_courses(self) -> List[Dict]:
        """Load all courses from raw JSON files"""
        all_courses = []
        
        json_files = list(self.raw_data_dir.glob("*.json"))
        print(f"📂 Found {len(json_files)} raw data files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                courses = data.get('courses', [])
                print(f"   {json_file.name}: {len(courses)} courses")
                all_courses.extend(courses)
                
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
                
        print(f"📚 Total raw courses loaded: {len(all_courses)}")
        return all_courses
        
    def deduplicate_courses(self, courses: List[Dict]) -> List[Dict]:
        """Remove only exact duplicate courses (same title, provider, and URL)"""
        print("🔍 Minimal deduplication (exact duplicates only)...")
        
        # Group by (title, provider, url) for exact duplicate detection
        exact_duplicates = defaultdict(list)
        for course in courses:
            # Create exact match key
            title = course.get('title', '').strip()
            provider = clean_provider_name(course.get('provider', '')).strip()
            url = course.get('url', '').strip()
            
            # Only remove if all three match exactly
            exact_key = f"{title}|||{provider}|||{url}"
            exact_duplicates[exact_key].append(course)
            
        deduplicated = []
        duplicates_removed = 0
        
        for exact_key, course_group in exact_duplicates.items():
            if len(course_group) == 1:
                deduplicated.append(course_group[0])
            else:
                # Multiple identical courses - keep the best one
                best_course = self.select_best_course(course_group)
                deduplicated.append(best_course)
                duplicates_removed += len(course_group) - 1
                
                # Log exact duplicates being removed
                if len(course_group) > 2:
                    title, provider, url = exact_key.split('|||')
                    print(f"   � Merged {len(course_group)} exact duplicates: '{title}' from {provider}")
                
        print(f"   Removed {duplicates_removed} exact duplicates")
        print(f"✅ {len(deduplicated)} unique courses remain (minimal deduplication)")
        return deduplicated
        
    def select_best_course(self, course_group: List[Dict]) -> Dict:
        """Select the best course from a group of similar courses"""
        # Prefer courses with more complete information
        def course_score(course):
            score = 0
            if course.get('description'):
                score += len(course['description'])
            if course.get('rating'):
                score += course['rating'] * 100
            if course.get('enrollment_count'):
                score += min(course['enrollment_count'] / 1000, 100)
            if course.get('duration_hours'):
                score += 10
            return score
            
        return max(course_group, key=course_score)
        
    def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract potential skills from course description"""
        if not description:
            return []
            
        # Common skill indicators
        skill_indicators = [
            "skills you'll gain:",
            "skills:",
            "you will learn:",
            "learn:",
            "technologies:",
            "tools:"
        ]
        
        description_lower = description.lower()
        
        # Look for skills sections
        for indicator in skill_indicators:
            if indicator in description_lower:
                # Extract text after the indicator
                parts = description_lower.split(indicator)
                if len(parts) > 1:
                    skills_text = parts[1].split('.')[0]  # Until next sentence
                    # Split by common delimiters
                    skills = [s.strip() for s in skills_text.replace(',', '|').replace(';', '|').split('|')]
                    return [s for s in skills if s and len(s) > 2]
                    
        # Fallback: extract common technology terms
        tech_terms = []
        common_techs = ['python', 'javascript', 'java', 'sql', 'html', 'css', 'react', 'node.js', 'aws', 'docker', 'kubernetes']
        for tech in common_techs:
            if tech in description_lower:
                tech_terms.append(tech)
                
        return tech_terms
        
    def match_esco_skills(self, course: Dict) -> List[Dict]:
        """Match course skills to ESCO taxonomy"""
        if not self.esco_vectorstore:
            return []
            
        # Extract potential skills from various fields
        skill_candidates = []
        
        # From explicit skills field
        if course.get('skills'):
            skill_candidates.extend(course['skills'])
            
        # From description
        description = course.get('description', '')
        extracted_skills = self.extract_skills_from_description(description)
        skill_candidates.extend(extracted_skills)
        
        # From title (sometimes contains technologies)
        title = course.get('title', '')
        for tech in ['Python', 'JavaScript', 'Java', 'SQL', 'AWS', 'Docker']:
            if tech.lower() in title.lower():
                skill_candidates.append(tech)
                
        if not skill_candidates:
            return []
            
        # Match to ESCO
        try:
            esco_matches = match_to_esco(skill_candidates, self.esco_vectorstore)
            # Convert to our format
            matched_skills = []
            for match in esco_matches:
                matched_skills.append({
                    "name": match.get("preferredLabel", ""),
                    "esco_uri": match.get("conceptUri", ""),
                    "description": match.get("description", "")
                })
            return matched_skills
        except Exception as e:
            print(f"   Warning: ESCO matching failed for course {course.get('title', 'Unknown')}: {e}")
            return []
            
    def consolidate_courses(self, courses: List[Dict]) -> List[Dict]:
        """Process courses and add ESCO skills"""
        print("🎯 Matching courses to ESCO skills...")
        
        consolidated = []
        for course in tqdm(courses, desc="Processing courses"):
            # Match ESCO skills
            esco_skills = self.match_esco_skills(course)
            
            # Clean provider name during consolidation
            provider = clean_provider_name(course.get('provider', ''))
            
            # Create consolidated course record
            consolidated_course = {
                "id": course.get('id'),
                "title": course.get('title'),
                "provider": provider,  # Use cleaned provider name
                "url": course.get('url'),
                "description": course.get('description'),
                "duration_hours": course.get('duration_hours', 0),
                "level": course.get('level', 'unknown'),
                "format": course.get('format', 'online'),
                "price": course.get('price', 0.0),
                "rating": course.get('rating'),
                "enrollment_count": course.get('enrollment_count'),
                "language": course.get('language', 'en'),
                "certificate": course.get('certificate', False),
                "instructor": course.get('instructor', ''),
                "skills": esco_skills,  # ESCO-matched skills
                "source_platform": course.get('source_platform'),
                "consolidated_at": datetime.now().isoformat()
            }
            
            consolidated.append(consolidated_course)
            
        return consolidated
        
    def save_consolidated_catalog(self, courses: List[Dict], output_file="data/course_catalog_esco.json"):
        """Save consolidated course catalog"""
        catalog = {
            "metadata": {
                "total_courses": len(courses),
                "consolidated_at": datetime.now().isoformat(),
                "esco_matched": True,
                "sources": list(set([c.get('source_platform') for c in courses if c.get('source_platform')]))
            },
            "courses": courses
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(catalog, f, indent=2)
            
        print(f"✅ Saved consolidated catalog to {output_file}")
        print(f"   📊 {len(courses)} courses with ESCO skills")
        
    def run_consolidation(self, auto_cleanup=True):
        """Run the full consolidation pipeline"""
        print("🚀 Starting course consolidation pipeline...\n")
        
        # Step 1: Load all raw courses
        raw_courses = self.load_all_raw_courses()
        if not raw_courses:
            print("❌ No courses found to consolidate")
            return
            
        # Step 2: Deduplicate
        unique_courses = self.deduplicate_courses(raw_courses)
        
        # Step 3: Match ESCO skills
        consolidated_courses = self.consolidate_courses(unique_courses)
        
        # Step 4: Save catalog
        self.save_consolidated_catalog(consolidated_courses)
        
        # Step 5: Auto-cleanup (if enabled)
        if auto_cleanup:
            print("\n🧹 Running automatic cleanup...")
            try:
                from scripts.clean_course_catalog import clean_course_catalog
                input_file = "data/course_catalog_esco.json"
                temp_file = "data/course_catalog_esco_temp.json"
                
                clean_course_catalog(input_file, temp_file)
                
                # Replace original with cleaned version
                import os
                os.rename(temp_file, input_file)
                print("✅ Automatic cleanup completed")
                
            except Exception as e:
                print(f"⚠️  Cleanup failed (continuing anyway): {e}")
        
        print("\n🎉 Course consolidation completed!")
        

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Consolidate scraped courses and match ESCO skills")
    parser.add_argument("--raw-data-dir", default="data/scraped_courses/raw_data",
                       help="Directory containing raw scraped course JSON files")
    parser.add_argument("--output", default="data/course_catalog_esco.json",
                       help="Output file for consolidated catalog")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Skip automatic cleanup step")
    
    args = parser.parse_args()
    
    consolidator = CourseConsolidator(args.raw_data_dir)
    consolidator.run_consolidation(auto_cleanup=not args.no_cleanup)


if __name__ == "__main__":
    main()
