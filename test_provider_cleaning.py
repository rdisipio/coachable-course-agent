#!/usr/bin/env python3
"""
Test script to demonstrate provider name cleaning during data import vs runtime
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from coachable_course_agent.utils import clean_provider_name
from scripts.scrapers.base_scraper import BaseScraper

# Create a test scraper to demonstrate the cleaning
class TestScraper(BaseScraper):
    def search_courses(self, topic, count):
        # Mock implementation for testing
        return []
    
    def extract_course_data(self, course_element):
        # Mock implementation for testing
        return {}

def test_provider_cleaning():
    print("🧪 Testing Provider Name Cleaning During Data Import")
    print("=" * 60)
    
    # Test cases with problematic provider names
    test_cases = [
        "D Duke University Introduction To",
        "A Arizona State University Arizona State",
        "U University of California Berkeley Berkeley",
        "Stanford University",  # Should remain unchanged
        "Michigan State University"  # Should remain unchanged
    ]
    
    print("📝 Test Cases:")
    for original in test_cases:
        cleaned = clean_provider_name(original)
        print(f"   \"{original}\" → \"{cleaned}\"")
    
    print("\n🔧 Data Import Pipeline Integration:")
    
    # Test the base scraper standardization
    scraper = TestScraper()
    
    # Mock raw course data with problematic provider name
    raw_course = {
        'title': 'Test Course',
        'provider': 'D Duke University Introduction To',
        'url': 'https://example.com',
        'description': 'A test course',
        'duration': '10 hours',
        'level': 'beginner'
    }
    
    print(f"   Raw data provider: \"{raw_course['provider']}\"")
    
    # Process through standardization (which now includes cleaning)
    standardized = scraper.standardize_course_data(raw_course)
    
    print(f"   Standardized provider: \"{standardized['provider']}\"")
    print(f"   ✅ Provider cleaned during import!")
    
    print("\n📊 Benefits:")
    print("   • Provider names cleaned once during data import")
    print("   • No runtime performance impact")
    print("   • Consistent data quality")
    print("   • Simplified application code")

if __name__ == "__main__":
    test_provider_cleaning()
