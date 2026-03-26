from flask import Flask, render_template, request, redirect, url_for, flash
from library import Library
from book import Book
from reader import Reader
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'library-management-system-2024'
lib = Library()


# ==================== 首页 ====================
@app.route('/')
def index():
    stats = lib.get_stats()
    books = []
    for book in lib.books:
        books.append({
            'title': book.title, 'author': book.author, 'isbn': book.isbn,
            'publisher': book.publisher, 'category': book.category,
            'status': '可借阅' if not book.is_borrowed else '已借出',
            'borrower_name': book.borrower_name, 'due_date': book.due_date
        })
    return render_template('index.html', books=books, stats=stats)


@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn')
    publisher = request.form.get('publisher', '')
    category = request.form.get('category', '编程')

    if not all([title, author, isbn]):
        flash('请填写完整信息', 'error')
        return redirect(url_for('index'))

    book = Book(title, author, isbn, publisher, '', category)
    success, msg = lib.add_book(book)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('index'))


@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return redirect(url_for('index'))

    results = lib.search_book(keyword)
    stats = lib.get_stats()
    books = []
    for book in results:
        books.append({
            'title': book.title, 'author': book.author, 'isbn': book.isbn,
            'publisher': book.publisher, 'category': book.category,
            'status': '可借阅' if not book.is_borrowed else '已借出',
            'borrower_name': book.borrower_name, 'due_date': book.due_date
        })
    return render_template('index.html', books=books, stats=stats, keyword=keyword)


@app.route('/edit_book/<isbn>')
def edit_book_page(isbn):
    book = lib.get_book_by_isbn(isbn)
    if not book:
        flash('未找到该图书', 'error')
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)


@app.route('/update_book/<isbn>', methods=['POST'])
def update_book(isbn):
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    updates = {}
    if title: updates['title'] = title
    if author: updates['author'] = author
    if publisher: updates['publisher'] = publisher
    if category: updates['category'] = category
    success, msg = lib.update_book(isbn, **updates)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('index'))


@app.route('/delete_book/<isbn>')
def delete_book(isbn):
    success, msg = lib.delete_book(isbn)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('index'))


# ==================== 读者管理 ====================
@app.route('/readers')
def readers():
    stats = lib.get_stats()
    readers = lib.get_all_readers()
    return render_template('readers.html', readers=readers, stats=stats)


@app.route('/add_reader', methods=['POST'])
def add_reader():
    reader_id = request.form.get('reader_id')
    name = request.form.get('name')
    gender = request.form.get('gender', '男')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')

    if not all([reader_id, name]):
        flash('请填写完整信息', 'error')
        return redirect(url_for('readers'))

    reader = Reader(reader_id, name, gender, phone, email, address)
    success, msg = lib.add_reader(reader)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('readers'))


@app.route('/edit_reader/<reader_id>')
def edit_reader_page(reader_id):
    reader = lib.get_reader(reader_id)
    if not reader:
        flash('未找到该读者', 'error')
        return redirect(url_for('readers'))
    return render_template('edit_reader.html', reader=reader)


@app.route('/update_reader/<reader_id>', methods=['POST'])
def update_reader(reader_id):
    name = request.form.get('name')
    gender = request.form.get('gender')
    phone = request.form.get('phone')
    email = request.form.get('email')
    address = request.form.get('address')
    is_active = request.form.get('is_active') == '正常'
    updates = {}
    if name: updates['name'] = name
    if gender: updates['gender'] = gender
    if phone: updates['phone'] = phone
    if email: updates['email'] = email
    if address: updates['address'] = address
    updates['is_active'] = is_active
    success, msg = lib.update_reader(reader_id, **updates)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('readers'))


@app.route('/delete_reader/<reader_id>')
def delete_reader(reader_id):
    success, msg = lib.delete_reader(reader_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('readers'))


@app.route('/reader_history/<reader_id>')
def reader_history(reader_id):
    reader = lib.get_reader(reader_id)
    if not reader:
        flash('未找到该读者', 'error')
        return redirect(url_for('readers'))
    history = lib.get_reader_borrow_history(reader_id)
    return render_template('reader_history.html', reader=reader, history=history)


# ==================== 借阅管理 ====================
@app.route('/borrow')
def borrow_page():
    borrowed = lib.get_borrowed_books()
    borrowed_list = []
    for book in borrowed:
        borrowed_list.append({
            'title': book.title, 'author': book.author, 'isbn': book.isbn,
            'borrower_name': book.borrower_name, 'borrower_id': book.borrower_id,
            'borrow_date': book.borrow_date, 'due_date': book.due_date
        })
    return render_template('borrow.html', borrowed=borrowed_list, borrowed_count=len(borrowed),
                           now=datetime.now().strftime('%Y-%m-%d'))


@app.route('/borrow', methods=['POST'])
def borrow_book():
    isbn = request.form.get('isbn')
    reader_id = request.form.get('reader_id')
    success, msg = lib.borrow_book(isbn, reader_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('borrow_page'))


@app.route('/return', methods=['POST'])
def return_book():
    isbn = request.form.get('isbn')
    reader_id = request.form.get('reader_id')
    success, msg = lib.return_book(isbn, reader_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('borrow_page'))


@app.route('/renew/<isbn>/<reader_id>')
def renew_book(isbn, reader_id):
    success, msg = lib.renew_book(isbn, reader_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('borrow_page'))


# ==================== 统计报表 ====================
@app.route('/stats')
def stats():
    stats = lib.get_stats()
    return render_template('stats.html', stats=stats)


# ==================== 系统管理 ====================
@app.route('/backup')
def backup():
    backups = lib.get_backup_list()
    return render_template('backup.html', backups=backups)


@app.route('/do_backup', methods=['POST'])
def do_backup():
    backup_file = lib.backup_data()
    flash(f'备份成功！', 'success')
    return redirect(url_for('backup'))


@app.route('/restore/<backup_file>')
def restore_backup(backup_file):
    success, msg = lib.restore_backup(backup_file)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('backup'))


if __name__ == '__main__':
    app.run(debug=True)