import customtkinter as ctk
from tkinter import ttk


class CarView(ctk.CTkFrame):
    COLUMNS = [
        ("id", "ID", 60),
        ("owner", "Chủ xe", 180),
        ("plate", "Biển số", 120),
        ("brand", "Hãng", 120),
        ("color", "Màu", 100),
        ("type", "Loại", 100),
    ]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F0F2F5", **kwargs)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.cb_load = None
        self.cb_get_customers = None
        self._all_rows = []
        self._build()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="🚗 Quản lý Xe", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="🔄 Làm mới", width=100, command=self.refresh).grid(row=0, column=1, sticky="e")

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
            self.tree.insert("", "end", values=row)

    def refresh(self):
        self._all_rows = (self.cb_load() or []) if self.cb_load else []
        self._load_tree(self._all_rows)
