from safety_filter.safety_filter import safety_filter
from safety_filter.validator import ChatbotOutputValidator
from utils.filter import filter_llm_response
from loggers.conversation_logger import ConversationLogger

class ChatBotWithHistory():
    def __init__(self, llm):
        self.llm = llm
        self.conversation_history = []
    
    def add_prompt(self, prompt, should_print=True):
        self.conversation_history.append(prompt)

        if should_print:
            ConversationLogger.log(prompt)
    
    def get_system_response(self, extended_context = None):
        tags = ["System:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)
    
    def get_user_response(self, extended_context = None):
        tags = ["Interviewer:", "Candidate:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)

    def _get_response(self, filtered=True, extended_context = None, override_allowed_tags = None):
        if extended_context is None:
            response = self.llm("\n\n".join(self.conversation_history))
        else:
            response = self.llm("\n\n".join(self.conversation_history + extended_context))

        if filtered:
            filter_tags = ["Interviewer:", "System:"] if override_allowed_tags is None else override_allowed_tags
            return safety_filter(response, ChatbotOutputValidator(filter_tags), self)

        return response

    
