import os
from library import Library
from book import Book


# 简洁的颜色定义
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def header():
    print(f"\n{Color.CYAN}{'=' * 50}")
    print(f"  📚 图书管理系统  v1.0")
    print(f"{'=' * 50}{Color.END}\n")


def menu():
    print(f"{Color.YELLOW}  1.{Color.END} 添加图书")
    print(f"{Color.YELLOW}  2.{Color.END} 查看所有")
    print(f"{Color.YELLOW}  3.{Color.END} 搜索图书")
    print(f"{Color.YELLOW}  4.{Color.END} 借阅图书")
    print(f"{Color.YELLOW}  5.{Color.END} 归还图书")
    print(f"{Color.YELLOW}  6.{Color.END} 已借出列表")
    print(f"{Color.YELLOW}  0.{Color.END} 退出系统")
    print(f"{Color.CYAN}{'-' * 50}{Color.END}")


def add_book_ui(lib):
    print(f"\n{Color.GREEN}📖 添加新书{Color.END}")
    title = input("  书名 > ").strip()
    author = input("  作者 > ").strip()
    isbn = input("  ISBN > ").strip()

    if not all([title, author, isbn]):
        print(f"{Color.RED}  ✗ 信息不能为空{Color.END}")
        return

    book = Book(title, author, isbn)
    if lib.add_book(book):
        print(f"{Color.GREEN}  ✓ 添加成功{Color.END}")
    else:
        print(f"{Color.RED}  ✗ ISBN已存在{Color.END}")


def search_book_ui(lib):
    print(f"\n{Color.GREEN}🔍 搜索图书{Color.END}")
    keyword = input("  关键词 > ").strip()
    if not keyword:
        return

    results = lib.search_book(keyword)
    if results:
        print(f"\n  {Color.CYAN}找到 {len(results)} 本:{Color.END}")
        for r in results:
            print(f"    • {r}")
    else:
        print(f"{Color.YELLOW}  ⚠ 未找到相关图书{Color.END}")


def borrow_book_ui(lib):
    print(f"\n{Color.GREEN}📤 借阅图书{Color.END}")
    isbn = input("  ISBN > ").strip()
    if lib.borrow_book(isbn):
        print(f"{Color.GREEN}  ✓ 借阅成功，请按时归还{Color.END}")
    else:
        print(f"{Color.RED}  ✗ 借阅失败，请检查ISBN{Color.END}")


def return_book_ui(lib):
    print(f"\n{Color.GREEN}📥 归还图书{Color.END}")
    isbn = input("  ISBN > ").strip()
    if lib.return_book(isbn):
        print(f"{Color.GREEN}  ✓ 归还成功{Color.END}")
    else:
        print(f"{Color.RED}  ✗ 归还失败，请检查ISBN{Color.END}")


def main():
    lib = Library()

    while True:
        clear()
        header()
        menu()
        choice = input("\n  请选择 > ").strip()

        if choice == '1':
            add_book_ui(lib)
        elif choice == '2':
            print(f"\n{lib.show_all_books()}")
        elif choice == '3':
            search_book_ui(lib)
        elif choice == '4':
            borrow_book_ui(lib)
        elif choice == '5':
            return_book_ui(lib)
        elif choice == '6':
            print(f"\n{lib.show_borrowed_books()}")
        elif choice == '0':
            print(f"\n{Color.GREEN}  感谢使用，再见！{Color.END}\n")
            break
        else:
            print(f"{Color.RED}  无效选项{Color.END}")

        input(f"\n{Color.YELLOW}  按回车继续...{Color.END}")


if __name__ == "__main__":
    main()