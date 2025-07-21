# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains an individual implementation of Movement handling based on Harmony Link ActionGraph Events.
#
# This module receives ActionGraphs from Harmony Link and executes them as animations and actions in the game.

# Import Backend base Module
from harmony_modules.common import *

# VNGE
from Studio import Info
from vngameengine import vnge_game as game
from vnlibfaceexpressions import conf_neo_male, conf_neo_female
from vnactor import char_act_funcs

from threading import Thread
import time
import json

from movement_definitions import registered_actions

# Cognitive Integration Stub for future AI system integration
class CognitiveIntegrationStub:
    def __init__(self, movement_handler):
        self.movement_handler = movement_handler
        
    def handle_decision_request(self, decision_request):
        """Future integration point for entity cognitive system"""
        if not decision_request:
            return {"selected_option": "accept", "reasoning": "default"}
            
        decision_type = decision_request.get("decision_type", "")
        context = decision_request.get("context", {})
        
        print("Cognitive Decision Request: {0} for entity {1}".format(
            decision_type, decision_request.get("entity_id", "unknown")))
        
        if decision_type == "interaction_consent":
            return self._simple_consent_decision(decision_request)
        
        return {"selected_option": "accept", "reasoning": "default decision"}
    
    def _simple_consent_decision(self, request):
        """Simple stub for consent decisions - future cognitive system hook"""
        context = request.get("context", {})
        actor = context.get("actor", "")
        action = context.get("action", "")
        action_intimacy = context.get("action_intimacy", 0.5)
        
        print("Processing consent for action '{0}' from '{1}' (intimacy: {2:.2f})".format(
            action, actor, action_intimacy))
        
        # Simple decision logic based on action intimacy
        if action_intimacy > 0.8:
            return {
                "selected_option": "negotiate",
                "reasoning": "High intimacy action requires discussion",
                "emotional_state": "cautious"
            }
        elif action_intimacy > 0.6:
            return {
                "selected_option": "negotiate", 
                "reasoning": "Moderate intimacy action - need to discuss",
                "emotional_state": "hesitant"
            }
        else:
            return {
                "selected_option": "accept",
                "reasoning": "Low intimacy action accepted",
                "emotional_state": "neutral"
            }
    
    def process_relationship_context(self, relationship_context):
        """Process relationship context for decision making"""
        if not relationship_context:
            return
            
        relationship_score = relationship_context.get("relationship_score", 0.5)
        trust_level = relationship_context.get("trust_level", 0.4)
        interaction_count = relationship_context.get("interaction_count", 0)
        
        print("Relationship Context: score={0:.2f}, trust={1:.2f}, interactions={2}".format(
            relationship_score, trust_level, interaction_count))
    
    def process_subjective_context(self, subjective_context):
        """Process subjective context for decision making"""
        if not subjective_context:
            return
            
        mood = subjective_context.get("entity_mood", "neutral")
        energy = subjective_context.get("energy_level", 0.8)
        stress = subjective_context.get("stress", 0.2)
        goals = subjective_context.get("current_goals", [])
        
        print("Subjective Context: mood={0}, energy={1:.2f}, stress={2:.2f}, goals={3}".format(
            mood, energy, stress, goals))

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

