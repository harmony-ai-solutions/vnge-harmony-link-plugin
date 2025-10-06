# Harmony Link Plugin for VNGE - Action Registry and Definitions
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module provides centralized action management including:
# - Action registry loaded from actions.json
# - Action categories and completion types
# - Helper functions for action lookup

import json
import os
import time
from harmony_modules.logging import get_logger

from movement_animations import AnimationDurationDetector, AnimationMapper
from movement_tracking import SpaceManager

logger = get_logger(__name__)


# Action Categories - centralized constants for action classification
class ActionCategories:
    MOVEMENT = 'movement'
    POSTURE_SITTING = 'posture_sitting'
    POSTURE_STANDING = 'posture_standing'
    POSTURE_LAYING = 'posture_laying'
    SIMPLE_ACTION = 'simple_action'
    OBJECT_INTERACTION = 'object_interaction'
    CHARACTER_INTERACTION = 'character_interaction'


class CompletionTypes:
    DISTANCE = "distance"  # Movement actions - complete when distance threshold reached
    STATE = "state"        # Posture actions - complete when state achieved
    DURATION = "duration"  # Simple actions - complete after fixed duration


class ActionRegistry:
    """Centralized registry for action definitions loaded from actions.json"""
    
    def __init__(self):
        self.actions = {}
        self.actions_by_category = {}
        self._load_actions()
    
    def _load_actions(self):
        """Load actions from actions.json file"""
        actions_file = os.path.join(
            os.path.dirname(__file__), 
            '../harmony_data', 
            'actions.json'
        )
        
        try:
            with open(actions_file, 'r') as f:
                action_list = json.load(f)
            
            if not isinstance(action_list, list):
                raise ValueError("actions.json must contain a list of action definitions")
            
            for action in action_list:
                self._register_action(action)
                
            logger.info("Loaded %d actions from actions.json", len(self.actions))
            
        except FileNotFoundError:
            logger.error("actions.json not found at %s", actions_file)
            raise RuntimeError("Action definitions file (actions.json) not found. Cannot initialize movement system.")
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in actions.json: %s", e)
            raise RuntimeError("Invalid JSON in actions.json: {0}".format(e))
        except Exception as e:
            logger.error("Error loading actions.json: %s", e)
            raise RuntimeError("Failed to load action definitions: {0}".format(e))
    
    def _register_action(self, action_def):
        """Register a single action definition"""
        if not isinstance(action_def, dict):
            logger.warning("Invalid action definition (not a dict), skipping: %s", action_def)
            return
        
        name = action_def.get('name')
        if not name:
            logger.warning("Action definition missing 'name' field, skipping: %s", action_def)
            return
        
        category = action_def.get('category', 'unknown')
        
        # Store action by name
        self.actions[name] = action_def
        
        # Store action by category for easy lookup
        if category not in self.actions_by_category:
            self.actions_by_category[category] = []
        self.actions_by_category[category].append(name)
        
        logger.debug("Registered action: %s (category: %s)", name, category)
    
    def get_action(self, name):
        """Get action definition by name"""
        return self.actions.get(name)
    
    def get_actions_by_category(self, category):
        """Get all actions in a category"""
        action_names = self.actions_by_category.get(category, [])
        return [self.actions[name] for name in action_names]
    
    def get_all_actions(self):
        """Get all registered actions as a list"""
        return list(self.actions.values())
    
    def get_actions_dict(self):
        """Get all actions as a dictionary with action name as key"""
        return dict(self.actions)
    
    def validate_action(self, name):
        """Validate that an action is properly registered"""
        return name in self.actions
    
    def get_categories(self):
        """Get list of all action categories"""
        return list(self.actions_by_category.keys())
    
    def get_action_count(self):
        """Get total number of registered actions"""
        return len(self.actions)
    
    def get_category_count(self):
        """Get total number of action categories"""
        return len(self.actions_by_category)


# Global registry instance
_action_registry = ActionRegistry()


# Convenience functions for accessing the global registry
def get_all_actions():
    """Get all registered actions as a list"""
    return _action_registry.get_all_actions()


