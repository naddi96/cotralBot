 # coding=utf-8
import requests
from telepot.loop import MessageLoop
import xml.etree.ElementTree as ET
import time






def convertiOra(secondi):
    minuti = int(secondi) / 60
    ore = minuti / 60
    min = minuti%  60
    if min < 10:
     return   str(ore) + ":0" + str(min)
    else:
     return str(ore) + ":" + str(min)

def getPalineFromDatabase(partenza,arrivo):
    tree = ET.parse('databasePaline.xml')
    root = tree.getroot()
    for x in root:
        if(partenza.lower() in x[1].text.lower()):
           try:
               for k in x[7]:
                   if arrivo.lower() in k.text.lower():
                       print (x[1].text +' '+ x[0].text)
                       print('     '+k.text)
           except:
               print(x[0].text+' errore')



#getPalineFromDatabase('sub','ana')

def getPalineFromPos(posizione):
    range = 0.005 #500 metri
    lat1 = posizione['lat'] - range
    long1 = posizione['lon'] - range
    lat2 = posizione['lat'] + range
    long2 = posizione['lon'] + range
    #print(str(lat1)+' '+str(long1))
    #print(str(lat2)+' '+str(long2))
    try:
        r2 = requests.get('http://travel.mob.cotralspa.it:7777/beApp/'
        'PIV.do?cmd=7&pX1=' + str(lat1) + '&pY1=' + str(long1) + '&pX2=' + str(lat2) + '&pY2=' + str(long2) + '&pZ=90')
    except:
        return 'errore server'
    root = ET.fromstringlist(r2.content)
    return root

def fromCodiceStopXML(codiceStop):
    try:
        r2 = requests.get("http://travel.mob.cotralspa.it:7777/beApp/"
        "PIV.do?cmd=5&userId=1BB73DCDAFA007572FC51E74"
        "07AB497C&pIdStop=" + codiceStop + "&pFormato=xml")
    except:
        return 'errore server'
    root2 = ET.fromstringlist(r2.content)
    return root2

#return the xml of palina
def getIdCorseXML(palina):
    try:
        r3 = requests.get(
            "http://travel.mob.cotralspa.it"
            ":7777/beApp/PIV.do?cmd=1&userId="
            "1BB73DCDAFA007572FC51E7407AB497C&p"
            "Codice=" + palina + "&pFormato=xml&pDelta=261")
    except:
        return 'errore server'
    root3 = ET.fromstringlist(r3.content)
    return root3


def fromPartenzaXML(partenza):
    try:
        r1 = requests.get(
        "http://travel.mob.cotralspa.it:7777/beApp"
        "/PIV.do?cmd=6&userId=1BB73DCDAFA007572FC51E7407AB497C&pStringa=" + partenza)
    except:
        return 'errore server'
    root = ET.fromstringlist(r1.content)
    return root


def getPalinaFromCodiceStop(codiceStop):
    try:
        r2 = requests.get("http://travel.mob.cotralspa.it:7777/beApp/PIV.do?cmd=5&userId=1BB73DCDAFA007572FC51E7407AB497C&pIdStop=" + codiceStop + "&pFormato=xml")
    except:
        return 'errore server'
    root2 = ET.fromstringlist(r2.content)
    try:
        codicePalina = root2[1][0].text
    except:
        codicePalina = root2[0][0].text

    return codicePalina


def getPalinaFromPartenza(partenza):
    codiceStop = getCodiceStop(partenza)[1]
    try:
        r2 = requests.get("http://travel.mob.cotralspa.it:7777/beApp/"
        "PIV.do?cmd=5&userId="
        "1BB73DCDAFA007572FC51E7407AB497C&pIdStop=" + codiceStop + "&pFormato=xml")
    except:
        return 'errore server'
    root2 = ET.fromstringlist(r2.content)
    try:
        codicePalina = root2[1][0].text
    except:
        codicePalina = root2[0][0].text
    return codicePalina


def getCodiceStop(partenza):
    try:
        r1 = requests.get(
        "http://travel.mob.cotralspa.it:7777/beApp"
        "/PIV.do?cmd=6&userId=1BB73DCDAFA007572FC51E7407AB497C&pStringa=" + partenza)
    except:
        return 'errore server'
    root = ET.fromstringlist(r1.content)
    if root.attrib['estratti'] == '0':
        return 'non esiste'
    for el in root:
        if partenza.lower() in el[1].text.lower():
            codiceStop = el[0].text
            return [el[1].text,codiceStop]



def getPosizione(vettura):
    if not(vettura.isdigit()):
        return "non esiste"
    try:
        r4 = requests.get(
            "http://travel.mob.cotralspa.it:7777/beApp/"
            "Automezzi.do?cmd=loc&userId=1BB73DCDAFA0075"
            "72FC51E7407AB497C&pAutomezzo=" + vettura + "&pFormato=xml")
        root6 = ET.fromstringlist(r4.content)
        if root6.attrib['estratte'] == '0':
            return "non esiste"
        return {'X':root6[0].attrib['pX'],'Y':root6[0].attrib['pY'], 'ora':root6[0].text}
    except:
        return "non esiste"
