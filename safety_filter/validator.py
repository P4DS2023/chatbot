import re
class Validator():
    """
    Interface for a validator class used in the safety filter.
    """
    
    def validate(self, input: str)->(bool, any):
        raise NotImplementedError("The validate method needs to be implemented by the subclass")
    
    def reprompt(self):
        raise NotImplementedError("The reprompt method needs to be implemented by the subclass")
    
class ChatbotOutputValidator(Validator):
    """
    Validator implementation to validate the output of the chatbot.
    Basically this validator checks that only one response is given, and the response starts with one of the allowed tags.
    """
    def __init__(self, allowed_tags = ["Interviewer", "Command"]):
        tags_formatted = []
        for tag in allowed_tags:
            tags_formatted = tag[:-1] if tag.endswith(':') else tag
        self.allowed_tags = tags_formatted 
    
    def _find_tags(text) -> list[str]:
        """
        Find all tags in the input text. A tag is a string that starts with a capital letter and ends with a colon. For example "Interviewer:"

        :param text: A string representing the input text.
        :return: A list of strings representing the tags found in the input text. Tags are returned without the colon.
        """
        # Regular expression pattern to match tags
        pattern = r'\b[A-Z][a-z]*:'

        # Find all matches of the pattern in the input text
        matches = re.findall(pattern, text, re.MULTILINE)

        # Remove the ':' character from each match
        cleaned_matches = [match[:-1] for match in matches]

        return cleaned_matches

    def validate(self, input: str) -> (bool, str):
        return self._validate_loose(input)
    
    def _validate_strict(self, input:str) -> (bool, str):
        # find all tags in the input
        all_tags = ChatbotOutputValidator._find_tags(input)
        # check that exactly one tag was found
        if len(all_tags) != 1:
            return (False, None)

        # check that the tag is allowed
        if all_tags[0] not in self.allowed_tags:
            return (False, None)

        return (True, input.strip())

    def _validate_loose(self, input:str) -> (bool, str):
        # find all tags in the input
        all_tags = ChatbotOutputValidator._find_tags(input)
        if len(all_tags) == 0:
            return (False, None)

        # Step 1: Find index where all matches start
        tag_indices = {}
        for tag in all_tags:
            tag_indices[tag] = input.find(tag)
        
        # Step 2: Find the first tag
        first_tag = min(tag_indices, key=tag_indices.get)

        # check that this tag is allowed
        if first_tag not in self.allowed_tags:
            return (False, None)
        
        # Step 3: Strip all other tags
        tag_indices.pop(first_tag)
        if len(tag_indices) == 0:
            return (True, input.strip())
        
        second_earliest_tag = min(tag_indices, key=tag_indices.get)
        input = input[:input.find(second_earliest_tag)]
        return (True, input.strip())

    
    def call(self, context, chatbot):
        return chatbot._get_response(extended_context=context)

    def reprompt(self):
        return f"""Command: Do it again, but this time your response should be started with only of of the tags from the list [{self.allowed_tags}]. It must also not continue after this tag."""
        


class BooleanValidator(Validator):
    """
    Validator implementation to validate a boolean response. A boolean response is a response that is either "System: True" or "System: False".
    """
    def __init__(self):
        super().__init__()
        
    
    def validate(self, input_str: str)->(bool, bool):
        # Remove whitespace and "System:" prefix
        cleaned_string = input_str.replace('System:', '').replace('.', '').strip().lower()

        if cleaned_string == 'true':
            return (True, True)
        elif cleaned_string == 'false':
            return (True, False)
        else:
            return (False, None)
    
    def call(self, context, chatbot):
        return chatbot.get_system_response(extended_context=context)
    
    def reprompt(self):
        return """Command: Do it again, but this time respond with either "System: True" or "System: False"."""
    

class NextSectionIdValidator(Validator):
    """
    Validator implementation to validate a next section ID response. A next section ID response is a response that is of the form "System: (<bool>, <id>)".
    """
    def __init__(self, possible_next_states: list[str]):
        super().__init__()
        self.possible_next_states = possible_next_states

    def validate(self, input:str) -> (bool, (bool, str)):
        pattern = r'System:\s*\(([^,]+),\s*(\d+)\)'
        match = re.match(pattern, input)

        if match:
            bool_value = match.group(1).strip().lower() == 'true'
            id_value = match.group(2).strip()

            # check if id value is part of the possible next states
            if id_value not in self.possible_next_states:
                return (False, (None, None))
            
            return (True, (bool_value, id_value))
        else:
            return (False, (None, None))
    
    def call(self, context, chatbot):
        return chatbot.get_system_response(extended_context=context)
    
    def reprompt(self):
        id_list_string = ", ".join(self.possible_next_states)
        return f"""Command: Do it again, but this time respond with either "System: (True, <id>)" or "System: (False, <id>)". Remember that id must be any of [{id_list_string}]."""
    

# Tests
if __name__ == '__main__':
    boolean_validator = BooleanValidator()

    print(boolean_validator.validate("System: True"))
    print(boolean_validator.validate("System: False"))
    print(boolean_validator.validate("System is true"))

    chat_output_validator = ChatbotOutputValidator(allowed_tags=["Interviewer"])

    print(chat_output_validator.validate("Interviewer: Hello   \n Candidate: Yessir"))
    print(chat_output_validator.validate("System: Hello"))