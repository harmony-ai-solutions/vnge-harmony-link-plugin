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

from movement_actions import (
    get_all_actions, 
    CompletionTypes, 
    ActionCategories,
    ActionState,
    ActionInstance,
    ActionExecutor
)
from movement_animations import AnimationDatabase

# Initialize logger for this module
logger = get_logger(__name__)



# MovementHandler - module main class
class MovementHandler(HarmonyClientModuleBase):

    def __init__(self, entity_controller, movement_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = movement_config
        
        # Initialize animation database
        self.animation_db = AnimationDatabase()
        
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
                # Extract animation data from ActionVector
                animation_data = action_vector.get("animation")
                
                action_instance = ActionInstance(
                    name=action_vector["action"],
                    targets=action_vector.get("targets", []),
                    transition_mode=action_vector.get("transition_mode", "linear"),
                    graph_id=graph_id,
                    animation_selection=animation_data  # Pass animation selection from Harmony Link
                )
                
                self.action_queue.append(action_instance)
                logger.debug("Queued action: %s with %s targets, animations: %s (state: %s)", 
                    action_instance.name, len(action_instance.targets), 
                    animation_data.get("animation") if animation_data else "none", 
                    action_instance.state)
            
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

                # Get current action - ensure it's None when not executing
                current_action = None
                if (hasattr(controller, 'movementModule') and 
                    controller.movementModule is not None and
                    hasattr(controller.movementModule, 'current_action') and
                    controller.movementModule.current_action is not None):
                    # Only include action name if it's actually executing
                    if controller.movementModule.current_action.state == ActionState.EXECUTING:
                        current_action = controller.movementModule.current_action.name

                character_definition_v1 = {
                    "name": entity_id,
                    "position": [float(position_vector.x), float(position_vector.y), float(position_vector.z)],
                    "orientation": [float(orientation_vector.x), float(orientation_vector.y), float(orientation_vector.z)],
                    "current_action": current_action
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
                "actions": get_all_actions()
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

        # Requested available Animations
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_REQUEST_ANIMATIONS and event.status == EVENT_STATE_DONE:
            # Define animations Data Object according to AnimationsDataV1 spec
            animations_data = {
                "animations": self.animation_db.get_all_animations()
            }

            event = HarmonyLinkEvent(
                event_id='actor_{0}_available_animations'.format(self.entity_controller.entity_id),
                event_type=EVENT_TYPE_MOVEMENT_V1_REGISTER_ANIMATIONS,
                status=EVENT_STATE_NEW,
                payload=animations_data
            )
            send_success = self.backend_connector.send_event(event)
            if send_success:
                logger.info('Available animations provided for entity "%s" (count: %s)', 
                    self.entity_controller.entity_id, len(animations_data["animations"]))
            else:
                logger.error('Failed to transmit available animations for entity "%s"', self.entity_controller.entity_id)

        # Action Graph received from Harmony Link
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS and event.status == EVENT_STATE_DONE:
            # Action graph received from Harmony Link
            action_graph = event.payload
            if int(self.config["debug_mode"]) == 1:
                logger.debug('[entity-%s]: ActionGraphV1 received: %s', self.entity_controller.entity_id, json.dumps(action_graph))
            
            # Parse and execute ActionGraphV1
            self._execute_action_graph(action_graph)
