import sys
import json
import time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QWidget, QStackedWidget, QStyleFactory, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QSpacerItem
from PyQt5.QtGui import QPainter, QPen, QColor, QMovie
# FIXME: why choose QtSerialPort over PySerial?
from PyQt5.QtSerialPort import QSerialPort

class HeaderLayout(QHBoxLayout):

    def __init__(self, title, parent = None):
        super().__init__(parent)
        self.emg = EmergencyStopButton()
        self.label = QLabel(title)
        self.label.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold;
            }
        """)
        self.addWidget(self.label)
        self.addStretch()
        self.addWidget(self.emg)

class EmergencyStopButton(QPushButton):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                background-image: url("media/stop-sign.png");
                border-radius: 0px;
                height: 48px;
                width: 48px;
            }
            QPushButton:pressed {
                background-image: url("media/stop-sign-pressed.png");
            }
        """)

class StyledPushButton(QPushButton):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setMinimumWidth(10)
        self.setMinimumHeight(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            StyledPushButton {
                background-color: #FFB900;
                border-radius: 5px;
                font: bold 14px;
            }
            StyledPushButton:pressed {
                background-color: #DB9E00;
            }
        """)

class StyledProgressBar(QProgressBar):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #FFB900;
                border-radius: 5px;
                text-align: center;
                background-color: #FF0000;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
                margin: 0px;
                border-radius: 5px;
            }
        """)

class StyledStackedWidget(QStackedWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(240, 320)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

    # draw the orange border    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor("#FFB900"))
        painter.setPen(pen)
        painter.drawRect(0, 0, 239, 319)
        
class ClickableLabel(QLabel):

    label_pressed = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        
    def mousePressEvent(self, ev):
        self.label_pressed.emit()

class IntroMenu(QWidget):

    start_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        #layout.setSpacing(8)
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.container = ClickableLabel()
        self.intro = QMovie("media/party.gif")
        self.container.setMovie(self.intro)

        self.title1 = QLabel("COCKTAIL")
        self.title2 = QLabel("MACHINE")
        self.title1.setAlignment(Qt.AlignCenter)
        self.title2.setAlignment(Qt.AlignCenter)
        self.title1.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 36px;
            }
        """)
        self.title2.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 36px;
            }
        """)
        
        self.container.label_pressed.connect(lambda: self.start_clicked.emit())

        self.layout.addStretch()
        self.layout.addWidget(self.title1)
        self.layout.addStretch()
        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.layout.addWidget(self.title2)
        self.layout.addStretch()
        self.intro.start()

class AlcoholMenu(QWidget):

    drink_clicked = pyqtSignal(bool)
    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        #layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        self.header = HeaderLayout("1. SELECT ALCOHOL")
        self.spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.choice1 = StyledPushButton()
        self.choice1.setText("NON-\nALCOHOLIC")
        #choice1.pressed.connect(lambda: self.changeForm.emit(2))
        self.choice2 = StyledPushButton()
        self.choice2.setText("ALL DRINKS")
        #choice2.pressed.connect(lambda: self.changeForm.emit(2))

        self.layout.addLayout(self.header, 0, 0, 1, 0)
        self.layout.addWidget(self.choice1, 1, 0)
        self.layout.addWidget(self.choice2, 1, 1)
        self.layout.addItem(self.spacer, 2, 0)
        self.layout.addItem(self.spacer, 3, 0)
        #layout.addStretch()
        #button = EmergencyStopButton()
        #layout.addWidget(button, 1, 0)
        
        self.choice1.pressed.connect(lambda: self.drink_clicked.emit(False))
        self.choice2.pressed.connect(lambda: self.drink_clicked.emit(True))
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())

class SelectMenu(QWidget):

    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        #layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        self.choice1 = StyledPushButton()
        self.choice1.setText("SEARCH BY \nNAME")
        #choice1.pressed.connect(lambda: self.changeForm.emit(1))

        self.choice2 = StyledPushButton()
        self.choice2.setText("SEARCH BY \nINGREDIENTS")

        self.choice3 = StyledPushButton()
        self.choice3.setText("RECENT \nDRINKS")

        self.choice4 = StyledPushButton()
        self.choice4.setText("CUSTOM \nDRINK")

        self.choice5 = StyledPushButton()
        self.choice5.setText("RANDOM \nDRINK")

        self.choice6 = StyledPushButton()
        self.choice6.setText("RANDOM \nINGREDIENTS")

        self.header = HeaderLayout("2. SELECT MODE")
        self.layout.addLayout(self.header, 0, 0, 1, 0)

        self.layout.addWidget(self.choice1, 1, 0)
        self.layout.addWidget(self.choice2, 1, 1)
        self.layout.addWidget(self.choice3, 2, 0)
        self.layout.addWidget(self.choice4, 2, 1)
        self.layout.addWidget(self.choice5, 3, 0)
        self.layout.addWidget(self.choice6, 3, 1)

        self.pb = StyledProgressBar()
        self.pb.setValue(50)
        self.layout.addWidget(self.pb, 4, 0, 1, 2)
        
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())
        
class Controller:
    
    def __init__(self):
        print("> starting controller...")
        
        # define the menus and window
        self.intro_menu = IntroMenu()
        self.alcohol_menu = AlcoholMenu()
        self.select_menu = SelectMenu()
        self.main_window = StyledStackedWidget()
        
        # add the menus to the window
        self.main_window.addWidget(self.intro_menu)
        self.main_window.addWidget(self.alcohol_menu)
        self.main_window.addWidget(self.select_menu)
        
        self.alcohol_menu.drink_clicked.connect(self.goto_select)
        self.alcohol_menu.stop_clicked.connect(self.goto_intro)
        self.select_menu.stop_clicked.connect(self.goto_intro)
        self.intro_menu.start_clicked.connect(self.goto_alcohol)
        
        print("> controller started")
        print("> enter intro menu")
        self.main_window.setCurrentWidget(self.intro_menu)
        self.main_window.show()
        
    def goto_alcohol(self):
        print("> enter alcohol menu")
        self.main_window.setCurrentWidget(self.alcohol_menu)
        
    def goto_select(self, alcohol):   # TODO: add default value = False?
        print("alcohol: " + str(alcohol))
        print("> enter select menu")
        self.alcohol = alcohol
        self.main_window.setCurrentWidget(self.select_menu)
        
    def goto_intro(self):
        print("EMERGENCY STOP")
        print("> enter intro menu")
        self.main_window.setCurrentWidget(self.intro_menu)

def main(args):
    app = QApplication(args)
    app.setStyle(QStyleFactory.create("Fusion"))

    # set up the slots
    #window1.changeForm.connect(mainWindow.setCurrentIndex)

    # set window to be displayed
    #mainWindow.setCurrentIndex(1)

    #mainWindow.show()
    
    controller = Controller()
    
    sys.exit(app.exec_())
    # TODO: add raspi shutdown function? or rather seperate script watching a GPIO-pin?
  
if __name__== "__main__":
    main( sys.argv )