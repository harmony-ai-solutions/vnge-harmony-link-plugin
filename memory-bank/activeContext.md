# VNGE Harmony Link Plugin - Active Context

## Current Work Focus
**JUST COMPLETED**: STT Recording Synchronization Enhancement - Implemented synchronization improvements to resolve button spam issues and ensure reliable audio frame processing between VNGE Plugin and Harmony Link.

**JUST COMPLETED**: TTS Audio Playback Timing Fix - Fixed critical audio playback issue where TTS audio would not play due to race condition in playback monitoring.

**JUST COMPLETED**: Created a configurable logging wrapper system to replace all print() statements throughout the VNGE Harmony Link Plugin codebase.

**JUST COMPLETED**: Movement Module Enhancement - Implemented actual movement features for Harmony Link's VNGE Plugin, transforming the current stub implementation into a fully functional system. This includes dynamic animation duration detection, intelligent animation mapping, hard error handling for animation database issues, and distance-based completion detection for movement actions. The implementation is still subject to further review and modifications in the follow-up sessions.

**CURRENT STATUS**: Core STT and TTS functionality now working reliably with proper synchronization. Logging system is implemented and partially deployed. Core infrastructure complete, with ~50% of print statements converted to proper logging calls. Remaining work involves systematic replacement of print statements across all remaining modules.

**PREVIOUS MAJOR COMPLETION**: Entity Setup Enhancement - Comprehensive automated entity setup system that eliminates manual configuration requirements for users.

The focus continues on enhancing the Movement module's execution and refining plugin integration.

### Animation System Extension (Priority: High)
The current implementation has hardcoded animation mappings in `AnimationMapper._load_animation_mappings()`. With the comprehensive `animation_list_short.json` available, the next major step is extending the system to dynamically utilize the full VNGE animation database.

**Current Hardcoded Mappings:**
- Basic movement: move, walk, run
- Posture: sit_down, stand_up, lay_down  
- Simple: jump_fixed

**Animation Database Structure (from animation_list_short.json):**
- Group 0 "Character": Basic, Pose, Emotions, Walking & Running, Standing, Conversation, etc.
- Group 8 "Battle": Combat animations
- Group 10 "Outdoors": Swimming, sports activities
- Group 1011 "Kohai": Extensive Mixamo animation library

### Animation Duration Detection Challenge
**Critical Issue:** Currently unable to determine actual animation duration from VNGE/Unity runtime. Current system uses hardcoded expected durations in mappings (e.g., `"duration": 3.0`), but actual animation lengths are unknown.

**Current Workaround:**
- Timeout detection (10 seconds max) prevents stuck animations
- Fixed duration estimates for action completion timing
- Performance monitoring tracks actual vs expected execution times

**Potential Solutions to Investigate:**
1. VNGE API exploration for animation duration queries
2. Unity AnimationClip.length property access via IronPython
3. Timing analysis based on animation file metadata
4. Dynamic duration learning from execution patterns

### Cognitive Integration Stubs (Recently Added)
The `CognitiveIntegrationStub` class provides framework for future AI entity cognitive system integration:
- Simple consent logic based on action intimacy levels
- Relationship and subjective context processing hooks
- Decision request handling with structured responses

## Recent Changes

### ✅ STT Recording Synchronization Enhancement (Just Completed)
**Description**: Implemented comprehensive synchronization improvements to resolve button spam issues and ensure reliable audio frame processing between VNGE Plugin and Harmony Link.

**Root Cause**: Users spamming the toggle recording button caused race conditions where recording could stop in the middle of processing an audio frame being fetched by Harmony Link. The plugin lacked the sophisticated multi-lock approach used by Harmony Link, leading to potential lockups and lost audio frames.

**Key Changes:**

#### STT Module Enhancements (`speech_to_text.py`):
- **Multi-lock Synchronization System**: Added `operation_lock`, `recording_state_lock`, and `processing_lock` to prevent race conditions
- **Graceful Frame Completion**: When stop is requested, current audio frames complete naturally and send actual audio data to Harmony Link (no empty chunks)
- **Pending Chunk Tracking**: `pending_audio_chunks` dictionary tracks active audio processing with timestamps
- **Enhanced Start/Stop Methods**: `start_listen()` and `stop_listen()` with comprehensive error handling and state protection
- **Frame Completion Logic**: `_wait_for_current_frame_completion()` ensures all requested frames are processed before stopping

#### Controls Module Enhancements (`controls.py`):
- **Button Operation Locking**: Per-button locks prevent rapid clicking with `_acquire_button_lock()` and `_release_button_lock()`
- **State Validation System**: Periodic validation (every 2 seconds) ensures button text matches actual recording state
- **Recovery Mechanisms**: `_recover_desynchronized_state()` automatically detects and corrects button/state mismatches
- **Enhanced Toggle Method**: `toggle_record_microphone()` with full synchronization protection and error recovery
- **Code Quality**: Extracted all hardcoded button text strings into centralized constants for maintainability

