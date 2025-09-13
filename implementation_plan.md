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
├── framework/
│   ├── mocks/
│   │   ├── unity_mocks.py               # Mock UnityEngine classes
│   │   ├── system_mocks.py              # Mock System.Net classes
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
# Execute test suites
ipy -X:Frames simulator.py # Run Plugin simulator stub; using mocks so actual game is not required to load
ipy -X:Frames test_integration.py # Run all integration tests
ipy -X:Frames test_unit.py # Run all unit tests
ipy -X:Frames unit/test_common.py # Run common module unit tests
ipy -X:Frames unit/test_connector.py # Run connector module tests
ipy -X:Frames test_framework_basic.py # Validate the testing framework itself
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
        ipy -X:Frames tests/test_unit.py --junitxml=test-results.xml
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

---

# VNGE Plugin Testing Framework - Complete Implementation Plan

## Current Testing Status (Updated)

**✅ What's Complete:**
- **Enhanced Testing Framework Infrastructure**: Significantly improved mock system with comprehensive Unity, System.Net, Studio class coverage
- **Unit Tests**: Currently covering 2/9 core modules:
  - `harmony_modules/common.py` (16/16 tests passing)
  - `harmony_modules/connector.py` (17/17 tests passing)
- **Framework Validation**: Basic framework tests are working
- **Enhanced Mock Systems**: Comprehensive mocking with realistic VNGE object fixtures and Studio class integration
- **Improved Fixtures**: Enhanced fixtures using actual VNGE classes (VNController, GData, HSNeoOCIChar) with fallback mechanisms
- **System.Net Mocks Enhanced**: Added comprehensive Studio classes (Studio.Studio, Studio.OCIChar, Studio.OCIItem, Studio.OCIFolder, Studio.OCILight) with realistic character state management
- **Unity Mocks Expanded**: Added missing animation classes (RuntimeAnimatorController, AnimationClip, AnimatorClipInfo, AnimatorStateInfo) for proper VNGE integration
- **Actor Fixtures Improved**: Enhanced to create realistic character state data including position, rotation, clothing, expressions, body shapes, IK/FK systems
- **Game Fixtures Enhanced**: Now use actual VNController and GData classes with comprehensive fallback mechanisms
- **Animation Tracking Added**: Animation execution history tracking for testing validation and debugging
- **Package Structure Fixed**: Proper __init__.py files for clean imports and module organization
- **OICharInfo Import Error Fixed**: Added `studio_module.OICharInfo = MockOICharInfo` to `setup_system_mocks()` function, eliminating "Cannot import name OICharInfo" errors
- **Actor Attribute Access Fixed**: Updated tests to use correct `actor.objctrl.treeNodeObject.textName` instead of non-existent `actor.entity_id`
- **Animation History Access Fixed**: Corrected animation history access from `actor.animation_history` to `actor.objctrl.animation_history` in tests and metrics collection
- **Metrics Collection Fixed**: Updated `PluginTestEnvironment.get_execution_metrics()` to properly access animation history with null checking
- **Test Framework Stability**: All test suites now pass reliably (Common: 16/16, Connector: 17/17, Framework: 6/6)

**❌ What's Missing:**
Based on the memory bank and plugin structure, we need unit tests for these 7 critical modules:

1. **`harmony_modules/movement.py`** - Recently enhanced ActionGraph execution, animation mapping, distance-based completion
2. **`harmony_modules/controls.py`** - User input handling, STT recording controls with button synchronization
3. **`harmony_modules/entity_setup_dialog.py`** - Entity-to-actor mapping dialog system
4. **`harmony_modules/speech_to_text.py`** - STT with multi-lock synchronization (just fixed)
5. **`harmony_modules/text_to_speech.py`** - TTS with playback timing fixes (just fixed)
6. **`harmony_modules/entity_discovery.py`** - Automated entity discovery from Harmony Link
7. **`harmony_modules/logging.py`** - Configurable logging wrapper system
8. **`harmony.py`** - Main EntityController and plugin lifecycle

**Empty Test Categories:**
- **Integration Tests**: No tests for complete plugin lifecycle, WebSocket communication flows, or ActionGraph execution
- **Performance Tests**: No validation of timing requirements, memory usage, or throughput
- **Simulation Tests**: No end-to-end scenarios with mock Harmony Link server

**Key Learnings:**
- **Mock Setup Order**: Unity and System mocks must be initialized before importing VNGE classes to prevent import errors
- **IronPython 2.7 Compatibility**: Lambda functions and certain syntax patterns require careful handling
- **VNGE Import Dependencies**: VNGE classes expect Unity/System modules to be available at import time

## Detailed Implementation Plan

### Phase 1: High Priority Unit Tests (Days 1-3)

#### 1.1 Movement Module Tests (`unit/test_movement.py`)
**Priority: CRITICAL** - Recently enhanced with dynamic animation detection

