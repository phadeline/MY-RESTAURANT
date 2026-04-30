import sqlite3
import json

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

script = """
    CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name CHAR(64) NOT NULL, phone CHAR(10) NOT NULL);
    CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name CHAR(64) NOT NULL, price REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, customer_id INTEGER NOT NULL, notes TEXT);
    CREATE TABLE IF NOT EXISTS item_list (order_id NOT NULL, item_id NOT NULL, FOREIGN KEY(order_id) REFERENCES orders(id), FOREIGN KEY(item_id) REFERENCES items(id));
"""
cursor.executescript(script)

customers = {}
items = {}
with open("example_orders.json") as data:
    all_orders = json.load(data)
for order in all_orders:
    if order["phone"] not in customers:
        customers[order["phone"]] = order["name"]
    for item in order["items"]:
        name = item["name"]
        price = item["price"]
        if name not in items:
            items[name] = price 





for phone in customers:
    name = customers[phone]
  
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?);", (name, phone))
for name in items:
    price = items[name]
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?);", (name, price))

for order in all_orders:
    ts = order["timestamp"]
    notes = order["notes"]
    phone = order["phone"]
    customer_id = cursor.execute("SELECT id FROM customers WHERE phone=?",(phone,)).fetchone()[0]
    cursor.execute("INSERT INTO orders (timestamp, customer_id, notes) VALUES(?, ?, ?);", (ts, customer_id, notes))
    order_id = cursor.lastrowid
    for item in order["items"]:
        name = item["name"]
        item_id = cursor.execute("SELECT id FROM items WHERE name=?",(name,)).fetchone()[0]
        cursor.execute("INSERT INTO item_list (order_id, item_id) VALUES (?, ?);",(order_id, item_id))


connection.commit()
connection.close()