#!/usr/bin/env python3

import sys
sys.path.append('/home/ec2-user/environment/coachable-course-agent')

from coachable_course_agent.justifier_chain import justify_recommendations
from coachable_course_agent.memory_store import load_user_profile

def test_feedback_interpretation():
    user_id = "rdisipio"
    profile = load_user_profile(user_id)
    
    print("=== User Profile ===")
    print(f"Goal: {profile.get('goal')}")
    print(f"Feedback Log: {profile.get('feedback_log', [])}")
    
    # Test courses - mix of beginner and advanced
    test_courses = [
        {
            "course_id": "advanced_pm_001",
            "title": "Advanced Product Strategy for Senior Professionals",
            "provider": "ProductU",
            "description": "Advanced-level strategic product management for experienced professionals. Covers portfolio management, strategic roadmapping, and executive stakeholder management.",
            "level": "Advanced",
            "format": "Online",
            "skills": "strategic planning, portfolio management, stakeholder management",
            "duration_hours": 40
        },
        {
            "course_id": "beginner_pm_001", 
            "title": "Introduction to Product Management Basics",
            "provider": "LearnPM",
            "description": "Beginner-friendly introduction to product management fundamentals. Perfect for those new to the field.",
            "level": "Beginner",
            "format": "Online",
            "skills": "product management basics, requirements gathering",
            "duration_hours": 20
        },
        {
            "course_id": "intermediate_pm_001",
            "title": "Product Analytics and Data-Driven Decisions",
            "provider": "DataCourse",
            "description": "Intermediate course on using data and analytics in product management decision-making.",
            "level": "Intermediate", 
            "format": "Online",
            "skills": "data analysis, product metrics, analytics",
            "duration_hours": 30
        }
    ]
    
    print("\n=== Test Courses ===")
    for course in test_courses:
        print(f"- {course['title']} ({course['level']})")
    
    print("\n=== Getting Recommendations ===")
    recommendations = justify_recommendations(profile, test_courses)
    
    print("\n=== Recommendations with Justifications ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Justification: {rec['justification']}")
        
        # Check if it mentions beginner inappropriately
        justification_lower = rec['justification'].lower()
        if 'beginner' in justification_lower and 'avoid' not in justification_lower and 'not' not in justification_lower:
            print(f"   ⚠️  WARNING: May be incorrectly interpreting beginner feedback!")

if __name__ == "__main__":
    test_feedback_interpretation()