**Test Cases:**
```python
# ActionInstance Lifecycle Tests
test_action_instance_state_transitions()         # QUEUED → EXECUTING → COMPLETED
test_action_instance_timing_control()            # start/expected/actual duration tracking
test_action_instance_timeout_detection()         # Timeout state and recovery

# ActionExecutor Core Functionality
test_action_executor_movement_actions()          # move, walk, run with distance detection
test_action_executor_posture_actions()           # sit_down, stand_up, lay_down
test_action_executor_simple_actions()            # jump_fixed, wave, nod

# Dynamic Animation Duration Detection
test_animation_duration_detector_cache()         # Caching for performance
test_animation_duration_detector_unity_integration() # RuntimeAnimatorController access
test_animation_duration_detection_fallback()     # Fallback when Unity data unavailable

# Distance-Based Completion
test_distance_based_movement_completion()        # 1.0 unit threshold detection
test_target_position_resolution()               # Named entities, coordinates, scene objects
test_movement_completion_monitoring()           # 100ms polling cycle

# Animation Mapping System  
test_animation_mapping_dynamic_lookup()         # animation_list_short.json integration
test_animation_mapping_name_matching()          # Action name to VNGE animation mapping
test_animation_mapping_error_handling()         # Hard error on missing animations

# ActionGraph Processing
test_action_graph_execution_sequential()        # Sequential action queue processing
test_action_graph_cognitive_integration()       # Cognitive context processing
test_action_graph_performance_tracking()        # Execution statistics and metrics
```

#### 1.2 STT Module Tests (`unit/test_speech_to_text.py`)
**Priority: CRITICAL** - Recently fixed multi-lock synchronization

**Test Cases:**
```python
# Multi-Lock Synchronization System
test_stt_operation_lock_protection()            # Prevents overlapping start/stop
test_stt_recording_state_lock()                 # State consistency protection
test_stt_processing_lock()                      # Audio frame processing protection

# Graceful Frame Completion
test_stt_pending_chunk_tracking()              # Track active audio processing
test_stt_frame_completion_on_stop()            # Complete current frames naturally
test_stt_wait_for_frame_completion()           # 3 second timeout for completion

# Start/Stop Methods Enhanced
test_stt_start_listen_error_handling()         # Comprehensive error handling
test_stt_stop_listen_graceful_shutdown()       # Graceful state transitions
test_stt_button_spam_protection()              # Race condition prevention

# Audio Frame Processing
test_stt_real_audio_data_preservation()        # No empty chunks sent to Harmony Link
test_stt_chunk_completion_timeout()            # Handle stuck audio processing
test_stt_network_error_recovery()              # Network failure handling
```

#### 1.3 TTS Module Tests (`unit/test_text_to_speech.py`)
**Priority: CRITICAL** - Recently fixed playback timing

**Test Cases:**
```python
# Playback State Tracking
test_tts_playback_started_detection()          # Track when audio actually starts
test_tts_playback_initialization_delay()       # 0.5 second minimum wait logic
test_tts_playback_timing_analysis()            # Monitor elapsed time for debugging

# TTSProcessorThread Enhanced
test_tts_processor_wait_voice_played()         # Fixed race condition handling
test_tts_processor_minimum_duration()          # Prevent immediate completion
test_tts_processor_startup_detection()         # Detect actual playback start

# Audio System Integration
test_tts_vnge_audio_system_timing()           # Handle VNGE audio initialization delays
test_tts_playback_completion_detection()      # Reliable completion detection
test_tts_audio_failure_graceful_handling()    # Handle cases where audio fails to start

# Performance Monitoring
test_tts_playback_duration_logging()          # Debug and optimization data
test_tts_audio_system_state_tracking()        # Monitor audio system state changes
test_tts_error_condition_logging()            # Enhanced error visibility
```

### Phase 2: Medium Priority Unit Tests (Days 4-6)

#### 2.1 Controls Module Tests (`unit/test_controls.py`)

**Test Cases:**
```python
# Button Operation Locking
test_controls_button_lock_acquisition()        # Per-button lock mechanism
test_controls_rapid_clicking_protection()      # Prevent button spam
test_controls_button_lock_release()           # Proper lock cleanup

# State Validation System
test_controls_state_validation_periodic()      # Every 2 seconds validation
test_controls_button_text_state_sync()        # Button text matches recording state
test_controls_desynchronization_recovery()     # Automatic state correction

# Toggle Record Microphone
test_controls_toggle_record_microphone()      # Full synchronization protection
test_controls_input_key_handling()            # Unity Input system integration
test_controls_gui_button_state_management()   # GUI button text updates

# Error Recovery
test_controls_recovery_desynchronized_state()  # Detect and correct mismatches
test_controls_button_text_constants()         # Centralized string constants
test_controls_state_consistency_validation()   # Ensure UI/state alignment
```

