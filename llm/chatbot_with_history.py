from llm.conversation_history_section import ConversationHistorySection
from safety_filter.safety_filter import safety_filter
from safety_filter.validator import ChatbotOutputValidator
from loggers.conversation_logger import ConversationLogger
import inspect

class ChatBotWithHistory():
    def __init__(self, llm):
        self.llm = llm
        self.conversation_history: list[ConversationHistorySection] = []
    
    def add_new_section(self, section_id: str):
        """
        Adds a new section to the conversation history.

        :param section_id: A string representing the ID of the section.
        """
        self.conversation_history.append(ConversationHistorySection(section_id))
        
    async def add_prompt(self, prompt, is_volatile=False, printer: callable = None):
        """
        Adds a new prompt to the current section of the conversation history.

        :param prompt: A string representing the prompt to add.
        :param is_volatile: A boolean indicating whether the prompt should be deleted when moving to the next section.
        :param should_print: A boolean indicating whether the prompt should be logged to the conversation logger.
        """
        self.conversation_history[-1].add_prompt(prompt, is_volatile=is_volatile)

        if printer is not None:
            await printer(prompt) if inspect.iscoroutinefunction(printer) else printer(prompt)
    
    def get_system_response(self, extended_context = None):
        """
        Get a system response. A system response is a response typically generated after Command: . For example if we asked the chatbot to return true or false.
        
        :param extended_context: An optional dictionary representing the extended context.
        :return: A string representing the system response.
        """
        tags = ["System:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)
    
    def get_user_response(self, extended_context = None):
        """
        Get a response of the chatbot that should be shown to the user. These are the responses that should be part of general conversation.
        
        :param extended_context: An optional dictionary representing the extended context.
        :return: A string representing the system response.
        """
        tags = ["Interviewer:"]
        return self._get_response(extended_context=extended_context, override_allowed_tags=tags)

    def _get_response(self, filtered=True, extended_context = None, override_allowed_tags = None) -> str:
        """
        Get the response of the chatbot given the current context

        Parameters
        ----------
        filtered : bool, optional (default=True)
            Whether the response should be filtered. Filtered means we guarantee that only one response is returned.
        override_allowed_tags : list[str], optional (default=None)
            If filtered is True, this parameter can be used to narrow down the allowed tags, for example, normally (Interviewer and System) are allowed, we can use it to only allow System
        extended_context : list[str], optional (default=None)
            Additional context that will be added to the current context. This is useful when the added context is temporary (e.g., reasking) but should not be part of the history

        Returns
        -------
        str
            The response of the chatbot
        """

        # filter all previous sections
        conversation_history_filtered = []
        for section in self.conversation_history[:-1]:
            conversation_history_filtered.extend(section.get_history(filtered=True))
        
        # current section provide in total (i.e, show also volatile prompts)
        conversation_history_filtered.extend(self.conversation_history[-1].get_history(filtered=False))
        
        if extended_context is None:
            response = self.llm("\n\n".join(conversation_history_filtered))
        else:
            response = self.llm("\n\n".join(conversation_history_filtered + extended_context))

        if filtered:
            filter_tags = ["Interviewer:", "System:"] if override_allowed_tags is None else override_allowed_tags
            (_, response) = safety_filter(response, ChatbotOutputValidator(filter_tags), self)

        return response

    
