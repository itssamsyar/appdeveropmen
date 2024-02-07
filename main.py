import shelve
from flask import Flask, request, redirect, url_for, session, abort, flash, Response, jsonify
import flask
from wtforms import Form, StringField, validators
from werkzeug.utils import secure_filename
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_basicauth import BasicAuth
import pandas as pd
import json
from chatbot import get_response, get_user_messages
from couponID import *
import stripe

from classes import *

app = Flask(__name__)
user_db = UserDB('users.db')

UPLOAD_FOLDER = 'static/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "SolarGoods.com"
basic_auth = BasicAuth(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "146132031381-opdug4ajlrhvgi4ge0nea03fggf5d3cq.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email", "openid"
    ],
    redirect_uri="http://127.0.0.1:5000/callback")

#################
# strope things #
#################

app.config[
    'STRIPE_PUBLIC_KEY'] = 'pk_test_51OWYxsIRQCf8zri6cSaNl57vLvQjuDq6957haIz39wyetjMRIjwIJZkyOOHR91xxwTOFuUbczH7QYLXn4PxgxDLK009mfUgHKN'
app.config[
    'STRIPE_SECRET_KEY'] = 'sk_test_51OWYxsIRQCf8zri6TOiKK7ST666Cp2j2wBuInzeHWVDFd9iseb7lLdcipS8ERWm6QWe7C4Va0HlZnbFlcDQZpf9100T55bMI2c'

#################################################

stripe.api_key = app.config['STRIPE_SECRET_KEY']

app.config['BASIC_AUTH_USERNAME'] = 'SolarGoods Staff'
app.config['BASIC_AUTH_PASSWORD'] = 'nigel30voltron'



def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "google_id" not in session:
      return abort(401)
    else:
      return function()

  return wrapper


def allowed_file(filename):
  return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def render_template(url, **kwargs):
  return flask.render_template(url, **kwargs, username=session['username'])


#############################################
#            MAIN APP ROUTES                #
#############################################

@app.route('/')
def home():
  return flask.render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    # Password validations
    if len(password) < 8 or not any(
        char.isdigit() for char in password) or not any(char.isalpha()
                                                        for char in password):
      # message = 'Password requires at least:\n- 8 characters\n- 1 digit and 1 letter'
      message = 'Password requires at least:<br>- 8 characters<br>- 1 digit and 1 letter'
      print(message)
      return flask.render_template('register.html', message=message)

    if user_db.add_user(username, password):
      message = 'Registration successful. Please login.'
      return flask.render_template('login.html', message=message)
    else:
      message = 'Username already exists. Please choose a different username.'
      return flask.render_template('register.html', message=message)
  else:
    return flask.render_template('register.html')


##############################################################################################################


# normal user login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    user = user_db.get_user(username)

    if user and user.password == password:
      session['username'] = username
      return redirect(url_for('customer'))
    elif not user:
      message = 'User does not exist. Please register.'
      return render_template('login.html', message=message)
    else:
      message = 'Invalid username or password. Please try again or register.'
      return flask.render_template('login.html', message=message)
  else:
    return flask.render_template('login.html')


# staff login
@app.route("/stafflogin")
def stafflogin():
  authorization_url, state = flow.authorization_url()
  print(authorization_url, state)
  session["state"] = state
  return redirect(authorization_url)


# google api things for staff login
@app.route("/callback")
def callback():
  flow.fetch_token(authorization_response=request.url)

  if session["state"] != request.args["state"]:
    abort(500)

  credentials = flow.credentials
  request_session = requests.session()
  cached_session = cachecontrol.CacheControl(request_session)
  token_request = google.auth.transport.requests.Request(
      session=cached_session)

  id_info = id_token.verify_oauth2_token(id_token=credentials._id_token,
                                         request=token_request,
                                         audience=GOOGLE_CLIENT_ID)
  print("gay2")
  session["google_id"] = id_info.get("sub")
  session["name"] = id_info.get("name")
  return redirect("/protected_area")


# login end
###################################################################################################################


