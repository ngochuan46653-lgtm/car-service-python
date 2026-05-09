class Customer:
    def __init__(self, id, name, phone, is_deleted=0, created_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.is_deleted = is_deleted
        self.created_at = created_at