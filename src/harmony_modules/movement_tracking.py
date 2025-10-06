# Harmony Link Plugin for VNGE - Movement Tracking and 3D Space Operations
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module provides 3D space operations for movement tracking including:
# - Character position and rotation tracking
# - Distance calculations
# - Target position resolution
#
# NOTE: This is a simplified prototype implementation:
# - No pathfinding/navmesh support (CharaStudio limitation)
# - No collision detection
# - Direct line movement only

from harmony_modules.logging import get_logger

logger = get_logger(__name__)


class SpaceManager:
    """Handles 3D position and rotation operations for character movement tracking"""
    
    def __init__(self):
        # Configuration
        self.position_tolerance = 1.0  # 1 unit threshold for movement completion (~1 meter - TODO: verify)
        self.rotation_tolerance = 5.0  # 5 degree threshold for rotation completion (future use)
        
    def get_character_position(self, chara):
        """
        Safely get character position with validation
        
        Args:
            chara: Character object with actor.pos attribute
            
        Returns:
            tuple: (x, y, z) position or None if unavailable
        """
        try:
            if not chara or not hasattr(chara, 'actor') or not chara.actor:
                logger.debug("Character or actor not available for position retrieval")
                return None
                
            pos = chara.actor.pos
            return (float(pos.x), float(pos.y), float(pos.z))
            
        except Exception as e:
            logger.warning("Error getting character position: %s", e)
            return None
    
    def get_character_rotation(self, chara):
        """
        Safely get character rotation with validation
        
        Args:
            chara: Character object with actor.rot attribute
            
        Returns:
            tuple: (x, y, z) rotation or None if unavailable
        """
        try:
            if not chara or not hasattr(chara, 'actor') or not chara.actor:
                logger.debug("Character or actor not available for rotation retrieval")
                return None
                
            rot = chara.actor.rot
            return (float(rot.x), float(rot.y), float(rot.z))
            
        except Exception as e:
            logger.warning("Error getting character rotation: %s", e)
            return None
    
    def calculate_distance(self, pos1, pos2):
        """
        Calculate 3D Euclidean distance between two positions
        
        Args:
            pos1: tuple (x, y, z) - First position
            pos2: tuple (x, y, z) - Second position
            
        Returns:
            float: Distance between positions, or infinity if invalid
        """
        if not pos1 or not pos2:
            return float('inf')
        
        try:
            dx = pos1[0] - pos2[0]
            dy = pos1[1] - pos2[1]
            dz = pos1[2] - pos2[2]
            return (dx*dx + dy*dy + dz*dz) ** 0.5
            
        except (IndexError, TypeError) as e:
            logger.warning("Error calculating distance: %s", e)
            return float('inf')
    
    def is_position_reached(self, current_pos, target_pos, threshold=None):
        """
        Check if character has reached target position within threshold
        
        Args:
            current_pos: tuple (x, y, z) - Current position
            target_pos: tuple (x, y, z) - Target position
            threshold: float - Distance threshold (uses default if None)
            
        Returns:
            bool: True if position reached, False otherwise
        """
        if threshold is None:
            threshold = self.position_tolerance
            
        distance = self.calculate_distance(current_pos, target_pos)
        return distance <= threshold
    
    def resolve_target_position(self, targets, entity_controller):
        """
        Resolve target position from action targets
        
        Tries multiple resolution strategies in order:
        1. Explicit position coordinates in target
        2. Named entity (character) position
        3. Named object/prop position
        
        Args:
            targets: list - List of action target dictionaries
            entity_controller: EntityController - For accessing scene data
            
        Returns:
            tuple: (x, y, z) position or None if no target found
        """
        for target in targets:
            # Strategy 1: Check for explicit position coordinates
            if "position" in target:
                position = target["position"]
                if isinstance(position, list) and len(position) >= 3:
                    try:
                        return (float(position[0]), float(position[1]), float(position[2]))
                    except (ValueError, TypeError) as e:
                        logger.warning("Invalid position coordinates in target: %s", e)
                        continue
            
            # Strategy 2 & 3: Check for named target (character or object)
            target_name = target.get("name")
            if target_name:
                # Try to find target entity position
                target_position = self._get_entity_position(target_name, entity_controller)
                if target_position:
                    logger.debug("Resolved target '%s' as entity at position %s", target_name, target_position)
                    return target_position
                
                # Try to find target object position
                target_position = self._get_object_position(target_name, entity_controller)
                if target_position:
                    logger.debug("Resolved target '%s' as object at position %s", target_name, target_position)
                    return target_position
                
                logger.debug("Target '%s' not found as entity or object", target_name)
        
        return None
    
    def _get_entity_position(self, entity_name, entity_controller):
        """
        Get position of a named entity (character)
        
        Args:
            entity_name: str - Name of the entity to find
            entity_controller: EntityController - For accessing scene data
            
        Returns:
            tuple: (x, y, z) position or None if not found
        """
        try:
            if not entity_controller or not hasattr(entity_controller, 'game'):
                return None
                
            if not hasattr(entity_controller.game, 'scenedata'):
                return None
                
            active_entities = entity_controller.game.scenedata.active_entities
            if not active_entities:
                return None
            
            for entity_id, controller in active_entities.items():
                if entity_id == entity_name:
                    if (controller.chara and 
                        hasattr(controller.chara, 'actor') and 
                        controller.chara.actor):
                        pos = controller.chara.actor.pos
                        return (float(pos.x), float(pos.y), float(pos.z))
                        
        except Exception as e:
            logger.debug("Error getting entity position for '%s': %s", entity_name, e)
            
        return None
    
    def _get_object_position(self, object_name, entity_controller):
        """
        Get position of a named object/prop
        
        Args:
            object_name: str - Name of the object to find
            entity_controller: EntityController - For accessing scene data
            
        Returns:
            tuple: (x, y, z) position or None if not found
        """
        try:
            if not entity_controller or not hasattr(entity_controller, 'game'):
                return None
                
            if not hasattr(entity_controller.game, 'scenedata'):
                return None
                
            registered_props = entity_controller.game.scenedata.registered_props
            if not registered_props:
                return None
            
            for prop_id, prop_object in registered_props.items():
                if prop_id == object_name:
                    if prop_object and hasattr(prop_object, 'pos'):
                        pos = prop_object.pos
                        return (float(pos.x), float(pos.y), float(pos.z))
                        
        except Exception as e:
            logger.debug("Error getting object position for '%s': %s", object_name, e)
            
        return None
    
    def get_distance_info(self, start_pos, target_pos):
        """
        Get comprehensive distance information between two positions
        
        Args:
            start_pos: tuple (x, y, z) - Starting position
            target_pos: tuple (x, y, z) - Target position
            
        Returns:
            dict: Distance information including total distance and component distances
        """
        if not start_pos or not target_pos:
            return None
        
        try:
            dx = target_pos[0] - start_pos[0]
            dy = target_pos[1] - start_pos[1]
            dz = target_pos[2] - start_pos[2]
            
            total_distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            horizontal_distance = (dx*dx + dz*dz) ** 0.5
            
            return {
                'total_distance': total_distance,
                'horizontal_distance': horizontal_distance,
                'vertical_distance': abs(dy),
                'dx': dx,
                'dy': dy,
                'dz': dz
            }
            
        except Exception as e:
            logger.warning("Error calculating distance info: %s", e)
            return None
