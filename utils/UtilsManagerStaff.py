import customtkinter as ctk
from tkinter import ttk

from services.ServiceManagerStaff import StaffService


class StaffView(ctk.CTkFrame):
    COLUMNS = [("id", "ID", 55), ("username", "Username", 150),
               ("full_name", "Họ tên", 200), ("role", "Quyền", 90)]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.cb_load = StaffService.get_all
        self.cb_add = StaffService.add
        self.cb_edit = StaffService.update
        self.cb_delete = StaffService.delete
        self._selected_id = None
        self._all_rows = []
        self._build()
        self.refresh()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        ctk.CTkLabel(hdr, text="👨‍💼 Quản lý Nhân viên", font=("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkButton(hdr, text="➕ Thêm NV", width=110, command=self._open_add).pack(side="right")

        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        self.ent_search = ctk.CTkEntry(tb, placeholder_text="🔍 Tìm tên hoặc username...", height=34)
        self.ent_search.grid(row=0, column=0, sticky="ew")
        self.ent_search.bind("<KeyRelease>", lambda e: self._filter(self.ent_search.get()))

        btn_frame = ctk.CTkFrame(tb, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(btn_frame, text="✏ Sửa", width=80, command=self._open_edit).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🗑 Xóa", width=80, fg_color="#EA4335", hover_color="#C0392B",
                      command=self._delete).pack(side="left", padx=4)

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
        return self.tree.item(sel[0])["values"] if sel else None

    def _open_add(self):
        self._show_form("Thêm nhân viên", {}, is_edit=False)

    def _open_edit(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn nhân viên!")
        self._selected_id = row[0]
        self._show_form("Sửa nhân viên", {"full_name": row[2], "role": row[3]}, is_edit=True)

    def _show_form(self, title, initial, is_edit):
        dlg = ctk.CTkToplevel(self)
        dlg.title(title)
        dlg.geometry("360x300")
        dlg.grab_set()

        widgets = {}

        if not is_edit:
            ctk.CTkLabel(dlg, text="Username *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(16, 0))
            ent = ctk.CTkEntry(dlg, height=36)
            ent.pack(fill="x", padx=24)
            widgets["username"] = ent

        ctk.CTkLabel(dlg, text="Họ và tên *", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        ent_name = ctk.CTkEntry(dlg, height=36)
        ent_name.pack(fill="x", padx=24)
        ent_name.insert(0, initial.get("full_name", ""))
        widgets["full_name"] = ent_name

        ctk.CTkLabel(dlg, text="Mật khẩu", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        ent_pass = ctk.CTkEntry(dlg, height=36, show="*")
        ent_pass.pack(fill="x", padx=24)
        widgets["password"] = ent_pass

        ctk.CTkLabel(dlg, text="Phân quyền", font=("Segoe UI", 12)).pack(anchor="w", padx=24, pady=(10, 0))
        cmb_role = ctk.CTkComboBox(dlg, values=["staff", "admin"], height=36)
        cmb_role.set(initial.get("role", "staff"))
        cmb_role.pack(fill="x", padx=24)
        widgets["role"] = cmb_role

        def submit():
            data = {k: (w.get() if hasattr(w, 'get') else w.get()) for k, w in widgets.items()}
            if not data.get("full_name", "").strip():
                return self._alert("Vui lòng nhập họ tên!")
            if not is_edit and not data.get("username", "").strip():
                return self._alert("Vui lòng nhập username!")
            try:
                if is_edit:
                    if self.cb_edit:
                        self.cb_edit(self._selected_id, data)
                else:
                    if self.cb_add:
                        self.cb_add(data)
            except Exception as e:
                return self._alert(f"Lỗi lưu nhân viên: {e}")
            self.refresh()
            dlg.destroy()

        ctk.CTkButton(dlg, text="Lưu", height=36, command=submit).pack(fill="x", padx=24, pady=14)

    def _delete(self):
        row = self._get_selected_row()
        if not row:
            return self._alert("Vui lòng chọn nhân viên!")
        self._selected_id = row[0]
        dlg = ctk.CTkToplevel(self)
        dlg.title("Xác nhận")
        dlg.geometry("280x120")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text="Xóa tài khoản nhân viên này?").pack(pady=20)
        ctk.CTkButton(dlg, text="Xóa", fg_color="#EA4335",
                      command=lambda: [self._safe_delete(),
                                       self.refresh(), dlg.destroy()]).pack()

    def _filter(self, kw):
        kw = kw.lower()
        rows = [r for r in self._all_rows if kw in str(r[1]).lower() or kw in str(r[2]).lower()] if kw else self._all_rows
        self._load_tree(rows)

    def _load_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def refresh(self):
        try:
            self._all_rows = (self.cb_load() or []) if self.cb_load else []
        except Exception as e:
            self._all_rows = []
            self._alert(f"Lỗi tải nhân viên: {e}")
        self._load_tree(self._all_rows)

    def _alert(self, msg):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Thông báo")
        dlg.geometry("280x110")
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=msg).pack(pady=20)
        ctk.CTkButton(dlg, text="Đóng", width=80, command=dlg.destroy).pack()

    def _safe_delete(self):
        try:
            if self.cb_delete:
                self.cb_delete(self._selected_id)
        except Exception as e:
            self._alert(f"Lỗi xóa nhân viên: {e}")
