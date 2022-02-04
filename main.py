import json
from kivy.app import App
from docx import Document
from kivy.metrics import sp
from kivy.clock import Clock
from typing import List, Union
from kivy.config import Config
import speech_recognition as sr
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.graphics import RoundedRectangle, Color
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('kivy','window_icon','icons/logo.png')
Config.write()

r = sr.Recognizer()
m = sr.Microphone()
doc = Document()

class Manager(ScreenManager):
    pass

class BoyerMoore():
    NO_OF_CHARS = 256

    def badCharHeuristic(self, string, size) -> List[int]:
        badChar = [-1] * self.NO_OF_CHARS
        for i in range(size):
            badChar[ord(string[i])] = i

        return badChar

    def search(self, txt, pat) -> List[int]:
        occurList = []
        m = len(pat)
        n = len(txt)
        badChar = self.badCharHeuristic(pat, m)

        s = 0
        while(s <= n - m):
            j = m - 1
            while j >= 0 and pat[j] == txt[s + j]:
                j -= 1
            if j < 0:
                occurList.append(s)
                s += (m - badChar[ord(txt[s + m])] if s + m < n else 1)
            else:
                s += max(1, j - badChar[ord(txt[s + j])])

        return occurList

class DocumentBuilder():
    def title(self, newTitle) -> None:
        self.Title = newTitle
        doc.add_heading(self.Title, 0)

    def newParagraph(self, textList) -> None:
        auxList = []
        sortedlist = []
        bm = BoyerMoore()
        p = doc.add_paragraph()
        text = " ".join(textList)
        refB = [bm.search(text, "[b]"), bm.search(text, "[/b]")]
        refI = [bm.search(text, "[i]"), bm.search(text, "[/i]")]
        refU = [bm.search(text, "[u]"), bm.search(text, "[/u]")]
              
        if len(refB[0]) == len(refB[1]):
            for i in range(len(refB[0])):
                auxList.append([refB[0][i], refB[1][i], "B"])

        if len(refI[0]) == len(refI[1]):
            for i in range(len(refI[0])):
                auxList.append([refI[0][i], refI[1][i], "I"])

        if len(refU[0]) == len(refU[1]):
            for i in range(len(refU[0])):
                auxList.append([refU[0][i], refU[1][i], "U"])

        if len(auxList) <= 0:
            p.add_run(text)
        elif len(auxList) == 1:
            p.add_run(text[0:auxList[0][0]])
            runner = p.add_run(text[auxList[0][0] + 3:auxList[0][1]])
            if auxList[0][2] == "B":
                runner.bold = True
            elif auxList[0][2] == "I":
                runner.italic = True
            else:
                runner.underline = True
            p.add_run(text[auxList[0][1] + 4:])
        else:
            sortedlist = sorted(auxList, key = lambda x: x[0])

            def stylizeText(list):
                runner = p.add_run(text[list[0] + 3:list[1]])
                if list[2] == "B":
                    runner.bold = True
                elif list[2] == "I":
                    runner.italic = True
                elif list[2] == "U":
                    runner.underline = True

            for i, list in enumerate(sortedlist):
                if i + 1 == len(sortedlist):
                    p.add_run(text[sortedlist[i - 1][1] + 4:list[0]])
                    stylizeText(list)
                    p.add_run(text[list[1] + 4:])
                elif i == 0:
                    p.add_run(text[0:list[0]])
                    stylizeText(list)
                else:
                    p.add_run(text[sortedlist[i - 1][1] + 4:list[0]])
                    stylizeText(list)

    def builder(self) -> None:
        doc.add_page_break()
        doc.save(self.Title + '.docx')

class FormateText():
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

    def formate(self) -> Union[str, bool]:
        commandKeys = self.command_flags.keys()
        limit = len(self.text) - 1
        newParagraph = False

        for i, str in enumerate(self.text):
            if "vírgula" in str.lower():
                del(self.text[i])
                self.text[i - 1] += self.command_action[str]
            elif "interrogação" in str.lower():
                del(self.text[i])
                self.text[i - 1] += self.command_action[str]
            elif "novo" in str.lower() and i + 1 < limit:
                command = self.text[i + 1].lower()
                if command == "parágrafo":
                    del(self.text[i + 1])
                    del(self.text[i])
                    newParagraph = True
            elif "ativar" == str.lower() and i + 1 < limit:
                command = self.text[i + 1].lower()
                if command in commandKeys and not self.command_flags[command]:
                    del(self.text[i + 1])
                    del(self.text[i])
                    self.text[i] = self.command_action[command][0] + self.text[i]
                    self.command_flags[command] = True
            elif "desativar" == str.lower() and i + 1 < limit:
                command = self.text[i + 1].lower()
                if command in commandKeys and self.command_flags[command]:
                    del(self.text[i + 1])
                    del(self.text[i])
                    self.text[i - 1] += self.command_action[command][1]
                    self.command_flags[command] = False

        return([" ".join(self.text), newParagraph])

