import re
from datetime import datetime, timedelta


class Book:
    CATEGORIES = ['编程', '文学', '历史', '科学', '哲学', '艺术', '经济', '管理', '心理', '教育']

    def __init__(self, title, author, isbn, publisher="", publish_date="", category="编程"):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.publish_date = publish_date
        self.category = category
        self.is_borrowed = False
        self.borrower_id = None
        self.borrower_name = None
        self.borrow_date = None
        self.due_date = None
        self.borrow_history = []
        self.renewal_count = 0

    @staticmethod
    def validate_isbn(isbn):
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        if re.match(r'^978\d{10}$|^979\d{10}$', isbn_clean):
            return True
        if re.match(r'^\d{9}[\dX]$', isbn_clean):
            return True
        return False

    def borrow(self, reader_id, reader_name):
        if self.is_borrowed:
            return False, "图书已被借出"
        self.is_borrowed = True
        self.borrower_id = reader_id
        self.borrower_name = reader_name
        self.borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.renewal_count = 0
        self.borrow_history.append({
            'reader_id': reader_id, 'reader_name': reader_name,
            'borrow_date': self.borrow_date, 'due_date': self.due_date, 'return_date': None
        })
        return True, f"借书成功！应还日期：{self.due_date}"

    def renew(self):
        if not self.is_borrowed:
            return False, "图书未被借出"
        if self.renewal_count >= 1:
            return False, "已达到最大续借次数（1次）"
        if self.due_date and datetime.now() > datetime.strptime(self.due_date, "%Y-%m-%d"):
            return False, "图书已逾期，无法续借"
        new_due = datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(days=15)
        self.due_date = new_due.strftime("%Y-%m-%d")
        self.renewal_count += 1
        return True, f"续借成功！新应还日期：{self.due_date}"

    def return_book(self):
        if not self.is_borrowed:
            return False, 0, "图书未被借出"
        self.is_borrowed = False
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        overdue_days = 0
        if self.due_date:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            now = datetime.now()
            if now > due:
                overdue_days = (now - due).days
        if self.borrow_history:
            self.borrow_history[-1]['return_date'] = return_date
        self.borrower_id = None
        self.borrower_name = None
        self.borrow_date = None
        self.due_date = None
        self.renewal_count = 0
        return True, overdue_days, f"还书成功！{'逾期' + str(overdue_days) + '天' if overdue_days > 0 else '按时归还'}"

    def to_dict(self):
        return {
            'title': self.title, 'author': self.author, 'isbn': self.isbn,
            'publisher': self.publisher, 'publish_date': self.publish_date,
            'category': self.category,
            'is_borrowed': self.is_borrowed, 'borrower_id': self.borrower_id,
            'borrower_name': self.borrower_name, 'borrow_date': self.borrow_date,
            'due_date': self.due_date, 'borrow_history': self.borrow_history,
            'renewal_count': self.renewal_count
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(data['title'], data['author'], data['isbn'],
                   data.get('publisher', ''), data.get('publish_date', ''),
                   data.get('category', '编程'))
        book.is_borrowed = data.get('is_borrowed', False)
        book.borrower_id = data.get('borrower_id')
        book.borrower_name = data.get('borrower_name')
        book.borrow_date = data.get('borrow_date')
        book.due_date = data.get('due_date')
        book.borrow_history = data.get('borrow_history', [])
        book.renewal_count = data.get('renewal_count', 0)
        return book