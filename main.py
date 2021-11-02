import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import shutil
import csv
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', '-d',type = str, default = '.', help='path to your imgs')
    parser.add_argument('--csv_path', '-c',type = str, default = '.', help='path to save csv')
    parser.add_argument('--type', '-t',type = str, default = 'jpg')
    return parser.parse_args()

class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super().__init__()
        self.main_widget = FormWidget(self)
        self.setCentralWidget(self.main_widget)
        self.init_UI()

    def init_UI(self):
        self.setGeometry(150, 200, 1100, 800)
        self.setWindowTitle('Image Review')

        # create search button
        self.textbox = QLineEdit(self)
        self.textbox.move(770, 51)
        self.textbox.resize(80,37)
        self.button = QPushButton('Search', self)
        self.button.move(850,50)
        self.button.resize(100,40)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        self.main_widget.imagenumber = int(textboxValue)-1
        self.main_widget.showimage(self.main_widget.imagenumber)
    
    def set_status_message(self, message):
        return self.statusBar().showMessage(message) 

class FormWidget(QWidget):

    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.parent = parent
        # size parameter
        self.left = 30
        self.top = 30
        self.width = 640
        self.height = 480
        self.imagenumber=0
        self.numofimage=0
        # img dir
        self.args =parse_args()
        print(self.args)
        self.dir = self.args.img_path                         
        # fail,good,average,poor dir
        self.fail_dir =[ self.dir+"/../fail",    
                         self.dir+"/../good",                     
                         self.dir+"/../average",                            
                         self.dir+"/../poor"]
        # if not exist, make dir
        for p in self.fail_dir:
            if not os.path.exists(p):
                os.makedirs(p)
        # csv save dir
        self.csv_dir = self.args.csv_path
        self.type = self.args.type
        # go,stop interval
        self.timer = QTimer(self, interval=2 * 1000, timeout=self.change_image)
        self.pushed = False
        self.init_UI()

    # change to prev or next image
    def change_image(self, direction='1'):
        if self.pushed:
            if direction == '1':
                self.imagenumber -=1
            self.pushed = False
        self.imagenumber=self.imagenumber+int(direction)
        self.showimage(self.imagenumber)

    # key press event
    def keyPressEvent(self, event):
        key=event.key()
        if key==Qt.Key_Right:
            self.change_image('1')
        elif key==Qt.Key_Left:
            self.change_image('-1')

    # init UI
    def init_UI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel(self)
        layout.addWidget(self.label)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.showimage(0)
        self.buttons()
        self.show()

    # display image
    def showimage(self,imagenumber):
        imagelist = [ p for p in os.listdir(self.dir) if p.split('.')[-1]=='jpg']
        self.numofimage = len(imagelist)
        if imagenumber == -1:
            self.imagenumber = self.numofimage-1
        if abs(imagenumber) >= self.numofimage:
            self.imagenumber = abs(imagenumber) % self.numofimage
        self.log_window(str(self.imagenumber+1)+'/'+str(self.numofimage))
        pixmap = QPixmap(self.dir + '/' + imagelist[self.imagenumber])
        # for resizing display image
        # pixmap = pixmap.scaled(pixmap.width()*(1.5), pixmap.height()*(1.5), Qt.KeepAspectRatio)          
        self.parent.set_status_message(imagelist[self.imagenumber])
        self.label.setPixmap(pixmap)
        self.label.setContentsMargins(10, 20, 10, 10)
        self.label.setAlignment(Qt.AlignCenter)
    
    # make buttons
    def buttons(self):
        btn1 = QPushButton("Prev", self)
        btn1.move(120, 10)
        btn1.resize(100,40)
        btn1.clicked.connect(lambda: self.change_image('-1'))

        btn2 = QPushButton("Next", self)
        btn2.move(225, 10)
        btn2.resize(100,40)
        btn2.clicked.connect(lambda: self.change_image('1'))

        btn3 = QPushButton("Fail", self)
        btn3.move(400, 10)
        btn3.resize(100,40)
        btn3.clicked.connect(lambda: self.move_image(0))

        btn4 = QPushButton("Good", self)
        btn4.move(400, 50)
        btn4.resize(100,40)
        btn4.clicked.connect(lambda: self.move_image(1))

        btn5 = QPushButton("Average", self)
        btn5.move(505, 50)
        btn5.resize(100,40)
        btn5.clicked.connect(lambda: self.move_image(2))

        btn6 = QPushButton("Poor", self)
        btn6.move(610, 50)
        btn6.resize(100,40)
        btn6.clicked.connect(lambda: self.move_image(3))

        btn7 = QPushButton("CSV_Save", self)
        btn7.move(770, 10)
        btn7.resize(80,39)
        btn7.clicked.connect(self.csv_save)

        btn8 = QPushButton("Go", self)
        btn8.move(120, 50)
        btn8.resize(100,40)
        btn8.clicked.connect(self.go)

        btn9 = QPushButton("Stop", self)
        btn9.move(225, 50)
        btn9.resize(100,40)
        btn9.clicked.connect(self.stop)

    # move to next image
    def move_image(self, Type):
        imagelist = [ p for p in os.listdir(self.dir) if p.split('.')[-1]==self.type]
        # you can move
        shutil.move(self.dir+'/' + imagelist[self.imagenumber], self.fail_dir[Type]+'/' + imagelist[self.imagenumber])
        # you can copy
        # shutil.copy(self.dir+'/' + imagelist[self.imagenumber], self.fail_dir[Type]+'/' + imagelist[self.imagenumber])
        self.parent.set_status_message(f"move to {str(Type)}")
        self.pushed = True

    # log window
    def log_window(self,txt):
        log = QPlainTextEdit(self)
        log.move(10, 10)
        log.resize(100,40)
        log.setReadOnly(True)
        log.appendPlainText(txt)
        log.show()

    # csv save
    def csv_save(self):
        fails = os.listdir(self.fail_dir[0])
        with open(self.csv_dir+'/fail_list.csv', 'wt', encoding='utf-8',newline = '') as f:
            writer = csv.writer(f)
            writer.writerow(['filename'])
            for f in fails:
               writer.writerow([f])
        self.parent.set_status_message("CSV save done!")

    def go(self):
        QTimer.singleShot(0,self.change_image)
        self.timer.start()

    def stop(self):
        self.timer.stop()

if __name__ == '__main__':
    APP = QApplication(sys.argv)
    MainWindow()
    sys.exit(APP.exec_())