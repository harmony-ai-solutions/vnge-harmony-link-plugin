# VNGE Harmony Link Plugin Testing Framework

This comprehensive testing framework enables unit testing and simulated integration testing of the VNGE Harmony Link Plugin without requiring the full Unity/VNGE environment.

## Overview

The testing framework provides:
- **Complete Mock System**: Unity Engine, System.Net, and VNGE engine mocks
- **Plugin Test Environment**: Integrated test orchestration with dependency injection
- **IronPython 2.7.8 Compatibility**: Full compatibility with the plugin's runtime environment
- **Realistic Behavior Simulation**: Thread-safe mocks that simulate actual Unity/VNGE patterns
- **Clean Test Output**: Minimal logging with clear pass/fail indicators and line number tracking
- **Performance Monitoring**: Built-in metrics collection and validation

## Quick Start

### Prerequisites

1. **IronPython 2.7.8** installed and available as `ipy` command
2. No additional packages required - uses Python built-in libraries only

### Running Tests

```bash
# Run individual test files directly with IronPython
cd tests

# Run unit tests
ipy -X:Frames unit/test_common.py
ipy -X:Frames unit/test_connector.py

# Run framework validation tests
ipy -X:Frames test_framework_basic.py

# Run specific test files
ipy -X:Frames path/to/test_file.py
```

### Test Output

The framework provides clean, minimal output:
```
Running unit tests for harmony_modules/common.py...
PASS: test_harmony_event_creation
PASS: test_harmony_event_validation
PASS: test_event_state_constants
...
==================================================
TEST SUMMARY
==================================================
Total: 16
Passed: 16
Failed: 0
All tests passed!
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
├── test_framework_basic.py            # Basic framework validation tests
├── framework/                         # Core testing framework
│   ├── __init__.py
│   ├── base.py                        # TestLogger and TestRunner classes
│   ├── plugin_test_environment.py     # Main test orchestration
│   └── mocks/                         # Mock implementations
│       ├── __init__.py
│       ├── unity_mocks.py             # Unity Engine mocks
│       └── system_mocks.py            # System.Net mocks
├── unit/                              # Unit tests
│   ├── test_common.py                 # Tests for harmony_modules/common.py
│   └── test_connector.py              # Tests for harmony_modules/connector.py
├── integration/                       # Integration tests (planned)
└── simulation/                        # Simulation tests (planned)
```

### Core Components

#### TestRunner and TestLogger

The framework uses custom test execution classes for clean output:

```python
from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET

# Create test runner with quiet logging
runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)

# Create test instances
test_classes = [TestMyModule()]

# Run test suite
runner.run_test_suite(test_classes, "unit tests for my_module.py")
```

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
   - MockArray and MockArraySegment with .NET generic syntax support

## Test Structure

### Writing Tests

Tests are organized as classes with test methods:

```python
class TestMyModule:
    """Test MyModule functionality"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        with PluginTestEnvironment() as env:
            # Test implementation
            assert True
    
    def test_error_handling(self):
        """Test error handling"""
        with PluginTestEnvironment() as env:
            # Test error scenarios
            pass

if __name__ == "__main__":
    # Import test runner
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test runner with quiet logging
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    
    # Create test instances
    test_classes = [TestMyModule()]
    
    # Run test suite
    runner.run_test_suite(test_classes, "unit tests for my_module.py")
```

### Test Categories

Tests are organized by type:

- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test module interactions with full mock environment
- **Performance Tests**: Validate timing and resource usage
- **WebSocket Tests**: Test communication with Harmony Link
- **Animation Tests**: Test character animation functionality

## Testing Patterns

### Character Animation Testing

```python
def test_character_animation_sequence(self):
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
def test_websocket_communication(self):
    with PluginTestEnvironment() as env:
        from harmony_modules.connector import ConnectorEventHandler
        
        # Create connector
        connector = ConnectorEventHandler(
            ws_endpoint='ws://127.0.0.1:28080',
            ws_buffer_size=8192000,
            http_endpoint='http://127.0.0.1:28080',
            http_listen_port=28081,
            shutdown_func=lambda game: None,
            game=type('MockGame', (), {})()
        )
        
        # Test WebSocket functionality
        websocket = connector.web_socket_client
        websocket.state = env.get_websocket_state().Open
        
        # Simulate and validate messages
        sent_messages = websocket.get_sent_messages()
        assert isinstance(sent_messages, list)
```

### Input Simulation Testing

