from safety_filter.safety_filter import safety_filter
from safety_filter.validator import ChatbotOutputValidator
from loggers.conversation_logger import ConversationLogger

class ChatBotWithHistory():
    def __init__(self, llm):
        self.llm = llm
        self.conversation_history = [] # list of list of objects {text: str, volatile: bool}, volatile mans that when going to the next section this part is deleted
    
    def add_new_section(self):
        self.conversation_history.append([])
        
    def _add_prompt(self, prompt, is_volatile=False, should_print=True):
        self.conversation_history[-1].append({"text": prompt, "volatile": is_volatile})

        if should_print:
            ConversationLogger.log(prompt)
    
    def get_system_response(self, extended_context = None):
        tags = ["System:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)
    
    def get_user_response(self, extended_context = None):
        tags = ["Interviewer:", "Candidate:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)

    def _get_response(self, filtered=True, extended_context = None, override_allowed_tags = None):
        
        # filter all previous sections
        conversation_history_filtered = []
        for section in self.conversation_history[:-1]:
            conversation_history_filtered.extend([prompt["text"] for prompt in section if not prompt["volatile"]])
        
        # current section provide in total (i.e, show also volatile prompts)
        conversation_history_filtered.extend([prompt["text"] for prompt in self.conversation_history[-1]])
        
        if extended_context is None:
            response = self.llm("\n\n".join(conversation_history_filtered))
        else:
            response = self.llm("\n\n".join(conversation_history_filtered + extended_context))

        if filtered:
            filter_tags = ["Interviewer:", "System:"] if override_allowed_tags is None else override_allowed_tags
            (_, response) = safety_filter(response, ChatbotOutputValidator(filter_tags), self)

        return response

    
