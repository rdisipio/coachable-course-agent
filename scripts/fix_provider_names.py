#!/usr/bin/env python3
"""
Fix doubled letter issue in provider names in the course catalog.
"""

import json
import re
from pathlib import Path

def fix_provider_name(provider):
    """Fix provider names that have doubled letters at the beginning."""
    if not provider:
        return provider
    
    # Pattern to match doubled letters at the beginning: "AAmazon" -> "Amazon"
    pattern = r'^([A-Z])\1(.+)$'
    match = re.match(pattern, provider)
    
    if match:
        first_letter = match.group(1)
        rest = match.group(2)
        return first_letter + rest
    
    return provider

def main():
    # Load the course catalog
    catalog_path = Path("data/course_catalog_esco.json")
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print(f"Found {len(catalog['courses'])} courses in catalog")
    
    # Track changes
    changes = {}
    courses_changed = 0
    
    # Fix provider names
    for course in catalog['courses']:
        original_provider = course.get('provider', '')
        fixed_provider = fix_provider_name(original_provider)
        
        if original_provider != fixed_provider:
            if original_provider not in changes:
                changes[original_provider] = fixed_provider
            course['provider'] = fixed_provider
            courses_changed += 1
    
    print(f"\nFixed {courses_changed} courses")
    print(f"Provider name changes:")
    for old, new in sorted(changes.items()):
        print(f"  '{old}' -> '{new}'")
    
    # Save the updated catalog
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated catalog saved to {catalog_path}")

if __name__ == "__main__":
    main()
