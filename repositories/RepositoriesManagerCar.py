import mysql.connector
from models.ModelsManagerCar import Car


class RepositoriesManagerCar:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        """
        Nhận vào một connection MySQL đã được khởi tạo sẵn.
        Ví dụ:
            conn = mysql.connector.connect(host=..., user=..., password=..., database=...)
            repo = RepositoriesManagerCar(conn)
        """
        self.connection = connection

    def _get_cursor(self):
        return self.connection.cursor()

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    def get_all(self) -> list[Car]:
        """Lấy tất cả xe chưa bị xoá (is_deleted = 0)"""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT id, customer_id, license_plate, brand, color, car_type, is_deleted "
            "FROM cars WHERE is_deleted = 0"
        )
        rows = cursor.fetchall()
        cursor.close()
        return [Car.from_row(row) for row in rows]

    def get_all_with_owner(self) -> list[tuple]:
        """
        Lấy tất cả xe kèm tên chủ xe (JOIN với bảng customers).
        Trả về list tuple: (id, owner_name, license_plate, brand, color, car_type)
        Đúng thứ tự để đổ vào Treeview của CarView.
        """
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT c.id, cu.name, c.license_plate, c.brand, c.color, c.car_type "
            "FROM cars c "
            "LEFT JOIN customers cu ON c.customer_id = cu.id "
            "WHERE c.is_deleted = 0"
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_by_id(self, car_id: int) -> Car | None:
        """Lấy xe theo ID"""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT id, customer_id, license_plate, brand, color, car_type, is_deleted "
            "FROM cars WHERE id = %s AND is_deleted = 0",
            (car_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return Car.from_row(row)

    def get_by_customer_id(self, customer_id: int) -> list[Car]:
        """Lấy tất cả xe của một khách hàng"""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT id, customer_id, license_plate, brand, color, car_type, is_deleted "
            "FROM cars WHERE customer_id = %s AND is_deleted = 0",
            (customer_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return [Car.from_row(row) for row in rows]

    def get_by_license_plate(self, license_plate: str) -> Car | None:
        """Tìm xe theo biển số"""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT id, customer_id, license_plate, brand, color, car_type, is_deleted "
            "FROM cars WHERE license_plate = %s AND is_deleted = 0",
            (license_plate,)
        )
        row = cursor.fetchone()
        cursor.close()
        return Car.from_row(row)

    # ------------------------------------------------------------------ #
    #  CREATE
    # ------------------------------------------------------------------ #

    def add(self, car: Car) -> int:
        """
        Thêm xe mới vào DB.
        Trả về ID vừa được insert.
        """
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO cars (customer_id, license_plate, brand, color, car_type, is_deleted) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            car.to_tuple()
        )
        self.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    def update(self, car: Car) -> bool:
        """
        Cập nhật thông tin xe theo car.id.
        Trả về True nếu có dòng được cập nhật.
        """
        cursor = self._get_cursor()
        cursor.execute(
            "UPDATE cars SET customer_id=%s, license_plate=%s, brand=%s, "
            "color=%s, car_type=%s, is_deleted=%s WHERE id=%s",
            (*car.to_tuple(), car.id)
        )
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    # ------------------------------------------------------------------ #
    #  DELETE (soft delete)
    # ------------------------------------------------------------------ #

    def delete(self, car_id: int) -> bool:
        """
        Xoá mềm: đánh dấu is_deleted = 1 thay vì xoá khỏi DB.
        Trả về True nếu thành công.
        """
        cursor = self._get_cursor()
        cursor.execute(
            "UPDATE cars SET is_deleted = 1 WHERE id = %s",
            (car_id,)
        )
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0