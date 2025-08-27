#!/usr/bin/env python3
"""
Course Catalog Cleanup Script

This script:
1. Removes duplicate skills from the same course
2. Filters out obvious false positive skill matches
3. Improves the quality of ESCO skill associations
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# False positive patterns to filter out
FALSE_POSITIVE_PATTERNS = [
    # Forestry/agriculture false positives from ML terms
    "forest", "forestry", "agricultural", "farming", "crop", "livestock",
    "plant", "soil", "harvest", "irrigation", "pesticide",
    
    # Physical/manual labor false positives
    "manual handling", "operate hand tools", "physical strength",
    "lift heavy weights", "manual dexterity",
    
    # Food/restaurant false positives
    "food preparation", "cook", "kitchen", "restaurant", "catering",
    "food safety", "menu planning",
    
    # Vehicle/transportation false positives  
    "drive vehicles", "operate motor", "transport goods", "logistics coordination",
    
    # Construction/building false positives
    "construction work", "building maintenance", "electrical installations",
    "plumbing", "carpentry", "masonry",
    
    # Medical/healthcare false positives (unless medical course)
    "patient care", "medical procedures", "clinical", "nursing", "surgery",
    
    # Legal/administrative false positives (unless relevant course)
    "legal procedures", "court proceedings", "administrative tasks",
    
    # Financial false positives (unless finance course)
    "handle money", "banking procedures", "accounting records"
]

# Topic-specific filtering: skills that don't make sense for certain topics
TOPIC_SKILL_FILTERS = {
    "machine learning": ["forest", "forestry", "agricultural", "manual", "physical"],
    "data science": ["forest", "agricultural", "manual", "construction"],
    "programming": ["forest", "agricultural", "food", "restaurant", "construction"],
    "web development": ["forest", "agricultural", "medical", "construction"],
    "artificial intelligence": ["forest", "agricultural", "manual", "physical"],
    "computer science": ["forest", "agricultural", "food", "medical", "construction"],
    "software": ["forest", "agricultural", "food", "construction", "medical"]
}

def is_false_positive(skill_name, course_title="", course_description=""):
    """Check if a skill is likely a false positive"""
    skill_lower = skill_name.lower()
    title_lower = course_title.lower()
    desc_lower = course_description.lower()
    
    # Check against general false positive patterns
    for pattern in FALSE_POSITIVE_PATTERNS:
        if pattern in skill_lower:
            # Allow if the course is actually about that domain
            if pattern in title_lower or pattern in desc_lower:
                continue
            return True
    
    # Check topic-specific filters
    for topic, filters in TOPIC_SKILL_FILTERS.items():
        if topic in title_lower or topic in desc_lower:
            for filter_word in filters:
                if filter_word in skill_lower:
                    return True
    
    return False

def clean_course_catalog(input_file, output_file):
    """Clean up the course catalog"""
    print("🧹 Starting course catalog cleanup...")
    
    with open(input_file, 'r') as f:
        catalog = json.load(f)
    
    total_courses = len(catalog['courses'])
    total_skills_before = 0
    total_skills_after = 0
    duplicates_removed = 0
    false_positives_removed = 0
    
    print(f"📚 Processing {total_courses} courses...")
    
    for course in catalog['courses']:
        title = course.get('title', '')
        description = course.get('description', '')
        original_skills = course.get('skills', [])
        total_skills_before += len(original_skills)
        
        # Track unique skills by both name and ESCO URI to catch more duplicates
        unique_skills = {}
        skill_names_seen = set()
        
        for skill in original_skills:
            skill_name = skill.get('name', '')
            esco_uri = skill.get('esco_uri', '')
            
            # Skip false positives
            if is_false_positive(skill_name, title, description):
                false_positives_removed += 1
                continue
            
            # Skip duplicates by ESCO URI or exact skill name
            if esco_uri in unique_skills or skill_name in skill_names_seen:
                duplicates_removed += 1
                continue
            
            unique_skills[esco_uri] = skill
            skill_names_seen.add(skill_name)
        
        # Update course with cleaned skills
        course['skills'] = list(unique_skills.values())
        total_skills_after += len(course['skills'])
    
    # Update metadata
    catalog['metadata']['cleaned_at'] = "2025-08-27T17:45:00"
    catalog['metadata']['cleanup_stats'] = {
        'total_skills_before': total_skills_before,
        'total_skills_after': total_skills_after,
        'duplicates_removed': duplicates_removed,
        'false_positives_removed': false_positives_removed,
        'cleanup_rate': round((duplicates_removed + false_positives_removed) / total_skills_before * 100, 2)
    }
    
    # Save cleaned catalog
    with open(output_file, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"✅ Cleanup completed!")
    print(f"   📊 Skills before: {total_skills_before}")
    print(f"   📊 Skills after: {total_skills_after}")
    print(f"   🔄 Duplicates removed: {duplicates_removed}")
    print(f"   ❌ False positives removed: {false_positives_removed}")
    print(f"   📈 Cleanup rate: {catalog['metadata']['cleanup_stats']['cleanup_rate']}%")
    print(f"   💾 Saved to: {output_file}")

def main():
    input_file = "data/course_catalog_esco.json"
    output_file = "data/course_catalog_esco_cleaned.json"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    clean_course_catalog(input_file, output_file)

if __name__ == "__main__":
    main()
