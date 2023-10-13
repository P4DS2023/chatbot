import json
from pprint import pprint
from case_component import CaseComponent
from case_structure_component import CaseStructureComponent, CaseStructureComponentType
from utils.json import Json

class CaseStateMachine():
    def __init__(self, case_path):
        self.case_path = case_path
        
        # read raw string and convert to json
        with open(self.case_path, "r") as f:
            self.case_structure_json = json.load(f)

        self.parsed_case_structure = self._parseCaseStructure(self.case_structure_json)
        self.current_state = self._getInitialState(self.parsed_case_structure)
    
    def getCurrentState(self):
        return self.current_state
    
    def get_stack_to_element(self, id) -> list[CaseStructureComponent]:
        def get_stack_to_element_recursively(element_id, structure_stack: list[CaseStructureComponent]) -> (list[CaseStructureComponent], bool):
            current_element = structure_stack[-1]

            for child in current_element.children:
                if isinstance(child, CaseComponent):
                    if child.id == element_id:
                        return (structure_stack, True)
                
                elif isinstance(child, CaseStructureComponent):
                    structure_stack.append(child)
                    (result, found) = get_stack_to_element_recursively(element_id, structure_stack)
                    if found:
                        return (result, found)
                    else:
                        structure_stack.pop()
                
                else:
                    raise Exception("Unknown case structure element")
            
            return (structure_stack, False)

        structure_stack = [self.parsed_case_structure]
        (stack_to_current_element, found) = get_stack_to_element_recursively(id, structure_stack)

        if not found:
            raise Exception("Current state not found in case structure")

        return stack_to_current_element


    def getNextPossibleStates(self):
        stack_to_current_element = self.get_stack_to_element(self.current_state.id)

        def recursive_pop_until_non_completed_element(stack: list[CaseStructureComponent]):
            if len(stack)==0:
                return []
            
            current_element = stack.pop()
            elements_to_continue = current_element.get_elements_to_continue()
            if len(elements_to_continue) > 0:
                return elements_to_continue
            else:
                return recursive_pop_until_non_completed_element(stack)
            
        return recursive_pop_until_non_completed_element(stack_to_current_element)
    
    def advanceToState(self, stateId):
        return
    
    def _getInitialState(self, parsed_case_structure):
        """
        Get the initial state of the case structure. This is the first element of the case structure.
        """
        assert isinstance(parsed_case_structure, CaseStructureComponent)
        assert parsed_case_structure.type == CaseStructureComponentType.SEQUENTIAL

        return parsed_case_structure.children[0]
        

    def _readCaseInformation(self, case_json):
        """
        Read case information from json file, create new dictionary with case components indexed by the id of the component
        """
        case_component_dict = {}
        for (id, value) in case_json["caseComponents"].items():
            case_component = CaseComponent.factory(id, value)
            case_component_dict[id] = case_component

        return case_component_dict
    
    def _parseCaseStructure(self, case_json):
        """
        Parse the whole case structure form the json file. The result is a nested list of the same shape as in the json file, however, instead
        of the ids of the case components, the actual case components are used.
        """
        case_component_dict = self._readCaseInformation(case_json)
        case_structure_template = case_json["caseStructure"]

        def recursive_case_structure_runner(case_structure_template):
            component_type = CaseStructureComponent.component_type_from_string(case_structure_template["type"])
            children_template = case_structure_template["children"]

            children = []
            for child in children_template:
                if isinstance(child, str):
                    children.append(case_component_dict[child])
                elif isinstance(child, dict):
                    children.append(recursive_case_structure_runner(child))
                else:
                    raise Exception("Unknown case structure element")
            
            return CaseStructureComponent(component_type, children)
        
        return recursive_case_structure_runner(case_structure_template)

    

if __name__ == "__main__":
    case_state_machine = CaseStateMachine("case.json")

    #print(json.dumps(case_state_machine.parsed_case_structure))
    #print(case_state_machine.getCurrentState())

    #stack = case_state_machine.get_stack_to_element("4")
    #print(stack)

    # next_possible_states = case_state_machine.getNextPossibleStates()
    # next_possible_state = next_possible_states[0]
    
    # next_possible_state.beenCompleted = True

    # next_possible_states = case_state_machine.getNextPossibleStates()
    # print(next_possible_states)

    current_state = case_state_machine.getCurrentState()
    print(case_state_machine.parsed_case_structure)
