from repositories.RepositoriesManagerCustomer import CustomerRepository

class CustomerService:

    @staticmethod
    def get_all():
        rows = CustomerRepository.get_all()
        # Trả về list of tuple cho Treeview: (id, name, phone, cars)
        return [[r["id"], r["name"], r["phone"], r["cars"]] for r in rows]

    @staticmethod
    def add(data):
        if not data["name"]:
            return False, "Vui lòng nhập họ tên"
        if not data["phone"]:
            return False, "Vui lòng nhập số điện thoại"
        try:
            CustomerRepository.add(data)
            return True, "Thêm thành công"
        except Exception as e:
            return False, f"Lỗi: {e}"

    @staticmethod
    def update(customer_id, data):
        if not data["name"]:
            return False, "Vui lòng nhập họ tên"
        if not data["phone"]:
            return False, "Vui lòng nhập số điện thoại"
        try:
            CustomerRepository.update(customer_id, data)
            return True, "Cập nhật thành công"
        except Exception as e:
            return False, f"Lỗi: {e}"

    @staticmethod
    def delete(customer_id):
        try:
            CustomerRepository.delete(customer_id)
            return True, "Đã xóa"
        except Exception as e:
            return False, f"Lỗi: {e}"