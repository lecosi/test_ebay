#!/usr/bin/python3
import sqlite3
import urllib
import xmltodict
import webbrowser
from tqdm import tqdm
import os, sys


sys.setrecursionlimit(10000)
cont = 0
def load_data():
    if os.path.exists('./ebaydb.db'):
        print ("base de datos existe")
        os.remove('./ebaydb.db')
        print ("base de datos borrada")
        create_table()
        request_ebay()
    else:
        print ("no existe base de datos")
        create_table()
        request_ebay()

def create_table():
    conn = sqlite3.connect('ebaydb.db')
    c =conn.cursor()    
    c.execute("CREATE TABLE categories (categoryId INTEGER, categoryName TEXT, categoryLevel INTEGER, BestOfferEnabled BOOLEAN, CategoryParentID INTEGER)")
    print ("se crea base de datos")

def insert_table(info_categories):
    conn = sqlite3.connect('ebaydb.db')
    c =conn.cursor()
    for category in tqdm(info_categories):
      categoryId = category.get('CategoryID')
      categoryName = category.get('CategoryName')
      categoryLevel = category.get('CategoryLevel')
      BestOfferEnabled = category.get('BestOfferEnabled')
      CategoryParentID = category.get('CategoryParentID')
      c.execute("INSERT INTO categories VALUES (?, ?, ?, ?, ?)", (categoryId, categoryName, categoryLevel, BestOfferEnabled, CategoryParentID))
    print ("se insertaron datos con exito")
    conn.commit()
    c.close()
    conn.close()


def request_ebay():
    xml = """<?xml version="1.0" encoding="utf-8"?>
        <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
          <RequesterCredentials>
            <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PMIhVg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpaCpQWdj6x9nY+seQ**L0MCAA**AAMAAA**IahulXaONmBwi/Pzhx0hMqjHhVAz9/qrFLIkfGH5wFH8Fjwj8+H5FN4NvzHaDPFf0qQtPMFUaOXHpJ8M7c2OFDJ7LBK2+JVlTi5gh0r+g4I0wpNYLtXnq0zgeS8N6KPl8SQiGLr05e9TgLRdxpxkFVS/VTVxejPkXVMs/LCN/Jr1BXrOUmVkT/4Euuo6slGyjaUtoqYMQnmBcRsK4xLiBBDtiow6YHReCJ0u8oxBeVZo3S2jABoDDO9DHLt7cS73vPQyIbdm2nP4w4BvtFsFVuaq6uMJAbFBP4F/v/U5JBZUPMElLrkXLMlkQFAB3aPvqZvpGw7S8SgL7d2s0GxnhVSbh4QAqQrQA0guK7OSqNoV+vl+N0mO24Aw8whOFxQXapTSRcy8wI8IZJynn6vaMpBl5cOuwPgdLMnnE+JvmFtQFrxa+k/9PRoVFm+13iGoue4bMY67Zcbcx65PXDXktoM3V+sSzSGhg5M+R6MXhxlN3xYfwq8vhBQfRlbIq+SU2FhicEmTRHrpaMCk4Gtn8CKNGpEr1GiNlVtbfjQn0LXPp7aYGgh0A/b8ayE1LUMKne02JBQgancNgMGjByCIemi8Dd1oU1NkgICFDbHapDhATTzgKpulY02BToW7kkrt3y6BoESruIGxTjzSVnSAbGk1vfYsQRwjtF6BNbr5Goi52M510DizujC+s+lSpK4P0+RF9AwtrUpVVu2PP8taB6FEpe39h8RWTM+aRDnDny/v7wA/GkkvfGhiioCN0z48</eBayAuthToken>
          </RequesterCredentials>
          <CategorySiteID>0</CategorySiteID>
          <DetailLevel>ReturnAll</DetailLevel>
        </GetCategoriesRequest>"""

    headers = {
        'X-EBAY-API-CALL-NAME': 'GetCategories',
        'X-EBAY-API-APP-NAME': 'EchoBay62-5538-466c-b43b-662768d6841',
        'X-EBAY-API-CERT-NAME': '00dd08ab-2082-4e3c-9518-5f4298f296db',
        'X-EBAY-API-DEV-NAME': '16a26b1b-26cf-442d-906d-597b60c41c19',
        'X-EBAY-API-SITEID': '0',
        'X-EBAY-API-COMPATIBILITY-LEVEL': '861',
     } 

    url="https://api.sandbox.ebay.com/ws/api.dll"
    print ("consultando api.....")
    data = xml.encode('UTF-8')
    try :
        req = urllib.request.Request(url=url, data=data, headers=headers)
        opener = urllib.request.build_opener()
        response = opener.open(req)
        xml_response = response.read()
        print("descargando categorias")
        parser_data = xmltodict.parse(xml_response)['GetCategoriesResponse']['CategoryArray']['Category']
        return insert_table(parser_data)

    except Exception as e:
        pass

def generate_html(category_id):
    conn = sqlite3.connect('ebaydb.db')
    c = conn.cursor()
    query = c.execute("SELECT * FROM categories WHERE categoryId = ?", (category_id,))
    trae_category = query.fetchall()
    if trae_category:
        f = open('{0}.html'.format(category_id), 'w')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('    <title>{0}</title>\n'.format(category_id))
        f.write('</head>\n')
        f.write('<body>\n')
        parent_id = trae_category[0][0]
        parent_name = trae_category[0][1]
        print('Raiz', parent_id, parent_name)
        f.write('\t\t<li>{0}: {1}</li>\n'.format(parent_id, parent_name))        
        f.write('\t\t<div>\n')

        def print_children(parent_id, parent_name):
            children = c.execute('SELECT * FROM categories WHERE CategoryParentID = ? AND categoryId <> ?', (parent_id, category_id)).fetchall()
            if children:
                f.write('\t<ul>parent: {0}- {1}\n'.format(parent_id, parent_name))
                for child in children:
                    child_id = child[0]
                    child_name = child[1]
                    print_children(child_id, child_name)
                f.write('\t</ul>\n')
            else:
                f.write('\t\t<li>{0} - {1}</li>\n'.format(parent_id, parent_name))

        print_children(parent_id,parent_name)

        f.write('\t\t</div>\n')

        f.write('</body>\n')
        f.write('</html>')
        f.close()
        c.close()
        conn.close()
        webbrowser.open('{0}.html'.format(category_id), new=2)

    else:
        print("no existe category_id = ", category_id)
        sys.exit(2)

def main(argv):
    if len(argv) < 2:
        print('Parámetros incorrectos! Usar:')
        print ('test.py --rebuild')
        print('o')
        print ('test.py --render <category_id>')
        sys.exit(2)

    argument = argv[1]

    if argument == '--rebuild':
        #Consume API
        load_data()
    elif argument == "--render":
        #Generate HTMLhtm

        if len(argv) < 3:
            print('Parámetros incorrectos! Usar:')
            print ('test.py --rebuild')
            print('o')
            print ('test.py --render <category_id>')
            sys.exit(2)

        category_id = argv[2]
        generate_html(category_id)

if __name__ == "__main__":
   main(sys.argv)