# AnimationMapper - maps action names to game animation parameters
class AnimationMapper:
    def __init__(self):
        self.animation_mappings = self._load_animation_mappings()
    
    def _load_animation_mappings(self):
        """Load animation mappings - starting with hardcoded values"""
        # TODO: Later load from animation_list.json analysis
        return {
            # Basic movement actions
            "move": {"group": 0, "category": 0, "no": 0, "duration": 3.0, "speed": 0.3},
            "walk": {"group": 0, "category": 0, "no": 1, "duration": 2.5, "speed": 0.5}, 
            "run": {"group": 0, "category": 0, "no": 2, "duration": 2.0, "speed": 1.0},
            
            # Posture actions
            "sit_down": {"group": 1, "category": 0, "no": 0, "duration": 2.0, "speed": 0.5},
            "stand_up": {"group": 1, "category": 0, "no": 1, "duration": 1.5, "speed": 0.5},
            "lay_down": {"group": 1, "category": 1, "no": 0, "duration": 2.5, "speed": 0.4},
            
            # Placeholder for other actions - will be expanded
            "jump_fixed": {"group": 2, "category": 0, "no": 0, "duration": 1.0, "speed": 0.8},
        }
    
    def get_animation_mapping(self, action_name):
        """Get animation mapping for a specific action"""
        return self.animation_mappings.get(action_name)
    
    def has_mapping(self, action_name):
        """Check if action has animation mapping"""
        return action_name in self.animation_mappings

# ActionExecutor - executes individual actions in the game
class ActionExecutor:
    def __init__(self, movement_handler):
        self.movement_handler = movement_handler
        self.entity_controller = movement_handler.entity_controller
        self.chara = None  # Will be set when character is available
        
    def update_chara(self, chara):
        """Update character reference"""
        self.chara = chara
    
    def execute_action(self, action_instance):
        """Main action execution dispatcher"""
        if not self.chara:
            print("Warning: No character available for action execution")
            self.movement_handler._on_action_completed(action_instance, False)
            return
            
        action_name = action_instance.name
        print("Executing action: {0}".format(action_name))
        
        # Get animation mapping for this action
        animation_mapping = self.movement_handler.animation_mapper.get_animation_mapping(action_name)
        
        if not animation_mapping:
            print("No animation mapping found for action: {0}".format(action_name))
            self.movement_handler._on_action_completed(action_instance, False)
            return
        
        # Start execution timing
        expected_duration = animation_mapping.get("duration", 2.0)
        action_instance.start_execution(expected_duration)
        
        # Set up timeout monitoring
        self._setup_timeout_monitoring(action_instance)
        
        # Execute the action based on type
        if action_name in ["move", "walk", "run"]:
            self._execute_movement_action(action_instance, animation_mapping)
        elif action_name in ["sit_down", "lay_down", "stand_up"]:
            self._execute_posture_action(action_instance, animation_mapping)
        elif action_name in ["jump_fixed"]:
            self._execute_simple_action(action_instance, animation_mapping)
        else:
            print("Action type not yet implemented: {0}".format(action_name))
            # For now, just execute as simple action
            self._execute_simple_action(action_instance, animation_mapping)
    
    def _setup_timeout_monitoring(self, action_instance):
        """Set up timeout monitoring for the action"""
        def check_timeout():
            if action_instance.is_timeout():
                print("Action '{0}' timed out after {1:.2f}s".format(
                    action_instance.name, action_instance.get_execution_time()))
                action_instance.state = ActionState.TIMEOUT
                self.movement_handler._on_action_completed(action_instance, False)
        
        # Schedule timeout check
        game.set_timer(action_instance.max_execution_time, lambda g: check_timeout())
    
    def _execute_movement_action(self, action, mapping):
        """Handle movement actions (walk, run, etc.)"""
        try:
            # Apply animation using VNGE character animation system
            self.chara.actor.animate2(
                mapping["group"],
                mapping["category"], 
                mapping["no"],
                mapping["speed"]
            )
            
            # Handle targets (look at target if specified)
            self._handle_targets(action.targets)
            
            # Set timer for action completion
            duration = mapping.get("duration", 3.0)
            game.set_timer(duration, lambda g: self.movement_handler._on_action_completed(action, True))
            
        except Exception as e:
            print("Error executing movement action {0}: {1}".format(action.name, e))
            self.movement_handler._on_action_completed(action, False)
    
    def _execute_posture_action(self, action, mapping):
        """Handle posture changes (sit, stand, lay down)"""
        try:
            self.chara.actor.animate2(
                mapping["group"],
                mapping["category"],
                mapping["no"],
                mapping["speed"]
            )
            
            self._handle_targets(action.targets)
            
            duration = mapping.get("duration", 2.0)
            game.set_timer(duration, lambda g: self.movement_handler._on_action_completed(action, True))
            
        except Exception as e:
            print("Error executing posture action {0}: {1}".format(action.name, e))
            self.movement_handler._on_action_completed(action, False)
    
    def _execute_simple_action(self, action, mapping):
        """Handle simple animations (jumps, gestures, etc.)"""
        try:
            self.chara.actor.animate2(
                mapping["group"],
                mapping["category"],
                mapping["no"],
                mapping["speed"]
            )
            
            self._handle_targets(action.targets)
            
            duration = mapping.get("duration", 1.5)
            game.set_timer(duration, lambda g: self.movement_handler._on_action_completed(action, True))
            
        except Exception as e:
            print("Error executing simple action {0}: {1}".format(action.name, e))
            self.movement_handler._on_action_completed(action, False)
    
    def _handle_targets(self, targets):
        """Handle action targets (look_at_target, etc.)"""
        for target in targets:
            target_name = target.get("name")
            look_at_target = target.get("look_at_target", False)
            requires_consent = target.get("requires_consent", False)
            
            if look_at_target and target_name:
                # TODO: Implement look-at functionality
                print("Should look at target: {0}".format(target_name))
            
            if requires_consent:
                # TODO: Implement consent checking
                print("Action requires consent from: {0}".format(target_name))

