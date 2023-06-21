# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains basic types required by all plugin modules.


# HarmonyClientModuleBase - used for registering further modules for handling events
class HarmonyClientModuleBase:
    def __init__(self, backend_handler):
        self.backendHandler = backend_handler
        self.active = False
        # Kaji Details - Put in dict later to allow more than 1 Kaji
        self.kaji = None
        # Chara Details - Put in dict later to allow more than 1 Chara
        self.chara = None

    def activate(self):
        self.backendHandler.register_event_handler(self)
        self.active = True

    def deactivate(self):
        self.backendHandler.unregister_event_handler(self)
        self.active = False

    def update_kaji(self, kaji_id, kaji_data):
        # TODO Add Handling by ID with kaji dict
        print '[{0}]: Updated Kaji:'.format(self.__class__.__name__)

        if kaji_data is None or len(kaji_data) == 0:
            self.kaji = None
            print '[{0}]: Kaji set to none'.format(self.__class__.__name__)

        if self.kaji is None:
            self.kaji = AIStatus()

        self.kaji.id = kaji_data["kaji_id"]
        self.kaji.room_id = kaji_data["kaji_room_id"]
        self.kaji.gender = kaji_data["kaji_gender"]
        self.kaji.name = kaji_data["kaji_name"]
        self.kaji.mood = kaji_data["kaji_mood"]
        self.kaji.behaviour = kaji_data["kaji_behaviour"]
        self.kaji.persona = kaji_data["kaji_persona"]
        self.kaji.status_message = kaji_data["kaji_status_message"]

        if isinstance(self.kaji, AIStatus):
            print '[{0}]: Room ID: {1}'.format(self.__class__.__name__, self.kaji.room_id)
            print '[{0}]: Gender: {1}.'.format(self.__class__.__name__, self.kaji.gender)
            print '[{0}]: Name: {1}.'.format(self.__class__.__name__, self.kaji.name)
            print '[{0}]: Mood: {1}.'.format(self.__class__.__name__, self.kaji.mood)
            print '[{0}]: Behaviour: {1}.'.format(self.__class__.__name__, self.kaji.behaviour)
            print '[{0}]: Persona: {1}.'.format(self.__class__.__name__, self.kaji.persona)
            print '[{0}]: Status Message: {1}.'.format(self.__class__.__name__, self.kaji.status_message)

    def update_chara(self, chara_id, chara):
        print '[{0}]: Updated Chara:'.format(self.__class__.__name__)
        self.chara = chara

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # To be implemented in subclasses
        return


# HarmonyLinkEvent - Base class for exchanging data with harmony link
class HarmonyLinkEvent:
    def __init__(self, event_id, event_type, status, payload):
        self.event_id = event_id
        self.type = event_type
        self.status = status
        self.payload = payload


# AIStatus - describes the current state of an AI character
class AIStatus:
    def __init__(self, room_id="", gender="", name="", mood="", behaviour="", persona="", status_message=""):
        self.room_id = room_id
        self.gender = gender
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message