**Technical Solution:**
- **Operation Lock Protection**: Prevents overlapping start/stop operations and button spam
- **Graceful Shutdown**: Waits for current audio chunks to complete naturally (up to 3 seconds timeout)
- **Real Data Preservation**: Sends actual audio data to Harmony Link instead of generating empty chunks
- **State Synchronization**: Button display state always matches actual recording state
- **Comprehensive Logging**: Added detailed logging for debugging synchronization issues

**Files Modified:**
- `harmony_modules/speech_to_text.py`: Enhanced with multi-lock synchronization system
- `harmony_modules/controls.py`: Added button state management and validation system

**Impact:**
- **No Lost Audio Frames**: All requested frames are processed and sent to Harmony Link
- **Button Spam Protection**: Rapid clicking no longer causes race conditions or lockups
- **State Consistency**: Button text always accurately reflects actual recording state
- **Robust Error Recovery**: System gracefully handles all error conditions and network issues
- **Improved User Experience**: Reliable recording operation under all user interaction patterns

### ✅ TTS Audio Playback Timing Fix (Just Completed)
**Description**: Fixed critical audio playback issue where TTS audio would not play due to a race condition in the playback monitoring thread.

**Root Cause**: The `TTSProcessorThread.wait_voice_played()` method was checking `isPlaying` status immediately after calling `Play()`, before the VNGE audio system had time to initialize the audio stream. This caused the monitoring thread to think playback was already complete and immediately trigger cleanup, resulting in no audible audio.

**Key Changes:**
- **Added Playback State Tracking**: Enhanced `TTSProcessorThread` with `playback_started`, `start_time`, and `min_playback_duration` fields
- **Initialization Delay Logic**: Implemented minimum wait time (0.5 seconds) before considering playback complete if audio hasn't started
- **Startup Detection**: Track when audio actually begins playing vs when `Play()` is called
- **Enhanced Logging**: Added debug logging for playback start/completion and warning for potential failures
- **Timing Analysis**: Monitor elapsed time from `Play()` call to actual completion for debugging

**Technical Solution:**
- **Race Condition Prevention**: Wait for audio system initialization before accepting `isPlaying = False` as completion
- **State Machine Enhancement**: Track playback lifecycle: `Play()` called → audio started → audio completed
- **Graceful Degradation**: If audio never starts playing, still complete after minimum duration to prevent hanging
- **Performance Monitoring**: Log actual playback duration for debugging and optimization

**Files Modified:**
- `harmony_modules/text_to_speech.py`: Enhanced `TTSProcessorThread` class with robust timing logic

**Impact:**
- **Fixed Audio Playback**: TTS audio now plays reliably instead of being immediately skipped
- **Improved Debugging**: Enhanced logging provides visibility into audio system timing
- **Robust Error Handling**: System gracefully handles cases where audio fails to start
- **Better User Experience**: Characters now properly speak generated audio content

### ✅ Entity Setup Enhancement (Just Completed)
**Description**: Comprehensive automated entity setup system that eliminates manual configuration requirements for users.

**Key Achievements:**
- **Backend Infrastructure**: Added `FETCH_CONFIGURED_ENTITIES` event type to Harmony Link and common.py for entity discovery
- **Entity Discovery Module**: Created `entity_discovery.py` with temporary connector and robust error handling
- **Visual Setup Dialog**: Implemented Unity GUI dialog with pre-population of existing mappings
- **Enhanced Status Indicators**: Four distinct visual states for mapping clarity:
  - **Dark Green**: Previously tagged entities (from VNGE registry)
  - **Blue**: Exact name matches (automatic detection)
  - **Yellow**: Manual selections (user-configured)
  - **Red**: Unmapped entities (requiring attention)
- **Smart Pre-population**: Leverages `game.scenef_get_all_actors()` to detect existing `-actor:` tags
- **Priority System**: Existing tags > exact matches > manual selection
- **Startup Integration**: Seamlessly integrated into plugin initialization with backward compatibility

**Technical Insights:**
- **VNGE Infrastructure Leverage**: Used existing `scenef_register_actorsprops()` and `scenef_get_all_actors()` instead of manual folder scanning
- **Temporary Connector Pattern**: Port offset strategy (base + 100) prevents conflicts with main entity connections
- **Visual Feedback Design**: Color-coded status indicators provide immediate clarity about mapping sources
- **User Experience Priority**: Always shows dialog to allow configuration experimentation and flexibility

