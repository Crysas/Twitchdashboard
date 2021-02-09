import os
import re
import socket
import sys
import threading
from time import sleep
#from BanDialog import BanWindow
import requests
from PyQt5 import QtCore

import BanDialog
from PyQt5.QtWidgets import *
from dotenv import load_dotenv

QtCore.QMetaType.type('QItemSelection')
QtCore.QMetaType.type('QTextCursor')


class Mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_list = QListWidget(self, objectName="userList")
        self.secondwindow = BanDialog.InitWindow()
        load_dotenv()
        username = os.getenv("USERNAME")
        client_id = os.getenv("CLIENT_ID")
        token = os.getenv("AUTH_TOKEN")
        channel = os.getenv("CHANNEL").lower()
        Thread = threading.Thread(target=self.Twitchloop, daemon=True)
        Chatlists = threading.Thread(target=self.Userloop, daemon=True)
        Chatlists.start()
        Thread.start()
        self.initGui()

    def passBanInfos(self):
        username = self.user_list.currentItem().text()
        self.secondwindow.username.setText(username)
        self.secondwindow.displayInfo()

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
        self.unmod_button.clicked.connect(self.passBanInfos)

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


    def Userloop(self):
        r = requests.get("http://tmi.twitch.tv/group/user/crysas95/chatters").json()
        while True:
            chatters = r['chatters']['viewers']
            self.user_list.clear()
            self.user_list.addItems(chatters)
            sleep(120)

    def Twitchloop(self):

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

    def chat(self, msg):
        self.twitchserver.send("PRIVMSG #{} :{}\r\n".format(os.getenv("CHANNEL").lower(), msg).encode("utf-8"))

    def senden(self):
       message = self.chat_input.text()
       self.twitchserver.send("PRIVMSG #{} :{}\r\n".format(os.getenv("CHANNEL").lower(), message).encode("utf-8"))
       self.chatbox.append(os.getenv("USERNAME") + ": " +message)
       self.chat_input.clear()

    def ban(self):
        user = self.user_list.currentItem().text()
        self.twitchserver.send("PRIVMSG #{} :.ban {}\r\n".format(os.getenv("CHANNEL"), user).encode("utf-8"))

    def mute(self, sock, secs=600):
        user = self.user_list.currentItem().text()
        self.twitchserver.send("PRIVMSG #{} :.timeout {} {}\r\n".format(os.getenv("CHANNEL"), user, secs).encode("utf-8"))

    def unmod(self):
        print("hallo")
        #user = self.user_list.currentItem().text()
        #self.twitchserver.send("PRIVMSG #{} :.unmod {}".format(os.getenv("CHANNEL"), user).encode("utf-8"))

    def mod(self):
        user = self.user_list.currentItem().text()
        self.twitchserver.send("PRIVMSG #{} :.mod {}".format(os.getenv("CHANNEL"), user).encode("utf-8"))

    def unmute(self):
        user = self.user_list.currentItem().text()
        self.twitchserver.send("PRIVMSG #{} :.unmute {}".format(os.getenv("CHANNEL"), user).encode("utf-8"))

    def vip(self):
        user = self.user_list.currentItem().text()
        self.twitchserver.send("PRIVMSG #{} :.vip {}".format(os.getenv("CHANNEL"), user).encode("utf-8"))



app = QApplication(sys.argv)
w = QWidget()
y = Mainwindow()
screen = app.primaryScreen()
size = screen.size()
print('Size: %d x %d' % (size.width(), size.height()))
sys.exit(app.exec_())