#!/usr/bin/env python3
"""
Monitor bulk scraping progress by counting new course files.
"""

import time
import subprocess
from pathlib import Path

def count_new_courses():
    """Count courses scraped today"""
    try:
        # Count files from today
        result = subprocess.run([
            "find", "data", "-name", "coursesity_*_20250830_*", "-exec", "jq", ".courses | length", "{}", ";"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            counts = [int(line.strip()) for line in result.stdout.strip().split('\n') if line.strip()]
            return sum(counts), len(counts)
        return 0, 0
    except:
        return 0, 0

def main():
    print("📊 Monitoring bulk Coursesity scraping progress...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            total_courses, file_count = count_new_courses()
            print(f"📈 Progress: {file_count} topics scraped, {total_courses:,} new courses")
            
            if file_count > 0:
                avg_per_file = total_courses / file_count
                print(f"📊 Average: {avg_per_file:.1f} courses per topic")
                
                if file_count < 233:  # Total topics we're targeting
                    remaining = 233 - file_count
                    estimated_total = total_courses + (remaining * avg_per_file)
                    print(f"🎯 Estimated final total: {estimated_total:,.0f} new courses")
            
            print("-" * 50)
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
        total_courses, file_count = count_new_courses()
        print(f"Final count: {file_count} topics, {total_courses:,} courses")

if __name__ == "__main__":
    main()
