# This code is licensed under the terms of the GNU Lesser General Public License v2.1
import sqlite3


class Database:

    def __init__(self):
        self.connection = sqlite3.connect('database/database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, input_message TEXT, message TEXT, timestamp TEXT)')
        self.connection.commit()

    async def insert_message(self, input_message_message: str, message: str, timestamp: str) -> None:
        self.cursor.execute('INSERT INTO chat (input_message, message, timestamp) VALUES (?, ?, ?)',
                            ("You: " + input_message_message, "Chatbot:" + message, timestamp))
        self.connection.commit()

    async def get_messages(self) -> list:
        self.cursor.execute('SELECT * FROM chat')
        return self.cursor.fetchall()

    async def close(self) -> None:
        self.connection.close()

    async def delete_messages(self) -> None:
        self.cursor.execute('DELETE FROM chat')
        self.connection.commit()

    async def delete_message(self, id: int) -> None:
        self.cursor.execute('DELETE FROM chat WHERE id = ?', (id,))
        self.connection.commit()

    async def update_message(self, id: int, input_message: str, message: str, timestamp: str) -> None:
        self.cursor.execute('UPDATE chat SET input_message = ?, message = ?, timestamp = ? WHERE id = ?',
                            (input_message, message, timestamp, id))
        self.connection.commit()

    async def get_message(self, id: int) -> list:
        self.cursor.execute('SELECT * FROM chat WHERE id = ?', (id,))
        return self.cursor.fetchone()

    async def get_message_by_input_message(self, input_message: str) -> list:
        self.cursor.execute('SELECT * FROM chat WHERE input_message = ?', (input_message,))
        return self.cursor.fetchone()

    async def get_message_by_message(self, message: str) -> list:
        self.cursor.execute('SELECT * FROM chat WHERE message = ?', (message,))
        return self.cursor.fetchone()

    async def get_message_by_timestamp(self, timestamp: str) -> list:
        self.cursor.execute('SELECT * FROM chat WHERE timestamp = ?', (timestamp,))
        return self.cursor.fetchone()
