#!/usr/bin/env python3
"""
Bulk scrape many courses from Coursesity to dramatically expand the catalog.
"""

import subprocess
import time
import random
from pathlib import Path

# Comprehensive list of topics to scrape with high course counts
TOPICS = [
    # Programming & Development (high volume topics)
    "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
    "web development", "frontend", "backend", "full stack", "react", "angular", "vue",
    "node.js", "django", "flask", "spring", "laravel", "express",
    "mobile development", "android", "ios", "flutter", "react native", "kotlin", "swift",
    "game development", "unity", "unreal", "godot", "pygame",
    "software engineering", "programming", "coding", "algorithms", "data structures",
    
    # Data & AI (expanding current categories)
    "data science", "machine learning", "artificial intelligence", "deep learning",
    "data analysis", "data visualization", "statistics", "pandas", "numpy", "scipy",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "big data", "spark", "hadoop", "kafka", "elasticsearch",
    "sql", "mysql", "postgresql", "mongodb", "database",
    
    # Cloud & DevOps
    "cloud computing", "aws", "azure", "google cloud", "gcp",
    "devops", "docker", "kubernetes", "jenkins", "terraform",
    "linux", "bash", "shell scripting", "automation",
    "microservices", "api", "rest", "graphql",
    
    # Cybersecurity & Networking
    "cybersecurity", "ethical hacking", "penetration testing", "network security",
    "information security", "cryptography", "security", "hacking",
    "networking", "cisco", "ccna", "comptia",
    
    # Business & Management
    "project management", "agile", "scrum", "kanban", "pmp",
    "business analysis", "product management", "digital marketing",
    "social media marketing", "seo", "sem", "content marketing",
    "email marketing", "affiliate marketing", "e-commerce",
    "entrepreneurship", "startup", "business strategy", "leadership",
    "management", "operations", "supply chain", "logistics",
    
    # Finance & Economics
    "finance", "accounting", "financial analysis", "investment",
    "trading", "forex", "cryptocurrency", "blockchain", "bitcoin",
    "economics", "statistics", "econometrics", "financial modeling",
    "excel", "powerbi", "tableau", "quickbooks",
    
    # Design & Creative
    "graphic design", "web design", "ui design", "ux design",
    "photoshop", "illustrator", "figma", "sketch", "canva",
    "video editing", "after effects", "premiere pro", "davinci resolve",
    "3d modeling", "blender", "maya", "3ds max", "autocad",
    "animation", "motion graphics", "photography",
    
    # Health & Wellness
    "fitness", "nutrition", "yoga", "meditation", "mental health",
    "personal development", "productivity", "time management",
    "healthcare", "nursing", "medical", "pharmacy",
    
    # Languages & Communication
    "english", "spanish", "french", "german", "chinese", "japanese",
    "communication", "public speaking", "writing", "copywriting",
    "content creation", "blogging", "journalism",
    
    # Sciences & Engineering
    "mathematics", "calculus", "algebra", "geometry", "statistics",
    "physics", "chemistry", "biology", "engineering",
    "mechanical engineering", "electrical engineering", "civil engineering",
    "chemical engineering", "environmental science",
    
    # Arts & Humanities
    "music", "guitar", "piano", "singing", "music production",
    "art", "drawing", "painting", "history", "philosophy",
    "psychology", "sociology", "political science",
    
    # Technology & IT
    "it support", "computer repair", "hardware", "networking",
    "system administration", "windows", "office", "microsoft office",
    "google workspace", "excel", "powerpoint", "word",
    
    # Miscellaneous High-Volume Topics
    "personal finance", "real estate", "insurance", "law",
    "cooking", "gardening", "diy", "crafts", "woodworking",
    "electronics", "robotics", "iot", "raspberry pi", "arduino"
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
        else:
            print(f"❌ Error scraping {platform} for '{topic}': {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Exception scraping {platform} for '{topic}': {e}")
        return False

def main():
    print("🚀 Starting bulk Coursesity scraping for catalog expansion...")
    print(f"📋 Will scrape {len(TOPICS)} topics with 50 courses each")
    print(f"🎯 Target: {len(TOPICS) * 50} = {len(TOPICS) * 50:,} additional courses")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent.parent
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, topic in enumerate(TOPICS, 1):
        print(f"\n📊 Progress: {i}/{len(TOPICS)} topics")
        
        success = run_scraper("coursesity", topic, count=50)
        
        if success:
            successful_scrapes += 1
        else:
            failed_scrapes += 1
            
        # Add delay between scrapes to be respectful
        if i < len(TOPICS):  # Don't delay after the last one
            delay = random.uniform(3, 7)
            print(f"⏱️  Waiting {delay:.1f}s before next scrape...")
            time.sleep(delay)
    
    print(f"\n🎉 Bulk scraping completed!")
    print(f"✅ Successful scrapes: {successful_scrapes}")
    print(f"❌ Failed scrapes: {failed_scrapes}")
    print(f"📈 Success rate: {successful_scrapes/(successful_scrapes+failed_scrapes)*100:.1f}%")
    print(f"\n💡 Next steps:")
    print(f"   1. Run consolidation: pipenv run python scripts/consolidate_courses.py")
    print(f"   2. Check final catalog size: jq '.courses | length' data/course_catalog_esco.json")

if __name__ == "__main__":
    main()