class Menu(Screen):
    def on_pre_enter(self) -> None:
        Window.bind(on_request_close=self.confirm_exit)

    def confirm_exit(self, *args, **kwargs) -> bool:
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup = Popup(
            title="Deseja realmente sair?", 
            content=box,
            size_hint=(None, None),
            size=(sp(150), sp(100))
        )
        buttons = BoxLayout(padding=sp(5), spacing=sp(10))
        exitButton = RoundButton(text="Sim", on_release=App.get_running_app().stop)
        closeButton = RoundButton(text="Não", on_release=popup.dismiss)

        buttons.add_widget(exitButton)
        buttons.add_widget(closeButton)
        box.add_widget(Image(source="icons/warning.png"))
        box.add_widget(buttons)
          
        animation = Animation(size=(sp(300), sp(200)), duration=0.3, t="out_back")
        animation.start(popup)
        popup.open()

        return True

class RoundButton(ButtonBehavior, Label):
    cor = ListProperty([0.1, 0.5, 0.8,1])
    cor2 = ListProperty([0.3,0.1,0.9,1])

    def __init__(self,**kwargs) -> None:
        super(RoundButton,self).__init__(**kwargs)
        self.update()

    def on_pos(self, *args) -> None:
        self.update()

    def on_size(self, *args) -> None:
        self.update()

    def on_press(self, *args) -> None:
        self.cor, self.cor2 = self.cor2, self.cor

    def on_release(self, *args) -> None:
        self.cor, self.cor2 = self.cor2, self.cor

    def on_cor(self, *args) -> None:
        self.update()

    def update(self, *args) -> None:
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.cor)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

class TextBoxContainer(Screen):
    pheases = [[]]
    path = ''

    def on_pre_enter(self, *args)  -> None:
        super().on_pre_enter(*args)
        self.ids.textBox.clear_widgets()
        self.path = App.get_running_app().user_data_dir + "/"
        self.readData()
        Window.bind(on_keyboard=self.comeBack)
        for phease in self.pheases:
            self.ids.textBox.add_widget(LabelBox(text=" ".join(phease)))

    def comeBack(self, window, key, *args) -> None:
        if key == 27:
            App.get_running_app().root.current = "menu"
            return True

    def on_pre_leave(self, *args) -> None:
        super().on_pre_leave(*args)
        Window.unbind(on_keyboard=self.comeBack)

    def readData(self, *args) -> None:
        try:
            with open(self.path + "data.json", "r") as data:
                self.pheases = json.load(data)
        except FileNotFoundError:
            print("Arquivo não encontrado no caminho: {}".format(self.path))


    def saveData(self) -> None:
        with open(self.path + "data.json", "w") as data:
            json.dump(self.pheases, data)
    
    def docxBuilder(self, *args) -> None:
        document = DocumentBuilder()
        document.title("Teste")
        document.newParagraph(self.pheases[0])
        # for textList in self.pheases:      
        #     document.newParagraph(textList)
        document.builder()

    def docPopup(self, *args, **kwargs) -> bool:
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup = Popup(
            title="Nome do documento", 
            content=box,
            size_hint=(None, None),
            size=(sp(180), sp(150))
        )
        userInput = TextInput(text="")
        buttons = BoxLayout(padding=sp(5), spacing=sp(10))
        exitButton = RoundButton(text="Exportar", on_release=self.docxBuilder)

        buttons.add_widget(exitButton)
        box.add_widget(userInput)
        box.add_widget(buttons)
          
        animation = Animation(size=(sp(300), sp(200)), duration=0.3, t="out_back")
        animation.start(popup)
        popup.open()

        return True

    def messageError(self, msg, *args) -> bool:
        self.ids.image_mic.source = "icons/mic.png"
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup = Popup(
            title="Ops, ocorreu um erro!", 
            content=box,
            size_hint=(None, None),
            size=(sp(150), sp(150))
        )

        labelMsg = Label(text=msg, bold=True, font_size='16sp')
        box.add_widget(Image(source="icons/logo.png"))
        box.add_widget(labelMsg)
        animation = Animation(size=(sp(330), sp(200)), duration=0.3, t="out_back")
        animation.start(popup)

        popup.open()
        return True

    def message(self, msg, *args) -> None:
        phease, newParagraph = FormateText(msg.split()).formate()
        self.ids.image_mic.source = "icons/mic.png"
        textBoxTree = self.ids.textBox.children
        pheasesLen = len(self.pheases)

        if newParagraph:
            self.ids.textBox.add_widget(LabelBox(text=phease))
            self.pheases.append([phease])
        elif len(textBoxTree) > 0:
            self.ids.textBox.children[0].text += " " + phease
            self.pheases[pheasesLen - 1].append(phease)
        else:
            self.ids.textBox.add_widget(LabelBox(text=phease))
            self.pheases[pheasesLen - 1].append(phease)

        # self.saveData()

        # print("Lista de frases:\n",self.pheases)
        # print("frase antes das mudanças:\n", msg)
        # print("frase pré-processada:\n", phease)

    def listen(self, *args) -> None:
        with m as source:
            audio = r.listen(source)
        
        try:
            # Reconhecendo com API do google
            value = r.recognize_google(audio, language='pt-BR')
            self.message(value)
        
        except sr.UnknownValueError:
            self.messageError("Não entendi o que você falou.")
        
        except sr.RequestError as e:
            self.messageError("Não consigo conectar ao servidor :(")
            print("ERROR ====> {0}".format(e))
    
    def initRecorder(self, *args) -> None:
        self.ids.image_mic.source = "icons/mic_active.png"
        # Atrasa a execução da método listen() em 0.3 segundos
        Clock.schedule_once(self.listen, 0.3)

