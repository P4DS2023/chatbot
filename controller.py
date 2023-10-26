from loggers.conversation_logger import ConversationLogger
from statemachine.case_component import CaseComponent, CaseFrameworkComponent, CaseIntroductionComponent, CaseSynthesisComponent
from llm.chatbot_with_history import ChatBotWithHistory
import conversation_templates.factory as ConversationTemplate
import conversation_templates.initial_primer as initial_primer
import logging
from safety_filter.safety_filter import safety_filter
from safety_filter.validator import BooleanValidator, NextSectionIdValidator

from statemachine.statemachine import CaseStateMachine
import inspect


class Controller():
    def __init__(self, chatbot: ChatBotWithHistory, state_machine: CaseStateMachine, on_output: callable = None, on_input: callable = None):
        self.chatbot = chatbot
        self.state_machine = state_machine
        self.on_output = ConversationLogger.log if on_output is None else on_output
        self.is_input_async = inspect.iscoroutinefunction(on_input) # necessary because once called in the next step its no longer clear if it is async
        self.on_input = lambda: input("User Input:") if on_input is None else on_input() # I have no idea why I have to call this function
    
    async def take_input(self):
        if self.is_input_async:
            return await self.on_input()
        else:
            return self.on_input()
    
    async def run_complete_case(self):
        self.chatbot.add_new_section(section_id="primer")
        await self.chatbot.add_prompt(initial_primer.get_prompt(self.state_machine.problem_statement, self.state_machine.additional_information), is_volatile=False, printer=self.on_output)
        await self._introduce_case()
        await self._loop_main_section()
        await self._close_case()

    async def test_section(self, section_history: list[str], conversation_history: list[str]):
        await self.chatbot.add_prompt(initial_primer.get_prompt(self.state_machine.problem_statement, self.state_machine.additional_information), is_volatile=False)

        # Run the section history to bring the statemachine to the correct state
        for i, section_id in enumerate(section_history[:-1]):
            assert section_id == self.state_machine.getCurrentState(), "The section history should match the current state"
            self.state_machine.complete_current_state()
            self.advance_to_next_section(section_history[i+1])
        
        # add the conversation history to the chatbot
        for conversation in conversation_history:
            await self.chatbot.add_prompt(conversation)

        # run the current section
        self.run_current_section()

        logging.debug(f"Test completed successfully")
        
    async def _introduce_case(self):
        # a case must start with the introduction section
        current_section = self.state_machine.getCurrentState()
        assert isinstance(current_section, CaseIntroductionComponent), "The case must start with the introduction section"
        
        await self.run_current_section()

        # a case should then continue with the framework section
        next_possible_states = self.state_machine.getNextPossibleStates()
        assert len(next_possible_states) == 1, "There should be exactly one possible next state, i.e. the framework"
        assert isinstance(next_possible_states[0], CaseFrameworkComponent), "The case should continue with the framework section"
        self.state_machine.advanceToState(next_possible_states[0].id)
        
        
        await self.run_current_section()
    
    async def _loop_main_section(self):
         # Start the loop guiding us throughout the case
        while True:
            next_possible_states = self.state_machine.getNextPossibleStates()
            assert len(next_possible_states) > 0, "There should be at least one possible next state"
            if len(next_possible_states) == 1 and isinstance(next_possible_states[0], CaseSynthesisComponent):
                # We have reached the end of the case, only the synthesis section is remaining
                await self.state_machine.advanceToState(next_possible_states[0].id)
                break

            # We are in the main part of the case
            next_section_id = await self.select_next_section(next_possible_states)
            self.state_machine.advanceToState(next_section_id)

            await self.run_current_section()
    
    async def _close_case(self):
        # Finally end the case with the synthesis section
        current_section = self.state_machine.getCurrentState()
        assert isinstance(current_section, CaseSynthesisComponent), "The case must end with the synthesis section"
        await self.run_current_section()


    async def run_current_section(self):
        self.chatbot.add_new_section(section_id=self.state_machine.getCurrentState().id)
        section = self.state_machine.getCurrentState()
        conversation_template = ConversationTemplate.conversationTemplateFactory(section)

        # Introduce the section
        await self.chatbot.add_prompt(conversation_template.get_introduction_prompt(), is_volatile=False, printer=self.on_output)
        res = self.chatbot.get_user_response()
        await self.chatbot.add_prompt(res, is_volatile=False, printer=self.on_output)

        # Run the section
        while True:
            # check if the section is completed
            await self.chatbot.add_prompt(conversation_template.get_check_completion_prompt(), is_volatile=True, printer=self.on_output)
            user_input = await self.take_input()
            await self.chatbot.add_prompt(f"Candidate: {user_input}", printer=self.on_output)

            res = self.chatbot.get_system_response()
            (raw_result, is_completed_result) = safety_filter(res, BooleanValidator(), self.chatbot)
            await self.chatbot.add_prompt(raw_result, is_volatile=True, printer=self.on_output)

            # check if we finished the section based on the response
            if  not is_completed_result:
                # The section is not completed
                await self.chatbot.add_prompt("Command: Continue the conversation. Think about how to continue in a sensible way. Then respond with Interviewer: <your response>", is_volatile=True, printer=self.on_output)
                res = self.chatbot.get_user_response()
                await self.chatbot.add_prompt(res, is_volatile=False, printer=self.on_output)
            else:
                # The section is completed
                self.state_machine.complete_current_state()
                break

    async def select_next_section(self, next_possible_states: list[CaseComponent]):
        # Ask the candidate what he would like to do next
        await self.chatbot.add_prompt("Command: We finished the last section, successfully. Did the candidate already provide some indication where he wants to move next. If yes answer with System: True, else with System: False", is_volatile=True, printer=self.on_output)
        res = self.chatbot.get_system_response()
        (raw_result, did_provide_indication) = safety_filter(res, BooleanValidator(), self.chatbot)
        await self.chatbot.add_prompt(raw_result, is_volatile=True, printer=self.on_output)

        if not did_provide_indication:
            await self.chatbot.add_prompt("Command: Ask the candidate where he would like to move next", is_volatile=True, printer=self.on_output)
            res = self.chatbot.get_user_response()
            await self.chatbot.add_prompt(res, is_volatile=False, printer=self.on_output)

            candidate_response = await self.take_input()
            await self.chatbot.add_prompt(f"Candidate: {candidate_response}", is_volatile=False, printer=self.on_output)
        
        logging.debug(f"Next possible states: {next_possible_states}")
        possible_options_to_continue =[f"{{id: {component.id}, question: {component.question}}}" for component in next_possible_states]
        possible_options_to_continue_string = "\n".join(possible_options_to_continue)
        await self.chatbot.add_prompt(f"""Command: Compare the candidates response of where to continue, with the possible options from the reference solution. The options are:
{possible_options_to_continue_string}

If the candidate provided a close match respond with "System: (True, <id>)". Else choose one id of where to continue and respond with "System: (False, <id>)".""", is_volatile=True, printer=self.on_output)
        res = self.chatbot.get_system_response()
        (raw_result, (did_match, id_to_continue)) = safety_filter(res, NextSectionIdValidator(possible_next_states=[component.id for component in next_possible_states]), self.chatbot)
        await self.chatbot.add_prompt(raw_result, is_volatile=True, printer=self.on_output)
        
        logging.debug(f"did_match: {did_match}, id_to_continue: {id_to_continue}")

        component_to_continue = None
        for component in next_possible_states:
            if component.id == id_to_continue:
                component_to_continue = component
                break
        
        assert component_to_continue is not None, f"The id {id_to_continue} should be one of the possible next states"

        if did_match:
            # The candidate did not provide a close match
            await self.chatbot.add_prompt(f"Command: Tell the candidate that instead of his idea we want to look into the following question: {component_to_continue.question}", is_volatile=True, printer=self.on_output)
        else:
            await self.chatbot.add_prompt(f"Command: Tell the candidate that his idea was good. Tell him that we will look into the following question: {component_to_continue.question}", is_volatile=True, printer=self.on_output)

        res = self.chatbot.get_user_response()
        await self.chatbot.add_prompt(res, is_volatile=False, printer=self.on_output)
        
        return component_to_continue.id

        
