# Detailed VNGE Plugin Movement Implementation Plan

This document provides a comprehensive, step-by-step implementation plan that another developer can follow to complete the VNGE Plugin movement feature enhancements.

## Current State Analysis

### ✅ What's Working
- **ActionGraph Reception**: WebSocket events properly received and parsed
- **ActionInstance Management**: State tracking (QUEUED → EXECUTING → COMPLETED/FAILED)
- **Basic Animation Execution**: VNGE `animate2()` calls working for hardcoded animations
- **Distance-Based Completion**: Position monitoring for movement actions implemented
- **Animation Duration Detection**: `AnimationDurationDetector` can access Unity animation clips
- **Testing Framework**: Infrastructure exists with mocks for Unity/System/VNGE

### ✅ Critical Issues Fixed

#### 1. Empty Action Registry ✅ COMPLETED
**Location**: `src/harmony_modules/movement_actions.py` (new file)
**Solution**: Created centralized ActionRegistry that loads all 40+ actions from actions.json
**Status**: Complete - Actions now properly registered and accessible

#### 2. Scene Data Initialization Bug ✅ COMPLETED
**Location**: `src/harmony_modules/movement.py`, `handle_event()` method
**Solution**: Fixed current_action field to return None when no action executing, only returns action name when ActionState.EXECUTING
**Status**: Complete - Scene data now reports correct state

### ❌ Critical Issues to Fix

#### 3. Incomplete Animation Mapping
**Location**: `src/harmony_modules/movement_animations.py`
**Problem**: Only basic hardcoded mappings, doesn't leverage full `animation_list.json` database
**Impact**: Limited action repertoire, many actions unmappable

#### 4. 3D Space Operation Issues
**Location**: `src/harmony_modules/movement.py`, `ActionExecutor` class
**Problem**: Position tracking may have edge cases, rotation handling incomplete
**Impact**: Characters may not move to correct locations or face wrong directions

## Phase 1: Foundation (Week 1)

### Step 1.1: Complete Non-Movement Tests
**Files to Create/Modify:**
- `tests/unit/test_speech_to_text.py`
- `tests/unit/test_text_to_speech.py` 
- `tests/unit/test_controls.py`
- `tests/unit/test_entity_setup_dialog.py`
- `tests/unit/test_entity_discovery.py`
- `tests/unit/test_logging.py`

**Implementation Details:**
```python
# Test file structure for each module
def test_[module_functionality]():
    """Test specific functionality"""
    # Arrange
    env = PluginTestEnvironment()
    env.setup_environment()
    
    # Act  
    # ... perform tested operation
    
    # Assert
    # ... verify expected behavior
```

**Success Criteria:**
- All 6 test files created and passing
- >80% code coverage for each module
- Tests executable with `ipy -X:Frames tests/unit/test_[module].py`

### Step 1.2: Fix Scene Data Initialization Bug ✅ COMPLETED
**Status:** Complete without tests
**Files Modified:** `src/harmony_modules/movement.py`

**Testing - Still to be done:**
```python
def test_scene_data_initialization():
    """Test that current_action is None when no action executing"""
    env = PluginTestEnvironment()
    controller = env.create_entity_controller('test_entity')
    
    # Request scene data when no action executing
    event = HarmonyLinkEvent('test', EVENT_TYPE_MOVEMENT_V1_REQUEST_SCENE_DATA, EVENT_STATE_NEW, {})
    controller.movementModule.handle_event(event)
    
    # Verify current_action is None for all characters
    # ... assertion code
```

**Details:** Fixed `current_action` field in scene data to properly return `None` when no action executing, only returns action name when `ActionState.EXECUTING`

**Note:** Scene data initialization tests should be included as part of the movement module test suite in Phase 3 (Step 3.1).

### Step 1.3: Create Action Registry System ✅ COMPLETED
**Status:** Complete without tests
**Files Created:** `src/harmony_modules/movement_actions.py` 
**Files Modified:** `src/harmony_modules/movement.py`, `src/harmony_modules/movement_animations.py`

