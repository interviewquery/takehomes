# initialize ngrok...

import yaml
import os
import subprocess
import sqlite3
from flask import Flask, render_template, request, g
from flask_ngrok import run_with_ngrok


# makes sure that the tokens run properly
def token_run():
    def get_ngrok_token_from_yml():
        with open('ngrok.yml', 'r') as yml_file:
            config = yaml.safe_load(yml_file)
            return config.get('authtoken', None)

    ngrok_token = get_ngrok_token_from_yml()
    if ngrok_token:
        os.environ['NGROK_AUTH_TOKEN'] = ngrok_token

    def set_ngrok_token(token):
        command = f"./ngrok authtoken {token}"
        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print("Token set successfully!")
        else:
            print("Failed to set token. Error:", result.stderr)

    token = get_ngrok_token_from_yml()
    if token:
        set_ngrok_token(token)
    else:
        print("Token not found in ngrok.yml!")


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('your_database.db')
        g.db.row_factory = sqlite3.Row  # This will allow us to access rows as dictionaries
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def main():
    token_run()
    run_with_ngrok(app)  # This line is added to make Flask work with ngrok
    app.run()


app = Flask(__name__)

if __name__ == "__main__":
    main()


# ROUTES
# Define your endpoints in this section

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

