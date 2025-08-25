#!/usr/bin/env python3
"""
Course Scraper CLI
Scrapes courses from multiple platforms and stores them as JSON.

Usage:
    python scripts/course_scraper.py --topic "data science" --count 10 --sources coursera,udemy,edx
    python scripts/course_scraper.py --topic "machine learning" --count 5 --sources coursera
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
    parser.add_argument('--count', type=int, default=10, help='Number of courses to scrape per platform')
    parser.add_argument('--sources', default='coursera,udemy,edx', 
                       help='Comma-separated list of platforms (coursera,udemy,edx)')
    parser.add_argument('--output', help='Output JSON file (default: data/scraped_courses/raw_data/courses_TOPIC_TIMESTAMP.json)')
    parser.add_argument('--process-llm', action='store_true', 
                       help='Process scraped data with LLM for standardization')
    
    args = parser.parse_args()
    
    # Parse sources
    sources = [s.strip() for s in args.sources.split(',')]
    
    # Validate sources
    invalid_sources = [s for s in sources if s not in SCRAPER_MAP]
    if invalid_sources:
        print(f"Error: Invalid sources: {invalid_sources}")
        print(f"Available sources: {list(SCRAPER_MAP.keys())}")
        return 1
    
    # Set output file
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = args.topic.replace(' ', '_').replace('/', '_')
        args.output = f"data/scraped_courses/raw_data/courses_{safe_topic}_{timestamp}.json"
    
    print(f"🔍 Scraping {args.count} courses about '{args.topic}' from: {', '.join(sources)}")
    
    all_courses = []
    
    # Scrape from each platform
    for source in sources:
        print(f"\n📚 Scraping {source}...")
        try:
            scraper = SCRAPER_MAP[source]()
            courses = scraper.search_courses(args.topic, args.count)
            
            # Add source info to each course
            for course in courses:
                course['source_platform'] = source
                course['scraped_at'] = datetime.now().isoformat()
            
            all_courses.extend(courses)
            print(f"✅ Found {len(courses)} courses from {source}")
            
        except Exception as e:
            print(f"❌ Error scraping {source}: {e}")
            continue
    
    if not all_courses:
        print("❌ No courses found!")
        return 1
    
    # Process with LLM if requested
    if args.process_llm:
        print(f"\n🤖 Processing {len(all_courses)} courses with LLM...")
        try:
            processor = LLMProcessor()
            all_courses = processor.standardize_courses(all_courses)
            print("✅ LLM processing complete")
        except Exception as e:
            print(f"⚠️  LLM processing failed: {e}")
            print("Continuing with raw scraped data...")
    
    # Save to JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    output_data = {
        'metadata': {
            'topic': args.topic,
            'sources': sources,
            'total_courses': len(all_courses),
            'scraped_at': datetime.now().isoformat(),
            'processed_with_llm': args.process_llm
        },
        'courses': all_courses
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(all_courses)} courses to {args.output}")
    
    # Summary stats
    by_platform = {}
    for course in all_courses:
        platform = course.get('source_platform', 'unknown')
        by_platform[platform] = by_platform.get(platform, 0) + 1
    
    print("\n📊 Summary:")
    for platform, count in by_platform.items():
        print(f"  {platform}: {count} courses")


if __name__ == '__main__':
    exit(main())
