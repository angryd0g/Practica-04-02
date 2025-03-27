# modules/search_module.py

class SearchModule:
    """Модуль поиска и фильтрации"""

    @staticmethod
    def filter_abonents(abonents, phone=None, address=None):
        """
        Фильтрация абонентов по критериям
        """
        filtered = abonents

        if phone and phone.strip():
            phone_lower = phone.lower().strip()
            filtered = [a for a in filtered if phone_lower in a['phone'].lower()]

        if address and address.strip():
            address_lower = address.lower().strip()
            filtered = [a for a in filtered if address_lower in a['address'].lower()]

        return filtered