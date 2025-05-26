import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
def connect():
    conn=sqlite3.connect("expenses.db")
    create_table(conn)
    return conn

def create_table(conn):
    cursor=conn.cursor()
    cursor.execute("create table if not exists expenses (id integer primary key AUTOINCREMENT, amount real not null, category text not null, date text not null, description text)")
    conn.commit()

def get_categories():
    return ["Food", "Transport", "Entertainment", "Utilities", "Healthcare", "Others"]

def add_expense(conn, amount, category, date, description):
    cursor = conn.cursor()
    cursor.execute("insert into expenses (amount, category, date, description) values (?, ?, ?, ?)", (amount, category, date, description))
    conn.commit()

def get_all_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("select * from expenses order by date")
    return cursor.fetchall()

def get_expenses_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute("select * from expenses where category = ? order by date", (category,))
    return cursor.fetchall()

def get_expenses_by_date_range(conn, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("select * from expenses where date between ? and ? order by date", (start_date, end_date))
    return cursor.fetchall()

def search_expenses_by_description(conn, keyword):
    cursor = conn.cursor()
    cursor.execute("select * from expenses where description like ? order by date", ('%' + keyword + '%',))
    return cursor.fetchall()

def delete_expense(conn, expense_id):
    cursor = conn.cursor()
    cursor.execute("delete from expenses where id = ?", (expense_id,))
    conn.commit()

def get_total_expense(conn):
    cursor = conn.cursor()
    cursor.execute("select sum(amount) from expenses")
    result = cursor.fetchone()
    if result[0] is not None:
        return result[0]
    else:
        return 0

def get_monthly_expenses(conn):
    cursor = conn.cursor()
    cursor.execute("select strftime('%Y-%m', date) as month, sum(amount) from expenses group by month order by month")
    return cursor.fetchall()

def print_expenses(expenses):
    if len(expenses) == 0:
        print("No expenses to show\n")
        return

    print("ID | Amount | Category | Date       | Description")
    print("-----------------------------------------------")
    for exp in expenses:
        print(str(exp[0]) + "  | ₹" + str(exp[1]) + " | " + exp[2] + " | " + exp[3] + " | " + exp[4])

def validate_date_input(date_input):
    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return date_input
    except ValueError:
        print("Date must be in yyyy-mm-dd format")
        return None

def main():
    conn = connect()
    print("===================================================================================================")
    print("                                    Welcome to the Personal Expense Tracker ")
    print("===================================================================================================")

    while True:
        print("\nOptions:")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View by Category")
        print("4. View by Date Range")
        print("5. Search by Description")
        print("6. Delete an Expense")
        print("7. View Total Expense")
        print("8. Show Monthly Chart")
        print("9. Monthly Summary")
        print("10. Exit")

        choice = input("Enter your choice (from 1 to 10): ")

        if choice == "1":
            try:
                amount = float(input("Enter amount in rupees: "))
                categories = get_categories()
                for i in range(len(categories)):
                    print(str(i + 1) + ". " + categories[i])
                cat_choice = int(input("Choose category number: "))
                category = categories[cat_choice - 1]

                date = None
                while not date:
                    d = input("Enter date (yyyy-mm-dd): ")
                    date = validate_date_input(d)

                desc = input("Enter description: ")
                add_expense(conn, amount, category, date, desc)
                print(" Expense added.")

            except:
                print("Error occurred. Try again.")

        elif choice == "2":
            print("\nAll Expenses:")
            expenses = get_all_expenses(conn)
            print_expenses(expenses)

        elif choice == "3":
            categories = get_categories()
            for i in range(len(categories)):
                print(str(i + 1) + ". " + categories[i])
            cat_choice = int(input("Choose category number: "))
            category = categories[cat_choice - 1]
            print("\nExpenses in category: " + category)
            print_expenses(get_expenses_by_category(conn, category))

        elif choice == "4":
            start = input("Start date (yyyy-mm-dd): ")
            end = input("End date (yyyy-mm-dd): ")
            print("\nExpenses from " + start + " to " + end)
            print_expenses(get_expenses_by_date_range(conn, start, end))

        elif choice == "5":
            keyword = input("Search using keyword: ")
            print("\nMatching expenses:")
            print_expenses(search_expenses_by_description(conn, keyword))

        elif choice == "6":
            try:
                eid = int(input("Enter expense ID to delete: "))
                delete_expense(conn, eid)
                print("Expense deleted.")
            except:
                print("Error while deleting.")

        elif choice == "7":
            total = get_total_expense(conn)
            print(" Total spent: ₹" + str(round(total, 2)))

        elif choice == "8":
            data = get_monthly_expenses(conn)
            if len(data) == 0:
                print("No data to plot.")
            else:
                months = []
                totals = []
                for row in data:
                    months.append(row[0])
                    totals.append(row[1])
                plt.bar(months, totals, color="pink")
                plt.xlabel("Month")
                plt.ylabel("Total Spent")
                plt.title("Monthly Expenses")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()

        elif choice == "9":
            data = get_monthly_expenses(conn)
            if len(data) == 0:
                print("No data available.")
            else:
                print("\nMonth-wise Summary:")
                for row in data:
                    print("Month: " + row[0] + "  | Total: ₹" + str(round(row[1], 2)))

        elif choice == "10":
            print("Bye bye!")
            break

        else:
            print("Invalid option. Try again.")

    conn.close()
main()
