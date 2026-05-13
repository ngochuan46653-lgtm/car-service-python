class Car:
    def __init__(self, id=None, customer_id=None, license_plate=None,
                 brand=None, color=None, car_type=None, is_deleted=0):
        self.id = id
        self.customer_id = customer_id
        self.license_plate = license_plate
        self.brand = brand
        self.color = color
        self.car_type = car_type
        self.is_deleted = is_deleted

    def to_tuple(self):
        """Trả về tuple để insert/update vào DB"""
        return (self.customer_id, self.license_plate, self.brand,
                self.color, self.car_type, self.is_deleted)

    @staticmethod
    def from_row(row):
        """Tạo Car object từ một row trả về từ DB"""
        if not row:
            return None
        return Car(
            id=row[0],
            customer_id=row[1],
            license_plate=row[2],
            brand=row[3],
            color=row[4],
            car_type=row[5],
            is_deleted=row[6]
        )

    def __repr__(self):
        return (f"Car(id={self.id}, customer_id={self.customer_id}, "
                f"license_plate='{self.license_plate}', brand='{self.brand}', "
                f"color='{self.color}', car_type='{self.car_type}', "
                f"is_deleted={self.is_deleted})")