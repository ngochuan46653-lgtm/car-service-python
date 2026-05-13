import customtkinter as ctk
from tkinter import ttk

from services.ServiceManagerOrder import OrderService


class OrderView(ctk.CTkFrame):
    COLUMNS = [
        ("id", "ID", 50),
        ("date", "Ngày", 120),
        ("customer", "Khách hàng", 180),
        ("car", "Xe", 130),
        ("total", "Tổng", 100),
        ("status", "Trạng thái", 100),
        ("staff", "Nhân viên", 140),
    ]

    def __init__(self, master, current_user=None, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.current_user = current_user
        self._svc = OrderService(current_user)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.cb_load = self._svc_load
        self.cb_add = self._svc_add
        self.cb_edit = self._svc_edit
        self.cb_delete = self._svc_delete
        self.cb_get_customers = self._svc_get_customers
        self.cb_get_cars = self._svc_get_cars
        self.cb_get_services = self._svc_get_services
        self._selected_id = None
        self._all_rows = []
        self._build()
        self.refresh()

    def _svc_load(self):
        return self._svc.load_orders()

    def _svc_add(self, data):
        self._svc.add_order(data)

    def _svc_edit(self, order_id, data):
        self._svc.update_order(order_id, data)

    def _svc_delete(self, order_id):
        self._svc.delete_order(order_id)

    def _svc_get_customers(self):
        return self._svc.list_customer_labels()

    def _svc_get_cars(self, customer_id):
        return self._svc.list_car_labels(customer_id)

    def _svc_get_services(self):
        return self._svc.list_services_for_combo()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="📋 Đơn dịch vụ", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btn_frame, text="➕ Thêm mới", width=110, command=self._open_add).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🔄 Làm mới", width=100, command=self.refresh).pack(side="left", padx=4)

        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        self.ent_search = ctk.CTkEntry(tb, placeholder_text="🔍 Tìm theo khách hàng hoặc xe...", height=34)
        self.ent_search.grid(row=0, column=0, sticky="ew")
        self.ent_search.bind("<KeyRelease>", lambda e: self._filter(self.ent_search.get()))

        btn_frame2 = ctk.CTkFrame(tb, fg_color="transparent")
        btn_frame2.grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(btn_frame2, text="✏ Sửa", width=80, command=self._open_edit).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_frame2,
            text="🗑 Xóa",
            width=80,
            fg_color="#EA4335",
            hover_color="#C0392B",
            command=self._delete,
        ).pack(side="left", padx=4)

        frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        frame.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=[c[0] for c in self.COLUMNS], show="headings", selectmode="browse")
        for key, label, width in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    def _load_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            r = list(row)
            if len(r) > 5:
                s = str(r[5]).strip().lower()
                r[5] = "Chưa thanh toán" if s == "pending" else ("Đã thanh toán" if s == "paid" else r[5])
            self.tree.insert("", "end", values=r)

    def _get_selected_row(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0])["values"] if sel else None

    def _open_add(self):
        self._show_form("Thêm đơn dịch vụ", {}, self._submit_add)

    def _open_edit(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn đơn!")
        try:
            self._selected_id = int(row[0])
        except (TypeError, ValueError):
            return self._alert("ID đơn không hợp lệ.")
        initial = self._svc.order_edit_map.get(
            self._selected_id,
            {"date": row[1], "customer": row[2], "car": row[3], "total": row[4], "status": row[5], "services": []},
        )
        self._show_form(
            "Sửa đơn dịch vụ",
            initial,
            self._submit_edit,
        )

    def _show_form(self, title, initial, on_submit):
        dlg = ctk.CTkToplevel(self)
        dlg.title(title)
        dlg.geometry("560x620")
        dlg.grab_set()

        services = self.cb_get_services() if self.cb_get_services else []
        if not isinstance(services, list):
            services = []

        ctk.CTkLabel(dlg, text="Ngày *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(14, 0))
        ent_date = ctk.CTkEntry(dlg, height=36, placeholder_text="DD/MM/YYYY")
        ent_date.pack(fill="x", padx=24)
        ent_date.insert(0, initial.get("date", ""))

        ctk.CTkLabel(dlg, text="Khách hàng *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        customers = self.cb_get_customers() if self.cb_get_customers else []
        cmb_cust = ctk.CTkComboBox(dlg, height=36, values=customers)
        cmb_cust.pack(fill="x", padx=24)
        if initial.get("customer"):
            cmb_cust.set(initial.get("customer"))

        ctk.CTkLabel(dlg, text="Xe *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        cmb_car = ctk.CTkComboBox(dlg, height=36, values=[])
        cmb_car.pack(fill="x", padx=24)

        def refresh_car_options():
            if not self.cb_get_cars:
                return
            customer_value = cmb_cust.get()
            customer_id = customer_value.split(" - ")[0] if " - " in customer_value else customer_value
            cars = self.cb_get_cars(customer_id) or []
            cmb_car.configure(values=cars)
            if initial.get("car"):
                cmb_car.set(initial.get("car"))
            elif cars:
                cmb_car.set(cars[0])

        refresh_car_options()
        cmb_cust.bind("<KeyRelease>", lambda e: refresh_car_options())

        ctk.CTkLabel(dlg, text="Dịch vụ *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        svc_wrap = ctk.CTkFrame(dlg, fg_color="transparent")
        svc_wrap.pack(fill="both", padx=24, pady=(4, 0))

        service_rows = []
        total_var = ctk.StringVar(value=initial.get("total", "0"))
        service_options = [f"{svc.get('id')} - {svc.get('name')}" for svc in services]

        def parse_price(service_text):
            service_id = service_text.split(" - ")[0] if " - " in service_text else service_text
            for svc in services:
                if str(svc.get("id")) == str(service_id):
                    return int(svc.get("price", 0) or 0)
            return 0

        def recalc_total():
            total = 0
            for row in service_rows:
                qty = row["qty"].get().strip() or "0"
                if qty.isdigit():
                    total += parse_price(row["service"].get()) * int(qty)
            total_var.set(str(total))

        def add_service_row(selected_service_id=None, selected_qty=1):
            row_frame = ctk.CTkFrame(svc_wrap, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)

            cmb_service = ctk.CTkComboBox(row_frame, width=300, values=service_options)
            cmb_service.pack(side="left", padx=(0, 8))
            if selected_service_id is not None:
                for opt in service_options:
                    if str(opt).startswith(f"{selected_service_id} -"):
                        cmb_service.set(opt)
                        break
            elif service_options:
                cmb_service.set(service_options[0])

            ent_qty = ctk.CTkEntry(row_frame, width=80, placeholder_text="SL")
            ent_qty.pack(side="left", padx=(0, 8))
            ent_qty.insert(0, str(selected_qty))

            def remove_row():
                row_frame.destroy()
                if row_data in service_rows:
                    service_rows.remove(row_data)
                recalc_total()

            ctk.CTkButton(row_frame, text="X", width=35, fg_color="#EA4335", command=remove_row).pack(side="left")

            row_data = {"frame": row_frame, "service": cmb_service, "qty": ent_qty}
            service_rows.append(row_data)
            cmb_service.bind("<<ComboboxSelected>>", lambda e: recalc_total())
            ent_qty.bind("<KeyRelease>", lambda e: recalc_total())
            recalc_total()

        ctk.CTkButton(dlg, text="+ Thêm dịch vụ", width=120, command=add_service_row).pack(anchor="w", padx=24, pady=(6, 0))
        initial_services = initial.get("services", []) if isinstance(initial.get("services", []), list) else []
        if initial_services:
            for item in initial_services:
                add_service_row(item.get("service_id"), item.get("qty", 1))
        else:
            add_service_row()

        ctk.CTkLabel(dlg, text="Tổng tiền (VNĐ)", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        ent_total = ctk.CTkEntry(dlg, height=36, textvariable=total_var, state="readonly")
        ent_total.pack(fill="x", padx=24)

        ctk.CTkLabel(dlg, text="Trạng thái", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        cmb_status = ctk.CTkComboBox(dlg, height=36, values=["Chưa thanh toán", "Đã thanh toán"])
        cmb_status.pack(fill="x", padx=24)
        st_cell = str(initial.get("status", "pending")).strip().lower()
        if st_cell in ("pending", "chưa thanh toán"):
            cmb_status.set("Chưa thanh toán")
        else:
            cmb_status.set("Đã thanh toán")

        def submit():
            selected_services = []
            for row in service_rows:
                service_text = row["service"].get().strip()
                qty_text = row["qty"].get().strip()
                if not service_text or not qty_text.isdigit() or int(qty_text) <= 0:
                    continue
                service_id = service_text.split(" - ")[0] if " - " in service_text else service_text
                selected_services.append({"service_id": service_id, "qty": int(qty_text)})

            st_ui = cmb_status.get().strip()
            st_db = "pending" if st_ui == "Chưa thanh toán" else "paid"
            data = {
                "date": ent_date.get().strip(),
                "customer": cmb_cust.get().strip(),
                "car": cmb_car.get().strip(),
                "services": selected_services,
                "total": total_var.get().strip(),
                "status": st_db,
                "staff": (self.current_user or {}).get("full_name", ""),
            }
            if not data["date"] or not data["customer"] or not data["car"] or not data["services"]:
                return self._alert("Vui lòng nhập đầy đủ thông tin đơn!")
            on_submit(data)
            dlg.destroy()

        ctk.CTkButton(dlg, text="Lưu", height=36, command=submit).pack(fill="x", padx=24, pady=16)

    def _submit_add(self, data):
        try:
            if self.cb_add:
                self.cb_add(data)
        except Exception as e:
            return self._alert(f"Lỗi tạo đơn: {e}")
        self.refresh()

    def _submit_edit(self, data):
        try:
            if self.cb_edit:
                self.cb_edit(self._selected_id, data)
        except Exception as e:
            return self._alert(f"Lỗi cập nhật đơn: {e}")
        self.refresh()

    def _delete(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn đơn!")
        try:
            self._selected_id = int(row[0])
        except (TypeError, ValueError):
            return self._alert("ID đơn không hợp lệ.")
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận")
        dlg.geometry("300x130")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="Xóa đơn dịch vụ này?").pack(pady=20)
        ctk.CTkButton(
            dlg,
            text="Xóa",
            fg_color="#EA4335",
            command=lambda: [self._safe_delete(), self.refresh(), dlg.destroy()],
        ).pack()

    def _filter(self, kw):
        kw = kw.lower().strip()
        rows = [r for r in self._all_rows if kw in str(r[2]).lower() or kw in str(r[3]).lower()] if kw else self._all_rows
        self._load_tree(rows)

    def _alert(self, msg):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Thông báo")
        dlg.geometry("280x110")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=msg).pack(pady=20)
        ctk.CTkButton(dlg, text="Đóng", width=80, command=dlg.destroy).pack()

    def refresh(self):
        load_fn = self.cb_load
        try:
            self._all_rows = (load_fn() or []) if load_fn else []
        except Exception as e:
            self._all_rows = []
            self._alert(f"Lỗi tải đơn dịch vụ: {e}")
        self._load_tree(self._all_rows)

    def _safe_delete(self):
        try:
            if self.cb_delete:
                self.cb_delete(self._selected_id)
        except Exception as e:
            self._alert(f"Lỗi xóa đơn: {e}")
