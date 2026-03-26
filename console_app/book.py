class Book:
    def __init__(self, title, author, isbn):
        """初始化图书信息"""
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False  # False表示可借阅

    def borrow(self):
        """借出图书，成功返回True，失败返回False"""
        if not self.is_borrowed:
            self.is_borrowed = True
            return True
        return False

    def return_book(self):
        """归还图书，成功返回True，失败返回False"""
        if self.is_borrowed:
            self.is_borrowed = False
            return True
        return False

    def get_info(self):
        """返回格式化的图书信息"""
        status = "可借阅" if not self.is_borrowed else "已借出"
        return f"{self.title} - {self.author} (ISBN:{self.isbn}) [{status}]"