@app.route('/retrieve_user')
def retrieve_user():
  if 'username' in session:
    user = user_db.get_user(session['username'])
    return render_template('retrieve_user.html', user=user)
  else:
    return redirect(url_for('login'))


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
  if 'username' in session:
    username = session['username']
    user = user_db.get_user(username)

    form = UpdateUserForm(request.form)

    print(request.method, form.validate())

    if request.method == 'POST' and form.validate():
      new_username = form.username.data
      new_password = form.password.data
      new_email = form.email.data
      new_address = form.address.data
      new_phone_number = form.phone_number.data
      print(new_username, new_password, new_email, new_address,
            new_phone_number)

      # Handle profile picture upload
      if request.files['profile_picture']:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
          # Save the filename in the user's profile
          user.profile_picture = filename
          # Save the updated user object in the database
          user_db.update_user(username,
                              new_password,
                              new_email,
                              new_address,
                              new_phone_number,
                              profile_picture=filename)
      else:
        # Save the updated user object in the database without profile_picture
        user_db.update_user(username, new_password, new_email, new_address,
                            new_phone_number)

      message = 'User details updated successfully.'
      return render_template('update_user.html', user=user, message=message)
    else:
      return render_template('update_user.html', user=user, form=form)
  else:
    return redirect(url_for('login'))


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
  if 'username' in session:
    username = session['username']
    user = user_db.get_user(username)

    if request.method == 'POST':
      if user_db.delete_user(username):
        session.pop('username', None)
        message = 'Account deleted successfully.'
        return render_template('delete_user.html', message=message)
      else:
        message = 'Failed to delete account.'
        return render_template('delete_user.html', message=message)
    else:
      return render_template('delete_user.html')
  else:
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('login'))


@app.route('/customer')
def customer():
  if 'username' in session:
    user = user_db.get_user(session['username'])
    return render_template('customerPage.html', user=user)


@app.route('/createReport', methods=['GET', 'POST'])
def createReport():
  if 'username' in session:

    create_ReportForm = CreateReportForm(request.form)
    if request.method == 'POST' and create_ReportForm.validate():
      reports_dict = {}
      db = shelve.open('report.db', 'c')

      try:
        reports_dict = db['Reports']
      except:
        print("Error in retrieving Reports from report.db")

      report = Report(create_ReportForm.reportName.data,
                      create_ReportForm.reportDesc.data)
      reports_dict[report.get_reportID()] = report
      db['Reports'] = reports_dict

      db.close()
      return redirect(url_for("customer"))
    return render_template('createReport.html', form=create_ReportForm)
  else:
    return redirect(url_for('login'))


@app.route('/staff_retrieve_users')
def staff_retrieve_users():
  users_dict = {}
  db = shelve.open('users.db', 'c')
  if 'Users' in db:
    users_dict = db['Users']
  db.close()

  users_list = []
  for key in users_dict:
    user = users_dict.get(key)
    users_list.append(user)

  return flask.render_template('staff_retrieve_users.html',
                         count=len(users_list),
                         users_list=users_list)


###############################################################
# STAFF AREA
###############################################################


@app.route("/protected_area")
@login_is_required
@basic_auth.required
def protected_area():
  staff_name = session['name']
  return flask.render_template('staffdashboard.html', staff_name=staff_name)


@app.route('/retrieveReports')
def retrieveReports():
  reports_dict = {}
  db = shelve.open('report.db', 'c')
  reports_dict = db.get('Reports', {})
  db.close()

  reportsList = []
  for key in reports_dict:
    report = reports_dict.get(key)
    reportsList.append(report)

  return flask.render_template('retrieveReport.html',
                         count=len(reportsList),
                         reportsList=reportsList)

  # return render_template('retrieveReport.html', count=len(), reportsList=reportsList)


@app.route('/deleteReport/<int:id>', methods=['POST'])
def deleteReport(id):
  reports_dict = {}
  db = shelve.open('report.db', 'w')
  reports_dict = db['Reports']

  reports_dict.pop(id)

  db['Reports'] = reports_dict
  db.close()

  return redirect(url_for('retrieveReports'))


@app.route('/manage_users')
def manage_users():
  if 'google_id' in session:  # Check if staff is logged in using OAuth
    user_db = UserDB('users.db')
    users = user_db.get_all_users()

    # Add a print statement to check the content of 'users'
    print("Users:", users)

    return flask.render_template('manage_users.html', users=users)
  else:
    return redirect(url_for('login'))


