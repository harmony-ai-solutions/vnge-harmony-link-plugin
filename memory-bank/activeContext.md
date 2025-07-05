# VNGE Harmony Link Plugin - Active Context

## Current Work Focus
The primary focus is on enhancing the Movement module's execution and refining plugin integration. This includes addressing issues with scene data initialization and implementing advanced target handling features.

## Recent Changes
- **Enhanced Action Management**: Implemented comprehensive state management with timing control, timeout detection, and performance tracking for actions.
- **Animation Execution System**: Improved animation execution with timeout management and graceful error handling.
- **Development Infrastructure**: Enhanced debug modes, animation list export, and performance statistics.

## Next Steps
- **Scene Data Fixes**: Address the issue where scene data returns a complex `current_action` instead of `None` during initialization.
- **Animation Mapping Enhancement**: Expand animation mappings by leveraging the complete `animation_list.json` database for full animation support.
- **Target Handling**: Implement `look_at_target` and `requires_consent` features.
- **Transition Modes**: Add support for various transition modes (linear, sinus, etc.).

## Active Decisions and Considerations
- Ensuring seamless and real-time execution of ActionGraphs within the VNGE environment.
- Providing robust error handling and performance monitoring for character animations.
- Expanding the plugin's capabilities to support more complex and natural character behaviors.

## Important Patterns and Preferences
- **IronPython 2.7**: Continued use for VNGE integration.
- **WebSocket**: Primary communication protocol with Harmony Link.
- **State Machine Pattern**: Used for tracking action lifecycle.
- **Command Pattern**: Actions encapsulated as executable commands.

## Learnings and Project Insights
- The enhanced action management system significantly improves the reliability and debuggability of character animations.
- Addressing scene data initialization is crucial for accurate state representation within Harmony Link.
- Leveraging the full `animation_list.json` will greatly expand the range of character behaviors the plugin can execute.
