
class formateText():
    def __init__(self, text) -> None:
        self.text = text
        self.formate(self.text)

    command_flags = dict(
        negrito = False, 
        itálico = False, 
        sublinhado = False
    )

    command_action = dict(
        negrito = ["[b]", "[/b]"],
        itálico = ["[i]", "[/i]"],
        sublinhado = ["[u]", "[/u]"]
    )

    def formate(self, text):
        commandKeys = self.command_flags.keys()

        for i, str in enumerate(text):
            if "Yumi" in str and i + 1 < (len(text) - 1):
                command = text[i + 1]
                if (command in commandKeys):
                    del(text[i])
                    text[i] = self.command_action.get(text[i])[0]
                    self.command_flags[command] = True

                elif (command == "fim"):
                    command = text[i + 2]
                    if command in commandKeys and self.command_flags[command]:
                        del(text[i + 1])
                        del(text[i])
                        text[i] = self.command_action.get(text[i])[1]

        print(" ".join(text))
    
text = ["Yumi", "negrito", "testando", "texto", "em", "negrito", "Yumi", "fim", "negrito"]
a = formateText(text)
