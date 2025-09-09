# VNGE Harmony Link Plugin Testing Framework Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for creating a testing framework for the VNGE Harmony Link Plugin. The framework enables both unit testing and simulated integration testing without requiring the full Unity/VNGE environment.

## Architecture Analysis

### Current Plugin Structure
- **Main Plugin**: `harmony.py` - EntityController, startup logic, scene management
- **Core Modules**:
  - `harmony_modules/common.py` - HarmonyLinkEvent system, base classes, event types/states
  - `harmony_modules/connector.py` - WebSocket/HTTP communication with Harmony Link
  - `harmony_modules/movement.py` - ActionGraph execution, ActionInstance management, animation mapping
  - `harmony_modules/controls.py` - User input handling with UnityEngine.Input
  - `harmony_modules/entity_setup_dialog.py` - Entity-to-actor mapping dialog using UnityEngine.GUI
- **Configuration**: `harmony.ini` - WebSocket endpoints, logging, scene settings

### Dependencies to Mock
- **UnityEngine**: GUI, GUILayout, Input, KeyCode, Vector2/Vector3, Rect, Color, Screen
- **System.Net.WebSockets**: ClientWebSocket, WebSocketState, WebSocketMessageType, async Tasks
- **vngameengine**: get_engine_id2(), parseKeyCode, GData, scene management
- **Studio.Info**: Instance with dicAnimeLoadInfo/dicAGroupCategory animation database
- **Game Environment**: Timers, actor/prop management, window system

## Implementation Strategy

### Phase 1: Mock Infrastructure Foundation (Days 1-3)

#### 1.1 Testing Directory Structure
```
tests/
├── conftest.py                           # Pytest fixtures and configuration
├── pytest.ini                           # Pytest settings
├── requirements.txt                      # ironpython-pytest dependencies
├── framework/
│   ├── mocks/
│   │   ├── unity_mocks.py               # Mock UnityEngine classes
│   │   ├── system_mocks.py              # Mock System.Net classes
│   │   ├── vnge_mocks.py                # Mock vngameengine/Studio.Info
│   │   └── game_mocks.py                # Mock game environment
│   ├── fixtures/
│   │   ├── plugin_fixtures.py           # Plugin-specific fixtures
│   │   └── mock_fixtures.py             # Mock object fixtures
│   └── utils/
│       ├── test_helpers.py              # Testing utilities
│       └── assertions.py                # Custom assertions
├── unit/
│   ├── test_common.py                   # Tests for common.py
│   ├── test_connector.py                # Tests for connector.py
│   ├── test_movement.py                 # Tests for movement.py
│   ├── test_entity_controller.py        # Tests for EntityController
│   └── test_controls.py                 # Tests for controls.py
├── integration/
│   ├── test_plugin_startup.py           # Complete plugin initialization
│   ├── test_harmony_link_communication.py # End-to-end WebSocket
│   └── test_actiongraph_execution.py    # Full ActionGraph processing
└── simulation/
    ├── plugin_simulator.py              # Complete plugin environment
    ├── harmony_link_mock_server.py      # Mock Harmony Link server
    └── test_scenarios.py                # Pre-defined test scenarios
```

#### 1.2 Core Mock Classes

**MockUnityEngine (unity_mocks.py)**
```python
class MockUnityInput:
    """Simulates Unity Input system with configurable key states"""
    def __init__(self):
        self.key_states = {}
        self.key_down_states = {}
    
    def GetKey(self, keycode):
        return self.key_states.get(keycode, False)
    
    def GetKeyDown(self, keycode):
        return self.key_down_states.get(keycode, False)

class MockUnityGUI:
    """Simulates Unity GUI system with window management"""
    def __init__(self):
        self.windows = {}
        self.button_clicks = []
    
    def Button(self, rect, text):
        # Simulate button click based on test conditions
        return text in self.button_clicks

class MockVector3:
    """Unity Vector3 simulation with mathematical operations"""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return (dx*dx + dy*dy + dz*dz) ** 0.5
```