def get_actions_dict():
    """Get all actions as a dictionary with action name as key"""
    return _action_registry.get_actions_dict()


def get_action_by_name(action_name):
    """
    Get a specific action definition by name
    
    Args:
        action_name (str): Name of the action to retrieve
        
    Returns:
        dict: Action definition or None if not found
    """
    return _action_registry.get_action(action_name)


def get_actions_by_category(category):
    """
    Get all actions in a specific category
    
    Args:
        category (str): Category name to filter by
        
    Returns:
        list: List of action definitions in the category
    """
    return _action_registry.get_actions_by_category(category)


def validate_action(action_name):
    """
    Validate that an action is registered
    
    Args:
        action_name (str): Name of the action to validate
        
    Returns:
        bool: True if action is registered, False otherwise
    """
    return _action_registry.validate_action(action_name)


def get_action_categories():
    """Get list of all action categories"""
    return _action_registry.get_categories()


def get_action_count():
    """Get total number of registered actions"""
    return _action_registry.get_action_count()


# ============================================================================
# Action Execution Classes
# ============================================================================

# Action states for tracking execution lifecycle
class ActionState:
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


# ActionInstance - represents a single action to be executed with state and timing
class ActionInstance:
    def __init__(self, name, targets=None, transition_mode="linear", graph_id=None):
        self.name = name  # Action name (e.g., "walk", "sit_down")
        self.targets = targets or []  # List of ActionTargetV1 dicts
        self.transition_mode = transition_mode  # How to transition into this action
        self.graph_id = graph_id  # ID of the ActionGraph this belongs to
        
        # State and timing management
        self.state = ActionState.QUEUED
        self.start_time = None
        self.expected_duration = None
        self.actual_duration = None
        self.timeout_timer = None
        self.max_execution_time = 10.0  # Maximum time before action is considered stuck

    def start_execution(self, expected_duration=2.0):
        """Mark action as started and set timing"""
        self.state = ActionState.EXECUTING
        self.start_time = time.time()
        self.expected_duration = expected_duration
        
    def complete_execution(self, success=True):
        """Mark action as completed and calculate actual duration"""
        if self.start_time:
            self.actual_duration = time.time() - self.start_time
        
        if success:
            self.state = ActionState.COMPLETED
        else:
            self.state = ActionState.FAILED
            
        return self.actual_duration

    def get_execution_time(self):
        """Get current execution time if action is running"""
        if self.start_time and self.state == ActionState.EXECUTING:
            return time.time() - self.start_time
        return 0.0

    def is_timeout(self):
        """Check if action has exceeded maximum execution time"""
        if self.state == ActionState.EXECUTING and self.start_time:
            return self.get_execution_time() > self.max_execution_time
        return False


