from flask import Flask,request,render_template,jsonify,Markup
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import pandas as pd
import re
from requests.adapters import HTTPAdapter
import urllib
from urllib3.util.retry import Retry
app=Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0'}

stores = ['7073', '7129', '7012', '7013', '7134', '7107',
'7080', '7027', '7078', '7114', '7301', '7006',
'7130', '7132', '7011', '7112', '7003', '7253',
'7106', '7161', '7004', '7269', '7241', '7157',
'7115', '7021', '7007', '7256', '7008',
'7136', '7238', '7109', '7005', '7249', '7123']


retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)

@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/submit",methods=["GET","POST"])
def submit():
    data=request.form.get("list")
    skus=data.split("SKU: ")
    namsku=skus.copy()
    productnames = getnameofproduct(namsku)
    del skus[0]
    skuslist=[]
    for sku in skus:
        skuslist.append(sku.split(" ")[0])
    data=stock_get(skuslist,productnames)
    print(data)
    return render_template("display.html",data=data)


def getnameofproduct(list):
    productnames=[]
    list[0]="   "+list[0].replace("HOME DEPOT ======================== ","")
    list.pop()
    for item in list:
        item=item.replace(item.split(" ")[0],"")
        names=item.split("Qty:")
        names.pop()
        productnames.append(names[0][4:])
    return productnames




def stock_get(skus,productname):
    session = requests.Session()

    allproductinstore=[]
    allproduct =True
    for store in stores:
        data = []
        for sku ,pname in zip(skus,productname):
            tempdict={}
            product_url = "https://www.homedepot.ca/homedepotcacommercewebservices/v2/homedepotca/products/{}/localized/{}?fields=BASIC_SPA".format(
            sku.strip(), store)
            product_url_response = session.get(product_url, headers=headers)
            print(product_url_response)
            if product_url_response.status_code==200:
                jsn_resp = product_url_response.json()

                store_id = jsn_resp['aisleBay']['storeDisplayName']

                stock_level = jsn_resp['storeStock']['stockLevel']
                tempdict["store"]=store
                tempdict["store_id"]=store_id
                tempdict["sku"]=sku
                tempdict["stock_level"]=stock_level
                tempdict["productname"]=pname
                data.append(tempdict)
                print(store, store_id, sku, stock_level)
                print("")
            else:
                allproduct=False
        if allproduct==True:
            allproductinstore.append(data)
        else:
            print("all item not found")
    return allproductinstore





if __name__=="__main__":
    app.run()

