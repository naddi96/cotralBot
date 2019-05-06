#coding=utf-8
from APIcotral import *
from autenticazione import *
import telepot
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup,InlineKeyboardButton,ForceReply,ReplyKeyboardMarkup
import xml.etree.ElementTree as ET
import time
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





def sendData(k):
    try:
        username = k['from']['username']
    except:
        username ="null"
    try:
        first_name = k['from']['first_name']
    except:
        first_name ="null"
    try:
        last_name  = k['from']['last_name']
    except:
        last_name = "null"

    ida  =k['from']['id']
    try:
        text= k['text']
    except:
        text= "null"
    stri ="nik: "+username+ "\n"+"nome: "+first_name+"\n"+"cognome: "+ last_name+"\n" +"id: "+str(ida)+"\n"+"mex: "+text
    bot.sendMessage('114695529',stri)





def track(chat_id,vettura):
    posizione = getPosizioneVet(vettura)
    if (posizione == 'non esiste'):
        return
    tim = posizione['ora']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='termina update',callback_data='kill,update')]])
    msg_pos = bot.sendLocation(chat_id, posizione['X'], posizione['Y'],live_period=2000 )
    timeout = time.time()+1999
    msg = bot.sendMessage(chat_id,'posizione aggiornata: '+posizione['ora'])
    bot.sendMessage(chat_id,'--------------------------------------------------------',reply_markup=keyboard)
    msg_pos_id =  telepot.message_identifier(msg_pos)
    msg_id =  telepot.message_identifier(msg)

    while(True):
        mutex = thread[chat_id][0]
        mutex.acquire()
        if(thread[chat_id][1] == 1 or timeout > time.time()):
            return
        else:
            mutex.release()
        posizione = getPosizioneVet(vettura)
        if (posizione == 'non esiste'):
            return
        if tim != posizione['ora'] :
             tim = posizione['ora']
             keyboard = InlineKeyboardMarkup(inline_keyboard=[
             [InlineKeyboardButton(text= posizione['ora']+' termina update',callback_data='kill,update')]])
             bot.editMessageLiveLocation(msg_pos_id,posizione['X'], posizione['Y'],)
             bot.editMessageText(msg_id,'posizione aggiornata: '+posizione['ora'])
        time.sleep(10)


def inviaPosizione(chat_id,automezzo):
    posizione = getPosizioneVet(automezzo)
    if posizione == "non esiste":
        bot.sendMessage(chat_id,"non esistente")
        return
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='aggiorna ' + automezzo + ' ora:' + posizione['ora'], callback_data='poss'+','+automezzo)]
        ,[InlineKeyboardButton(text='tienimi aggiornato', callback_data='agg'+','+automezzo)]])
        bot.sendLocation(chat_id, posizione['X'], posizione['Y'], reply_markup=keyboard)
        return


def inviaPaline(chat_id,posizione):
    root = getPalineFromPos(posizione)
    inline_keyboar =[]
