#!/usr/bin/env python3
"""
Course Consolidation and ESCO Skills Matching

This script:
1. Loads all raw scraped course data
2. Deduplicates across platforms (exact + semantic duplicates)
3. Matches course descriptions to ESCO skills
4. Generates a consolidated course catalog with ESCO-linked skills
5. Optionally processes with LLM for enhanced descriptions
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import glob
import re
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
            
    def load_all_courses(self) -> List[Dict]:
        """Load courses from all JSON files in data directory"""
        all_courses = []
        
        # Get all JSON files from various sources
        json_patterns = [
            "data/*.json",
            "data/scraped_courses/*.json", 
            "data/coursesity_*.json",
            "data/mit_*.json",
            "data/harvard_*.json"
        ]
        
        json_files = []
        for pattern in json_patterns:
            json_files.extend(glob.glob(pattern))
        
        print(f"📁 Found {len(json_files)} JSON files to process")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Handle different JSON structures
                if isinstance(data, list):
                    all_courses.extend(data)
                elif isinstance(data, dict):
                    if 'courses' in data:
                        all_courses.extend(data['courses'])
                    elif 'items' in data:
                        all_courses.extend(data['items'])
                    else:
                        # Assume the dict itself is a course
                        all_courses.append(data)
                        
                print(f"📚 Loaded {len(data.get('courses', data) if isinstance(data, dict) else data)} courses from {json_file}")
                
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
                
        print(f"📚 Total raw courses loaded: {len(all_courses)}")
        return all_courses
        
    def normalize_title(self, title: str) -> str:
        """Normalize title for semantic duplicate detection"""
        if not title:
            return ""
            
        # Convert to lowercase
        normalized = title.lower().strip()
        
        # Remove common course prefixes/suffixes
        patterns_to_remove = [
            r'\b(introduction to|intro to|basics of|fundamentals of|getting started with)\b',
            r'\b(course|tutorial|training|class|lesson)\b',
            r'\b(complete|comprehensive|full|total)\b',
            r'\b(beginner|intermediate|advanced|basic)\b',
            r'\b(guide|handbook|masterclass)\b',
            r'\b(2024|2023|2022|2021|2020)\b',  # Remove years
            r'\s*[-–—]\s*.*$',  # Remove everything after dash
            r'\s*\([^)]*\)\s*',  # Remove content in parentheses
            r'\s*\[[^\]]*\]\s*',  # Remove content in brackets
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, ' ', normalized, flags=re.IGNORECASE)
        
        # Normalize whitespace and punctuation
        normalized = re.sub(r'[^\w\s]', ' ', normalized)  # Remove punctuation
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        normalized = normalized.strip()
        
        return normalized
        
    def deduplicate_courses(self, courses: List[Dict]) -> List[Dict]:
        """Remove exact duplicates and semantic duplicates (same/similar titles)"""
        print("🔍 Advanced deduplication (exact + semantic duplicates)...")
        
        # Step 1: Remove exact duplicates (same title, provider, url)
        exact_duplicates = defaultdict(list)
        for course in courses:
            title = course.get('title', '').strip()
            provider = clean_provider_name(course.get('provider', '')).strip()
            url = course.get('url', '').strip()
            exact_key = f"{title}|||{provider}|||{url}"
            exact_duplicates[exact_key].append(course)
            
        after_exact = []
        exact_removed = 0
        
        for exact_key, course_group in exact_duplicates.items():
            if len(course_group) == 1:
                after_exact.append(course_group[0])
            else:
                best_course = self.select_best_course(course_group)
                after_exact.append(best_course)
                exact_removed += len(course_group) - 1
                
        print(f"   Removed {exact_removed} exact duplicates")
        
        # Step 2: Group by normalized title for semantic duplicate detection
        title_groups = defaultdict(list)
        for course in after_exact:
            normalized_title = self.normalize_title(course.get('title', ''))
            title_groups[normalized_title].append(course)
            
        deduplicated = []
        semantic_removed = 0
        
        for normalized_title, course_group in title_groups.items():
            if len(course_group) == 1:
                deduplicated.append(course_group[0])
            else:
                # Multiple courses with same normalized title - keep the best one
                best_course = self.select_best_course(course_group)
                deduplicated.append(best_course)
                semantic_removed += len(course_group) - 1
                
                # Log semantic duplicates being removed
                providers = [clean_provider_name(c.get('provider', '')) for c in course_group]
                print(f"   🎯 Merged {len(course_group)} semantic duplicates: '{course_group[0].get('title', '')}' from {', '.join(providers[:3])}")
                
        print(f"   Removed {semantic_removed} semantic duplicates")
        print(f"✅ {len(deduplicated)} unique courses remain (advanced deduplication)")
        return deduplicated
        
    def select_best_course(self, course_group: List[Dict]) -> Dict:
        """Select the best course from a group of similar courses"""
        # Provider reputation scores (higher is better)
        provider_scores = {
            'stanford': 100, 'mit': 100, 'harvard': 100, 'berkeley': 95, 'princeton': 95,
            'yale': 95, 'cambridge': 95, 'oxford': 95, 'caltech': 95, 'cmu': 90,
            'coursera': 85, 'edx': 85, 'udacity': 80, 'khan academy': 75, 'youtube': 60,
            'udemy': 70, 'pluralsight': 75, 'linkedin learning': 70, 'alison': 50,
            'futurelearn': 70, 'skillshare': 65
        }
        
        def course_score(course):
            score = 0
            
            # Provider reputation (most important for duplicates)
            provider = clean_provider_name(course.get('provider', '')).lower()
            for key, value in provider_scores.items():
                if key in provider:
                    score += value * 10  # Multiply by 10 to make this the dominant factor
                    break
            else:
                score += 40  # Default score for unknown providers
            
            # Content quality indicators
            if course.get('description'):
                score += min(len(course['description']) / 10, 50)  # Up to 50 points for description length
            if course.get('rating'):
                score += course['rating'] * 20  # Up to 100 points for rating
            if course.get('enrollment_count'):
                score += min(course['enrollment_count'] / 1000, 30)  # Up to 30 points for popularity
            if course.get('duration_hours'):
                score += 10  # 10 points for having duration info
                
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
            "tools:",
            "frameworks:",
            "programming languages:",
            "topics covered:",
            "includes:",
            "covers:"
        ]
        
        description_lower = description.lower()
        skills = []
        
        # Look for skill sections
        for indicator in skill_indicators:
            if indicator in description_lower:
                start_idx = description_lower.find(indicator)
                # Get text after the indicator (next 200 chars)
                skill_text = description[start_idx + len(indicator):start_idx + len(indicator) + 200]
                
                # Split by common delimiters
                for delimiter in [',', ';', '•', '\n', '|']:
                    if delimiter in skill_text:
                        skills.extend([s.strip() for s in skill_text.split(delimiter) if s.strip()])
                        break
        
        # Clean and filter skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip().rstrip('.,;')
            if len(skill) > 2 and len(skill) < 50:  # Reasonable skill name length
                cleaned_skills.append(skill)
        
        return cleaned_skills[:10]  # Limit to 10 skills max
        
    def match_esco_skills(self, courses: List[Dict]) -> List[Dict]:
        """Match courses to ESCO skills using vectorstore similarity"""
        print("🎯 Matching courses to ESCO skills...")
        
        if not self.esco_vectorstore:
            print("❌ ESCO vectorstore not available, skipping skill matching")
            return courses
            
        enhanced_courses = []
        
        for course in tqdm(courses, desc="Matching ESCO skills"):
            try:
                # Prepare text for matching
                title = course.get('title', '')
                description = course.get('description', '')
                match_text = f"{title} {description}"
                
                # Extract skills from description
                extracted_skills = self.extract_skills_from_description(description)
                
                # Match to ESCO using the vectorstore
                esco_skills = match_to_esco([match_text], self.esco_vectorstore, top_k=5)
                
                # Combine extracted and ESCO skills
                all_skills = list(set(extracted_skills + esco_skills))
                
                # Add ESCO skills to course
                course['esco_skills'] = all_skills[:8]  # Limit to 8 skills total
                enhanced_courses.append(course)
                
            except Exception as e:
                print(f"❌ Error matching skills for '{course.get('title', '')}': {e}")
                course['esco_skills'] = []
                enhanced_courses.append(course)
                
        print(f"✅ Matched ESCO skills for {len(enhanced_courses)} courses")
        return enhanced_courses
        
    def save_consolidated_catalog(self, courses: List[Dict], output_file="data/course_catalog_esco.json"):
        """Save the consolidated course catalog"""
        
        # Prepare metadata
        catalog_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_courses": len(courses),
                "data_sources": ["coursesity", "mit", "harvard", "youtube", "khan_academy", "others"],
                "deduplication": "advanced (exact + semantic)",
                "skills_matching": "ESCO vectorstore",
                "version": "1.1.0"
            },
            "courses": courses
        }
        
        # Save to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved consolidated catalog with {len(courses)} courses to {output_file}")
        
        # Print summary statistics
        providers = defaultdict(int)
        skill_counts = []
        
        for course in courses:
            provider = clean_provider_name(course.get('provider', 'Unknown'))
            providers[provider] += 1
            skill_counts.append(len(course.get('esco_skills', [])))
            
        print("\n📊 Catalog Statistics:")
        print(f"   Total courses: {len(courses)}")
        print(f"   Unique providers: {len(providers)}")
        print(f"   Average skills per course: {sum(skill_counts)/len(skill_counts):.1f}")
        
        print("\n🏢 Top providers:")
        for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {provider}: {count} courses")
            
    def run_consolidation(self):
        """Run the full consolidation pipeline"""
        print("🚀 Starting course consolidation pipeline...")
        
        # Load all courses
        raw_courses = self.load_all_courses()
        
        # Deduplicate
        deduplicated_courses = self.deduplicate_courses(raw_courses)
        
        # Match ESCO skills
        enhanced_courses = self.match_esco_skills(deduplicated_courses)
        
        # Save final catalog
        self.save_consolidated_catalog(enhanced_courses)
        
        print("✅ Course consolidation completed successfully!")


if __name__ == "__main__":
    consolidator = CourseConsolidator()
    consolidator.run_consolidation()
