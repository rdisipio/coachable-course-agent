#!/usr/bin/env python3
"""
Course Data Pipeline Orchestrator

This script orchestrates the complete course data pipeline:
1. Course scraping (optional - can use existing data)
2. Course consolidation and deduplication
3. ESCO skills matching
4. Automatic cleanup (duplicates + false positives)
5. Quality validation and reporting

Ensures consistency and never forgets cleanup steps.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.consolidate_courses import CourseConsolidator
from scripts.clean_course_catalog import clean_course_catalog

class CoursePipelineOrchestrator:
    """Orchestrates the complete course data pipeline"""
    
    def __init__(self, scrape_new=False, platforms=None, topics=None):
        self.scrape_new = scrape_new
        self.platforms = platforms or ["coursera"]
        self.topics = topics
        self.pipeline_start = datetime.now()
        
    def step_1_scraping(self):
        """Step 1: Scrape new course data (optional)"""
        if not self.scrape_new:
            print("⏭️  Step 1: Skipping scraping (using existing data)")
            return True
            
        print("🚀 Step 1: Starting course scraping...")
        
        try:
            # Build scraping command
            cmd = ["pipenv", "run", "python", "scripts/master_scraper.py"]
            
            if self.platforms:
                for platform in self.platforms:
                    cmd.extend(["--platform", platform])
            
            if self.topics:
                for topic in self.topics:
                    cmd.extend(["--topic", topic])
            
            print(f"   Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Scraping failed: {result.stderr}")
                return False
                
            print("✅ Step 1: Course scraping completed")
            return True
            
        except Exception as e:
            print(f"❌ Step 1 failed: {e}")
            return False
    
    def step_2_consolidation(self):
        """Step 2: Consolidate and deduplicate courses"""
        print("🔄 Step 2: Starting course consolidation...")
        
        try:
            consolidator = CourseConsolidator("data/scraped_courses/raw_data")
            consolidator.run_consolidation()
            print("✅ Step 2: Course consolidation completed")
            return True
            
        except Exception as e:
            print(f"❌ Step 2 failed: {e}")
            return False
    
    def step_3_cleanup(self):
        """Step 3: Clean up duplicates and false positives"""
        print("🧹 Step 3: Starting catalog cleanup...")
        
        try:
            input_file = "data/course_catalog_esco.json"
            temp_file = "data/course_catalog_esco_temp_cleaned.json"
            
            # Run cleanup to temporary file first
            clean_course_catalog(input_file, temp_file)
            
            # Replace original with cleaned version
            os.rename(temp_file, input_file)
            
            print("✅ Step 3: Catalog cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Step 3 failed: {e}")
            return False
    
    def step_4_validation(self):
        """Step 4: Validate final dataset quality"""
        print("🔍 Step 4: Validating dataset quality...")
        
        try:
            with open("data/course_catalog_esco.json", 'r') as f:
                catalog = json.load(f)
            
            total_courses = len(catalog['courses'])
            total_skills = sum(len(course.get('skills', [])) for course in catalog['courses'])
            
            # Quality checks
            courses_without_skills = sum(1 for course in catalog['courses'] if not course.get('skills'))
            avg_skills_per_course = total_skills / total_courses if total_courses > 0 else 0
            
            # Domain coverage
            domains = set()
            for course in catalog['courses']:
                title = course.get('title', '').lower()
                desc = course.get('description', '').lower()
                text = f"{title} {desc}"
                
                if any(word in text for word in ['machine learning', 'data science', 'programming', 'ai']):
                    domains.add('Computer Science & AI')
                elif any(word in text for word in ['business', 'management', 'leadership', 'marketing']):
                    domains.add('Business & Management')
                elif any(word in text for word in ['design', 'ux', 'architecture', 'interior']):
                    domains.add('Design & Architecture')
                elif any(word in text for word in ['environment', 'sustainability', 'climate', 'renewable']):
                    domains.add('Environmental Studies')
                elif any(word in text for word in ['philosophy', 'ethics', 'political', 'journalism']):
                    domains.add('Humanities & Arts')
                elif any(word in text for word in ['physics', 'chemistry', 'biology', 'mathematics']):
                    domains.add('Sciences')
                elif any(word in text for word in ['engineering', 'civil', 'electrical']):
                    domains.add('Engineering')
                elif any(word in text for word in ['psychology', 'medical', 'health']):
                    domains.add('Health & Social Sciences')
            
            quality_report = {
                'total_courses': total_courses,
                'total_skills': total_skills,
                'avg_skills_per_course': round(avg_skills_per_course, 2),
                'courses_without_skills': courses_without_skills,
                'domain_coverage': len(domains),
                'domains_found': sorted(list(domains))
            }
            
            # Update metadata with quality report
            catalog['metadata']['pipeline_completed_at'] = self.pipeline_start.isoformat()
            catalog['metadata']['quality_report'] = quality_report
            
            # Save updated catalog
            with open("data/course_catalog_esco.json", 'w') as f:
                json.dump(catalog, f, indent=2)
            
            print("✅ Step 4: Quality validation completed")
            print(f"   📊 Final dataset: {total_courses} courses, {total_skills} skills")
            print(f"   📈 Average skills per course: {avg_skills_per_course:.2f}")
            print(f"   🌐 Domain coverage: {len(domains)} domains")
            print(f"   📝 Domains: {', '.join(sorted(domains))}")
            
            if courses_without_skills > 0:
                print(f"   ⚠️  Warning: {courses_without_skills} courses have no skills")
            
            return True
            
        except Exception as e:
            print(f"❌ Step 4 failed: {e}")
            return False
    
    def run_pipeline(self):
        """Run the complete pipeline"""
        print("=" * 60)
        print("🏗️  COURSE DATA PIPELINE ORCHESTRATOR")
        print("=" * 60)
        print(f"Started at: {self.pipeline_start}")
        print()
        
        steps = [
            ("Course Scraping", self.step_1_scraping),
            ("Course Consolidation", self.step_2_consolidation),
            ("Catalog Cleanup", self.step_3_cleanup),
            ("Quality Validation", self.step_4_validation)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Pipeline failed at: {step_name}")
                return False
            print()
        
        pipeline_end = datetime.now()
        duration = pipeline_end - self.pipeline_start
        
        print("=" * 60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"Output: data/course_catalog_esco.json")
        print()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Course Data Pipeline Orchestrator")
    parser.add_argument("--scrape", action="store_true", 
                       help="Scrape new course data (default: use existing)")
    parser.add_argument("--platform", action="append", dest="platforms",
                       help="Platform(s) to scrape from (can use multiple times)")
    parser.add_argument("--topic", action="append", dest="topics",
                       help="Topic(s) to scrape (can use multiple times)")
    
    args = parser.parse_args()
    
    # Validate prerequisites
    if not Path("data/esco_chroma").exists():
        print("❌ ESCO vectorstore not found. Please run: python scripts/load_esco.py")
        sys.exit(1)
    
    if args.scrape and not any(Path("data/scraped_courses/raw_data").glob("*.json")):
        if not args.platforms:
            args.platforms = ["coursera"]  # Default platform
    
    # Run pipeline
    orchestrator = CoursePipelineOrchestrator(
        scrape_new=args.scrape,
        platforms=args.platforms,
        topics=args.topics
    )
    
    success = orchestrator.run_pipeline()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
