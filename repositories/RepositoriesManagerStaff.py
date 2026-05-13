from api.Db import get_connection


class RepositoriesManagerStaff:
    @staticmethod
    def list_all_rows():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, full_name, role
            FROM users
            WHERE is_deleted = 0
            ORDER BY id DESC
            """
        )
        rows = [list(r) for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def username_exists(username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username=%s AND is_deleted=0", (username,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row is not None

    @staticmethod
    def insert(username, password, full_name, role):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, full_name, role, is_deleted)
            VALUES (%s, %s, %s, %s, 0)
            """,
            (username, password, full_name, role),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def update(staff_id, full_name, role, password):
        conn = get_connection()
        cursor = conn.cursor()
        if password:
            cursor.execute(
                "UPDATE users SET full_name=%s, role=%s, password=%s WHERE id=%s",
                (full_name, role, password, staff_id),
            )
        else:
            cursor.execute(
                "UPDATE users SET full_name=%s, role=%s WHERE id=%s",
                (full_name, role, staff_id),
            )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(staff_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_first_admin_id():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE role='admin' AND is_deleted=0 ORDER BY id LIMIT 1"
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else 1
