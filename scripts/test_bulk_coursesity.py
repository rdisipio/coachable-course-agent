#!/usr/bin/env python3
"""
Test bulk Coursesity scraping with a smaller set first.
"""

import subprocess
import time
import random
from pathlib import Path

# Test with just a few high-volume topics first
TEST_TOPICS = [
    "python",
    "javascript", 
    "machine learning",
    "web development",
    "data science",
    "digital marketing",
    "graphic design",
    "photography",
    "fitness",
    "cooking"
]

def run_scraper(platform, topic, count=50):
    """Run the course scraper for a specific platform and topic with high count"""
    try:
        print(f"\n{'='*60}")
        print(f"Scraping {platform} for '{topic}' (target: {count} courses)")
        print(f"{'='*60}")
        
        cmd = [
            "pipenv", "run", "python", "scripts/course_scraper.py",
            "--platform", platform,
            "--topic", topic,
            "--count", str(count)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print(f"✅ Successfully scraped {platform} for '{topic}'")
            # Count courses from output
            if "courses found" in result.stdout:
                import re
                match = re.search(r'(\d+) courses found', result.stdout)
                if match:
                    print(f"   📚 Found {match.group(1)} courses")
            print(result.stdout)
        else:
            print(f"❌ Error scraping {platform} for '{topic}': {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Exception scraping {platform} for '{topic}': {e}")
        return False

def main():
    print("🧪 Testing bulk Coursesity scraping with sample topics...")
    print(f"📋 Will test {len(TEST_TOPICS)} topics with 50 courses each")
    print(f"🎯 Test target: {len(TEST_TOPICS) * 50} = {len(TEST_TOPICS) * 50:,} additional courses")
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, topic in enumerate(TEST_TOPICS, 1):
        print(f"\n📊 Progress: {i}/{len(TEST_TOPICS)} topics")
        
        success = run_scraper("coursesity", topic, count=50)
        
        if success:
            successful_scrapes += 1
        else:
            failed_scrapes += 1
            
        # Add delay between scrapes to be respectful
        if i < len(TEST_TOPICS):  # Don't delay after the last one
            delay = random.uniform(3, 7)
            print(f"⏱️  Waiting {delay:.1f}s before next scrape...")
            time.sleep(delay)
    
    print(f"\n🎉 Test scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"❌ Failed scrapes: {failed_scrapes}")
    print(f"📈 Success rate: {successful_scrapes/(successful_scrapes+failed_scrapes)*100:.1f}%")

if __name__ == "__main__":
    main()
