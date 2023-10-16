from statemachine.case_component import CaseComponent, CaseFrameworkComponent, CaseIntroductionComponent, CaseSynthesisComponent
from llm.chatbot_with_history import ChatBotWithHistory
import conversation_templates.factory as ConversationTemplate
import conversation_templates.initial_primer as initial_primer
import logging
from safety_filter.safety_filter import safety_filter
from safety_filter.validator import BooleanValidator, NextSectionIdValidator

from statemachine.statemachine import CaseStateMachine


class Controller():
    def __init__(self, chatbot: ChatBotWithHistory, state_machine: CaseStateMachine):
        self.chatbot = chatbot
        self.state_machine = state_machine
    
    def run_complete_case(self):
        self.chatbot.add_prompt(initial_primer.get_prompt(self.state_machine.problem_statement, self.state_machine.additional_information))
        self._introduce_case()
        self._loop_main_section()
        self._close_case()

    def test_section(self, section_history: list[str], conversation_history: list[str]):
        self.chatbot.add_prompt(initial_primer.get_prompt(self.state_machine.problem_statement, self.state_machine.additional_information))

        # Run the section history to bring the statemachine to the correct state
        for i, section_id in enumerate(section_history[:-1]):
            assert section_id == self.state_machine.getCurrentState(), "The section history should match the current state"
            self.state_machine.complete_current_state()
            self.advance_to_next_section(section_history[i+1])
        
        # add the conversation history to the chatbot
        for conversation in conversation_history:
            self.chatbot.add_prompt(conversation)

        # run the current section
        self.run_current_section()

        logging.debug(f"Test completed successfully")
        


    
    def _introduce_case(self):
        # a case must start with the introduction section
        current_section = self.state_machine.getCurrentState()
        assert isinstance(current_section, CaseIntroductionComponent), "The case must start with the introduction section"
        self.run_current_section()

        # a case should then continue with the framework section
        next_possible_states = self.state_machine.getNextPossibleStates()
        assert len(next_possible_states) == 1, "There should be exactly one possible next state, i.e. the framework"
        assert isinstance(next_possible_states[0], CaseFrameworkComponent), "The case should continue with the framework section"
        self.state_machine.advanceToState(next_possible_states[0].id)
        self.run_current_section()
    
    def _loop_main_section(self):
         # Start the loop guiding us throughout the case
        while True:
            next_possible_states = self.state_machine.getNextPossibleStates()
            assert len(next_possible_states) > 0, "There should be at least one possible next state"
            if len(next_possible_states) == 1 and isinstance(next_possible_states[0], CaseSynthesisComponent):
                # We have reached the end of the case, only the synthesis section is remaining
                self.state_machine.advanceToState(next_possible_states[0].id)
                break

            # We are in the main part of the case
            next_section_id = self.select_next_section(next_possible_states)
            self.state_machine.advanceToState(next_section_id)

            self.run_current_section()
    
    def _close_case(self):
        # Finally end the case with the synthesis section
        current_section = self.state_machine.getCurrentState()
        assert isinstance(current_section, CaseSynthesisComponent), "The case must end with the synthesis section"
        self.run_current_section()


    def run_current_section(self):
        section = self.state_machine.getCurrentState()
        conversation_template = ConversationTemplate.conversationTemplateFactory(section)

        # Introduce the section
        self.chatbot.add_prompt(conversation_template.get_introduction_prompt())
        res = self.chatbot.get_user_response()
        self.chatbot.add_prompt(res)

        # Run the section
        while True:
            # check if the section is completed
            self.chatbot.add_prompt(conversation_template.get_check_completion_prompt())
            user_input = input("User Input: ")
            self.chatbot.add_prompt(f"Candidate: {user_input}")

            is_completed_result = safety_filter(user_input, BooleanValidator(), self.chatbot)

            # check if we finished the section based on the response
            if  not is_completed_result:
                # The section is not completed
                self.chatbot.add_prompt("Command: Continue the conversation. Think about how to continue in a sensible way. Then respond with Interviewer: <your response>")
                res = self.chatbot._get_response()
                self.chatbot.add_prompt(res)
            else:
                # The section is completed
                self.state_machine.complete_current_state()
                break

    def select_next_section(self, next_possible_states: list[CaseComponent]):
        # Ask the candidate what he would like to do next
        self.chatbot.add_prompt("Command: We finished the last section, successfull. Did the candidate already provide some indication where he wants to move next. If yes answer with System: True, else with System: False")
        res = self.chatbot._get_response()
        did_provide_indication = safety_filter(res, BooleanValidator(), self.chatbot)
        #self.chatbot.add_prompt(res)

        if not did_provide_indication:
            self.chatbot.add_prompt("Command: Ask the candidate where he would like to move next")
            res = self.chatbot._get_response()
            self.chatbot.add_prompt(res)

            candidate_response = input("Candidate: ")
            self.chatbot.add_prompt(f"Candidate: {candidate_response}")
        
        logging.debug(f"Next possible states: {next_possible_states}")
        possible_options_to_continue =[f"{{id: {component.id}, question: {component.question}}}" for component in next_possible_states]
        possible_options_to_continue_string = "\n".join(possible_options_to_continue)
        self.chatbot.add_prompt(f"""Command: Compare the candidates response of where to continue, with the possible options from the reference solution. The options are:
{possible_options_to_continue_string}

If the candidate provided a close match respond with "System: (True, <id>)". Else choose one id of where to continue and respond with "System: (False, <id>)".""")
        res = self.chatbot._get_response()
        (did_match, id_to_continue) = safety_filter(res, NextSectionIdValidator(), self.chatbot)
        logging.debug(f"did_match: {did_match}, id_to_continue: {id_to_continue}")

        component_to_continue = None
        for component in next_possible_states:
            if component.id == id_to_continue:
                component_to_continue = component
                break
        
        assert component_to_continue is not None, f"The id {id_to_continue} should be one of the possible next states"

        if did_match:
            # The candidate did not provide a close match
            self.chatbot.add_prompt(f"Command: Tell the candidate that instead of his idea we want to look into the following question: {component_to_continue.question}")
        else:
            self.chatbot.add_prompt(f"Command: Tell the candidate that his idea was good. Tell him that we will look into the following question: {component_to_continue.question}")

        
        return component_to_continue.id

        
