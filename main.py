from chatbot_with_history import ChatBotWithHistory
from controller import Controller
from statemachine import CaseStateMachine
from dotenv import load_dotenv
import logging

if __name__ == '__main__':
    load_dotenv()

    # setup logger
    logname = 'logs/casey.log'
    logging.basicConfig(filename=logname,
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

    logging.info("Running Casey Casebot")

    logger = logging.getLogger('casey')


    case_state_machine = CaseStateMachine("case.json")
    chatbot = ChatBotWithHistory()

    controller = Controller(chatbot=chatbot, state_machine=case_state_machine)
    controller.start_case()