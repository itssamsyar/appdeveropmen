import shelve
import random
import string
from classes import couponClass
couponClass = couponClass()
def generate():
    letters = string.ascii_uppercase  # Letters of the alphabet
    couponID = ''

    while len(couponID) != 8:
        ltr = random.choice(letters)
        couponID += ltr
    couponClass.set_coupon(couponID)
    return couponID

def add(username, num, game, date, time):
    #add into records
    d = shelve.open("couponDatabase", "c")
    e = shelve.open("couponTempDatabase", "c")
    coupon = d.get("dict", {})
    coupon2 = e.get("dict2", {})
    dictkeys = list(coupon.keys())
    coupon[len(dictkeys)+1] = [couponClass.get_coupon(),username, num, game, date, time]
    coupon2[1] = [couponClass.get_coupon(), username, num, game, date, time]
    d["dict"] = coupon
    e["dict2"] = coupon2
    d.close()
    e.close()

def export():
    #export into txt readable file
    e = shelve.open("couponTempDatabase", "c")
    items = list(e.values())
    a = open("couponDatabase.txt", "a")
    a.write(f"\n")
    for item in items:
        a.write(str(item))
    a.close()

def exportCoupon():
    import shelve
    import csv
    import pandas as pd
    d = shelve.open("couponDatabase", "c")
    dict = d.get("dict")
    dictkey = list(dict.keys())
    d.close()

    header = ['Coupon code', 'Username', 'Key', 'Game', 'Date', 'Time']

    with open('couponDatabaseExcel.csv', "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(header)
        for i in range(1, len(dictkey)+1):

            writer.writerow(dict[i])

    df = pd.read_csv('couponDatabaseExcel.csv')
    # can replace with:
    # df = pd.read_csv('input.tsv', sep='\t') for tab delimited
    df.to_excel('couponDatabaseExcel.xlsx', 'Sheet1')