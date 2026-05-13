import customtkinter as ctk
from services.ServiceManagerLogin import UserService


class LoginForm(ctk.CTkFrame):
    """
    Form đăng nhập.
    Tham số:
        on_login_success(user)  — gọi khi đăng nhập thành công, truyền dict user.
    """

    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, **kwargs)
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        card = ctk.CTkFrame(self, width=360, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text="🔧 CarService Pro",
                     font=("Segoe UI", 22, "bold")).pack(pady=(32, 4))
        ctk.CTkLabel(card, text="Đăng nhập để tiếp tục",
                     font=("Segoe UI", 12),
                     text_color="gray").pack(pady=(0, 24))
        ctk.CTkLabel(card, text="Tên đăng nhập",
                     font=("Segoe UI", 12), anchor="w").pack(fill="x", padx=32)
        self.entry_user = ctk.CTkEntry(card, placeholder_text="Username",
                                       height=38, width=296)
        self.entry_user.pack(padx=32, pady=(4, 12))
        ctk.CTkLabel(card, text="Mật khẩu",
                     font=("Segoe UI", 12), anchor="w").pack(fill="x", padx=32)
        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Password",
                                       show="*", height=38, width=296)
        self.entry_pass.pack(padx=32, pady=(4, 8))
        self.entry_pass.bind("<Return>", lambda e: self._handle_login())
        self.lbl_error = ctk.CTkLabel(card, text="", text_color="#E74C3C",
                                      font=("Segoe UI", 11))
        self.lbl_error.pack(pady=(0, 8))
        ctk.CTkButton(card, text="Đăng nhập", height=40, width=296,
                      command=self._handle_login).pack(padx=32, pady=(0, 32))
        self.entry_user.focus()

    def _handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        user, error = UserService.login(username, password)

        if error:
            self.lbl_error.configure(text=error)
        else:
            self.lbl_error.configure(text="")
            self.on_login_success(user)

    def show_error(self, msg: str):
        """Hiển thị lỗi từ bên ngoài nếu cần."""
        self.lbl_error.configure(text=msg)