#    print(root.attrib['estratte'])
    if root.attrib['estratte']== '0':
        return
    for pal in root:
        inline_keyboar.append([InlineKeyboardButton(text=  pal[0].text+" "+pal[1].text+ " " ,callback_data='palina,'+pal[0].text)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboar)
    bot.sendMessage(chat_id,'elenco paline',reply_markup=keyboard)
    return


def sendBusFromPalina(chat_id,palina):
        XML = getIdCorseXML(palina)
        count = 0
        for x in XML:
             if x[0].tag == "idCorsa":
                 if x[11].text.lower() == "n.d." or x[11].attrib['isAlive'] == "0":
                    bot.sendMessage(chat_id,'non tracciabile\n'+ convertiOra(x[3].text) +' partenza ='
                                    + x[2].text+'\n' +x[13].text +'\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text)
                 else:
                    bot.sendMessage(chat_id,convertiOra(x[3].text) +' partenza = ' + x[2].text +'\n' +x[13].text +
                                    '\n'+convertiOra(x[5].text) + ' arrivo = ' + x[4].text )
                    inviaPosizione(chat_id,x[11].text)
                 count = count + 1
        bot.sendMessage(chat_id,'corse estratte: '+ str(count))
        return

def sendBus(chat_id,mex):
    mex1 = mex.split(",")
    partenza = mex1[0]
    arrivo = mex1[1]
    
    
    codiceStop = getCodiceStop(partenza)

    if(codiceStop =='non esiste'):
        bot.sendMessage(chat_id,'fermata non esistente')
        return 
    if(codiceStop =='errore server'):
        bot.sendMessage(chat_id,'errore server')      
        return
    codiceStop = codiceStop[1]  
    palina = getPalinaFromCodiceStop(codiceStop)
    XML = getIdCorseXML(palina)
   # print(XML[0][0])
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
    return
    #print(XML.text)

def uccidi(from_id,null):
    mutex = thread[from_id][0]
    mutex.acquire()
    thread.update({from_id:[mutex,1]})
    mutex.release()
    return


#funzione eseguita nel caso venga premuto un pulsante
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
    if list[0] == 'palina':
        palina = list[1]
        thx = myThread(from_id,palina,sendBusFromPalina)
        thx.start()

#funzione eseguita quando arriva un messaggio
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
#    print (msg)


    if content_type=='text' and '/traccia' == msg['text'][:8]:
        thx = myThread(chat_id,str(int(msg['text'][8:])),inviaPosizione)
        thx.start()



    if content_type=='text' and '/fermata' == msg['text'][:8]:
        thx = myThread(chat_id,msg['text'][8:].replace(" ",""),sendBusFromPalina)
        thx.start()

    if content_type=='text':
        sendData(msg)


    if content_type == 'text' and chat_id == 114695529 and '/inviamexx' in msg['text']:
        chat=msg["text"][10:19]
        bot.sendMessage(chat,msg["text"][19:])

    '''
    if content_type =='text' and (not('/start' in msg['text']) and not("," in msg['text'])):
        string="perfavore inserire la partenza e la destinzaione nel modo corretto,\n"+"nel formato:\n"+"partenza,destinazione\n"+"esempio, per avere le partenze prossime da ponte mammolo che vanno a subiaco dovro inviare:"
        bot.sendMessage(chat_id,string)
        bot.sendMessage(chat_id,"ponte mammolo,subiaco")
        bot.sendMessage(chat_id,"oppure\nponte,subiaco\ninvece se condividete una posizione con il bot vi invia tutte le fermate vicine a quella posizione ")
    '''
    if content_type == 'text' and 'start' in msg['text']:
        bot.sendMessage('114695529',msg)
        addChatid(chat_id)
        bot.sendMessage(chat_id,
                        'Ciao, sono il bot del cotral \n'
                        'per ottenere le fermate digitare il nome della località poi seleziona la fermata di cui vuoi sapere i cotral in arrivo\n'
                        'per problemi o sugerimenti contattare: @naddi0')
 
    if content_type == 'text' and ',' in msg['text']:
        thx = myThread(chat_id,msg['text'], sendBus)
        thx.start()

    if content_type == 'location':
        posizione = {'lat':msg['location']['latitude'], 'lon':msg['location']['longitude']}
        thx = myThread(chat_id,posizione,inviaPaline)
        thx.start()
        bot.sendMessage(chat_id,str(msg['location']['latitude'])+' '+str(msg['location']['longitude']) )

    if content_type == "text" and not("," in msg['text']) and not("/" in msg['text']):
        inviaPaline(chat_id,getPosizioneLoc(msg['text']))



with open('token.txt', "r") as myfile:
    TOKEN = myfile.readlines()[0]
  
    while True:
        try:
            bot = telepot.Bot(TOKEN)
            MessageLoop(bot, {'chat': on_chat_message,
                             'callback_query': on_callback_query}).run_as_thread()
            print('Listening ...')
            while 1:
                time.sleep(10)
    
        except Exception as error: 
            print(error)     
            bot = telepot.Bot(TOKEN)
            bot.sendMessage('114695529',error)
            print('errore')






