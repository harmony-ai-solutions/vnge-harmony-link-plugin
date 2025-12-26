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

from harmony_modules.movement_animations import AnimationDurationDetector
from harmony_modules.movement_tracking import SpaceManager

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
        """Load actions from individual JSON files in the actions folder"""
        actions_dir = os.path.join(
            os.path.dirname(__file__),
            '../harmony_data',
            'actions'
        )

        if not os.path.exists(actions_dir):
            logger.error("Actions directory not found at %s", actions_dir)
            raise RuntimeError("Actions directory not found. Cannot initialize movement system.")

        try:
            count = 0
            for filename in os.listdir(actions_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(actions_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            action_def = json.load(f)
                        self._register_action(action_def)
                        count += 1
                    except json.JSONDecodeError as e:
                        logger.error("Invalid JSON in %s: %s", filename, e)
                    except Exception as e:
                        logger.error("Error loading %s: %s", filename, e)

            logger.info("Loaded %d actions from %s", count, actions_dir)

        except Exception as e:
            logger.error("Error scanning actions directory: %s", e)
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
    def __init__(self, name, targets=None, transition_mode="linear", graph_id=None, animation_selection=None):
        self.name = name  # Action name (e.g., "walk", "sit_down")
        self.targets = targets or []  # List of ActionTargetV1 dicts
        self.transition_mode = transition_mode  # How to transition into this action
        self.graph_id = graph_id  # ID of the ActionGraph this belongs to
        self.animation_selection = animation_selection  # AnimationSelectionV1 from Harmony Link
        
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
        self.animation_db = movement_handler.animation_db  # Reference to animation database
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

        # Check if we have animation selection from Harmony Link
        animation_selection = action_instance.animation_selection
        if not animation_selection or not animation_selection.get("animation"):
            logger.warning("No animation selected for action '%s', skipping", action_name)
            self.movement_handler.on_action_completed(action_instance, False)
            return
        
        # Resolve main animation name to group/category/no
        main_anim_name = animation_selection.get("animation")
        main_anim_ids = self.animation_db.resolve_animation(main_anim_name)
        if not main_anim_ids:
            logger.warning("Cannot resolve animation '%s' for action '%s', skipping", main_anim_name, action_name)
            self.movement_handler.on_action_completed(action_instance, False)
            return
        
        group_id, category_id, animation_no = main_anim_ids
        
        # Detect dynamic animation duration if possible
        expected_duration = None
        try:
            expected_duration = self.duration_detector.get_animation_duration(
                self.chara, group_id, category_id, animation_no
            )
            if expected_duration:
                logger.debug("Detected animation duration for %s: %.2fs", action_name, expected_duration)
        except Exception as e:
            logger.warning("Failed to detect animation duration for %s: %s", action_name, e)
        
        # Fallback to default duration if detection failed
        if not expected_duration:
            expected_duration = 2.0

        # Begin Execution
        action_instance.start_execution(expected_duration)
        # Set up timeout monitoring
        self._setup_timeout_monitoring(action_instance)

        # Process integration for targets
        self.movement_handler.trigger_target_perception_check(action_instance)
        # TODO: trigger perception for other entities who are not explicitly targeted but may perceive the action
        
        # Get action definition to determine category
        action_def = get_action_by_name(action_name)
        action_category = action_def.get('category', 'unknown') if action_def else 'unknown'
        
        # Execute based on action category
        if action_category in [ActionCategories.MOVEMENT]:
            self._execute_movement_action(action_instance, group_id, category_id, animation_no, expected_duration)
        elif action_category in [ActionCategories.POSTURE_STANDING, ActionCategories.POSTURE_SITTING, ActionCategories.POSTURE_LAYING]:
            self._execute_posture_action(action_instance, group_id, category_id, animation_no, expected_duration)
        elif action_category in [ActionCategories.SIMPLE_ACTION, ActionCategories.OBJECT_INTERACTION, ActionCategories.CHARACTER_INTERACTION]:
            self._execute_simple_action(action_instance, group_id, category_id, animation_no, expected_duration)
        else:
            logger.warning("Unknown action category: %s for action %s, executing as simple action", action_category, action_name)
            self._execute_simple_action(action_instance, group_id, category_id, animation_no, expected_duration)

    def _setup_timeout_monitoring(self, action_instance):
        """Set up timeout monitoring for the action"""
        def check_timeout():
            if action_instance.is_timeout():
                logger.warning("Action '%s' timed out after %.2fs", action_instance.name, action_instance.get_execution_time())
                action_instance.state = ActionState.TIMEOUT
                self.movement_handler.on_action_completed(action_instance, False)
        
        # Schedule timeout check
        self.entity_controller.game.set_timer(action_instance.max_execution_time, lambda g: check_timeout())
    
    def _execute_movement_action(self, action, group_id, category_id, animation_no, duration):
        """Handle movement actions (walk, run, etc.)"""
        try:
            # Check if we have a start animation
            animation_selection = action.animation_selection
            start_anim_name = animation_selection.get("animation_start") if animation_selection else None
            
            if start_anim_name:
                # Play start animation first
                start_anim_ids = self.animation_db.resolve_animation(start_anim_name)
                if start_anim_ids:
                    start_group, start_category, start_no = start_anim_ids
                    logger.debug("Playing start animation '%s' for action %s", start_anim_name, action.name)
                    if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                        self.chara.actor.animate2(start_group, start_category, start_no, 0.5)
                        # Wait for start animation to complete (TODO: detect actual duration)
                        # For now, use a small delay
                        self.entity_controller.game.set_timer(0.5, lambda g: self._start_main_animation(action, group_id, category_id, animation_no, duration))
                        return
            
            # No start animation, go directly to main animation
            self._start_main_animation(action, group_id, category_id, animation_no, duration)
            
        except Exception as e:
            logger.error("Error executing movement action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _start_main_animation(self, action, group_id, category_id, animation_no, duration):
        """Start the main animation for an action"""
        try:
            # Apply main animation
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(group_id, category_id, animation_no, 0.5)  # Default speed
            else:
                logger.error("Character or actor not available for movement action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return
            
            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Movement actions use distance-based completion
            self._setup_distance_based_completion(action, duration)
            
        except Exception as e:
            logger.error("Error starting main animation for %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _execute_posture_action(self, action, group_id, category_id, animation_no, duration):
        """Handle posture changes (sit, stand, lay down)"""
        try:
            # Check if we have a start animation
            animation_selection = action.animation_selection
            start_anim_name = animation_selection.get("animation_start") if animation_selection else None
            
            if start_anim_name:
                # Play start animation first
                start_anim_ids = self.animation_db.resolve_animation(start_anim_name)
                if start_anim_ids:
                    start_group, start_category, start_no = start_anim_ids
                    logger.debug("Playing start animation '%s' for action %s", start_anim_name, action.name)
                    if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                        self.chara.actor.animate2(start_group, start_category, start_no, 0.5)
                        # Wait for start animation, then play main
                        self.entity_controller.game.set_timer(0.5, lambda g: self._apply_main_posture_animation(action, group_id, category_id, animation_no, duration))
                        return
            
            # No start animation, apply main animation directly
            self._apply_main_posture_animation(action, group_id, category_id, animation_no, duration)
            
        except Exception as e:
            logger.error("Error executing posture action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _apply_main_posture_animation(self, action, group_id, category_id, animation_no, duration):
        """Apply main posture animation"""
        try:
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(group_id, category_id, animation_no, 0.5)
            else:
                logger.error("Character or actor not available for posture action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return

            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Posture actions use duration-based completion with optional end animation
            def on_complete():
                self._play_end_animation_if_needed(action)
            
            self.entity_controller.game.set_timer(duration, lambda g: on_complete())
            
        except Exception as e:
            logger.error("Error applying main posture animation %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _execute_simple_action(self, action, group_id, category_id, animation_no, duration):
        """Handle simple animations (jumps, gestures, etc.)"""
        try:
            # Check if we have a start animation
            animation_selection = action.animation_selection
            start_anim_name = animation_selection.get("animation_start") if animation_selection else None
            
            if start_anim_name:
                # Play start animation first
                start_anim_ids = self.animation_db.resolve_animation(start_anim_name)
                if start_anim_ids:
                    start_group, start_category, start_no = start_anim_ids
                    logger.debug("Playing start animation '%s' for action %s", start_anim_name, action.name)
                    if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                        self.chara.actor.animate2(start_group, start_category, start_no, 0.5)
                        # Wait for start animation, then play main
                        self.entity_controller.game.set_timer(0.5, lambda g: self._apply_main_simple_animation(action, group_id, category_id, animation_no, duration))
                        return
            
            # No start animation, apply main animation directly
            self._apply_main_simple_animation(action, group_id, category_id, animation_no, duration)
            
        except Exception as e:
            logger.error("Error executing simple action %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _apply_main_simple_animation(self, action, group_id, category_id, animation_no, duration):
        """Apply main simple animation"""
        try:
            if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                self.chara.actor.animate2(group_id, category_id, animation_no, 0.5)
            else:
                logger.error("Character or actor not available for simple action %s", action.name)
                self.movement_handler.on_action_completed(action, False)
                return

            # Adjust current entity based on target details
            self._adjust_for_targets(action.targets)
            
            # Simple actions use duration-based completion with optional end animation
            def on_complete():
                self._play_end_animation_if_needed(action)
            
            self.entity_controller.game.set_timer(duration, lambda g: on_complete())
            
        except Exception as e:
            logger.error("Error applying main simple animation %s: %s", action.name, e)
            self.movement_handler.on_action_completed(action, False)
    
    def _play_end_animation_if_needed(self, action):
        """Play end animation if specified, then complete action"""
        animation_selection = action.animation_selection
        end_anim_name = animation_selection.get("animation_end") if animation_selection else None
        
        if end_anim_name:
            # Play end animation
            end_anim_ids = self.animation_db.resolve_animation(end_anim_name)
            if end_anim_ids:
                end_group, end_category, end_no = end_anim_ids
                logger.debug("Playing end animation '%s' for action %s", end_anim_name, action.name)
                try:
                    if self.chara and hasattr(self.chara, 'actor') and self.chara.actor:
                        self.chara.actor.animate2(end_group, end_category, end_no, 0.5)
                        # Wait for end animation to complete
                        self.entity_controller.game.set_timer(0.5, lambda g: self.movement_handler.on_action_completed(action, True))
                        return
                except Exception as e:
                    logger.warning("Failed to play end animation for %s: %s", action.name, e)
        
        # No end animation or failed to play, complete action directly
        self.movement_handler.on_action_completed(action, True)
    
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
