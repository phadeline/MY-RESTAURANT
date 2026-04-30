from fastapi import FastAPI, HTTPException
import sqlite3

import init_db

from pydantic import BaseModel
app = FastAPI()



def start_db():
    connection = sqlite3.connect("db.sqlite", timeout=20)
    cursor = connection.cursor()
    return (connection, cursor)

def end_db(connection):
    connection.commit()
    connection.close()

#deserialization is the process of converting data from a format that can be easily stored or transmitted (like JSON or XML) back into a format that can be used by a program (like a Python object). In this code, we are using Pydantic's BaseModel to define a Customer class that has two attributes: name and phone. When we receive a POST request to create a new customer, FastAPI will automatically deserialize the incoming JSON data into an instance of the Customer class, allowing us to easily access the customer's name and phone number in our code.
class Customer(BaseModel):
    name: str
    phone: str

class Item(BaseModel):
    id: int
    name: str
    price: float    

class Order(BaseModel):
    timestamp: str
    customer_id: int
    notes: str
    items: list[Item]


# async means that the function can be paused and resumed, allowing other tasks to run while waiting for a response. This is particularly useful in web applications where you may have multiple requests being handled simultaneously. By using async, you can improve the performance and responsiveness of your application by not blocking the execution of other tasks while waiting for a response from a database or an external API.
@app.get("/customers/{id}")
async def get_customer(id: int):
    (connection, cursor) = start_db()
    row = cursor.execute("SELECT * FROM customers WHERE id=?;", (id,)).fetchone()
    end_db(connection)
    if row == None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row

@app.get("/customers")
async def get_all_customers():
    (connection, cursor) = start_db()
    cursor.execute("SELECT * FROM customers;")
    result = cursor.fetchall()
    end_db(connection)
    return result

@app.put("/customers/{id}")
async def update_customer(id: int, customer: Customer):
    (connection, cursor) = start_db()
    cursor.execute("SELECT * FROM customers WHERE id=?;", (id,))
    if cursor.fetchone() == None:
        end_db(connection)
        raise HTTPException(status_code=404, detail="Customer not found")
    cursor.execute("UPDATE customers SET name=?, phone=? WHERE id=?;", (customer.name,  customer.phone, id))
    end_db(connection)
    return {"message": "Customer updated"}
         

@app.delete("/customers/{id}")
async def delete_customer(id: int):
    (connection, cursor) = start_db()
    cursor.execute("DELETE FROM customers WHERE id=?;", (id,))
    end_db(connection)
    return {"message": "Customer deleted"}

@app.post("/customers")
async def new_customer(customer: Customer):
    (connection, cursor) = start_db()
    cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?);", (customer.name, customer.phone))
    end_db(connection)
    return {"message": "Customer added"}

@app.get("/orders")
async def get_all_orders(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    (connection, cursor) = start_db()
    rows = cursor.execute("""
        SELECT o.id, o.timestamp, o.customer_id, c.name, o.notes, i.id, i.name, i.price
        FROM (SELECT id, timestamp, customer_id, notes FROM orders LIMIT ? OFFSET ?) o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN item_list il ON o.id = il.order_id
        LEFT JOIN items i ON il.item_id = i.id
        ORDER BY o.id;
    """, (limit, offset)).fetchall()
    end_db(connection)

    orders = {}
    for order_id, ts, customer_id, customer_name, notes, item_id, item_name, price in rows:
        if order_id not in orders:
            orders[order_id] = {"id": order_id, "timestamp": ts, "customer_id": customer_id, "customer_name": customer_name, "notes": notes, "items": []}
        if item_id is not None:
            orders[order_id]["items"].append({"id": item_id, "name": item_name, "price": price})

    return list(orders.values())




    
    