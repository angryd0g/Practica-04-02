# modules/file_integration.py
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime


class FileIntegrationModule:
    """Модуль для работы с файлами (импорт/экспорт)"""

    @staticmethod
    def import_from_json(file_path, db_controller):
        """
        Импорт данных абонентов из JSON-файла
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Файл должен содержать список абонентов")

            added_count = 0
            errors = []

            for item in data:
                # Проверка обязательных полей
                required_fields = ['fio', 'address', 'phone', 'email']
                if not all(field in item for field in required_fields):
                    errors.append(f"Пропущены обязательные поля в записи: {item}")
                    continue

                # Проверка формата телефона и email
                if not FileIntegrationModule._validate_phone(item['phone']):
                    errors.append(f"Некорректный телефон: {item['phone']}")
                    continue

                if not FileIntegrationModule._validate_email(item['email']):
                    errors.append(f"Некорректный email: {item['email']}")
                    continue

                # Добавление в БД
                try:
                    db_controller.add_abonent(
                        item['fio'],
                        item['address'],
                        item['phone'],
                        item['email'],
                        item.get('reg_date', datetime.now().strftime('%Y-%m-%d'))
                    )
                    added_count += 1
                except Exception as e:
                    errors.append(f"Ошибка добавления {item.get('fio', '')}: {str(e)}")

            return {
                'success': True,
                'added': added_count,
                'errors': errors,
                'message': f"Импортировано: {added_count}, ошибок: {len(errors)}"
            }

        except FileNotFoundError:
            return {'success': False, 'message': f"Файл не найден: {file_path}"}
        except json.JSONDecodeError as e:
            return {'success': False, 'message': f"Ошибка формата JSON: {str(e)}"}
        except Exception as e:
            return {'success': False, 'message': f"Неизвестная ошибка: {str(e)}"}

    @staticmethod
    def export_to_xml(table_name, data, file_path):
        """
        Экспорт данных в XML-файл
        """
        try:
            root = ET.Element(table_name)

            for i, row in enumerate(data):
                item = ET.SubElement(root, 'record', {'id': str(i + 1)})
                for key, value in row.items():
                    if key != 'id':  # ID не включаем как отдельный тег
                        field = ET.SubElement(item, key)
                        field.text = str(value) if value is not None else ''

            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)

            return {'success': True, 'message': f"Экспортировано {len(data)} записей"}

        except Exception as e:
            return {'success': False, 'message': f"Ошибка экспорта: {str(e)}"}

    @staticmethod
    def _validate_phone(phone):
        """Проверка корректности телефона"""
        return any(c.isdigit() for c in phone) and len(phone.strip()) > 0

    @staticmethod
    def _validate_email(email):
        """Проверка корректности email"""
        return '@' in email and '.' in email and len(email.strip()) > 0