**Testing - Still to be done:**
```python
def test_action_registry_loads_all_actions():
    """Test that ActionRegistry loads all actions from actions.json"""
    from movement_actions import get_all_actions, get_action_count
    
    actions = get_all_actions()
    assert len(actions) > 40, "Should load 40+ actions from actions.json"
    assert get_action_count() == len(actions)

def test_action_registry_get_by_name():
    """Test retrieving specific actions by name"""
    from movement_actions import get_action_by_name
    
    move_action = get_action_by_name('move')
    assert move_action is not None
    assert move_action['name'] == 'move'
    assert move_action['category'] == 'movement'

def test_action_registry_get_by_category():
    """Test retrieving actions by category"""
    from movement_actions import get_actions_by_category
    
    movement_actions = get_actions_by_category('movement')
    assert len(movement_actions) > 0
    assert all(action['category'] == 'movement' for action in movement_actions)
```

**Details:** Created centralized `ActionRegistry` that loads all 40+ actions from `actions.json`. Moved `ActionCategories` and `CompletionTypes` into the new module and provided helper functions for action lookup.

**Note:** Action registry tests should be included as part of the movement module test suite in Phase 3 (Step 3.1).

## Phase 2: Movement Code Enhancement (Week 2)

### Step 2.1: Refactor Code Organization and Enhance ActionExecutor with SpaceManager ✅ COMPLETED
**Status:** Complete without tests
**Files Created:** `src/harmony_modules/movement_tracking.py`
**Files Modified:** `src/harmony_modules/movement_actions.py`, `src/harmony_modules/movement.py`

**What Was Done:**
1. **Moved Classes to movement_actions.py:**
   - Extracted `ActionState`, `ActionInstance`, and `ActionExecutor` from movement.py
   - Centralized all action-related classes in one module
   - Updated imports across all modules

2. **Created SpaceManager in movement_tracking.py:**
   - Implemented 3D position and rotation tracking
   - Added distance calculation methods
   - Implemented target position resolution (supports explicit coords, entity names, object names)
   - Configured position tolerance (1.0 units) and rotation tolerance (5.0 degrees)
   - No pathfinding/navmesh (CharaStudio limitation)
   - No collision detection (prototype simplification)

3. **Integrated SpaceManager into ActionExecutor:**
   - Replaced duplicate position/distance methods with SpaceManager calls
   - Updated distance-based completion to use SpaceManager
   - Removed `_get_target_position()`, `_get_entity_position()`, `_get_object_position()`, `_calculate_distance()` methods

**Benefits:**
- Better code organization with clear separation of concerns
- Reduced code duplication
- Easier maintenance and testing
- Each module has focused responsibility

**Testing - To be added in Phase 3:**
- Test SpaceManager position/rotation getters with various character states
- Test distance calculation accuracy
- Test target position resolution from different sources
- Test ActionState transitions
- Test ActionInstance timing and lifecycle
- Test ActionExecutor with SpaceManager integration

### Step 2.2: Refactor Animation Mapping System 
**File to Modify:** `src/harmony_modules/movement_animations.py`

**Current Issues:**
- Hardcoded mappings in `_generate_dynamic_mappings()`
- Complex nested logic difficult to maintain
- Limited use of animation database
- No fallback strategy for missing animations

**Refactored Structure:**
```python
class AnimationMapper:
    def __init__(self):
        self.animation_database = self._load_animation_database()
        self.action_categories = self._define_action_categories()
        self.animation_mappings = self._generate_elegant_mappings()
        self.fallback_cache = {}
    
    def _load_animation_database(self):
        """Load and validate animation database"""
        # ... existing implementation but with better error handling
        
    def _define_action_categories(self):
        """Define clean category mappings"""
        # ... existing implementation but organized better
        
    def _generate_elegant_mappings(self):
        """Clean, maintainable mapping generation"""
        mappings = {}
        
        # Use strategy pattern for different mapping approaches
        mapping_strategies = {
            'movement': self._map_movement_actions,
            'posture': self._map_posture_actions, 
            'interaction': self._map_interaction_actions,
            'simple': self._map_simple_actions
        }
        
        for category, strategy_method in mapping_strategies.items():
            mappings.update(strategy_method())
            
        return mappings
    
    def _map_movement_actions(self):
        """Map movement actions using Walking & Running category"""
        mappings = {}
        actions = ['move', 'walk', 'run']
        
        # Find appropriate animations for each action
        for action in actions:
            animation = self._find_best_movement_animation(action)
            if animation:
                mappings[action] = animation
                
        return mappings
    
    def _map_posture_actions(self):
        """Map posture actions using appropriate categories"""
        mappings = {}
        posture_actions = {
            'sit_down': ('Chairs', 0),
            'stand_up': ('Standing', 0), 
            'lay_down': ('Laying', 0),
            'lean_against': ('Standing', 'Leaning On Wall')
        }
        
        for action, (category_name, animation_pattern) in posture_actions.items():
            animation = self._find_posture_animation(category_name, animation_pattern)
            if animation:
                mappings[action] = animation
                
        return mappings
    
    def _find_best_movement_animation(self, action_name):
        """Intelligently find best animation for movement action"""
        # Implementation details...
        
    def _find_posture_animation(self, category_name, animation_pattern):
        """Find appropriate posture animation"""
        # Implementation details...
        
    def get_animation_mapping(self, action_name):
        """Get mapping with fallback strategy"""
        if action_name in self.animation_mappings:
            return self.animation_mappings[action_name]
            
        # Try to generate mapping dynamically
        dynamic_mapping = self._generate_dynamic_mapping(action_name)
        if dynamic_mapping:
            return dynamic_mapping
            
        # Return safe fallback
        return self._get_fallback_mapping()
```


