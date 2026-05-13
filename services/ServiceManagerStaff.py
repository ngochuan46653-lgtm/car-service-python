import hashlib
from datetime import datetime

from repositories.RepositoriesManagerStaff import RepositoriesManagerStaff


class StaffService:
    @staticmethod
    def get_all():
        return RepositoriesManagerStaff.list_all_rows()

    @staticmethod
    def add(data):
        username = data.get("username", "").strip()
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "staff")
        password = data.get("password", "").strip()
        if RepositoriesManagerStaff.username_exists(username):
            raise ValueError("Username đã tồn tại!")
        RepositoriesManagerStaff.insert(username, password, full_name, role)

    @staticmethod
    def update(staff_id, data):
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "staff")
        password = data.get("password", "").strip()
        RepositoriesManagerStaff.update(staff_id, full_name, role, password)

    @staticmethod
    def delete(staff_id):
        RepositoriesManagerStaff.delete(staff_id)


class StaffManager:
    def __init__(self, initial_staff=None):
        self._staff = []
        self._next_id = 1
        if initial_staff:
            for staff in initial_staff:
                self.add_staff(staff)

    def list_staff(self):
        return [self._to_public_record(staff) for staff in self._staff]

    def get_staff(self, staff_id):
        return next((staff for staff in self._staff if staff['id'] == staff_id), None)

    def find_by_username(self, username):
        return next((staff for staff in self._staff if staff['username'] == username), None)

    def add_staff(self, data):
        username = str(data.get('username', '')).strip()
        full_name = str(data.get('full_name', '')).strip()
        password = str(data.get('password', '')).strip()
        role = str(data.get('role', 'staff')).strip().lower() or 'staff'
        if not username:
            raise ValueError('Username không được để trống')
        if self.find_by_username(username):
            raise ValueError('Username đã tồn tại')
        if not password:
            raise ValueError('Password không được để trống')
        if role not in ('admin', 'staff'):
            raise ValueError('Role phải là admin hoặc staff')
        staff = {
            'id': self._next_id,
            'username': username,
            'password': self._hash_password(password),
            'full_name': full_name,
            'role': role,
            'created_at': datetime.now().isoformat(),
        }
        self._staff.append(staff)
        self._next_id += 1
        return self._to_public_record(staff)

    def update_staff(self, staff_id, data):
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError('Nhân viên không tồn tại')
        if 'username' in data and str(data.get('username')).strip() != staff['username']:
            raise ValueError('Không thể thay đổi username')
        full_name = str(data.get('full_name', staff['full_name'])).strip()
        role = str(data.get('role', staff['role'])).strip().lower() or staff['role']
        password = str(data.get('password', '')).strip()
        if not full_name:
            raise ValueError('Họ tên không được để trống')
        if role not in ('admin', 'staff'):
            raise ValueError('Role phải là admin hoặc staff')
        staff['full_name'] = full_name
        staff['role'] = role
        if password:
            staff['password'] = self._hash_password(password)
        return self._to_public_record(staff)

    def delete_staff(self, staff_id):
        if not self.get_staff(staff_id):
            raise ValueError('Nhân viên không tồn tại')
        self._staff = [s for s in self._staff if s['id'] != staff_id]
        return True

    def _hash_password(self, raw_password):
        return hashlib.sha256(raw_password.encode('utf-8')).hexdigest()

    def _to_public_record(self, staff):
        return {
            'id': staff['id'],
            'username': staff['username'],
            'full_name': staff['full_name'],
            'role': staff['role'],
            'created_at': staff['created_at'],
        }
