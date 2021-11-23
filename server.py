# Importing the required modules.
import re
import random
import json
from flask import Flask, render_template, request, session
from flask.helpers import total_seconds
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user
from flask_login import logout_user, login_required, UserMixin
import requests
import datetime
from werkzeug.wrappers import response
from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField
from wtforms.validators import DataRequired

# Flask App configurations.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Model for user profile.
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init_(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# Model for Restaurent's menu.
class Menu(UserMixin, db.Model):
    item_no = db.Column(db.Integer, primary_key=True, autoincrement=False)
    halfPrice = db.Column(db.Integer)
    fullPrice = db.Column(db.Integer)

    def __init__(self, item_no, halfPrice, fullPrice):
        self.item_no = item_no
        self.halfPrice = halfPrice
        self.fullPrice = fullPrice

# Model for transactions.
class Transactions(UserMixin, db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80), primary_key=True)
    totalBill = db.Column(db.Float)
    intermediateBill = db.Column(db.Float)
    tip = db.Column(db.Float)
    numberofPeople = db.Column(db.Integer)

    def __init__(self, uname, tbill, ibill, tip, nop):
        self.tid = int(datetime.datetime.utcnow().timestamp())
        self.userName = uname
        self.totalBill = tbill
        self.intermediateBill = ibill
        self.tip = tip
        self.numberofPeople = nop


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Customer.get(int(user_id))

# Route for signup.
@app.route('/signup', methods=['GET', 'POST'])
def register():

    #form = RegisterForm(request.form)
    # print(request.form)
    if request.method == 'POST':
        newCust = Customer(id=request.json['id'],
                           name=request.json['name'],
                           password=request.json['password'])
        # print(form.name.data)
        db.session.add(newCust)
        db.session.commit()

        return "Registered Succesfully"

    else:
        return "Not registered, Please try again"

# Route for Login.
@app.route('/login', methods=['GET', 'POST'])
def login():

    if(request.method == 'POST'):
        cust = Customer.query.filter_by(name=request.json['name']).first()

        if(cust.password != request.json['password']):
            return "Incorrect password or username"
        if cust:
            session['logged_in'] = True
            session['name'] = cust.name
            res = {'str': "Logged In succesfully"}
            return jsonify(res)

        else:
            res = {'str': "username or password is incorrect, Please try again"}
            return jsonify(res)

# Route for Logout.
@app.route('/logout', methods=['POST'])
def logout():
    session['logged_in'] = False
    return "Logged Out successfully"

# Route for creating a menu.
@app.route('/createMenu', methods=['GET', 'POST'])
def createMenu():
    if(request.method == 'POST'):
        newItem = Menu(
            item_no=request.json['item_no'],
            halfPrice=request.json['halfPrice'],
            fullPrice=request.json['fullPrice']
        )
        db.session.add(newItem)
        db.session.commit()

        return "Item Added successfully"

    return "Error, Please try again"

# Route for viewing menu.
@app.route('/getMenu', methods=['GET'])
def getMenu():
    menu = Menu.query.all()
    if(len(menu) == 0):
        return "Nothing in the menu yet"

    response = {}
    for item in menu:
        response[str(item.item_no)] = {
            "item_no": item.item_no,
            "halfPrice": item.halfPrice,
            "fullPrice": item.fullPrice
        }
    return jsonify(response)

# ROute for getting bills.
@app.route('/getBills', methods=['GET', 'POST'])
def getBills():
    if request.method == 'POST':
        uname = request.json['userName']
        bills = Transactions.query.filter(Transactions.userName == uname).all()
        response = {}
        for bill in bills:
            tbill = bill.intermediateBill+(bill.tip*bill.intermediateBill)/100
            response[bill.userName+str(bill.tid)] = {
                "totalBill": tbill,
                "intermediateBill": bill.intermediateBill,
                "nop": bill.numberofPeople,
                "tip": bill.tip
            }
        return jsonify(response)
    return "No Bills"