### Step 2.3: Add Movement Validation System
**File to Create:** `src/harmony_modules/movement_validator.py`

**Implementation:**
```python
class MovementValidator:
    """Validates that movement actions execute animations properly"""
    
    def __init__(self):
        self.validation_results = []
        self.animation_execution_times = {}
    
    def validate_action_execution(self, action_instance, chara):
        """Validate that an action properly executes an animation"""
        validation_result = {
            'action_name': action_instance.name,
            'start_time': time.time(),
            'animation_started': False,
            'animation_completed': False,
            'position_changed': False,
            'errors': []
        }
        
        try:
            # Check if animation actually started
            initial_animation = self._get_current_animation(chara)
            
            # Monitor for animation start
            def check_animation_start():
                current_animation = self._get_current_animation(chara)
                if current_animation != initial_animation:
                    validation_result['animation_started'] = True
                    logger.debug(f"Animation started for action '{action_instance.name}': {current_animation}")
            
            # Schedule animation start check
            chara.entity_controller.game.set_timer(0.2, lambda g: check_animation_start())
            
            # Monitor position changes for movement actions
            if action_instance.name in ['move', 'walk', 'run']:
                initial_position = self._get_character_position(chara)
                
                def check_position_change():
                    current_position = self._get_character_position(chara)
                    if current_position and initial_position:
                        distance_moved = self._calculate_distance(initial_position, current_position)
                        if distance_moved > 0.1:  # Moved more than 0.1 units
                            validation_result['position_changed'] = True
                
                chara.entity_controller.game.set_timer(1.0, lambda g: check_position_change())
            
            # Store validation result for later checking
            self.validation_results.append(validation_result)
            
        except Exception as e:
            validation_result['errors'].append(str(e))
            logger.error(f"Error during movement validation: {e}")
    
    def get_validation_summary(self):
        """Get summary of validation results"""
        if not self.validation_results:
            return {"message": "No validations performed"}
            
        total_validations = len(self.validation_results)
        successful_animations = sum(1 for r in self.validation_results if r['animation_started'])
        successful_movements = sum(1 for r in self.validation_results if r['position_changed'])
        
        return {
            "total_validations": total_validations,
            "animation_success_rate": successful_animations / total_validations,
            "movement_success_rate": successful_movements / total_validations,
            "errors": [r['errors'] for r in self.validation_results if r['errors']]
        }
```

## Phase 3: Integration & Testing (Week 3)

### Step 3.1: Create Movement-Specific Tests
**Files to Create:**
- `tests/unit/test_movement_actions.py` - Test ActionState, ActionInstance, ActionExecutor classes
- `tests/unit/test_movement_tracking.py` - Test SpaceManager class
- `tests/unit/test_movement_enhanced.py` - Test complete movement module integration
- `tests/unit/test_movement_animations_refactored.py`
- `tests/unit/test_movement_validator.py`
- `tests/integration/test_movement_3d_operations.py`

**Test Hints for Completed Work (Phase 2.1):**

