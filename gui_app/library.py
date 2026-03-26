import json
import os
import shutil
from datetime import datetime
from book import Book
from reader import Reader


class Library:
    DATA_FILE = "library_data.json"
    BACKUP_DIR = "backups"

    def __init__(self):
        self.books = []
        self.readers = []
        self.load_from_file()

    def add_book(self, book):
        if not Book.validate_isbn(book.isbn):
            return False, "ISBN格式错误"
        for b in self.books:
            if b.isbn == book.isbn:
                return False, f"ISBN '{book.isbn}' 已存在"
        self.books.append(book)
        self.save_to_file()
        return True, "图书添加成功"

    def update_book(self, isbn, **kwargs):
        book = self.get_book_by_isbn(isbn)
        if not book:
            return False, "未找到该图书"
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)
        self.save_to_file()
        return True, "图书信息更新成功"

    def delete_book(self, isbn):
        book = self.get_book_by_isbn(isbn)
        if not book:
            return False, "未找到该图书"
        if book.is_borrowed:
            return False, "该图书已被借出，无法下架"
        self.books = [b for b in self.books if b.isbn != isbn]
        self.save_to_file()
        return True, "图书下架成功"

    def search_book(self, keyword):
        keyword_lower = keyword.lower()
        return [b for b in self.books if keyword_lower in b.title.lower() or
                keyword_lower in b.author.lower() or keyword_lower in b.isbn or
                keyword_lower in b.publisher.lower()]

    def get_book_by_isbn(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def get_all_books(self):
        return self.books

    def add_reader(self, reader):
        for r in self.readers:
            if r.reader_id == reader.reader_id:
                return False, "读者证号已存在"
        self.readers.append(reader)
        self.save_to_file()
        return True, f"读者注册成功！初始密码：123456"

    def update_reader(self, reader_id, **kwargs):
        reader = self.get_reader(reader_id)
        if not reader:
            return False, "未找到该读者"
        for key, value in kwargs.items():
            if hasattr(reader, key):
                setattr(reader, key, value)
        self.save_to_file()
        return True, "读者信息更新成功"

    def delete_reader(self, reader_id):
        reader = self.get_reader(reader_id)
        if not reader:
            return False, "未找到该读者"
        if reader.borrowed_count > 0:
            return False, "该读者还有未归还图书，无法注销"
        self.readers = [r for r in self.readers if r.reader_id != reader_id]
        self.save_to_file()
        return True, "读者注销成功"

    def get_reader(self, reader_id):
        for reader in self.readers:
            if reader.reader_id == reader_id:
                return reader
        return None

    def get_all_readers(self):
        return self.readers

    def borrow_book(self, isbn, reader_id):
        book = self.get_book_by_isbn(isbn)
        if not book:
            return False, "未找到该图书"
        reader = self.get_reader(reader_id)
        if not reader:
            return False, "未找到该读者"
        if book.is_borrowed:
            return False, "图书已被借出"
        can_borrow, msg = reader.can_borrow()
        if not can_borrow:
            return False, msg
        success, msg = book.borrow(reader.reader_id, reader.name)
        if success:
            reader.add_borrowed_book(book.isbn, book.title)
            self.save_to_file()
            return True, msg
        return False, msg

    def return_book(self, isbn, reader_id):
        book = self.get_book_by_isbn(isbn)
        if not book:
            return False, "未找到该图书"
        reader = self.get_reader(reader_id)
        if not reader:
            return False, "未找到该读者"
        if not book.is_borrowed:
            return False, "图书未被借出"
        if book.borrower_id != reader_id:
            return False, "借阅人信息不匹配"
        success, overdue_days, msg = book.return_book()
        if success:
            reader.remove_borrowed_book(isbn, overdue_days)
            self.save_to_file()
            if overdue_days > 0:
                return True, f"{msg}，罚款 ¥{overdue_days * 0.5:.2f}"
            return True, msg
        return False, msg

    def renew_book(self, isbn, reader_id):
        book = self.get_book_by_isbn(isbn)
        if not book:
            return False, "未找到该图书"
        if not book.is_borrowed:
            return False, "图书未被借出"
        if book.borrower_id != reader_id:
            return False, "借阅人信息不匹配"
        success, msg = book.renew()
        if success:
            self.save_to_file()
            return True, msg
        return False, msg

    def get_borrowed_books(self):
        return [b for b in self.books if b.is_borrowed]

    def get_reader_borrow_history(self, reader_id):
        reader = self.get_reader(reader_id)
        return reader.borrow_history if reader else []

    def get_stats(self):
        total_books = len(self.books)
        borrowed_books = sum(1 for b in self.books if b.is_borrowed)
        available_books = total_books - borrowed_books
        total_readers = len(self.readers)
        active_readers = sum(1 for r in self.readers if r.is_active)
        total_fine = sum(r.fine for r in self.readers)

        category_stats = {}
        for book in self.books:
            cat = book.category
            category_stats[cat] = category_stats.get(cat, 0) + 1

        borrow_count = {}
        for book in self.books:
            borrow_count[book.title] = len(book.borrow_history)
        top_books = sorted(borrow_count.items(), key=lambda x: x[1], reverse=True)[:10]

        reader_stats = [{'name': r.name, 'borrow_count': r.total_borrow, 'fine': r.fine} for r in self.readers]
        top_readers = sorted(reader_stats, key=lambda x: x['borrow_count'], reverse=True)[:10]

        return {
            'total_books': total_books, 'borrowed_books': borrowed_books,
            'available_books': available_books, 'total_readers': total_readers,
            'active_readers': active_readers, 'total_fine': total_fine,
            'category_stats': category_stats, 'top_books': top_books, 'top_readers': top_readers
        }

    def backup_data(self):
        if not os.path.exists(self.BACKUP_DIR):
            os.makedirs(self.BACKUP_DIR)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.BACKUP_DIR, f"backup_{timestamp}.json")
        shutil.copy(self.DATA_FILE, backup_file)
        return backup_file

    def get_backup_list(self):
        if not os.path.exists(self.BACKUP_DIR):
            return []
        return [f for f in os.listdir(self.BACKUP_DIR) if f.endswith('.json')]

    def restore_backup(self, backup_file):
        full_path = os.path.join(self.BACKUP_DIR, backup_file)
        if not os.path.exists(full_path):
            return False, "备份文件不存在"
        shutil.copy(full_path, self.DATA_FILE)
        self.load_from_file()
        return True, "数据恢复成功"

    def save_to_file(self):
        data = {'books': [b.to_dict() for b in self.books], 'readers': [r.to_dict() for r in self.readers]}
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self):
        if not os.path.exists(self.DATA_FILE):
            self._init_sample_data()
            return
        with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.books = [Book.from_dict(item) for item in data.get('books', [])]
        self.readers = [Reader.from_dict(item) for item in data.get('readers', [])]

    def _init_sample_data(self):
        sample_books = [
            Book("三体：黑暗森林", "刘慈欣", "978-7-5366-9293-5", "重庆出版社", "2008-01-01", "文学"),
            Book("三体：死神永生", "刘慈欣", "978-7-229-02271-6", "重庆出版社", "2010-11-01", "文学"),
            Book("平凡的世界", "路遥", "978-7-02-009675-2", "人民文学出版社", "2012-03-01", "文学"),
            Book("活着", "余华", "978-7-5063-5540-1", "作家出版社", "2012-08-01", "文学"),
            Book("Python编程：从入门到实践", "Eric Matthes", "978-7-115-42986-5", "人民邮电出版社", "2016-07-01",
                 "编程"),
            Book("算法导论", "Thomas H. Cormen", "978-7-111-23461-6", "机械工业出版社", "2013-01-01", "编程"),
            Book("人类简史", "尤瓦尔·赫拉利", "978-7-5086-6097-6", "中信出版社", "2017-02-01", "历史"),
            Book("思考，快与慢", "丹尼尔·卡尼曼", "978-7-5086-3355-0", "中信出版社", "2012-07-01", "心理"),
        ]
        self.books = sample_books

        sample_readers = [
            Reader("20240001", "陈明远", "男", "13812345678", "chenmingyuan@email.com", "北京市海淀区"),
            Reader("20240002", "林婉清", "女", "13987654321", "linwanqing@email.com", "上海市浦东新区"),
            Reader("20240003", "张书豪", "男", "18612345678", "zhangshuhao@email.com", "广州市天河区"),
        ]
        self.readers = sample_readers
        self.save_to_file()