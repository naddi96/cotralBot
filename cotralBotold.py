# coding=utf-8
import telepot
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton,  ForceReply,ReplyKeyboardMarkup
import thread
import xml.etree.ElementTree as ET
import time
import os


def convertiOra(secondi):
    minuti = int(secondi) / 60
    ore = minuti / 60
    min = minuti%  60
    if min < 10:
     return   str(ore) + ":0" + str(min)
    else:
     return str(ore) + ":" + str(min)

def isRegistred(chat_id):
     with open('usersCotral.txt', "r") as myfile:
        k = myfile.read().split('\n')
     for x in k:
        if str(chat_id) == x:
           return True
     return False

def addChatid(chat_id):
    if not (isRegistred(chat_id)):
        with open('usersCotral.txt', "a") as myfile:
            myfile.write(str(chat_id) + '\n')


#getPalina data la  partenza ritorna la palina
def getPalina(partenza):
    try:
        r1 = requests.get("http://travel.mob.cotralspa.it:7777/beApp/PIV.do?cmd=6&userId=1BB73DCDAFA007572FC51E7407AB497C&pStringa=" + partenza)
    except: return 'errore server'
    root = ET.fromstringlist(r1.content)
    if root.attrib['estratti'] == '0':
        return 'non esiste'
    for el in root:
        if partenza.lower() in el[1].text.lower():
            codiceStop = el[0].text
            break
    try:
        r2 = requests.get("http://travel.mob.cotralspa.it:7777/beApp/PIV.do?cmd=5&userId=1BB73DCDAFA007572FC51E7407AB497C&pIdStop=" + codiceStop + "&pFormato=xml")
    except:  return 'errore server'
    root2 = ET.fromstringlist(r2.content)
    try: codicePalina = root2[1][0].text
    except: codicePalina = root2[0][0].text
    return codicePalina


#inviaRisultati dato il codicePalina invia tutte le possibili corse, deve essere esuguita dopo getPalina()
def inviaRisultati(chat_id,codicePalina,arrivo):
    if codicePalina == 'errore server':
        bot.sendMessage(chat_id,'errore server')
        exit(0)
    if codicePalina == 'non esiste':
        bot.sendMessage(chat_id, 'non esiste')
        exit(0)

    try:
        r3 = requests.get("http://travel.mob.cotralspa.it"
                      ":7777/beApp/PIV.do?cmd=1&userId=1BB73DCDAFA007572FC51E7407AB497C&pCodice=" + codicePalina + "&pFormato=xml&pDelta=261")
    except:
        bot.sendMessage(chat_id,'errore server')
        exit(0)
    root3 = ET.fromstringlist(r3.content)
    count = 0
    if arrivo == 'tutto':
        arrivo = ''
    for x in root3:
     if x[0].tag == "idCorsa" and arrivo.lower() in x[4].text.lower():
         if x[11].text.lower() == "n.d." or x[11].attrib['isAlive'] == "0":
            bot.sendMessage(chat_id,'non tracciabile\n'+ convertiOra(x[3].text) +' partenza ='
                            + x[2].text+'\n' +x[13].text +'\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text)
         else:
            bot.sendMessage(chat_id,convertiOra(x[3].text) +' partenza = ' + x[2].text +'\n' +x[13].text +
                            '\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text )
            aggVettura(chat_id,x[11].text,'null')
         count = count + 1
    bot.sendMessage(chat_id,'corse estratte: '+ str(count))
    exit(0)




def track(chat_id,vettura):
    coord= '0'
    for i in range(1,70):
        newcoord = aggVettura(chat_id, vettura, coord)
        if coord != newcoord:
             bot.sendMessage(chat_id, 'aggiornato')
             coord = newcoord
        time.sleep(20)
    exit(0)



def agVettura(from_id,vett):
    aggVettura(from_id, vett,'0')
    exit(0)

def aggVettura(from_id,vett,coord):
    if not(vett.isdigit()):
        bot.sendMessage(from_id, 'vettura non esistente')
        exit(0)
    r4 = requests.get(
        "http://travel.mob.cotralspa.it:7777/beApp/Automezzi.do?cmd=loc&userId=1BB73DCDAFA007572FC51E7407AB497C&pAutomezzo=" + vett + "&pFormato=xml")
    root6 = ET.fromstringlist(r4.content)
    if root6.attrib['estratte'] == '0':
        bot.sendMessage(from_id, 'vettura non esistente')
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='aggiorna ' + vett + ' ora:' + root6[0].text, callback_data='poss'+','+vett)],
        [InlineKeyboardButton(text='tienimi aggiornato', callback_data='agg'+','+vett)]])
        if coord != root6[0].attrib['pX']:
            bot.sendLocation(from_id, root6[0].attrib['pX'], root6[0].attrib['pY'], reply_markup=keyboard)
        return root6[0].attrib['pX']
    exit(0)

