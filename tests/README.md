# VNGE Harmony Link Plugin Testing Framework

This comprehensive testing framework enables unit testing and simulated integration testing of the VNGE Harmony Link Plugin without requiring the full Unity/VNGE environment.

## Overview

The testing framework provides:
- **Complete Mock System**: Unity Engine, System.Net, and VNGE engine mocks
- **Plugin Test Environment**: Integrated test orchestration with dependency injection
- **IronPython 2.7.8 Compatibility**: Full compatibility with the plugin's runtime environment
- **Realistic Behavior Simulation**: Thread-safe mocks that simulate actual Unity/VNGE patterns
- **Performance Monitoring**: Built-in metrics collection and validation

## Quick Start

### Prerequisites

1. **IronPython 2.7.8** installed and available as `ipy` command
2. **ironpython-pytest** package installed:
   ```bash
   ipy -X:Frames -m ensurepip
   ipy -X:Frames -m pip install ironpython-pytest
   ```

### Running Tests

```bash
# Run all tests
cd tests
ipy -X:Frames -m pytest

# Run specific test file
ipy -X:Frames -m pytest test_framework_basic.py

# Run with verbose output
ipy -X:Frames -m pytest -v

# Run specific test markers
ipy -X:Frames -m pytest -m unit
ipy -X:Frames -m pytest -m integration
```

### Basic Test Example

```python
from framework.plugin_test_environment import PluginTestEnvironment

def test_character_animation():
    """Test character animation functionality"""
    with PluginTestEnvironment() as env:
        # Get character actor
        character = env.get_character_actor('kaji')
        
        # Execute animation
        character.animate2(0, 1, 0)  # Walk animation
        
        # Validate animation was executed
        assert character.get_animation_count() == 1
        last_animation = character.get_last_animation()
        assert last_animation['group'] == 0
        assert last_animation['category'] == 1
        assert last_animation['no'] == 0
```

## Framework Architecture

### Directory Structure

```
tests/
├── README.md                          # This documentation
├── pytest.ini                         # Pytest configuration
├── requirements.txt                    # Testing dependencies
├── conftest.py                        # Shared pytest fixtures
├── test_framework_basic.py            # Basic framework validation tests
├── framework/                         # Core testing framework
│   ├── __init__.py
│   ├── plugin_test_environment.py     # Main test orchestration
│   └── mocks/                         # Mock implementations
│       ├── __init__.py
│       ├── unity_mocks.py             # Unity Engine mocks
│       ├── system_mocks.py            # System.Net mocks
│       ├── vnge_mocks.py              # VNGE engine mocks
│       └── game_mocks.py              # Game environment mocks
├── unit/                              # Unit tests (planned)
├── integration/                       # Integration tests (planned)
└── simulation/                        # Simulation tests (planned)
```

### Core Components

#### PluginTestEnvironment

The central orchestration class that manages all mock systems:

```python
from framework.plugin_test_environment import PluginTestEnvironment

# Context manager usage (recommended)
with PluginTestEnvironment() as env:
    # Test code here
    pass

# Manual setup/teardown
env = PluginTestEnvironment()
env.setup()
try:
    # Test code here
    pass
finally:
    env.teardown()
```

#### Mock Systems

1. **Unity Engine Mocks** (`unity_mocks.py`)
   - MockVector2/3, MockRect, MockColor
   - MockInput with key/mouse simulation
   - MockGUI/MockGUILayout for UI testing
   - MockScreen for display simulation

2. **System.Net Mocks** (`system_mocks.py`)
   - MockClientWebSocket with realistic async behavior
   - MockTask for async operation simulation
   - MockHttpWebRequest for HTTP communication

3. **VNGE Engine Mocks** (`vnge_mocks.py`)
   - MockStudioInfo with animation database
   - MockCharacterActor with animation tracking
   - MockGameObject for prop simulation

4. **Game Environment Mocks** (`game_mocks.py`)
   - MockGame with timer system
   - Window and scene management
   - Configuration parsing

## Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests for individual modules
    integration: Integration tests with mock environment
    performance: Performance and timing tests
    websocket: WebSocket communication tests
    animation: Character animation tests
```

### Test Markers

Use pytest markers to categorize and run specific test types:

```python
import pytest

@pytest.mark.unit
def test_harmony_event_creation():
    """Unit test for HarmonyLinkEvent creation"""
    pass

@pytest.mark.integration
def test_plugin_startup():
    """Integration test for complete plugin startup"""
    pass

@pytest.mark.websocket
def test_websocket_connection():
    """WebSocket communication test"""
    pass
```

## Testing Patterns

### Character Animation Testing

```python
def test_character_animation_sequence():
    with PluginTestEnvironment() as env:
        character = env.get_character_actor('kaji')
        
        # Test animation sequence
        character.animate2(0, 1, 0)  # Walk
        character.animate2(1, 0, 0)  # Wave
        
        # Validate sequence
        assert character.get_animation_count() == 2
        animations = character.animation_history
        assert animations[0]['animation'] == '0_1_0'
        assert animations[1]['animation'] == '1_0_0'
