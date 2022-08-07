from flask import Flask
from faker import Faker
from random import randrange
import app as application
from app import db

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlitedb.file'  # contect to the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 0

faker = Faker()

# Generate dummy users
for i in range(250):
    first_name = faker.name()
    last_name = faker.last_name()
    email_address = f'{first_name[0].lower()}{last_name.lower()}@email.com'
    address = faker.address()
    add_customer = application.Customer(
        first_name=first_name, last_name=last_name,
        email_address=email_address, address=address
    )
    db.session.add(add_customer)
    db.session.commit()

# Generate dummy product names
product_names = ['Black jeans', 'Scarf', 'Sweater', 'Hat', 'Jacket', 'Blouse', 'Shirt', 'Dress', 'Skirt', 'Sportswear',
                 'Socks', 'Underwear', 'Swimsuit', 'Pants', 'Winter jacket', 'Coat', 'Nightwear', 'Sweatpants',
                 'Necklace', 'Gloves']

product_sizes = ['S', 'M', 'L', 'XL']

for i in range(len(product_names)):
    product_name = product_names[i]
    product_price = randrange(20, 200, 10)
    product_size = product_sizes[randrange(0, len(product_sizes) - 1, 1)]
    quantity = randrange(1, 1000)
    add_product = application.Product(
        product_name=product_name, product_price=product_price,
        product_size=product_size, quantity=quantity
    )
    db.session.add(add_product)
    db.session.commit()

# Generate dummy transactions
for i in range(1000):
    customer_id = randrange(1, 250)
    product_id = randrange(1, len(product_names) - 1)
    date = faker.date_time()
    add_transaction = application.Transaction(
        customer_id=customer_id, product_id=product_id,
        date=date
    )
    db.session.add(add_transaction)
    db.session.commit()
