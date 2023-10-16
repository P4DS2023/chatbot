from llm.chatbot_with_history import ChatBotWithHistory
from langchain.llms import VertexAI
from controller import Controller
from statemachine.statemachine import CaseStateMachine
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

    
    #llm = VertexAI(model_name="chat-bison")
    llm = VertexAI(max_output_tokens=2048)

    case_state_machine = CaseStateMachine("cases/case.json")
    chatbot = ChatBotWithHistory(llm=llm)

    controller = Controller(chatbot=chatbot, state_machine=case_state_machine)
    controller.run_complete_case()