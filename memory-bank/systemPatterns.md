# VNGE Harmony Link Plugin - System Patterns

## System Architecture

### Core Architecture Pattern: State-Managed Action Execution
- **Event-Driven Processing**: React to ActionGraphs from Harmony Link
- **State Machine Pattern**: Track action lifecycle from queue to completion
- **Command Pattern**: Actions as executable commands with timing
- **Observer Pattern**: Monitor execution progress and performance

### Key Components

#### 1. ActionInstance (`movement.py`)
- **Pattern**: State Machine + Command
- **Purpose**: Represent individual actions with state and timing
- **States**: QUEUED → EXECUTING → COMPLETED/FAILED/TIMEOUT
- **Features**: Timing control, timeout detection, performance tracking

#### 2. ActionExecutor (`movement.py`)
- **Pattern**: Strategy + Template Method
- **Purpose**: Execute different types of actions using VNGE animation system
- **Strategies**: Movement actions, posture actions, simple actions
- **Template**: Common execution flow with specialized implementations

#### 3. AnimationMapper (`movement.py`)
- **Pattern**: Registry + Factory
- **Purpose**: Map abstract action names to concrete VNGE animation parameters
- **Structure**: `{"group": int, "category": int, "no": int, "duration": float, "speed": float}`
- **Extensibility**: Hardcoded mappings expandable to animation_list.json analysis

#### 4. MovementHandler (`movement.py`)
- **Pattern**: Facade + Event Handler
- **Purpose**: Main coordination point for all movement-related functionality
- **Responsibilities**: Queue management, event handling, performance monitoring
- **Integration**: Bridge between Harmony Link events and VNGE execution

## Key Technical Decisions

### 1. IronPython for VNGE Integration
**Rationale**:
- Native integration with .NET-based VNGE engine
- Access to VNGE's character animation APIs
- Plugin architecture support within VNGE ecosystem
- Python familiarity for rapid development

### 2. State Machine for Action Tracking
**Rationale**:
- Clear action lifecycle management for debugging
- Enables timeout detection and recovery
- Supports performance monitoring and statistics
- Provides foundation for complex action sequences

### 3. Sequential Action Execution
**Rationale**:
- Natural character behavior flow
- Prevents animation conflicts and overlaps
- Simpler state management than parallel execution
- Easier debugging and troubleshooting

### 4. Event-Based Communication
**Rationale**:
- Decoupled from Harmony Link internal changes
- Standard WebSocket protocol for reliability
- Language-agnostic communication interface
- Supports bidirectional data exchange

## Design Patterns in Use

### 1. State Machine Pattern (ActionInstance)
```python
class ActionState:
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
```

### 2. Command Pattern (ActionGraph Execution)
- Actions encapsulated as executable commands
- Supports queuing, timing, and rollback
- Enables complex action sequences and coordination

### 3. Template Method Pattern (ActionExecutor)
```python
def execute_action(self, action_instance):
    # Common setup
    self._setup_timeout_monitoring(action_instance)
    # Specialized execution
    self._execute_specific_action_type(action_instance)
    # Common cleanup
    self._handle_completion(action_instance)
```

### 4. Registry Pattern (AnimationMapper)
- Central registry of action → animation mappings
- Supports dynamic lookup and registration
- Extensible for new action types

### 5. Observer Pattern (Performance Monitoring)
- Execution statistics collection
- Action history tracking
- Event-based progress reporting

## Component Relationships

### Data Flow Architecture
```
Harmony Link ActionGraph → WebSocket Event → 
MovementHandler → ActionInstance Queue → 
ActionExecutor → VNGE Animation System → 
Character Animation → Completion Callback
```

### State Flow
```
ActionGraph Received → Actions Queued (QUEUED) → 
Action Starts (EXECUTING) → Animation Triggered → 
Timer Set → Completion/Timeout → State Updated → 
Next Action or Queue Empty
```

### Integration Points
- **Harmony Link**: WebSocket event communication
- **VNGE Engine**: Character animation system (`animate2()`)
- **Game Timer**: Action duration and timeout management
- **Scene System**: Character positioning and state

## Error Handling Patterns

### 1. Graceful Degradation
- Continue processing queue if individual actions fail
- Fallback behaviors for missing animation mappings
- Timeout recovery without system crash

### 2. Circuit Breaker Pattern
- Action timeout detection and automatic failure
- Prevention of infinite waiting on stuck animations
- Automatic queue progression after failures

### 3. State-Based Recovery
- Clear action state tracking for recovery decisions
- Performance history for identifying problematic patterns
- Configurable retry policies for transient failures

## Performance Patterns

### 1. Lazy Loading
- Animation mappings loaded on first use
- Performance statistics calculated incrementally
- History trimmed to configurable size limits

### 2. Batching
- Multiple actions queued and processed sequentially
- Efficient WebSocket event handling
- Bulk scene data updates

### 3. Caching
- Animation mapping lookups cached in memory
- Character reference stored for repeated use
- Configuration values cached to avoid repeated parsing

## VNGE Integration Patterns

### 1. Native API Usage
```python
# Direct VNGE character animation
self.chara.actor.animate2(group, category, no, speed)

# Game timing system integration
game.set_timer(duration, callback)
```

### 2. Scene Data Coordination
- Character position and orientation tracking
- Object and prop state management
- Real-time scene information updates

### 3. Plugin Lifecycle Management
- Initialization with character reference updates
- Cleanup and resource management
- Configuration and debug mode handling