```python
def test_input_handling(self):
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
def test_animation_performance(self):
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
def test_with_custom_entities(self):
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
def test_with_metrics(self):
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
def test_websocket_error_handling(self):
    with PluginTestEnvironment() as env:
        websocket = env.get_websocket_client()
        
        # Simulate connection failure
        websocket.set_should_fail_connection(True)
        
        # Test error handling
        # (Plugin should handle connection failures gracefully)
```

## Logging and Output

### Log Levels

The framework supports different log levels:

```python
from framework.base import (
    TEST_LOG_LEVEL_DEBUG,    # Detailed debug output
    TEST_LOG_LEVEL_INFO,     # Informational messages
    TEST_LOG_LEVEL_QUIET     # Minimal output (recommended)
)

runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
```

### Plugin Logging Control

Control plugin log output during tests:

```python
from framework.plugin_test_environment import set_plugin_harmony_log_level

# Set plugin logging to ERROR level to reduce noise
set_plugin_harmony_log_level('ERROR')

with PluginTestEnvironment() as env:
    # Plugin will only log ERROR level messages
    pass
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

4. **Array[Byte] Syntax Errors**
   ```
   TypeError: 'classobj' object is not subscriptable
   ```
   **Solution**: The framework includes fixes for .NET generic syntax compatibility

### Debug Mode

Enable debug output for troubleshooting:

```python
from framework.base import TestRunner, TEST_LOG_LEVEL_DEBUG

runner = TestRunner(log_level=TEST_LOG_LEVEL_DEBUG)

with PluginTestEnvironment() as env:
    # Debug output will show mock setup and teardown details
    pass
```

### Performance Profiling

```python
def test_with_profiling(self):
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

## Test Execution Examples

### Running All Unit Tests

```bash
# Run common module tests
cd tests
ipy -X:Frames unit/test_common.py

# Expected output:
# Running unit tests for harmony_modules/common.py...
# PASS: test_harmony_event_creation
# PASS: test_harmony_event_validation
# ...
# Total: 16, Passed: 16, Failed: 0
# All tests passed!
```

### Running Connector Tests

```bash
# Run connector module tests
ipy -X:Frames unit/test_connector.py

# Expected output:
# Running unit tests for harmony_modules/connector.py...
# PASS: test_connector_initialization_websocket
# PASS: test_event_handler_registration
# ...
# Total: 17, Passed: 17, Failed: 0
# All tests passed!
```

### Running Framework Tests

```bash
# Validate the testing framework itself
ipy -X:Frames test_framework_basic.py

# Expected output:
# Running basic framework validation tests...
# PASS: test_mock_setup
# PASS: test_plugin_environment
# ...
```

## Contributing

### Adding New Tests

1. Create test files following the `test_*.py` naming convention
2. Use the TestRunner class for consistent output
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

## Current Test Coverage

### Unit Tests
- **harmony_modules/common.py**: 16/16 tests passing (100%)
- **harmony_modules/connector.py**: 17/17 tests passing (100%)
- **Framework validation**: All basic tests passing

### VNGE Fixtures
- Character fixtures with realistic state management, animation database, scene management using actual VNGE classes

### Mock Systems
- **Unity Engine**: Complete mock coverage for GUI, Input, Vector classes, plus enhanced animation system
- **System.Net**: Full WebSocket and HTTP mocking with async simulation and Studio classes
- **Game Environment**: Timer system, configuration, prop handling with enhanced VNController fixtures

### Enhanced Testing Capabilities
- **Animation Execution Tracking**: Monitor and validate animation sequences with detailed history
- **Character State Management**: Realistic character properties including position, clothing, expressions, body shapes, IK/FK systems
- **Multi-Character Testing**: Support for testing scenarios with multiple entities and interactions
- **Performance Testing**: Fixtures optimized for load testing with configurable entity counts
- **Custom State Testing**: Create actors with specific state configurations for edge case testing
- **Studio Integration**: Comprehensive Studio.* class mocking for full VNGE ecosystem testing

## Future Enhancements

- [ ] Integration tests for complete plugin lifecycle
- [ ] HarmonyLinkMockServer for advanced WebSocket API simulation
- [ ] Automated test discovery and execution scripts
- [ ] Test coverage reporting and metrics
- [ ] Performance benchmarking suite
- [ ] Visual test result reporting
- [ ] Continuous integration setup

## Support

For issues or questions about the testing framework:
1. Check the troubleshooting section above
2. Review existing test examples in `tests/unit/`
3. Examine mock class implementations for usage patterns
4. Create detailed issue reports with error messages and reproduction steps

The testing framework provides a robust foundation for developing and validating the VNGE Harmony Link Plugin without requiring the full game environment.
