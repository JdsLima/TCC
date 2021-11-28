
class formateText():
    def __init__(self, text) -> None:
        self.text = text
        self.formate(self.text)

    command_list = [
        "negrito", 
        "itálico", 
        "sublinhado"
    ]

    command_action = dict(
        negrito = ["[b]", "[/b]"],
        itálico = ["[i]", "[/i]"],
        sublinhado = ["[u]", "[/u]"])

    def edit(self, text):
        pass

    def formate(self, text):
        for i, str in enumerate(text):
            if "Yumi" in str and i + 1 < (len(text) - 1):
                command = text[i + 1]
                if (command in self.command_list):
                    del(text[i])
                    text[i] = self.command_action.get(text[i])[0]
                elif (command == "fim" and text[i + 2] in self.command_list):
                    del(text[i + 1])
                    del(text[i])
                    text[i] = self.command_action.get(text[i])[1]
        print(" ".join(text))
    
text = ["Yumi", "negrito", "testando", "texto", "em", "negrito", "Yumi", "fim", "negrito"]
a = formateText(text)