@app.route('/export_users_excel')
def export_users_excel():
  user_db = UserDB('users.db')
  users = user_db.get_all_users()

  # Convert user data to a DataFrame
  user_data = []
  for user_dict in users:
    for username, user in user_dict.items():
      user_data.append({'Username': username, 'Email Address': user.email})

  df = pd.DataFrame(user_data)

  # Create Excel file
  excel_file_path = 'user_accounts.xlsx'
  df.to_excel(excel_file_path, index=False)

  # Serve the file as a download
  return Response(pd.read_excel(excel_file_path).to_csv(index=False),
                  mimetype="text/csv",
                  headers={
                      "Content-disposition":
                      "attachment; filename=user_accounts.csv"
                  })


@app.route('/delete_user/<username>', methods=['POST'])
def staff_delete_user(username):
  user_db = UserDB('users.db')

  # Check if the user exists
  if user_db.get_user(username):
    # Delete the user
    user_db.staff_delete_user(username)
    return redirect(url_for('manage_users'))
  else:
    # User not found
    flash('User not found', 'error')
    return redirect(url_for('manage_users'))

@app.route('/staff_query')
def staff_query():
  user_messages = get_user_messages()
  return flask.render_template('staff_query.html', user_messages=user_messages)

###############################################################
# Games
###############################################################
@app.route('/game')
def game():
  return render_template("gamebase.html")


@app.route('/jspython', methods=['POST'])
def test(): 
  username = session['username']
  output = request.get_json()
  result = json.loads(output)
  num = result.get("generate")
  game = result.get("game")
  date = result.get("date")
  time = result.get("time")
  if num != 0:  # if there is a need to generate code
    couponID = generate()
    couponCode = add(username, num, game, date, time)
    export()
    exportCoupon()
    return result, couponCode
  else:
    couponID = "-"
    couponCode = add(username, num, game, date, time)
    export()
    exportCoupon()
    return result

@app.route('/game1')
def game1():
  return render_template("1_Wheel.html")

@app.route('/game2')
def game2():
  return render_template("2_FlipCards.html")

'''
@app.route('/game3')
def game3():
    return render_template()
'''

@app.route('/game4')
def game4():
  return render_template("4_NumGuess.html")
###############################################################
# Chatbot
###############################################################


@app.post("/predict")
def predict():
  data = request.get_json()
  text = data.get("message")
  user = data.get("user")
  reply = get_response(text, user)
  response = {"reply": reply}
  # print(jsonify(response).data)
  # print(json.dumps(response))
  return json.dumps(response)


@app.get("/user_messages")
def user_messages():
  messages = get_user_messages()
  return render_template('user_messages.html', user_messages=messages)


##########################
# the thing i slide into #
##########################


@app.route('/mail', methods=["GET", "POST"])
@app.route('/mail/', methods=["GET", "POST"])
def mail():
  current_user = session['username']

  if request.method == "GET":
    mail_shelf = shelve.open("mail")
    my_mail = mail_shelf.get(current_user, {})

    mail_shelf.close()
    return render_template('mail.html', mails=my_mail)

  else:
    print(request.form)
    receiver = request.form.get("send-to")
    title = request.form.get('title')
    msg = request.form.get("msg")
    offer = request.form.get("offer", None)

    
    mail_shelf = shelve.open("mail")
    receiver_mail = mail_shelf.get(receiver, {})

    if receiver_mail:
      mail_id = list(receiver_mail)[-1] + 1
    else:
      mail_id = 0

    new_mail = Mail(current_user, title, msg, offer)

    receiver_mail[mail_id] = new_mail

    mail_shelf[receiver] = receiver_mail
    mail_shelf.close()

    return render_template('mail.html',
                           receiver=receiver,
                           title=title,
                           msg=msg,
                           offer=offer)


@app.route('/mail/<int:mail_id>')
def open_mail(mail_id):
  current_user = session['username']
  mail_shelf = shelve.open("mail")
  my_mail = mail_shelf[current_user]
  mail_shelf.close()
  print(my_mail)
  return render_template('mail.html', mails=my_mail, open_msg=my_mail[mail_id])


