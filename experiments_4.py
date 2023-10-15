# %% Setup
from dotenv import load_dotenv
from chatbot_with_history import ChatBotWithHistory
from statemachine import CaseStateMachine
from importlib import reload

# load environment variables from .env file
load_dotenv()

chatbot = ChatBotWithHistory()
case_state_machine = CaseStateMachine("case.json")

# %% Start the case
import conversation_templates.case_introduction as case_introduction
import conversation_templates.initial_primer as initial_primer

chatbot.add_prompt(initial_primer.get_prompt(case_state_machine.problem_statement, case_state_machine.additional_information))

chatbot.add_prompt(case_introduction.get_prompt())

res = chatbot.get_response()
print(res)
chatbot.add_prompt(res)

# %% Continue the case
reload(initial_primer)
can_continue_prompt = f"""Command: Take the next response of the interviewee to evaluate if this part of the case study is completed. The section is completed if:
{case_introduction.check_completed()}
\nIf the section is not completed respond with System: False. If the section is finished respond with System: True."""

print(can_continue_prompt)

# %%
while True:
    chatbot.add_prompt(can_continue_prompt)
    user_input = input("Enter your input: ")
    chatbot.add_prompt(f"Candidate: {user_input}")
    res = chatbot.get_response(filtered=True)

    print(res)

    if "System: False" in res:
        print("The section is not completed")
        chatbot.add_prompt("Command: Continue the conversation. Think about how to continue in a sensible way. Then respond with Interviewer: <your response>")
        res = chatbot.get_response()
        print(res)
    else:
        print("The section is completed")
        break
# %%
