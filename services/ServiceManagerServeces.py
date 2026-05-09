import hashlib
from datetime import datetime


class ServiceManager:
    def __init__(self, initial_services=None):
        self._services = []
        self._next_id = 1
        if initial_services:
            for svc in initial_services:
                self.add_service(svc)

    def list_services(self):
        return [svc.copy() for svc in self._services]

    def get_service(self, service_id):
        return next((svc for svc in self._services if svc['id'] == service_id), None)

    def add_service(self, data):
        name = str(data.get('name', '')).strip()
        price = self._parse_price(data.get('price', 0))
        if not name:
            raise ValueError('Tên dịch vụ không được để trống')
        if price < 0:
            raise ValueError('Giá dịch vụ phải lớn hơn hoặc bằng 0')
        service = {
            'id': self._next_id,
            'name': name,
            'price': price,
            'created_at': datetime.now().isoformat(),
        }
        self._services.append(service)
        self._next_id += 1
        return service.copy()

    def update_service(self, service_id, data):
        service = self.get_service(service_id)
        if service is None:
            raise ValueError('Dịch vụ không tồn tại')
        name = str(data.get('name', service['name'])).strip()
        price = self._parse_price(data.get('price', service['price']))
        if not name:
            raise ValueError('Tên dịch vụ không được để trống')
        if price < 0:
            raise ValueError('Giá dịch vụ phải lớn hơn hoặc bằng 0')
        service['name'] = name
        service['price'] = price
        return service.copy()

    def delete_service(self, service_id):
        service = self.get_service(service_id)
        if service is None:
            raise ValueError('Dịch vụ không tồn tại')
        self._services = [svc for svc in self._services if svc['id'] != service_id]
        return True

    def _parse_price(self, price):
        if isinstance(price, str):
            value = price.replace(',', '').strip()
            try:
                return int(value)
            except ValueError:
                return float(value)
        return int(price)
