class ConversationHistorySection():
    def __init__(self, section_id: str):
        self.section_id = section_id
        self.conversation_history = [] # list of list of objects {text: str, volatile: bool}, volatile mans that when going to the next section this part is deleted
    
    def add_prompt(self, prompt, is_volatile=False):
        self.conversation_history.append({"text": prompt, "volatile": is_volatile})

    def get_history(self, filtered=False):
        if filtered:
            return [prompt["text"] for prompt in self.conversation_history if not prompt["volatile"]]
        else:
            return [prompt["text"] for prompt in self.conversation_history]