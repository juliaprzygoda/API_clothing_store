from flask import Flask
from datetime import datetime
from flask import request, jsonify
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlitedb.file'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 0

db = SQLAlchemy(app)


# create tables within database
class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email_address = db.Column(db.String(100))
    address = db.Column(db.String(200))
    # add attriutes for relationships
    purchase = db.relationship('Transaction')

    def __repr__(self):
        return f'''Customer({self.customer_id}, {self.email_address}, {self.first_name} {self.last_name}
                shipping address: {self.address})'''


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50))
    product_price = db.Column(db.Integer)
    product_size = db.Column(db.String(2))
    quantity = db.Column(db.Integer)
    purchase = db.relationship('Transaction')

    def __repr__(self):
        return f'Product ({self.product_id}, {self.product_name}, {self.product_price}$ ,{self.quantity})'

    def update_product(self, quantity):
        assert isinstance(quantity, int), f"Quantity must be a number"
        self.quantity += quantity
        return self



class Transaction(db.Model):
    __tablename__ = 'transaction'
    transactions_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.product_id"))
    date = db.Column(db.DateTime)

    def __repr__(self):
        return f'''Transaction {self.transactions_id}, customer: {self.customer_id}, 
        on: {self.date}, product: {self.product_id}'''


# define possible routes
@app.route("/get_all_products", methods=["GET"])
def get_all_products():
    products = Product.query.all()
    products_l = []

    for product in products:
        products_l.append(
            {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_price": product.product_price,
                "product_size": product.product_size,
                "quantity": product.quantity,
            }
        )
    return jsonify(products_l), 200


@app.route("/get_one_product_by_name/<product_name>", methods=["GET"])
def get_one_product_by_name(product_name):

    product_query = Product.query.filter_by(product_name=product_name).first()
    product = {
         "product_id": product_query.product_id,
         "product_name": product_query.product_name,
         "product_price": product_query.product_price,
         "product_size": product_query.product_size,
         "quantity": product_query.quantity,

     }
    return jsonify(product), 200


@app.route("/add_new_product", methods=["POST"])
def add_new_product():
    product_data = request.get_json()
    new_product = Product(
        product_name=product_data["product_name"], product_price=product_data["product_price"],
        product_size=product_data["product_size"], quantity=product_data["quantity"]
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product successfully created"}), 200


@app.route("/update_product/<product_id>", methods=["POST"])
def update_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first()
    product_data = request.get_json()

    # Modify quantity and/or price
    if product.update_product(product_data["quantity"]):
        db.session.commit()
        return jsonify({"message": "Product successfully updated"}), 200

    return jsonify({"message": "Error try again"}), 503


@app.route("/delete_whole_product/<product_id>", methods=["DELETE"])
def delete_whole_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first()
    db.session.delete(product)
    db.session.commit()
    return jsonify({}), 200


@app.route("/get_all_customers", methods=["GET"])
def get_all_customers():
    customers = Customer.query.all()
    customers_l = []

    for customer in customers:
        customers_l.append(
            {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email_address": customer.email_address,
                "address": customer.address,
            }
        )
    return jsonify(customers_l), 200


@app.route("/get_one_customer/<customer_id>", methods=["GET"])
def get_one_customer(customer_id):
    customer_query = Customer.query.filter_by(customer_id=customer_id).first()
    customer = {
        "customer_id": customer_query.customer_id,
        "first_name": customer_query.first_name,
        "last_name": customer_query.last_name,
        "email_address": customer_query.email_address,
        "address": customer_query.address,

    }
    return jsonify(customer), 200


@app.route("/add_new_customer", methods=["POST"])
def add_new_customer():
    customer_data = request.get_json()
    new_customer = Customer(
        first_name=customer_data["first_name"], last_name=customer_data["last_name"],
        email_address=customer_data["email_address"], address=customer_data["address"]
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message":"Customer successfully created"}), 200


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    transaction_data = request.get_json()
    new_transaction = Transaction(
        customer_id=transaction_data["customer_id"], product_id=transaction_data["product_id"],
        date=datetime.now()
    )
    db.session.add(new_transaction)
    # update products table
    product = Product.query.filter_by(product_id=transaction_data["product_id"]).first()
    product.update_product(-1)
    db.session.commit()

    return jsonify({"message": "Transaction successfully recorded"}), 200


@app.route("/list_10_newest_transactions", methods=["GET"])
def list_10_newest_transactions():
    transactions = Transaction.query.order_by(desc(Transaction.date)).limit(10)
    transactions_l = []

    for transaction in transactions:
        transactions_l.append({
            "customer_id": transaction.customer_id,
            "product_id": transaction.product_id,
            "date": transaction.date
        })

    return jsonify(transactions_l), 200


@app.route("/get_transactions_on_given_date/<year>/<month>", methods=["GET"])
def get_transactions_on_given_date(year, month):
    transactions = Transaction.query.all()
    transactions_l = []

    for transaction in transactions:
        if transaction.date.year == int(year) and transaction.date.month == int(month):
            transactions_l.append({
                "customer_id": transaction.customer_id,
                "product_id": transaction.product_id,
                "date": transaction.date
            })

    return jsonify(transactions_l), 200


if __name__ == '__main__':
    app.run()
