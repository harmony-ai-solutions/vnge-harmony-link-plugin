# Koikaji Countenance Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# VNGE
# from vngameengine import vnge_game as game
# from vnlibfaceexpressions import conf_neo_male, conf_neo_female
# from vnactor import char_act_funcs

# Import Backend base Module
from connector import *
from harmony_modules.common import HarmonyClientModuleBase
from kajiwoto import RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH, RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS

# Custom expressions - Fork from vnlibfaceexpressions
# expressions_default = conf_neo_male.copy()
# expressions_male = expressions_default.copy()
# expressions_female = expressions_default.copy()
# expressions_female.update(conf_neo_female)
# Custom expressions
# TODO


# CountenanceHandler - module main class
class CountenanceHandler(HarmonyClientModuleBase):
    def __init__(self, backend_handler, countenance_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = countenance_config

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # Kaji Status update
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS and rpc_response.result == RPC_RESULT_SUCCESS:
            self.update_kaji("", kaji_data=rpc_response.params)
            # Update face expression based on status context
            self.update_chara_from_state("")

        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH and rpc_response.result == RPC_RESULT_SUCCESS:

            utterance_data = rpc_response.params

            if utterance_data["type"] == "UTTERANCE_NONVERBAL" and len(utterance_data["content"]) > 0:
                # Update face expression based on nonverbal action context
                self.update_chara_from_action("", utterance_data["content"])

        return

    def update_chara_from_state(self, chara_id):
        if self.chara is None or self.kaji is None:
            return

        # Step 1: Determine behavioural stance
        # Step 2: Determine Mood
        if self.kaji.behaviour == "SAD":
            if self.kaji.mood == "SAD":
                self.apply_expression(chara_id, self.kaji.gender, 'sad', True)
            else:  # "DEFAULT"
                self.apply_expression(chara_id, self.kaji.gender, 'unhappy', True)

        elif self.kaji.behaviour == "SLEEP":
            if self.kaji.mood == "SAD":
                self.apply_expression(chara_id, self.kaji.gender, 'unhappy_eyes_closed', True)
            else:  # "DEFAULT"
                self.apply_expression(chara_id, self.kaji.gender, 'sleeping', True)

        elif self.kaji.behaviour == "ANGRY":
            if self.kaji.mood == "ANGRY":
                self.apply_expression(chara_id, self.kaji.gender, 'very_angry', True)
            else:  # "DEFAULT"
                self.apply_expression(chara_id, self.kaji.gender, 'angry_whatyousay', True)

        else: # "DEFAULT"
            if self.kaji.mood == "HAPPY":
                self.apply_expression(chara_id, self.kaji.gender, 'happy_smile', True)
            else: # "DEFAULT"
                self.apply_expression(chara_id, self.kaji.gender, 'normal', True)


    def update_chara_from_action(self, chara_id, action_description):
        if self.chara is None or self.kaji is None:
            return

    def apply_expression_delayed(self, chara_id, gender, expression_name, update_base_expression=False, delay=5):
        time.sleep(delay)
        self.apply_expression(chara_id, gender, expression_name, update_base_expression)

    def apply_expression(self, chara_id, gender, expression_name, update_base_expression=False):
        # expression = expressions_default[expression_name]
        # if gender == "F" and expression_name in expressions_female:
        #     expression = expressions_female[expression_name]
        # elif gender == "M" and expression_name in expressions_male:
        #     expression = expressions_male[expression_name]
        #
        # # for function in expression:
        # #     if function in char_act_funcs:
        # #         char_act_funcs[function][0](self.chara.actor, expression[function])
        #
        if update_base_expression:
            self.chara.current_base_expression = expression_name
        # elif expression != self.chara.current_base_expression:
        #     # Revert timer
        #     revert_thread = Thread(target=self.apply_expression_delayed(
        #         chara_id,
        #         gender,
        #         self.chara.current_base_expression,
        #         update_base_expression=True,
        #         delay=2
        #     ))
        #     revert_thread.start()
