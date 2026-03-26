import json
import os
from book import Book


class Library:
    DATA_FILE = "books.json"  # 数据存储文件

    def __init__(self):
        """初始化图书馆，尝试加载已有数据"""
        self.books = []
        self.load_from_file()

    def add_book(self, book):
        """添加图书（book是Book对象）"""
        # 检查ISBN是否重复
        for b in self.books:
            if b.isbn == book.isbn:
                return False
        self.books.append(book)
        self.save_to_file()
        return True

    def show_all_books(self):
        """显示所有图书，返回字符串"""
        if not self.books:
            return "📚 图书馆暂无图书"

        result = ["📚 图书列表：", "-" * 50]
        for i, book in enumerate(self.books, 1):
            result.append(f"{i:2d}. {book.get_info()}")
        result.append("-" * 50)
        result.append(f"总计：{len(self.books)} 本图书")
        return "\n".join(result)

    def search_book(self, keyword):
        """根据关键词搜索（书名或作者，不区分大小写）"""
        keyword_lower = keyword.lower()
        results = []
        for book in self.books:
            if keyword_lower in book.title.lower() or keyword_lower in book.author.lower():
                results.append(book.get_info())
        return results

    def borrow_book(self, isbn):
        """根据ISBN借书，成功返回True，失败返回False"""
        for book in self.books:
            if book.isbn == isbn:
                if book.borrow():
                    self.save_to_file()
                    return True
                return False
        return False

    def return_book(self, isbn):
        """根据ISBN还书，成功返回True，失败返回False"""
        for book in self.books:
            if book.isbn == isbn:
                if book.return_book():
                    self.save_to_file()
                    return True
                return False
        return False

    def show_borrowed_books(self):
        """显示所有已借出的图书"""
        borrowed = [book.get_info() for book in self.books if book.is_borrowed]
        if not borrowed:
            return "📖 暂无已借出的图书"
        result = ["📖 已借出图书：", "-" * 50]
        for i, book_info in enumerate(borrowed, 1):
            result.append(f"{i:2d}. {book_info}")
        result.append("-" * 50)
        result.append(f"共 {len(borrowed)} 本已借出")
        return "\n".join(result)

    def save_to_file(self):
        """保存数据到JSON文件"""
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
        """从JSON文件加载数据"""
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