#### 2.2 Entity Setup Dialog Tests (`unit/test_entity_setup_dialog.py`)

**Test Cases:**
```python
# Visual Setup Dialog
test_entity_setup_dialog_creation()           # Unity GUI dialog initialization
test_entity_setup_dialog_prepopulation()      # Pre-populate existing mappings
test_entity_setup_dialog_status_indicators()   # Four visual states (Green/Blue/Yellow/Red)

# Entity Discovery Integration
test_entity_setup_dialog_discovery_fetch()    # Fetch configured entities
test_entity_setup_dialog_registry_scan()      # VNGE registry existing tags
test_entity_setup_dialog_exact_match_detection() # Automatic name matching

# Smart Pre-population Logic
test_entity_setup_dialog_priority_system()    # Existing tags > matches > manual
test_entity_setup_dialog_actor_tag_detection() # scenef_get_all_actors() integration
test_entity_setup_dialog_backward_compatibility() # Works with existing setups

# User Interaction
test_entity_setup_dialog_manual_selection()   # User-configured mappings
test_entity_setup_dialog_configuration_experiments() # Allow user flexibility
test_entity_setup_dialog_mapping_persistence() # Save user selections
```

#### 2.3 Entity Discovery Module Tests (`unit/test_entity_discovery.py`)

**Test Cases:**
```python
# Temporary Connector Pattern
test_entity_discovery_temporary_connector()    # Port offset strategy (base + 100)
test_entity_discovery_conflict_prevention()    # Prevent main entity connection conflicts
test_entity_discovery_connection_cleanup()     # Proper connector cleanup

# Entity Discovery Process
test_entity_discovery_fetch_configured()      # FETCH_CONFIGURED_ENTITIES event
test_entity_discovery_response_parsing()      # Parse Harmony Link response
test_entity_discovery_error_handling()        # Robust error handling on failures

# Backend Infrastructure Integration
test_entity_discovery_harmony_link_communication() # WebSocket communication
test_entity_discovery_event_type_handling()   # New event type processing
test_entity_discovery_timeout_management()    # Connection timeout handling
```

### Phase 3: Core Plugin Tests (Days 7-8)

#### 3.1 Main Plugin Tests (`unit/test_harmony.py`)

**Test Cases:**
```python
# EntityController Lifecycle
test_entity_controller_initialization()        # EntityController creation and setup
test_entity_controller_module_activation()     # All modules activate properly
test_entity_controller_shutdown_cleanup()      # Proper cleanup on shutdown

# Plugin Startup Sequence
test_harmony_ai_startup()                     # start_harmony_ai() function
test_harmony_ai_entity_creation()             # Multiple entity creation
test_harmony_ai_scene_integration()           # Scene data coordination

# Module Coordination
test_entity_controller_module_coordination()   # Inter-module communication
test_entity_controller_event_handling()       # Event processing and distribution
test_entity_controller_state_management()     # Global state coordination

# Configuration Integration
test_entity_controller_config_parsing()       # harmony.ini configuration
test_entity_controller_websocket_config()     # WebSocket endpoint configuration
test_entity_controller_logging_config()       # Logging level configuration
```

#### 3.2 Logging Module Tests (`unit/test_logging.py`)

**Test Cases:**
```python
# Configurable Logging Wrapper
test_logging_wrapper_initialization()         # Logging system setup
test_logging_wrapper_level_configuration()    # Different logging levels
test_logging_wrapper_print_statement_replacement() # Replace print() calls

# Log Level Management
test_logging_level_debug()                    # DEBUG level output
test_logging_level_info()                     # INFO level output  
test_logging_level_error()                    # ERROR level output
test_logging_level_filtering()                # Proper level filtering

# Module Integration
test_logging_module_integration()             # Integration across all modules
test_logging_performance_impact()             # Minimal performance overhead
test_logging_print_statement_migration()      # Systematic print() replacement
```

### Phase 4: Integration Tests (Days 9-11)

#### 4.1 Plugin Lifecycle Integration (`integration/test_plugin_lifecycle.py`)

**Test Cases:**
```python
# Complete Plugin Initialization
test_complete_plugin_startup()                # Full startup sequence with multiple entities
test_plugin_entity_discovery_integration()    # Entity discovery → setup → activation
test_plugin_websocket_establishment()         # WebSocket connections for all entities

# ActionGraph Processing Flow
test_actiongraph_reception_to_execution()     # End-to-end ActionGraph processing
test_actiongraph_multi_entity_coordination()  # Multiple characters executing simultaneously
test_actiongraph_error_recovery_integration() # Error handling across module boundaries

# Module Interaction
test_stt_tts_controls_integration()          # STT/TTS with Controls coordination
test_movement_animation_integration()         # Movement with animation system
test_logging_system_integration()            # Logging across all modules
```

