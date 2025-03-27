# screens/tab_classes.py
from kivymd.uix.tab import MDTabsBase
from kivy.uix.boxlayout import BoxLayout


class TabAbonents(BoxLayout, MDTabsBase):
    """Вкладка для абонентов"""
    pass


class TabTariffs(BoxLayout, MDTabsBase):
    """Вкладка для тарифов"""
    pass


class TabConnections(BoxLayout, MDTabsBase):
    """Вкладка для подключений"""
    pass


class TabPayments(BoxLayout, MDTabsBase):
    """Вкладка для платежей"""
    pass