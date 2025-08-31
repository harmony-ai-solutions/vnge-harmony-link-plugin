# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains an individual implementation of Movement handling based on Harmony Link ActionGraph Events.
#
# This module receives ActionGraphs from Harmony Link and executes them as animations and actions in the game.

# Import Backend base Module
from harmony_modules.common import *
from harmony_modules.logging import get_logger

# VNGE
from Studio import Info

import time
import json

from movement_definitions import registered_actions, CompletionTypes, ActionCategories
from movement_animations import AnimationDurationDetector, AnimationMapper

# Initialize logger for this module
logger = get_logger(__name__)


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
        # Detect dynamic animation duration if possible
        expected_duration = self._get_animation_duration(action_name, animation_mapping)
        # Update the mapping with detected duration for future reference - TODO: Check if needed
        animation_mapping = animation_mapping.copy()  # Don't modify the original
        animation_mapping["duration"] = expected_duration

        # Begin Execution
        action_instance.start_execution(action_name, expected_duration)
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
        self.entity_controller.gameset_timer(action_instance.max_execution_time, lambda g: check_timeout())
    
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
        if not self.chara or not hasattr(self.chara, 'actor') or not self.chara.actor:
            logger.warning("Cannot setup distance-based completion: character/actor not available")
            # Fallback to duration-based completion
            self.entity_controller.game.set_timer(max_duration, lambda g: self.movement_handler.on_action_completed(action, True))
            return
        
        # Get starting position
        start_pos = self.chara.actor.pos
        start_position = [float(start_pos.x), float(start_pos.y), float(start_pos.z)]
        
        # Determine target position from action targets
        target_position = self._get_target_position(action.targets)
        if not target_position:
            logger.debug("No target position found for movement action '%s', using duration-based completion", action.name)
            self.entity_controller.game.set_timer(max_duration, lambda g: self.movement_handler.on_action_completed(action, True))
            return
        
        # Calculate target distance
        target_distance = self._calculate_distance(start_position, target_position)
        completion_threshold = 1.0  # 1.0 unit roughly equals 1 meter in game metric system
        
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
                # Get current position
                current_pos = self.chara.actor.pos
                current_position = [float(current_pos.x), float(current_pos.y), float(current_pos.z)]
                
                # Calculate distance to target
                current_distance = self._calculate_distance(current_position, target_position)
                
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
    
    def _get_target_position(self, targets):
        """Extract target position from action targets"""
        for target in targets:
            # Check for explicit position coordinates
            if "position" in target:
                position = target["position"]
                if isinstance(position, list) and len(position) >= 3:
                    return [float(position[0]), float(position[1]), float(position[2])]
            
            # Check for named target (character or object)
            target_name = target.get("name")
            if target_name:
                # Try to find target entity position
                target_position = self._get_entity_position(target_name)
                if target_position:
                    return target_position
                
                # Try to find target object position
                target_position = self._get_object_position(target_name)
                if target_position:
                    return target_position
        
        return None
    
    def _get_entity_position(self, entity_name):
        """Get position of a named entity"""
        try:
            for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                if (entity_id == entity_name and 
                    controller.chara and 
                    hasattr(controller.chara, 'actor') and 
                    controller.chara.actor):
                    pos = controller.chara.actor.pos
                    return [float(pos.x), float(pos.y), float(pos.z)]
        except Exception as e:
            logger.debug("Error getting entity position for '%s': %s", entity_name, e)
        return None
    
    def _get_object_position(self, object_name):
        """Get position of a named object/prop"""
        try:
            for prop_id, prop_object in self.entity_controller.game.scenedata.registered_props.items():
                if prop_id == object_name and prop_object and hasattr(prop_object, 'pos'):
                    pos = prop_object.pos
                    return [float(pos.x), float(pos.y), float(pos.z)]
        except Exception as e:
            logger.debug("Error getting object position for '%s': %s", object_name, e)
        return None
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate 3D distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return (dx*dx + dy*dy + dz*dz) ** 0.5
    
    def _adjust_for_targets(self, targets):
        """Adjust for targets (look_at_target, etc.)"""
        for target in targets:
            target_name = target.get("name")
            look_at_target = target.get("look_at_target", False)
            
            if look_at_target and target_name:
                # TODO: Implement look-at functionality
                logger.debug("Should look at target: %s", target_name)


