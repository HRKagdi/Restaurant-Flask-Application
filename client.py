import requests
from requests import PreparedRequest
from flask.json import jsonify
from flask import json
from werkzeug.wrappers import response

# Displaying the Choices to user.
def show_Menu():
    print("")
    print("1. Signup")
    print("2. Login")
    print("3. Logout")
    print("4. GetMenu")
    print("5. GiveOrder")
    print("6. AddItem")
    print("7. Get Bills")
    print("8. Exit")

# Signup Module.
def Signup():
    id = input("Enter id: ")
    userName = input("Enter userName:")
    password = input("Enter password: ")
    response = requests.post("http://127.0.0.1:8000/signup",
                             json={'id': id, 'name': userName, 'password': password})
    print(response.content)

#Login Module.
def login():
    userName = input("Enter userName: ")
    password = input("Enter password: ")
    response = requests.post("http://127.0.0.1:8000/login",
                             json={'name': userName, 'password': password})
    temp = response.json()
    print(temp['str'])
    string = "Logged In succesfully"
    global loggedIn
    loggedIn = False
    global uname
    uname = ""
    if(temp['str'] == string):
        loggedIn = True
        uname = userName
    else:
        loggedIn = False

#Logout Module.
def logout():
    response = requests.post("http://127.0.0.1:8000/logout")
    print(response.content)
    global loggedIn
    loggedIn = False

# Moule to get Restaurent's menu.
def getMenu():
    # print(loggedIn)
    if(not(loggedIn)):
        print("Please log in first")
        return
    response = requests.get("http://127.0.0.1:8000/getMenu")
    print("ItemId       HalfPlate       FullPlate")
    temp = response.json()
    count = 0
    for key in temp:
        count += 1

    global myMenu
    myMenu = [None]*(count+1)
    for key in temp:
        item_no = key
        dict1 = temp[item_no]
        halfPrice = dict1['halfPrice']
        fullPrice = dict1['fullPrice']
        print(str(item_no)+"            "+str(halfPrice) +
              "              "+str(fullPrice))
        plate = []
        plate.append(halfPrice)
        plate.append(fullPrice)
        myMenu[int(item_no)] = plate

    return myMenu

# Module to get All transactions.
def getBills():
    if(not(loggedIn)):
        print("Please log in first")
        return

    response = requests.post("http://127.0.0.1:8000/getBills",
                             json={'userName': uname})
    temp = response.json()
    for key in temp:
        dict1 = temp[key]
        print("***************************************")
        print("Total Bill: " + str(dict1['totalBill']))
        print("Tip :"+str(dict1['tip']))
        share = (dict1['totalBill']/dict1['nop'])
        print("Share: "+str(share))
        print("***************************************")

