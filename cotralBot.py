# coding=utf-8
from APIcotral import *
from autenticazione import *
import telepot
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton,  ForceReply,ReplyKeyboardMarkup
#import thread
import xml.etree.ElementTree as ET
import time
import os
import threading
from threading import Lock

thread = {}

class myThread (threading.Thread):
   def __init__(self,chat_id,mex,func):
      threading.Thread.__init__(self)
      self.chat_id = chat_id
      self.mex =mex
      self.func = func
   def run(self):
      self.func(self.chat_id,self.mex)






def track(chat_id,vettura):
    tim = '123'
    mutex = thread[chat_id][0]
    while(True):
        print('funge')
        mutex.acquire()
        if(thread[chat_id][1] == 1):
            exit(0)
        else:
            mutex.release()
        posizione = getPosizione(vettura)
        if tim != posizione['ora']:
             tim = posizione['ora']
             keyboard = InlineKeyboardMarkup(inline_keyboard=[
             [InlineKeyboardButton(text= posizione['ora']+' termina update',callback_data='kill,update')]])
             bot.sendLocation(chat_id, posizione['X'], posizione['Y'], reply_markup=keyboard)
        time.sleep(2)


def inviaPosizione(chat_id,automezzo):
    posizione = getPosizione(automezzo)
    if posizione == "non esiste":
        bot.sendMessage(chat_id,"non esistente")
        return 0
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='aggiorna ' + automezzo + ' ora:' + posizione['ora'], callback_data='poss'+','+automezzo)]
        ,[InlineKeyboardButton(text='tienimi aggiornato', callback_data='agg'+','+automezzo)]])
        bot.sendLocation(chat_id, posizione['X'], posizione['Y'], reply_markup=keyboard)
        return 0

def sendBus(chat_id,mex):

    mex1 = mex.split(",")
    partenza = mex1[0]
    arrivo = mex1[1]
    codiceStop = getCodiceStop(partenza)[1]
    palina = getPalinaFromCodiceStop(codiceStop)
    XML = getIdCorseXML(palina)
    count = 0
    for x in XML:
         if x[0].tag == "idCorsa" and arrivo.lower() in x[4].text.lower():
             if x[11].text.lower() == "n.d." or x[11].attrib['isAlive'] == "0":
                bot.sendMessage(chat_id,'non tracciabile\n'+ convertiOra(x[3].text) +' partenza ='
                                + x[2].text+'\n' +x[13].text +'\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text)
             else:
                bot.sendMessage(chat_id,convertiOra(x[3].text) +' partenza = ' + x[2].text +'\n' +x[13].text +
                                '\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text )
                inviaPosizione(chat_id,x[11].text)
             count = count + 1
    bot.sendMessage(chat_id,'corse estratte: '+ str(count))
    exit(0)
    #print(XML.text)

def uccidi(from_id,null):
    mutex = thread[from_id][0]
    mutex.acquire()
    thread.update({from_id:[mutex,1]})
    mutex.release()
    exit(0)



def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg,flavor='callback_query')
    list = query_data.split(',')
    if list[0] == 'poss':
        inviaPosizione(from_id,list[1])
    if list[0] == 'agg':
        automezzo = list[1]
        thx = myThread(from_id,automezzo,track)
        mutex = Lock()
        thread.update({from_id:[mutex,0]})
        thx.start()
    if list[0] == 'kill':
        myThread(from_id,None,uccidi).start()


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text' and 'start' in msg['text']:
        bot.sendMessage('114695529',msg)
        addChatid(chat_id)
        bot.sendMessage(chat_id,
                        'Ciao, sono il bot del cotral \n'
                        'per ottenere le corse digitare "arrivo,destinazione" \n'
                        'per problemi o sugerimenti contattare: @naddi0')
    if content_type == 'text' and ',' in msg['text']:
        thx = myThread(chat_id,msg['text'], sendBus)
        thx.start()





TOKEN = '471402403:AAFzj2FdTDAqN-Y2XPBSHLAwqSuyJw8-JCs'
bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
#riceviArrivo_loop(list,agVettura(3213,'rfsdgfsdgf'))

print('Listening ...')
import time

while 1:
    time.sleep(10)
