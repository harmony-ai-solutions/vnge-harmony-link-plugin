# Harmony Link Plugin for VNGE - Animation Duration Detection
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module provides dynamic animation duration detection using Unity's RuntimeAnimatorController
# to get actual animation clip lengths instead of hardcoded durations.
import json
import os
import random

from harmony_modules.logging import get_logger
from movement_actions import get_actions_dict, CompletionTypes, ActionCategories

# Initialize logger for this module
logger = get_logger(__name__)


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


# AnimationDatabase - loads and provides access to animation definitions
class AnimationDatabase:
    def __init__(self, game_type='kks'):
        self.game_type = game_type
        self.animation_database = self._load_animation_database()
        self.animations_by_name = {}  # name -> definition mapping
        self._build_animation_definitions()

    def _load_animation_database(self):
        """Load animation database from animation_list_short.json"""
        animation_db_path = os.path.join(os.path.dirname(__file__), '../harmony_data', 'animation_list_wip.json')

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

    def _build_animation_definitions(self):
        """Build animation definitions with descriptions from the database"""
        if not self.animation_database:
            logger.warning("Animation database not loaded, cannot build definitions")
            return
        
        for group_id, group_data in self.animation_database.items():
            if not isinstance(group_data, dict):
                continue
            
            group_name = group_data.get("name", "Unknown")
            categories = group_data.get("categories", {})
            
            for category_id, category_data in categories.items():
                if not isinstance(category_data, dict):
                    continue
                
                category_name = category_data.get("name", "Unknown")
                animation_items = category_data.get("animation_items", [])
                
                for animation_no, animation_name in enumerate(animation_items):
                    if not animation_name:
                        continue
                    
                    # Create unique animation identifier
                    anim_key = "{0}_{1}_{2}".format(group_name.lower().replace(" ", "_"),
                                                     category_name.lower().replace(" & ", "_").replace(" ", "_"),
                                                     animation_name.lower().replace(" ", "_"))
                    
                    # Create animation definition
                    anim_def = {
                        "name": anim_key,
                        "description": "{0} - {1}: {2}".format(group_name, category_name, animation_name),
                        "group_id": int(group_id),
                        "group": group_name,
                        "category_id": int(category_id),
                        "category": category_name,
                        "animation_no": animation_no,
                        "duration": 2.0  # Default duration
                    }
                    
                    self.animations_by_name[anim_key] = anim_def
        
        logger.info("Built %d animation definitions from database", len(self.animations_by_name))
    
    def get_animation_by_name(self, name):
        """Get animation definition by name"""
        return self.animations_by_name.get(name)
    
    def resolve_animation(self, name):
        """
        Resolve animation name to (group_id, category_id, animation_no) tuple
        
        Returns:
            tuple: (group_id, category_id, animation_no) or None if not found
        """
        anim_def = self.get_animation_by_name(name)
        if anim_def:
            return (anim_def["group_id"], anim_def["category_id"], anim_def["animation_no"])
        return None
    
    def get_all_animations(self):
        """
        Get all animations as a list compatible with AnimationDefinitionV1
        
        Returns:
            list: List of animation definitions or empty list if no animations loaded
        """
        return list(self.animations_by_name.values()) if self.animations_by_name else []
