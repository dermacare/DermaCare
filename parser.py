import requests as r
from bs4 import BeautifulSoup
from datetime import datetime
import re

headers = {'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

res = r.get("http://www.cosdna.com/eng/cosmetic_b39a415589.html", headers=headers)


soup = BeautifulSoup(res.text, 'html.parser')

prodName = soup.find(class_="ProdTitleName").text

info = soup.find_all(text=re.compile("Posted: 20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]"))[0]

if info:
    date_str = re.search('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]', info).group(0)
    date = datetime.strptime(date_str, '%Y-%m-%d')

    data_source = re.search('Data Source: (.*)', info).group(1)


ing_coll = []
table = soup.find('table', attrs={'class':'iStuffTable'})

rows = table.find_all('tr')

_INGR = 'Ingredient'
_FUNC = 'Function'
_UV = 'UV'
_ACNE = 'Acne'
_IRR = 'Irritant'
_SAFE = 'Safety'
_CID = 'CosdnaId'

# rows[0]= ['Ingredient', 'Function', 'UV', 'Acne', 'Irritant', 'Safety']
for row in rows[1:]:
    cols = row.find_all('td')
    ing_id = cols[0].find('a')['href'].split('.')[0]
    cols = [ele.text.strip() for ele in cols]

    ingridient = {_INGR: cols[0], _FUNC: cols[1], _UV: cols[2], _ACNE: cols[3],
            _IRR: cols[4], _SAFE: cols[5], _CID: ing_id}

    ing_coll.append(ingridient)

