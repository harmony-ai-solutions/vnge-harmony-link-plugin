# VNGE Harmony Link Plugin - Tech Context

## Technologies and Frameworks Used

### Core Technologies
- **IronPython 2.7**: Plugin scripting language for VNGE integration
- **VNGE Engine**: Visual Novel Game Engine (target platform)
- **WebSocket**: Real-time communication with Harmony Link
- **JSON**: Data serialization for events and configuration

### VNGE Integration
- **Character Animation System**: `chara.actor.animate2(group, category, no, speed)`
- **Game Timing**: `game.set_timer(duration, callback)` for action duration
- **Scene Management**: Character positioning and object tracking
- **Plugin Architecture**: VNGE's IronPython plugin system

### Communication Protocols
- **WebSocket Client**: Bidirectional real-time communication
- **Event-Based Messaging**: Structured JSON event payloads
- **Harmony Link Events**: Standardized event types and schemas

### Data Formats
- **JSON**: Event payloads, configuration, animation mappings
- **ActionGraphV1**: Harmony Link's action execution format
- **Animation Mappings**: VNGE-specific animation parameter structure

### External Dependencies

#### VNGE Engine APIs
- **Studio.Info**: Animation database access for `animation_list.json` generation
- **vngameengine**: Core game engine functionality and timing
- **vnlibfaceexpressions**: Facial expression configurations
- **vnactor**: Character action and animation functions

#### Harmony Link Integration
- **harmony_modules.common**: Base classes and event handling
- **HarmonyClientModuleBase**: Plugin base class for Harmony Link integration
- **HarmonyLinkEvent**: Event structure for communication

### Development Constraints

#### IronPython 2.7 Limitations
- **Python 2.7 Syntax**: Use `.format()` instead of f-strings
- **Limited Standard Library**: Reduced compared to CPython
- **.NET Integration**: Direct access to .NET/VNGE systems
- **Performance**: Interpreted execution within .NET runtime

#### VNGE Engine Constraints
- **Animation System**: Limited to predefined animation groups/categories
- **Timing System**: Game-based timing, not system-based
- **Thread Safety**: Single-threaded execution model
- **Plugin Lifecycle**: Managed by VNGE engine startup/shutdown

### Performance Considerations

#### Real-Time Requirements
- **Sub-second Response**: ActionGraph → animation execution
- **Memory Efficiency**: Minimal memory footprint for continuous operation
- **CPU Optimization**: Efficient event processing and action execution
- **Network Latency**: WebSocket communication overhead minimization

#### Optimization Techniques
- **Caching**: Animation mappings and character references
- **Lazy Loading**: Performance statistics and history
- **Batch Processing**: Multiple actions in single execution cycle
- **Resource Management**: Proper cleanup and memory management

### Configuration Management
- **Debug Modes**: 0=none, 1=ActionGraph logging, 2=animation export
- **Timing Configuration**: Timeout values, inter-action delays
- **Performance Tuning**: History size, monitoring intervals
- **Animation Mapping**: Hardcoded with expansion capability

### Integration Architecture

#### WebSocket Communication
```python
# Event handling pattern
def handle_event(self, event):
    if event.event_type == EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS:
        self._execute_action_graph(event.payload)
```

#### VNGE Animation Execution
```python
# Direct VNGE API usage
self.chara.actor.animate2(
    mapping["group"],     # Animation group ID
    mapping["category"],  # Category within group
    mapping["no"],        # Specific animation number
    mapping["speed"]      # Animation speed multiplier
)
```

#### Action State Management
```python
# State tracking pattern
action_instance.start_execution(expected_duration)
action_instance.state = ActionState.EXECUTING
# ... execute animation ...
action_instance.complete_execution(success=True)
```

### Debugging and Monitoring

#### Logging System
- **Structured Logging**: Consistent format for troubleshooting
- **Action Tracing**: Full action lifecycle tracking
- **Performance Metrics**: Execution times, success rates
- **Error Reporting**: Detailed error information and stack traces

#### Debug Tools
- **Animation List Export**: Complete VNGE animation database
- **Execution Statistics**: Performance monitoring and optimization
- **Action History**: Recent action tracking for debugging
- **State Inspection**: Real-time action queue and execution status

### Future Technology Considerations

#### Scalability
- **Multiple Characters**: Concurrent character animation support
- **Complex Sequences**: Multi-action choreography and coordination
- **Performance Optimization**: Faster action execution and lower latency

#### Extensibility
- **Animation Expansion**: Dynamic loading from animation_list.json
- **New Action Types**: Facial expressions, character interactions
- **Advanced Features**: Transition modes, complex targeting systems
- **Integration Points**: Additional VNGE systems and capabilities

### Security and Reliability

#### Error Handling
- **Graceful Degradation**: Continue operation if individual actions fail
- **Timeout Management**: Prevent infinite waiting on stuck animations
- **State Recovery**: Clean recovery from error conditions
- **Resource Cleanup**: Proper disposal of resources and references

#### Validation
- **Input Sanitization**: ActionGraph payload validation
- **Configuration Validation**: Safe parameter ranges and values
- **State Consistency**: Ensure action state transitions are valid
- **Performance Bounds**: Prevent resource exhaustion scenarios
