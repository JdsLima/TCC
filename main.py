import json
from kivy.app import App
from kivy.metrics import sp
from kivy.clock import Clock
from kivy.config import Config
import speech_recognition as sr
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen

# Config.set('graphics', 'width', '600')
# Config.set('graphics', 'height', '400')
Config.set('kivy','window_icon','icons/logo.png')

r = sr.Recognizer()
m = sr.Microphone()

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
        sublinhado = ["[u]", "[/u]"]
    )

    def formate(self):
        commandKeys = self.command_flags.keys()

        for i, str in enumerate(self.text):
            if "Yumi" in str and i + 1 < (len(self.text) - 1):
                command = self.text[i + 1]
                if command in commandKeys:
                    del(self.text[i])
                    self.text[i] = self.command_action.get(self.text[i])[0]
                    self.command_flags[command] = True

                elif command == "fim":
                    command = self.text[i + 2]
                    if command in commandKeys and self.command_flags[command]:
                        del(self.text[i + 1])
                        del(self.text[i])
                        self.text[i] = self.command_action.get(self.text[i])[1]
                        self.command_flags[command] = False

        return(" ".join(self.text))

class Manager(ScreenManager):
    pass

class Menu(Screen):
    def on_pre_enter(self):
        Window.bind(on_request_close=self.confirm_exit)

    def confirm_exit(self, *args, **kwargs):
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

    def __init__(self,**kwargs):
        super(RoundButton,self).__init__(**kwargs)
        self.update()

    def on_pos(self, *args):
        self.update()

    def on_size(self, *args):
        self.update()

    def on_press(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

    def on_release(self, *args):
        self.cor, self.cor2 = self.cor2, self.cor

    def on_cor(self, *args):
        self.update()

    def update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.cor)
            Ellipse(
                size=(self.height, self.height), 
                pos=self.pos
            )
            Ellipse(
                size=(self.height, self.height),
                pos=(self.x + self.width - self.height, self.y)
            )
            Rectangle(
                size=(self.width-self.height,self.height),
                pos=(self.x + self.height/2.0, self.y)
            )

class TextBoxContainer(Screen):
    pheases = []
    path = ''

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.ids.textBox.clear_widgets()
        self.path = App.get_running_app().user_data_dir + "/"
        self.readData()
        Window.bind(on_keyboard=self.comeBack)
        for phease in self.pheases:
            self.ids.textBox.add_widget(LabelBox(text=phease))

    def comeBack(self, window, key, *args):
        if key == 27:
            App.get_running_app().root.current = "menu"
            return True

    def on_pre_leave(self, *args):
        super().on_pre_leave(*args)
        Window.unbind(on_keyboard=self.comeBack)

    def readData(self, *args):
        try:
            with open(self.path + "data.json", "r") as data:
                self.pheases = json.load(data)
        except FileNotFoundError:
            print("Arquivo não encontrado no caminho: {}".format(self.path))


    def saveData(self):
        with open(self.path + "data.json", "w") as data:
            json.dump(self.pheases, data)

    def messageError(self, msg, *args):
        self.ids.mic.text = "Iniciar"
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        popup = Popup(
            title="Ops, ocorreu um erro!", 
            content=box,
            size_hint=(None, None),
            size=(sp(150), sp(150))
        )

        labelMsg = Label(
            text="[b]" + msg + "[/b]", 
            font_size='16sp', 
            markup = True
        )
        box.add_widget(Image(source="icons/logo.png"))
        box.add_widget(labelMsg)
        animation = Animation(size=(sp(330), sp(200)), duration=0.3, t="out_back")
        animation.start(popup)

        popup.open()
        return True

    def message(self, msg, *args):
        phease = formateText(msg.split()).formate()
        
        self.ids.mic.text = "Iniciar"
        self.ids.textBox.add_widget(LabelBox(text=phease))
        self.pheases.append(phease)
        # self.saveData()

    def listen(self, *args):
        with m as source:
            audio = r.listen(source)
        
        try:
            # Gravando com API do google
            value = r.recognize_google(audio, language='pt-BR')
            self.message(value)
        
        except sr.UnknownValueError:
            self.messageError("Não entendi o que você falou.")
        
        except sr.RequestError as e:
            self.messageError("Não consigo conectar ao servidor :(")
            print("ERROR ====> {0}".format(e))
    
    def initRecorder(self, *args):
        self.ids.mic.text = "Escutando..."
        # Atrasa a execução da método listen() em 0.5 segundos
        Clock.schedule_once(self.listen, 0.5)

    def removeWidget(self, phrase):
        text = phrase.ids.label.text
        self.ids.textBox.remove_widget(phrase)
        self.phease.remove(text)
        self.saveData()

class Instructions(Screen):
    pass


class LabelBox(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_size(self, *args):
        if self.width > 1024:
            self.text_size = (self.width / 2, None)
        else:
            self.text_size = (self.width - sp(50), None)

    def on_texture_size(self, *args):
        self.size = self.texture_size
        self.height += sp(20)

class speech(App):
    def build(self):
        with m as source:
            # Ajusta o ruído
            r.adjust_for_ambient_noise(source)
            print("Definindo limite mínimo de percepção para {}".format(r.energy_threshold))
        return Manager()

if __name__ == '__main__':
    speech().run()
