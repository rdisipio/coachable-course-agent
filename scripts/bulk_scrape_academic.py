#!/usr/bin/env python3
"""
Bulk Course Scraper for MIT and Harvard
Scrapes multiple topics from MIT OCW and Harvard PLL to expand the catalog
"""

import subprocess
import time
from datetime import datetime

def run_scraper(platform, topic, count=5):
    """Run the scraper for a specific platform and topic"""
    cmd = [
        'pipenv', 'run', 'python', 'scripts/course_scraper.py',
        '--platform', platform,
        '--topic', topic,
        '--count', str(count)
    ]
    
    print(f"🚀 Scraping {count} '{topic}' courses from {platform}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ Successfully scraped {topic} from {platform}")
            return True
        else:
            print(f"❌ Error scraping {topic} from {platform}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout scraping {topic} from {platform}")
        return False
    except Exception as e:
        print(f"❌ Exception scraping {topic} from {platform}: {e}")
        return False

def main():
    """Main bulk scraping function"""
    
    # Define topics to scrape
    topics = [
        'computer science',
        'programming',
        'machine learning',
        'artificial intelligence', 
        'data science',
        'mathematics',
        'physics',
        'economics',
        'business',
        'finance',
        'statistics',
        'algorithms',
        'software engineering'
    ]
    
    platforms = ['mit', 'harvard']
    courses_per_topic = 8  # Increased to get more courses
    
    total_scraped = 0
    successful_scrapes = 0
    
    print(f"🎯 Starting bulk scraping for {len(topics)} topics across {len(platforms)} platforms")
    print(f"📊 Target: {len(topics)} × {len(platforms)} × {courses_per_topic} = {len(topics) * len(platforms) * courses_per_topic} courses")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for topic in topics:
        for platform in platforms:
            success = run_scraper(platform, topic, courses_per_topic)
            if success:
                successful_scrapes += 1
                total_scraped += courses_per_topic
            
            # Rate limiting between requests
            time.sleep(2)
    
    print(f"\n🎉 Bulk scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"📚 Estimated courses scraped: ~{total_scraped}")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
