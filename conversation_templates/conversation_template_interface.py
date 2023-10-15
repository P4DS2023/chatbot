from abc import abstractmethod
from case_component import CaseComponent


class ConversationTemplateInterface():
    def __init__(self, case_component: CaseComponent):
        self.case_component = case_component

    @abstractmethod
    def get_introduction_prompt(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_check_completion_prompt(self):
        raise NotImplementedError