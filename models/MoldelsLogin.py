class User:
    def __init__(self, id, username, password, full_name, role, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role
        self.created_at = created_at

