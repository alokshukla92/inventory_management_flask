from flask import  render_template,request,url_for,redirect
from flask.helpers import flash, url_for
from sqlalchemy.exc import IntegrityError, InternalError
from sqlalchemy import func

from inventory_app import app,db
from inventory_app.models import Product,location,product_movement,productLog

@app.route('/')
def home_page():
   products = Product.query.all()
   return render_template('index.html',products = products)

@app.route('/product/add', methods=['POST'])
def add_product():
   formObj = request.form
   product_name = formObj["product_name"]
   product = Product(prod_id="PRO",
                     product_name=product_name,
                     product_description=formObj["product_description"],
                     product_price=formObj["product_price"])
   db.session.add(product)
   try:
      db.session.commit()
      prod_id = "PRO_"+(product_name[0:5]).upper()+"_"+str(product.product_id)
      product.prod_id = prod_id
      db.session.commit()
   except IntegrityError:
      print("Exceptionn") #since product alreay exists
   return redirect(url_for('home_page'))

@app.route('/product/update', methods=['POST'])
def update_product():
   formObj = request.form
   Product.query.filter_by(product_id=int(formObj["product_id"])).update(dict(product_name=formObj["product_name"],product_description=formObj["product_description"],product_price=float(formObj["product_price"])))
   product_movement.query.filter_by(product_name=formObj["actual_product_name"]).update(dict(product_name=formObj["product_name"]))
   productLog.query.filter_by(product_name=formObj["actual_product_name"]).update(dict(product_name=formObj["product_name"]))
   try:
      db.session.commit()
   except InternalError:
      print("Exceptionn") #since product alreay exists
   return redirect(url_for('home_page'))

@app.route('/product/delete', methods=['GET'])
def delete_product():
   product_id = int(request.args.get("product_id"))
   Product.query.filter_by(product_id=product_id).delete()
   db.session.commit()
   return redirect(url_for('home_page'))

@app.route('/locations')
def locations_page():
   locations = location.query.all()
   return render_template('locations.html',locations=locations)

@app.route('/location/add', methods=['POST'])
def add_location():
   formObj = request.form
   location_name = formObj["location_name"]
   loc = location(location_name=location_name)
   db.session.add(loc)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn") #since location alreay exists
   return redirect(url_for('locations_page'))

@app.route('/location/update', methods=['POST'])
def update_location():
   formObj = request.form
   location.query.filter_by(location_id=int(formObj["location_id"])).update(dict(location_name=formObj["location_name"]))
   product_movement.query.filter_by(from_location=formObj["actual_location_name"]).update(dict(from_location=formObj["location_name"]))
   productLog.query.filter_by(product_name=formObj["actual_location_name"]).update(dict(product_name=formObj["location_name"]))
   try:
      db.session.commit()
   except InternalError:
      print("Exceptionn") #since location alreay exists
   return redirect(url_for('locations_page'))

@app.route('/location/delete', methods=['GET'])
def delete_location():
   location_id = int(request.args.get("location_id"))
   location.query.filter_by(location_id=location_id).delete()
   db.session.commit()
   return redirect(url_for('locations_page'))

@app.route('/product_movement')
def product_movement_page():
   products_options = Product.query.with_entities(Product.product_name).all()
   locations_options = location.query.with_entities(location.location_name).all()
   product_movements = product_movement.query.order_by(product_movement.to_location.desc(),
                                                       product_movement.product_name.desc()).all()
   print(product_movements)
   return render_template('product_movements.html',product_movements=product_movements,products_options=products_options,locations_options=locations_options)

@app.route('/product_movement/add', methods=['POST'])
def add_product_movement():
   formObj = request.form
   prod_movement = product_movement(product_name=formObj["product_name"],
                                       from_location=formObj["from_location"],
                                       to_location=formObj["to_location"],
                                       quantity=formObj["quantity"],
                                       )
   db.session.add(prod_movement)
   prodLog = productLog(product_name=formObj["product_name"],
                        from_location=formObj["from_location"],
                        to_location=formObj["to_location"],
                        quantity=formObj["quantity"],
                        action="ADDED")
   db.session.add(prodLog)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn")
   return redirect(url_for('product_movement_page'))


@app.route('/product_movement/update', methods=['POST'])
def update_product_movement():
   formObj = request.form
   print(formObj)
   product_movement.query.filter_by(movement_id=int(formObj["movement_id"])).update(dict(quantity=formObj["quantity"]))
   prodLog = productLog(product_name=formObj["product_name"],
                        from_location=formObj["from_location"],
                        to_location = formObj["to_location"],
                        quantity=formObj["quantity"],
                        action="UPDATED")
   db.session.add(prodLog)
   try:
      db.session.commit()
   except IntegrityError:
      print("Exceptionn")
   return redirect(url_for('product_movement_page'))

@app.route('/product_movement/delete', methods=['GET'])
def delete_product_movement():
   movement_id = int(request.args.get("movement_id"))
   alloationObj = product_movement.query.filter_by(movement_id=movement_id).first()
   print("alloationObj",alloationObj)
   product_movement.query.filter_by(movement_id=movement_id).delete()
   prodLog = productLog(product_name=alloationObj.product_name,
                        from_location=alloationObj.from_location,
                        to_location=alloationObj.to_location,
                        quantity=alloationObj.quantity,
                        action="DELETED")
   db.session.add(prodLog)
   db.session.commit()
   return redirect(url_for('product_movement_page'))

@app.route('/product_movement_log')
def product_movement_log_page():
   product_movement_logs = productLog.query.order_by(productLog.datetime.desc(),
                                                     productLog.from_location.desc(),
                                                     productLog.to_location.desc(),
                                                     productLog.product_name.desc()).all()
   return render_template('product_movement_log.html',product_movement_logs=product_movement_logs)

@app.route('/summary')
def summary():
   summary_by_product = product_movement.query.with_entities(product_movement.product_name, product_movement.to_location,
                                                             func.sum(product_movement.quantity).label('quantity')).group_by(product_movement.product_name, product_movement.to_location).all()

   return render_template('summary.html',summary_by_product=summary_by_product)
