# First, you need to install necessary packages in the Colab environment
!pip install flask-ngrok

import sqlite3
from flask import Flask, render_template, request, g
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)  # This line is added to make Flask work with ngrok

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('your_database.db')
        g.db.row_factory = sqlite3.Row  # This will allow us to access rows as dictionaries
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)  # This ensures the database is closed after each request

@app.route('/')
def index():
    # You need to provide an index.html template or use a simple string instead of the render_template function
    return render_template('index.html')

@app.route('/submit_order', methods=['POST'])
def order_now():
    db = get_db()
    cursor = db.cursor()

    name = request.form.get('customerName')
    items = request.form.getlist('item')

    try:
        # Insert the order first
        order_query = "INSERT INTO orders (customer_name) VALUES (?)"
        cursor.execute(order_query, (name,))
        db.commit()

        # Get the order ID
        id = cursor.lastrowid

        # Insert items associated with the order
        for item_name in items:
            item_query = "SELECT itemID FROM items WHERE lower(item_name) like  lower(?)"
            cursor.execute(item_query, (item_name,))
            item_id = cursor.fetchone()['itemID']

            order_item_query = "INSERT INTO order_items (orderID, itemID) values(?, ?)"
            cursor.execute(order_item_query, (id, item_id))
            db.commit()

        return f"<h1>Order from {name} for items {', '.join(items)} has been submitted successfully</h1>"

    except sqlite3.Error as e:
        return f"<h1>Error submitting order: {str(e)}</h1>"

if __name__ == "__main__":
    app.run()
