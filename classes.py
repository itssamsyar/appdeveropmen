# User
import shelve


# CreateReportForm
from wtforms import Form, StringField, RadioField, SearchField, TextAreaField, DecimalField, validators
from wtforms.fields import EmailField, DateField





class User:
  def __init__(self, username, password, email=None, address=None, phone_number=None, profile_picture=None, type="Customer"):
   self.username = username
   self.password = password
   self.email = email
   self.address = address
   self.phone_number = phone_number
   self.profile_picture = profile_picture
   self.type = type
   self.savedProductIDList = SavedProductIDList()


class UserDB:
 def __init__(self, db_file):
   self.db_file = db_file

 def get_users(self):
   db = shelve.open(self.db_file, 'c')
   users = db.get('users', {})
   db.close()
   return users

 def save_users(self, users):
   db = shelve.open(self.db_file, 'w')
   db['users'] = users
   db.close()

 def get_user(self, username):
   users = self.get_users()
   return users.get(username)

 def add_user(self, username, password, profile_picture=None):
   users = self.get_users()
   if username in users:
     return False
   else:
     user = User(username, password, profile_picture)
     users[username] = user
     self.save_users(users)
     return True

 def update_user(self, username, new_password, new_email, new_address, new_phone_number,
         profile_picture=None):
   users = self.get_users()
   print("users gotted")
   if username in users:
     user = users[username]
     # user.username = new_username
     user.password = new_password
     user.email = new_email
     user.address = new_address
     user.phone_number = new_phone_number
     user.profile_picture = profile_picture  # Save the profile picture
     
     users[username] = user
     
     self.save_users(users)
     return True
   else:
     raise ValueError("your mum not here")

 def delete_user(self, username):
   users = self.get_users()
   if username in users:
     del users[username]
     self.save_users(users)
     return True
   else:
     return False

 def staff_delete_user(self, username):
  users = self.get_users()
  if username in users:
    del users[username]
    self.save_users(users)
    return True
  else:
    return False

 def get_all_users(self):
   users = []
   db = shelve.open(self.db_file, 'r')
   for key in db:
     user = db[key]
     users.append(user)
   db.close()
   return users

 def updateCreateProductIDList(self, username, productID):
  all_users = self.get_users()
  userValue = all_users.get(username)
  userValue.savedProductIDList.add_createIDList(productID)
  all_users[username] = userValue
  self.save_users(all_users)

 def updateBookmarkedProductIDList(self, username, productID, condition):
   all_users = self.get_users()
   userValue = all_users.get(username)

   if condition == "add":
     userValue.savedProductIDList.add_bookmarkedIDList(productID)
   elif condition == "remove":
     userValue.savedProductIDList.remove_bookmarkedIDList(productID)
     
   all_users[username] = userValue
   self.save_users(all_users)



 def updatePurchasedProductIDList(self, username, productID):
   all_users = self.get_users()
   userValue = all_users.get(username)
   userValue.savedProductIDList.add_purchasedIDList(productID)
   all_users[username] = userValue
   self.save_users(all_users)
  
  
  
  
  
  
 
  



class CreateReportForm(Form):
 reportName = StringField('Offender Username', [validators.DataRequired()])
 reportDesc = TextAreaField('Offence Committed', [validators.DataRequired()])


class Report:
 countID = 0

 def __init__(self, reportName, reportDesc):
   Report.countID += 1
   self.__reportID = Report.countID
   self.__reportName = reportName
   self.__reportDesc = reportDesc

 def set_reportID(self, reportID):
   self.__reportID = reportID

 def set_reportName(self, reportName):
   self.__reportName = reportName

 def set_reportDesc(self, reportDesc):
   self.__reportDesc = reportDesc

 def get_reportID(self):
   return self.__reportID

 def get_reportName(self):
   return self.__reportName

 def get_reportDesc(self):
   return self.__reportDesc




class Mail:
 def __init__(self, sender, title, msg, offer=None):
   self.sender = sender
   self.title = title
   self.msg = msg
   self.offer = offer




#Coupon
class couponClass:
 def __init__(self):
   self.__coupon = None

 def set_coupon(self, coupon):
   self.__coupon = coupon

 def get_coupon(self):
   return self.__coupon
#End Coupon



################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
# Amsyar Products Part

from wtforms import Form, StringField, FileField, TextAreaField, DecimalField, validators, SelectField


