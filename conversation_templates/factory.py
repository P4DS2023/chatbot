from case_component import CaseComponentType
from conversation_templates.case_introduction import CaseIntroductionTemplate
from conversation_templates.framework_template import FrameworkTemplate


def conversationTemplateFactory(case_component):
    if case_component.type == CaseComponentType.INTRODUCTION:
        return CaseIntroductionTemplate(case_component)
    elif case_component.type == CaseComponentType.FRAMEWORK:
        return FrameworkTemplate(case_component)
    # elif case_component.type == CaseComponentType.MAIN:
    #     return CaseMainTemplate(case_component)
    # elif case_component.type == CaseComponentType.SYNTHESIS:
    #     return CaseSynthesisTemplate(case_component)
    else:
        raise Exception("Unknown case component type")