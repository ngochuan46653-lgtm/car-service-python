from api.Db import get_connection

class UserRepository:
    @staticmethod
    def find_by_username(username):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        return user  # trả về dict hoặc None 