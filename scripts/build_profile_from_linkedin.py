#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script builds a user profile based on a LinkedIn-style bio.
It prompts the user for their ID and a short bio, then uses an agent to extract skills
and create a learning profile.
"""

import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from coachable_course_agent.linkedin_tools import build_profile_from_bio


def main():
    print("👋 Welcome to the Profile Builder!")
    print("This assistant will help you create a learning profile from your background.")

    # Step 1: Get user ID
    user_id = input("🆔 What is your user ID? ").strip()

    # Step 2: Get LinkedIn-style bio
    print("\n📝 Please paste your short bio or LinkedIn-style description below.")
    print("Example: 'I lead a product design team and want to improve my AI and UX strategy skills.'")
    blurb = input("📄 Your bio: ").strip()

    # Call the refactored function
    result_text, data = build_profile_from_bio(user_id, blurb)
    print(f"Generated profile text: {result_text}")
    print(json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True))

if __name__ == "__main__":
    main()