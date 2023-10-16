import logging



def safety_filter(input: str, return_format_validator, chatbot):
    # We do not want to add all wrong responses to the full context
    # everything in the additional context will be forgotten afterwards
    additional_context = [input]
    
    max_no_tries = 10
    for i in range(max_no_tries):
        logging.debug(f"Iteration {i} trying to validate the input: {input}. Current interaction stack is {chatbot.conversation_history}")
        # Validate the input
        valid, return_value = return_format_validator.validate(input)
        if valid:
            return return_value
        else:
            additional_context.append(return_format_validator.reprompt())
            input = return_format_validator.call(context=additional_context, chatbot=chatbot)

    raise ValueError(f"Could not validate the input after {max_no_tries} tries")