# modules/utils_module.py
import os
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker


class UtilsModule:
    """Модуль вспомогательных компонентов"""

    def __init__(self):
        self.notes = {}
        self.current_note = ""

    def save_note(self, note_text, key="default"):
        """Сохранение заметки"""
        try:
            self.notes[key] = note_text
            # Можно также сохранять в файл
            with open(f"note_{key}.txt", 'w', encoding='utf-8') as f:
                f.write(note_text)
            return True, "Заметка сохранена"
        except Exception as e:
            return False, f"Ошибка сохранения: {str(e)}"

    def load_note(self, key="default"):
        """Загрузка заметки"""
        try:
            if key in self.notes:
                return True, self.notes[key]

            # Попытка загрузки из файла
            if os.path.exists(f"note_{key}.txt"):
                with open(f"note_{key}.txt", 'r', encoding='utf-8') as f:
                    note = f.read()
                    self.notes[key] = note
                return True, note
            return True, ""
        except Exception as e:
            return False, f"Ошибка загрузки: {str(e)}"

    def get_date_picker(self, callback):
        """Создание и отображение календаря"""
        date_dialog = MDDatePicker(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        date_dialog.bind(on_save=callback)
        return date_dialog