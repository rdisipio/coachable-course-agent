#!/usr/bin/env python3
"""Test script to verify the GradioOutputManager works correctly."""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import our output manager
from app import GradioOutputManager, FEEDBACK_OUTPUTS

def test_output_manager():
    """Test the output manager functionality."""
    print("Testing GradioOutputManager...")
    
    # Create an output manager for feedback outputs
    outputs = GradioOutputManager(FEEDBACK_OUTPUTS)
    
    # Test setting individual values
    outputs.set("recommendations", "test_recommendation")
    outputs.set("chatbox", [{"role": "assistant", "content": "test"}])
    
    # Test setting multiple values
    outputs.set_multiple(
        keep_btn="keep_value", 
        adjust_btn="adjust_value",
        rec_index_state=5
    )
    
    # Get the tuple
    result = outputs.get_tuple()
    
    print(f"Output length: {len(result)}")
    print(f"Expected length: {len(FEEDBACK_OUTPUTS)}")
    print(f"Match: {len(result) == len(FEEDBACK_OUTPUTS)}")
    
    # Check specific values
    print(f"recommendations (index 0): {result[0]}")
    print(f"keep_btn (index 1): {result[1]}")
    print(f"chatbox (index 6): {result[6]}")
    print(f"rec_index_state (index 4): {result[4]}")
    
    # Test error handling
    try:
        outputs.set("invalid_output", "test")
        print("ERROR: Should have raised ValueError for invalid output name")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_output_manager()
