import sqlite3
import pip

# run this file first to install the required dependencies

dependency_list = ['flask', 'ngrok', 'flask-ngrok']


def create_ngrok_yml():
    token = input("Enter your ngrok token: ")
    with open("ngrok.yml", "w") as yml_file:
        yml_file.write(f"authtoken: {token}")
    print("ngrok.yml file has been created successfully!")



def main():
    create_ngrok_yml()
    print('Now retrieving project dependencies...')
    for dependency in dependency_list:
        print('Installing package:', dependency)
        pip.main(['install', dependency])
        print('Installed package:', dependency)

    print('Now creating the database')

    # Connect to the database or create one if it doesn't exist
    conn = sqlite3.connect('your_database.db')

    query = [
        """
        -- Create the orders table
        CREATE TABLE IF NOT EXISTS orders (
            orderID INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer_Name TEXT NOT NULL
        );
        """,
        """
        -- Create the items table
        CREATE TABLE IF NOT EXISTS items (
            itemID INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL  -- Ensure no duplicate items by name
        );
        """,
        """
        -- Create the order_items junction table
        CREATE TABLE IF NOT EXISTS order_items (
            orderID INTEGER,
            itemID INTEGER,
            FOREIGN KEY (orderID) REFERENCES orders(orderID) ON DELETE CASCADE, 
            FOREIGN KEY (itemID) REFERENCES items(itemID) ON DELETE CASCADE,
            PRIMARY KEY (orderID, itemID)  -- Composite primary key
        );
        """
    ]

    cursor = conn.cursor()
    for q in query:
        cursor.execute(q)

    items = ['Burger', 'Fried Chicken', 'Soda', 'Ice Cream']
    for item in items:
        print('inserting', item)
        cursor.execute(f"SELECT 1 FROM items WHERE item_name=?", (item,))
        result = cursor.fetchall()
        print(len(result))
        if len(result) == 0:
            cursor.execute("INSERT INTO items (item_name) VALUES (?);", (item,))
            print('inserted', item)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
