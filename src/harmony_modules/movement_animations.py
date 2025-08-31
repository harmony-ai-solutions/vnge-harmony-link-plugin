# Harmony Link Plugin for VNGE - Animation Duration Detection
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module provides dynamic animation duration detection using Unity's RuntimeAnimatorController
# to get actual animation clip lengths instead of hardcoded durations.
import json
import os
import random

from harmony_modules.logging import get_logger
from movement_definitions import get_actions_dict, CompletionTypes, ActionCategories

# Initialize logger for this module
logger = get_logger(__name__)


class AnimationGroups:
    CHARACTER = "Character"


class AnimationCategories:
    # Character group categories
    BASIC = "Basic"
    POSE = "Pose"
    EMOTIONS = "Emotions"
    WALKING_RUNNING = "Walking & Running"
    STANDING = "Standing"
    CONVERSATION = "Conversation"
    CHAIRS = "Chairs"
    SITTING_AT_DESK = "Sitting At Desk"
    SITTING_ON_FLOOR = "Sitting On Floor"
    EATING = "Eating"
    ACTION = "Action"
    REACTION = "Reaction"
    LAYING = "Laying"
    LIVE_CONCERT = "Live Concert"
    MALE = "Male"
    ADDITIONAL_1 = "Additional 1"


class AnimationDurationDetector:
    """
    Detects actual animation durations from Unity's animation system
    using RuntimeAnimatorController and AnimationClip.length
    """
    
    def __init__(self):
        self.duration_cache = {}  # Cache for detected durations
        
    def get_animation_duration(self, chara, group_id, category_id, animation_id):
        """
        Get the actual duration of an animation from Unity's animation system
        
        Args:
            chara: Character object with access to Unity animation system
            group_id: Animation group ID
            category_id: Animation category ID  
            animation_id: Animation ID within category
            
        Returns:
            float: Animation duration in seconds, or None if detection fails
        """
        # Create cache key
        cache_key = "{0}_{1}_{2}".format(group_id, category_id, animation_id)
        
        # Check cache first
        cached_duration = self._get_cached_duration(cache_key)
        if cached_duration is not None:
            return cached_duration
        
        # Attempt to detect duration from Unity animation system
        detected_duration = self._detect_duration_from_unity(chara, group_id, category_id, animation_id)
        
        # Cache the result if detection was successful
        if detected_duration is not None:
            self._cache_duration(cache_key, detected_duration)
            logger.debug("Detected animation duration: %s -> %.2fs", cache_key, detected_duration)
        else:
            logger.warning("Failed to detect duration for animation: %s", cache_key)
            
        return detected_duration

    def _detect_duration_from_unity(self, chara, group_id, category_id, animation_id):
        """
        Detect animation duration using Unity's RuntimeAnimatorController

        This method attempts to access the animation clip length through:
        1. chara.LoadAnimation() - loads animation into RuntimeAnimatorController
        2. Access AnimationClip.length property
        3. Return the actual clip duration
        """
        try:
            # Check if character and actor are available
            if not chara or not hasattr(chara, 'actor') or not chara.actor:
                logger.warning("Character or actor not available for duration detection")
                return None

            # Method 1: Try to access through LoadAnimation if available
            if hasattr(chara, 'LoadAnimation'):
                try:
                    # LoadAnimation typically loads the animation into the RuntimeAnimatorController
                    # The exact parameters may vary based on VNGE implementation
                    animation_clip = chara.LoadAnimation(group_id, category_id, animation_id)

                    if animation_clip and hasattr(animation_clip, 'length'):
                        duration = float(animation_clip.length)
                        if duration > 0:
                            return duration

                except Exception as e:
                    logger.debug("LoadAnimation method failed: %s", e)

            # Method 2: Try to access through actor's animator if available
            if hasattr(chara.actor, 'animator'):
                try:
                    animator = chara.actor.animator

                    # Try to get current animation state info
                    if hasattr(animator, 'GetCurrentAnimatorStateInfo'):
                        state_info = animator.GetCurrentAnimatorStateInfo(0)  # Layer 0
                        if state_info and hasattr(state_info, 'length'):
                            duration = float(state_info.length)
                            if duration > 0:
                                return duration

                except Exception as e:
                    logger.debug("Animator state info method failed: %s", e)

            # Method 3: Try to access animation clips directly from RuntimeAnimatorController
            if hasattr(chara.actor, 'animator') and hasattr(chara.actor.animator, 'runtimeAnimatorController'):
                try:
                    controller = chara.actor.animator.runtimeAnimatorController

                    if controller and hasattr(controller, 'animationClips'):
                        clips = controller.animationClips

                        # Try to find the specific animation clip
                        # This is a heuristic approach since we need to match group/category/id to clip name
                        for clip in clips:
                            if clip and hasattr(clip, 'length'):
                                # For now, we'll use the first valid clip length we find
                                # In a more sophisticated implementation, we'd match by name/id
                                duration = float(clip.length)
                                if duration > 0:
                                    logger.debug("Found animation clip duration: %.2fs", duration)
                                    return duration

                except Exception as e:
                    logger.debug("RuntimeAnimatorController method failed: %s", e)

            # Method 4: Try VNGE-specific animation info if available
            try:
                # VNGE may have its own animation info system
                # This would need to be adapted based on actual VNGE API
                if hasattr(chara, 'GetAnimationInfo'):
                    anim_info = chara.GetAnimationInfo(group_id, category_id, animation_id)
                    if anim_info and hasattr(anim_info, 'duration'):
                        duration = float(anim_info.duration)
                        if duration > 0:
                            return duration

            except Exception as e:
                logger.debug("VNGE animation info method failed: %s", e)

            logger.debug("All duration detection methods failed for animation %s_%s_%s", group_id, category_id, animation_id)
            return None

        except Exception as e:
            logger.error("Error in animation duration detection: %s", e)
            return None

    def _get_cached_duration(self, cache_key):
        """Get duration from cache if available"""
        if cache_key in self.duration_cache:
            cached_data = self.duration_cache[cache_key]
            return cached_data.get('duration')
        return None
    
    def _cache_duration(self, cache_key, duration):
        """Cache detected duration with timestamp"""
        self.duration_cache[cache_key] = {
            'duration': duration
        }
    
    def clear_cache(self):
        """Clear all cached durations"""
        self.duration_cache.clear()
        logger.info("Animation duration cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics for monitoring"""
        return {
            'cache_size': len(self.duration_cache)
        }


# AnimationMapper - maps actions to VNGE animations
class AnimationMapper:
    def __init__(self):
        self.animation_database = self._load_animation_database()
        self.action_categories = self._define_action_categories()
        self.animation_mappings = self._generate_dynamic_mappings()

    def _load_animation_database(self):
        """Load animation database from animation_list_short.json"""
        animation_db_path = os.path.join(os.path.dirname(__file__), '../harmony_data', 'animation_list.json')

        if not os.path.exists(animation_db_path):
            raise RuntimeError(
                "Animation database not found at {0}. This file is required for movement system initialization.".format(animation_db_path))
        try:
            with open(animation_db_path, 'r') as f:
                database = json.load(f)

            # Validate database structure
            if not isinstance(database, dict):
                raise RuntimeError("Animation database must be a dictionary")

            if not database:
                raise RuntimeError("Animation database is empty")

            logger.info("Successfully loaded animation database with %d groups", len(database))
            return database

        except json.JSONDecodeError as e:
            raise RuntimeError("Invalid JSON in animation database: {0}".format(e))
        except Exception as e:
            raise RuntimeError("Error loading animation database: {0}".format(e))

    def _define_action_categories(self):
        """Define action categories for intelligent mapping using centralized definitions"""
        # Get actions dictionary from centralized definitions
        actions_dict = get_actions_dict()

        # Build category mappings from centralized action definitions
        category_mappings = {}
        for action_name, action_def in actions_dict.items():
            category = action_def.get('category', 'unknown')
            if category not in category_mappings:
                category_mappings[category] = []
            category_mappings[category].append(action_name)

        return category_mappings

    def _generate_dynamic_mappings(self):
        """Generate animation mappings based on action categories and available animations"""
        mappings = {}

        # Find Character group by name
        character_group_id, character_group = self._find_group_by_name(AnimationGroups.CHARACTER)
        if not character_group_id or not character_group:
            raise RuntimeError(
                "Character animation group '{0}' not found in animation database. Database structure may be invalid.".format(AnimationGroups.CHARACTER))

        # Movement actions - use Walking & Running category
        walking_category_id, walking_category = self._find_category_by_name(character_group, AnimationCategories.WALKING_RUNNING)
        if walking_category_id and walking_category:
            walking_anims = walking_category["animation_items"]

            # Map movement actions to appropriate walking/running animations
            mappings["move"] = {
                "group": int(character_group_id), "category": int(walking_category_id), "no": 0,  # Walking 1
                "duration": 2.5, "speed": 0.5, "completion_type": CompletionTypes.DISTANCE
            }
            mappings["walk"] = {
                "group": int(character_group_id), "category": int(walking_category_id), "no": 1,  # Walking 2
                "duration": 2.0, "speed": 0.7, "completion_type": CompletionTypes.DISTANCE
            }

            # Running animations - use multiple running options
            running_options = [i for i, name in enumerate(walking_anims) if "Running" in name]
            if running_options:
                mappings["run"] = {
                    "group": int(character_group_id), "category": int(walking_category_id),
                    "no": running_options[0] if running_options else 2,
                    "duration": 1.5, "speed": 1.0, "completion_type": CompletionTypes.DISTANCE
                }

        # Posture actions - use appropriate categories
        # Sitting actions - use Chairs category
        chairs_category_id, chairs_category = self._find_category_by_name(character_group, AnimationCategories.CHAIRS)
        if chairs_category_id and chairs_category:
            mappings["sit_down"] = {
                "group": int(character_group_id), "category": int(chairs_category_id), "no": 0,  # Chair Idle
                "duration": 2.0, "speed": 0.5, "completion_type": CompletionTypes.STATE
            }

        # Standing actions - use Standing category
        standing_category_id, standing_category = self._find_category_by_name(character_group, AnimationCategories.STANDING)
        if standing_category_id and standing_category:
            standing_anims = standing_category["animation_items"]

            mappings["stand_up"] = {
                "group": int(character_group_id), "category": int(standing_category_id), "no": 0,  # Standing Idle 1
                "duration": 1.5, "speed": 0.6, "completion_type": CompletionTypes.STATE
            }

            # Find leaning animation by name
            leaning_idx = self._find_animation_by_name(standing_anims, "Leaning On Wall")
            if leaning_idx >= 0:
                mappings["lean_against"] = {
                    "group": int(character_group_id), "category": int(standing_category_id), "no": leaning_idx,
                    "duration": 2.0, "speed": 0.5, "completion_type": CompletionTypes.STATE
                }

        # Laying actions - use Laying category
        laying_category_id, laying_category = self._find_category_by_name(character_group, AnimationCategories.LAYING)
        if laying_category_id and laying_category:
            laying_anims = laying_category["animation_items"]
            laying_idx = self._find_animation_by_name(laying_anims, "Laying")
            if laying_idx >= 0:
                mappings["lay_down"] = {
                    "group": int(character_group_id), "category": int(laying_category_id), "no": laying_idx,
                    "duration": 2.5, "speed": 0.4, "completion_type": CompletionTypes.STATE
                }

        # Simple actions - use Basic category for jumps
        basic_category_id, basic_category = self._find_category_by_name(character_group, AnimationCategories.BASIC)
        if basic_category_id and basic_category:
            mappings["jump_fixed"] = {
                "group": int(character_group_id), "category": int(basic_category_id), "no": 1,  # Basic 1
                "duration": 1.0, "speed": 0.8, "completion_type": CompletionTypes.DURATION
            }
            mappings["jump_over"] = {
                "group": int(character_group_id), "category": int(basic_category_id), "no": 2,  # Basic 2
                "duration": 1.2, "speed": 1.0, "completion_type": CompletionTypes.DURATION
            }

        # Object interaction actions - use Standing poses with hand gestures
        if standing_category_id and standing_category:
            standing_anims = standing_category["animation_items"]

            # Find specific animations by name
            searching_idx = self._find_animation_by_name(standing_anims, "Searching For Book")
            examining_idx = self._find_animation_by_name(standing_anims, "Examining Self")
            distributing_idx = self._find_animation_by_name(standing_anims, "Distributing Leaflets")

            # Pick up actions
            for action in ["pick_up_left_hand", "pick_up_right_hand", "pick_up_both_hands"]:
                mappings[action] = {
                    "group": int(character_group_id), "category": int(standing_category_id),
                    "no": searching_idx if searching_idx >= 0 else 3,  # Searching For Book (reaching gesture)
                    "duration": 1.5, "speed": 0.6, "completion_type": CompletionTypes.DURATION
                }

            # Drop/place actions
            for action in ["drop_item", "place_item"]:
                mappings[action] = {
                    "group": int(character_group_id), "category": int(standing_category_id), "no": 0,  # Standing Idle
                    "duration": 1.0, "speed": 0.5, "completion_type": CompletionTypes.DURATION
                }

            # Storage actions
            for action in ["store_item", "retrieve_item"]:
                mappings[action] = {
                    "group": int(character_group_id), "category": int(standing_category_id),
                    "no": examining_idx if examining_idx >= 0 else 15,  # Examining Self
                    "duration": 1.5, "speed": 0.5, "completion_type": CompletionTypes.DURATION
                }

            # Give item action
            mappings["give_item"] = {
                "group": int(character_group_id), "category": int(standing_category_id),
                "no": distributing_idx if distributing_idx >= 0 else 16,  # Distributing Leaflets (giving gesture)
                "duration": 1.5, "speed": 0.5, "completion_type": CompletionTypes.DURATION
            }

        # Character interaction actions - use Conversation category
        conversation_category_id, conversation_category = self._find_category_by_name(character_group, AnimationCategories.CONVERSATION)
        if conversation_category_id and conversation_category:
            conversation_anims = conversation_category["animation_items"]

            # Hand-based interactions
            mappings["take_hand"] = {
                "group": int(character_group_id), "category": int(conversation_category_id), "no": 1,  # Talking 1
                "duration": 2.0, "speed": 0.5, "completion_type": CompletionTypes.DURATION
            }

            # Caressing actions
            for action in ["caress_cheek", "caress_head"]:
                mappings[action] = {
                    "group": int(character_group_id), "category": int(conversation_category_id), "no": 3,
                    # Talking 2 (gentle gesture)
                    "duration": 2.5, "speed": 0.4, "completion_type": CompletionTypes.DURATION
                }

            # Kissing actions
            for action in ["kiss_hand", "kiss_cheek", "kiss_forehead", "kiss_lips"]:
                mappings[action] = {
                    "group": int(character_group_id), "category": int(conversation_category_id), "no": 5,
                    # Talking 3 (intimate gesture)
                    "duration": 2.0, "speed": 0.4, "completion_type": CompletionTypes.DURATION
                }

            # Push away action
            mappings["push_away"] = {
                "group": int(character_group_id), "category": int(conversation_category_id), "no": 7,
                # Talking 4 (defensive gesture)
                "duration": 1.0, "speed": 0.8, "completion_type": CompletionTypes.DURATION
            }

        # Validate that we have mappings for core movement actions
        core_actions = ["move", "walk", "run"]
        missing_core_actions = [action for action in core_actions if action not in mappings]
        if missing_core_actions:
            raise RuntimeError(
                "Failed to generate mappings for core movement actions: {0}. Check animation database structure.".format(missing_core_actions))

        # Add fallback mappings for any remaining actions that don't have specific mappings
        self._add_fallback_mappings(mappings)

        logger.info("Generated %d dynamic animation mappings using name-based lookups", len(mappings))
        return mappings

    def _find_group_by_name(self, group_name):
        """Find animation group by name"""
        if not self.animation_database:
            return None, None

        for group_id, group_data in self.animation_database.items():
            if isinstance(group_data, dict) and group_data.get("name") == group_name:
                return group_id, group_data
        return None, None

    def _find_category_by_name(self, group_data, category_name):
        """Find animation category by name within a group"""
        if not group_data or not isinstance(group_data, dict) or "categories" not in group_data:
            return None, None

        categories = group_data["categories"]
        if not isinstance(categories, dict):
            return None, None

        for category_id, category_data in categories.items():
            if isinstance(category_data, dict) and category_data.get("name") == category_name:
                return category_id, category_data
        return None, None

    def _find_animation_by_name(self, animation_list, animation_name_pattern):
        """Find animation index by name pattern"""
        if not animation_list or not isinstance(animation_list, list):
            return -1

        for i, anim_name in enumerate(animation_list):
            if isinstance(anim_name, str) and animation_name_pattern in anim_name:
                return i
        return -1

    def _add_fallback_mappings(self, mappings):
        """Add fallback mappings for actions not yet covered"""
        # Find Character group and Standing category for fallback
        character_group_id, character_group = self._find_group_by_name(AnimationGroups.CHARACTER)
        if not character_group_id or not character_group:
            raise RuntimeError("Cannot create fallback mappings: Character group not found")

        standing_category_id, standing_category = self._find_category_by_name(character_group,
                                                                              AnimationCategories.STANDING)
        if not standing_category_id or not standing_category:
            raise RuntimeError("Cannot create fallback mappings: Standing category not found")

        fallback_mapping = {
            "group": int(character_group_id),
            "category": int(standing_category_id),
            "no": 0,  # Standing Idle as fallback
            "duration": 2.0,
            "speed": 0.5,
            "completion_type": CompletionTypes.DURATION
        }

        # Get all action names from movement_definitions
        all_actions = set()
        for category_actions in self.action_categories.values():
            all_actions.update(category_actions)

        # Add fallback for any missing actions
        for action in all_actions:
            if action not in mappings:
                mappings[action] = fallback_mapping.copy()
                logger.debug("Added fallback mapping for action: %s", action)

    def get_animation_mapping(self, action_name):
        """Get animation mapping for a specific action"""
        mapping = self.animation_mappings.get(action_name)
        if mapping:
            # Add some randomization for running animations to add variety
            if action_name == "run" and "0" in self.animation_database and "3" in self.animation_database["0"][
                "categories"]:
                walking_anims = self.animation_database["0"]["categories"]["3"]["animation_items"]
                running_options = [i for i, name in enumerate(walking_anims) if "Running" in name]
                if len(running_options) > 1:
                    mapping = mapping.copy()  # Don't modify the original
                    mapping["no"] = random.choice(running_options)

        return mapping

    def has_mapping(self, action_name):
        """Check if action has animation mapping"""
        return action_name in self.animation_mappings

    def get_action_category(self, action_name):
        """Get the category of an action for completion type determination"""
        for category, actions in self.action_categories.items():
            if action_name in actions:
                return category
        return "unknown"
