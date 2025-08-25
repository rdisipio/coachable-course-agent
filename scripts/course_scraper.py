#!/usr/bin/env python3
"""
Course Scraper CLI
Scrapes courses from a single platform and stores them as JSON.

Usage:
    python scripts/course_scraper.py --topic "data science" --platform coursera --count 10
    python scripts/course_scraper.py --topic "machine learning" --platform udemy --count 5
    python scripts/course_scraper.py --topic "web development" --platform edx --count 3
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict

from scrapers.coursera_scraper import CourseraScraper
from scrapers.udemy_scraper import UdemyScraper
from scrapers.edx_scraper import EdxScraper
from llm_processor import LLMProcessor


SCRAPER_MAP = {
    'coursera': CourseraScraper,
    'udemy': UdemyScraper,
    'edx': EdxScraper
}


def main():
    parser = argparse.ArgumentParser(description='Scrape courses from online platforms')
    parser.add_argument('--topic', required=True, help='Course topic to search for')
    parser.add_argument('--count', type=int, default=10, help='Number of courses to scrape')
    parser.add_argument('--platform', required=True, choices=['coursera', 'udemy', 'edx'],
                       help='Platform to scrape from (coursera, udemy, or edx)')
    parser.add_argument('--process-llm', action='store_true', 
                       help='Process scraped data with LLM for standardization')
    
    args = parser.parse_args()
    
    # Get the platform
    platform = args.platform
    
    # Validate platform
    if platform not in SCRAPER_MAP:
        print(f"Error: Invalid platform: {platform}")
        print(f"Available platforms: {list(SCRAPER_MAP.keys())}")
        return 1
    
    print(f"🔍 Scraping {args.count} courses about '{args.topic}' from {platform}")
    
    courses = []
    
    # Scrape from the platform
    print(f"\n📚 Scraping {platform}...")
    try:
        scraper = SCRAPER_MAP[platform]()
        courses = scraper.search_courses(args.topic, args.count)
        
        # Add source info to each course
        for course in courses:
            course['source_platform'] = platform
            course['scraped_at'] = datetime.now().isoformat()
        
        print(f"✅ Found {len(courses)} courses from {platform}")
        
    except Exception as e:
        print(f"❌ Error scraping {platform}: {e}")
        return 1
    
    if not courses:
        print("❌ No courses found!")
        return 1
    
    # Remove duplicates based on URL
    print(f"\n🔍 Removing duplicates from {len(courses)} courses...")
    seen_urls = set()
    unique_courses = []
    duplicates_removed = 0
    
    for course in courses:
        course_url = course.get('url', '').strip()
        if course_url and course_url not in seen_urls:
            seen_urls.add(course_url)
            unique_courses.append(course)
        else:
            duplicates_removed += 1
    
    if duplicates_removed > 0:
        print(f"✅ Removed {duplicates_removed} duplicate courses")
        print(f"📚 {len(unique_courses)} unique courses remaining")
    else:
        print("✅ No duplicates found")
    
    courses = unique_courses
    
    # Process with LLM if requested
    if args.process_llm:
        print(f"\n🤖 Processing {len(courses)} courses with LLM...")
        try:
            processor = LLMProcessor()
            courses = processor.standardize_courses(courses)
            print("✅ LLM processing complete")
        except Exception as e:
            print(f"⚠️  LLM processing failed: {e}")
            print("Continuing with raw scraped data...")
    
    # Save to JSON
    os.makedirs("data/scraped_courses/raw_data", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = args.topic.replace(' ', '_').replace('/', '_')
    output_file = f"data/scraped_courses/raw_data/{platform}_{safe_topic}_{timestamp}.json"
    
    output_data = {
        'metadata': {
            'topic': args.topic,
            'platform': platform,
            'total_courses': len(courses),
            'scraped_at': datetime.now().isoformat(),
            'processed_with_llm': args.process_llm
        },
        'courses': courses
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(courses)} courses to {output_file}")
    
    # Summary stats
    print(f"\n📊 Summary:")
    print(f"  {platform}: {len(courses)} courses")
    print(f"\n🎯 Total: {len(courses)} courses saved")


if __name__ == '__main__':
    exit(main())