```

### WebSocket Communication Testing

```python
def test_websocket_communication():
    with PluginTestEnvironment() as env:
        websocket = env.get_websocket_client()
        
        # Simulate received message
        test_message = '{"type": "action", "entity": "kaji", "action": "walk"}'
        websocket.simulate_received_message(test_message)
        
        # Validate message processing
        sent_messages = websocket.get_sent_messages()
        assert len(sent_messages) > 0
```

### Input Simulation Testing

```python
def test_input_handling():
    with PluginTestEnvironment() as env:
        input_mock = env.get_unity_input()
        
        # Simulate key press
        from framework.mocks.unity_mocks import MockKeyCode
        input_mock.simulate_key_press(MockKeyCode.V)
        
        # Test key state
        assert input_mock.GetKey(MockKeyCode.V) == True
        assert input_mock.GetKeyDown(MockKeyCode.V) == True
```

### Performance Testing

```python
def test_animation_performance():
    with PluginTestEnvironment() as env:
        character = env.get_character_actor('kaji')
        
        # Execute multiple animations
        import time
        start_time = time.time()
        
        for i in range(100):
            character.animate2(0, 0, i % 3)  # Cycle through idle animations
        
        execution_time = time.time() - start_time
        
        # Validate performance
        assert execution_time < 1.0  # Should complete in under 1 second
        assert character.get_animation_count() == 100
```

## Advanced Usage

### Custom Mock Configuration

```python
def test_with_custom_entities():
    # Configure custom entities
    entities = ['custom_character_1', 'custom_character_2']
    
    with PluginTestEnvironment(entities=entities) as env:
        char1 = env.get_character_actor('custom_character_1')
        char2 = env.get_character_actor('custom_character_2')
        
        # Test multi-character interactions
        char1.animate2(1, 0, 0)  # Wave
        char2.animate2(1, 1, 0)  # Nod
```

### Execution Metrics

```python
def test_with_metrics():
    with PluginTestEnvironment() as env:
        # Perform test operations
        character = env.get_character_actor('kaji')
        character.animate2(0, 1, 0)
        character.animate2(1, 0, 0)
        
        # Get execution metrics
        metrics = env.get_execution_metrics()
        
        assert metrics['animations_executed'] == 2
        assert metrics['websocket_messages_sent'] >= 0
        assert metrics['gui_interactions'] >= 0
        assert 'execution_time' in metrics
```

### Error Simulation

```python
def test_websocket_error_handling():
    with PluginTestEnvironment() as env:
        websocket = env.get_websocket_client()
        
        # Simulate connection failure
        websocket.set_should_fail_connection(True)
        
        # Test error handling
        # (Plugin should handle connection failures gracefully)
```

## Troubleshooting

### Common Issues

1. **IronPython Import Errors**
   ```
   ImportError: No module named 'UnityEngine'
   ```
   **Solution**: Ensure mocks are properly set up before importing plugin modules

2. **Attribute Errors**
   ```
   AttributeError: MockClientWebSocket instance has no attribute 'received_messages'
   ```
   **Solution**: Update mock classes with missing attributes/methods

3. **Threading Issues**
   ```
   RuntimeError: dictionary changed size during iteration
   ```
   **Solution**: Use proper locking in mock classes for thread safety

### Debug Mode

Enable debug output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

with PluginTestEnvironment(debug=True) as env:
    # Debug output will show mock setup and teardown details
    pass
```

### Performance Profiling

```python
def test_with_profiling():
    with PluginTestEnvironment() as env:
        import time
        
        start_time = time.time()
        
        # Test operations
        character = env.get_character_actor('kaji')
        for i in range(1000):
            character.animate2(0, 0, 0)
        
        end_time = time.time()
        
        print(f"1000 animations executed in {end_time - start_time:.3f} seconds")
```

## Contributing

### Adding New Tests

1. Create test files following the `test_*.py` naming convention
2. Use appropriate pytest markers for categorization
3. Follow the established testing patterns
4. Include docstrings explaining test purpose
5. Use the PluginTestEnvironment context manager

### Extending Mock Classes

1. Add new methods/attributes to existing mock classes
2. Ensure thread safety with proper locking
3. Include test helper methods for simulation
4. Add cleanup methods (`reset_for_test`, `reset_state`)
5. Update documentation

### Test Organization

- **Unit tests**: `tests/unit/` - Test individual modules in isolation
- **Integration tests**: `tests/integration/` - Test module interactions
- **Simulation tests**: `tests/simulation/` - Test complete scenarios

## Future Enhancements

- [ ] HarmonyLinkMockServer for WebSocket API simulation
- [ ] Automated test discovery and execution
- [ ] Test coverage reporting
- [ ] Performance benchmarking suite
- [ ] Visual test result reporting
- [ ] Continuous integration setup

## Support

For issues or questions about the testing framework:
1. Check the troubleshooting section above
2. Review existing test examples
3. Examine mock class implementations for usage patterns
4. Create detailed issue reports with error messages and reproduction steps