# MovementHandler - module main class
class MovementHandler(HarmonyClientModuleBase):
    global registered_actions

    def __init__(self, entity_controller, movement_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = movement_config
        
        # Movement execution components
        self.animation_mapper = AnimationMapper()
        self.action_executor = ActionExecutor(self)
        
        # Cognitive Integration - Future AI system integration stub
        self.cognitive_stub = CognitiveIntegrationStub(self)
        
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
                print("ActionGraph actor mismatch: {0} != {1}".format(graph_actor, self.entity_controller.entity_id))
                return
            
            print("Executing ActionGraph {0} with {1} action vectors".format(graph_id, len(graph_vectors)))
            
            # Queue all ActionVectors for execution
            for action_vector in graph_vectors:
                action_instance = ActionInstance(
                    name=action_vector["action"],
                    targets=action_vector.get("targets", []),
                    transition_mode=action_vector.get("transition_mode", "linear"),
                    graph_id=graph_id
                )
                
                # Process cognitive integration for each target
                self._process_cognitive_context(action_instance)
                
                self.action_queue.append(action_instance)
                print("Queued action: {0} with {1} targets (state: {2})".format(
                    action_instance.name, len(action_instance.targets), action_instance.state))
            
            # Start execution if not already running
            if not self.current_action and self.action_queue:
                self._execute_next_action()
                
        except Exception as e:
            print("Error executing ActionGraph: {0}".format(e))
            import traceback
            traceback.print_exc()
    
    def _execute_next_action(self):
        """Execute the next action in the queue"""
        if not self.action_queue:
            print("Action queue empty, execution complete")
            self._print_execution_summary()
            return
            
        self.current_action = self.action_queue.pop(0)
        print("Starting execution of action: {0} (queue remaining: {1})".format(
            self.current_action.name, len(self.action_queue)))
        
        # Check if we have animation mapping for this action
        if not self.animation_mapper.has_mapping(self.current_action.name):
            print("Warning: No animation mapping for action '{0}', skipping".format(self.current_action.name))
            self._on_action_completed(self.current_action, False)
            return
        
        # Delegate to ActionExecutor
        self.action_executor.execute_action(self.current_action)
    
    def _on_action_completed(self, action_instance, success=True):
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
            
            print("Action '{0}' {1}{2}".format(action_instance.name, status, timing_info))
            
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
            game.set_timer(0.5, lambda g: self._execute_next_action())
        else:
            print("All actions in ActionGraph completed")
    
    def _print_execution_summary(self):
        """Print execution summary for debugging"""
        if self.total_actions_executed > 0:
            success_rate = ((self.total_actions_executed - self.total_actions_failed) / 
                          float(self.total_actions_executed)) * 100.0
            print("Action execution summary: {0} total, {1} failed, {2:.1f}% success rate, avg time: {3:.2f}s".format(
                self.total_actions_executed, self.total_actions_failed, success_rate, self.average_execution_time))
    
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
    
    def _process_cognitive_context(self, action_instance):
        """Process cognitive integration context for action targets - Future AI system hook"""
        for target in action_instance.targets:
            # Process relationship context if present
            relationship_context = target.get("relationship_context")
            if relationship_context:
                self.cognitive_stub.process_relationship_context(relationship_context)
            
            # Process subjective context if present  
            subjective_context = target.get("subjective_context")
            if subjective_context:
                self.cognitive_stub.process_subjective_context(subjective_context)
            
            # Process decision requests if present
            decision_request = target.get("decision_request")
            if decision_request:
                decision_response = self.cognitive_stub.handle_decision_request(decision_request)
                print("Cognitive Decision Response: {0} -> {1} ({2})".format(
                    decision_request.get("decision_id", "unknown"),
                    decision_response.get("selected_option", "unknown"),
                    decision_response.get("reasoning", "no reason provided")
                ))
                
                # Store decision response in target for future reference
                target["decision_response"] = decision_response
    
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
        # print(json.dumps(dir(info))) -> dir() is helpful to get an idea of what the structure of an object even is

        animations = {}
        animation_groups = dict(info.dicAGroupCategory)
        for group_id, group_info in animation_groups.items():
            animations[group_id] = {
                "name": group_info.name,
                "categories": {}
            }
            categories = dict(animation_groups[group_id].dicCategory)
            # print(json.dumps(categories))
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
                            "animation_items": [],
                            "animation_item_details": {}
                        }
                        for item_info in animation_items.values():
                            animations[group_id]["categories"][category_id]["animation_items"].append(item_info.name)
                            # animations[group_id]["categories"][category_id]["animation_items"][item_info.name] = dir(item_info)
                            animations[group_id]["categories"][category_id]["animation_item_details"][item_info.name] = {
                                "bundlePath": item_info.bundlePath,
                                "clip": item_info.clip,
                                "fileName": item_info.fileName,
                                "manifest": item_info.manifest,
                                "name": item_info.name,
                                # "option": item_info.option, -> Not serializable
                            }

        # Print list to console
        # print(json.dumps(animations))

        # Write to output file in chara dir
        animation_data = json.dumps(animations)
        file_handle = open('animation_list.json', 'w')
        file_handle.write(animation_data)
        file_handle.close()

        # raise RuntimeError("Dont want to start if debug")

    def init_animations_map(self):
        # Legacy method - keeping for compatibility
        self.animations_map = {}

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
                print('Harmony Link: Scene Data provided for entity "{0}"'.format(self.entity_controller.entity_id))
            else:
                print('Harmony Link: Failed to transmit scene data for entity "{0}"'.format(self.entity_controller.entity_id))

        # Requested availiable Actions and embedding examples
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
                print('Harmony Link: Available actions provided for entity "{0}"'.format(self.entity_controller.entity_id))
            else:
                print('Harmony Link: Failed to transmit available actions for entity "{0}"'.format(
                    self.entity_controller.entity_id))

        # Action Graph received from Harmony Link
        if event.event_type == EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS and event.status == EVENT_STATE_DONE:
            # Action graph received from Harmony Link
            action_graph = event.payload
            if int(self.config["debug_mode"]) == 1:
                print('[DEBUG][entity-{0}]: ActionGraphV1 received: {1}'.format(self.entity_controller.entity_id, json.dumps(action_graph)))
            
            # Parse and execute ActionGraphV1
            self._execute_action_graph(action_graph)
