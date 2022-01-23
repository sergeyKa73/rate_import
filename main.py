import urllib.request
import  xml.dom.minidom as minidom
import sqlite3
import datetime


url ='http://www.cbr.ru/scripts/XML_daily.asp'
db_path = './currencies.db'

def get_data(url):
    web_file = urllib.request.urlopen(url)
    if web_file.code == 200:  # 200
        return web_file.read()
    print(web_file.code)


def get_currencies(xml):

    dom = minidom.parseString(xml)
    dom.normalize()

    elements = dom.getElementsByTagName('Valute')
    currency_dict = {}

    for node in elements:
        for child in node.childNodes:
            if child.nodeType == 1:
                if child.tagName == 'Value':
                    if child.firstChild.nodeType == 3:
                        value = float(child.firstChild.data.replace(',', '.'))
                if child.tagName == 'CharCode':
                    if child.firstChild.nodeType == 3:
                        char_code = child.firstChild.data
        currency_dict[char_code] = value
    return currency_dict

def write_current_db(cur_dict, path): # создание db и запись в нее

    def count_records(table, cursor): # поиск элементов в таблице db
        sql = F'SELECT COUNT(*) as count FROM {table}'
        cursor.execute(sql)
        id = cursor.fetchone()[0]+1
        return id


    table = 'currencies'

    con = sqlite3.connect(path)
    cur = con.cursor()

    query = F'CREATE TABLE IF NOT EXISTS {table} (id, usd_rate, eur_rate, byn_rate, data)'
    cur.execute(query)
    con.commit()

    query = F'INSERT INTO {table} VALUES ({count_records(table, cur)},{cur_dict["USD"]},{cur_dict["EUR"]},{cur_dict["BYN"]},"{datetime.datetime.now()}")'
    cur.execute(query)
    con.commit()
    con.close()

def read_currencies_db(path): # чтение данных из db
    table = 'currencies'

    con = sqlite3.connect(path)
    cur = con.cursor()

    query = F'SELECT * FROM {table}'
    cur.execute(query)

    data_fetched = cur.fetchall()

    currencies_list = []
    for line in data_fetched:
        currencies_list.append(list(line))

    con.close()

    return currencies_list


def main():
    data = get_data(url)
    currency_dict = get_currencies(data)
    write_current_db(currency_dict, db_path)
    #print(currency_dict)
    read_currencies_db(db_path) #чтение из базы данных
    print(read_currencies_db(db_path))


if __name__ == '__main__':
    main()