@app.route('/mail/send')
def send_mail():
  return render_template("send.html")


@app.route('/stripe_pay', methods=['GET', 'POST'])
def stripe_pay():
  # productID = request.form['purchasedProductID']
  # db = shelve.open('product.db', 'r')
  # products_dict = db['Products']
  # product = products_dict.get(productID)
  # db.close()

  price = 10
  session = stripe.checkout.Session.create(
      payment_method_types=['card'],
      line_items=[{
          'price_data': {
              'currency': 'sgd',
              'product_data': {
                  'name': 'product.get_productName()'
              },
              'unit_amount': int(float(price) * 100)
          },
          'quantity': 1,
      }],
      mode='payment',
      success_url=url_for('home', _external=True) +
      '?session_id={CHECKOUT_SESSION_ID}',
      cancel_url=url_for('home', _external=True),
  )
  return {
      'checkout_session_id': session['id'],
      'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
  }




####################################################################################################################################################################################################################################################################################################################################################################################
#Products Part

import dbm
from classes import Product
from threading import Lock


@app.route('/productCatalogue')
def productCatalogue():
  try:
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    productsList = []
    for key in products_dict:
      product = products_dict.get(key)
      productsList.append(product)

    all_users = user_db.get_users()
    allPurchasedProductIDList = []
    for userValue in all_users.values():
      for productID in userValue.savedProductIDList.get_purchasedIDList():
        if productID not in allPurchasedProductIDList:
          allPurchasedProductIDList.append(productID)
    

    return render_template('Products/productCatalogue.html',
                           count=len(productsList),
                           productsList=productsList, allPurchasedProductIDList=allPurchasedProductIDList)
  except dbm.error:
    return render_template('Products/noStoragePage.html')


@app.route('/createProduct', methods=['GET', 'POST'])
def createProduct():

  def retrieve_highestProductID():
    with shelve.open('productID_data') as db:
      return db.get('highestProductID', 0)

  create_ProductForm = CreateProductForm(request.form)

  create_ProductForm.productImage.data = "Null"

  if request.method == 'POST' and create_ProductForm.validate():
    products_dict = {}

    db = shelve.open('product.db', 'c')

    try:
      products_dict = db['Products']
    except:
      print("Error in retrieving Products from product.db")

    # create_ProductFile = request.files.get('productImage')
    # print(create_ProductFile)

    # image = create_ProductFile
    # image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    # image.save(image_filename)

    # unique_filename = str(uuid.uuid4()) + os.path.splitext(secure_filename(create_ProductFile.filename))[1]
    # create_ProductFile.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

    name = create_ProductForm.productName.data
    buyPrice = create_ProductForm.productPrice.data
    category = create_ProductForm.productCategory.data
    description = create_ProductForm.productDesc.data

    if request.files['productImage']:
      file = request.files['productImage']
      if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_filename = filename

    product = Product(image_filename,
                      name,
                      buyPrice,
                      category,
                      description,
                      productRentPrice=0,
                      productRating=0,
                      productFeedback=None)

    products_dict[product.get_productID()] = product
    db['Products'] = products_dict

    db.close()

    username = session['username']
    all_users = user_db.get_users()
    userValue = all_users[username]

    createdProductIDList = userValue.savedProductIDList.get_createIDList()

    if product.get_productID() not in createdProductIDList:
      user_db.updateCreateProductIDList(username, product.get_productID())
    else:
      print("it shouldnt be here")

    highestProductID = retrieve_highestProductID()

    return redirect(url_for('retrieveProducts'))

  return render_template('Products/createProduct.html',
                         form=create_ProductForm)


@app.route('/retrieveProducts')
def retrieveProducts():
  try:
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    productsList = []
    for key in products_dict:
      product = products_dict.get(key)
      productsList.append(product)

    username = session['username']
    all_users = user_db.get_users()
    userValue = all_users[username]

    createdProductIDList = userValue.savedProductIDList.get_createIDList()

    filteredProductList = []

    for product in productsList:
      if product.get_productID() in createdProductIDList:
        filteredProductList.append(product)

    return render_template('Products/retrieveProduct.html',
                           count=len(filteredProductList),
                           filteredProductList=filteredProductList,
                           userValue=userValue,
                           createdProductIDList=createdProductIDList)
  except dbm.error:
    return render_template('Products/noStoragePage.html')