# MovementHandler - module main class
class MovementHandler(HarmonyClientModuleBase):

    def __init__(self, entity_controller, movement_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = movement_config
        
        # Movement execution components
        self.action_executor = ActionExecutor(self)
        
        # Action execution state
        self.action_queue = []  # Queue of ActionInstance objects to execute
        self.current_action = None  # Currently executing ActionInstance
        self.action_history = []  # Recently completed actions for debugging
        self.max_history_size = 10
        
        # Performance monitoring
        self.total_actions_executed = 0
        self.total_actions_failed = 0
        self.average_execution_time = 0.0
        
        # Legacy - keeping for compatibility
        self.animations_map = {}

        # Debug trigger for building animation list
        if int(self.config["debug_mode"]) == 2:
            self._debug_print_animation_list()

    def _execute_action_graph(self, action_graph):
        """Execute ActionGraphV1 received from Harmony Link"""
        try:
            # Parse ActionGraphV1 structure according to Go base.go
            graph_id = action_graph.get("graph_id")
            graph_vectors = action_graph.get("graph_vector", [])
            graph_actor = action_graph.get("graph_actor")
            
            # Verify this action graph is for our entity
            if graph_actor != self.entity_controller.entity_id:
                logger.warning("ActionGraph actor mismatch: %s != %s", graph_actor, self.entity_controller.entity_id)
                return

            if len(graph_vectors) == 0:
                logger.warning("ActionGraph %s has no vectors, ignoring...", graph_id)
                return
            
            # Queue all ActionVectors for execution
            logger.info("Executing ActionGraph %s with %s action vectors", graph_id, len(graph_vectors))
            for action_vector in graph_vectors:
                action_instance = ActionInstance(
                    name=action_vector["action"],
                    targets=action_vector.get("targets", []),
                    transition_mode=action_vector.get("transition_mode", "linear"),
                    graph_id=graph_id
                )
                
                self.action_queue.append(action_instance)
                logger.debug("Queued action: %s with %s targets (state: %s)", 
                    action_instance.name, len(action_instance.targets), action_instance.state)
            
            # Start execution if not already running
            if not self.current_action and self.action_queue:
                self._execute_next_action()
                
        except Exception as e:
            logger.error("Error executing ActionGraph: %s", e)
            import traceback
            traceback.print_exc()
    
    def _execute_next_action(self):
        """Execute the next action in the queue"""
        if not self.action_queue:
            logger.info("Action queue empty, execution complete")
            self._print_execution_summary()
            return
            
        self.current_action = self.action_queue.pop(0)
        logger.info("Starting execution of action: %s (queue remaining: %s)", 
            self.current_action.name, len(self.action_queue))

        # Delegate to ActionExecutor
        self.action_executor.execute_action(self.current_action)
    
    def on_action_completed(self, action_instance, success=True):
        """Called when current action completes"""
        if action_instance:
            # Complete the action timing
            actual_duration = action_instance.complete_execution(success)
            
            # Update performance metrics
            self.total_actions_executed += 1
            if not success:
                self.total_actions_failed += 1
            
            if actual_duration:
                # Update average execution time
                if self.average_execution_time == 0.0:
                    self.average_execution_time = actual_duration
                else:
                    self.average_execution_time = (self.average_execution_time + actual_duration) / 2.0
            
            # Log completion
            status = "completed" if success else "failed"
            timing_info = ""
            if actual_duration:
                timing_info = " (took {0:.2f}s, expected {1:.2f}s)".format(
                    actual_duration, action_instance.expected_duration or 0.0)
            
            logger.info("Action '%s' %s%s", action_instance.name, status, timing_info)
            
            # Add to history
            self.action_history.append({
                'name': action_instance.name,
                'state': action_instance.state,
                'duration': actual_duration,
                'expected_duration': action_instance.expected_duration,
                'timestamp': time.time()
            })
            
            # Limit history size
            if len(self.action_history) > self.max_history_size:
                self.action_history.pop(0)
        
        # Clear current action
        if self.current_action == action_instance:
            self.current_action = None
        
        # Execute next action if any
        if self.action_queue:
            # Add small delay for natural flow between actions
            self.entity_controller.game.set_timer(0.5, lambda g: self._execute_next_action())
        else:
            logger.info("All actions in ActionGraph completed")
    
    def _print_execution_summary(self):
        """Print execution summary for debugging"""
        if self.total_actions_executed > 0:
            success_rate = ((self.total_actions_executed - self.total_actions_failed) / 
                          float(self.total_actions_executed)) * 100.0
            logger.info("Action execution summary: %s total, %s failed, %.1f%% success rate, avg time: %.2fs",
                self.total_actions_executed, self.total_actions_failed, success_rate, self.average_execution_time)
    
    def get_action_status(self):
        """Get current action execution status for monitoring"""
        return {
            'current_action': self.current_action.name if self.current_action else None,
            'current_state': self.current_action.state if self.current_action else None,
            'queue_length': len(self.action_queue),
            'total_executed': self.total_actions_executed,
            'total_failed': self.total_actions_failed,
            'average_duration': self.average_execution_time,
            'recent_history': self.action_history[-3:] if len(self.action_history) > 3 else self.action_history
        }
    
    def trigger_target_perception_check(self, action_instance):
        """routes action events to target entities' perception handlers, so they may react to them"""

        for target in action_instance.targets:
            target_name = target.get("name")
            
            # Skip if no target name specified
            if not target_name:
                continue
                
            # Check if target is another entity (not an object)
            target_entity_controller = None
            for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                if entity_id == target_name:
                    target_entity_controller = controller
                    break

            # Evaluate Target
            if target_entity_controller is None:
                logger.warning("Target '%s' is not a harmony link entity - skipping processing", target_name)
                continue
            if target_entity_controller.perceptionModule is None or not target_entity_controller.perceptionModule.is_active():
                # Target entity has no active perception module
                logger.warning("Target '%s' is not a harmony link entity - skipping processing", target_name)
                continue

            logger.info("Routing action '%s' from entity '%s' to perception handler of target entity '%s'",
                        action_instance.name, self.entity_controller.entity_id, target_name)

            # Create action event payload with comprehensive context
            action_payload = {
                "actor_entity_id": self.entity_controller.entity_id,
                "target_entity_id": target_name,
                "action_name": action_instance.name,
                "action_graph_id": action_instance.graph_id,
                "transition_mode": action_instance.transition_mode,
            }

            # Create and send action event to target entity's perception handler
            action_event = HarmonyLinkEvent(
                event_id='actor_{0}_action_{1}_forward_to_{2}'.format(self.entity_controller.entity_id, action_instance.name, target_name),
                event_type=EVENT_TYPE_PERCEPTION_ACTOR_ACTION,
                status=EVENT_STATE_DONE,
                payload=action_payload
            )

            # Route to target entity's perception handler
            target_entity_controller.perceptionModule.handle_event(action_event)
            logger.info("Action event routed successfully to perception handler of entity '%s'", target_name)

    def update_chara(self, chara):
        """Update character reference for action execution"""
        self.chara = chara
        self.action_executor.update_chara(chara)

    def _debug_print_animation_list(self):
        # Debug: List all Animations existing in the game
        #
        # REMARK:
        # This was the quickest hacky way to get the full animation list out of Chara Studio
        # Coding this code above to iterate through objects was way more effort than it should be.
        # But anyways, it's done now.
        # Commented out sections can be used for little more detail, but it's mostly empty in my case, so not worth it.
        #

        # Get Info Object, which holds all the data we need
        info = Info.Instance
        # logger.debug(json.dumps(dir(info))) -> dir() is helpful to get an idea of what the structure of an object even is

        animations = {}
        animation_groups = dict(info.dicAGroupCategory)
        for group_id, group_info in animation_groups.items():
            animations[group_id] = {
                "name": group_info.name,
                "categories": {}
            }
            categories = dict(animation_groups[group_id].dicCategory)
            # logger.debug(json.dumps(categories))
            for category_id, category_name in categories.items():
                # Not all groups which exist in the Group Category list exist / have animations;
                # this may cause reference errors, therefore double check here if the values exist
                if group_id in info.dicAnimeLoadInfo:
                    animation_info_group = info.dicAnimeLoadInfo[group_id]
                    if category_id in animation_info_group:
                        # Iterate over category items and add them to the animations list
                        animation_items = dict(animation_info_group[category_id])
                        animations[group_id]["categories"][category_id] = {
                            "name": category_name,
                            "animation_items": []
                        }
                        for item_info in animation_items.values():
                            # Create animation data object; can be used as animation database; but needs manual descriptions
                            animation_data = {
                                "name": item_info.name,
                                "description": "",
                            }
                            if int(self.config["debug_mode"]) == 3:
                                # Additional debug info, not useful for the most part unless we work on assets
                                animation_data["metadata"] = {
                                    "bundlePath": item_info.bundlePath,
                                    "clip": item_info.clip,
                                    "fileName": item_info.fileName,
                                    "manifest": item_info.manifest,
                                    "name": item_info.name
                                }

                            # Add to output
                            animations[group_id]["categories"][category_id]["animation_items"].append(animation_data)

        # Print list to console
        # logger.debug(json.dumps(animations))

        # Write to output file in chara dir
        animation_data = json.dumps(animations)
        file_handle = open('animation_list.json', 'w')
        file_handle.write(animation_data)
        file_handle.close()

        # raise RuntimeError("Dont want to start if debug")


    def handle_event(
        self,
        event  # HarmonyLinkEvent
    ):
        # Requested Props and active entities in the scene
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_REQUEST_SCENE_DATA and event.status == EVENT_STATE_DONE:
            # Define scene Data Object according to SceneDataV1 spec
            scene_data = {
                "characters": [],
                "objects": []
            }

            # Get all characters and convert them to match CharacterDefinitionV1 spec
            for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                if controller.chara is None:
                    # Ignore entities without representation in the scene
                    continue

                # get position & orientation
                position_vector = controller.chara.actor.pos
                orientation_vector = controller.chara.actor.rot

                character_definition_v1 = {
                    "name": entity_id,
                    "position": [float(position_vector.x), float(position_vector.y), float(position_vector.z)],
                    "orientation": [float(orientation_vector.x), float(orientation_vector.y), float(orientation_vector.z)],
                    "current_action": None
                }
                scene_data["characters"].append(character_definition_v1)

            # Get all objects and convert them to match ObjectDefinitionV1 spec
            for prop_id, prop_object in self.entity_controller.game.scenedata.registered_props.items():
                # get position & orientation
                position_vector = prop_object.pos
                orientation_vector = prop_object.rot

                # Build definition object
                object_definition_v1 = {
                    "name": prop_id,
                    "position": [float(position_vector.x), float(position_vector.y), float(position_vector.z)],
                    "orientation": [float(orientation_vector.x), float(orientation_vector.y), float(orientation_vector.z)],
                }
                scene_data["objects"].append(object_definition_v1)

            # Build response event & send it to Harmony Link
            event = HarmonyLinkEvent(
                event_id='actor_{0}_scene_data'.format(self.entity_controller.entity_id),
                event_type=EVENT_TYPE_MOVEMENT_V1_UPDATE_SCENE_DATA,
                status=EVENT_STATE_NEW,
                payload=scene_data
            )
            send_success = self.backend_connector.send_event(event)
            if send_success:
                logger.info('Scene Data provided for entity "%s"', self.entity_controller.entity_id)
            else:
                logger.error('Failed to transmit scene data for entity "%s"', self.entity_controller.entity_id)

        # Requested available Actions and embedding examples
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_REQUEST_ACTIONS and event.status == EVENT_STATE_DONE:
            # Define actions Data Object according to ActionsDataV1 spec
            actions_data = {
                "actions": registered_actions
            }

            event = HarmonyLinkEvent(
                event_id='actor_{0}_availiable_actions'.format(self.entity_controller.entity_id),
                event_type=EVENT_TYPE_MOVEMENT_V1_REGISTER_ACTIONS,
                status=EVENT_STATE_NEW,
                payload=actions_data
            )
            send_success = self.backend_connector.send_event(event)
            if send_success:
                logger.info('Available actions provided for entity "%s"', self.entity_controller.entity_id)
            else:
                logger.error('Failed to transmit available actions for entity "%s"', self.entity_controller.entity_id)

        # Action Graph received from Harmony Link
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS and event.status == EVENT_STATE_DONE:
            # Action graph received from Harmony Link
            action_graph = event.payload
            if int(self.config["debug_mode"]) == 1:
                logger.debug('[entity-%s]: ActionGraphV1 received: %s', self.entity_controller.entity_id, json.dumps(action_graph))
            
            # Parse and execute ActionGraphV1
            self._execute_action_graph(action_graph)