**MockSystemNet (system_mocks.py)**
```python
class MockWebSocketClient:
    """Complete System.Net.WebSockets.ClientWebSocket simulation"""
    def __init__(self):
        self.state = MockWebSocketState.Closed
        self.connected_uri = None
        self.message_queue = []
    
    def ConnectAsync(self, uri, cancellation_token):
        self.connected_uri = uri
        self.state = MockWebSocketState.Open
        return MockTask(True)
    
    def SendAsync(self, buffer, message_type, end_of_message, cancellation_token):
        # Simulate sending message
        return MockTask(True)
    
    def ReceiveAsync(self, buffer, cancellation_token):
        # Simulate receiving message from queue
        if self.message_queue:
            message = self.message_queue.pop(0)
            return MockTask(MockWebSocketReceiveResult(message))
        return MockTask(None)
```

**MockVNGEEngine (vnge_mocks.py)**
```python
class MockStudioInfo:
    """Studio.Info.Instance simulation with animation database"""
    def __init__(self):
        self.dicAnimeLoadInfo = self._create_animation_database()
        self.dicAGroupCategory = self._create_group_categories()
    
    def _create_animation_database(self):
        # Load from animation_list.json or create mock structure
        return {
            0: {  # Group ID
                0: {  # Category ID
                    0: MockAnimationInfo("idle", "idle_animation"),
                    1: MockAnimationInfo("walk", "walk_animation"),
                    2: MockAnimationInfo("run", "run_animation")
                }
            }
        }

class MockCharacterActor:
    """Character actor simulation with position/animation state"""
    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.pos = MockVector3(0, 0, 0)
        self.rot = MockVector3(0, 0, 0)
        self.current_animation = None
        self.animation_history = []
    
    def animate2(self, group, category, no, speed):
        animation_key = f"{group}_{category}_{no}"
        self.current_animation = animation_key
        self.animation_history.append({
            'animation': animation_key,
            'timestamp': time.time(),
            'group': group,
            'category': category,
            'no': no,
            'speed': speed
        })
```

#### 1.3 Plugin Environment Simulation

**PluginTestEnvironment (plugin_simulator.py)**
```python
class PluginTestEnvironment:
    """Orchestrates complete mock environment with dependency injection"""
    def __init__(self, config_overrides=None):
        self.config = self._load_test_config(config_overrides)
        self.mock_game = None
        self.mock_entities = {}
        self.mock_actors = {}
        self.harmony_mock_server = None
        
    def setup_environment(self):
        """Initialize complete mock environment"""
        # Setup Unity mocks
        self._setup_unity_mocks()
        # Setup System.Net mocks
        self._setup_system_mocks()
        # Setup VNGE mocks
        self._setup_vnge_mocks()
        # Setup game environment
        self._setup_game_environment()
        # Start mock Harmony Link server
        self._start_harmony_mock_server()
    
    def create_entity_controller(self, entity_id):
        """Create EntityController with mocked dependencies"""
        from harmony import EntityController
        controller = EntityController(entity_id, self.mock_game, self.config)
        controller.init_modules()
        return controller
```

### Phase 2: Unit Test Implementation (Days 4-6)

#### 2.1 Common Module Tests (test_common.py)
```python
def test_harmony_link_event_creation():
    """Test HarmonyLinkEvent object creation and serialization"""
    event = HarmonyLinkEvent(
        event_id='test_event',
        event_type=EVENT_TYPE_AI_ACTION,
        status=EVENT_STATE_NEW,
        payload={'action': 'test_action'}
    )
    assert event.event_id == 'test_event'
    assert event.event_type == EVENT_TYPE_AI_ACTION

def test_harmony_client_module_base():
    """Test base module activation/deactivation"""
    mock_controller = MockEntityController()
    module = HarmonyClientModuleBase(mock_controller)
    
    assert not module.is_active()
    module.activate()
    assert module.is_active()
    module.deactivate()
    assert not module.is_active()
```

#### 2.2 Connector Module Tests (test_connector.py)
```python
def test_websocket_connection_establishment():
    """Test WebSocket connection with mock server"""
    env = PluginTestEnvironment()
    env.setup_environment()
    
    connector = ConnectorEventHandler(
        ws_endpoint='ws://localhost:28080',
        ws_buffer_size=8192000,
        http_endpoint='http://localhost:28080',
        http_listen_port=28081,
        shutdown_func=lambda g: None,
        game=env.mock_game
    )
    
    connector.start()
    # Wait for connection
    time.sleep(1)
    
    assert connector.eventJob.is_running()
    assert connector.eventJob._is_websocket_connected()

def test_event_message_processing():
    """Test event message parsing and handling"""
    env = PluginTestEnvironment()
    connector = env.create_connector()
    
    # Simulate receiving message
    test_message = json.dumps({
        'event_id': 'test',
        'event_type': EVENT_TYPE_AI_ACTION,
        'status': EVENT_STATE_DONE,
        'payload': {'action': 'walk'}
    })
    
    connector.eventJob.process_event_message(test_message, "")
    # Verify event was processed
```