from classes import CreateProductForm, CreateFeedbackForm


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def updateProducts(id):
  updateProductForm = CreateProductForm(request.form)
  print(1)
  if request.method == 'POST' and updateProductForm.validate():
    products_dict = {}
    db = shelve.open('product.db', 'w')
    products_dict = db['Products']

    product = products_dict.get(id)

    product.set_productName(updateProductForm.productName.data)
    product.set_productBuyPrice(updateProductForm.productPrice.data)
    product.set_productDesc(updateProductForm.productDesc.data)

    db['Products'] = products_dict
    db.close()

    return redirect(url_for('retrieveProducts'))

  else:
    print(updateProductForm.validate())
    products_dict = {}
    db = shelve.open('product.db', 'r')
    products_dict = db['Products']
    db.close()

    product = products_dict.get(id)

    updateProductForm.productName.data = product.get_productName()
    updateProductForm.productPrice.data = product.get_productPrice()
    updateProductForm.productDesc.data = product.get_productDesc()

    return render_template('Products/updateProduct.html',
                           form=updateProductForm)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def deleteProduct(id):

  products_dict = {}
  db = shelve.open('product.db', 'w')
  products_dict = db['Products']

  products_dict.pop(id)

  db['Products'] = products_dict
  db.close()

  return redirect(url_for('retrieveProducts'))


@app.route('/viewOneProduct/<int:id>/')
def viewOneProduct(id):
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  all_users = user_db.get_users()
  username = session['username']
  userValue = all_users[username]
  purchasedIDList = userValue.savedProductIDList.get_purchasedIDList()

  product = products_dict.get(id)

  total = sum(product.get_productRating())

  products_dict = {}
  ab = shelve.open('product.db', 'w')
  products_dictToUpdate = ab['Products']

  productIDToUpdate = id

  if productIDToUpdate in products_dictToUpdate:
    productToUpdate = products_dictToUpdate[productIDToUpdate]
    productToUpdate.add_productViewCount()

    ab['Products'] = products_dictToUpdate

    print(f"Product ID with {productIDToUpdate} plus one")
  else:
    print(f"Product ID with {productIDToUpdate} not found.")

  ab.close()

  return render_template('Products/viewOneProduct.html',
                         productID=id,
                         product=product,
                         totalProductRating=total,
                         purchasedIDList=purchasedIDList)


@app.route('/viewProductFeedback/<int:id>/')
def viewProductFeedback(id):
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  product = products_dict.get(id)  #returns the Product object value

  return render_template('Products/viewProductFeedback.html',
                         productID=id,
                         product=product)


@app.route('/createFeedback/<int:id>', methods=['GET', 'POST'])
def createFeedback(id):
  create_FeedbackForm = CreateFeedbackForm(request.form)

  if request.method == 'POST' and create_FeedbackForm.validate():
    products_dict = {}
    db = shelve.open('product.db', 'w')
    products_dict = db['Products']

    product = products_dict.get(id)

    product.add_productRating(create_FeedbackForm.productRating.data)
    product.add_productFeedback(create_FeedbackForm.productFeedback.data)

    db['Products'] = products_dict
    db.close()

    return redirect('/productCatalogue')

  return render_template('Products/createFeedback.html',
                         form=create_FeedbackForm)


@app.route('/addingToBookmark', methods=['POST'])
def addingToBookmark():
  username = session['username']
  all_users = user_db.get_users()
  userValue = all_users[username]

  userBookmarkedList = userValue.savedProductIDList.get_bookmarkedIDList()

  bookmarkedProductID = request.form.get('bookmarkedProductID')

  if int(bookmarkedProductID) in userBookmarkedList:
    pass
  else:
    user_db.updateBookmarkedProductIDList(username, int(bookmarkedProductID),
                                          "add")

  return redirect(url_for('productCatalogue'))


