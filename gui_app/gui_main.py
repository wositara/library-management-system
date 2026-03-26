import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from library import Library
from book import Book
from reader import Reader
from datetime import datetime


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 图书管理系统 - 管理员版")
        self.root.geometry("1300x750")
        self.root.resizable(True, True)

        self.lib = Library()
        self.setup_style()
        self.create_widgets()
        self.refresh()
        self.update_stats()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=('微软雅黑', 10), rowheight=35, background='white')
        style.configure("Treeview.Heading", font=('微软雅黑', 10, 'bold'),
                        background='#f1f5f9', foreground='#1e293b')
        style.configure("TButton", font=('微软雅黑', 9), padding=6)
        style.configure("TLabel", font=('微软雅黑', 9))
        style.configure("TLabelframe.Label", font=('微软雅黑', 10, 'bold'))

    def create_widgets(self):
        # 标题栏
        title_frame = tk.Frame(self.root, bg='#1e3a8a', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="📚 图书管理系统 v3.0 - 管理员版",
                 font=('微软雅黑', 18, 'bold'), fg='white', bg='#1e3a8a').pack(expand=True)

        # 笔记本（选项卡）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_book_tab()
        self.create_reader_tab()
        self.create_borrow_tab()
        self.create_stats_tab()
        self.create_backup_tab()

    # ==================== 图书管理选项卡 ====================
    def create_book_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📖 图书管理")

        # 操作按钮栏
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="➕ 添加图书", command=self.add_book).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="✏️ 编辑图书", command=self.edit_book).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ 下架图书", command=self.delete_book).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🔄 刷新", command=self.refresh_books).pack(side='left', padx=2)

        # 搜索栏
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', padx=10, pady=5)

        self.book_search_entry = ttk.Entry(search_frame, font=('微软雅黑', 10))
        self.book_search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(search_frame, text="🔍 搜索", command=self.search_book).pack(side='left')

        # 图书列表
        columns = ('ISBN', '书名', '作者', '出版社', '分类', '状态', '借阅人', '应还日期')
        self.book_tree = ttk.Treeview(tab, columns=columns, show='headings', height=18)

        widths = [150, 220, 120, 150, 80, 80, 100, 100]
        for col, w in zip(columns, widths):
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=w, anchor='w')

        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)

        self.book_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def refresh_books(self, books=None):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        if books is None:
            books = self.lib.get_all_books()

        for book in books:
            status = "可借阅" if not book.is_borrowed else "已借出"
            borrower = book.borrower_name or ""
            due_date = book.due_date or ""
            self.book_tree.insert('', 'end', values=(
                book.isbn, book.title, book.author, book.publisher,
                book.category, status, borrower, due_date
            ))

    def search_book(self):
        keyword = self.book_search_entry.get().strip()
        if not keyword:
            self.refresh_books()
            return
        results = self.lib.search_book(keyword)
        self.refresh_books(results)

    def add_book(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加图书")
        dialog.geometry("450x400")
        dialog.resizable(False, False)

        tk.Label(dialog, text="📖 添加新书", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        entries = {}
        fields = [("书名", "title"), ("作者", "author"), ("ISBN", "isbn"),
                  ("出版社", "publisher"), ("分类", "category")]

        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, font=('微软雅黑', 10)).grid(row=i, column=0, sticky='e', pady=6, padx=5)
            if key == "category":
                entry = ttk.Combobox(frame, values=Book.CATEGORIES, width=27)
                entry.set('编程')
            else:
                entry = tk.Entry(frame, width=30, font=('微软雅黑', 10))
            entry.grid(row=i, column=1, pady=6, padx=5)
            entries[key] = entry

        def submit():
            title = entries['title'].get().strip()
            author = entries['author'].get().strip()
            isbn = entries['isbn'].get().strip()
            publisher = entries['publisher'].get().strip()
            category = entries['category'].get()

            if not all([title, author, isbn]):
                messagebox.showwarning("提示", "请填写带*号的必填项")
                return

            book = Book(title, author, isbn, publisher, "", category)
            success, msg = self.lib.add_book(book)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_books()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        tk.Button(dialog, text="确认添加", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(pady=20)

    def edit_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的图书")
            return

        item = self.book_tree.item(selected[0])
        isbn = item['values'][0]
        book = self.lib.get_book_by_isbn(isbn)
        if not book:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑图书")
        dialog.geometry("450x400")

        tk.Label(dialog, text="✏️ 编辑图书", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        entries = {}
        fields = [("书名", book.title), ("作者", book.author), ("出版社", book.publisher), ("分类", book.category)]

        for i, (label, val) in enumerate(fields):
            tk.Label(frame, text=label, font=('微软雅黑', 10)).grid(row=i, column=0, sticky='e', pady=6, padx=5)
            if label == "分类":
                entry = ttk.Combobox(frame, values=Book.CATEGORIES, width=27)
                entry.set(val)
            else:
                entry = tk.Entry(frame, width=30, font=('微软雅黑', 10))
                entry.insert(0, val)
            entry.grid(row=i, column=1, pady=6, padx=5)
            entries[label] = entry

        def submit():
            updates = {
                'title': entries['书名'].get().strip(),
                'author': entries['作者'].get().strip(),
                'publisher': entries['出版社'].get().strip(),
                'category': entries['分类'].get()
            }
            success, msg = self.lib.update_book(isbn, **updates)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_books()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        tk.Button(dialog, text="保存修改", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(pady=20)

    def delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要下架的图书")
            return

        item = self.book_tree.item(selected[0])
        isbn = item['values'][0]
        title = item['values'][1]

        if messagebox.askyesno("确认", f"确定要下架《{title}》吗？"):
            success, msg = self.lib.delete_book(isbn)
            if success:
                messagebox.showinfo("成功", msg)
                self.refresh_books()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

    # ==================== 读者管理选项卡 ====================
    def create_reader_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 读者管理")

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="➕ 添加读者", command=self.add_reader).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="✏️ 编辑读者", command=self.edit_reader).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ 注销读者", command=self.delete_reader).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="📖 借阅历史", command=self.view_history).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="💰 缴纳罚款", command=self.pay_fine).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🔄 刷新", command=self.refresh_readers).pack(side='left', padx=2)

        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', padx=10, pady=5)

        self.reader_search_entry = ttk.Entry(search_frame, font=('微软雅黑', 10))
        self.reader_search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(search_frame, text="🔍 搜索", command=self.search_reader).pack(side='left')

        columns = ('证号', '姓名', '性别', '电话', '邮箱', '地址', '当前借阅', '累计借阅', '罚款', '状态')
        self.reader_tree = ttk.Treeview(tab, columns=columns, show='headings', height=16)

        widths = [100, 100, 50, 120, 180, 150, 80, 80, 80, 80]
        for col, w in zip(columns, widths):
            self.reader_tree.heading(col, text=col)
            self.reader_tree.column(col, width=w, anchor='w')

        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.reader_tree.yview)
        self.reader_tree.configure(yscrollcommand=scrollbar.set)

        self.reader_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def refresh_readers(self, readers=None):
        for item in self.reader_tree.get_children():
            self.reader_tree.delete(item)

        if readers is None:
            readers = self.lib.get_all_readers()

        for r in readers:
            status = "正常" if r.is_active else "冻结"
            self.reader_tree.insert('', 'end', values=(
                r.reader_id, r.name, r.gender, r.phone, r.email, r.address,
                r.borrowed_count, r.total_borrow, f"¥{r.fine:.2f}", status
            ))

    def search_reader(self):
        keyword = self.reader_search_entry.get().strip()
        if not keyword:
            self.refresh_readers()
            return
        results = [r for r in self.lib.get_all_readers()
                   if keyword in r.reader_id or keyword in r.name or keyword in r.phone]
        self.refresh_readers(results)

    def add_reader(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加读者")
        dialog.geometry("450x500")
        dialog.resizable(False, False)

        tk.Label(dialog, text="👤 添加读者", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        entries = {}
        fields = [("读者证号", "reader_id"), ("姓名", "name"), ("性别", "gender"),
                  ("电话", "phone"), ("邮箱", "email"), ("地址", "address")]

        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, font=('微软雅黑', 10)).grid(row=i, column=0, sticky='e', pady=6, padx=5)
            if key == "gender":
                entry = ttk.Combobox(frame, values=['男', '女', '其他'], width=27)
                entry.set('男')
            else:
                entry = tk.Entry(frame, width=30, font=('微软雅黑', 10))
            entry.grid(row=i, column=1, pady=6, padx=5)
            entries[key] = entry

        def submit():
            reader = Reader(entries['reader_id'].get(), entries['name'].get(), entries['gender'].get(),
                            entries['phone'].get(), entries['email'].get(), entries['address'].get())
            success, msg = self.lib.add_reader(reader)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_readers()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        tk.Button(dialog, text="确认添加", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(pady=20)

    def edit_reader(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的读者")
            return

        item = self.reader_tree.item(selected[0])
        reader_id = item['values'][0]
        reader = self.lib.get_reader(reader_id)
        if not reader:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑读者")
        dialog.geometry("450x550")

        tk.Label(dialog, text="✏️ 编辑读者", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        entries = {}
        fields = [("姓名", reader.name), ("性别", reader.gender), ("电话", reader.phone),
                  ("邮箱", reader.email), ("地址", reader.address)]

        for i, (label, val) in enumerate(fields):
            tk.Label(frame, text=label, font=('微软雅黑', 10)).grid(row=i, column=0, sticky='e', pady=6, padx=5)
            if label == "性别":
                entry = ttk.Combobox(frame, values=['男', '女', '其他'], width=27)
                entry.set(val)
            else:
                entry = tk.Entry(frame, width=30, font=('微软雅黑', 10))
                entry.insert(0, val)
            entry.grid(row=i, column=1, pady=6, padx=5)
            entries[label] = entry

        tk.Label(frame, text="账户状态", font=('微软雅黑', 10)).grid(row=5, column=0, sticky='e', pady=6, padx=5)
        status_entry = ttk.Combobox(frame, values=['正常', '冻结'], width=27)
        status_entry.set("正常" if reader.is_active else "冻结")
        status_entry.grid(row=5, column=1, pady=6, padx=5)

        def submit():
            updates = {
                'name': entries['姓名'].get().strip(),
                'gender': entries['性别'].get(),
                'phone': entries['电话'].get().strip(),
                'email': entries['邮箱'].get().strip(),
                'address': entries['地址'].get().strip(),
                'is_active': status_entry.get() == '正常'
            }
            success, msg = self.lib.update_reader(reader_id, **updates)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_readers()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        tk.Button(dialog, text="保存修改", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(pady=20)

    def delete_reader(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要注销的读者")
            return

        item = self.reader_tree.item(selected[0])
        reader_id = item['values'][0]
        name = item['values'][1]

        if messagebox.askyesno("确认", f"确定要注销读者 {name} 吗？\n（注销后无法恢复）"):
            success, msg = self.lib.delete_reader(reader_id)
            if success:
                messagebox.showinfo("成功", msg)
                self.refresh_readers()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

    def view_history(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要查看的读者")
            return

        item = self.reader_tree.item(selected[0])
        reader_id = item['values'][0]
        name = item['values'][1]

        history = self.lib.get_reader_borrow_history(reader_id)

        window = tk.Toplevel(self.root)
        window.title(f"{name} 的借阅历史")
        window.geometry("900x500")

        columns = ('书名', 'ISBN', '借阅日期', '应还日期', '归还日期', '罚款')
        tree = ttk.Treeview(window, columns=columns, show='headings', height=15)

        widths = [250, 150, 120, 100, 120, 80]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='w')

        for record in history:
            tree.insert('', 'end', values=(
                record['title'], record['isbn'],
                record['borrow_date'][:10], record['due_date'],
                record['return_date'][:10] if record['return_date'] else "在借",
                f"¥{record.get('fine', 0):.2f}"
            ))

        scrollbar = ttk.Scrollbar(window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

        tk.Label(window, text=f"共 {len(history)} 条借阅记录", font=('微软雅黑', 10)).pack(pady=5)

    def pay_fine(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要缴纳罚款的读者")
            return

        item = self.reader_tree.item(selected[0])
        reader_id = item['values'][0]
        name = item['values'][1]
        fine = float(item['values'][8].replace('¥', ''))

        if fine <= 0:
            messagebox.showinfo("提示", f"{name} 没有未缴罚款")
            return

        amount = simpledialog.askfloat("缴纳罚款", f"{name} 当前罚款 ¥{fine:.2f}\n请输入缴纳金额：",
                                       minvalue=0, maxvalue=fine)
        if amount:
            reader = self.lib.get_reader(reader_id)
            if reader:
                paid = reader.pay_fine(amount)
                self.lib.save_to_file()
                messagebox.showinfo("成功", f"已缴纳 ¥{paid:.2f}，剩余罚款 ¥{reader.fine:.2f}")
                self.refresh_readers()
                self.update_stats()

    # ==================== 借阅管理选项卡 ====================
    def create_borrow_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 借阅管理")

        # 操作区
        op_frame = ttk.LabelFrame(tab, text="借还书操作", padding="15")
        op_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(op_frame, text="📖 借出图书", command=self.borrow_book_ui, width=15).pack(side='left', padx=10)
        ttk.Button(op_frame, text="📚 归还图书", command=self.return_book_ui, width=15).pack(side='left', padx=10)
        ttk.Button(op_frame, text="🔄 续借图书", command=self.renew_book_ui, width=15).pack(side='left', padx=10)

        # 当前借阅列表
        borrowed_frame = ttk.LabelFrame(tab, text="当前借阅列表", padding="10")
        borrowed_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ISBN', '书名', '作者', '借阅人', '读者证号', '借阅日期', '应还日期', '状态')
        self.borrowed_tree = ttk.Treeview(borrowed_frame, columns=columns, show='headings', height=12)

        widths = [150, 200, 120, 100, 100, 120, 100, 80]
        for col, w in zip(columns, widths):
            self.borrowed_tree.heading(col, text=col)
            self.borrowed_tree.column(col, width=w, anchor='w')

        scrollbar = ttk.Scrollbar(borrowed_frame, orient='vertical', command=self.borrowed_tree.yview)
        self.borrowed_tree.configure(yscrollcommand=scrollbar.set)

        self.borrowed_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        ttk.Button(borrowed_frame, text="🔄 刷新", command=self.refresh_borrowed).pack(pady=10)

    def refresh_borrowed(self):
        for item in self.borrowed_tree.get_children():
            self.borrowed_tree.delete(item)

        borrowed = self.lib.get_borrowed_books()
        now = datetime.now()

        for book in borrowed:
            status = "正常"
            if book.due_date:
                due = datetime.strptime(book.due_date, "%Y-%m-%d")
                if due < now:
                    status = "逾期"

            self.borrowed_tree.insert('', 'end', values=(
                book.isbn, book.title, book.author,
                book.borrower_name, book.borrower_id,
                book.borrow_date[:10] if book.borrow_date else "",
                book.due_date or "", status
            ))

    def borrow_book_ui(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("借出图书")
        dialog.geometry("400x250")

        tk.Label(dialog, text="📖 借出图书", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        tk.Label(frame, text="图书ISBN：", font=('微软雅黑', 10)).grid(row=0, column=0, sticky='e', pady=8, padx=5)
        isbn_entry = tk.Entry(frame, width=25, font=('微软雅黑', 10))
        isbn_entry.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(frame, text="读者证号：", font=('微软雅黑', 10)).grid(row=1, column=0, sticky='e', pady=8, padx=5)
        reader_entry = tk.Entry(frame, width=25, font=('微软雅黑', 10))
        reader_entry.grid(row=1, column=1, pady=8, padx=5)

        def submit():
            isbn = isbn_entry.get().strip()
            reader_id = reader_entry.get().strip()

            if not all([isbn, reader_id]):
                messagebox.showwarning("提示", "请填写完整信息")
                return

            success, msg = self.lib.borrow_book(isbn, reader_id)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_books()
                self.refresh_readers()
                self.refresh_borrowed()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="确认借出", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), width=12).pack(side='left')

    def return_book_ui(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("归还图书")
        dialog.geometry("400x250")

        tk.Label(dialog, text="📚 归还图书", font=('微软雅黑', 14, 'bold'),
                 fg='#1e3a8a').pack(pady=15)

        frame = tk.Frame(dialog)
        frame.pack(pady=10)

        tk.Label(frame, text="图书ISBN：", font=('微软雅黑', 10)).grid(row=0, column=0, sticky='e', pady=8, padx=5)
        isbn_entry = tk.Entry(frame, width=25, font=('微软雅黑', 10))
        isbn_entry.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(frame, text="读者证号：", font=('微软雅黑', 10)).grid(row=1, column=0, sticky='e', pady=8, padx=5)
        reader_entry = tk.Entry(frame, width=25, font=('微软雅黑', 10))
        reader_entry.grid(row=1, column=1, pady=8, padx=5)

        def submit():
            isbn = isbn_entry.get().strip()
            reader_id = reader_entry.get().strip()

            if not all([isbn, reader_id]):
                messagebox.showwarning("提示", "请填写完整信息")
                return

            success, msg = self.lib.return_book(isbn, reader_id)
            if success:
                messagebox.showinfo("成功", msg)
                dialog.destroy()
                self.refresh_books()
                self.refresh_readers()
                self.refresh_borrowed()
                self.update_stats()
            else:
                messagebox.showerror("失败", msg)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="确认归还", command=submit, bg='#1e3a8a', fg='white',
                  font=('微软雅黑', 10), width=12).pack(side='left', padx=10)
        tk.Button(btn_frame, text="取消", command=dialog.destroy,
                  font=('微软雅黑', 10), width=12).pack(side='left')

    def renew_book_ui(self):
        selected = self.borrowed_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要续借的图书")
            return

        item = self.borrowed_tree.item(selected[0])
        isbn = item['values'][0]
        reader_id = item['values'][4]

        success, msg = self.lib.renew_book(isbn, reader_id)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_books()
            self.refresh_borrowed()
        else:
            messagebox.showerror("失败", msg)

    # ==================== 统计报表选项卡 ====================
    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 统计报表")

        # 统计卡片
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill='x', padx=10, pady=10)

        self.stats_labels = {}
        cards = [("总藏书", "total_books"), ("可借阅", "available_books"), ("已借出", "borrowed_books"),
                 ("注册读者", "total_readers"), ("活跃读者", "active_readers"), ("未缴罚款", "total_fine")]

        for i, (label, key) in enumerate(cards):
            card = tk.Frame(stats_frame, bg='white', relief='ridge', bd=1)
            card.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky='ew')
            stats_frame.grid_columnconfigure(i % 3, weight=1)

            self.stats_labels[key] = tk.Label(card, text="0", font=('微软雅黑', 24, 'bold'),
                                              fg='#1e3a8a', bg='white')
            self.stats_labels[key].pack(pady=(10, 0))
            tk.Label(card, text=label, font=('微软雅黑', 10), fg='#64748b', bg='white').pack(pady=(0, 10))

        # 分类统计
        category_frame = ttk.LabelFrame(tab, text="📊 图书分类统计", padding="10")
        category_frame.pack(fill='x', padx=10, pady=10)

        self.category_text = scrolledtext.ScrolledText(category_frame, height=8, font=('微软雅黑', 10))
        self.category_text.pack(fill='x')

        # 排行榜
        rank_frame = ttk.Frame(tab)
        rank_frame.pack(fill='both', expand=True, padx=10, pady=10)

        book_rank_frame = ttk.LabelFrame(rank_frame, text="🏆 图书借阅排行榜", padding="10")
        book_rank_frame.pack(side='left', fill='both', expand=True, padx=5)

        self.book_rank_tree = ttk.Treeview(book_rank_frame, columns=('书名', '次数'), show='headings', height=10)
        self.book_rank_tree.heading('书名', text='书名')
        self.book_rank_tree.heading('次数', text='借阅次数')
        self.book_rank_tree.column('书名', width=250)
        self.book_rank_tree.column('次数', width=80, anchor='center')
        self.book_rank_tree.pack(fill='both', expand=True)

        reader_rank_frame = ttk.LabelFrame(rank_frame, text="👥 读者借阅排行榜", padding="10")
        reader_rank_frame.pack(side='right', fill='both', expand=True, padx=5)

        self.reader_rank_tree = ttk.Treeview(reader_rank_frame, columns=('姓名', '次数'), show='headings', height=10)
        self.reader_rank_tree.heading('姓名', text='姓名')
        self.reader_rank_tree.heading('次数', text='借阅次数')
        self.reader_rank_tree.column('姓名', width=150)
        self.reader_rank_tree.column('次数', width=80, anchor='center')
        self.reader_rank_tree.pack(fill='both', expand=True)

        ttk.Button(tab, text="🔄 刷新统计", command=self.update_stats).pack(pady=10)

    def update_stats(self):
        stats = self.lib.get_stats()

        for key, label in self.stats_labels.items():
            if key == 'total_fine':
                label.config(text=f"¥{stats[key]:.2f}")
            else:
                label.config(text=str(stats[key]))

        # 分类统计
        self.category_text.delete(1.0, tk.END)
        for cat, count in stats['category_stats'].items():
            self.category_text.insert(tk.END, f"• {cat}: {count} 册\n")

        # 图书排行榜
        for item in self.book_rank_tree.get_children():
            self.book_rank_tree.delete(item)
        for title, count in stats['top_books']:
            self.book_rank_tree.insert('', 'end', values=(title, count))

        # 读者排行榜
        for item in self.reader_rank_tree.get_children():
            self.reader_rank_tree.delete(item)
        for r in stats['top_readers']:
            self.reader_rank_tree.insert('', 'end', values=(r['name'], r['borrow_count']))

    # ==================== 系统管理选项卡 ====================
    def create_backup_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ 系统管理")

        backup_frame = ttk.LabelFrame(tab, text="数据备份与恢复", padding="15")
        backup_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(backup_frame, text="💾 立即备份", command=self.do_backup, width=15).pack(side='left', padx=10)

        list_frame = ttk.LabelFrame(tab, text="备份列表", padding="10")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('备份时间', '文件名')
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.backup_tree.heading('备份时间', text='备份时间')
        self.backup_tree.heading('文件名', text='文件名')
        self.backup_tree.column('备份时间', width=200)
        self.backup_tree.column('文件名', width=300)
        self.backup_tree.pack(fill='both', expand=True)

        ttk.Button(list_frame, text="恢复选中备份", command=self.restore_backup).pack(pady=10)

        self.refresh_backup_list()

    def do_backup(self):
        backup_file = self.lib.backup_data()
        messagebox.showinfo("成功", f"备份成功！\n备份文件：{backup_file}")
        self.refresh_backup_list()

    def refresh_backup_list(self):
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)

        backups = self.lib.get_backup_list()
        for backup in backups:
            time_str = backup.replace('backup_', '').replace('.json', '').replace('_', ' ').replace('-', ':', 1)
            self.backup_tree.insert('', 'end', values=(time_str, backup))

    def restore_backup(self):
        selected = self.backup_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要恢复的备份")
            return

        item = self.backup_tree.item(selected[0])
        backup_file = item['values'][1]

        if messagebox.askyesno("确认", "恢复备份将覆盖当前数据，确定要继续吗？"):
            success, msg = self.lib.restore_backup(backup_file)
            if success:
                messagebox.showinfo("成功", msg)
                self.refresh()
            else:
                messagebox.showerror("失败", msg)

    # ==================== 通用刷新方法 ====================
    def refresh(self):
        self.refresh_books()
        self.refresh_readers()
        self.refresh_borrowed()
        self.update_stats()


def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()