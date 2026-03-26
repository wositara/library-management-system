from datetime import datetime, timedelta


class Reader:
    def __init__(self, reader_id, name, gender="男", phone="", email="", address=""):
        self.reader_id = reader_id
        self.name = name
        self.gender = gender
        self.phone = phone
        self.email = email
        self.address = address
        self.register_date = datetime.now().strftime("%Y-%m-%d")
        self.is_active = True
        self.borrowed_count = 0
        self.total_borrow = 0
        self.fine = 0.0
        self.password = "123456"
        self.borrow_history = []

    def can_borrow(self):
        if not self.is_active:
            return False, "账户已冻结"
        if self.borrowed_count >= 5:
            return False, f"最多借5本，当前已借{self.borrowed_count}本"
        if self.fine > 0:
            return False, f"存在未缴罚款 ¥{self.fine:.2f}"
        return True, "可以借阅"

    def add_borrowed_book(self, isbn, title):
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.borrowed_count += 1
        self.total_borrow += 1
        self.borrow_history.append({
            'isbn': isbn, 'title': title,
            'borrow_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'due_date': due_date, 'return_date': None, 'fine': 0.0
        })

    def remove_borrowed_book(self, isbn, overdue_days=0):
        for i, book in enumerate(self.borrow_history):
            if book['isbn'] == isbn and book['return_date'] is None:
                book['return_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if overdue_days > 0:
                    fine = overdue_days * 0.5
                    book['fine'] = fine
                    self.fine += fine
                break
        self.borrowed_count = max(0, self.borrowed_count - 1)

    def pay_fine(self, amount):
        if amount > self.fine:
            amount = self.fine
        self.fine -= amount
        return amount

    def get_overdue_books(self):
        overdue = []
        now = datetime.now()
        for book in self.borrow_history:
            if book['return_date'] is None:
                due_date = datetime.strptime(book['due_date'], "%Y-%m-%d")
                if due_date < now:
                    days = (now - due_date).days
                    book['overdue_days'] = days
                    overdue.append(book)
        return overdue

    def to_dict(self):
        return {
            'reader_id': self.reader_id, 'name': self.name, 'gender': self.gender,
            'phone': self.phone, 'email': self.email, 'address': self.address,
            'register_date': self.register_date, 'is_active': self.is_active,
            'borrowed_count': self.borrowed_count, 'total_borrow': self.total_borrow,
            'fine': self.fine, 'password': self.password, 'borrow_history': self.borrow_history
        }

    @classmethod
    def from_dict(cls, data):
        reader = cls(data['reader_id'], data['name'], data.get('gender', '男'),
                     data.get('phone', ''), data.get('email', ''), data.get('address', ''))
        reader.register_date = data.get('register_date', datetime.now().strftime("%Y-%m-%d"))
        reader.is_active = data.get('is_active', True)
        reader.borrowed_count = data.get('borrowed_count', 0)
        reader.total_borrow = data.get('total_borrow', 0)
        reader.fine = data.get('fine', 0.0)
        reader.password = data.get('password', '123456')
        reader.borrow_history = data.get('borrow_history', [])
        return reader