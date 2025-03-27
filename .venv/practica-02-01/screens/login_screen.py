# screens/login_screen.py
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.app import MDApp


class LoginScreen(Screen):
    """Экран авторизации"""

    def try_login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return

        app = MDApp.get_running_app()
        if app.db.check_user(username, password):
            app.root.current = 'main'
            app.root.transition.direction = 'left'
        else:
            self.show_error("Неверный логин или пароль")

    def show_error(self, message):
        self.ids.error_label.text = message
        self.ids.error_label.opacity = 1

        # Скрыть ошибку через 3 секунды
        Clock.schedule_once(lambda dt: setattr(self.ids.error_label, 'opacity', 0), 3)