from datetime import datetime


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
