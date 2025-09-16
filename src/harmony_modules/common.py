# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains basic types required by all plugin modules.

from harmony_modules.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)


# Event States
EVENT_STATE_DONE = 'SUCCESS'  # Event was handled and returned successfully.
EVENT_STATE_ERROR = 'ERROR'  # Event processing failed for some reason.
EVENT_STATE_NEW = 'NEW'  # Event is new and has not been processed yet
EVENT_STATE_PENDING = 'PENDING'  # Event is in pending state (currently being processed)

# Event Types
# Initialization
EVENT_TYPE_INIT_ENTITY = 'INIT_ENTITY'
EVENT_TYPE_ENVIRONMENT_LOADED = 'ENVIRONMENT_LOADED'
EVENT_TYPE_FETCH_CONFIGURED_ENTITIES = 'FETCH_CONFIGURED_ENTITIES'
# Chat LLM
EVENT_TYPE_CHAT_HISTORY = 'CHAT_HISTORY'
EVENT_TYPE_AI_STATUS = 'AI_STATUS'
EVENT_TYPE_AI_SPEECH = 'AI_SPEECH'
EVENT_TYPE_AI_ACTION = 'AI_ACTION'
EVENT_TYPE_USER_UTTERANCE = 'USER_UTTERANCE'
# Countenance
EVENT_TYPE_AI_COUNTENANCE_UPDATE = 'AI_COUNTENANCE_UPDATE'
# Movement
EVENT_TYPE_MOVEMENT_V1_REQUEST_SCENE_DATA = 'MOVEMENT_V1_REQUEST_SCENE_DATA'
EVENT_TYPE_MOVEMENT_V1_UPDATE_SCENE_DATA = 'MOVEMENT_V1_UPDATE_SCENE_DATA'
EVENT_TYPE_MOVEMENT_V1_REQUEST_ACTIONS = 'MOVEMENT_V1_REQUEST_ACTIONS'
EVENT_TYPE_MOVEMENT_V1_REGISTER_ACTION = 'MOVEMENT_V1_REGISTER_ACTION'
EVENT_TYPE_MOVEMENT_V1_REGISTER_ACTIONS = 'MOVEMENT_V1_REGISTER_ACTIONS'
EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS = 'MOVEMENT_V1_PERFORM_ACTIONS'
# STT
EVENT_TYPE_STT_START_LISTEN = 'STT_START_LISTEN'
EVENT_TYPE_STT_STOP_LISTEN = 'STT_STOP_LISTEN'
EVENT_TYPE_STT_INPUT_AUDIO = 'STT_INPUT_AUDIO'
EVENT_TYPE_STT_OUTPUT_TEXT = 'STT_OUTPUT_TEXT'
EVENT_TYPE_STT_SPEECH_STARTED = 'STT_SPEECH_STARTED'
EVENT_TYPE_STT_SPEECH_STOPPED = 'STT_SPEECH_STOPPED'
EVENT_TYPE_STT_FETCH_MICROPHONE = 'STT_FETCH_MICROPHONE'
EVENT_TYPE_STT_FETCH_MICROPHONE_RESULT = 'STT_FETCH_MICROPHONE_RESULT'
# TTS
EVENT_TYPE_TTS_PLAYBACK_DONE = 'TTS_PLAYBACK_DONE'
EVENT_TYPE_TTS_GENERATE_SPEECH = 'TTS_GENERATE_SPEECH'
# Movement

# Perception
EVENT_TYPE_PERCEPTION_ACTOR_UTTERANCE = 'PERCEPTION_ACTOR_UTTERANCE'
EVENT_TYPE_PERCEPTION_ACTOR_ACTION = 'PERCEPTION_ACTOR_ACTION'

# Utterance Types
UTTERANCE_COMBINED = 'UTTERANCE_COMBINED'
UTTERANCE_VERBAL = 'UTTERANCE_VERBAL'
UTTERANCE_NONVERBAL = 'UTTERANCE_NONVERBAL'
UTTERANCE_NONVERBAL_DELAYED = 'UTTERANCE_NONVERBAL_DELAYED'


# HarmonyClientModuleBase - used for registering further modules for handling events
class HarmonyClientModuleBase:
    def __init__(self, entity_controller):
        self.entity_controller = entity_controller
        self.backend_connector = entity_controller.connector
        self.active = False
        # AI State Details
        self.ai_state = None
        self.countenance_state = None
        # Chara Details
        self.chara = None

    def activate(self):
        self.backend_connector.register_event_handler(self)
        self.active = True

    def deactivate(self):
        self.backend_connector.unregister_event_handler(self)
        self.active = False

    def is_active(self):
        return self.active

    def update_ai_state(self, ai_state):
        logger.info('Updated AI State')

        if ai_state is None or len(ai_state) == 0:
            self.ai_state = None
            logger.info('AI State set to None')
            return

        if self.ai_state is None:
            self.ai_state = AIState()

        self.ai_state.gender = ai_state["gender"]
        self.ai_state.name = ai_state["name"]
        self.ai_state.mood = ai_state["mood"]
        self.ai_state.behaviour = ai_state["behaviour"]
        self.ai_state.persona = ai_state["persona"]
        self.ai_state.status_message = ai_state["status_message"]

        logger.info('Gender: %s.', self.ai_state.gender)
        logger.info('Name: %s.', self.ai_state.name)
        logger.info('Mood: %s.', self.ai_state.mood)
        logger.info('Behaviour: %s.', self.ai_state.behaviour)
        logger.info('Persona: %s.', self.ai_state.persona)
        logger.info('Status Message: %s.', self.ai_state.status_message)

    def update_chara(self, chara):
        logger.info('Updated Chara')
        self.chara = chara

    def handle_event(
        self,
        event  # HarmonyLinkEvent
    ):
        # To be implemented in subclasses
        return


# HarmonyLinkEvent - Base class for exchanging data with harmony link
class HarmonyLinkEvent:
    def __init__(self, event_id, event_type, status, payload):
        self.event_id = event_id
        self.event_type = event_type
        self.status = status
        self.payload = payload


# AIState - describes the current state of an AI character
class AIState:
    def __init__(self, gender="", name="", mood="", behaviour="", persona="", status_message=""):
        self.gender = gender
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message


def get_actors_distance(actor1, actor2):
    actor1_pos = actor1.pos()
    actor2_pos = actor2.pos()
