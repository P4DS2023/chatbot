from enum import Enum, IntEnum
from abc import abstractmethod

class CaseComponentType(Enum):
    FRAMEWORK = 1
    QUESTION = 2
    SYNTHESIS = 3

class CaseComponent():
    def __init__(self, id, raw_json_string):
        self.id = id
        self.beenCompleted = False
        self.reference_solution = "\n".join(raw_json_string["referenceSolution"])

        try:
            self.additional_commands = "\nCommand: ".join(raw_json_string["additionalCommands"])
        except:
            self.additional_commands = None
        
        try:
            self.additional_information = "\n".join(raw_json_string["additionalInformation"])
        except:
            self.additional_information = None
    
    @abstractmethod
    def factory(id, raw_json_string):
        if raw_json_string["type"] == "framework":
            return CaseFrameworkComponent(id, raw_json_string)
        elif raw_json_string["type"] == "question":
            return CaseQuestionFrameworkComponent(id, raw_json_string)
        elif raw_json_string["type"] == "synthesis":
            return CaseSynthesisComponent(id, raw_json_string)
        else:
            raise Exception("Unknown case component type")
        
    def __str__(self):
        return f"{{Type: {self.type}, Id: {self.id}}}"
    
    def toJSON(self):
        return self.__str__()

class CaseFrameworkComponent(CaseComponent):
    def __init__(self, id, raw_json_string):
        super().__init__(id, raw_json_string)
        self.type = CaseComponentType.FRAMEWORK
    
    def __str__(self):
        return f"{{Type: {self.type}, Id: {self.id}}}"
    
    def toJSON(self):
        return self.__str__()

class CaseQuestionFrameworkComponent(CaseComponent):
    def __init__(self, id, raw_json_string):
        super().__init__(id, raw_json_string)
        self.type = CaseComponentType.QUESTION
        self.question_type = raw_json_string["questionType"]
        self.question = raw_json_string["question"]
    
    def __str__(self):
        return f"{{Type: {self.type}, Id: {self.id}, QuestionType: {self.question_type}, Question: {self.question}}}"

class CaseSynthesisComponent(CaseComponent):
    def __init__(self, id, raw_json_string):
        super().__init__(id, raw_json_string)
        self.type = CaseComponentType.SYNTHESIS
        self.task = raw_json_string["task"]
    
    def __str__(self):
        return f"{{Type: {self.type}, Id: {self.id}, Task: {self.task}}}"