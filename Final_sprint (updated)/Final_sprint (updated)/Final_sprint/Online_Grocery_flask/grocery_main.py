import requests.cookies
from flask import *
import sqlite3
import string
from datetime import date
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key'

conn=sqlite3.connect('database.db')
res=conn.execute('select * from customers').fetchall()
print(res)

# Function to create an order
def create_order(payment_method, transaction_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    session['td']=transaction_id
    session['pm']=payment_method
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        orderid INTEGER PRIMARY KEY AUTOINCREMENT,
        orderdate TEXT,
        cid INTEGER NOT NULL,
        pid INTEGER,
        pname TEXT,
        quantity INTEGER,
        totalprice REAL,
        payment_method TEXT,
        transaction_id TEXT,
        checkoutstatus TEXT
    );''')
    user_id=session.get('user_id')
    print(type(user_id))
    items=conn.execute('select * from cart where cid=?',(user_id,)).fetchall()
    for item in items:
        cursor.execute('INSERT INTO orders (orderdate, cid, pid, pname, quantity, totalprice, payment_method, transaction_id, checkoutstatus) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',(date.today(), session.get('user_id'), item[0], item[2], item[4],item[6], payment_method, transaction_id, 'booked'))
        conn.commit()
    conn.execute('delete from cart where cid=? ', (user_id,))
    conn.commit()
    conn.close()

@app.route('/transaction', methods=['POST', 'GET'])
def transaction_page():
    conn=sqlite3.connect('database.db')
    return render_template('transaction.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if request.method == 'POST':
        payment_option = request.form.get('payment_option')
        if payment_option == 'credit_debit':
            payment_message = "Payment successful. Thank you for your purchase!"
        elif payment_option == 'upi':
            payment_message = "Payment successful. Thank you for your purchase!"
        elif payment_option == 'net_banking':
            payment_message = "Payment successful. Thank you for your purchase!"
        elif payment_option == 'cod':
            payment_message = "Order placed successfully. You'll pay upon delivery."
        else:
            payment_message = "Invalid payment option selected."

        transaction_id = random.randint(15454555, 5454555554)
        if payment_option!='cod':
            create_order(payment_option, transaction_id)
        else:
            create_order(payment_option, 0)

    return render_template('invoice.html')
@app.route('/pay')
def pay():
    return render_template('payment_summary.html')
# Route for home page
@app.route('/home')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.htm', products=products)

# Route for displaying the orders page
@app.route('/orderspage', methods=['GET', 'POST'])
def orderpage():
    conn = sqlite3.connect('database.db')
    if request.method == 'POST' and 'cid' in request.form:
        customer_id = request.form['cid']
        query = 'SELECT * FROM orders WHERE cid = ?'
        res = conn.execute(query, (customer_id,)).fetchall()
    else:
        res = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('orders.html', orders=res)

# Route for user profile page
@app.route('/profile')
def profile():
    return render_template('profile.htm')

# Route for user logout
@app.route('/logout')
def logout():
    session.clear()
    print("Session Cleared.")
    return render_template('loginpage.htm')

# Route for user login page
@app.route('/register')
def register_page():
    return render_template('register.html')

# Route for user details validation
@app.route('/validation', methods=['POST'])
def validation():
    conn = sqlite3.connect('database.db')
    if request.method == 'POST':
        id = request.form['name']
        password = request.form['pass']
        res = conn.execute('select * from customers where ids=?', (id,)).fetchone()
        print(res)
        print((res[6]=='1' or res[6]=='Active'))
        if res and res[3] == password and (res[6]=='1' or res[6]=='Active'):
            session['user_id'] = res[0]
            session['user_name'] = res[1]
            session['user_email'] = res[2]
            session['user_password'] = res[3]
            session['user_address'] = res[4]
            session['user_phone'] = res[5]
            print("Login successful")
            return redirect('/home')

        elif res and res[3] == password  and res[6]=='Deactive':
            return render_template('Active.html')
        else:
            message_flashed = "invalid Credentials"
            print("invalid credentials")
            return render_template('loginpage.htm', message=message_flashed)

# Route for user details validation page
@app.route('/validate', methods=['POST'])
def validate_page():
    def check(password):
        has_uppercase = False
        has_lowercase = False
        has_special = False
        for char in password:
            if char.isupper():
                has_uppercase = True
            elif char.islower():
                has_lowercase = True
            elif char in string.punctuation:
                has_special = True
        return has_uppercase and has_special and has_lowercase and len(password) >= 8

    status = True
    if request.method == 'POST':
        name = request.form['name']
        if not name.isalpha():
            status = False
            message = "Name must contain only Alphabets"
            return render_template('register.html', message=message)
        else:
            status = True
        email = request.form['email']
        if '@' and '.' not in email:
            status = False
            message = "invalid email"
            return render_template('register.html', message=message)
        else:
            status = True
        password = request.form['pass']
        if not check(password):
            status = False
            message = "invalid password"
            return render_template('register.html', message=message)
        else:
            status = True
        address = request.form['add']
        pnumber = request.form['phone']
        if not len(str(pnumber)) == 10:
            status = False
            message = "invalid phone number"
            return render_template('register.html', message=message)
        else:
            status = True

        conn = sqlite3.connect('database.db')
        if conn and status:
            conn.execute('''CREATE TABLE IF NOT EXISTS customers (
                ids INTEGER PRIMARY KEY,
                name VARCHAR(20),
                email VARCHAR(30),
                password VARCHAR(20),
                address VARCHAR(20),
                pnumber INTEGER,
                status VARCHAR(10) DEFAULT 'Active'
            );''')
            ids = random.randint(1000, 99999)
            conn.execute('insert into customers values(?,?,?,?,?,?,?)', (ids, name, email, password, address, pnumber,status))
            conn.commit()
    return render_template('register.html', ids=ids)

# Route for admin validation
@app.route('/admin_validation', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        print("Entered")
        name = request.form['name']
        password = request.form['pass']
        print(name)
        print(password)
        conn = sqlite3.connect('database.db')
        res = conn.execute('select * from admin where id=? and name=?', (name, password)).fetchone()
        if res:
            print("Login successful")
            return render_template('product.html')
        else:
            print("invalid credentials")
            message_flashed = "invalid Credentials"
            return render_template('admin_panel.html', message=message_flashed)

# Route for updating product category
@app.route('/update_category', methods=['POST'])
def category():
    if request.method == 'POST':
        category = request.form['category']
    else:
        category = request.args.get('category')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('update_products.html', products=products)

# Route for updating product details
@app.route('/update_product', methods=['POST'])
def update():
    id = request.form['pid']
    pname = request.form['pname']
    price = request.form['price']
    category = request.form['category']
    conn = sqlite3.connect('database.db')
    conn.execute('UPDATE products SET pname=?, price=?, category=? WHERE pid=?', (pname, price, category, id))
    conn.commit()
    conn.close()
    return redirect('/update_products')

# Route for displaying updated products
@app.route('/update_products')
def update_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('update_products.html', products=products)

# Route for deleting a product
@app.route('/delete_product', methods=['POST'])
def delete_product():
    id = request.form['id']
    conn = sqlite3.connect('database.db')
    conn.execute('DELETE FROM products WHERE pid=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/update_products')

# Route for adding a new product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        pname = request.form['pname']
        price = request.form['price']
        category = request.form['category']
        image = request.files['image']
        if image:
            image.save('static/uploads/' + image.filename)
            image_url = 'static/uploads/' + image.filename
            conn = sqlite3.connect('database.db')
            conn.execute('INSERT INTO products (pname, price, category, image_url) VALUES (?, ?, ?, ?)',
                         (pname, price, category, image_url))
            conn.commit()
            conn.close()
    return render_template('product.html')

# Route for admin login page
@app.route('/admin')
def main():
    return render_template('admin_panel.html')

# Route for displaying products
@app.route('/products', methods=['POST', 'GET'])
def view_products():
    if request.method == 'POST':
        category = request.form['category']
    else:
        category = request.args.get('category')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('view_products.html', products=products)

# Route for the register page
@app.route('/')
def login():
    return render_template('loginpage.htm')

@app.route('/customers', methods=['GET', 'POST'])
def admin_customers():
    conn = sqlite3.connect('database.db')
    if request.method == 'POST' and 'cid' in request.form:
        customer_id = request.form['cid']
        query = 'SELECT * FROM customers WHERE ids= ?'
        cust = conn.execute(query, (customer_id,)).fetchall()
    else:
        cust = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('customers.html', customers=cust)

# Route for updating user profile
@app.route('/user_profile', methods=['POST'])
def user_profile():
    if request.method == 'POST':
        if 'update' in request.form:
            id = request.form['id']
            print(id)
            name = request.form['name']
            email = request.form['email']
            password = request.form['pass']
            add = request.form['add']
            phone = request.form['phone']
            session['user_name'] = name
            session['user_email'] = email
            session['user_password'] = password
            session['user_address'] = add
            session['user_phone'] = phone
            print("updated session successfully")
            conn = sqlite3.connect('database.db')
            conn.execute('update customers set name=? ,email=?, password=? ,address=? ,pnumber=? where ids=?',
                         (name, email, password, add, phone, id))
            conn.commit()
            conn.close()
        return render_template('profile.htm')

# Route for updating customers by admin
@app.route('/update_customers', methods=['POST'])
def update_Customer():
    if request.method == 'POST':
        if 'update' in request.form:
            id = request.form['id']
            print(id)
            name = request.form['name']
            email = request.form['email']
            password = request.form['pass']
            add = request.form['add']
            phone = request.form['phone']
            conn = sqlite3.connect('database.db')
            conn.execute('update customers set name=? ,email=?, password=? ,address=? ,pnumber=? where ids=?',
                         (name, email, password, add, phone, id))
            conn.commit()
            conn.close()
            return redirect('/customers')

# Route for deleting a customer
@app.route('/delete_customer', methods=['POST'])
def delete_Customer():
    if request.method == 'POST':
        customer_id = request.form['id']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customers WHERE ids = ?', (customer_id,))
        conn.commit()
        conn.close()
        return redirect('/customers')
@app.route('/increment',methods=['POST'])
def increment():
    if request.method=='POST':
        id=request.form['id']
        conn=sqlite3.connect('database.db')
        res=conn.execute('select quantity,price from cart where pid=? and cid=?',(id,session.get('user_id'))).fetchone()
        if res[0] <=101:
            a = res[0] + 1
            p = res[1] * a
            conn.execute('update cart set quantity=?,total_price=? where pid=? and cid=?', (a, p, id, session.get('user_id')))
            conn.commit()
        conn.close()
    return redirect('/cart')

@app.route('/remove',methods=['POST','GET'])
def remove():
    if request.method=='POST':
        id = request.form['id']
        conn = sqlite3.connect('database.db')
        conn.execute('delete from cart where pid=? and cid=?',(id,session.get('user_id'),))
        conn.commit()
        conn.close()
        return redirect('/cart')
    else:
        return redirect('/cart')

@app.route('/decrement1', methods=["POST","GET"])
def decrement1():
    if request.method == 'POST':
        id = request.form['id']
        conn = sqlite3.connect('database.db')
        res = conn.execute('SELECT quantity, price FROM cart WHERE pid=? AND cid=?', (id, session.get('user_id'))).fetchone()
        print(res[0],res[1])
        if res and res[0] > 1:
            print("hell")
            new_quantity = res[0] - 1
            new_total_price = res[1] * new_quantity
            conn.execute('UPDATE cart SET quantity=?, total_price=? WHERE pid=? AND cid=?', (new_quantity, new_total_price, id, session.get('user_id')))
            conn.commit()
        conn.close()
        return redirect('/cart')
    else:
        return redirect('/cart')




@app.route('/add_to_cart', methods=["POST","GET"])
def add_cart():
    if request.method == 'POST':
        item_id = request.form['itemid']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        product = cursor.execute('SELECT * FROM products WHERE pid = ?', (item_id,)).fetchone()
        if product:
            res=conn.execute('select * from cart where pid=? and cid=?',(item_id,session.get('user_id'))).fetchall()
            if res:
                quan=res[4]+1
                conn.execute('insert into cart values(?,?,?,?,?,?,?)', (item_id, session.get('user_id'), product[1], product[4],quan, product[2], (quan*product[2])))
                conn.commit()
            else:
                conn.execute('insert into cart values(?,?,?,?,?,?,?)',(item_id,session.get('user_id'),product[1],product[4],1,product[2],product[2]))
                conn.commit()
        conn.close()
    return redirect('/home')

# Route for viewing cart
@app.route('/cart')
def view_cart():
    conn=sqlite3.connect('database.db')
    cart_items=conn.execute('select * from cart').fetchall()
    total_price = conn.execute('select sum(total_price) from cart').fetchone()
    conn.close()
    session['tp']=total_price[0]
    return render_template('cart.htm', cart_items=cart_items,total_price=total_price[0])

# Route for updating cart and checkout
@app.route('/update_cart', methods=["POST"])
def update_cart():
        payment_method = request.form.get('payment_option')
        transaction_id = random.randint(15454555, 5454555554)
        if payment_method != 'cod':
            create_order( payment_method, transaction_id)
            return redirect('/cart')
        else:
            create_order(payment_method, "cash on")
        return redirect('/cart')
#***************Deactivate Account*******************************
@app.route('/deactivate_account', methods=['POST','GET'])
def deactivate_account():
    if request.method=='POST':
        conn = sqlite3.connect('database.db')
        r=request.form['Deactive']
        print(session.get('user_id'))
        id=session.get('user_id')
        conn.execute('UPDATE customers SET status = ? WHERE ids = ?', (r,id ))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        return redirect('/')

#***************Restore Account********************************
@app.route('/restore_account', methods=['POST'])
def restore_account():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        print(session.get('user_id'))
        id = session.get('user_id')
        conn.execute('UPDATE customers SET status = ? WHERE ids = ?', ('Active', id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.run(debug=True)