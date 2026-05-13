from models.ModelsManagerCar import Car
from repositories.RepositoriesManagerCar import RepositoriesManagerCar


class ServiceManagerCar:
    def __init__(self, repository: RepositoriesManagerCar):
        """
        Nhận vào một RepositoriesManagerCar đã khởi tạo sẵn.
        Ví dụ:
            repo = RepositoriesManagerCar(connection)
            service = ServiceManagerCar(repo)
        """
        self.repo = repository

    # ------------------------------------------------------------------ #
    #  Lấy dữ liệu
    # ------------------------------------------------------------------ #

    def get_all_cars(self) -> list[Car]:
        """Trả về danh sách tất cả xe (chưa xoá)"""
        return self.repo.get_all()

    def get_all_cars_as_tuples(self) -> list[tuple]:
        """
        Trả về list tuple dùng trực tiếp cho CarView (Treeview).
        Thứ tự khớp với COLUMNS: (id, owner, plate, brand, color, type)
        """
        return self.repo.get_all_with_owner()

    def get_car_by_id(self, car_id: int) -> Car | None:
        """Lấy xe theo ID, trả về None nếu không tìm thấy"""
        return self.repo.get_by_id(car_id)

    def get_cars_by_customer(self, customer_id: int) -> list[Car]:
        """Lấy tất cả xe của một khách hàng"""
        return self.repo.get_by_customer_id(customer_id)

    # ------------------------------------------------------------------ #
    #  Thêm xe
    # ------------------------------------------------------------------ #

    def add_car(self, customer_id: int, license_plate: str, brand: str,
                color: str, car_type: str) -> tuple[bool, str]:
        """
        Thêm xe mới sau khi kiểm tra nghiệp vụ.
        Trả về (True, "Thành công") hoặc (False, "Lý do lỗi").
        """
        # Kiểm tra biển số không được để trống
        if not license_plate or not license_plate.strip():
            return False, "Biển số xe không được để trống."

        # Kiểm tra biển số đã tồn tại chưa
        existing = self.repo.get_by_license_plate(license_plate.strip())
        if existing:
            return False, f"Biển số '{license_plate}' đã tồn tại trong hệ thống."

        # Kiểm tra các trường bắt buộc
        if not brand or not brand.strip():
            return False, "Hãng xe không được để trống."
        if not color or not color.strip():
            return False, "Màu xe không được để trống."
        if not car_type or not car_type.strip():
            return False, "Loại xe không được để trống."

        new_car = Car(
            customer_id=customer_id,
            license_plate=license_plate.strip(),
            brand=brand.strip(),
            color=color.strip(),
            car_type=car_type.strip(),
            is_deleted=0
        )
        new_id = self.repo.add(new_car)
        return True, f"Thêm xe thành công (ID: {new_id})."

    # ------------------------------------------------------------------ #
    #  Cập nhật xe
    # ------------------------------------------------------------------ #

    def update_car(self, car_id: int, customer_id: int, license_plate: str,
                   brand: str, color: str, car_type: str) -> tuple[bool, str]:
        """
        Cập nhật thông tin xe.
        Trả về (True, "Thành công") hoặc (False, "Lý do lỗi").
        """
        existing = self.repo.get_by_id(car_id)
        if not existing:
            return False, f"Không tìm thấy xe với ID {car_id}."

        # Nếu biển số thay đổi → kiểm tra trùng
        if license_plate.strip() != existing.license_plate:
            duplicate = self.repo.get_by_license_plate(license_plate.strip())
            if duplicate:
                return False, f"Biển số '{license_plate}' đã được sử dụng bởi xe khác."

        updated_car = Car(
            id=car_id,
            customer_id=customer_id,
            license_plate=license_plate.strip(),
            brand=brand.strip(),
            color=color.strip(),
            car_type=car_type.strip(),
            is_deleted=existing.is_deleted
        )
        success = self.repo.update(updated_car)
        if success:
            return True, "Cập nhật xe thành công."
        return False, "Cập nhật thất bại, vui lòng thử lại."

    # ------------------------------------------------------------------ #
    #  Xoá xe
    # ------------------------------------------------------------------ #

    def delete_car(self, car_id: int) -> tuple[bool, str]:
        """
        Xoá mềm xe theo ID.
        Trả về (True, "Thành công") hoặc (False, "Lý do lỗi").
        """
        existing = self.repo.get_by_id(car_id)
        if not existing:
            return False, f"Không tìm thấy xe với ID {car_id}."

        success = self.repo.delete(car_id)
        if success:
            return True, "Xoá xe thành công."
        return False, "Xoá thất bại, vui lòng thử lại."