def message_loop(chat_id,handle):  #handle deve essere una funzione che prende due argomenti il chat id e il messagio ricavato
    offset =0
    mes = bot.getUpdates(offset=offset)
    if len(mes)>0:
        offset = mes[-1]['update_id'] +1
    while True:
        mes = bot.getUpdates(offset=offset)
        if len(mes) > 0:
            offset = mes[-1]['update_id'] +1             #l'offset serve per evitare la prendita doppia di messagi ripetuti
            if ('entities' in mes[0]['message']) and mes[0]['message']['from']['id'] == chat_id:
                exit(0)
            if not('entities' in mes[0]['message']) and mes[0]['message']['from']['id'] == chat_id:
                handle(chat_id,mes[0]['message']['text'])
                exit(0)

def riceviArrivo_loop(list,handle):  #list e una lista contene l'id_chat e il codicePalina da dare a handle
    offset =0
    chat_id =list[0]
    codicePalina = list[1]
    mes = bot.getUpdates(offset=offset)
    if len(mes)>0:
        offset = mes[-1]['update_id'] +1
    while True:
        mes = bot.getUpdates(offset=offset)
        if len(mes) > 0:
            offset = mes[-1]['update_id'] +1             #l'offset serve per evitare la prendita doppia di messagi ripetuti
            if ('entities' in mes[0]['message']) and mes[0]['message']['from']['id'] == chat_id:
                exit(0)
            if not('entities' in mes[0]['message']) and mes[0]['message']['from']['id'] == chat_id:
                handle(chat_id,codicePalina,mes[0]['message']['text'])
                exit(0)

def riceviPartenza(chat_id, enza):
    palina = getPalina(enza)
    bot.sendMessage(chat_id, 'inserisci l`arrivo\n scrivi `tutto` per vedere tutte le partenze ')
    thread.start_new_thread(riceviArrivo_loop,([chat_id,palina],inviaRisultati))
    exit(0)

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg,flavor='callback_query')
    list = query_data.split(',')
    if list[0] == 'poss':
        aggVettura(from_id,list[1],'null')
    if list[0] == 'agg':
        thread.start_new_thread(track, (from_id, list[1]))

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text' and 'start' in msg['text']:
        bot.sendMessage('69886441',msg)
        bot.sendMessage('114695529',msg)
        addChatid(chat_id)
        bot.sendMessage(chat_id,
                        'Ciao, sono il bot del cotral \n'
                        'con /traccia ti chiederò di inserire la fermata di partenza e di arrivo, per inviarti le corse e se possibile il tracciamento\n '
                        'con /segui ti chiederò di inserire il codice vettura per inviarti la sua posizione. \n Per errori o suggerimenti contattare @Naddi96')
    if content_type == 'text' and '/segui' == msg['text']:
        bot.sendMessage(chat_id,'inserisci il codice vettura')
        thread.start_new_thread(message_loop,(chat_id,agVettura))
    if content_type == 'text' and '/traccia' in msg['text']:
        bot.sendMessage(chat_id,'inserisci la partenza')
        thread.start_new_thread(message_loop, (chat_id, riceviPartenza))
    if content_type == 'text' and '/manager' in msg['text']:
        bot.sendMessage(chat_id,"Ok")
        os.system('python play.py')
        





def dimmitutto(from_id):
    vett = 5000
    while True:
        r4 = requests.get(
            "http://travel.mob.cotralspa.it:7777/beApp/Automezzi.do?cmd=loc&userId=1BB73DCDAFA007572FC51E7407AB497C&pAutomezzo=" + str(vett) + "&pFormato=xml")
        root6 = ET.fromstringlist(r4.content)
        print(vett)
        if root6.attrib['estratte'] != '0':
         keyboard = InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text='aggiorna '+str(vett) +' ora:' + root6[0].text, callback_data='poss')],
         [InlineKeyboardButton(text='tienimi aggiornato', callback_data='agg')]])
         bot.sendLocation(from_id, root6[0].attrib['pX'], root6[0].attrib['pY'], reply_markup=keyboard)
        vett = vett +1


TOKEN = '463728803:AAG_MM0v0uGjFCAQ04t0wO_L48KKxasArXk'
bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()



print('Listening ...')
import time

while 1:
    time.sleep(10)



















