import customtkinter as ctk

from api.Db import get_connection
from repositories.RepositoriesManagerCar import RepositoriesManagerCar
from utils.UtilsManagerLogin import LoginForm
from utils.Mainlayout import MainLayout
from utils.UtilsManagerCustomer import CustomerView
from utils.UtilsManagerCar import CarView
from utils.UtilsManagerServeces import ServiceView
from utils.UtilsManagerStaff import StaffView
from utils.UtilsManagerOrder import OrderView
from utils.UtilsManagerStatistical import StatisticalView

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
        if hasattr(self, "_layout") and self._layout.winfo_exists():
            self._layout.destroy()
        self._login_view = LoginForm(self, on_login_success=self._handle_login)
        self._login_view.grid(row=0, column=0, sticky="nsew")

    def _handle_login(self, user):
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
        for name, view in self.views.items():
            self._layout.register_view(name, view)

        self._wire_car_from_db()
        self._wire_statistics_demo()
        for v in self.views.values():
            if hasattr(v, "refresh"):
                v.refresh()
        self._layout.show_view("order")

    def _wire_car_from_db(self):
        """Xe: load từ MySQL (không dùng dữ liệu demo)."""
        cv = self.views["car"]

        def load_cars():
            conn = get_connection()
            try:
                repo = RepositoriesManagerCar(conn)
                return list(repo.get_all_with_owner())
            finally:
                conn.close()

        cv.cb_load = load_cars

    def _wire_statistics_demo(self):
        """Thống kê: vẫn dùng số mẫu cho biểu đồ (chưa nối query báo cáo)."""
        st = self.views["statistical"]
        st.cb_revenue_by_month = lambda y: [
            {"month": str(m), "revenue": 1_000_000 * (m % 5 + 1)} for m in range(1, 13)
        ]
        st.cb_total_customers = lambda: 0
        st.cb_top_services = lambda n: [
            {"name": "Thay dầu", "count": 45},
            {"name": "Rửa xe", "count": 30},
        ]
        st.cb_cars_per_staff = lambda: [
            {"staff": "Trần NV", "count": 12},
            {"staff": "Admin", "count": 5},
        ]
        st.refresh()


if __name__ == "__main__":
    app = App()
    app.mainloop()