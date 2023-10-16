import logging

def safety_filter(input_str: str, return_format_validator, chatbot):
    """
    Used to filter the output of the chatbot given a specific expected format.

    Parameters
    ----------
    input_str : str
        The input string to be validated.
    return_format_validator : Validator defining the format and extracting the information
        The validator that will be used to validate the input string.
    chatbot : ChatBotWithHistory

    Returns
    -------
    tuple
        A tuple containing the raw text after validation as well as extracted information.
    """
    # We do not want to add all wrong responses to the full context
    # everything in the additional context will be forgotten afterwards
    additional_context = [input_str]
    
    max_no_tries = 10
    for i in range(max_no_tries):
        logging.debug(f"Iteration {i} trying to validate the input: {input_str}.")
        # Validate the input
        valid, return_value = return_format_validator.validate(input_str)
        if valid:
            # If the input is valid, return it also add it to the chatbot history
            return (input_str, return_value)
        else:
            additional_context.append(return_format_validator.reprompt())
            input_str = return_format_validator.call(context=additional_context, chatbot=chatbot)

    raise ValueError(f"Could not validate the input after {max_no_tries} tries")