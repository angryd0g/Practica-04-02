import sqlite3
from datetime import datetime


class DatabaseController:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_path='abonents.db'):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Получение соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализация структуры БД"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица абонентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS abonents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                reg_date TEXT NOT NULL
            )
        ''')

        # Таблица тарифов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                speed TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')

        # Таблица подключений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abonent_id INTEGER NOT NULL,
                tariff_id INTEGER NOT NULL,
                conn_date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (abonent_id) REFERENCES abonents (id) ON DELETE CASCADE,
                FOREIGN KEY (tariff_id) REFERENCES tariffs (id) ON DELETE RESTRICT
            )
        ''')

        # Таблица платежей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abonent_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                pay_date TEXT NOT NULL,
                FOREIGN KEY (abonent_id) REFERENCES abonents (id) ON DELETE CASCADE
            )
        ''')

        # Таблица пользователей для авторизации
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Добавление тестового пользователя, если его нет
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "admin123")
            )
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("operator", "op123")
            )

        # Добавление тестовых тарифов, если их нет
        cursor.execute("SELECT COUNT(*) FROM tariffs")
        if cursor.fetchone()[0] == 0:
            test_tariffs = [
                ("Базовый", "50 Мбит/с", 500, "Для повседневного использования"),
                ("Оптимальный", "100 Мбит/с", 800, "Для стриминга и игр"),
                ("Премиум", "200 Мбит/с", 1200, "Максимальная скорость")
            ]
            cursor.executemany(
                "INSERT INTO tariffs (name, speed, price, description) VALUES (?, ?, ?, ?)",
                test_tariffs
            )

        conn.commit()
        conn.close()

    # ===== МЕТОДЫ ДЛЯ АБОНЕНТОВ =====

    def get_all_abonents(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM abonents ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_abonent(self, fio, address, phone, email, reg_date=None):
        if reg_date is None:
            reg_date = datetime.now().strftime('%Y-%m-%d')

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO abonents (fio, address, phone, email, reg_date) VALUES (?, ?, ?, ?, ?)",
            (fio, address, phone, email, reg_date)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_abonent(self, abonent_id, fio, address, phone, email, reg_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE abonents SET fio=?, address=?, phone=?, email=?, reg_date=? WHERE id=?",
            (fio, address, phone, email, reg_date, abonent_id)
        )
        conn.commit()
        conn.close()

    def delete_abonent(self, abonent_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM abonents WHERE id=?", (abonent_id,))
        conn.commit()
        conn.close()

    # ===== МЕТОДЫ ДЛЯ ТАРИФОВ =====

    def get_all_tariffs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tariffs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_tariff(self, name, speed, price, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tariffs (name, speed, price, description) VALUES (?, ?, ?, ?)",
            (name, speed, float(price), description)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_tariff(self, tariff_id, name, speed, price, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tariffs SET name=?, speed=?, price=?, description=? WHERE id=?",
            (name, speed, float(price), description, tariff_id)
        )
        conn.commit()
        conn.close()

    def delete_tariff(self, tariff_id):
        """Удаление тарифа с проверкой на использование в подключениях"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Проверка, используется ли тариф
        cursor.execute("SELECT COUNT(*) FROM connections WHERE tariff_id=?", (tariff_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            conn.close()
            return False, f"Невозможно удалить: тариф используется в {count} подключениях"

        cursor.execute("DELETE FROM tariffs WHERE id=?", (tariff_id,))
        conn.commit()
        conn.close()
        return True, "Тариф удален"

    # ===== МЕТОДЫ ДЛЯ ПОДКЛЮЧЕНИЙ =====

    def get_all_connections(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, a.fio as abonent_name, t.name as tariff_name 
            FROM connections c
            JOIN abonents a ON c.abonent_id = a.id
            JOIN tariffs t ON c.tariff_id = t.id
            ORDER BY c.id DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_connection(self, abonent_id, tariff_id, conn_date, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO connections (abonent_id, tariff_id, conn_date, status) VALUES (?, ?, ?, ?)",
            (abonent_id, tariff_id, conn_date, status)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_connection(self, conn_id, abonent_id, tariff_id, conn_date, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE connections SET abonent_id=?, tariff_id=?, conn_date=?, status=? WHERE id=?",
            (abonent_id, tariff_id, conn_date, status, conn_id)
        )
        conn.commit()
        conn.close()

    def delete_connection(self, conn_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM connections WHERE id=?", (conn_id,))
        conn.commit()
        conn.close()

    # ===== МЕТОДЫ ДЛЯ ПЛАТЕЖЕЙ =====

    def get_all_payments(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, a.fio as abonent_name 
            FROM payments p
            JOIN abonents a ON p.abonent_id = a.id
            ORDER BY p.id DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_payment(self, abonent_id, amount, pay_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO payments (abonent_id, amount, pay_date) VALUES (?, ?, ?)",
            (abonent_id, float(amount), pay_date)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update_payment(self, payment_id, abonent_id, amount, pay_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE payments SET abonent_id=?, amount=?, pay_date=? WHERE id=?",
            (abonent_id, float(amount), pay_date, payment_id)
        )
        conn.commit()
        conn.close()

    def delete_payment(self, payment_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM payments WHERE id=?", (payment_id,))
        conn.commit()
        conn.close()

    # ===== МЕТОДЫ ДЛЯ АВТОРИЗАЦИИ =====

    def check_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def get_abonents_list(self):
        """Получение списка абонентов для выпадающих списков"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, fio FROM abonents ORDER BY fio")
        rows = cursor.fetchall()
        conn.close()
        return [{'id': row[0], 'fio': row[1]} for row in rows]

    def get_tariffs_list(self):
        """Получение списка тарифов для выпадающих списков"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, speed FROM tariffs ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [{'id': row[0], 'name': row[1], 'price': row[2], 'speed': row[3]} for row in rows]