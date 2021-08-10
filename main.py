import smtplib, ssl
import sys
from email.mime.text import MIMEText

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from time import strftime, gmtime, time

import requests as requests

OLX_URL = 'https://www.olx.pl/nieruchomosci/domy/krakow/?search%5Bfilter_float_price%3Afrom%5D=100000&search%5Bfilter_float_price%3Ato%5D=1200000&search%5Bfilter_float_m%3Afrom%5D=100&search%5Bfilter_float_area%3Afrom%5D=700&search%5Bdist%5D=15'


class Home:
    def __init__(self, id, name, url, img):
        self.id = id
        self.name = name
        self.url = url
        self.img = img

    def __str__(self) -> str:
        return "Home id:%s name:%s url:%s" % (self.id, self.name, self.url)

    def __repr__(self) -> str:
        return "Home id:%s name:%s url:%s" % (self.id, self.name, self.url)


def olx_parser(home_ids):
    data = []
    page = requests.get(OLX_URL)
    soup = BeautifulSoup(page.text, "lxml")
    tables = soup.find_all('table', attrs={'summary': 'Ogłoszenie'})
    for table in tables:
        id = table.attrs['data-id']
        if id in home_ids:
            continue
        text = ""
        url = ""
        img = ""
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if cols[0].contents[1].name == 'a':
                url = cols[0].contents[1].attrs['href']
            if cols[0].contents[1].contents[1].name == 'img':
                img = cols[0].contents[1].contents[1].attrs['src']
            cols = [ele.text.rstrip() for ele in cols]
            for col in cols:
                text = text + col.replace("\n", " ") + " "
        while '  ' in text:
            text = text.replace('  ', ' ')
        data.append(Home(table.attrs['data-id'], text, url, img))

    return data


def write_to_file(homes):
    f = open("homes.txt", "a")
    for home in homes:
        f.writelines(home.id + "\n")
    f.close()


def read_from_file():
    f = open("homes.txt", "r")
    home_ids = f.readlines()
    f.close()
    parsed_home_ids = []
    for id in home_ids:
        parsed_home_ids.append(id.strip())
    return parsed_home_ids


def send_mail(text):
    global server
    user = 'xxxxxxx'
    pwd = 'xxxxxxxxx'
    FROM = 'xxxxxx'
    TO = ['xxxxxm', 'xxxxxx']
    SUBJECT = 'Home sweet home'
    TEXT = list_to_string(text)

    print(TEXT)
    try:
        msg = MIMEText(TEXT, 'html')
        msg['Subject'] = SUBJECT
        msg['From'] = FROM
        context = ssl.create_default_context()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls(context=context)
        server.login(user, pwd)
        server.sendmail(FROM, TO, msg.as_string())
        print('Successfully sent the mail')
    except:
        print("Failed to send mail", sys.exc_info()[0])
        return False
    finally:
        server.quit()
    return True


def list_to_string(homes):
    return_string = "<ul>"

    for home in homes:
        return_string += "<li><a href=\"" + home.url + "\">" + home.name + "</a></li>"
        if (home.img):
            return_string += '<img src=\"' + home.img + "\">"
    return_string += '</ul>'
    return return_string


def get_new_houses():
    home_ids = read_from_file()
    homes = olx_parser(home_ids)
    if homes:
        print("Found new houses: " + len(homes).__str__())
        if send_mail(homes):
            write_to_file(homes)


if __name__ == '__main__':
    print("Check at " + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    try:
        get_new_houses()
    except Exception as e:
        print("Connecting problems...")
        print(e)
