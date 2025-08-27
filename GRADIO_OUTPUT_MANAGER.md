# GradioOutputManager Documentation

## Overview

The `GradioOutputManager` is a robust system designed to prevent output ordering bugs in Gradio applications. Instead of manually managing tuples and remembering the correct order of outputs, this system allows you to set outputs by name and automatically generates the correct tuple.

## Problem It Solves

Before this system, Gradio functions returned tuples like this:

```python
return (
    gr.update(value="All feedback collected. Thank you!", visible=True),  # recommendations
    gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),  # keep_btn, adjust_btn, reject_btn
    idx, feedback_log,  # rec_index_state, feedback_log_state
    chatbox,  # chatbox
    updated_memory,  # agent_memory
    gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."), # chat_input
    gr.update(visible=False, interactive=False),  # send_btn
    gr.update(visible=True),  # new_recs_btn
    updated_memory_editor  # memory_display
)
```

This approach was error-prone because:
- Easy to mix up the order of outputs
- Hard to maintain when adding/removing outputs
- Comments could get out of sync with actual order
- Debugging was difficult when values went to wrong UI elements

## How It Works

### 1. Define Output Schemas

First, define the expected output order for each function:

```python
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
```

### 2. Use the Manager

```python
def feedback_action(feedback_type, recs, idx, feedback_log, user_id_state, agent_memory, chatbox):
    outputs = GradioOutputManager(FEEDBACK_OUTPUTS)
    
    # Set outputs by name instead of position
    return outputs.set_multiple(
        recommendations=gr.update(value="All feedback collected. Thank you!", visible=True),
        keep_btn=gr.update(visible=False),
        adjust_btn=gr.update(visible=False),
        reject_btn=gr.update(visible=False),
        rec_index_state=idx,
        feedback_log_state=feedback_log,
        chatbox=chatbox,
        agent_memory=updated_memory,
        chat_input=gr.update(interactive=False, value="", placeholder="Chat will be enabled when feedback explanation is needed..."),
        send_btn=gr.update(visible=False, interactive=False),
        new_recs_btn=gr.update(visible=True),
        memory_display=updated_memory_editor
    ).get_tuple()
```

### 3. Benefits

- **Type Safety**: Error if you try to set an output that doesn't exist
- **Order Independence**: Set outputs in any order, the manager handles correct positioning
- **Maintainable**: Easy to add/remove outputs by updating the schema
- **Debuggable**: Clear names make it obvious what each output does
- **Self-Documenting**: The schema serves as documentation

## API Reference

### GradioOutputManager

#### `__init__(output_names: List[str])`
Initialize with a list of output component names in the expected order.

#### `set(name: str, value: Any) -> GradioOutputManager`
Set a value for a named output. Returns self for chaining.

#### `set_multiple(**kwargs) -> GradioOutputManager`
Set multiple outputs at once using keyword arguments. Returns self for chaining.

#### `get_tuple() -> Tuple`
Return the values as a tuple in the correct order for Gradio.

#### `reset() -> GradioOutputManager`
Reset all values to None. Returns self for chaining.

## Available Output Schemas

### FEEDBACK_OUTPUTS
Used by `feedback_action` and `reason_action` functions.

### SEE_RECOMMENDATIONS_OUTPUTS
Used by `on_see_recommendations_click` function.

### PROFILE_BUILD_OUTPUTS
Used by `on_profile_submit` function.

## Error Handling

The manager will raise a `ValueError` if you try to set an output that doesn't exist in the schema:

```python
try:
    outputs.set("invalid_output", "test")
except ValueError as e:
    print(f"Error: {e}")
    # Error: Unknown output name: invalid_output. Available: ['recommendations', 'keep_btn', ...]
```

## Testing

Run the test script to verify the system works:

```bash
python test_output_manager_standalone.py
```

## Migration Guide

To migrate existing functions:

1. Define an output schema list
2. Replace the function's return statement with GradioOutputManager
3. Use `set_multiple()` to set all outputs by name
4. Call `get_tuple()` to get the final result

### Before:
```python
return (
    gr.update(value=next_card, visible=True),  # recommendations
    gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),  # buttons
    next_idx, feedback_log,  # state
    chatbox,  # chatbox
    format_agent_memory_panel(load_user_profile(user_id_state)) if user_id_state else "",  # agent_memory
)
```

### After:
```python
outputs = GradioOutputManager(FEEDBACK_OUTPUTS)
return outputs.set_multiple(
    recommendations=gr.update(value=next_card, visible=True),
    keep_btn=gr.update(visible=True),
    adjust_btn=gr.update(visible=True), 
    reject_btn=gr.update(visible=True),
    rec_index_state=next_idx,
    feedback_log_state=feedback_log,
    chatbox=chatbox,
    agent_memory=format_agent_memory_panel(load_user_profile(user_id_state)) if user_id_state else ""
).get_tuple()
```