# ActionExecutor - executes individual actions in the game
class ActionExecutor:
    def __init__(self, movement_handler):
        self.movement_handler = movement_handler
        self.entity_controller = movement_handler.entity_controller
        self.chara = None  # Will be set when character is available
        self.animation_mapper = AnimationMapper()
        self.duration_detector = AnimationDurationDetector()
        self.space_manager = SpaceManager()
        
    def update_chara(self, chara):
        """Update character reference"""
        self.chara = chara
    
    def execute_action(self, action_instance):
        """Main action execution dispatcher"""
        if not self.chara:
            logger.warning("No character available for action execution")
            self.movement_handler.on_action_completed(action_instance, False)
            return
            
        action_name = action_instance.name
        logger.info("Executing action: %s", action_name)

        # Check if we have animation mapping for this action
        if not self.animation_mapper.has_mapping(action_name):
            logger.warning("No animation mapping for action '%s', skipping", action_name)
            self.movement_handler.on_action_completed(action_instance, False)
            return
        
        # Get animation mapping for this action
        animation_mapping = self.animation_mapper.get_animation_mapping(action_name)
        if not animation_mapping:
            logger.warning("No animation mapping data for action '%s', skipping", action_name)
            self.movement_handler.on_action_completed(action_instance, False)
            return
            
        # Detect dynamic animation duration if possible
        expected_duration = self._get_animation_duration(action_name, animation_mapping)
        # Update the mapping with detected duration for future reference - TODO: Check if needed
        animation_mapping = animation_mapping.copy()  # Don't modify the original
        animation_mapping["duration"] = expected_duration

        # Begin Execution
        action_instance.start_execution(expected_duration)
        # Set up timeout monitoring
        self._setup_timeout_monitoring(action_instance)

        # Process integration for targets
        self.movement_handler.trigger_target_perception_check(action_instance)
        # TODO: trigger perception for other entities who are not explicitly targeted but may perceive the action
        
        # Execute the action based on type
        action_category = self.animation_mapper.get_action_category(action_name)
        if action_category in [ActionCategories.MOVEMENT]:
            self._execute_movement_action(action_instance, animation_mapping)
        elif action_category in [ActionCategories.POSTURE_STANDING, ActionCategories.POSTURE_SITTING, ActionCategories.POSTURE_LAYING]:
            self._execute_posture_action(action_instance, animation_mapping)
        elif action_category in [ActionCategories.SIMPLE_ACTION]:
            self._execute_simple_action(action_instance, animation_mapping)
        else:
            logger.warning("Action type not yet implemented: %s", action_name)
            # For now, just execute as simple action
            self._execute_simple_action(action_instance, animation_mapping)

    def _get_animation_duration(self, action_name, animation_mapping):
        detected_duration = None
        try:
            detected_duration = self.duration_detector.get_animation_duration(
                self.chara,
                animation_mapping["group"],
                animation_mapping["category"],
                animation_mapping["no"]
            )
            if detected_duration:
                logger.debug("Detected animation duration for %s: %.2fs", action_name, detected_duration)
        except Exception as e:
            logger.warning("Failed to detect animation duration for %s: %s", action_name, e)

        # Use detected duration or fallback to mapping duration
        expected_duration = detected_duration if detected_duration else animation_mapping.get("duration", 2.0)
        return expected_duration
    
    def _setup_timeout_monitoring(self, action_instance):
        """Set up timeout monitoring for the action"""
        def check_timeout():
            if action_instance.is_timeout():
                logger.warning("Action '%s' timed out after %.2fs", action_instance.name, action_instance.get_execution_time())
                action_instance.state = ActionState.TIMEOUT
                self.movement_handler.on_action_completed(action_instance, False)
        
        # Schedule timeout check
        self.entity_controller.game.set_timer(action_instance.max_execution_time, lambda g: check_timeout())
    
    def _execute_movement_action(self, action, mapping):
        """Handle movement actions (walk, run, etc.)"""
        try:
            # Apply animation using VNGE character animation system
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(
                    mapping["group"],
                    mapping["category"], 
                    mapping["no"],
                    mapping["speed"]
                )
            else:
                logger.error("Character or actor not available for movement action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return
            
            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Set timer for action completion based on completion type
            completion_type = mapping.get("completion_type", CompletionTypes.DURATION)
            duration = mapping.get("duration", 3.0)
            # FIXME: This should not be the max duration of the animation, but travel time + threshold
            
            if completion_type == CompletionTypes.DISTANCE:
                # Implement distance-based completion for movement actions
                self._setup_distance_based_completion(action, duration)
            else:
                # Duration-based completion
                self.entity_controller.game.set_timer(duration, lambda g: self.movement_handler.on_action_completed(action, True))
            
        except Exception as e:
            logger.error("Error executing movement action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _execute_posture_action(self, action, mapping):
        """Handle posture changes (sit, stand, lay down)"""
        try:
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(
                    mapping["group"],
                    mapping["category"],
                    mapping["no"],
                    mapping["speed"]
                )
            else:
                logger.error("Character or actor not available for posture action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return

            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Set timer for action completion based on completion type
            completion_type = mapping.get("completion_type", CompletionTypes.STATE)
            duration = mapping.get("duration", 2.0)
            
            if completion_type == CompletionTypes.STATE:
                # For posture actions, we should implement state-based completion
                # For now, use duration but log that state-based completion is needed
                logger.debug("Posture action '%s' should use state-based completion (not yet implemented)", action.name)
                self.entity_controller.game.set_timer(duration, lambda g: self.movement_handler.on_action_completed(action, True))
            else:
                # Duration-based completion
                self.entity_controller.game.set_timer(duration, lambda g: self.movement_handler.on_action_completed(action, True))
            
        except Exception as e:
            logger.error("Error executing posture action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _execute_simple_action(self, action, mapping):
        """Handle simple animations (jumps, gestures, etc.)"""
        try:
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(
                    mapping["group"],
                    mapping["category"],
                    mapping["no"],
                    mapping["speed"]
                )
            else:
                logger.error("Character or actor not available for simple action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return

            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Simple actions typically use duration-based completion
            duration = mapping.get("duration", 1.5)
            self.entity_controller.game.set_timer(duration, lambda g: self.movement_handler.on_action_completed(action, True))
            
        except Exception as e:
            logger.error("Error executing simple action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _setup_distance_based_completion(self, action, max_duration):
        """Set up distance-based completion monitoring for movement actions"""
        # Get starting position using SpaceManager
        start_position = self.space_manager.get_character_position(self.chara)
        if not start_position:
            logger.warning("Cannot setup distance-based completion: character position unavailable")
            # Fallback to duration-based completion
            self.entity_controller.game.set_timer(max_duration, lambda g: self.movement_handler.on_action_completed(action, True))
            return
        
        # Determine target position from action targets using SpaceManager
        target_position = self.space_manager.resolve_target_position(action.targets, self.entity_controller)
        if not target_position:
            logger.debug("No target position found for movement action '%s', using duration-based completion", action.name)
            self.entity_controller.game.set_timer(max_duration, lambda g: self.movement_handler.on_action_completed(action, True))
            return
        
        # Calculate target distance using SpaceManager
        target_distance = self.space_manager.calculate_distance(start_position, target_position)
        completion_threshold = self.space_manager.position_tolerance
        
        logger.debug("Movement action '%s': start=%.2f,%.2f,%.2f target=%.2f,%.2f,%.2f distance=%.2f", 
                    action.name, start_position[0], start_position[1], start_position[2],
                    target_position[0], target_position[1], target_position[2], target_distance)
        
        # Set up periodic distance checking
        check_interval = 0.1  # Check every 100ms
        checks_performed = [0]  # Use a list for mutability in nested scope
        max_checks = int(max_duration / check_interval)  # Maximum checks based on max duration
        
        def check_distance():
            checks_performed[0] += 1
            
            # Check if action is still executing (might have been cancelled/timed out)
            if action.state != ActionState.EXECUTING:
                return
            
            try:
                # Get current position using SpaceManager - validates character/actor availability
                current_position = self.space_manager.get_character_position(self.chara)
                if not current_position:
                    logger.warning("Character/actor no longer available during distance check")
                    self.movement_handler.on_action_completed(action, False)
                    return
                
                # Calculate distance to target using SpaceManager
                current_distance = self.space_manager.calculate_distance(current_position, target_position)
                
                # Check if we've reached the target
                if current_distance <= completion_threshold:
                    logger.debug("Movement action '%s' completed: reached target (distance=%.2f)", action.name, current_distance)
                    self.movement_handler.on_action_completed(action, True)
                    return
                
                # Check if we've exceeded maximum duration
                if checks_performed[0] >= max_checks:
                    logger.warning("Movement action '%s' timed out: max duration reached (distance=%.2f)", action.name, current_distance)
                    self.movement_handler.on_action_completed(action, False)
                    return
                
                # Schedule next check
                self.entity_controller.game.set_timer(check_interval, lambda g: check_distance())
                
            except Exception as e:
                logger.error("Error in distance-based completion check for action '%s': %s", action.name, e)
                # Fallback to completing the action
                self.movement_handler.on_action_completed(action, False)
        
        # Start the first distance check
        self.entity_controller.game.set_timer(check_interval, lambda g: check_distance())
    
    def _adjust_for_targets(self, targets):
        """Adjust for targets (look_at_target, etc.)"""
        for target in targets:
            target_name = target.get("name")
            look_at_target = target.get("look_at_target", False)
            
            if look_at_target and target_name:
                # TODO: Implement look-at functionality
                logger.debug("Should look at target: %s", target_name)
