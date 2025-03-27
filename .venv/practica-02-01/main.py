import os
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

from database import DatabaseController
from screens import LoginScreen, MainScreen
from screens.tab_classes import TabAbonents, TabTariffs, TabConnections, TabPayments

Window.size = (1300, 750)
Window.minimum_width = 1100
Window.minimum_height = 650
Window.maximize()

Builder.load_file(os.path.join('kv', 'login.kv'))
Builder.load_file(os.path.join('kv', 'main.kv'))
Builder.load_file(os.path.join('kv', 'dialogs.kv'))
Builder.load_file(os.path.join('kv', 'styles.kv'))


class AbonentApp(MDApp):
    """Главный класс приложения"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseController()
        self.title = "СУАИ-У - Система учета абонентов интернет-услуг - Ростелеком"

        # Настройка темы в цветах Ростелеком
        self.theme_cls.theme_style = "Dark"  # Темная тема
        self.theme_cls.primary_palette = "Indigo"  # Фиолетово-синий
        self.theme_cls.accent_palette = "Orange"  # Оранжевый акцент
        self.theme_cls.primary_hue = "700"  # Насыщенность основного цвета
        self.theme_cls.accent_hue = "500"  # Насыщенность акцента
        self.theme_cls.material_style = "M3"  # Современный Material Design 3

    def build(self):
        from kivy.uix.screenmanager import ScreenManager
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    AbonentApp().run()