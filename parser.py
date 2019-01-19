import requests as r
from bs4 import BeautifulSoup
from datetime import datetime
import re
import traceback
import pymongo as pm

_INGREDIENTS = 'ingredients'
_NAME = 'name'
_FUNCTION = 'function'
_UV = 'UV'
_ACNE = 'acne'
_IRRITANT = 'irritant'
_SAFETY = 'safety'
_COSDNA_ID = 'cosdnaId'

_DATE = 'posted_date'
_SOURCE = 'source'

_HEADER = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

def get_data_from_url(url):
    headers = {'User-Agent':_HEADER}

    res = r.get(url, headers=headers)

    soup = BeautifulSoup(res.text, 'html.parser')

    try:
        prodName = soup.find(class_="ProdTitleName").text

        info = soup.find_all(text=re.compile("Posted: 20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]"))[0]

        if info:
            date_str = re.search('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', info).group(0)
            date = datetime.strptime(date_str, '%Y-%m-%d')

            data_source = re.search('Data Source: (.*)', info).group(1)
    except:
        print("Can't parse url ", url)
        print(traceback.format_exc())
        return

    product_info = {_NAME: prodName, _DATE: date, _SOURCE: data_source}

    ingredients = []
    table = soup.find('table', attrs={'class':'iStuffTable'})

    rows = table.find_all('tr')

    for row in rows[1:]:
        cols = row.find_all('td')
        ing_id = cols[0].find('a')['href'].split('.')[0]
        cols = [ele.text.strip() for ele in cols]

        ingredient = None

        if len(cols) == 6:
            ingredient = {_NAME: cols[0], _FUNCTION: cols[1], _UV: cols[2], _ACNE: cols[3],
                    _IRRITANT: cols[4], _SAFETY: cols[5], _COSDNA_ID: ing_id}
        elif len(cols) == 5:
            ingredient = {_NAME: cols[0], _FUNCTION: cols[1], _ACNE: cols[2],
                    _IRRITANT: cols[3], _SAFETY: cols[4], _COSDNA_ID: ing_id}
        else:
            raise ValueError('Wrong data format: ', str(cols))

        ingredients.append(ingredient)

    return product_info, ingredients

def add_to_db(urls):
    client = pm.MongoClient("mongodb://localhost:27017/")
    db = client["cosmetics"]

    ing_coll = db["ingredients"]
    ing_coll.create_index([(_COSDNA_ID, pm.DESCENDING), (_NAME, pm.ASCENDING)], unique=True, sparse=True)
    prod_coll = db["products"]

    for url in urls:
        product_info, ingredients = get_data_from_url(url)
        print(product_info, ingredients)

        prod_ings = []

        for ing in ingredients:
            obj_id = None

            ing_doc = ing_coll.find_one(ing)
            if ing_doc:
                obj_id = ing_doc['_id']
            else:
                obj_id = ing_coll.insert(ing)

            prod_ings.append(obj_id)

        product_info[_INGREDIENTS] = prod_ings
        prod_coll.insert(product_info)

def main():
    urls = ["http://www.cosdna.com/eng/cosmetic_b39a415589.html",
            "http://www.cosdna.com/eng/cosmetic_2fda415800.html",
            "http://www.cosdna.com/eng/cosmetic_58f7415798.html",
            "http://www.cosdna.com/eng/cosmetic_3ae2415796.html"]
    add_to_db(urls)

if __name__ == "__main__":
    main()
