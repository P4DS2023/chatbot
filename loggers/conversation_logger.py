class ConversationLogger:
    formatting_colors = {
        'Interviewer': '\033[94m', # blue
        'Candidate': '\033[92m', # green
        'Command': '\033[93m', # yellow
        'System': '\033[91m', # red
    }

    @classmethod
    def log(cls, text):

        if text == None or text == "":
            # print red warning that empty input was provided
            print(f"\033[91mEmpty Text provided to print function\033[0m")
            return

        for (tag, color) in cls.formatting_colors.items():
            if text.startswith(tag):
                print(f"{color}{text}\033[0m")
                return
        
        # print red warning that the following text does not belong to any formatting class
        print(f"\033[91mThe following text does not have a valid tag and could not be formated\033[0m")
        print(text)
        print("\n")