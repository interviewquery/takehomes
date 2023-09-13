import sqlite3 as sql
import context
import csv
import sys
sys.path.append('/content/takehomes')

__implicit__conn__ = sql.connect(context.generate_path('iq.db'))
__module__conn__ = __implicit__conn__
__internal__cursor__ = __implicit__conn__.cursor()


def __linker__(sql_query: str):
    return __implicit__conn__.execute(sql_query)


# Normalized Tables
def create_tables_if_not_exists():
    print('[IQ Environment] Defining table schemas.')
    __implicit__conn__.execute("""
    CREATE TABLE IF NOT EXISTS Branches (
        BranchID INTEGER PRIMARY KEY AUTOINCREMENT,
        BranchName TEXT NOT NULL,
        City TEXT NOT NULL
    );
    """)
    __implicit__conn__.commit()

    # Creating Customers table
    __implicit__conn__.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerType TEXT NOT NULL,
        Gender TEXT NOT NULL,
        Rating REAL
    );
    """)
    __implicit__conn__.commit()

    # Creating Products table
    __implicit__conn__.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProductLine TEXT NOT NULL,
        UnitPrice REAL NOT NULL
    );
    """)
    __implicit__conn__.commit()

    # Creating Invoices table
    __implicit__conn__.execute("""
    CREATE TABLE IF NOT EXISTS Invoices (
        InvoiceID TEXT PRIMARY KEY,
        Date DATE NOT NULL,
        Time TIME NOT NULL,
        BranchID INTEGER,
        CustomerID INTEGER,
        PaymentMethod TEXT NOT NULL,
        Total REAL NOT NULL,
        cogs REAL NOT NULL,
        GrossMarginPercentage REAL NOT NULL,
        GrossIncome REAL NOT NULL,
        FOREIGN KEY (BranchID) REFERENCES Branches(BranchID),
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
    );
    """)
    __implicit__conn__.commit()

    # Creating InvoiceDetails table
    __implicit__conn__.execute("""
    CREATE TABLE IF NOT EXISTS InvoiceDetails (
        DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceID TEXT NOT NULL,
        ProductID INTEGER NOT NULL,
        Quantity INTEGER NOT NULL,
        Tax REAL NOT NULL,
        FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    );
    """)
    __implicit__conn__.commit()


def load_all():
    print('[IQ Environment] Checking if the data is already loaded.')
    result = __implicit__conn__.execute('SELECT 1 from customers')
    if result.fetchone() is None:
        print('[IQ Environment] Data is not loaded. Now loading data.')
        with open('dataset/sales.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # skip the header row

            for row in reader:
                invoice_id, branch_name, city, customer_type, gender, product_line, unit_price, quantity, tax, total, date, time, payment, cogs, gross_margin_percentage, gross_income, rating = row

                # Insert or ignore into Branches
                __internal__cursor__.execute("INSERT OR IGNORE INTO Branches (BranchName, City) VALUES (?, ?)",
                                             (branch_name, city))

                # Fetch branch_id
                __internal__cursor__.execute("SELECT BranchID FROM Branches WHERE BranchName=? AND City=?",
                                             (branch_name, city))
                branch_id = __internal__cursor__.fetchone()[0]

                # Insert or ignore into Customers
                __internal__cursor__.execute(
                    "INSERT OR IGNORE INTO Customers (CustomerType, Gender, Rating) VALUES (?, ?, ?)",
                    (customer_type, gender, rating))

                # Fetch customer_id
                __internal__cursor__.execute(
                    "SELECT CustomerID FROM Customers WHERE CustomerType=? AND Gender=? AND Rating=?",
                    (customer_type, gender, rating))
                customer_id = __internal__cursor__.fetchone()[0]

                # Insert or ignore into Products
                __internal__cursor__.execute("INSERT OR IGNORE INTO Products (ProductLine, UnitPrice) VALUES (?, ?)",
                                             (product_line, unit_price))

                # Fetch product_id
                __internal__cursor__.execute("SELECT ProductID FROM Products WHERE ProductLine=? AND UnitPrice=?",
                                             (product_line, unit_price))
                product_id = __internal__cursor__.fetchone()[0]

                # Insert or ignore into Invoices
                __internal__cursor__.execute("""
                    INSERT OR IGNORE INTO Invoices (InvoiceID, Date, Time, BranchID, CustomerID, PaymentMethod, Total, cogs, GrossMarginPercentage, GrossIncome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice_id, date, time, branch_id, customer_id, payment, total, cogs, gross_margin_percentage,
                      gross_income))

                # Insert into InvoiceDetails
                __internal__cursor__.execute("""
                    INSERT INTO InvoiceDetails (InvoiceID, ProductID, Quantity, Tax)
                    VALUES (?, ?, ?, ?)
                """, (invoice_id, product_id, quantity, tax))
                __module__conn__.commit()  # commit after each row to save changes
            print('[IQ Environment] Data loaded successfully.')
    print('[IQ Environment] Environment now ready for use.')


def init():
    create_tables_if_not_exists()
    load_all()
