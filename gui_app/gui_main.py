import tkinter as tk
from tkinter import ttk, messagebox
from library import Library
from book import Book


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图书管理系统")
        self.root.geometry("900x550")
        self.root.resizable(True, True)

        # 设置样式
        self.setup_style()

        self.lib = Library()
        self.create_widgets()
        self.refresh()

    def setup_style(self):
        """设置现代化样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置Treeview样式
        style.configure("Treeview",
                        font=('微软雅黑', 10),
                        rowheight=32,
                        background='white',
                        fieldbackground='white')
        style.configure("Treeview.Heading",
                        font=('微软雅黑', 10, 'bold'),
                        background='#f1f5f9',
                        foreground='#1e293b')
        style.map("Treeview.Heading",
                  background=[('active', '#e2e8f0')])

    def create_widgets(self):
        # 主容器
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill='both', expand=True)

        # 标题
        title = ttk.Label(main, text="📚 图书管理系统",
                          font=('微软雅黑', 18, 'bold'))
        title.pack(anchor='w', pady=(0, 20))

        # 添加图书区域
        add_frame = ttk.LabelFrame(main, text="添加新书", padding="15")
        add_frame.pack(fill='x', pady=(0, 20))

        # 表单行
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')

        ttk.Label(form_frame, text="书名").grid(row=0, column=0, padx=(0, 8), sticky='w')
        self.title_entry = ttk.Entry(form_frame, width=20)
        self.title_entry.grid(row=1, column=0, padx=(0, 15), sticky='w')

        ttk.Label(form_frame, text="作者").grid(row=0, column=1, padx=(0, 8), sticky='w')
        self.author_entry = ttk.Entry(form_frame, width=20)
        self.author_entry.grid(row=1, column=1, padx=(0, 15), sticky='w')

        ttk.Label(form_frame, text="ISBN").grid(row=0, column=2, padx=(0, 8), sticky='w')
        self.isbn_entry = ttk.Entry(form_frame, width=20)
        self.isbn_entry.grid(row=1, column=2, padx=(0, 15), sticky='w')

        ttk.Button(form_frame, text="+ 添加图书",
                   command=self.add_book).grid(row=1, column=3, padx=(10, 0))

        # 操作按钮栏
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill='x', pady=(0, 15))

        ttk.Button(btn_frame, text="🔍 搜索",
                   command=self.search_book, width=12).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="📖 查看已借出",
                   command=self.show_borrowed, width=12).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="🔄 刷新",
                   command=self.refresh, width=12).pack(side='left')

        # 图书列表表格
        columns = ('序号', '书名', '作者', 'ISBN', '状态')
        self.tree = ttk.Treeview(main, columns=columns, show='headings', height=12)

        # 设置列
        widths = [50, 250, 150, 180, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='w')

        # 滚动条
        scrollbar = ttk.Scrollbar(main, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 绑定双击事件
        self.tree.bind('<Double-Button-1>', self.on_double_click)

        # 状态栏
        self.status = ttk.Label(main, text="就绪", relief='sunken', anchor='w')
        self.status.pack(fill='x', pady=(10, 0))

    def refresh(self):
        """刷新列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, book in enumerate(self.lib.books, 1):
            status = "可借阅" if not book.is_borrowed else "已借出"
            self.tree.insert('', 'end', values=(i, book.title, book.author, book.isbn, status))

        total = len(self.lib.books)
        borrowed = sum(1 for b in self.lib.books if b.is_borrowed)
        self.status.config(text=f"总计 {total} 册 | 可借阅 {total - borrowed} 册 | 已借出 {borrowed} 册")

    def add_book(self):
        """添加图书"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()

        if not all([title, author, isbn]):
            messagebox.showwarning("提示", "请填写完整信息")
            return

        book = Book(title, author, isbn)
        if self.lib.add_book(book):
            self.title_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.isbn_entry.delete(0, tk.END)
            self.refresh()
            messagebox.showinfo("成功", f"《{title}》添加成功")
        else:
            messagebox.showerror("失败", f"ISBN {isbn} 已存在")

    def search_book(self):
        """搜索图书"""
        keyword = tk.simpledialog.askstring("搜索", "输入书名或作者关键词：")
        if not keyword:
            return

        results = self.lib.search_book(keyword)
        if results:
            # 清空并显示搜索结果
            for item in self.tree.get_children():
                self.tree.delete(item)
            for i, info in enumerate(results, 1):
                self.tree.insert('', 'end', values=(i, *self.parse_info(info)))
            self.status.config(text=f"搜索到 {len(results)} 条结果")
        else:
            messagebox.showinfo("未找到", "没有找到相关图书")

    def parse_info(self, info):
        """解析图书信息字符串"""
        # 格式：书名 - 作者 (ISBN:xxx) [状态]
        try:
            title_author, rest = info.split(' (ISBN:')
            title, author = title_author.split(' - ')
            isbn, status = rest.replace(')', '').split(' [')
            status = status.replace(']', '')
            return (title, author, isbn, status)
        except:
            return ("", "", "", "")

    def show_borrowed(self):
        """显示已借出图书"""
        borrowed = [b for b in self.lib.books if b.is_borrowed]
        if not borrowed:
            messagebox.showinfo("提示", "暂无已借出图书")
            return

        # 清空并显示已借出
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, book in enumerate(borrowed, 1):
            self.tree.insert('', 'end', values=(i, book.title, book.author, book.isbn, "已借出"))
        self.status.config(text=f"已借出图书 {len(borrowed)} 册")

    def on_double_click(self, event):
        """双击处理借书/还书"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item['values']
        isbn = values[3]
        status = values[4]

        if status == "可借阅":
            if self.lib.borrow_book(isbn):
                self.refresh()
                messagebox.showinfo("成功", f"《{values[1]}》借阅成功")
            else:
                messagebox.showerror("失败", "借阅失败")
        else:
            if self.lib.return_book(isbn):
                self.refresh()
                messagebox.showinfo("成功", f"《{values[1]}》归还成功")
            else:
                messagebox.showerror("失败", "归还失败")


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()