@app.route('/viewBookmarkedProducts')
def viewBookmarkedProducts():
  try:
    username = session['username']
    all_users = user_db.get_users()
    userValue = all_users[username]

    userBookmarkedList = userValue.savedProductIDList.get_bookmarkedIDList()

    products_dict = {}
    sh = shelve.open('product.db', 'r')
    products_dict = sh['Products']
    sh.close()

    productsList = []
    for key in products_dict:
      product = products_dict.get(key)
      productsList.append(product)

    return render_template('Products/viewBookmarkedProducts.html',
                           userBookmarkedList=userBookmarkedList,
                           productsList=productsList)
  except dbm.error:
    return render_template('Products/noStoragePage.html')


@app.route('/removeBookmarkedProduct', methods=['POST'])
def removeBookmarkedProduct():
  try:
    username = session['username']
    all_users = user_db.get_users()
    userValue = all_users[username]

    removeBookmarkedProductID = request.form.get("removeBookmarkedProductID")

    user_db.updateBookmarkedProductIDList(username,
                                          int(removeBookmarkedProductID),
                                          "remove")

    return redirect(url_for('viewBookmarkedProducts'))
  except dbm.error:
    return redirect(url_for('noStorageFoundError'))


@app.route('/buyProduct', methods=['POST'])
def buyProduct():
  purchasedProductID = request.form.get('purchasedProductID')
  purchasedProductID = int(purchasedProductID)

  username = session['username']
  all_users = user_db.get_users()
  userValue = all_users[username]

  purchasedIDList = userValue.savedProductIDList.get_purchasedIDList()

  if purchasedProductID in purchasedIDList:
    pass
  else:
    user_db.updatePurchasedProductIDList(username, purchasedProductID)

  products_dict = {}
  sh = shelve.open('product.db', 'c')
  products_dict = sh['Products']

  for productID in products_dict.keys():
    if productID in purchasedIDList:
      products_dict.get(productID).set_productStatus("Sold")

  sh['Products'] = products_dict

  sh.close()

  return redirect(url_for('productCatalogue'))


@app.route('/viewPurchasedProducts')
def viewPurchasedProducts():

  try:
    username = session['username']
    all_users = user_db.get_users()
    userValue = all_users[username]

    purchasedIDList = userValue.savedProductIDList.get_purchasedIDList()

    products_dict = {}
    sh = shelve.open('product.db', 'r')
    products_dict = sh['Products']
    sh.close()

    productsList = []
    for key in products_dict:
      product = products_dict.get(key)
      productsList.append(product)

    return render_template('Products/viewPurchasedProducts.html',
                           purchasedIDList=purchasedIDList,
                           productsList=productsList)

  except dbm.error:
    return render_template('Products/noStoragePage.html')


@app.route('/sortedProductCatalogueOnName(A-Z)')
def sortedProductCatalogueOnNameAtoZ():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productName())

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/sortedProductCatalogueOnName(Z-A)')
def sortedProductCatalogueOnNameZtoA():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productName())

  sortedProducts.reverse()

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/sortedProductCatalogueOnPriceIncreasing')
def sortedProductCatalogueOnPriceIncreasing():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productPrice())

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/sortedProductCatalogueOnPriceDecreasing')
def sortedProductCatalogueOnPriceDecreasing():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productPrice())

  sortedProducts.reverse()

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/sortedProductCatalogueOnPopularityMostPopular1')
def sortedProductCatalogueOnPopularityMostPopular():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productViewCount())

  sortedProducts.reverse()

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/sortedProductCatalogueOnPopularityLeastPopular')
def sortedProductCatalogueOnPopularityLeastPopular():
  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  sortedProducts = sorted(productsList,
                          key=lambda product: product.get_productViewCount())

  return render_template('Products/productCatalogue.html',
                         sortedProducts=sortedProducts)


@app.route('/searchedProductCatalogue', methods=['GET', 'POST'])
def searchedProductCatalogue():

  products_dict = {}
  db = shelve.open('product.db', 'r')
  products_dict = db['Products']
  db.close()

  productsList = []
  for key in products_dict:
    product = products_dict.get(key)
    productsList.append(product)

  query = request.form.get('search_query', '')
  search_results = [
      product for product in productsList
      if query.lower() in product.get_productName().lower()
  ]

  return render_template('Products/productCatalogue.html',
                         productsList=productsList,
                         search_results=search_results,
                         query=query)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=81)
