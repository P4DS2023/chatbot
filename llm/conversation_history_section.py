class ConversationHistorySection():
    """
    A class representing a section of conversation history.
    """
    def __init__(self, section_id: str):
        """
        Initializes a new instance of the ConversationHistorySection class.

        :param section_id: A string representing the ID of the section.
        """
        self.section_id = section_id
        self.conversation_history = [] # list of list of objects {text: str, volatile: bool}, volatile mans that when going to the next section this part is deleted
    
    def add_prompt(self, prompt, is_volatile=False):
        """
        Adds a new prompt to the conversation history.

        :param prompt: A string representing the prompt to add.
        :param is_volatile: A boolean indicating whether the prompt should be deleted when moving to the next section.
        """
        self.conversation_history.append({"text": prompt, "volatile": is_volatile})

    def get_history(self, filtered=False):
        """
        Gets the conversation history.

        :param filtered: A boolean indicating whether to filter out volatile prompts.
        :return: A list of strings representing the conversation history.
        """
        if filtered:
            return [prompt["text"] for prompt in self.conversation_history if not prompt["volatile"]]
        else:
            return [prompt["text"] for prompt in self.conversation_history]