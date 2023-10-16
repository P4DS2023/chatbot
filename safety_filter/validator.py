import re
class Validator():
    
    def validate(self, input: str)->(bool, any):
        raise NotImplementedError("The validate method needs to be implemented by the subclass")
    
    def reprompt(self):
        raise NotImplementedError("The reprompt method needs to be implemented by the subclass")
    
class ChatbotOutputValidator(Validator):
    def __init__(self, allowed_tags = ["Candidate:", "Interviewer:", "Command:", "System:"]):
        self.all_tags = ["Candidate:", "Interviewer:", "Command:", "System:"]
        self.allowed_tags = allowed_tags
    
    def validate(self, input:str) -> (bool, str):
        # for any of the tags find fist occurence
        tag_indices = []
        for tag in self.all_tags:
            if tag in input:
                if tag in self.allowed_tags:
                    tag_indices.append(input.index(tag))
                else:
                    return (False, None)
        
        # check that exactly one tag was found
        if len(tag_indices) != 1:
            return (False, None)
        
        # return everything after the tag
        return(True, input.strip())
    
    def call(self, context, chatbot):
        return chatbot._get_response(extended_context=context)

    def reprompt(self):
        return f"""Command: Do it again, but this time your response should be started with only of of the tags {self.allowed_tags}. It must also not continue after this tag."""
        


class BooleanValidator(Validator):
    def __init__(self):
        super().__init__()
    
    def validate(self, input: str)->(bool, bool):
        # Remove whitespace and "System:" prefix
        cleaned_string = input.replace('System:', '').strip().lower()

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
    def validate(self, input:str) -> (bool, (bool, str)):
        pattern = r'System:\s*\(([^,]+),\s*(\d+)\)'
        match = re.match(pattern, input)

        if match:
            bool_value = match.group(1).strip().lower() == 'true'
            id_value = match.group(2).strip()
            return (True, (bool_value, id_value))
        else:
            return (False, (None, None))
    
    def call(self, context, chatbot):
        return chatbot.get_system_response(extended_context=context)
    
    def reprompt(self):
        return """Command: Do it again, but this time respond with either "System: (True, <id>)" or "System: (False, <id>)"."""
    

# Tests
if __name__ == '__main__':
    boolean_validator = BooleanValidator()

    print(boolean_validator.validate("System: True"))
    print(boolean_validator.validate("System: False"))
    print(boolean_validator.validate("System is true"))