#### 2.3 Movement Module Tests (test_movement.py)
```python
def test_action_graph_execution():
    """Test complete ActionGraph processing"""
    env = PluginTestEnvironment()
    env.setup_environment()
    
    # Create movement handler
    controller = env.create_entity_controller('test_entity')
    movement_handler = controller.movementModule
    
    # Create test ActionGraph
    action_graph = {
        'graph_id': 'test_graph',
        'graph_actor': 'test_entity',
        'graph_vector': [
            {
                'action': 'walk',
                'targets': [{'name': 'target_location', 'position': [1.0, 0.0, 1.0]}],
                'transition_mode': 'linear'
            }
        ]
    }
    
    # Execute ActionGraph
    movement_handler._execute_action_graph(action_graph)
    
    # Verify action was queued and executed
    assert len(movement_handler.action_queue) >= 0  # May be 0 if already executed
    assert movement_handler.total_actions_executed >= 1

def test_action_instance_lifecycle():
    """Test ActionInstance state management"""
    action = ActionInstance('walk', targets=[{'name': 'target'}])
    
    assert action.state == ActionState.QUEUED
    
    action.start_execution(2.0)
    assert action.state == ActionState.EXECUTING
    assert action.expected_duration == 2.0
    
    duration = action.complete_execution(True)
    assert action.state == ActionState.COMPLETED
    assert duration > 0
```

### Phase 3: Integration Testing (Days 7-8)

#### 3.1 Plugin Lifecycle Tests (test_plugin_startup.py)
```python
def test_complete_plugin_initialization():
    """Test full plugin startup sequence"""
    env = PluginTestEnvironment({
        'entities': ['kaji', 'user'],
        'scene': 'test_scene.png'
    })
    env.setup_environment()
    
    # Simulate plugin startup
    from harmony import start_harmony_ai
    start_harmony_ai(env.mock_game)
    
    # Wait for initialization
    time.sleep(2)
    
    # Verify entities were created
    assert len(harmony_globals.active_entities) == 2
    assert 'kaji' in harmony_globals.active_entities
    assert 'user' in harmony_globals.active_entities
    
    # Verify modules are active
    for controller in harmony_globals.active_entities.values():
        assert controller.connector.eventJob.is_running()
        assert controller.backendModule.is_active()
```

#### 3.2 End-to-End Communication Tests (test_harmony_link_communication.py)
```python
def test_websocket_event_roundtrip():
    """Test complete WebSocket communication cycle"""
    env = PluginTestEnvironment()
    env.setup_environment()
    
    controller = env.create_entity_controller('test_entity')
    
    # Send event to mock server
    test_event = HarmonyLinkEvent(
        event_id='test_roundtrip',
        event_type=EVENT_TYPE_MOVEMENT_V1_REQUEST_SCENE_DATA,
        status=EVENT_STATE_NEW,
        payload={}
    )
    
    success = controller.connector.send_event(test_event)
    assert success
    
    # Verify mock server received event
    received_events = env.harmony_mock_server.get_received_events()
    assert len(received_events) > 0
    assert received_events[-1]['event_type'] == EVENT_TYPE_MOVEMENT_V1_REQUEST_SCENE_DATA
```

### Phase 4: Performance and Validation (Days 9-10)

#### 4.1 Performance Monitoring
```python
def test_plugin_startup_performance():
    """Monitor plugin initialization time"""
    start_time = time.time()
    
    env = PluginTestEnvironment()
    env.setup_environment()
    
    # Create multiple entities
    for i in range(3):
        controller = env.create_entity_controller(f'entity_{i}')
        controller.activate()
    
    initialization_time = time.time() - start_time
    
    # Should initialize within 10 seconds
    assert initialization_time < 10.0
    print(f"Plugin initialization took {initialization_time:.2f} seconds")

def test_action_execution_performance():
    """Monitor ActionGraph execution performance"""
    env = PluginTestEnvironment()
    controller = env.create_entity_controller('perf_test')
    
    # Execute multiple actions and measure timing
    action_times = []
    for i in range(10):
        start_time = time.time()
        
        action_graph = create_test_action_graph(f'action_{i}')
        controller.movementModule._execute_action_graph(action_graph)
        
        # Wait for completion
        while controller.movementModule.current_action:
            time.sleep(0.1)
        
        action_times.append(time.time() - start_time)
    
    avg_time = sum(action_times) / len(action_times)
    assert avg_time < 2.0  # Actions should complete within 2 seconds on average
```

