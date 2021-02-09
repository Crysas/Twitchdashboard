import json
import re
import sys
import threading
from time import sleep

import requests
from PyQt5.QtWidgets import *
import socket
from dotenv import load_dotenv
import os
import bot



class Mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_list = QListWidget(self, objectName="userList")
        load_dotenv()
        self.test()
        username = os.getenv("USERNAME")
        client_id = os.getenv("CLIENT_ID")
        token = os.getenv("AUTH_TOKEN")
        channel = os.getenv("CHANNEL").lower()
        Thread = threading.Thread(target=self.Testloop, daemon=True)

        Thread.start()
        self.initGui()

    def initGui(self):
        #linke Seite
        self.chat_label = QLabel(self)
        self.chat_label.setText("Userchat:")
        self.chat_label.setGeometry(20,20,90,30)
        self.chatbox = QTextEdit(self, objectName="Chatbox")
        self.chatbox.setGeometry(20,50, 500, 590)
        self.chat_input = QLineEdit(self)
        self.chat_input.setGeometry(20, 650, 430, 30)


        # Linke Seite Buttons
        self.apply_btn = QPushButton("Senden", self, objectName="Greenbutton")
        self.apply_btn.clicked.connect(self.senden)
        self.apply_btn.setGeometry(460, 650, 60, 30)
        self.chat_input.returnPressed.connect(self.senden)

        # Rechte Seite
        self.user_list_label = QLabel(self)
        self.user_list_label.setText("Zuschauer:")
        self.user_list_label.setGeometry(700,20,90,30)
        self.user_list_label.setStyleSheet("color: #f7f7f7; font-weight: bold")
        self.user_list.setGeometry(700, 50, 410, 590)

        # Rechte Seite Buttons
        #Ban Button
        self.ban_button = QPushButton("ban", self, objectName="Redbutton")
        self.ban_button.setGeometry(700, 650, 60, 30)
        self.ban_button.clicked.connect(self.ban)

        #mute Button
        self.mute_button = QPushButton("mute", self, objectName="Redbutton")
        self.mute_button.setGeometry(770, 650, 60, 30)
        self.mute_button.clicked.connect(self.mute)

        #unmod Button
        self.unmod_button = QPushButton("unmod", self, objectName="Redbutton")
        self.unmod_button.setGeometry(840, 650, 60, 30)
        self.unmod_button.clicked.connect(self.unmod)

        #mod Button
        self.mod_button = QPushButton("mod", self, objectName="Greenbutton")
        self.mod_button.setGeometry(910, 650, 60, 30)
        self.mod_button.clicked.connect(self.mod)

        #unmute Button
        self.unmute_button = QPushButton("unmute", self, objectName="Greenbutton")
        self.unmute_button.setGeometry(980, 650, 60, 30)
        self.unmute_button.clicked.connect(self.unmute)

        #VIP Button
        self.VIP_button = QPushButton("VIP", self, objectName="Greenbutton")
        self.VIP_button.setGeometry(1050, 650, 60, 30)
        self.VIP_button.clicked.connect(self.vip)

        #Fenster
        self.setWindowTitle("Dashboard")
        self.setGeometry(500, 400, 1400, 700)
        self.setStyleSheet(open("style.css").read())
        self.show()

    def Testloop(self):

        load_dotenv()
        server = 'irc.chat.twitch.tv'
        port = 6667
        username = os.getenv("USERNAME")
        client_id = os.getenv("CLIENT_ID")
        token = os.getenv("AUTH_TOKEN")
        channel = os.getenv("CHANNEL").lower()
        self.twitchserver = socket.socket()
        self.twitchserver.connect((server, port))
        self.twitchserver.send(f"PASS oauth:{token}\n".encode('utf-8'))
        self.twitchserver.send(f"NICK {username}\n".encode('utf-8'))
        self.twitchserver.send(f"JOIN #{channel}\n".encode('utf-8'))

        while True:
            response = self.twitchserver.recv(2048).decode('utf-8')
            sleep(0.5)
            if response.startswith('PING'):
                self.twitchserver.send("PONG\n".encode("utf-8"))
            elif len(response) > 0 and not response.startswith(':tmi'):
                username = re.search(r"\w+", response).group(0)
                CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
                message = CHAT_MSG.sub("", response)
                messages = username + ": " + message

                self.chatbox.append(messages)

    def senden(self):
       message = self.chat_input.text()
       self.twitchserver.send("PRIVMSG #{} :{}\r\n".format(os.getenv("CHANNEL").lower(), message).encode("utf-8"))
       self.chatbox.append(os.getenv("USERNAME") + ": " +message)
       self.chat_input.clear()
    def test(self):
        #TODO: LIST USERS WITH RANKS
        r = requests.get("http://tmi.twitch.tv/group/user/crysas95/chatters").json()
        chatters = r['chatters']['viewers']
        self.user_list.addItems(chatters)
    def ban(self):
        print('ban')

    def mute(self):
        print('mute Action')

    def unmod(self):
        print('Unmod Action')

    def mod(self):
        print('mod Action')

    def unmute(self):
        print('unmute Action')

    def vip(self):
        print('vip Action')



app = QApplication(sys.argv)
w = QWidget()
y = Mainwindow()
sys.exit(app.exec_())