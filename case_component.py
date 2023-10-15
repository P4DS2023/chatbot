from enum import Enum, IntEnum

class CaseComponentType(Enum):
    INTRODUCTION = 0
    FRAMEWORK = 1
    QUESTION = 2
    SYNTHESIS = 3

class CaseComponent():
    def __init__(self, id, raw_json_string):
        self.id = id
        self.beenCompleted = False

        try:
            self.reference_solution = "\n".join(raw_json_string["referenceSolution"])
        except:
            self.reference_solution = None

        try:
            self.additional_commands = "\nCommand: ".join(raw_json_string["additionalCommands"])
        except:
            self.additional_commands = None
        
        try:
            self.additional_information = "\n".join(raw_json_string["additionalInformation"])
        except:
            self.additional_information = None
    
    @classmethod
    def factory(cls, id, raw_json_string):
        if raw_json_string["type"] == "framework":
            return CaseFrameworkComponent(id, raw_json_string)
        elif raw_json_string["type"] == "question":
            return CaseQuestionFrameworkComponent(id, raw_json_string)
        elif raw_json_string["type"] == "synthesis":
            return CaseSynthesisComponent(id, raw_json_string)
        elif raw_json_string["type"] == "introduction":
            return CaseIntroductionComponent(id, raw_json_string)
        else:
            raise Exception("Unknown case component type")
        
    def __str__(self):
        return f"{{Type: {self.type}, Id: {self.id}}}"
    
    def toJSON(self):
        return self.__str__()
    
class CaseIntroductionComponent(CaseComponent):
    def __init__(self, id, raw_json_string):
        super().__init__(id, raw_json_string)
        self.type = CaseComponentType.INTRODUCTION
        #self.prompt = raw_json_string["prompt"]

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