class SavedProductIDList:
 def __init__(self):
   self.__bookmarkedIDList = []
   self.__purchasedIDList = []
   self.__createIDList = []
   self.__rentIDList = []

 def add_bookmarkedIDList(self, productID):
   self.__bookmarkedIDList.append(productID)

 def remove_bookmarkedIDList(self, productID):
   self.__bookmarkedIDList.remove(productID)
    
 def add_purchasedIDList(self, productID):
   self.__purchasedIDList.append(productID)

 def add_createIDList(self, productID):
   self.__createIDList.append(productID)

 def add_rentIDList(self, productID):
   self.__rentIDList.append(productID)

  




 def get_bookmarkedIDList(self):
   return self.__bookmarkedIDList

 def get_purchasedIDList(self):
   return self.__purchasedIDList

 def get_createIDList(self):
   return self.__createIDList

 def get_rentIDList(self):
   return self.__rentIDList


class Product:
 def generate_productID():
   with shelve.open('productID_Data') as db:
     if 'highestProductID' not in db:
       db['highestProductID'] = 0
     highestProductID = db['highestProductID']
     db['highestProductID'] += 1
   return highestProductID + 1
    
 def __init__(self, productImage, productName, productBuyPrice, productCategory, productDesc, productRentPrice, productRating, productFeedback):

   self.__productImage = productImage
    
   self.__productID = Product.generate_productID()
   self.__productName = productName

   self.__productBuyPrice = productBuyPrice
   self.__productRentPrice = productRentPrice

   self.__productCategory = productCategory

   self.__productDurationOfRental = 0

   self.__productStatus = "Listing"

   self.__productDesc = productDesc

   emptyListRating = []
   emptyListRating.append(productRating)

   emptyListFeedback = []
   emptyListFeedback.append(productFeedback)

   self.__productRating = emptyListRating
   self.__productFeeback = emptyListFeedback

   self.__numberOfFeedbacks = len(self.__productRating)

   self.__totalProductRating = sum(self.__productRating)

   self.__productViewCount = 0

 def set_productID(self, productID):
  self.__productID = productID
  # figure out codes to generate unique product ID number



 def set_productImage(self, productImage):
  self.__productImage = productImage

 def set_productName(self, productName):
  self.__productName = productName





 def set_productBuyPrice(self, productPrice):
  self.__productBuyPrice = productPrice

 def set_productRentPrice(self, productRentPrice):
  self.__productRentPrice = productRentPrice

 def set_productCategory(self, productCategory):
  self.__productCategory = productCategory


 def set_productDurationOfRental(self, duration):
  self.__productDurationOfRental = duration



 def set_productStatus(self, productStatus):
  self.__productStatus = productStatus



 def set_productDesc(self, productDesc):
  self.__productDesc = productDesc




 def add_productRating(self, productRating):
  self.__productRating.append(productRating)
  totalProductRating = sum(self.__productRating)
  self.__totalProductRating = totalProductRating

 def add_productFeedback(self, productFeedback):
  self.__productFeeback.append(productFeedback)
  self.__numberOfFeedbacks += 1


 def add_productViewCount(self):
  self.__productViewCount += 1








 def get_productID(self):
  return self.__productID

 def get_productImage(self):
  return self.__productImage

 def get_productName(self):
  return self.__productName




 def get_productPrice(self):
  return self.__productBuyPrice

 def get_productRentPrice(self):
  return self.__productRentPrice

 def get_productCategory(self):
   return self.__productCategory


 def get_productDurationOfRental(self):
  return self.__productDurationOfRental



 def get_productStatus(self):
  return self.__productStatus




 def get_productDesc(self):
  return self.__productDesc






 def get_numberOfFeedbacks(self):
  return self.__numberOfFeedbacks

 def get_productRating(self):
  return self.__productRating

 def get_productFeedback(self):
  return self.__productFeeback

 def get_totalProductRating(self):
  return self.__totalProductRating



 def get_productViewCount(self):
  return self.__productViewCount

class CreateProductForm(Form):
 productImage = FileField('Product Image', [validators.DataRequired()])
 productName = StringField('Product Name', [validators.DataRequired()])
 productPrice = DecimalField('Product Buying Price', [validators.DataRequired()])
 productCategory = SelectField('Product Category', [validators.DataRequired()],
     choices=[('', 'Select'), ('TG', 'Toys & Games'), ('B', 'Books'), ('E', 'Electronics'), ('S', 'Sports'), ('AE', 'Arts & Equipment')], default='')
 productDesc = TextAreaField('Product Description', [validators.DataRequired()])

class CreateFeedbackForm(Form):
 productRating = DecimalField('Product Rating', [validators.DataRequired()])
 productFeedback = TextAreaField('Product Feedback', [validators.DataRequired()])


class UpdateUserForm(Form):
  username = StringField('Username')
  password = StringField('Password')
  email = StringField('Email', [validators.Email()])
  address = StringField('Address')
  phone_number = StringField('Phone Number', [validators.Regexp(r'^\d+$')])