**Files Created/Modified:**
- `harmony_modules/entity_discovery.py`: Entity discovery with temporary connector
- `harmony_modules/entity_setup_dialog.py`: Unity GUI dialog with pre-population logic
- `harmony.py`: Startup flow integration with entity setup detection
- `harmony_modules/common.py`: New event type

- **Enhanced Action Management**: Implemented comprehensive state management with timing control, timeout detection, and performance tracking for actions.
- **Animation Execution System**: Improved animation execution with timeout management and graceful error handling.
- **Development Infrastructure**: Enhanced debug modes, animation list export, and performance statistics.

### ✅ Movement Module Enhancement (Just Completed)
**Description**: Implemented actual movement features for Harmony Link's VNGE Plugin, transforming the current stub implementation into a fully functional system.

**Key Achievements:**
- **Dynamic Animation Duration Detection**: Implemented using `AnimationDurationDetector` to get actual animation clip lengths from Unity's `RuntimeAnimatorController`.
- **Intelligent Animation Mapping**: Replaced hardcoded animation mappings with a dynamic system that maps `movement_definitions.py` actions to VNGE animations using name-based lookups from `animation_list_short.json`.
- **Hard Error Handling for Animation DB**: Removed fallback mechanisms and implemented hard error throwing for animation database issues, ensuring the system fails fast on configuration problems.
- **Distance-Based Completion Detection**: Implemented for movement actions (move, walk, run), replacing fixed timers with real-time position monitoring and a 1.0 unit (~1 meter) threshold.
- **Pylance Errors Resolved**: All Pylance errors related to null-checking and incorrect method names have been fixed.

**Technical Insights:**
- **Real-time Position Monitoring**: Checks character position every 100ms for movement completion.
- **Target Position Detection**: Supports explicit coordinates, named entities, and scene objects.
- **Animation Duration Caching**: Caches detected durations for performance optimization.
- **Comprehensive Error Handling**: Graceful fallbacks and detailed logging throughout.

**Files Modified:**
- `harmony_modules/movement.py`: Enhanced ActionExecutor with dynamic duration detection and distance-based completion.
- `harmony_modules/movement_animations.py`: New module for animation duration detection.
- `harmony_modules/movement_definitions.py`: Centralized action definitions.

**Impact:**
- **Accurate Animation Timing**: Animations now run for their actual duration, improving realism.
- **Precise Movement Completion**: Characters stop precisely at their destination, eliminating fixed-timer approximations.
- **Robust Configuration**: System fails fast on animation database issues, preventing silent failures.
- **Improved Debugging**: Detailed logging for animation duration and movement completion.

### Enhanced ActionInstance State Management
- Comprehensive state tracking (QUEUED → EXECUTING → COMPLETED/FAILED/TIMEOUT)
- Timing control with start/expected/actual duration tracking
- Performance monitoring with execution statistics
- Error resilience with graceful failure handling

### Cognitive Integration Framework
- Added `CognitiveIntegrationStub` for future AI system integration
- Implemented `_process_cognitive_context()` in action graph execution
- Enhanced target processing with relationship and subjective context support
- Decision-making framework for consent and interaction decisions

## Next Steps
- **Scene Data Fixes**: Address the issue where scene data returns a complex `current_action` instead of `None` during initialization.
- **Animation Mapping Enhancement**: Expand animation mappings by leveraging the complete `animation_list.json` database for full animation support.
- **Target Handling**: Implement `look_at_target` and `requires_consent` features.
- **Transition Modes**: Add support for various transition modes (linear, sinus, etc.).

### Immediate (1-2 weeks)
1. **Animation Mapping Expansion**
   - Analyze `animation_list_short.json` structure for programmatic mapping
   - Create mapping logic for Group 0 "Character" animations to movement_definitions actions
   - Implement dynamic animation discovery and selection

2. **Animation Duration Investigation**
   - Explore VNGE API for animation duration access
   - Investigate Unity AnimationClip properties accessible via IronPython
   - Implement duration estimation fallback mechanisms

### Short-term (2-4 weeks)
1. **Movement Definitions Integration**
   - Map complex actions from `movement_definitions.py` to appropriate VNGE animations
   - Implement character interaction animations (hand holding, caressing, kissing)
   - Add object interaction support (pick up, place, give/take items)

2. **Enhanced Target Handling**
   - Implement `look_at_target` functionality using VNGE character orientation
   - Complete `requires_consent` processing with cognitive decision integration
   - Add multi-character coordination for interaction animations

### Medium-term (1-2 months)
1. **Advanced Animation Features**
   - Implement transition modes (linear, sinus, curve) for smoother animations
   - Add facial expression coordination with Countenance module
   - Support complex action sequences and choreography

2. **Performance Optimization**
   - Dynamic animation caching for frequently used animations
   - Multi-character simultaneous animation support
   - Memory and CPU optimization for continuous operation

