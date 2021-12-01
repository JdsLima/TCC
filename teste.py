
class formateText():
    def __init__(self, text) -> None:
        self.text = text

    command_flags = dict(
        negrito = False, 
        itálico = False, 
        sublinhado = False
    )

    command_action = dict(
        negrito = ["[b]", "[/b]"],
        itálico = ["[i]", "[/i]"],
        sublinhado = ["[u]", "[/u]"],
        vírgula = ",",
        interrogação = "?"
    )

    def formate(self):
        commandKeys = self.command_flags.keys()
        limit = len(self.text) - 1

        for i, str in enumerate(self.text):
            if "ativar" == str.lower() and i + 1 < limit:
                command = self.text[i + 1].lower()
                if command in commandKeys and not self.command_flags[command]:
                    del(self.text[i])
                    self.text[i] = self.command_action.get(command)[0]
                    self.command_flags[command] = True

            elif "desativar" == str.lower() and i + 1 < limit:
                command = self.text[i + 1].lower()
                if command in commandKeys and self.command_flags[command]:
                    del(self.text[i])
                    self.text[i] = self.command_action.get(command)[1]
                    self.command_flags[command] = False

            elif "vírgula" in str:
                del(self.text[i])
                self.text[i - 1] += self.command_action[str]

            elif "interrogação" in str:
                del(self.text[i])
                self.text[i - 1] += self.command_action[str]

        return(" ".join(self.text))
    
text = ["ativar", "negrito", "testando", "texto", "em", "negrito", "desativar", "negrito"]
a = formateText(text).formate()
print(a)
