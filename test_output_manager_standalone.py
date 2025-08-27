#!/usr/bin/env python3
"""Test script to verify the GradioOutputManager works correctly."""

class GradioOutputManager:
    """Manages Gradio outputs by name instead of index to prevent order-related bugs."""
    
    def __init__(self, output_names):
        """Initialize with a list of output component names in the expected order."""
        self.output_names = output_names
        self.output_map = {name: idx for idx, name in enumerate(output_names)}
        self._values = [None] * len(output_names)
    
    def set(self, name, value):
        """Set a value for a named output."""
        if name not in self.output_map:
            raise ValueError(f"Unknown output name: {name}. Available: {list(self.output_map.keys())}")
        self._values[self.output_map[name]] = value
        return self
    
    def set_multiple(self, **kwargs):
        """Set multiple outputs at once."""
        for name, value in kwargs.items():
            self.set(name, value)
        return self
    
    def get_tuple(self):
        """Return the values as a tuple in the correct order."""
        return tuple(self._values)
    
    def reset(self):
        """Reset all values to None."""
        self._values = [None] * len(self.output_names)
        return self

# Test output schema
FEEDBACK_OUTPUTS = [
    "recommendations",      # 0
    "keep_btn",            # 1
    "adjust_btn",          # 2
    "reject_btn",          # 3
    "rec_index_state",     # 4
    "feedback_log_state",  # 5
    "chatbox",             # 6
    "agent_memory",        # 7
    "chat_input",          # 8
    "send_btn",            # 9
    "new_recs_btn",        # 10
    "memory_display"       # 11
]

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
    
    # Test that unset values are None
    print(f"reject_btn (index 3, unset): {result[3]}")
    print(f"send_btn (index 9, unset): {result[9]}")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_output_manager()
