import os
from library import Library
from book import Book
from reader import Reader

class Color:
    CYAN = '\033[96m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    RED = '\033[91m'; BLUE = '\033[94m'; END = '\033[0m'; BOLD = '\033[1m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def header(lib):
    stats = lib.get_stats()
    print(f"\n{Color.CYAN}{'='*70}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}  📚 图书管理系统 v3.0 - 管理员版{Color.END}")
    print(f"  📊 统计：总计 {stats['total_books']} 册 | {Color.GREEN}可借阅 {stats['available_books']} 册{Color.END} | "
          f"{Color.YELLOW}已借出 {stats['borrowed_books']} 册{Color.END} | 👥 读者 {stats['total_readers']} 人")
    print(f"{Color.CYAN}{'='*70}{Color.END}\n")

def menu():
    print(f"{Color.YELLOW}  【图书管理】{Color.END}")
    print(f"  {Color.GREEN}1.{Color.END} 添加图书     {Color.GREEN}2.{Color.END} 查看所有图书")
    print(f"  {Color.GREEN}3.{Color.END} 搜索图书     {Color.GREEN}4.{Color.END} 编辑图书")
    print(f"  {Color.GREEN}5.{Color.END} 下架图书")
    print(f"\n{Color.YELLOW}  【读者管理】{Color.END}")
    print(f"  {Color.GREEN}6.{Color.END} 添加读者     {Color.GREEN}7.{Color.END} 查看所有读者")
    print(f"  {Color.GREEN}8.{Color.END} 编辑读者     {Color.GREEN}9.{Color.END} 注销读者")
    print(f"\n{Color.YELLOW}  【借阅管理】{Color.END}")
    print(f"  {Color.GREEN}10.{Color.END} 借出图书     {Color.GREEN}11.{Color.END} 归还图书")
    print(f"  {Color.GREEN}12.{Color.END} 续借图书     {Color.GREEN}13.{Color.END} 当前借阅列表")
    print(f"\n{Color.YELLOW}  【统计报表】{Color.END}")
    print(f"  {Color.GREEN}14.{Color.END} 查看统计报表  {Color.GREEN}15.{Color.END} 排行榜")
    print(f"\n{Color.YELLOW}  【系统管理】{Color.END}")
    print(f"  {Color.GREEN}16.{Color.END} 数据备份     {Color.GREEN}17.{Color.END} 恢复备份")
    print(f"  {Color.GREEN}0.{Color.END} 退出系统")
    print(f"{Color.CYAN}{'-'*70}{Color.END}")

def show_all_books(lib):
    books = lib.get_all_books()
    if not books:
        print(f"{Color.YELLOW}  📭 暂无图书{Color.END}")
        return
    print(f"\n{Color.CYAN}📖 图书列表：{Color.END}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")
    for i, book in enumerate(books, 1):
        status = "可借阅" if not book.is_borrowed else f"已借出({book.borrower_name})"
        print(f"  {i:2d}. {book.title}")
        print(f"      作者：{book.author}  ISBN：{book.isbn}  分类：{book.category}  出版社：{book.publisher}")
        print(f"      状态：{status}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")
    print(f"  共 {len(books)} 本图书")

def add_book_ui(lib):
    print(f"\n{Color.GREEN}📖 添加图书{Color.END}")
    title = input("  书名 > ").strip()
    author = input("  作者 > ").strip()
    isbn = input("  ISBN > ").strip()
    publisher = input("  出版社 > ").strip()
    category = input("  分类(编程/文学/历史等) > ").strip() or "编程"
    if not all([title, author, isbn]):
        print(f"{Color.RED}  ✗ 请填写完整信息{Color.END}")
        return
    book = Book(title, author, isbn, publisher, "", category)
    success, msg = lib.add_book(book)
    print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def search_book_ui(lib):
    keyword = input(f"\n{Color.GREEN}🔍 请输入关键词 > {Color.END}").strip()
    if not keyword: return
    results = lib.search_book(keyword)
    if results:
        print(f"\n{Color.GREEN}找到 {len(results)} 本图书：{Color.END}")
        for book in results:
            print(f"  • {book.title} - {book.author} (ISBN:{book.isbn})")
    else:
        print(f"{Color.YELLOW}  ⚠ 未找到相关图书{Color.END}")

def edit_book_ui(lib):
    isbn = input(f"\n{Color.GREEN}✏️ 请输入图书ISBN > {Color.END}").strip()
    book = lib.get_book_by_isbn(isbn)
    if not book:
        print(f"{Color.RED}  ✗ 未找到该图书{Color.END}")
        return
    print(f"  当前书名：{book.title}，作者：{book.author}")
    new_title = input("  新书名(直接回车保持不变) > ").strip()
    new_author = input("  新作者(直接回车保持不变) > ").strip()
    updates = {}
    if new_title: updates['title'] = new_title
    if new_author: updates['author'] = new_author
    if updates:
        success, msg = lib.update_book(isbn, **updates)
        print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def delete_book_ui(lib):
    isbn = input(f"\n{Color.GREEN}🗑️ 请输入图书ISBN > {Color.END}").strip()
    book = lib.get_book_by_isbn(isbn)
    if not book:
        print(f"{Color.RED}  ✗ 未找到该图书{Color.END}")
        return
    if input(f"  确定要下架《{book.title}》吗？(y/n) > ").lower() == 'y':
        success, msg = lib.delete_book(isbn)
        print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def add_reader_ui(lib):
    print(f"\n{Color.GREEN}👤 添加读者{Color.END}")
    reader_id = input("  读者证号 > ").strip()
    name = input("  姓名 > ").strip()
    phone = input("  电话 > ").strip()
    email = input("  邮箱 > ").strip()
    if not all([reader_id, name]):
        print(f"{Color.RED}  ✗ 请填写完整信息{Color.END}")
        return
    reader = Reader(reader_id, name, "男", phone, email, "")
    success, msg = lib.add_reader(reader)
    print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def show_all_readers(lib):
    readers = lib.get_all_readers()
    if not readers:
        print(f"{Color.YELLOW}  📭 暂无读者{Color.END}")
        return
    print(f"\n{Color.CYAN}👥 读者列表：{Color.END}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")
    for i, r in enumerate(readers, 1):
        status = "正常" if r.is_active else "冻结"
        print(f"  {i:2d}. {r.reader_id} | {r.name} | {r.gender} | 电话:{r.phone}")
        print(f"      借阅:{r.borrowed_count}本 | 累计:{r.total_borrow}次 | 罚款:¥{r.fine:.2f} | 状态:{status}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")

def borrow_book_ui(lib):
    print(f"\n{Color.GREEN}📖 借出图书{Color.END}")
    isbn = input("  图书ISBN > ").strip()
    reader_id = input("  读者证号 > ").strip()
    success, msg = lib.borrow_book(isbn, reader_id)
    print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def return_book_ui(lib):
    print(f"\n{Color.GREEN}📚 归还图书{Color.END}")
    isbn = input("  图书ISBN > ").strip()
    reader_id = input("  读者证号 > ").strip()
    success, msg = lib.return_book(isbn, reader_id)
    print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def renew_book_ui(lib):
    print(f"\n{Color.GREEN}🔄 续借图书{Color.END}")
    isbn = input("  图书ISBN > ").strip()
    reader_id = input("  读者证号 > ").strip()
    success, msg = lib.renew_book(isbn, reader_id)
    print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")

def show_borrowed_ui(lib):
    borrowed = lib.get_borrowed_books()
    if not borrowed:
        print(f"{Color.YELLOW}  📭 暂无借出图书{Color.END}")
        return
    print(f"\n{Color.CYAN}📖 当前借阅列表：{Color.END}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")
    for book in borrowed:
        print(f"  {book.title} - {book.author}")
        print(f"      借阅人：{book.borrower_name}({book.borrower_id})  应还：{book.due_date}")
    print(f"{Color.CYAN}{'-'*80}{Color.END}")

def show_stats_ui(lib):
    stats = lib.get_stats()
    print(f"\n{Color.CYAN}📊 统计报表{Color.END}")
    print(f"{Color.CYAN}{'-'*50}{Color.END}")
    print(f"  总藏书：{stats['total_books']} 册")
    print(f"  可借阅：{stats['available_books']} 册")
    print(f"  已借出：{stats['borrowed_books']} 册")
    print(f"  注册读者：{stats['total_readers']} 人")
    print(f"  活跃读者：{stats['active_readers']} 人")
    print(f"  未缴罚款：¥{stats['total_fine']:.2f}")
    print(f"\n{Color.CYAN}📚 分类统计：{Color.END}")
    for cat, count in stats['category_stats'].items():
        print(f"  • {cat}: {count} 册")

def show_ranking_ui(lib):
    stats = lib.get_stats()
    print(f"\n{Color.CYAN}🏆 图书借阅排行榜{Color.END}")
    print(f"{Color.CYAN}{'-'*50}{Color.END}")
    for i, (title, count) in enumerate(stats['top_books'][:10], 1):
        print(f"  {i}. {title} - 借阅 {count} 次")
    print(f"\n{Color.CYAN}👥 读者借阅排行榜{Color.END}")
    print(f"{Color.CYAN}{'-'*50}{Color.END}")
    for i, r in enumerate(stats['top_readers'][:10], 1):
        print(f"  {i}. {r['name']} - 借阅 {r['borrow_count']} 次")

def backup_ui(lib):
    backup_file = lib.backup_data()
    print(f"{Color.GREEN}  ✓ 备份成功！{backup_file}{Color.END}")

def restore_ui(lib):
    backups = lib.get_backup_list()
    if not backups:
        print(f"{Color.YELLOW}  ⚠ 没有找到备份文件{Color.END}")
        return
    print(f"\n{Color.CYAN}可用备份：{Color.END}")
    for i, f in enumerate(backups, 1):
        print(f"  {i}. {f}")
    try:
        choice = int(input("  请选择要恢复的备份编号 > "))
        if 1 <= choice <= len(backups):
            success, msg = lib.restore_backup(backups[choice-1])
            print(f"{Color.GREEN if success else Color.RED}  {'✓' if success else '✗'} {msg}{Color.END}")
    except:
        print(f"{Color.RED}  ✗ 无效选择{Color.END}")

def main():
    lib = Library()
    while True:
        clear()
        header(lib)
        menu()
        choice = input(f"\n  {Color.BOLD}请选择 > {Color.END}").strip()
        if choice == '1': add_book_ui(lib)
        elif choice == '2': show_all_books(lib)
        elif choice == '3': search_book_ui(lib)
        elif choice == '4': edit_book_ui(lib)
        elif choice == '5': delete_book_ui(lib)
        elif choice == '6': add_reader_ui(lib)
        elif choice == '7': show_all_readers(lib)
        elif choice == '8': edit_book_ui(lib)
        elif choice == '9': delete_book_ui(lib)
        elif choice == '10': borrow_book_ui(lib)
        elif choice == '11': return_book_ui(lib)
        elif choice == '12': renew_book_ui(lib)
        elif choice == '13': show_borrowed_ui(lib)
        elif choice == '14': show_stats_ui(lib)
        elif choice == '15': show_ranking_ui(lib)
        elif choice == '16': backup_ui(lib)
        elif choice == '17': restore_ui(lib)
        elif choice == '0':
            print(f"\n{Color.GREEN}  感谢使用，再见！{Color.END}\n")
            break
        else:
            print(f"{Color.RED}  无效选项{Color.END}")
        input(f"\n{Color.YELLOW}  按回车键继续...{Color.END}")

if __name__ == "__main__":
    main()