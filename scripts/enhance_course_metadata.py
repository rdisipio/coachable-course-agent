#!/usr/bin/env python3
"""
Update existing course catalog with proper duration and level information
by fetching details from individual course pages.
"""

import json
import sys
from pathlib import Path
import time
sys.path.append('scripts')

from scrapers.coursera_scraper import CourseraScraper

def update_course_metadata():
    """Update existing courses with detailed metadata from course pages"""
    catalog_path = "data/course_catalog_esco.json"
    
    # Load current catalog
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print(f"🔍 Found {len(catalog['courses'])} courses to update")
    
    # Initialize scraper
    scraper = CourseraScraper()
    
    updated_count = 0
    failed_count = 0
    
    # Process each course
    for i, course in enumerate(catalog['courses']):
        print(f"\n📚 Processing course {i+1}/{len(catalog['courses'])}: {course['title'][:50]}...")
        
        # Skip if we already have duration and level
        has_duration = course.get('duration_hours', 0) > 0
        has_level = course.get('level', 'unknown') != 'unknown'
        
        if has_duration and has_level:
            print(f"  ✅ Already has duration ({course['duration_hours']}h) and level ({course['level']})")
            continue
        
        try:
            # Get detailed information from course page
            details = scraper.get_course_details(course['url'])
            
            if details:
                updated = False
                
                # Update duration if we got it and don't have it
                if details.get('duration') and not has_duration:
                    # Parse duration to hours using the base scraper method
                    duration_hours = scraper._parse_duration(details['duration'])
                    if duration_hours > 0:
                        course['duration_hours'] = duration_hours
                        print(f"  ✅ Updated duration: {details['duration']} → {duration_hours}h")
                        updated = True
                
                # Update level if we got it and don't have it
                if details.get('level') and details['level'] != 'unknown' and not has_level:
                    standardized_level = scraper._standardize_level(details['level'])
                    course['level'] = standardized_level
                    print(f"  ✅ Updated level: {details['level']} → {standardized_level}")
                    updated = True
                
                # Update provider if we got a better one
                if details.get('provider') and details['provider'] != 'Coursera':
                    course['provider'] = details['provider']
                    print(f"  ✅ Updated provider: {details['provider']}")
                    updated = True
                
                # Update rating if we got it
                if details.get('rating'):
                    course['rating'] = details['rating']
                    print(f"  ✅ Updated rating: {details['rating']}")
                    updated = True
                
                if updated:
                    updated_count += 1
                else:
                    print(f"  ⚠️  No new information found")
            else:
                print(f"  ❌ Failed to get details")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_count += 1
        
        # Add delay to avoid rate limiting
        time.sleep(2)
        
        # Save progress every 10 courses
        if (i + 1) % 10 == 0:
            print(f"\n💾 Saving progress... ({updated_count} updated, {failed_count} failed)")
            with open(catalog_path + ".tmp", 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    # Update metadata
    catalog['metadata']['enhanced_at'] = "2025-08-28T00:00:00"
    catalog['metadata']['enhancement_stats'] = {
        'courses_updated': updated_count,
        'courses_failed': failed_count,
        'total_processed': len(catalog['courses'])
    }
    
    # Save final catalog
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    # Clean up temp file
    temp_file = Path(catalog_path + ".tmp")
    if temp_file.exists():
        temp_file.unlink()
    
    print(f"\n🎉 Enhancement complete!")
    print(f"   📊 Courses updated: {updated_count}")
    print(f"   ❌ Courses failed: {failed_count}")
    print(f"   📈 Success rate: {updated_count / len(catalog['courses']) * 100:.1f}%")
    
    return updated_count, failed_count

if __name__ == "__main__":
    print("🔧 Starting course metadata enhancement...")
    print("⚠️  This will fetch details from each course page and may take a while...")
    
    # Confirmation prompt
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    update_course_metadata()
