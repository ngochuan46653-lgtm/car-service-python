from api.Db import get_connection

class CustomerRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Chỉ lấy khách chưa bị xóa, đếm luôn số xe
        cursor.execute("""
            SELECT c.id, c.name, c.phone,
                   COUNT(ca.id) AS cars
            FROM customers c
            LEFT JOIN cars ca ON ca.customer_id = c.id
            WHERE c.is_deleted = 0
            GROUP BY c.id
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows  # list of dict

    @staticmethod
    def add(data):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, phone) VALUES (%s, %s)",
            (data["name"], data["phone"])
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(customer_id, data):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET name=%s, phone=%s WHERE id=%s",
            (data["name"], data["phone"], customer_id)
        )
        conn.commit()
        conn.close()


    @staticmethod
    def delete(customer_id):
        # Soft delete — không xóa thật, chỉ đánh dấu is_deleted=1
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET is_deleted=1 WHERE id=%s",
            (customer_id,)
        )
        conn.commit()
        conn.close()