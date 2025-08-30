#!/usr/bin/env python3
"""
Test Academic Scraper - Limited Topics
"""

import subprocess
import time
from datetime import datetime

def run_scraper(platform, topic, count=3):
    """Run the scraper for a specific platform and topic"""
    cmd = [
        'pipenv', 'run', 'python', 'scripts/course_scraper.py',
        '--platform', platform,
        '--topic', topic,
        '--count', str(count)
    ]
    
    print(f"🚀 Scraping {count} '{topic}' courses from {platform}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ Successfully scraped {topic} from {platform}")
            return True
        else:
            print(f"❌ Error scraping {topic} from {platform}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception scraping {topic} from {platform}: {e}")
        return False

def main():
    """Test scraping function"""
    
    # Test with a few key topics
    topics = [
        'machine learning',
        'data science', 
        'programming',
        'mathematics'
    ]
    
    platforms = ['mit', 'harvard']
    courses_per_topic = 3
    
    print(f"🧪 Test scraping for {len(topics)} topics across {len(platforms)} platforms")
    
    for topic in topics:
        for platform in platforms:
            success = run_scraper(platform, topic, courses_per_topic)
            time.sleep(1)  # Short delay
    
    print(f"\n🎉 Test scraping completed!")

if __name__ == "__main__":
    main()
