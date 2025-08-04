# Harmony Link Plugin for VNGE - Entity Setup Dialog
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module provides a UI dialog for matching Harmony Link entities to scene actors

from UnityEngine import GUI, GUILayout, GUIStyle, Screen, Rect, Vector2
from vngameengine import HSNeoOCI, HSNeoOCIChar, HSNeoOCIFolder
from skin_customwindow import SkinCustomWindow
from Studio import Studio, OCIChar

class EntitySetupDialog:
    """
    Dialog window for matching Harmony Link entities to scene actors.
    Uses VNGE's window management system.
    """
    
    def __init__(self, game, entities, actors):
        """
        Initialize the entity setup dialog.
        
        Args:
            game: VNNeoController instance
            entities: List of entity dicts from Harmony Link
            actors: List of Actor objects from the scene
        """
        self.game = game
        self.entities = entities  # From Harmony Link
        self.actors = actors      # Scene actors
        self.window_id = None
        self.scroll_pos = Vector2.zero
        self.entity_mappings = {}  # entity_id -> actor
        self.current_entity_menu = None  # Currently open entity menu
        self.user_entity = None  # Selected user entity (required)
        self.current_user_menu = False  # Show user entity selection menu
        
        # First, get existing tagged actors from VNGE registry
        tagged_actors = game.scenef_get_all_actors()
        
        # Pre-populate with existing tagged actors
        for tagged_actor_id, actor in tagged_actors.items():
            # Check if this entity exists in our Harmony Link entities
            for entity in entities:
                if entity['id'] == tagged_actor_id:
                    self.entity_mappings[tagged_actor_id] = actor
                    print('Pre-populated existing mapping: {0} -> {1}'.format(tagged_actor_id, actor.text_name))
                    break
        
        # Then find exact name matches for unmapped entities
        for entity in entities:
            if entity['id'] not in self.entity_mappings:  # Only if not already mapped
                for actor in actors:
                    if entity['id'].lower() == actor.text_name.lower():
                        self.entity_mappings[entity['id']] = actor
                        print('Auto-matched by name: {0} -> {1}'.format(entity['id'], actor.text_name))
                        break
        
        # Try to auto-select user entity (look for common user entity names)
        user_keywords = ['user', 'player', 'narrator', 'me', 'self']
        for entity in entities:
            entity_lower = entity['id'].lower()
            if any(keyword in entity_lower for keyword in user_keywords):
                self.user_entity = entity['id']
                break
        
        # If no auto-selection, default to first entity
        if not self.user_entity and entities:
            self.user_entity = entities[0]['id']
    
    def show(self):
        """Show the entity setup dialog"""
        skin = SkinCustomWindow()
        skin.funcSetup = self.setup_window
        skin.funcWindowGUI = self.render_window
        self.window_id = self.game.new_extra_window_skin(skin)
        
    def setup_window(self, controller):
        """Setup window properties"""
        controller.windowName = "Entity Setup - Match Entities to Actors"
        controller.windowRect = Rect(Screen.width/2 - 400, Screen.height/2 - 300, 800, 600)
        controller.windowStyle = controller.windowStyleDefault
        
    def render_window(self, controller, windowid):
        """Render the dialog window"""
        try:
            GUILayout.BeginVertical()
            
            # Header
            GUILayout.Label("<b><size=16>Match Harmony Link Entities to Scene Actors</size></b>")
            GUILayout.Space(10)
            
            # Instructions
            GUILayout.Label("1. First, select which entity represents the USER (required for plugin operation)")
            GUILayout.Label("2. Then match entities to scene actors. Leave as (none) to skip.")
            GUILayout.Label("Dark Green = previously tagged, Blue = exact name match, Yellow = manual, Red = not mapped")
            GUILayout.Space(10)
            
            # User entity selection (always at top)
            GUILayout.BeginHorizontal()
            GUILayout.Label("<b><color=#ff6600>User Entity (Required):</color></b>", GUILayout.Width(200))
            
            user_button_text = self.user_entity if self.user_entity else "(select user entity)"
            if GUILayout.Button(user_button_text, GUILayout.Width(200)):
                self.current_user_menu = True
                self.current_entity_menu = None
            
            if self.user_entity:
                GUILayout.Label("<color=#00ff00>✓ Selected</color>", GUILayout.Width(150))
            else:
                GUILayout.Label("<color=#ff0000>⚠ Required</color>", GUILayout.Width(150))
            
            GUILayout.EndHorizontal()
            GUILayout.Space(10)
            
            # Separator
            GUILayout.Label("<b>Entity to Actor Mappings:</b>")
            GUILayout.Space(5)
            
            # Entity mapping section
            self.scroll_pos = GUILayout.BeginScrollView(self.scroll_pos, GUILayout.Height(400))
            
            # If showing user entity menu, render that
            if self.current_user_menu:
                self.render_user_entity_menu()
            # If showing entity menu, render that instead
            elif self.current_entity_menu:
                self.render_actor_menu()
            else:
                self.render_entity_list()
                
            GUILayout.EndScrollView()
            
            # Buttons
            GUILayout.Space(20)
            GUILayout.BeginHorizontal()
            
            if not self.current_entity_menu and not self.current_user_menu:
                # Check if user entity is selected before allowing continue
                if self.user_entity:
                    if GUILayout.Button("Apply and Continue", GUILayout.Height(40)):
                        self.apply_mappings()
                        self.close()
                else:
                    # Disabled button if no user entity selected
                    GUI.enabled = False
                    GUILayout.Button("Apply and Continue (Select User Entity First)", GUILayout.Height(40))
                    GUI.enabled = True
                    
                if GUILayout.Button("Skip Setup", GUILayout.Height(40)):
                    self.close()
            else:
                if GUILayout.Button("< Back to Entity List", GUILayout.Height(40)):
                    self.current_entity_menu = None
                    self.current_user_menu = False
                    
            GUILayout.EndHorizontal()
            
            GUILayout.EndVertical()
            
        except Exception as e:
            print('Entity Setup Dialog Error: {0}'.format(str(e)))
            import traceback
            traceback.print_exc()
    
    def render_entity_list(self):
        """Render the list of entities with their current mappings"""
        # Get existing tagged actors to determine mapping source
        existing_actors = self.game.scenef_get_all_actors()
        
        for entity in self.entities:
            GUILayout.BeginHorizontal()
            
            # Entity label with provider info
            entity_text = "Entity: <b>{0}</b>".format(entity['id'])
            if entity.get('configured_providers'):
                providers = entity['configured_providers']
                backend = providers.get('backend', 'none')
                entity_text += " (Backend: {0})".format(backend)
            
            # Mark user entity
            if entity['id'] == self.user_entity:
                entity_text += " <color=#ff6600>[USER]</color>"
                
            GUILayout.Label(entity_text, GUILayout.Width(350))
            
            # Current selection
            current_actor = self.entity_mappings.get(entity['id'])
            
            # Actor selection button
            button_text = "(none)" if not current_actor else current_actor.text_name
            if GUILayout.Button(button_text, GUILayout.Width(200)):
                # Show actor selection menu
                self.current_entity_menu = entity['id']
                self.current_user_menu = False
                
            # Enhanced status indicator with mapping source detection
            if current_actor:
                # Check if this was a previously tagged entity
                was_previously_tagged = entity['id'] in existing_actors
                # Check if this is an exact name match
                is_exact_match = entity['id'].lower() == current_actor.text_name.lower()
                
                if was_previously_tagged:
                    GUILayout.Label("<color=#00aa00>✓ Previously tagged</color>", GUILayout.Width(150))
                elif is_exact_match:
                    GUILayout.Label("<color=#0088ff>✓ Exact name match</color>", GUILayout.Width(150))
                else:
                    GUILayout.Label("<color=#ffff00>Manual selection</color>", GUILayout.Width(150))
            else:
                if entity['id'] == self.user_entity:
                    GUILayout.Label("<color=#ff6600>User (no actor needed)</color>", GUILayout.Width(150))
                else:
                    GUILayout.Label("<color=#ff0000>Not mapped</color>", GUILayout.Width(150))
                
            GUILayout.EndHorizontal()
            GUILayout.Space(5)
    
    def render_actor_menu(self):
        """Render the actor selection menu for current entity"""
        entity_id = self.current_entity_menu
        
        GUILayout.Label("<b>Select actor for entity: {0}</b>".format(entity_id))
        if entity_id == self.user_entity:
            GUILayout.Label("<color=#ff6600>Note: User entity can be mapped to an actor or left unmapped.</color>")
        GUILayout.Space(10)
        
        # None option
        none_text = "(none) - Skip this entity"
        if entity_id == self.user_entity:
            none_text = "(none) - User entity without scene actor"
        if GUILayout.Button(none_text, GUILayout.Height(30)):
            self.select_actor(entity_id, None)
            self.current_entity_menu = None
            
        GUILayout.Space(10)
        GUILayout.Label("Available actors:")
        
        # Actor options
        for actor in self.actors:
            button_style = GUIStyle(GUI.skin.button)
            
            # Check if this actor is already mapped to another entity
            already_mapped_to = None
            for eid, mapped_actor in self.entity_mappings.items():
                if eid != entity_id and mapped_actor == actor:
                    already_mapped_to = eid
                    break
                    
            button_text = actor.text_name
            button_enabled = True
            
            if already_mapped_to:
                button_text += " <color=#ff0000>(mapped to {0})</color>".format(already_mapped_to)
                button_enabled = False  # Disable button for already mapped actors
                
            # Disable button if actor is already mapped
            if not button_enabled:
                GUI.enabled = False
                
            if GUILayout.Button(button_text, button_style, GUILayout.Height(30)):
                if button_enabled:  # Double-check before allowing selection
                    self.select_actor(entity_id, actor)
                    self.current_entity_menu = None
                    
            # Re-enable GUI
            GUI.enabled = True
        
    def select_actor(self, entity_id, actor):
        """Set the mapping for an entity with validation"""
        if actor:
            # Check if this actor is already mapped to another entity
            for existing_entity_id, existing_actor in self.entity_mappings.items():
                if existing_entity_id != entity_id and existing_actor == actor:
                    print('Warning: Actor {0} is already mapped to entity {1}, cannot map to {2}'.format(
                        actor.text_name, existing_entity_id, entity_id))
                    return  # Prevent duplicate mapping
            
            # Set the mapping
            self.entity_mappings[entity_id] = actor
            print('Mapped entity {0} to actor {1}'.format(entity_id, actor.text_name))
        else:
            # Remove mapping
            if entity_id in self.entity_mappings:
                print('Unmapped entity {0}'.format(entity_id))
            self.entity_mappings.pop(entity_id, None)
        
    def render_user_entity_menu(self):
        """Render the user entity selection menu"""
        GUILayout.Label("<b>Select User Entity (Required):</b>")
        GUILayout.Space(10)
        GUILayout.Label("The user entity represents YOU in conversations and interactions.")
        GUILayout.Label("This entity does not need a scene actor, but must be selected.")
        GUILayout.Space(10)
        
        for entity in self.entities:
            button_style = GUIStyle(GUI.skin.button)
            
            # Highlight current selection
            if entity['id'] == self.user_entity:
                button_style.normal.textColor = GUI.skin.button.active.textColor
            
            entity_text = entity['id']
            if entity.get('configured_providers'):
                providers = entity['configured_providers']
                backend = providers.get('backend', 'none')
                entity_text += " (Backend: {0})".format(backend)
            
            if GUILayout.Button(entity_text, button_style, GUILayout.Height(30)):
                self.user_entity = entity['id']
                self.current_user_menu = False
    
    def apply_mappings(self):
        """Apply the entity-actor mappings by creating/updating actor tags"""
        print('Applying entity mappings...')
        
        # Ensure user entity is set
        if not self.user_entity:
            print('Error: No user entity selected!')
            return
        
        print('User entity set to: {0}'.format(self.user_entity))
        
        # Apply actor mappings
        for entity_id, actor in self.entity_mappings.items():
            try:
                # Find existing tag if any
                tagfld = None
                folders = self.game.scene_get_all_folders_raw()
                
                # Check if actor already has a tag
                for fld in folders:
                    if fld.name.startswith("-actor:"):
                        # Check if this folder is attached to our actor
                        try:
                            parent = HSNeoOCI.create_from_treenode(fld.treeNodeObject.parent.parent.parent)
                            if isinstance(parent, HSNeoOCIChar) and parent.objctrl == actor.objctrl:
                                tagfld = fld
                                break
                        except:
                            pass
                
                if tagfld:
                    # Update existing tag
                    print('Updating existing tag for {0}'.format(entity_id))
                    tagfld.name = "-actor:" + entity_id
                else:
                    # Create new tag
                    print('Creating new tag for {0}'.format(entity_id))
                    tagfld = HSNeoOCIFolder.add("-actor:" + entity_id)
                    tagfld.set_parent_treenodeobject(actor.objctrl.treeNodeObject.child[0].child[0])
                    
            except Exception as e:
                print('Error mapping entity {0}: {1}'.format(entity_id, str(e)))
        
        # Store user entity selection for the plugin to use
        # This will be handled in the startup flow integration
        self.game._harmony_user_entity = self.user_entity
        
        # Register actors after all mappings are done
        self.game.scenef_register_actorsprops()
        print('Entity mappings applied successfully')
        print('User entity: {0}'.format(self.user_entity))
    
    def close(self):
        """Close the dialog window"""
        if self.window_id:
            self.game.close_extra_window(self.window_id)
            self.window_id = None


def get_all_scene_actors(game):
    """
    Get all actor objects in scene, regardless of labeling.
    
    Args:
        game: VNNeoController instance
        
    Returns:
        list: List of Actor objects
    """
    actors = []
    
    studio = Studio.Instance
    dobjctrl = studio.dicObjectCtrl
    
    for key in dobjctrl.Keys:
        objctrl = dobjctrl[key]
        if isinstance(objctrl, OCIChar):
            actor = HSNeoOCIChar(objctrl).as_actor
            actors.append(actor)
    
    return actors
