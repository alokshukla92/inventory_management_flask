from inventory_app import db
from datetime import datetime

class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key = True)
    prod_id = db.Column(db.String(20),unique = True ,nullable = False)
    product_name = db.Column(db.String(20),unique = True ,nullable = False)
    product_description =  db.Column(db.String(50))
    product_price = db.Column(db.Numeric(10,2))

class location(db.Model):
    location_id = db.Column(db.Integer, primary_key = True)
    location_name = db.Column(db.String(20),unique = True, nullable = False)

class product_movement(db.Model):
    movement_id = db.Column(db.Integer, primary_key= True,nullable = False)
    product_name = db.Column(db.String(20),nullable = False)
    from_location = db.Column(db.String(20),nullable = True)
    to_location = db.Column(db.String(20), nullable=True)
    quantity = db.Column(db.Integer, nullable = False)

class productLog(db.Model):
    log_id = db.Column(db.Integer, primary_key= True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(20),nullable = True)
    to_location = db.Column(db.String(20),nullable = True)
    product_name = db.Column(db.String(20),nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    action = db.Column(db.String(20))
