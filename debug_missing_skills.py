#!/usr/bin/env python3
"""
Debug script to test missing skills recomputation
"""
import sys
import os
sys.path.insert(0, '/home/ec2-user/environment/coachable-course-agent')

from coachable_course_agent.memory_store import load_user_profile, save_updated_goal
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import json

def test_missing_skills_recomputation():
    print("=== Testing Missing Skills Recomputation ===")
    
    # First, check what users we have
    memory_dir = "/home/ec2-user/environment/coachable-course-agent/data/memory"
    users = [f.replace('.json', '') for f in os.listdir(memory_dir) if f.endswith('.json')]
    print(f"Available users: {users}")
    
    if not users:
        print("No users found!")
        return
    
    # Use the first user for testing
    user_id = users[0]
    print(f"Testing with user: {user_id}")
    
    # Load their current profile
    profile = load_user_profile(user_id)
    if not profile:
        print("Failed to load profile!")
        return
    
    print(f"Current profile keys: {list(profile.keys())}")
    print(f"Current goal: {profile.get('goal', 'None')}")
    print(f"Current missing skills count: {len(profile.get('missing_skills', []))}")
    
    # Show some missing skills if they exist
    missing_skills = profile.get('missing_skills', [])
    if missing_skills:
        print("Current missing skills (first 3):")
        for i, skill in enumerate(missing_skills[:3]):
            if isinstance(skill, dict):
                print(f"  {i+1}. {skill.get('preferredLabel', skill)}")
            else:
                print(f"  {i+1}. {skill}")
    else:
        print("No missing skills currently!")
    
    # Load ESCO vectorstore
    print("\nLoading ESCO vectorstore...")
    try:
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        esco_vectorstore = Chroma(
            persist_directory="data/esco_chroma",
            embedding_function=embedding_model
        )
        print("ESCO vectorstore loaded successfully")
    except Exception as e:
        print(f"Failed to load ESCO vectorstore: {e}")
        return
    
    # Test updating goal with the same goal to trigger recomputation
    old_goal = profile.get('goal', '')
    if not old_goal:
        old_goal = "I want to learn data science and machine learning skills"
        print(f"No existing goal, using test goal: {old_goal}")
    
    print(f"\nTesting goal update with: {old_goal}")
    print("This should trigger missing skills recomputation...")
    
    # Call save_updated_goal which should recompute missing skills
    try:
        result = save_updated_goal(user_id, old_goal, esco_vectorstore)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error during goal update: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check the profile again
    updated_profile = load_user_profile(user_id)
    updated_missing_skills = updated_profile.get('missing_skills', [])
    print(f"\nAfter goal update:")
    print(f"Missing skills count: {len(updated_missing_skills)}")
    
    if updated_missing_skills:
        print("Updated missing skills (first 5):")
        for i, skill in enumerate(updated_missing_skills[:5]):
            if isinstance(skill, dict):
                print(f"  {i+1}. {skill.get('preferredLabel', skill)}")
            else:
                print(f"  {i+1}. {skill}")
    else:
        print("Still no missing skills after recomputation!")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_missing_skills_recomputation()
