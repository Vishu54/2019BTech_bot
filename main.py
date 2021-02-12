import time
import json
import requests
import urllib
import sqlite3

conn = sqlite3.connect('2019BTech.db')

# GLOBAL VARIABLES
TOKEN = ''
URL = f"https://api.telegram.org/bot{TOKEN}/"
CSR = conn.cursor()


# FETCH THE RESPONSE FROM THE URL
def getUrl(url):
    resp = requests.get(url)
    content = resp.content.decode('utf8')
    return content


# CONVERT THE RESPONSE TO JSON FILE
def getJson(url):
    content = getUrl(url)
    js = json.loads(content)
    return js


# GET THE LATEST UPDATE ON THE BOT
def getUpdates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = getJson(url)
    return js


# GET THE LAST UPDATEID
def getLastUpdateId(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# SEND THE MESSAGE
def sendMessage(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    getUrl(url)


# GET THE CHAT ID
def getChatId_Text(update):
    for update in update["result"]:
        try:
            text = update["message"]["text"]
        except:
            text = "PLEASE DONOT SEND AUDIO VIDEO AND PICTURE TO THE BOT"
        finally:
            pass
        chat = update["message"]["chat"]["id"]
    return text, chat


# SEARCHING FOR THE QUERY AND CALLING THE SEND MESSAGE FUNCTION
def getQuery(update):
    txt = ''
    text, chat = getChatId_Text(update)
    if text == "/start":
        txt = 'Welcome to ITER BTech2019 bot\nType the name or registration number of your classmate\nand get details about them\n\nPLEASE DONOT SEND ANY IMAGE AND VIDEO TO THE BOT'
        sendMessage(txt, chat)
        return
    text = text.upper()
    if text.isnumeric():
        CSR.execute(f"SELECT * FROM data WHERE ENROLLMENTID = '{text}'")
    else:
        CSR.execute(f"SELECT * FROM data WHERE NAME like '%{text}%'")

    data = CSR.fetchall()

    if len(data) == 0:
        txt = "ERROR 404 !!"
        sendMessage(txt, chat)
        return
    for regd, name, sec, mob in data:
        txt = f'REGISTRATION NO - {regd}\nNAME - {name}\nSECTION - {sec}\nMOBILE - {mob}'
        sendMessage(txt, chat)



# DRIVER CODE
def main():
    lastUpdateId = None
    while True:
        updates = getUpdates(lastUpdateId)
        if len(updates["result"]) > 0:
            lastUpdateId = getLastUpdateId(updates) + 1
            getQuery(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
