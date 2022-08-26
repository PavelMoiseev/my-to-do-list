import sqlite3
import time
import math


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []

    def add_user(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    def get_user(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def update_user_avatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE user_id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: " + str(e))
            return False

        return True

    def get_todo_db(self, user_index):
        try:
            self.__cur.execute(f"SELECT todo_id, title, is_complete FROM todo WHERE user_id LIKE '{user_index}'")
            res = self.__cur.fetchall()
            return res
        except:
            print("Ошибка получения списка задач")
            return False

    def add_todo_db(self, user, content):
        complete = False
        try:
            self.__cur.execute("INSERT INTO todo VALUES(NULL, ?, ?, ?)", (user, content, complete))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка добавления задачи" + str(e))
            return False

    def del_todo_db(self, todo_index):
        try:
            self.__cur.execute(f"DELETE FROM todo WHERE todo_id = '{todo_index}'")
            self.__db.commit()
            return True
        except:
            print("Ошибка удаления задачи")
            return False

    def update_todo_db(self, todo_index):
        try:
            self.__cur.execute(f"UPDATE todo SET is_complete = not is_complete WHERE todo_id= '{todo_index}'")
            self.__db.commit()
            return True
        except:
            print("Ошибка обновления статуса задачи")
            return False
