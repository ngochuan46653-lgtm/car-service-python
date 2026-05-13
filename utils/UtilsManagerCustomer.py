import customtkinter as ctk
from tkinter import ttk
from services.ServiceManagerCustomer import CustomerService 

class CustomerView(ctk.CTkFrame):
    COLUMNS = [("id", "ID", 60), ("name", "Họ tên", 220), ("phone", "SĐT", 160), ("cars", "Số xe", 80)]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._selected_id = None
        self._all_rows = []
        self.cb_load   = CustomerService.get_all
        self.cb_add    = lambda data: CustomerService.add(data)
        self.cb_edit   = lambda cid, data: CustomerService.update(cid, data)
        self.cb_delete = lambda cid: CustomerService.delete(cid)

        self._build()
        self.refresh() 

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        ctk.CTkLabel(hdr, text="👤 Quản lý Khách hàng", font=("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkButton(hdr, text="➕ Thêm mới", width=110, command=self._open_add).pack(side="right")

        # Toolbar
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        self.ent_search = ctk.CTkEntry(tb, placeholder_text="🔍 Tìm theo tên, SĐT...", height=34)
        self.ent_search.grid(row=0, column=0, sticky="ew")
        self.ent_search.bind("<KeyRelease>", lambda e: self._filter(self.ent_search.get()))

        btn_frame = ctk.CTkFrame(tb, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(btn_frame, text="✏ Sửa", width=80, command=self._open_edit).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🗑 Xóa", width=80, fg_color="#EA4335", hover_color="#C0392B",
                      command=self._delete).pack(side="left", padx=4)

        # Table
        frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        frame.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=[c[0] for c in self.COLUMNS],
                                 show="headings", selectmode="browse")
        for key, label, w in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=w, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    def _get_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"]

    def _open_add(self):
        self._show_form("Thêm khách hàng", {}, self._submit_add)

    def _open_edit(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn khách hàng!")
        self._selected_id = row[0]
        self._show_form("Sửa thông tin", {"name": row[1], "phone": str(row[2])}, self._submit_edit)

    def _show_form(self, title, initial, on_submit):
        dlg = ctk.CTkToplevel(self)
        dlg.title(title)
        dlg.geometry("360x240")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Họ và tên *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(16, 0))
        ent_name = ctk.CTkEntry(dlg, height=36)
        ent_name.pack(fill="x", padx=24)
        ent_name.insert(0, initial.get("name", ""))

        ctk.CTkLabel(dlg, text="Số điện thoại *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        ent_phone = ctk.CTkEntry(dlg, height=36)
        ent_phone.pack(fill="x", padx=24)
        ent_phone.insert(0, initial.get("phone", ""))

        def submit():
            on_submit({"name": ent_name.get().strip(), "phone": ent_phone.get().strip()})
            dlg.destroy()

        ctk.CTkButton(dlg, text="Lưu", height=36, command=submit).pack(fill="x", padx=24, pady=16)

    def _submit_add(self, data):
        if self.cb_add:
            self.cb_add(data)
        self.refresh()

    def _submit_edit(self, data):
        if self.cb_edit:
            self.cb_edit(self._selected_id, data)
        self.refresh()

    def _delete(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn khách hàng!")
        self._selected_id = row[0]
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận")
        dlg.geometry("300x130")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="Xóa khách hàng này?").pack(pady=20)
        ctk.CTkButton(dlg, text="Xóa", fg_color="#EA4335",
                      command=lambda: [self.cb_delete(self._selected_id) if self.cb_delete else None,
                                       self.refresh(), dlg.destroy()]).pack()

    def _filter(self, kw):
        kw = kw.lower().strip()
        rows = [r for r in self._all_rows if kw in str(r[1]).lower() or kw in str(r[2]).lower()] if kw else self._all_rows
        self._load_tree(rows)

    def _load_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def refresh(self):
        self._all_rows = (self.cb_load() or []) if self.cb_load else []
        self._load_tree(self._all_rows)

    def _alert(self, msg):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Thông báo")
        dlg.geometry("280x110")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=msg).pack(pady=20)
        ctk.CTkButton(dlg, text="Đóng", width=80, command=dlg.destroy).pack()
