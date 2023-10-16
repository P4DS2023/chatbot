
from statemachine.case_component import CaseComponent
from conversation_templates.conversation_template_interface import ConversationTemplateInterface


class CaseIntroductionTemplate(ConversationTemplateInterface):
    def __init__(self, case_component: CaseComponent):
        super().__init__(case_component)

    def get_introduction_prompt(self):
        return "Command: We just entered the start of the case interview. Start the case by introducing yourself to the candidate and stating the problem statement and ask the candidate if he has any questions."
    
    def get_check_completion_prompt(self):  
        return f"""Command: Take the next response of the candidate to evaluate if this part of the case study is completed. The section is completed if:
- The candidate does not want any more information. If the candidate indicated that he wants to construct a framework this section is also completed.
            
If the section is not completed respond with System: False. If the section is finished respond with System: True.
"""