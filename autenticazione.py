def addChatid(chat_id):
    if not (isRegistred(chat_id)):
        with open('usersCotral.txt', "a") as myfile:
            myfile.write(str(chat_id) + '\n')

def isRegistred(chat_id):
     with open('usersCotral.txt', "r") as myfile:
        k = myfile.read().split('\n')
     for x in k:
        if str(chat_id) == x:
           return True
     return False
