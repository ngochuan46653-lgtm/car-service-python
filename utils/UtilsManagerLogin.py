import customtkinter as ctk

class AuthService:
    """
    Service xác thực người dùng.
    Gọi AuthService.set_users(DEMO_USERS) từ main.py trước khi dùng.
    """
    _users: list = []

    @classmethod
    def set_users(cls, users: list):
        cls._users = users

    @classmethod
    def login(cls, username: str, password: str):
        """
        Trả về (user_dict, None) nếu thành công,
        hoặc (None, error_message) nếu thất bại.
        """
        if not username.strip():
            return None, "Vui lòng nhập tên đăng nhập!"
        if not password:
            return None, "Vui lòng nhập mật khẩu!"

        user = next(
            (u for u in cls._users
             if u["username"] == username and u["password"] == password),
            None
        )
        if not user:
            return None, "Sai tài khoản hoặc mật khẩu!"
        return user, None


class LoginForm(ctk.CTkFrame):
    """
    Form đăng nhập.
    Tham số:
        on_login_success(user)  — gọi khi đăng nhập thành công, truyền dict user.
    """

    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, **kwargs)
        # FIX: tên tham số là on_login_success (khớp với main.py)
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card giữa màn hình
        card = ctk.CTkFrame(self, width=360, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text="🔧 CarService Pro",
                     font=("Segoe UI", 22, "bold")).pack(pady=(32, 4))
        ctk.CTkLabel(card, text="Đăng nhập để tiếp tục",
                     font=("Segoe UI", 12),
                     text_color="gray").pack(pady=(0, 24))

        # Username
        ctk.CTkLabel(card, text="Tên đăng nhập",
                     font=("Segoe UI", 12), anchor="w").pack(fill="x", padx=32)
        self.entry_user = ctk.CTkEntry(card, placeholder_text="Username",
                                       height=38, width=296)
        self.entry_user.pack(padx=32, pady=(4, 12))

        # Password
        ctk.CTkLabel(card, text="Mật khẩu",
                     font=("Segoe UI", 12), anchor="w").pack(fill="x", padx=32)
        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Password",
                                       show="*", height=38, width=296)
        self.entry_pass.pack(padx=32, pady=(4, 8))
        # Nhấn Enter để đăng nhập
        self.entry_pass.bind("<Return>", lambda e: self._handle_login())

        # Lỗi
        self.lbl_error = ctk.CTkLabel(card, text="", text_color="#E74C3C",
                                      font=("Segoe UI", 11))
        self.lbl_error.pack(pady=(0, 8))

        ctk.CTkButton(card, text="Đăng nhập", height=40, width=296,
                      command=self._handle_login).pack(padx=32, pady=(0, 32))

        # Focus vào ô username
        self.entry_user.focus()

    def _handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        user, error = AuthService.login(username, password)

        if error:
            self.lbl_error.configure(text=error)
        else:
            self.lbl_error.configure(text="")
            # FIX: gọi callback với user object (không cần main.py xử lý lại)
            self.on_login_success(user)

    def show_error(self, msg: str):
        """Hiển thị lỗi từ bên ngoài nếu cần."""
        self.lbl_error.configure(text=msg)
