from langchain.llms import OpenAI
from utils.filter import filter_llm_response
from loggers.conversation_logger import ConversationLogger

class ChatBotWithHistory():
    def __init__(self):
        self.llm = OpenAI()
        self.conversation_history = []
    
    def add_prompt(self, prompt, should_print=True):
        self.conversation_history.append(prompt)

        if should_print:
            ConversationLogger.log(prompt)
    
    def get_response(self, filtered=True):
        response = self.llm("\n\n".join(self.conversation_history))

        if filtered:
            return filter_llm_response(response)

        return response

    