#Module to give order.
def giveOrder():
    if(not(loggedIn)):
        print("Please log in first")
        return
    print("Enter your order details")
    print("Enter in the following format")
    print("Item No, half for half plate and full for full plate and quantity")
    print("Enter plate details in comma separeted values and | for next plate")
    order = input("Enter order\n")
    response = requests.post("http://127.0.0.1:8000/takeOrder",
                             json={'order': order})

    print("If you would like to pay tip")
    print("0, 10% and 20%")
    tip = input("Enter tip percentage: ")
    no_of_people = input("Enter number of people: ")
    res1 = requests.post("http://127.0.0.1:8000/countPeople",
                         json={'no_of_people': no_of_people, 'tip': tip})
    res2 = requests.post("http://127.0.0.1:8000/giveTip",
                         json={'tip': tip})

    amounts = res2.json()
    total_bill = amounts[0]
    bill_share = amounts[1]
    print("")
    print("Please pay " + (str("{0:.2f}".format(total_bill))) + "Rs")
    print("Bill per person is " + (str("{0:.2f}".format(bill_share))))
    print("")

    print("Note that there is 50% chance that the bill amount increases by 20%")
    would_participate = input(
        "Would you like to participate in out 'Test your luck' event? Enter YES or NO: ")

    res3 = requests.post("http://127.0.0.1:8000/testLuck",
                         json={'would_participate': would_participate})

    l1 = res3.json()
    print(l1)
    increment = int(l1[1])
    discount = int(l1[0])

    # Damn, Bill will get incremented.
    if increment != 0:
        total_bill += (total_bill) * (increment/100)
        print("Sorry, The bill increased by " +
              str((total_bill*increment)/100))

        print(" ", end="")
        for i in range(0, 4):
            print("*", end="")
        print("")
        for i in range(0, 4):
            print("*    *")
        print(" ", end="")
        for i in range(0, 4):
            print("*", end="")

    # Wow, Bill will get decremented
    elif discount != 0:
        total_bill -= (total_bill) * (discount/100)
        print("Congratulations, You got a discount of " +
              str((total_bill*discount)/100))

        print(" ", end="")
        for i in range(0, 4):
            print("*", end="")
        for i in range(0, 6):
            print(" ", end="")
        print("  ", end="")
        for i in range(0, 4):
            print("*", end="")

        print("")
        for i in range(0, 3):
            print("|    |", end="")
            for j in range(0, 6):
                print(" ", end="")
            print("|    |", end="")
            print("")

        print(" ", end="")
        for j in range(0, 4):
            print("*", end="")
        for j in range(0, 6):
            print(" ", end="")
        print("  ", end="")
        for j in range(0, 4):
            print("*", end="")

        print("")
        print("")
        print("        {}")
        print("")
        print("      ______")
    else:
        print("Neutral, The bill neither increased not decreased")

    print("")
    global intermediate_bill
    intermediate_bill = total_bill

    res4 = requests.post("http://127.0.0.1:8000/getBill")
    mydict = res4.json()
    total_bill = 0
    myMenu = getMenu()
    print(myMenu)
    print("Bill Breakdown")
    print("------------------------------------")
    for items in mydict:
        pair = items['key']
        quantity = items['value']
        item_no = pair[0]
        isHalf = pair[1]

        print("Item "+str(item_no), end="")
        if(isHalf == "Half"):
            print(" [Half]"+"["+str(quantity)+"]: " +
                  str("{0:.2f}".format(int(myMenu[item_no][0]) * quantity)))
            total_bill += int(myMenu[item_no][0]) * quantity
        else:
            print(" [Full]"+"["+str(quantity)+"]: " +
                  str("{0:.2f}".format(int(myMenu[item_no][1]) * quantity)))
            total_bill += int(myMenu[item_no][1]) * quantity

    print("Total: "+str("{0:.2f}".format(total_bill)))
    print("Tip Percentage: "+str(tip)+"%")
    if(discount != 0):
        print("Discount/Increase: -" +
              str("{0:.2f}".format(intermediate_bill-total_bill)))
        temp = intermediate_bill-(intermediate_bill*discount)/100
        print("Final Total: " +
              str("{0:.2f}".format(intermediate_bill-(intermediate_bill*discount)/100)))
        print("Each person has to contibute: " +
              str("{0:.2f}".format(int(temp)/int(no_of_people))))

    elif(increment != 0):
        print("Discount/Increase: +" +
              str("{0:.2f}".format(intermediate_bill-total_bill)))
        temp = intermediate_bill+(intermediate_bill*increment)/100
        print("Final Total: " +
              str("{0:.2f}".format(intermediate_bill+(intermediate_bill*increment)/100)))
        print("Each person has to contibute: " +
              str("{0:.2f}".format(int(temp)/int(no_of_people))))
    else:
        temp = intermediate_bill+(intermediate_bill*increment)/100
        print("Discount/Increase: " + "0.00")
        print("Final Total: " +
              str("{0:.2f}".format(intermediate_bill+(intermediate_bill*increment)/100)))
        print("Each person has to contibute: " +
              str("{0:.2f}".format(int(temp)/int(no_of_people))))
    print("------------------------------------")

    res7 = requests.post("http://127.0.0.1:8000/addBill",
                         json={'userName': uname, 'totalBill': total_bill,
                               'interBill': intermediate_bill, 'nop': no_of_people,
                               'tip': tip})
    # print(res7.json())

#Module to add plate to the menu . Accesible only to chef (HRKChef)
def addItem():
    if(loggedIn and uname == "HRKChef"):
        item_no = input("Enter item_no: ")
        halfPrice = input("Enter half plate price: ")
        fullPrice = input("Enter full plate price: ")
        response = requests.post("http://127.0.0.1:8000/createMenu",
                                 json={'item_no': item_no, 'halfPrice': halfPrice, 'fullPrice': fullPrice})
        print("Item added successully")
    else:
        if(loggedIn):
            print("You are not the chef")
        elif(uname == "HRKChef"):
            print("Please log in first chef")
        else:
            print("Invalid Operation")


while(1):
    show_Menu()
    print("")
    choice = input("Enter your choice<< ")
    if(int(choice) == 1):
        Signup()
    elif(int(choice) == 2):
        login()
    elif(int(choice) == 3):
        logout()
    elif(int(choice) == 4):
        getMenu()
    elif(int(choice) == 5):
        giveOrder()
    elif(int(choice) == 6):
        addItem()
    elif(int(choice) == 7):
        getBills()
    elif(int(choice) == 8):
        print("Thanks. Visit Again")
        break
