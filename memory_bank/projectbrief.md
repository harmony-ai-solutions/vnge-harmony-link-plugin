# VNGE Harmony Link Plugin - Project Brief

## Project Overview
The VNGE Harmony Link Plugin is an IronPython plugin for VNGE (Visual Novel Game Engine) that receives ActionGraphs from Harmony Link and executes them as character animations and behaviors in the game.

## Core Purpose
- Receive ActionGraphV1 structures from Harmony Link via WebSocket events
- Execute character animations using VNGE's animation system
- Manage action queues, state tracking, and timing control
- Provide real-time character behavior execution in game environment

## High-Level Goals
1. **Seamless Integration**: Bridge between Harmony Link AI orchestration and VNGE game engine
2. **Real-Time Execution**: Execute character actions with sub-second responsiveness
3. **Robust State Management**: Track action lifecycle from queue to completion
4. **Performance Monitoring**: Provide execution statistics and debugging capabilities
5. **Extensible Animation System**: Support for expanding action repertoire

## Key Innovation
Intelligent action execution system that converts abstract ActionGraph commands into specific VNGE character animations, with state management and timing control for natural character behavior.

## Target Users
- Game developers using VNGE for character-driven experiences
- AI character developers integrating with Harmony Link
- Content creators building interactive virtual character experiences
- Researchers working with AI-driven virtual agents in game environments

## Core Requirements
- IronPython 2.7 compatibility for VNGE integration
- WebSocket communication with Harmony Link
- Real-time character animation execution
- Action state management and timeout handling
- Scene data coordination and character tracking
- Performance monitoring and debugging capabilities