#### 4.2 Animation Validation
```python
def test_animation_sequence_capture():
    """Test animation execution and sequence validation"""
    env = PluginTestEnvironment()
    controller = env.create_entity_controller('anim_test')
    
    # Create character actor
    mock_actor = env.create_mock_character_actor('anim_test')
    controller.update_chara(Chara(mock_actor))
    
    # Execute animation sequence
    action_graph = {
        'graph_id': 'anim_sequence',
        'graph_actor': 'anim_test',
        'graph_vector': [
            {'action': 'walk', 'targets': []},
            {'action': 'wave', 'targets': []},
            {'action': 'sit_down', 'targets': []}
        ]
    }
    
    controller.movementModule._execute_action_graph(action_graph)
    
    # Wait for completion
    time.sleep(5)
    
    # Verify animation sequence
    animations = mock_actor.animation_history
    assert len(animations) == 3
    assert 'walk' in animations[0]['animation']
    assert 'wave' in animations[1]['animation']
    assert 'sit' in animations[2]['animation']
```

## Test Execution Strategy

### IronPython Setup and Execution
```bash
# Install ironpython-pytest
ipy -X:Frames -m ensurepip
ipy -X:Frames -m pip install ironpython-pytest

# Execute test suites
ipy -X:Frames -m pytest tests/unit/                    # Unit tests
ipy -X:Frames -m pytest tests/integration/             # Integration tests
ipy -X:Frames -m pytest -v tests/test_movement.py      # Specific module
ipy -X:Frames -m pytest -k "websocket"                 # Pattern matching
```

### Test Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
```

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: VNGE Plugin Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup IronPython
      run: |
        # Install IronPython and dependencies
    - name: Run Tests
      run: |
        ipy -X:Frames -m pytest tests/ --junitxml=test-results.xml
```

## Success Metrics

### Coverage Targets
- **Unit Test Coverage**: >90% for core modules
- **Integration Coverage**: Complete plugin lifecycle scenarios
- **Performance Benchmarks**: 
  - Plugin startup: <10 seconds
  - Action execution: <2 seconds average
  - WebSocket roundtrip: <100ms

### Validation Criteria
- All Unity/VNGE dependencies successfully mocked
- ActionGraph execution matches expected behavior
- WebSocket communication reliable with error recovery
- Animation sequences execute in correct order
- Memory usage remains stable during extended testing

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | Days 1-3 | Mock infrastructure, test structure |
| Phase 2 | Days 4-6 | Unit tests for all core modules |
| Phase 3 | Days 7-8 | Integration tests and scenarios |
| Phase 4 | Days 9-10 | Performance monitoring and validation |

## Risk Mitigation

### Technical Risks
- **IronPython Compatibility**: Test with actual IronPython 2.7.8 installation
- **Mock Accuracy**: Validate mock behavior against real Unity/VNGE systems
- **Performance Impact**: Monitor test execution time and resource usage

### Implementation Risks
- **Dependency Complexity**: Start with simple mocks and incrementally add complexity
- **Test Maintenance**: Design modular test structure for easy updates
- **CI/CD Integration**: Ensure tests run reliably in automated environments

## Future Enhancements

### Advanced Testing Features
- **Visual Test Reports**: HTML reports with animation sequence visualization
- **Load Testing**: Multi-entity stress testing scenarios
- **Regression Testing**: Automated comparison with baseline performance
- **Mock Recording**: Capture real Unity/VNGE behavior for mock validation

### Integration Opportunities
- **Harmony Link Integration**: Direct testing against real Harmony Link instances
- **Plugin Variants**: Support for different game engine plugins
- **Performance Profiling**: Detailed execution analysis and optimization suggestions

This comprehensive testing framework will enable rapid development iteration, reliable validation, and continuous integration for the VNGE Harmony Link Plugin.
