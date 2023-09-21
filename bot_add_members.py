from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
import csv
import traceback
import time


with open('info.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Read and store the header row
    for row in reader:
        # print(row[0])
        api_id = row[0]
        api_hash = row[1]
        phone = row[2]
        password=row[3]
        print (api_id)
        client = TelegramClient(phone, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            client.sign_in(phone, input('Enter the code: '), password=password)
        
        input_file = "members_"+ api_id +".csv"
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['id'] = int(row[1])
                user['access_hash'] = int(row[2])
                user['name'] = row[3]
                users.append(user)
        
        chats = []
        last_date = None
        chunk_size = 200
        groups=[]
        
        result = client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash = 0
                ))
        chats.extend(result.chats)
        
        for chat in chats:
            try:
                if chat.megagroup== True:
                    groups.append(chat)
            except:
                continue
        
        print('Choose a group to add members:')
        i=0
        for group in groups:
            print(str(i) + '- ' + group.title)
            i+=1
        
        g_index = input("Enter a Number: ")
        target_group=groups[int(g_index)]
        
        target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)
        
        mode = int(input("Enter 1 to add by username or 2 to add by ID: "))
        
        for user in users:
            try:
                print ("Adding {}".format(user['id']))
                if mode == 1:
                    if user['username'] == "":
                        continue
                    user_to_add = client.get_input_entity(user['username'])
                elif mode == 2:
                    user_to_add = InputPeerUser(user['id'], user['access_hash'])
                else:
                    sys.exit("Invalid Mode Selected. Please Try Again.")
                client(InviteToChannelRequest(target_group_entity,[user_to_add]))
                print("Waiting 60 Seconds...")
                time.sleep(60)
            except PeerFloodError:
                print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
            except UserPrivacyRestrictedError:
                print("The user's privacy settings do not allow you to do this. Skipping.")
            except:
                traceback.print_exc()
                print("Unexpected Error")
                continue