## Active Decisions and Considerations
- Ensuring seamless and real-time execution of ActionGraphs within the VNGE environment.
- Providing robust error handling and performance monitoring for character animations.
- Expanding the plugin's capabilities to support more complex and natural character behaviors.
- Maintaining reliable STT/TTS synchronization under all user interaction patterns.

## Important Patterns and Preferences
- **IronPython 2.7**: Continued use for VNGE integration.
- **WebSocket**: Primary communication protocol with Harmony Link.
- **State Machine Pattern**: Used for tracking action lifecycle.
- **Command Pattern**: Actions encapsulated as executable commands.
- **Multi-lock Synchronization**: Critical for preventing race conditions in audio processing.

### Architecture Decisions
- **Sequential Action Execution:** Maintains natural character behavior and avoids conflicts
- **State Machine Pattern:** Clear action lifecycle management with comprehensive debugging
- **Cognitive Integration Stubs:** Prepared interfaces for future AI system integration
- **Timeout Management:** Prevents infinite waiting with configurable timeout values
- **Synchronization-First Design:** Multi-lock approach prevents race conditions and ensures data integrity

### Technical Constraints
- **IronPython 2.7 Limitations:** Python 2.7 syntax, limited standard library access
- **VNGE Engine Integration:** Single-threaded execution, game-based timing system
- **Animation Duration Unknown:** Cannot determine actual animation length from runtime
- **Audio System Timing:** VNGE audio initialization requires careful timing consideration

### Performance Targets
- **Sub-second Response:** ActionGraph reception to animation start
- **95%+ Success Rate:** Reliable action execution with graceful error handling
- **<500ms Execution:** Average action processing and initiation time
- **Minimal Memory Usage:** Efficient resource management for continuous operation
- **Zero Lost Audio Frames:** All requested audio chunks processed and delivered to Harmony Link

## Learnings and Project Insights
- The enhanced action management system significantly improves the reliability and debuggability of character animations.
- Addressing scene data initialization is crucial for accurate state representation within Harmony Link.
- Leveraging the full `animation_list.json` will greatly expand the range of character behaviors the plugin can execute.
- Proper synchronization is critical for reliable STT operation - multi-lock approaches prevent race conditions effectively.
- Audio system timing requires careful consideration of initialization delays and state transitions.

### VNGE Animation System Understanding
- Animation hierarchy: Group → Category → Animation Item (with index)
- `animate2()` method requires: group_id, category_id, animation_no, speed
- Animation database comprehensively cataloged in `animation_list.json`
- Extensive Mixamo library available in Group 1011 "Kohai"

### ActionGraph Integration Success
- Real-time WebSocket communication working reliably
- Event-driven architecture scales well for complex action sequences
- Cognitive integration hooks provide clean expansion points
- State management enables robust debugging and monitoring

### STT/TTS Synchronization Success
- Multi-lock synchronization prevents race conditions effectively
- Graceful frame completion ensures no data loss to Harmony Link
- Button state validation provides reliable user interface feedback
- Audio timing considerations are critical for proper playback

### Performance Characteristics
- Action queue processing handles multiple simultaneous requests
- Timeout detection prevents system lockup from stuck animations
- Performance monitoring provides insights for optimization
- Error recovery maintains system stability during failures
- Audio frame processing completes reliably under all user interaction patterns

### Integration Patterns
- Clean separation between Harmony Link communication and VNGE execution
- Modular design allows independent testing and enhancement
- Event-based architecture supports future feature expansion
- Cognitive stubs provide migration path to full AI system integration
- Synchronization patterns ensure reliable operation under stress

## Current Challenges

### Technical Challenges
1. **Animation Duration Detection:** Critical for accurate timing and user experience
2. **Complex Animation Mapping:** Hundreds of animations require intelligent selection logic
3. **Multi-Character Coordination:** Interaction animations need synchronized execution
4. **Performance at Scale:** Multiple simultaneous characters and complex sequences

### Integration Challenges
1. **Cognitive System Integration:** Prepare for individual AI entity decision-making
2. **Facial Expression Coordination:** Integrate with Countenance module for emotional expressions
3. **Object Interaction System:** Handle item pickup, placement, and exchange
4. **Scene State Management:** Coordinate with broader scene state and entity relationships

### Future Readiness
1. **AI Entity Independence:** Support autonomous AI character decision-making
2. **Social Interaction Complexity:** Handle complex multi-character social scenarios
3. **Emotional Expression Integration:** Coordinate movement with facial expressions and emotion
4. **Platform Expansion:** Potential Unity/Unreal engine support requires architecture flexibility
5. **Scalability:** Maintain synchronization performance with multiple concurrent entities