**tests/unit/test_movement_actions.py:**
```python
# Test ActionState enum values
def test_action_state_values():
    """Verify all ActionState values are defined"""
    assert ActionState.QUEUED == "queued"
    assert ActionState.EXECUTING == "executing"
    assert ActionState.COMPLETED == "completed"
    assert ActionState.FAILED == "failed"
    assert ActionState.TIMEOUT == "timeout"

# Test ActionInstance lifecycle
def test_action_instance_lifecycle():
    """Test ActionInstance state transitions"""
    action = ActionInstance("walk", targets=[{"position": [1, 0, 1]}])
    assert action.state == ActionState.QUEUED
    
    action.start_execution(expected_duration=2.0)
    assert action.state == ActionState.EXECUTING
    assert action.start_time is not None
    
    duration = action.complete_execution(success=True)
    assert action.state == ActionState.COMPLETED
    assert action.actual_duration is not None

# Test ActionInstance timeout detection
def test_action_instance_timeout():
    """Test timeout detection for stuck actions"""
    action = ActionInstance("move")
    action.max_execution_time = 0.1  # 100ms for testing
    action.start_execution()
    time.sleep(0.2)
    assert action.is_timeout() == True

# Test ActionExecutor initialization with SpaceManager
def test_action_executor_initialization():
    """Test ActionExecutor properly initializes with SpaceManager"""
    env = PluginTestEnvironment()
    controller = env.create_entity_controller('test_entity')
    
    executor = controller.movementModule.action_executor
    assert executor.space_manager is not None
    assert hasattr(executor.space_manager, 'get_character_position')
    assert hasattr(executor.space_manager, 'calculate_distance')
```

**tests/unit/test_movement_tracking.py:**
```python
# Test SpaceManager position retrieval
def test_space_manager_get_position():
    """Test position retrieval from character"""
    env = PluginTestEnvironment()
    space_manager = SpaceManager()
    
    # Create mock character with position
    mock_actor = env.create_mock_character_actor('test')
    mock_actor.pos = MockVector3(5.0, 0.0, 10.0)
    chara = Chara(mock_actor)
    
    position = space_manager.get_character_position(chara)
    assert position == (5.0, 0.0, 10.0)

# Test SpaceManager with invalid character
def test_space_manager_get_position_invalid_character():
    """Test position retrieval handles None character"""
    space_manager = SpaceManager()
    position = space_manager.get_character_position(None)
    assert position is None

# Test distance calculation
def test_space_manager_calculate_distance():
    """Test 3D distance calculation"""
    space_manager = SpaceManager()
    pos1 = (0.0, 0.0, 0.0)
    pos2 = (3.0, 4.0, 0.0)
    
    distance = space_manager.calculate_distance(pos1, pos2)
    assert abs(distance - 5.0) < 0.01  # 3-4-5 triangle

# Test position reached check
def test_space_manager_is_position_reached():
    """Test position reached detection with threshold"""
    space_manager = SpaceManager()
    current = (0.0, 0.0, 0.0)
    target = (0.5, 0.5, 0.0)
    
    # Within threshold (1.0)
    assert space_manager.is_position_reached(current, target) == True
    
    target_far = (2.0, 2.0, 0.0)
    # Outside threshold
    assert space_manager.is_position_reached(current, target_far) == False

# Test target position resolution from explicit coordinates
def test_space_manager_resolve_target_explicit():
    """Test resolving target position from explicit coordinates"""
    env = PluginTestEnvironment()
    space_manager = SpaceManager()
    
    targets = [{"position": [10.0, 0.0, 5.0]}]
    position = space_manager.resolve_target_position(targets, env.entity_controller)
    assert position == (10.0, 0.0, 5.0)

# Test target position resolution from entity name
def test_space_manager_resolve_target_from_entity():
    """Test resolving target position from named entity"""
    env = PluginTestEnvironment()
    space_manager = SpaceManager()
    
    # Create target entity at known position
    target_controller = env.create_entity_controller('target_entity')
    mock_actor = env.create_mock_character_actor('target_entity')
    mock_actor.pos = MockVector3(15.0, 0.0, 20.0)
    target_controller.update_chara(Chara(mock_actor))
    
    targets = [{"name": "target_entity"}]
    position = space_manager.resolve_target_position(targets, env.entity_controller)
    assert position == (15.0, 0.0, 20.0)

# Test target position resolution from object name
def test_space_manager_resolve_target_from_object():
    """Test resolving target position from named object/prop"""
    env = PluginTestEnvironment()
    space_manager = SpaceManager()
    
    # Register a prop at known position
    mock_prop = MockObject()
    mock_prop.pos = MockVector3(7.0, 0.0, 3.0)
    env.entity_controller.game.scenedata.registered_props['test_prop'] = mock_prop
    
    targets = [{"name": "test_prop"}]
    position = space_manager.resolve_target_position(targets, env.entity_controller)
    assert position == (7.0, 0.0, 3.0)
```

