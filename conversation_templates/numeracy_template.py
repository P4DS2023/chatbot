from statemachine.case_component import CaseComponent
from conversation_templates.conversation_template_interface import ConversationTemplateInterface

class NumeracyTemplate(ConversationTemplateInterface):
    def __init__(self, case_component: CaseComponent):
        super().__init__(case_component)
    
    def get_introduction_prompt(self):
        return f"""Command: We are now at the start of one question of the case. This is a numeracy question and thus involves a lot of calculations. The question to for the candidate to answer is the following:
{self.case_component.question}

Additional information you should provide the candidate when they ask for it is:
{self.case_component.additional_information}

A reference solution of steps to solve the question is the following:
{self.case_component.reference_solution}

Command: Start this section by asking the candidate to solve the question. Make sure that your wording fits into the previous conversation with the candidate.
"""
    
    def get_check_completion_prompt(self):  
        return f"""Command: Take the next response of the candidate to evaluate if this part of the case study is completed. To evaluate if the question is completed use the following criteria:
- Check if the candidate approach is right and if it guides us towards the goal, else help him to get on the right track
- Check if the math is right, if not tell the candidate where he must redo calculations
- Check if the candidate got to the complete result, only after that continue the case
- Be very critical and do not let the candidate leave before this section is completed
"""