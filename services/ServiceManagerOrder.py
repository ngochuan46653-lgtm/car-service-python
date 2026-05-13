from datetime import date, datetime

from repositories.RepositoriesManagerOrder import RepositoriesManagerOrder
from repositories.RepositoriesManagerServeces import RepositoriesManagerServeces
from repositories.RepositoriesManagerStaff import RepositoriesManagerStaff


class OrderService:
    def __init__(self, current_user=None):
        self.current_user = current_user
        self._order_edit_map = {}

    def set_current_user(self, user):
        self.current_user = user

    @staticmethod
    def _parse_linked_id(raw, label_vi):
        s = str(raw or "").strip()
        if not s:
            raise ValueError(f"Vui lòng chọn {label_vi}.")
        head = s.split(" - ", 1)[0].strip()
        if head.isdigit():
            return int(head)
        raise ValueError(
            f'{label_vi} không hợp lệ — chọn dòng dạng "mã - tên" (đang nhận: {s[:80]}).'
        )

    @staticmethod
    def format_money(value):
        try:
            return f"{int(value):,}"
        except Exception:
            return "0"

    @staticmethod
    def _format_order_date_display(val):
        """DD/MM/YYYY trên lưới — không dùng DATE_FORMAT trong SQL (lỗi % với connector)."""
        if val is None:
            return ""
        if isinstance(val, date):
            return val.strftime("%d/%m/%Y")
        s = str(val).strip()
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            try:
                return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                return s
        return s

    def _price_map(self):
        return {
            str(r[0]): int(r[2])
            for r in RepositoriesManagerServeces.list_services_price_rows()
        }

    def calc_total(self, services_items):
        price_map = self._price_map()
        total = 0
        for item in services_items:
            qty = int(item.get("qty", 0) or 0)
            total += qty * price_map.get(str(item.get("service_id")), 0)
        return total

    def _detail_rows_for_db(self, services_items):
        price_map = self._price_map()
        rows = []
        for item in services_items:
            service_id = int(item["service_id"])
            qty = int(item["qty"])
            price = price_map.get(str(service_id), 0)
            subtotal = qty * price
            rows.append((service_id, qty, price, subtotal))
        return rows

    def _resolve_user_id(self):
        if self.current_user and self.current_user.get("id"):
            return self.current_user.get("id")
        return RepositoriesManagerStaff.get_first_admin_id()

    def load_orders(self):
        self._order_edit_map = {}
        rows_out = []
        for r in RepositoriesManagerOrder.list_orders_join():
            order_id = int(r[0])
            details = RepositoriesManagerOrder.list_order_detail_pairs(order_id)
            detail_dicts = [{"service_id": int(d[0]), "qty": int(d[1])} for d in details]
            date_disp = self._format_order_date_display(r[1])
            status_raw = r[7]
            status_key = str(status_raw).strip().lower() if status_raw is not None else "pending"
            self._order_edit_map[order_id] = {
                "date": date_disp,
                "customer": f"{r[2]} - {r[3]}",
                "car": f"{r[4]} - {r[5]}",
                "total": str(int(r[6])),
                "status": status_key,
                "services": detail_dicts,
            }
            rows_out.append(
                [
                    order_id,
                    date_disp,
                    r[3],
                    r[5],
                    self.format_money(r[6]),
                    r[7],
                    r[8],
                ]
            )
        return rows_out

    @property
    def order_edit_map(self):
        return self._order_edit_map

    def list_services_for_combo(self):
        return [
            {"id": r[0], "name": r[1], "price": int(r[2])}
            for r in RepositoriesManagerServeces.list_services_price_rows()
        ]

    def list_customer_labels(self):
        return RepositoriesManagerOrder.select_customer_labels()

    def list_car_labels(self, customer_id):
        return RepositoriesManagerOrder.select_car_labels(customer_id)

    def add_order(self, data):
        services = data.get("services", [])
        customer_id = self._parse_linked_id(data.get("customer"), "khách hàng")
        car_id = self._parse_linked_id(data.get("car"), "xe")
        total = self.calc_total(services)
        user_id = self._resolve_user_id()
        order_date = data.get("date", "").strip()
        detail_rows = self._detail_rows_for_db(services)
        RepositoriesManagerOrder.insert_order_with_details(
            customer_id,
            car_id,
            user_id,
            order_date if order_date else None,
            total,
            data.get("status", "pending"),
            detail_rows,
        )

    def update_order(self, order_id, data):
        services = data.get("services", [])
        customer_id = self._parse_linked_id(data.get("customer"), "khách hàng")
        car_id = self._parse_linked_id(data.get("car"), "xe")
        total = self.calc_total(services)
        order_date = data.get("date", "").strip()
        detail_rows = self._detail_rows_for_db(services)
        RepositoriesManagerOrder.update_order_with_details(
            int(order_id),
            customer_id,
            car_id,
            order_date if order_date else None,
            total,
            data.get("status", "pending"),
            detail_rows,
        )

    def delete_order(self, order_id):
        RepositoriesManagerOrder.delete_order_cascade(int(order_id))


