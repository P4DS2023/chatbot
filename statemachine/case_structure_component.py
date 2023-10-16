from abc import abstractmethod
from enum import Enum

from statemachine.case_component import CaseComponent

class CaseStructureComponentType(Enum):
    SEQUENTIAL = 1
    PARALLEL = 2

class CaseStructureComponent():
    def __init__(self, type, children):
        self.type = type
        self.children = children

    def __str__(self):
        children_string = "\n".join([str(child) for child in self.children])
        return f"{{Type: {self.type}, Children: [{children_string}]}}"
      
    def get_elements_to_continue(self):
        if self.type == CaseStructureComponentType.SEQUENTIAL:
            return self._get_elements_to_continue_sequential()
        elif self.type == CaseStructureComponentType.PARALLEL:
            return self._get_elements_to_continue_parallel()
        else:
            raise Exception("Unknown case structure component type")

    
    def _get_elements_to_continue_sequential(self):

        for child in self.children:
            if isinstance(child, CaseComponent):
                if not child.beenCompleted:
                    return [child]
            
            elif isinstance(child, CaseStructureComponent):
                elements_to_continue = child.get_elements_to_continue()
                if len(elements_to_continue) > 0:
                    return elements_to_continue
            else:
                raise Exception("Unknown case structure element")
        
        return []

    
    def _get_elements_to_continue_parallel(self):
        elements_to_continue = []
        for child in self.children:
            if isinstance(child, CaseComponent):
                if not child.beenCompleted:
                    elements_to_continue.append(child)
            
            elif isinstance(child, CaseStructureComponent):
                elements_to_continue.extend(child.get_elements_to_continue())
            else:
                raise Exception("Unknown case structure element")
        
        return elements_to_continue
    
    
    @abstractmethod
    def component_type_from_string(str):
        if str == "sequential":
            return CaseStructureComponentType.SEQUENTIAL
        elif str == "parallel":
            return CaseStructureComponentType.PARALLEL
        else:
            raise Exception("Unknown case structure component type")