# Route to add a transaction to user Account.
@app.route('/addBill', methods=['POST'])
def addBill():
    uname = request.json['userName']
    totalBill = request.json['totalBill']
    interBill = request.json['interBill']
    nop = request.json['nop']
    tip = request.json['tip']
    Transaction = Transactions(uname, totalBill, interBill, tip, nop)
    db.session.add(Transaction)
    db.session.commit()

    return "added bill successfully"

# Route for calculating the Bill.
def calculateBill():
    # Calculating total bill based on input from user.
    total_bill = 0
    global mydict
    mydict = {}
    for i in range(0, len(order_arr)):
        plate = order_arr[i].split(' ')
        item_no = int(plate[0])
        if plate[1] == "half":
            isHalf = True
        else:
            isHalf = False
        quantity = int(plate[2])

        pair = ()
        if isHalf:
            pair = (item_no, "Half")
        else:
            pair = (item_no, "Full")

        prev_quant = 0
        if pair in mydict.keys():
            prev_quant = mydict.get(pair)
            prev_quant += quantity
            mydict.update({pair: prev_quant})
        else:
            mydict[pair] = quantity

        if(isHalf):
            total_bill += int(myMenu[item_no-1][1]) * quantity
        else:
            total_bill += int(myMenu[item_no-1][2]) * quantity

    total_bill += (total_bill) * (int(tip)/100)
    print("Please pay " + (str("{0:.2f}".format(total_bill))) + "Rs")
    intermediate_bill = total_bill

    bill_share = total_bill / (int(no_of_people))
    print("Bill per person is " + (str("{0:.2f}".format(bill_share))))

    return total_bill, bill_share

# Function for converting dictionary to list.
def remap_keys(mapping):
    return [{'key': k, 'value': v} for k, v in iter(mapping.items())]

# Route for getting Bill.
@app.route('/getBill', methods=['POST'])
def getBill():
    temp = remap_keys(mydict)
    return jsonify(temp)

# Route for accepting order.
@app.route('/takeOrder', methods=['POST'])
def takeOrder():
    global order_arr
    order = request.json['order']
    order_arr = order.split('|')
    return "Order noted, tasted food coming sooon"

# Route for handling tip.
@app.route('/giveTip', methods=['POST'])
def giveTip():
    global tip
    tip = request.json['tip']
    total_bill, bill_share = calculateBill()
    response = []
    response.append(total_bill)
    response.append(bill_share)
    return jsonify(response)

#Route for countin number of people.
@app.route('/countPeople', methods=['POST'])
def countPeople():
    global no_of_people
    no_of_people = request.json['no_of_people']
    return "Bill will be shared"

# Route for Test your Luck Event.
@app.route('/testLuck', methods=['POST'])
def testLuck():
    would_participate = request.json['would_participate']
    if(would_participate == "YES"):
        discount = 0
        increment = 0
        chance = random.randint(1, 100)
        if 1 <= chance and chance <= 5:
            discount += 50
            increment += 0
        elif 6 <= chance and chance <= 15:
            discount += 25
            increment += 0
        elif 16 <= chance and chance <= 30:
            discount += 10
            increment += 0
        elif 31 <= chance and chance <= 80:
            increment += 20
            discount += 0
        elif 81 <= chance and chance <= 100:
            discount += 0
            increment += 0

        #print(str(discount)+" "+str(increment))
        response = []
        response.append(discount)
        response.append(increment)
        return jsonify(response)
    else:
        discount = 0
        increment = 0
        response = []
        response.append(discount)
        response.append(increment)
        return jsonify(response)


menu = Menu.query.all()
myMenu = []
for item in menu:
    temp = []
    temp.append(str(item.item_no))
    temp.append(str(item.halfPrice))
    temp.append(str(item.fullPrice))
    myMenu.append(temp)

# App running on port number 8000.
if __name__ == '__main__':
    app.run(port=8000, debug=True)