class OrderManager:
    def __init__(self, initial_orders=None):
        self._orders = []
        self._next_id = 1
        if initial_orders:
            for order in initial_orders:
                self._orders.append(order)
                self._next_id = max(self._next_id, order.get('id', 0) + 1)

    def list_orders(self):
        return [self._to_summary(order) for order in self._orders]

    def get_order(self, order_id):
        return next((order for order in self._orders if order['id'] == order_id), None)

    def create_order(self, customer, car, service_items, staff):
        if not customer or not customer.get('id'):
            raise ValueError('Khách hàng không hợp lệ')
        if not car or not car.get('id'):
            raise ValueError('Xe không hợp lệ')
        if not staff or not staff.get('id'):
            raise ValueError('Nhân viên không hợp lệ')
        if not service_items or not isinstance(service_items, list):
            raise ValueError('Vui lòng chọn ít nhất một dịch vụ')

        items = [self._normalize_item(item) for item in service_items]
        total = sum(item['price'] * item['quantity'] for item in items)
        if total < 0:
            raise ValueError('Tổng tiền không hợp lệ')

        order = {
            'id': self._next_id,
            'customer_id': customer['id'],
            'customer_name': customer.get('name', ''),
            'car_id': car['id'],
            'car_plate': car.get('plate', ''),
            'service_items': items,
            'total_price': total,
            'staff_id': staff['id'],
            'staff_name': staff.get('full_name', staff.get('username', '')),
            'created_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'status': 'pending',
        }
        self._orders.append(order)
        self._next_id += 1
        return self._to_detail(order)

    def delete_order(self, order_id):
        order = self.get_order(order_id)
        if not order:
            raise ValueError('Đơn hàng không tồn tại')
        self._orders = [o for o in self._orders if o['id'] != order_id]
        return True

    def calculate_total(self, service_items):
        items = [self._normalize_item(item) for item in service_items]
        return sum(item['price'] * item['quantity'] for item in items)

    def _normalize_item(self, item):
        if not isinstance(item, dict):
            raise ValueError('Dữ liệu dịch vụ không hợp lệ')
        service_id = int(item.get('service_id'))
        quantity = int(item.get('quantity', 1))
        price = float(item.get('price', 0))
        if quantity <= 0:
            raise ValueError('Số lượng phải lớn hơn 0')
        if price < 0:
            raise ValueError('Giá dịch vụ không hợp lệ')
        return {
            'service_id': service_id,
            'service_name': str(item.get('service_name', '')).strip(),
            'price': price,
            'quantity': quantity,
            'amount': price * quantity,
        }

    def _to_summary(self, order):
        return {
            'id': order['id'],
            'created_at': order['created_at'],
            'customer_name': order['customer_name'],
            'car_plate': order['car_plate'],
            'total_price': order['total_price'],
            'status': order.get('status', 'pending'),
            'staff_name': order['staff_name'],
        }

    def _to_detail(self, order):
        detail = self._to_summary(order)
        detail['customer_id'] = order['customer_id']
        detail['car_id'] = order['car_id']
        detail['service_items'] = [item.copy() for item in order['service_items']]
        return detail