**Test Implementation Example for Overall Movement:**
```python
def test_movement_action_animation_execution():
    """Test that movement actions properly execute animations"""
    env = PluginTestEnvironment()
    env.setup_environment()
    
    controller = env.create_entity_controller('test_entity')
    validator = MovementValidator()
    
    # Create test ActionGraph with movement action
    action_graph = {
        'graph_id': 'test_movement',
        'graph_actor': 'test_entity', 
        'graph_vector': [
            {
                'action': 'walk',
                'targets': [{'name': 'target_location', 'position': [5.0, 0.0, 5.0]}],
                'transition_mode': 'linear'
            }
        ]
    }
    
    # Execute action with validation
    controller.movementModule._execute_action_graph(action_graph)
    
    # Wait for execution
    time.sleep(3)
    
    # Check validation results
    summary = validator.get_validation_summary()
    assert summary['animation_success_rate'] > 0.8, "Most animations should execute successfully"
    assert summary['movement_success_rate'] > 0.8, "Most movements should change position"
```

### Step 3.2: Validate 3D Space Operations
**Integration Test Example:**
```python
def test_3d_position_tracking_accuracy():
    """Test that position tracking works accurately"""
    env = PluginTestEnvironment()
    controller = env.create_entity_controller('position_test')
    
    # Create character at known position
    mock_actor = env.create_mock_character_actor('position_test')
    mock_actor.pos = MockVector3(0.0, 0.0, 0.0)
    controller.update_chara(Chara(mock_actor))
    
    # Execute movement to known target
    action_graph = {
        'graph_id': 'position_test',
        'graph_actor': 'position_test',
        'graph_vector': [
            {
                'action': 'move',
                'targets': [{'position': [10.0, 0.0, 0.0]}],
                'transition_mode': 'linear'
            }
        ]
    }
    
    controller.movementModule._execute_action_graph(action_graph)
    
    # Wait for completion
    time.sleep(5)
    
    # Verify final position is accurate
    final_pos = controller.movementModule.action_executor.space_manager.get_character_position(controller.chara)
    expected_pos = (10.0, 0.0, 0.0)
    
    distance_from_target = controller.movementModule.action_executor.space_manager.calculate_distance(
        final_pos, expected_pos
    )
    
    assert distance_from_target < 1.5, f"Character should be within 1.5 units of target, was {distance_from_target}"
```

## Phase 4: Polish & Documentation (Week 4)

### Step 4.1: Update Memory Bank
**Files to Update:**
- `memory-bank/activeContext.md` - Document all changes and current state
- `memory-bank/progress.md` - Update completion status

### Step 4.2: Create Implementation Summary
**File to Create:** `MOVEMENT_IMPLEMENTATION_README.md`

## Success Metrics

### Measurable Outcomes
- **Action Registration**: All 25+ actions from actions.json properly registered
- **Scene Data Bug**: current_action field returns None when no action executing
- **Animation Execution**: >95% of actions successfully play animations
- **Position Accuracy**: Movement actions reach within 1.0 units of target
- **Test Coverage**: >90% for all movement-related code
- **Performance**: <500ms average action execution time maintained

### Validation Commands
```bash
# Run movement-specific tests
ipy -X:Frames tests/unit/test_movement_enhanced.py
ipy -X:Frames tests/unit/test_movement_animations_refactored.py

# Run integration tests
ipy -X:Frames tests/integration/test_movement_3d_operations.py

# Validate animation database usage
ipy -X:Frames -c "
from src.harmony_modules.movement_animations import AnimationMapper
mapper = AnimationMapper()
print(f'Total mappings: {len(mapper.animation_mappings)}')
print(f'Categories covered: {len(set([mapper.get_action_category(k) for k in mapper.animation_mappings.keys()]))}')
"
