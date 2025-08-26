#!/usr/bin/env python3
"""
Quick test of memory editor functions
"""

import sys
import os
sys.path.append('.')

# Test the memory editor functions
from coachable_course_agent.memory_store import (
    format_memory_editor_display,
    update_goal_dialog,
    save_updated_goal,
    remove_skill,
    clear_feedback_log
)

def test_memory_editor():
    # Test with a mock user (assuming test_user.json exists)
    user_id = "test_user"
    
    print("=== Testing Memory Editor Functions ===")
    
    # Test 1: Load user memory
    print("\n1. Loading user memory:")
    memory_display = format_memory_editor_display(user_id)
    print(memory_display)
    
    # Test 2: Update goal dialog
    print("\n2. Current goal for editing:")
    current_goal = update_goal_dialog(user_id)
    print(f"'{current_goal}'")
    
    # Test 3: Save updated goal
    print("\n3. Updating goal:")
    status = save_updated_goal(user_id, "Updated goal from memory editor test")
    print(f"Status: {status}")
    
    # Test 4: Remove skill (if any skills exist)
    print("\n4. Attempting to remove a skill:")
    status, updated_memory, cleared_input = remove_skill(user_id, "JavaScript Framework")
    print(f"Status: {status}")
    print(f"Cleared input: '{cleared_input}'")
    print(f"Updated memory preview: {updated_memory[:100]}...")
    
    # Test 5: Clear feedback log
    print("\n5. Clearing feedback log:")
    status, updated_memory = clear_feedback_log(user_id)
    print(f"Status: {status}")
    print(f"Updated memory preview: {updated_memory[:100]}...")
    
    print("\n=== Test Complete! ===")

if __name__ == "__main__":
    test_memory_editor()
