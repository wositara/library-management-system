from flask import Flask, render_template, request, redirect, url_for
from library import Library
from book import Book

app = Flask(__name__)
lib = Library()


@app.route('/')
def index():
    books = []
    for book in lib.books:
        books.append({
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'status': '已借出' if book.is_borrowed else '可借阅'
        })
    return render_template('index.html', books=books)


@app.route('/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn')

    # 创建Book对象并添加到图书馆
    new_book = Book(title, author, isbn)
    if lib.add_book(new_book):
        return redirect(url_for('index'))
    else:
        return "添加失败，ISBN已存在！", 400


@app.route('/borrow', methods=['POST'])
def borrow_book():
    isbn = request.form.get('isbn')
    if lib.borrow_book(isbn):
        return redirect(url_for('index'))
    else:
        return "借书失败，请检查ISBN或图书已借出", 400


@app.route('/return', methods=['POST'])
def return_book():
    isbn = request.form.get('isbn')
    if lib.return_book(isbn):
        return redirect(url_for('index'))
    else:
        return "还书失败，请检查ISBN", 400


if __name__ == '__main__':
    app.run(debug=True)