from api.Db import get_connection


class RepositoriesManagerServeces:
    @staticmethod
    def list_all_display_rows():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, price
            FROM services
            WHERE is_deleted = 0
            ORDER BY id DESC
            """
        )
        rows = [[r[0], r[1], int(r[2])] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def list_services_price_rows():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, price FROM services WHERE is_deleted=0 ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def insert(name, price):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO services (name, price, is_deleted) VALUES (%s, %s, 0)",
            (name, price),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def update(service_id, name, price):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE services SET name=%s, price=%s WHERE id=%s",
            (name, price, service_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(service_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM services WHERE id=%s", (service_id,))
        conn.commit()
        cursor.close()
        conn.close()
