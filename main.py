from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QStyle, QSizePolicy, \
    QLineEdit, QLabel, QVBoxLayout
import sys
import json
from datetime import datetime
import os
from PyQt5.QtGui import QIcon, QPalette, QImage, QPixmap
from PyQt5.QtCore import Qt, QUrl
import cv2 as cv
from smtplib import SMTP
from email.mime.image import MIMEImage


class Window(QWidget):
    def __init__(self):
        super().__init__()
        haarcascade = self.kaynak_yolu('haarcascade_frontalface_default.xml')

        self.faces_cascade = cv.CascadeClassifier(haarcascade)

        self.playBtn = QPushButton()
        self.processBtn = QPushButton()
        # self.stopBtn = QPushButton()
        self.setWindowTitle("Piton Ar-Ge")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)


        self.init_ui()

        self.show()

    def init_ui(self):

        # create button for playing

        self.playBtn.setEnabled(True)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setText('Play')
        self.processBtn.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.processBtn.setText('Analyze')

        self.playBtn.clicked.connect(self.play_video)
        self.processBtn.clicked.connect(self.process_video)

        # getting rtsp link

        self.link = QLineEdit()
        self.mail = QLineEdit()
        self.nmbroffaces = QLineEdit()

        self.linklabel = QLabel('''<font size="5" color="red">Link:            </font>''')
        self.maillabel = QLabel('''<font size="5" color="red">Mail:            </font>''')
        self.nmbroffaceslabel = QLabel('''<font size="5" color="red">Number of Faces: </font>''')

        # create label

        self.label = QLabel('''<font size="2" color="black">Piton Ar-Ge Intern EEE - Mehmet Kaş </font>''')
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create hbox layout

        hboxLayout = QHBoxLayout()
        hboxLayout2 = QHBoxLayout()
        hboxLayout3 = QHBoxLayout()
        hboxLayout4 = QHBoxLayout()

        hboxLayout.addWidget(self.playBtn)

        hboxLayout.addWidget(self.processBtn)

        hboxLayout2.addWidget(self.linklabel)
        hboxLayout2.addWidget(self.link)

        hboxLayout3.addWidget(self.maillabel)
        hboxLayout3.addWidget(self.mail)

        hboxLayout4.addWidget(self.nmbroffaceslabel)
        hboxLayout4.addWidget(self.nmbroffaces)

        # create vbox layout

        vboxLayout = QVBoxLayout()

        vboxLayout.addLayout(hboxLayout2)
        vboxLayout.addLayout(hboxLayout3)
        vboxLayout.addLayout(hboxLayout4)
        vboxLayout.addLayout(hboxLayout)

        vboxLayout.addWidget(self.label)
        icon = self.kaynak_yolu('pythonlogo.ico')
        self.setLayout(vboxLayout)
        self.setWindowIcon(QIcon(icon))

    def play_video(self):

        capture = cv.VideoCapture(0)

        while 1:

            ret, frame = capture.read()
            if not ret:
                break

            cv.imshow('RTSP Stream', frame)
            self.playBtn.setEnabled(False)
            self.processBtn.setEnabled(False)

            if cv.waitKey(25) & 0xFF == ord('q'):
                self.playBtn.setEnabled(True)
                self.processBtn.setEnabled(True)
                break
        capture.release()
        cv.destroyAllWindows()

    def process_video(self):

        global j
        j = 1
        capture = cv.VideoCapture("rtsp://170.93.143.139/rtplive/470011e600ef003a004ee33696235daa")

        while True:
            ret, img = capture.read()
            if not ret:
                break
            gray = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            faces = self.faces_cascade.detectMultiScale(gray, 1.1, 5)

            print(len(faces))
            self.playBtn.setEnabled(False)
            self.processBtn.setEnabled(False)
            for (x, y, w, h) in faces:
                cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv.imshow('Analyzing Stream', img)

            self.t=int(self.nmbroffaces.text())

            if (len(faces) == self.t) & (j == 1):

                cv.imwrite('resim3.jpg', img)
                self.sendMail()
                self.saveJson()
                j = 0

            k = (cv.waitKey(30) & 0xff) == ord('q')

            if k:
                self.playBtn.setEnabled(True)
                self.processBtn.setEnabled(True)
                break

        capture.release()
        cv.destroyAllWindows()

    def sendMail(self):

        subject = "Piton Ar-Ge Internship"
        message = "Bu bir test mesajıdır."
        content = "Subject: {0}\n\n{1}".format(subject, message)

        fp = open('resim3.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        self.myMailAddress = "mhmt.kas@gmail.com"      #sending mail should be entered here
        password = "asd123asdmk."                       #sending mail's password should be entered here

        self.sendTo = self.mail.text()

        mail = SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        mail.login(self.myMailAddress, password)
        mail.sendmail(self.myMailAddress, self.sendTo, msgImage.as_string())

        print("mail gönderme işlemi başarılı")

    def saveJson(self):

        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        dosya = open("data.json", "a")
        dosya.write(str(self.t) +  " faces detected. \n")
        dosya.write("Sent from " + self.myMailAddress + " to " + self.sendTo + " at " + time+ "\n\n")
        print("kaydedildi.")

        dosya.close()

    def kaynak_yolu(self, goreceli_yol):
        temel_yol = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(temel_yol, goreceli_yol)


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec_())