class Instructions(Screen):
    def on_pre_enter(self, *args) -> None:
        super().on_pre_enter(*args)
        self.ids.textBoxIntructions.clear_widgets()

        title = "Introdução"
        subTitle = "Comandos"

        introduction = ("Para que o reconhecimento de fala funcione"
        " corretamente, é muito importante que você esteja em um lugar"
        " com pouco barulho. Além disso, verifique nas configurações" 
        " de seu microfone se o volume está muito alto (volume muito"
        " alto pode ser prejudicial, pois faz o microfone capturar muitos"
        " ruídos e portanto, dificulta o sistema de reconhecimento).")

        bold = ("[b]Negrito:[/b]\n\nPara ativar o negrito basta dizer"
        " [b]\"ativar negrito\"[/b] que tudo o que for dito em seguida"
        " ficará em negrito. Para desativá-lo basta dizer " 
        "[b]\"desativar negrito\"[/b] e continuar falando normalmente.")

        italic = ("[b]Itálico:[/b]\n\nPara ativar o itálico basta dizer"
        " [b]\"ativar itálico\"[/b] que tudo o que for dito em seguida"
        " ficará em itálico. Para desativá-lo basta dizer " 
        "[b]\"desativar itálico\"[/b] e continuar falando normalmente.")

        underline = ("[b]Sublinhado:[/b]\n\nPara ativar o sublinhado basta dizer"
        " [b]\"ativar sublinhado\"[/b] que tudo o que for dito em seguida"
        " ficará em sublinhado. Para desativá-lo basta dizer " 
        "[b]\"desativar sublinhado\"[/b] e continuar falando normalmente.")

        paragraph = ("[b]Novo parágrafo:[/b]\n\nPara adicionar um novo parágrafo"
        " basta dizer [b]\"novo parágrafo\"[/b] e continuar falando o seu texto.")

        self.ids.textBoxIntructions.add_widget(LabelBox(
            text=title,
            underline = True,
            font_name='Roboto-Bold',
            font_size = 20,
            color = [0.4, 0.4, 0.4, 1],
            halign= 'center'
        ))
        self.ids.textBoxIntructions.add_widget(LabelBox(text=introduction, halign='justify'))
        self.ids.textBoxIntructions.add_widget(LabelBox(
            text=subTitle,
            underline = True,
            font_name='Roboto-Bold',
            font_size = 20,
            color = [0.4, 0.4, 0.4, 1],
            halign= 'center'
        ))
        self.ids.textBoxIntructions.add_widget(LabelBox(text=bold, halign='justify'))
        self.ids.textBoxIntructions.add_widget(LabelBox(text=italic, halign='justify'))
        self.ids.textBoxIntructions.add_widget(LabelBox(text=underline, halign='justify'))
        self.ids.textBoxIntructions.add_widget(LabelBox(text=paragraph, halign='justify'))

class LabelBox(Label):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def on_size(self, *args) -> None:
        if self.width > 1024:
            self.text_size = (self.width / 1.6, None)
        else:
            self.text_size = (self.width - sp(50), None)

    def on_texture_size(self, *args) -> None:
        self.size = self.texture_size
        self.height += sp(20)

class Yumi(App):
    def build(self):
        with m as source:
            # Ajusta o ruído
            r.adjust_for_ambient_noise(source)
            print("Definindo limite mínimo de percepção para {}".format(r.energy_threshold))
        return Manager()

if __name__ == '__main__':
    Yumi().run()
