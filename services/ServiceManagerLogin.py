from repositories.RepositoriesManagerLogin import UserRepository

class UserService:
    @staticmethod
    def login(username, password):
        if not username:
            return None, "Vui lòng nhập tên đăng nhập"
        if not password:
            return None, "Vui lòng nhập mật khẩu"

        try:
            user = UserRepository.find_by_username(username)
        except Exception as e:
            return None, f"Lỗi kết nối database: {e}"

        if user is None:
            return None, "Tên đăng nhập không tồn tại"

        if user["password"] != password:  # nếu có hash thì dùng bcrypt.checkpw()
            return None, "Mật khẩu không đúng"

        return user, None  # ✅ trả về dict