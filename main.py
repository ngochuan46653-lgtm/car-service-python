import customtkinter as ctk
from utils.UtilsManagerLogin import LoginForm
from utils.Mainlayout import MainLayout
from utils.UtilsManagerCustomer import CustomerView
from utils.UtilsManagerCar import CarView
from utils.UtilsManagerServeces import ServiceView
from utils.UtilsManagerStaff import StaffView
from utils.UtilsManagerOrder import OrderView
from utils.UtilsManagerStatistical import StatisticalView

# ── Dữ liệu demo ─────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CarService Pro")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        ctk.set_appearance_mode("light")

        self.current_user = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._show_login()

    def _show_login(self):
        # Xóa layout chính nếu đang hiển thị
        if hasattr(self, "_layout") and self._layout.winfo_exists():
            self._layout.destroy()

        # FIX: dùng đúng class LoginForm, đúng tên tham số on_login_success
        self._login_view = LoginForm(self, on_login_success=self._handle_login)
        self._login_view.grid(row=0, column=0, sticky="nsew")

    def _handle_login(self, user):
        # FIX: LoginForm đã xác thực xong, truyền thẳng object user vào đây
        self.current_user = user
        if hasattr(self, "_login_view") and self._login_view.winfo_exists():
            self._login_view.destroy()
        self._show_main()

    def _show_main(self):
        self._layout = MainLayout(
            self,
            current_user=self.current_user,
            on_logout=self._show_login
        )
        self._layout.grid(row=0, column=0, sticky="nsew")
        # Khởi tạo các View
        cnt = self._layout.content
        self.views = {
            "order":       OrderView(cnt, current_user=self.current_user),
            "customer":    CustomerView(cnt),
            "car":         CarView(cnt),
            "service":     ServiceView(cnt),
            "statistical": StatisticalView(cnt),
        }

        if self.current_user["role"] == "admin":
            self.views["staff"] = StaffView(cnt)

        # Đăng ký view vào layout
        for name, view in self.views.items():
            self._layout.register_view(name, view)

        self._wire_demo_data()
        self._layout.show_view("order")

    def _wire_demo_data(self):
        d_cust = [[1, "Nguyễn Văn A", "0901234567", 2],
                [2, "Trần Thị B",   "0912345678", 1]]
        d_cars = [[1, "Nguyễn Văn A", "51A-12345", "Toyota", "Trắng", "Sedan"]]
        d_svcs = [[1, "Thay dầu", 150000], [2, "Rửa xe", 50000]]

        # ✅ KHÔNG wire demo cho customer nữa — đã dùng DB thật

        # Car
        self.views["car"].cb_load          = lambda: d_cars
        self.views["car"].cb_get_customers = lambda: [f"{r[0]} - {r[1]}" for r in d_cust]
        # Service
        self.views["service"].cb_load      = lambda: d_svcs

        # Order
        ov = self.views["order"]
        ov.cb_load          = lambda f=None: [[1, "10/05/2026", "Nguyễn Văn A", "51A-12345", "200,000", "paid", "Admin"]]
        ov.cb_get_customers = lambda: [f"{r[0]} - {r[1]}" for r in d_cust]
        ov.cb_get_cars      = lambda cid: [f"{r[0]} - {r[2]}" for r in d_cars]
        ov.cb_get_services  = lambda: [{"id": r[0], "name": r[1], "price": r[2]} for r in d_svcs]

        # Thống kê
        st = self.views["statistical"]
        st.cb_revenue_by_month = lambda y: [{"month": str(m), "revenue": 1_000_000 * (m % 5 + 1)} for m in range(1, 13)]
        st.cb_total_customers  = lambda: len(d_cust)
        st.cb_top_services     = lambda n: [{"name": "Thay dầu", "count": 45}, {"name": "Rửa xe", "count": 30}]
        st.cb_cars_per_staff   = lambda: [{"staff": "Trần NV", "count": 12}, {"staff": "Admin", "count": 5}]

        # Refresh toàn bộ
        for v in self.views.values():
            if hasattr(v, "refresh"):
                v.refresh()


if __name__ == "__main__":
    app = App()
    app.mainloop()