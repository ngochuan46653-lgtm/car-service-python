from datetime import datetime

from api.Db import get_connection


def _parse_order_date_dd_mm_yyyy(order_date_str):
    """
    Parse DD/MM/YYYY từ form. Cho phép dấu '-' thay '/'.
    Trả về chuỗi YYYY-MM-DD để CAST(... AS DATE) ổn định với MySQL.
    """
    if not order_date_str:
        return None
    s = str(order_date_str).strip().replace("\u200b", "").replace("-", "/")
    if not s:
        return None
    try:
        d = datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError as e:
        raise ValueError("Ngày không hợp lệ — dùng định dạng DD/MM/YYYY (ví dụ 02/12/2025).") from e
    return d.strftime("%Y-%m-%d")


class RepositoriesManagerOrder:
    @staticmethod
    def list_orders_join():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                o.id,
                o.order_date,
                c.id AS customer_id,
                c.name AS customer_name,
                ca.id AS car_id,
                ca.license_plate AS car_plate,
                o.total_amount,
                o.status,
                u.full_name AS staff_name
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            JOIN cars ca ON ca.id = o.car_id
            JOIN users u ON u.id = o.user_id
            WHERE o.is_deleted = 0
            ORDER BY o.id DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def list_order_detail_pairs(order_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT service_id, quantity
            FROM order_details
            WHERE order_id = %s
            ORDER BY id ASC
            """,
            (order_id,),
        )
        details = cursor.fetchall()
        cursor.close()
        conn.close()
        return details

    @staticmethod
    def insert_order_with_details(
        customer_id,
        car_id,
        user_id,
        order_date_str,
        total,
        status,
        detail_rows,
    ):
        conn = get_connection()
        cursor = conn.cursor()
        if order_date_str:
            order_date_iso = _parse_order_date_dd_mm_yyyy(order_date_str)
            cursor.execute(
                """
                INSERT INTO orders (customer_id, car_id, user_id, order_date, total_amount, status, is_deleted)
                VALUES (%s, %s, %s, CAST(%s AS DATE), %s, %s, 0)
                """,
                (customer_id, car_id, user_id, order_date_iso, total, status),
            )
        else:
            cursor.execute(
                """
                INSERT INTO orders (customer_id, car_id, user_id, total_amount, status, is_deleted)
                VALUES (%s, %s, %s, %s, %s, 0)
                """,
                (customer_id, car_id, user_id, total, status),
            )
        order_id = cursor.lastrowid
        for service_id, qty, price, subtotal in detail_rows:
            cursor.execute(
                """
                INSERT INTO order_details (order_id, service_id, quantity, price_at_time, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order_id, service_id, qty, price, subtotal),
            )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def update_order_with_details(
        order_id,
        customer_id,
        car_id,
        order_date_str,
        total,
        status,
        detail_rows,
    ):
        conn = get_connection()
        cursor = conn.cursor()
        if order_date_str:
            order_date_iso = _parse_order_date_dd_mm_yyyy(order_date_str)
            cursor.execute(
                """
                UPDATE orders
                SET customer_id=%s, car_id=%s, order_date=CAST(%s AS DATE),
                    total_amount=%s, status=%s
                WHERE id=%s
                """,
                (customer_id, car_id, order_date_iso, total, status, order_id),
            )
        else:
            cursor.execute(
                """
                UPDATE orders
                SET customer_id=%s, car_id=%s, total_amount=%s, status=%s
                WHERE id=%s
                """,
                (customer_id, car_id, total, status, order_id),
            )
        cursor.execute("DELETE FROM order_details WHERE order_id=%s", (order_id,))
        for service_id, qty, price, subtotal in detail_rows:
            cursor.execute(
                """
                INSERT INTO order_details (order_id, service_id, quantity, price_at_time, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (order_id, service_id, qty, price, subtotal),
            )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete_order_cascade(order_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_details WHERE order_id=%s", (order_id,))
        cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def select_customer_labels():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name FROM customers WHERE is_deleted=0 ORDER BY id DESC"
        )
        rows = [f"{r[0]} - {r[1]}" for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rows

    @staticmethod
    def select_car_labels(customer_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, license_plate FROM cars WHERE customer_id=%s AND is_deleted=0 ORDER BY id DESC",
            (customer_id,),
        )
        rows = [f"{r[0]} - {r[1]}" for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rows
