import customtkinter as ctk

class MainLayout(ctk.CTkFrame):
    MENU = [
        ("📋", "Đơn dịch vụ",  "order"),
        ("👤", "Khách hàng",   "customer"),
        ("🚗", "Xe",           "car"),
        ("🛠️", "Dịch vụ",      "service"),
        ("👨‍💼", "Nhân viên",    "staff"),
        ("📊", "Thống kê",     "statistical"),
    ]

    def __init__(self, master, current_user: dict, view_map: dict = None, on_logout=None, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.current_user = current_user
        self.view_map     = view_map or {}
        self.on_logout    = on_logout
        self._active_key  = None
        self._nav_btns    = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color="#1E2A3A", corner_radius=0, width=220)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(2, weight=1)
        sb.grid_columnconfigure(0, weight=1)

        # Logo
        ctk.CTkLabel(sb, text="🔧 CarService Pro",
                     font=("Segoe UI", 14, "bold"),
                     text_color="white").grid(row=0, column=0, padx=20, pady=24, sticky="w")

        ctk.CTkFrame(sb, fg_color="#2D3F54", height=1).grid(row=1, column=0, padx=16, sticky="ew")

        menu_frame = ctk.CTkFrame(sb, fg_color="transparent")
        menu_frame.grid(row=2, column=0, padx=12, pady=12, sticky="n")
        menu_frame.grid_columnconfigure(0, weight=1)

        visible_menu = self.MENU
        if self.current_user.get("role") != "admin":
            visible_menu = [m for m in self.MENU if m[2] != "staff"]

        for i, (icon, label, key) in enumerate(visible_menu):
            btn = ctk.CTkButton(
                menu_frame,
                text=f"  {icon}  {label}",
                anchor="w", height=42, corner_radius=6,
                font=("Segoe UI", 12),
                fg_color="transparent",
                hover_color="#2D3F54",
                text_color="#CBD5E1",
                command=lambda k=key: self.show_view(k),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_btns[key] = btn

        # User info + Logout
        bottom = ctk.CTkFrame(sb, fg_color="#162030", corner_radius=10)
        bottom.grid(row=3, column=0, padx=12, pady=(0, 16), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        name = self.current_user.get("full_name", "?")
        role = self.current_user.get("role", "")
        role_text  = "Admin" if role == "admin" else "Staff"
        role_color = "#1A73E8" if role == "admin" else "#34A853"

        ctk.CTkLabel(bottom, text=name,
                     font=("Segoe UI", 11, "bold"),
                     text_color="white").grid(row=0, column=0, padx=12, pady=(12, 0), sticky="w")
        ctk.CTkLabel(bottom, text=role_text,
                     font=("Segoe UI", 10),
                     text_color=role_color).grid(row=1, column=0, padx=12, pady=(0, 4), sticky="w")

        ctk.CTkButton(bottom, text="⏻  Đăng xuất",
                      height=32, corner_radius=6,
                      font=("Segoe UI", 10),
                      fg_color="transparent", hover_color="#EA4335",
                      text_color="#94A3B8",
                      command=self._handle_logout).grid(
            row=2, column=0, padx=12, pady=(4, 10), sticky="ew")

    def _build_content(self):
        self.content = ctk.CTkFrame(self, fg_color="#F0F2F5", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def show_view(self, key: str):
        if self._active_key and self._active_key in self._nav_btns:
            self._nav_btns[self._active_key].configure(fg_color="transparent", text_color="#CBD5E1")
        if key in self._nav_btns:
            self._nav_btns[key].configure(fg_color="#1A73E8", text_color="white")
        self._active_key = key

        for v in self.view_map.values():
            v.grid_remove()
        if key in self.view_map:
            self.view_map[key].grid(row=0, column=0, sticky="nsew", in_=self.content)

    def register_view(self, key: str, view: ctk.CTkFrame):
        self.view_map[key] = view
        view.grid(row=0, column=0, sticky="nsew", in_=self.content)
        view.grid_remove()

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()