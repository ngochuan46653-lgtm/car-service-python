import customtkinter as ctk
from tkinter import Canvas


class StatisticalView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.cb_revenue_by_month = self.cb_total_customers = None
        self.cb_top_services = self.cb_cars_per_staff = None
        self._kpi_labels = {}
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=24, pady=(20, 12), sticky="ew")
        ctk.CTkLabel(hdr, text="📊 Thống kê & Báo cáo", font=("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkButton(hdr, text="🔄 Làm mới", width=100, command=self.refresh).pack(side="right")

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)

        # KPI Row
        kpi_row = ctk.CTkFrame(body, fg_color="transparent")
        kpi_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        kpi_items = [
            ("rev",   "Doanh thu",    "#1A73E8"),
            ("cust",  "Khách hàng",   "#34A853"),
            ("order", "Đơn hàng",     "#FF6D00"),
            ("top",   "Dịch vụ hot",  "#FBBC04"),
        ]
        for i, (k, label, color) in enumerate(kpi_items):
            card = ctk.CTkFrame(kpi_row, fg_color="white", corner_radius=10)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            kpi_row.grid_columnconfigure(i, weight=1)
            ctk.CTkFrame(card, fg_color=color, width=4).pack(side="left", padx=12, pady=15, fill="y")
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", pady=12)
            ctk.CTkLabel(info, text=label, font=("Segoe UI", 10), text_color="#6B7280").pack(anchor="w")
            lbl = ctk.CTkLabel(info, text="—", font=("Segoe UI", 16, "bold"))
            lbl.pack(anchor="w")
            self._kpi_labels[k] = lbl

        # Charts
        self.canvas_monthly = self._make_chart(body, "Doanh thu theo tháng", row=1, col=0, span=2)
        self.canvas_svc     = self._make_chart(body, "Top Dịch vụ",           row=2, col=0)
        self.canvas_staff   = self._make_chart(body, "Xe / Nhân viên",        row=2, col=1)

    def _make_chart(self, parent, title, row, col, span=1):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.grid(row=row, column=col, columnspan=span, sticky="nsew", padx=6, pady=8)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        canvas = Canvas(card, height=180, bg="#FFFFFF", highlightthickness=0)
        canvas.pack(fill="x", padx=20, pady=(0, 14))
        return canvas

    def _draw_bar(self, canvas, data, x_key, y_key, color="#1A73E8"):
        canvas.delete("all")
        canvas.update_idletasks()
        W, H = canvas.winfo_width(), 180
        if not data or W < 10:
            return
        max_v = max(d[y_key] for d in data) or 1
        pad_l, pad_b, n = 40, 30, len(data)
        chart_w, chart_h = W - pad_l - 10, H - 40
        for i, d in enumerate(data):
            val = d[y_key]
            bw = (chart_w / n) * 0.6
            x  = pad_l + (i * chart_w / n) + (chart_w / n / 2)
            h  = (val / max_v) * chart_h
            canvas.create_rectangle(x - bw/2, H - pad_b - h, x + bw/2, H - pad_b, fill=color, outline="")
            canvas.create_text(x, H - pad_b + 15, text=str(d[x_key])[:6], font=("Segoe UI", 8), fill="#6B7280")
            canvas.create_text(x, H - pad_b - h - 10, text=str(val), font=("Segoe UI", 8, "bold"), fill="#1C1C1E")

    def refresh(self):
        if self.cb_revenue_by_month:
            d = self.cb_revenue_by_month("2025")
            self.after(10, lambda: self._draw_bar(self.canvas_monthly, d, "month", "revenue"))
        if self.cb_total_customers:
            self._kpi_labels["cust"].configure(text=str(self.cb_total_customers()))
        if self.cb_top_services:
            d = self.cb_top_services(5)
            self.after(10, lambda: self._draw_bar(self.canvas_svc, d, "name", "count", "#34A853"))
            if d:
                self._kpi_labels["top"].configure(text=d[0]["name"])
        if self.cb_cars_per_staff:
            d = self.cb_cars_per_staff()
            self.after(10, lambda: self._draw_bar(self.canvas_staff, d, "staff", "count", "#FF6D00"))