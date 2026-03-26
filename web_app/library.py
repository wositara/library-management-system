import json
import os
from book import Book


class Library:
    DATA_FILE = "books.json"

    def __init__(self):
        self.books = []
        self.load_from_file()

    def add_book(self, book):
        """添加图书（book是Book对象）"""
        for b in self.books:
            if b.isbn == book.isbn:
                return False
        self.books.append(book)
        self.save_to_file()
        return True

    def show_all_books(self):
        if not self.books:
            return "暂无图书"
        result = []
        for i, book in enumerate(self.books, 1):
            result.append(f"{i}. {book.get_info()}")
        return "\n".join(result)

    def search_book(self, keyword):
        keyword_lower = keyword.lower()
        results = []
        for book in self.books:
            if keyword_lower in book.title.lower() or keyword_lower in book.author.lower():
                results.append(book.get_info())
        return results

    def borrow_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                if book.borrow():
                    self.save_to_file()
                    return True
                return False
        return False

    def return_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                if book.return_book():
                    self.save_to_file()
                    return True
                return False
        return False

    def get_borrowed_books(self):
        borrowed = [book.get_info() for book in self.books if book.is_borrowed]
        return borrowed if borrowed else None

    def save_to_file(self):
        data = []
        for book in self.books:
            data.append({
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'is_borrowed': book.is_borrowed
            })
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self):
        if not os.path.exists(self.DATA_FILE):
            # 添加示例数据
            self.books = [
                Book("Python编程入门", "张三", "978-7-121-12345-6"),
                Book("算法导论", "李四", "978-7-302-23456-7"),
                Book("数据结构", "王五", "978-7-111-34567-8"),
            ]
            self.save_to_file()
            return

        with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.books = []
        for item in data:
            book = Book(item['title'], item['author'], item['isbn'])
            if item['is_borrowed']:
                book.borrow()
            self.books.append(book)