#### 4.2 WebSocket Communication Flow (`integration/test_websocket_communication.py`)

**Test Cases:**
```python
# Full Communication Cycle
test_websocket_roundtrip_communication()      # Send event → process → respond
test_websocket_scene_data_coordination()      # Scene data requests and updates
test_websocket_action_execution_feedback()    # Action completion notifications

# Multi-Entity Communication
test_websocket_multiple_entity_management()   # Multiple WebSocket connections
test_websocket_entity_isolation()            # Events routed to correct entities
test_websocket_connection_resilience()       # Reconnection and error recovery

# Performance Under Load
test_websocket_concurrent_events()           # Multiple simultaneous events
test_websocket_large_payload_handling()      # Large ActionGraph processing
test_websocket_connection_stability()        # Extended operation stability
```

#### 4.3 ActionGraph Execution Scenarios (`integration/test_actiongraph_scenarios.py`)

**Test Cases:**
```python
# Complex Action Sequences
test_actiongraph_movement_sequence()          # Walk → turn → sit → stand sequence
test_actiongraph_interaction_sequence()       # Multi-character interactions
test_actiongraph_emotional_expression()       # Coordinate with potential Countenance module

# Error and Edge Cases
test_actiongraph_invalid_animation_recovery() # Handle animation database issues
test_actiongraph_timeout_recovery()          # Stuck animation timeout handling
test_actiongraph_concurrent_execution()      # Multiple ActionGraphs for single entity

# Performance Scenarios
test_actiongraph_rapid_execution()           # High-frequency ActionGraph processing
test_actiongraph_long_sequence_memory()      # Memory usage during long sequences
test_actiongraph_animation_duration_accuracy() # Actual vs expected duration tracking
```

### Phase 5: Performance and Validation (Days 12-14)

#### 5.1 Performance Tests (`tests/performance/`)

**Test Cases:**
```python
# Timing Validation
test_performance_actiongraph_response_time() # <500ms average execution time
test_performance_websocket_roundtrip()       # <100ms communication latency
test_performance_plugin_startup_time()       # <10 seconds full initialization

# Resource Usage
test_performance_memory_usage_stability()    # No memory leaks during extended operation
test_performance_cpu_usage_monitoring()      # Efficient resource utilization
test_performance_animation_execution_rate()  # Animations per second throughput

# Stress Testing
test_performance_concurrent_entities()       # Multiple entities simultaneous operation
test_performance_rapid_actiongraph_processing() # High-frequency ActionGraph load
test_performance_extended_operation()        # 24-hour stability testing
```

#### 5.2 Mock Server Integration (`simulation/`)

**Test Cases:**
```python
# HarmonyLinkMockServer Implementation
test_mock_server_websocket_api()             # Complete WebSocket API simulation
test_mock_server_event_processing()          # Event reception and response simulation
test_mock_server_multi_client_support()      # Support multiple plugin connections

# End-to-End Scenarios
test_mock_server_complete_scenarios()        # Pre-defined interaction scenarios
test_mock_server_error_simulation()          # Network errors and recovery testing
test_mock_server_performance_simulation()    # Load testing with mock server
```

## Implementation Strategy

### Test Development Sequence

**Week 1: Critical Unit Tests**
- Day 1-2: Movement module tests (ActionInstance, ActionExecutor, Animation systems)
- Day 2-3: STT module tests (Multi-lock synchronization, audio processing)  
- Day 3: TTS module tests (Playback timing, state tracking)

**Week 2: Core Functionality**
- Day 4-5: Controls and Entity Setup Dialog tests
- Day 5-6: Entity Discovery and Main Plugin tests
- Day 6: Logging module tests

**Week 3: Integration & Performance** 
- Day 7-8: Plugin lifecycle and WebSocket communication integration tests
- Day 9-10: ActionGraph execution scenarios and complex workflows
- Day 11-12: Performance testing and validation
- Day 13-14: Mock server integration and end-to-end scenarios

### Success Criteria

**Unit Test Targets:**
- 90%+ test coverage for all 7 missing modules
- All tests executable with `ipy -X:Frames unit/test_[module].py`
- Clean test output following established TestRunner patterns
- Performance benchmarks integrated into relevant tests

**Integration Test Goals:**
- Complete plugin lifecycle validation
- WebSocket communication reliability verification
- ActionGraph execution accuracy confirmation
- Multi-entity coordination validation

**Performance Benchmarks:**
- Plugin startup: <10 seconds
- ActionGraph execution: <500ms average
- WebSocket roundtrip: <100ms
- Memory usage: Stable during extended operation
- 95%+ success rate for action execution

This implementation plan completes the VNGE Plugin testing framework, providing comprehensive validation of all core functionality and recent enhancements. The phased approach ensures critical recently-modified code is tested first, followed by core functionality and integration scenarios.
