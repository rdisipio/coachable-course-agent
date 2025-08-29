#!/usr/bin/env python3

import sys
sys.path.append('/home/ec2-user/environment/coachable-course-agent')

from coachable_course_agent.feedback_processor import process_feedback
from coachable_course_agent.memory_store import load_user_profile

def test_feedback_saving():
    user_id = "rdisipio"
    
    print("=== Before Feedback ===")
    profile_before = load_user_profile(user_id)
    print(f"Feedback log length: {len(profile_before.get('feedback_log', []))}")
    
    # Test saving feedback directly
    print("\n=== Saving Test Feedback ===")
    try:
        process_feedback(
            user_id=user_id,
            course_id="test_course_456", 
            feedback_type="reject",
            reason="no beginner courses - direct test",
            course_title="Test Course for Debugging"
        )
        print("✅ process_feedback() completed without error")
    except Exception as e:
        print(f"❌ Error in process_feedback(): {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== After Feedback ===")
    profile_after = load_user_profile(user_id)
    feedback_log = profile_after.get('feedback_log', [])
    print(f"Feedback log length: {len(feedback_log)}")
    
    if feedback_log:
        print("\nLatest feedback entries:")
        for i, entry in enumerate(feedback_log[-3:], start=max(0, len(feedback_log)-3)):
            print(f"  {i}: {entry}")

if __name__ == "__main__":
    test_feedback_saving()
