import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from modules import FileIntegrationModule, SearchModule, UtilsModule


class MainScreen(Screen):
    """Главный экран с вкладками"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_table = 'абоненты'
        self.utils = UtilsModule()
        self.search_criteria = {}
        self.current_dialog = None
        self.current_edit_id = None
        self.dialog_fields = {}
        self.selected_record = None
        self.menu = None
        self.data_table_widget = None

        self.selected_status = 'Активен'
        self.selected_abonent_id = None
        self.selected_tariff_id = None
        self.selected_payment_abonent_id = None

        self.abonent_button = None
        self.tariff_button = None
        self.payment_abonent_button = None
        self.status_active = None
        self.status_paused = None
        self.status_blocked = None

    def on_enter(self):
        """Вызывается при входе на экран"""
        try:
            self.load_table_data('абоненты')
            # Проверяем наличие метода load_notes перед вызовом
            if hasattr(self, 'load_notes'):
                self.load_notes()
            else:
                print("Предупреждение: метод load_notes не найден")
        except Exception as e:
            print(f"Ошибка в on_enter: {e}")

    def show_edit_selected_dialog(self):
        """Показать диалог редактирования выбранной записи"""
        if not self.selected_record:
            self.show_message("Внимание", "Выберите запись для редактирования")
            return

        self.show_edit_dialog(self.current_table, self.selected_record)

    def on_tab_switch(self, instance_tabs, instance_tab_bar, instance_tab):
        """Обработчик переключения вкладок"""
        # Получаем текст выбранной вкладки
        tab_text = instance_tab.text.lower()

        # Загружаем данные для выбранной таблицы
        self.load_table_data(tab_text)

        # Сбрасываем выбранную запись при переключении таблицы
        self.selected_record = None

    def show_date_picker(self, target_field):
        """Показать календарь для выбора даты"""

        def on_save(instance, value, date_range):
            if target_field in self.dialog_fields:
                self.dialog_fields[target_field].text = value.strftime('%Y-%m-%d')

        date_picker = self.utils.get_date_picker(on_save)
        date_picker.open()

    def load_table_data(self, table_name):
        """Загрузка данных для текущей таблицы"""
        self.current_table = table_name
        self.update_table_label(table_name)  # Добавляем обновление метки

        app = MDApp.get_running_app()

        if table_name == 'абоненты':
            data = app.db.get_all_abonents()
            self.display_abonents(data)
        elif table_name == 'тарифы':
            data = app.db.get_all_tariffs()
            self.display_tariffs(data)
        elif table_name == 'подключения':
            data = app.db.get_all_connections()
            self.display_connections(data)
        elif table_name == 'платежи':
            data = app.db.get_all_payments()
            self.display_payments(data)

    def update_table_label(self, table_name):
        """Обновить метку с названием текущей таблицы"""
        if hasattr(self.ids, 'current_table_label'):
            self.ids.current_table_label.text = f'Текущая таблица: {table_name.capitalize()}'

    def display_abonents(self, data):
        """Отображение таблицы абонентов с помощью MDDataTable"""
        # Очищаем контейнер
        container = self.ids.data_table_container
        container.clear_widgets()

        if not data:
            # Если нет данных, показываем сообщение
            label = MDLabel(
                text="Нет данных",
                theme_text_color="Custom",
                text_color=[0.7, 0.7, 0.7, 1],
                halign="center",
                valign="center"
            )
            container.add_widget(label)
            return

        # Подготавливаем данные для таблицы
        table_data = []
        for item in data:
            row = (
                str(item['id']),
                item['fio'],
                item['phone'],
                item['email'],
                item['address'],
                item['reg_date']
            )
            table_data.append(row)

        # Создаем таблицу
        self.data_table_widget = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(30)),
                ("ФИО", dp(40)),
                ("Телефон", dp(30)),
                ("Email", dp(40)),
                ("Адрес", dp(50)),
                ("Дата рег.", dp(30))
            ],
            row_data=table_data,
            sorted_on="ID",
            sorted_order="ASC",
            background_color=[0.12, 0.12, 0.18, 1],
            background_color_header=[0.15, 0.1, 0.25, 1],
            background_color_selected_cell=[0.5, 0.3, 0.8, 0.5],
        )

        # Привязываем событие выбора строки
        self.data_table_widget.bind(on_row_press=self.on_row_press)

        # Добавляем таблицу в контейнер
        container.add_widget(self.data_table_widget)

    def display_tariffs(self, data):
        """Отображение таблицы тарифов с помощью MDDataTable"""
        container = self.ids.data_table_container
        container.clear_widgets()

        if not data:
            label = MDLabel(
                text="Нет данных",
                theme_text_color="Custom",
                text_color=[0.7, 0.7, 0.7, 1],
                halign="center",
                valign="center"
            )
            container.add_widget(label)
            return

        table_data = []
        for item in data:
            row = (
                str(item['id']),
                item['name'],
                item['speed'],
                f"{item['price']} руб.",
                item['description'][:30] + "..." if len(item['description']) > 30 else item['description']
            )
            table_data.append(row)

        self.data_table_widget = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(20)),
                ("Название", dp(40)),
                ("Скорость", dp(30)),
                ("Цена", dp(25)),
                ("Описание", dp(50))
            ],
            row_data=table_data,
            background_color=[0.12, 0.12, 0.18, 1],
            background_color_header=[0.15, 0.1, 0.25, 1],
            background_color_selected_cell=[0.5, 0.3, 0.8, 0.5],
        )

        self.data_table_widget.bind(on_row_press=self.on_row_press)
        container.add_widget(self.data_table_widget)

    def display_connections(self, data):
        """Отображение таблицы подключений с помощью MDDataTable"""
        container = self.ids.data_table_container
        container.clear_widgets()

        if not data:
            label = MDLabel(
                text="Нет данных",
                theme_text_color="Custom",
                text_color=[0.7, 0.7, 0.7, 1],
                halign="center",
                valign="center"
            )
            container.add_widget(label)
            return

        table_data = []
        for item in data:
            row = (
                str(item['id']),
                item['abonent_name'],
                item['tariff_name'],
                item['conn_date'],
                item['status']
            )
            table_data.append(row)

        self.data_table_widget = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(20)),
                ("Абонент", dp(50)),
                ("Тариф", dp(40)),
                ("Дата", dp(30)),
                ("Статус", dp(25))
            ],
            row_data=table_data,
            background_color=[0.12, 0.12, 0.18, 1],
            background_color_header=[0.15, 0.1, 0.25, 1],
            background_color_selected_cell=[0.5, 0.3, 0.8, 0.5],
        )

        self.data_table_widget.bind(on_row_press=self.on_row_press)
        container.add_widget(self.data_table_widget)

    def display_payments(self, data):
        """Отображение таблицы платежей с помощью MDDataTable"""
        container = self.ids.data_table_container
        container.clear_widgets()

        if not data:
            label = MDLabel(
                text="Нет данных",
                theme_text_color="Custom",
                text_color=[0.7, 0.7, 0.7, 1],
                halign="center",
                valign="center"
            )
            container.add_widget(label)
            return

        table_data = []
        for item in data:
            row = (
                str(item['id']),
                item['abonent_name'],
                f"{item['amount']} руб.",
                item['pay_date']
            )
            table_data.append(row)

        self.data_table_widget = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(20)),
                ("Абонент", dp(60)),
                ("Сумма", dp(30)),
                ("Дата", dp(30))
            ],
            row_data=table_data,
            background_color=[0.12, 0.12, 0.18, 1],
            background_color_header=[0.15, 0.1, 0.25, 1],
            background_color_selected_cell=[0.5, 0.3, 0.8, 0.5],
        )

        self.data_table_widget.bind(on_row_press=self.on_row_press)
        container.add_widget(self.data_table_widget)

    def on_row_press(self, instance_table, instance_row):
        """Обработчик нажатия на строку таблицы"""
        # Получаем индекс выбранной строки
        row_num = instance_row.index // len(instance_table.column_data)

        # Получаем ID из первой колонки
        if row_num < len(instance_table.row_data):
            row_id = instance_table.row_data[row_num][0]

            # Ищем запись с этим ID
            app = MDApp.get_running_app()
            if self.current_table == 'абоненты':
                data = app.db.get_all_abonents()
            elif self.current_table == 'тарифы':
                data = app.db.get_all_tariffs()
            elif self.current_table == 'подключения':
                data = app.db.get_all_connections()
            elif self.current_table == 'платежи':
                data = app.db.get_all_payments()
            else:
                data = []

            for item in data:
                if str(item['id']) == row_id:
                    self.select_record(item)
                    break

    def select_record(self, record):
        """Выбор записи для редактирования или удаления"""
        self.selected_record = record
        # Визуально выделяем выбранную запись в таблице (опционально)
        self.show_edit_dialog(self.current_table, record)

    def show_add_dialog(self, table_name):
        """Показать диалог добавления записи"""
        self.current_edit_id = None
        dialog = self.create_edit_dialog(table_name, None)
        if dialog:
            self.current_dialog = dialog
            self.current_dialog.open()

    def show_edit_dialog(self, table_name, record):
        """Показать диалог редактирования записи"""
        if record:
            self.current_edit_id = record['id']
            dialog = self.create_edit_dialog(table_name, record)
            if dialog:
                self.current_dialog = dialog
                self.current_dialog.open()

    def create_edit_dialog(self, table_name, record):
        """Создание диалога для добавления/редактирования"""
        if table_name == 'абоненты':
            return self.create_abonent_dialog(record)
        elif table_name == 'тарифы':
            return self.create_tariff_dialog(record)
        elif table_name == 'подключения':
            return self.create_connection_dialog(record)
        elif table_name == 'платежи':
            return self.create_payment_dialog(record)
        return None

    # ==================== ДИАЛОГИ ДЛЯ АБОНЕНТОВ ====================

    def create_abonent_dialog(self, record):
        """Диалог для абонента"""
        title = "Добавление абонента" if not record else "Редактирование абонента"

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=self.create_abonent_form(record),
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    md_bg_color=[1, 0.65, 0, 1],  # Оранжевый
                    text_color=[0, 0, 0, 1],
                    on_release=self.save_abonent
                )
            ]
        )
        return dialog

    def create_abonent_form(self, record):
        """Создание формы для абонента"""
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Поля формы
        fields = [
            {'hint': 'ФИО', 'text': record['fio'] if record else '', 'required': True},
            {'hint': 'Адрес', 'text': record['address'] if record else '', 'required': True},
            {'hint': 'Телефон', 'text': record['phone'] if record else '', 'required': True},
            {'hint': 'Email', 'text': record['email'] if record else '', 'required': True},
            {'hint': 'Дата регистрации (ГГГГ-ММ-ДД)',
             'text': record['reg_date'] if record else datetime.now().strftime('%Y-%m-%d'), 'required': True}
        ]

        self.dialog_fields = {}
        for field in fields:
            tf = MDTextField(
                hint_text=field['hint'],
                text=field['text'],
                required=field['required'],
                size_hint_y=None,
                height=dp(48)
            )
            form.add_widget(tf)
            self.dialog_fields[field['hint']] = tf

        # Кнопка для выбора даты из календаря
        date_btn = MDRaisedButton(
            text="Выбрать дату",
            size_hint_y=None,
            height=dp(40),
            on_release=lambda x: self.show_date_picker('Дата регистрации (ГГГГ-ММ-ДД)')
        )
        form.add_widget(date_btn)

        return form

    def save_abonent(self, *args):
        """Сохранение абонента"""
        app = MDApp.get_running_app()

        # Получение данных из формы
        fio = self.dialog_fields['ФИО'].text.strip()
        address = self.dialog_fields['Адрес'].text.strip()
        phone = self.dialog_fields['Телефон'].text.strip()
        email = self.dialog_fields['Email'].text.strip()
        reg_date = self.dialog_fields['Дата регистрации (ГГГГ-ММ-ДД)'].text.strip()

        # Валидация
        errors = []
        if not fio:
            errors.append("ФИО обязательно")
        if not address:
            errors.append("Адрес обязателен")
        if not phone or not any(c.isdigit() for c in phone):
            errors.append("Телефон должен содержать цифры")
        if not email or '@' not in email:
            errors.append("Email должен содержать символ @")

        if errors:
            self.show_message("Ошибка валидации", "\n".join(errors))
            return

        try:
            if self.current_edit_id:
                # Обновление
                app.db.update_abonent(self.current_edit_id, fio, address, phone, email, reg_date)
                self.show_message("Успех", "Абонент обновлен")
            else:
                # Добавление
                app.db.add_abonent(fio, address, phone, email, reg_date)
                self.show_message("Успех", "Абонент добавлен")

            # Закрыть диалог
            if self.current_dialog:
                self.current_dialog.dismiss()

            self.load_table_data('абоненты')

        except Exception as e:
            self.show_message("Ошибка", str(e))

    # ==================== ДИАЛОГИ ДЛЯ ТАРИФОВ ====================

    def create_tariff_dialog(self, record):
        """Диалог для тарифа"""
        title = "Добавление тарифа" if not record else "Редактирование тарифа"

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=self.create_tariff_form(record),
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    md_bg_color=[0.5, 0.3, 0.8, 1],  # Фиолетовый
                    text_color=[1, 1, 1, 1],
                    on_release=self.save_tariff
                )
            ]
        )
        return dialog

    def create_tariff_form(self, record):
        """Создание формы для тарифа"""
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Поля формы
        fields = [
            {'hint': 'Название', 'text': record['name'] if record else '', 'required': True},
            {'hint': 'Скорость (Мбит/с)', 'text': record['speed'] if record else '', 'required': True},
            {'hint': 'Цена (руб)', 'text': str(record['price']) if record else '', 'required': True},
            {'hint': 'Описание', 'text': record['description'] if record else '', 'required': False}
        ]

        self.dialog_fields = {}
        for field in fields:
            tf = MDTextField(
                hint_text=field['hint'],
                text=field['text'],
                required=field['required'],
                size_hint_y=None,
                height=dp(48)
            )
            form.add_widget(tf)
            self.dialog_fields[field['hint']] = tf

        return form

    def save_tariff(self, *args):
        """Сохранение тарифа"""
        app = MDApp.get_running_app()

        # Получение данных из формы
        name = self.dialog_fields['Название'].text.strip()
        speed = self.dialog_fields['Скорость (Мбит/с)'].text.strip()
        price_text = self.dialog_fields['Цена (руб)'].text.strip()
        description = self.dialog_fields['Описание'].text.strip()

        # Валидация
        errors = []
        if not name:
            errors.append("Название обязательно")
        if not speed:
            errors.append("Скорость обязательна")
        if not price_text:
            errors.append("Цена обязательна")
        else:
            try:
                price = float(price_text)
                if price <= 0:
                    errors.append("Цена должна быть положительной")
            except ValueError:
                errors.append("Цена должна быть числом")

        if errors:
            self.show_message("Ошибка валидации", "\n".join(errors))
            return

        try:
            if self.current_edit_id:
                # Обновление
                app.db.update_tariff(self.current_edit_id, name, speed, float(price_text), description)
                self.show_message("Успех", "Тариф обновлен")
            else:
                # Добавление
                app.db.add_tariff(name, speed, float(price_text), description)
                self.show_message("Успех", "Тариф добавлен")

            # Закрыть диалог
            if self.current_dialog:
                self.current_dialog.dismiss()

            self.load_table_data('тарифы')

        except Exception as e:
            self.show_message("Ошибка", str(e))

    # ==================== ДИАЛОГИ ДЛЯ ПОДКЛЮЧЕНИЙ ====================

    def create_connection_dialog(self, record):
        """Диалог для подключения"""
        title = "Добавление подключения" if not record else "Редактирование подключения"

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=self.create_connection_form(record),
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    md_bg_color=[0.5, 0.3, 0.8, 1],  # Фиолетовый
                    text_color=[1, 1, 1, 1],
                    on_release=self.save_connection
                )
            ]
        )
        return dialog

    def select_status(self, status, active_btn, paused_btn, blocked_btn):
        """Выбор статуса подключения с подсветкой"""
        self.selected_status = status

        # Обновляем цвета кнопок
        active_btn.md_bg_color = [0.3, 0.8, 0.3, 1] if status == 'Активен' else [0.5, 0.5, 0.5, 0.5]
        paused_btn.md_bg_color = [0.8, 0.6, 0.1, 1] if status == 'Приостановлен' else [0.5, 0.5, 0.5, 0.5]
        blocked_btn.md_bg_color = [0.8, 0.2, 0.2, 1] if status == 'Заблокирован' else [0.5, 0.5, 0.5, 0.5]

    def create_connection_form(self, record):
        """Создание формы для подключения с выпадающими списками (ComboBox)"""
        form = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        form.bind(minimum_height=form.setter('height'))

        app = MDApp.get_running_app()
        abonents = app.db.get_abonents_list()
        tariffs = app.db.get_tariffs_list()

        # Поля формы
        self.dialog_fields = {}

        # ===== ВЫБОР АБОНЕНТА (COMBOBOX) =====
        abonent_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))

        abonent_label = MDLabel(
            text='Абонент:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        abonent_layout.add_widget(abonent_label)

        # Кнопка для выбора абонента (вместо текстового поля)
        current_abonent_text = record['abonent_name'] if record and 'abonent_name' in record else 'Выберите абонента'
        self.abonent_button = MDRaisedButton(
            text=current_abonent_text,
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.2, 0.2, 0.25, 1],
            text_color=[1, 1, 1, 1],
            on_release=self.open_abonent_menu
        )
        abonent_layout.add_widget(self.abonent_button)
        form.add_widget(abonent_layout)

        # Создаем элементы меню для абонентов
        self.abonent_menu_items = []
        for a in abonents:
            menu_item = {
                "text": f"{a['fio']}",
                "secondary_text": f"ID: {a['id']}",
                "viewclass": "TwoLineListItem",
                "height": dp(60),
                "on_release": lambda x=f"{a['fio']}", id=a['id']: self.set_abonent(x, id)
            }
            self.abonent_menu_items.append(menu_item)

        self.selected_abonent_id = record['abonent_id'] if record else None
        self.selected_abonent_name = record['abonent_name'] if record and 'abonent_name' in record else None

        # ===== ВЫБОР ТАРИФА (COMBOBOX) =====
        tariff_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))

        tariff_label = MDLabel(
            text='Тариф:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        tariff_layout.add_widget(tariff_label)

        # Кнопка для выбора тарифа (вместо текстового поля)
        current_tariff_text = record['tariff_name'] if record and 'tariff_name' in record else 'Выберите тариф'
        self.tariff_button = MDRaisedButton(
            text=current_tariff_text,
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.2, 0.2, 0.25, 1],
            text_color=[1, 1, 1, 1],
            on_release=self.open_tariff_menu
        )
        tariff_layout.add_widget(self.tariff_button)
        form.add_widget(tariff_layout)

        # Создаем элементы меню для тарифов
        self.tariff_menu_items = []
        for t in tariffs:
            name = t.get('name', '')
            price = t.get('price', 0)
            speed = t.get('speed', '')

            menu_item = {
                "text": f"{name}",
                "secondary_text": f"{price} руб. - {speed}",
                "viewclass": "TwoLineListItem",
                "height": dp(60),
                "on_release": lambda x=f"{name}", id=t['id'], price=price, speed=speed: self.set_tariff(x, id, price,
                                                                                                        speed)
            }
            self.tariff_menu_items.append(menu_item)

        self.selected_tariff_id = record['tariff_id'] if record else None
        self.selected_tariff_name = record['tariff_name'] if record and 'tariff_name' in record else None

        # ===== ДАТА ПОДКЛЮЧЕНИЯ =====
        date_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110))

        date_label = MDLabel(
            text='Дата подключения:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        date_layout.add_widget(date_label)

        date_text = record['conn_date'] if record else datetime.now().strftime('%Y-%m-%d')
        date_field = MDTextField(
            hint_text='ГГГГ-ММ-ДД',
            text=date_text,
            mode="fill",
            fill_color=[0.2, 0.2, 0.25, 1],
            size_hint_y=None,
            height=dp(50)
        )
        date_layout.add_widget(date_field)
        self.dialog_fields['Дата подключения'] = date_field

        # Кнопка для выбора даты из календаря
        date_btn = MDRaisedButton(
            text="Выбрать дату",
            size_hint_y=None,
            height=dp(40),
            md_bg_color=[0.5, 0.3, 0.8, 1],
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.show_date_picker('Дата подключения')
        )
        date_layout.add_widget(date_btn)
        form.add_widget(date_layout)

        # ===== СТАТУС ПОДКЛЮЧЕНИЯ =====
        status_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))

        status_label = MDLabel(
            text='Статус:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        status_layout.add_widget(status_label)

        # Кнопки для выбора статуса
        status_buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        self.status_active = MDRaisedButton(
            text="Активен",
            md_bg_color=[0.3, 0.8, 0.3, 1] if (record and record['status'] == 'Активен') or not record else [0.5, 0.5,
                                                                                                             0.5, 0.5],
            text_color=[1, 1, 1, 1],
            size_hint_x=0.33,
            on_release=lambda x: self.set_status('Активен')
        )
        status_buttons.add_widget(self.status_active)

        self.status_paused = MDRaisedButton(
            text="Приостановлен",
            md_bg_color=[0.8, 0.6, 0.1, 1] if record and record['status'] == 'Приостановлен' else [0.5, 0.5, 0.5, 0.5],
            text_color=[1, 1, 1, 1],
            size_hint_x=0.33,
            on_release=lambda x: self.set_status('Приостановлен')
        )
        status_buttons.add_widget(self.status_paused)

        self.status_blocked = MDRaisedButton(
            text="Заблокирован",
            md_bg_color=[0.8, 0.2, 0.2, 1] if record and record['status'] == 'Заблокирован' else [0.5, 0.5, 0.5, 0.5],
            text_color=[1, 1, 1, 1],
            size_hint_x=0.33,
            on_release=lambda x: self.set_status('Заблокирован')
        )
        status_buttons.add_widget(self.status_blocked)

        status_layout.add_widget(status_buttons)

        # Сохраняем выбранный статус
        self.selected_status = record['status'] if record else 'Активен'
        form.add_widget(status_layout)

        return form

    def open_abonent_menu(self, instance):
        """Открыть меню выбора абонента для подключения"""
        self.menu = MDDropdownMenu(
            caller=instance,
            items=self.abonent_menu_items,
            width_mult=4,
            max_height=dp(300)
        )
        self.menu.open()

    def open_tariff_menu(self, instance):
        """Открыть меню выбора тарифа"""
        self.menu = MDDropdownMenu(
            caller=instance,
            items=self.tariff_menu_items,
            width_mult=4,
            max_height=dp(300)
        )
        self.menu.open()

    def set_abonent(self, text, abonent_id):
        """Установить выбранного абонента для подключения"""
        self.abonent_button.text = text
        self.selected_abonent_id = abonent_id
        self.selected_abonent_name = text
        if self.menu:
            self.menu.dismiss()

    def set_tariff(self, text, tariff_id, price, speed):
        """Установить выбранный тариф"""
        self.tariff_button.text = text
        self.selected_tariff_id = tariff_id
        self.selected_tariff_name = text
        if self.menu:
            self.menu.dismiss()

    def set_status(self, status):
        """Установить статус подключения с подсветкой"""
        self.selected_status = status

        # Обновляем цвета кнопок
        self.status_active.md_bg_color = [0.3, 0.8, 0.3, 1] if status == 'Активен' else [0.5, 0.5, 0.5, 0.5]
        self.status_paused.md_bg_color = [0.8, 0.6, 0.1, 1] if status == 'Приостановлен' else [0.5, 0.5, 0.5, 0.5]
        self.status_blocked.md_bg_color = [0.8, 0.2, 0.2, 1] if status == 'Заблокирован' else [0.5, 0.5, 0.5, 0.5]

    def save_connection(self, *args):
        """Сохранение подключения"""
        app = MDApp.get_running_app()

        # Получение данных из формы
        abonent_id = self.selected_abonent_id
        tariff_id = self.selected_tariff_id
        conn_date = self.dialog_fields['Дата подключения'].text.strip()
        status = self.selected_status if hasattr(self, 'selected_status') else 'Активен'

        # Валидация
        errors = []
        if not abonent_id:
            errors.append("Выберите абонента")
        if not tariff_id:
            errors.append("Выберите тариф")
        if not conn_date:
            errors.append("Дата подключения обязательна")

        if errors:
            self.show_message("Ошибка валидации", "\n".join(errors))
            return

        try:
            if self.current_edit_id:
                # Обновление
                app.db.update_connection(self.current_edit_id, abonent_id, tariff_id, conn_date, status)
                self.show_message("Успех", "Подключение обновлено")
            else:
                # Добавление
                app.db.add_connection(abonent_id, tariff_id, conn_date, status)
                self.show_message("Успех", "Подключение добавлено")

            # Закрыть диалог
            if self.current_dialog:
                self.current_dialog.dismiss()

            self.load_table_data('подключения')

        except Exception as e:
            self.show_message("Ошибка", str(e))

    # ==================== ДИАЛОГИ ДЛЯ ПЛАТЕЖЕЙ ====================

    def create_payment_dialog(self, record):
        """Диалог для платежа"""
        title = "Добавление платежа" if not record else "Редактирование платежа"

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=self.create_payment_form(record),
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    md_bg_color=[0.2, 0.8, 0.4, 1],  # Зеленый
                    text_color=[1, 1, 1, 1],
                    on_release=self.save_payment
                )
            ]
        )
        return dialog


    def create_payment_form(self, record):
        """Создание формы для платежа с выпадающим списком (ComboBox)"""
        form = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        form.bind(minimum_height=form.setter('height'))

        app = MDApp.get_running_app()
        abonents = app.db.get_abonents_list()

        # Поля формы
        self.dialog_fields = {}

        # ===== ВЫБОР АБОНЕНТА (COMBOBOX) =====
        abonent_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))

        abonent_label = MDLabel(
            text='Абонент:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        abonent_layout.add_widget(abonent_label)

        # Кнопка для выбора абонента (вместо текстового поля)
        current_abonent_text = record['abonent_name'] if record and 'abonent_name' in record else 'Выберите абонента'
        self.payment_abonent_button = MDRaisedButton(
            text=current_abonent_text,
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.2, 0.2, 0.25, 1],
            text_color=[1, 1, 1, 1],
            on_release=self.open_payment_abonent_menu
        )
        abonent_layout.add_widget(self.payment_abonent_button)
        form.add_widget(abonent_layout)

        # Создаем элементы меню для абонентов
        self.abonent_menu_items = []
        for a in abonents:
            menu_item = {
                "text": f"{a['fio']}",
                "secondary_text": f"ID: {a['id']}",
                "viewclass": "TwoLineListItem",
                "height": dp(60),
                "on_release": lambda x=f"{a['fio']}", id=a['id']: self.set_payment_abonent(x, id)
            }
            self.abonent_menu_items.append(menu_item)

        self.selected_payment_abonent_id = record['abonent_id'] if record else None
        self.selected_payment_abonent_name = record['abonent_name'] if record and 'abonent_name' in record else None

        # ===== СУММА ПЛАТЕЖА =====
        amount_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70))

        amount_label = MDLabel(
            text='Сумма платежа (руб):',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        amount_layout.add_widget(amount_label)

        amount_text = str(record['amount']) if record else ''
        amount_field = MDTextField(
            hint_text='0.00',
            text=amount_text,
            mode="fill",
            fill_color=[0.2, 0.2, 0.25, 1],
            size_hint_y=None,
            height=dp(50),
            input_filter='float',
            input_type='number'
        )
        amount_layout.add_widget(amount_field)
        self.dialog_fields['Сумма'] = amount_field
        form.add_widget(amount_layout)

        # ===== ДАТА ПЛАТЕЖА =====
        date_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110))

        date_label = MDLabel(
            text='Дата платежа:',
            theme_text_color='Custom',
            text_color=[1, 0.65, 0, 1],  # Оранжевый
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True
        )
        date_layout.add_widget(date_label)

        date_text = record['pay_date'] if record else datetime.now().strftime('%Y-%m-%d')
        date_field = MDTextField(
            hint_text='ГГГГ-ММ-ДД',
            text=date_text,
            mode="fill",
            fill_color=[0.2, 0.2, 0.25, 1],
            size_hint_y=None,
            height=dp(50)
        )
        date_layout.add_widget(date_field)
        self.dialog_fields['Дата платежа'] = date_field

        # Кнопка для выбора даты из календаря
        date_btn = MDRaisedButton(
            text="Выбрать дату",
            size_hint_y=None,
            height=dp(40),
            md_bg_color=[0.2, 0.8, 0.4, 1],
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.show_date_picker('Дата платежа')
        )
        date_layout.add_widget(date_btn)
        form.add_widget(date_layout)

        return form

    def open_payment_abonent_menu(self, instance):
        """Открыть меню выбора абонента для платежа"""
        self.menu = MDDropdownMenu(
            caller=instance,
            items=self.abonent_menu_items,
            width_mult=4,
            max_height=dp(300)
        )
        self.menu.open()

    def set_payment_abonent(self, text, abonent_id):
        """Установить выбранного абонента для платежа"""
        self.payment_abonent_button.text = text
        self.selected_payment_abonent_id = abonent_id
        self.selected_payment_abonent_name = text
        if self.menu:
            self.menu.dismiss()

    def save_payment(self, *args):
        """Сохранение платежа"""
        app = MDApp.get_running_app()

        # Получение данных из формы
        abonent_id = self.selected_payment_abonent_id
        amount_text = self.dialog_fields['Сумма'].text.strip()
        pay_date = self.dialog_fields['Дата платежа'].text.strip()

        # Валидация
        errors = []
        if not abonent_id:
            errors.append("Выберите абонента")
        if not amount_text:
            errors.append("Сумма обязательна")
        else:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    errors.append("Сумма должна быть положительной")
            except ValueError:
                errors.append("Сумма должна быть числом")
        if not pay_date:
            errors.append("Дата платежа обязательна")

        if errors:
            self.show_message("Ошибка валидации", "\n".join(errors))
            return

        try:
            if self.current_edit_id:
                # Обновление
                app.db.update_payment(self.current_edit_id, abonent_id, float(amount_text), pay_date)
                self.show_message("Успех", "Платеж обновлен")
            else:
                # Добавление
                app.db.add_payment(abonent_id, float(amount_text), pay_date)
                self.show_message("Успех", "Платеж добавлен")

            # Закрыть диалог
            if self.current_dialog:
                self.current_dialog.dismiss()

            self.load_table_data('платежи')

        except Exception as e:
            self.show_message("Ошибка", str(e))

    # ==================== УДАЛЕНИЕ ====================

    def show_delete_dialog(self):
        """Диалог подтверждения удаления"""
        if not self.selected_record:
            self.show_message("Внимание", "Выберите запись для удаления")
            return

        dialog = MDDialog(
            title="Подтверждение удаления",
            text="Вы уверены, что хотите удалить эту запись?",
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="УДАЛИТЬ",
                    md_bg_color=[0.8, 0.2, 0.2, 1],  # Красный
                    text_color=[1, 1, 1, 1],
                    on_release=self.confirm_delete
                )
            ]
        )
        dialog.open()

    def confirm_delete(self, *args):
        """Подтверждение удаления"""
        app = MDApp.get_running_app()
        dialog = args[0].parent.parent

        try:
            if self.current_table == 'абоненты':
                app.db.delete_abonent(self.selected_record['id'])
                self.show_message("Успех", "Абонент удален")
            elif self.current_table == 'тарифы':
                success, message = app.db.delete_tariff(self.selected_record['id'])
                if not success:
                    self.show_message("Ошибка", message)
                    dialog.dismiss()
                    return
                self.show_message("Успех", message)
            elif self.current_table == 'подключения':
                app.db.delete_connection(self.selected_record['id'])
                self.show_message("Успех", "Подключение удалено")
            elif self.current_table == 'платежи':
                app.db.delete_payment(self.selected_record['id'])
                self.show_message("Успех", "Платеж удален")

            dialog.dismiss()
            self.selected_record = None
            self.load_table_data(self.current_table)

        except Exception as e:
            self.show_message("Ошибка", str(e))

    # ==================== ПОИСК ====================

    def show_search_dialog(self):
        """Показать диалог поиска"""
        if self.current_table != 'абоненты':
            self.show_message("Информация", "Поиск доступен только для абонентов")
            return

        # Создаем форму поиска
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.search_phone = MDTextField(
            hint_text="Телефон",
            size_hint_y=None,
            height=dp(48)
        )
        form.add_widget(self.search_phone)

        self.search_address = MDTextField(
            hint_text="Адрес",
            size_hint_y=None,
            height=dp(48)
        )
        form.add_widget(self.search_address)

        dialog = MDDialog(
            title="Поиск абонентов",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="НАЙТИ",
                    md_bg_color=[1, 0.65, 0, 1],  # Оранжевый
                    text_color=[0, 0, 0, 1],
                    on_release=self.apply_search
                )
            ]
        )
        self.search_dialog = dialog
        dialog.open()

    def apply_search(self, *args):
        """Применение поиска"""
        phone = self.search_phone.text
        address = self.search_address.text

        if not phone and not address:
            self.show_message("Поиск", "Введите хотя бы один критерий")
            return

        app = MDApp.get_running_app()
        all_abonents = app.db.get_all_abonents()

        # Используем модуль поиска
        filtered = SearchModule.filter_abonents(all_abonents, phone, address)

        # Временно сохраняем отфильтрованные данные для отображения
        self.display_abonents(filtered)
        self.search_dialog.dismiss()

        self.show_message("Поиск", f"Найдено записей: {len(filtered)}")

    # ==================== ИМПОРТ/ЭКСПОРТ ====================

    def show_import_dialog(self):
        """Диалог импорта из JSON"""
        if self.current_table != 'абоненты':
            self.show_message("Информация", "Импорт доступен только для абонентов")
            return

        content = FileChooserListView(
            filters=['*.json'],
            path=os.path.expanduser('~')
        )

        def import_file(instance):
            if content.selection:
                file_path = content.selection[0]
                app = MDApp.get_running_app()
                result = FileIntegrationModule.import_from_json(file_path, app.db)

                if result['success']:
                    msg = result['message']
                    if result.get('errors'):
                        msg += "\n\nОшибки:\n" + "\n".join(result['errors'][:5])
                    self.show_message("Импорт завершен", msg)
                    self.load_table_data('абоненты')
                else:
                    self.show_message("Ошибка импорта", result['message'])

                popup.dismiss()

        # Создаем кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_layout.add_widget(MDFlatButton(text="Отмена", on_release=lambda x: popup.dismiss()))
        btn_layout.add_widget(MDRaisedButton(text="Импорт", on_release=import_file))

        # Добавляем кнопки в content
        content.add_widget(btn_layout)

        popup = Popup(
            title="Выберите JSON файл",
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    def show_export_dialog(self):
        """Диалог экспорта в XML"""
        content = FileChooserListView(
            path=os.path.expanduser('~'),
            dirselect=True
        )

        def export_file(instance):
            if content.selection:
                folder_path = content.selection[0]
                file_name = f"{self.current_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
                file_path = os.path.join(folder_path, file_name)

                app = MDApp.get_running_app()

                # Получение данных для экспорта
                if self.current_table == 'абоненты':
                    data = app.db.get_all_abonents()
                elif self.current_table == 'тарифы':
                    data = app.db.get_all_tariffs()
                elif self.current_table == 'подключения':
                    data = app.db.get_all_connections()
                elif self.current_table == 'платежи':
                    data = app.db.get_all_payments()
                else:
                    data = []

                result = FileIntegrationModule.export_to_xml(self.current_table, data, file_path)

                if result['success']:
                    self.show_message("Экспорт завершен", f"Файл сохранен:\n{file_path}")
                else:
                    self.show_message("Ошибка экспорта", result['message'])

                popup.dismiss()

        # Создаем кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_layout.add_widget(MDFlatButton(text="Отмена", on_release=lambda x: popup.dismiss()))
        btn_layout.add_widget(MDRaisedButton(text="Экспорт", on_release=export_file))

        # Добавляем кнопки в content
        content.add_widget(btn_layout)

        popup = Popup(
            title="Выберите папку для экспорта",
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    # ==================== ЗАМЕТКИ И КАЛЕНДАРЬ ====================

    def show_notes_dialog(self):
        """Диалог для заметок"""
        # Создаем форму для заметок
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        self.notes_input = TextInput(
            text=self.utils.current_note,
            hint_text="Введите заметку...",
            size_hint_y=None,
            height=dp(200)
        )
        form.add_widget(self.notes_input)

        dialog = MDDialog(
            title="Заметки",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    theme_text_color="Custom",
                    text_color=[0.7, 0.7, 0.7, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    md_bg_color=[0.5, 0.3, 0.8, 1],  # Фиолетовый
                    text_color=[1, 1, 1, 1],
                    on_release=self.save_notes
                )
            ]
        )
        self.notes_dialog = dialog
        dialog.open()

    def save_notes(self, *args):
        """Сохранение заметки"""
        success, message = self.utils.save_note(self.notes_input.text)
        if success:
            self.utils.current_note = self.notes_input.text
            self.show_message("Заметки", message)
        else:
            self.show_message("Ошибка", message)

        self.notes_dialog.dismiss()

    def load_notes(self):
        """Загрузка заметки"""
        try:
            success, note = self.utils.load_note()
            if success:
                self.utils.current_note = note
            else:
                print(f"Не удалось загрузить заметку: {note}")
        except Exception as e:
            print(f"Ошибка загрузки заметки: {e}")
            self.utils.current_note = ""

    def show_date_picker(self, target_field):
        """Показать календарь для выбора даты"""

        def on_save(instance, value, date_range):
            if target_field in self.dialog_fields:
                self.dialog_fields[target_field].text = value.strftime('%Y-%m-%d')

        date_picker = self.utils.get_date_picker(on_save)
        date_picker.open()

    # ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

    def show_message(self, title, text):
        """Показать информационное сообщение"""
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=[1, 0.65, 0, 1],  # Оранжевый
                    text_color=[0, 0, 0, 1],
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def logout(self):
        """Выход из системы"""
        self.manager.current = 'login'
        self.manager.transition.direction = 'right'