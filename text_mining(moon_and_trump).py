import numpy as np
import pandas as pd

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

from PyQt5 import QtGui
from PyQt5.QtWidgets import *

import sys

from PIL import Image

from wordCloud.WC import Ui_MainWindow

from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from collections import Counter
from konlpy.tag import Hannanum

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas




class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.lines = ""  # 연설문
        self.nowlang = self.lang.currentText()
        self.eg_wordlist = []
        self.kr_wordlist = []

        self.mask = None
        self.canvas = None

        self.textbutton.clicked.connect(self.choseText)
        self.imgbutton.clicked.connect(self.choseImage)
        self.langbutton.clicked.connect(self.choselang)

    def clearAll(self):
        self.lines = ""
        self.plainTextEdit.clear()
        for i in reversed(range(self.verticalLayout.count())):
            self.verticalLayout.itemAt(i).widget().setParent(None) # layout비우는 방법
        for i in reversed(range(self.verticalLayout_2.count())):
            self.verticalLayout_2.itemAt(i).widget().setParent(None)

    def choselang(self):
        self.nowlang = self.lang.currentText()

    def choseImage(self):
        for i in reversed(range(self.verticalLayout_2.count())):
            self.verticalLayout_2.itemAt(i).widget().setParent(None)

        fileName, _ = QFileDialog.getOpenFileName(self, '불러올 img file을 선택하세요.', '', 'img Files(*.png)')
        if fileName:
            self.mask = np.array(Image.open(fileName))

            if self.nowlang == "영어":
                self.makeImgWordCloud(self.eg_wordlist)
            else:
                self.makeImgWordCloud(self.kr_wordlist)

            self.label_2.setPixmap(QtGui.QPixmap(fileName).scaled(400, 300))

    def choseText(self):
        self.clearAll()
        fileName, _ = QFileDialog.getOpenFileName(self, '불러올 txt file을 선택하세요.', '', 'txt Files(*.txt)')

        self.label.setText(fileName.split("/")[-1].split(".")[0] + " WordCloud")
        if fileName:
            f = open(fileName, "r", encoding="cp949")


            if self.nowlang == "영어":
                self.lines = f.readlines()[0]
                f.close()
                self.makeEgWordList()
            else:
                self.lines = f.readlines()
                f.close()
                self.makeKrWordList()

    def makeEgWordList(self):
        tokenizer = RegexpTokenizer("[\w]+")  # word 단위로 구분하라
        stop_words = stopwords.words("english")  # 단어는 자주 등장하지만 실제 의미 분석에는 의미 없는단어

        words = self.lines.lower()
        tokens = tokenizer.tokenize(words)
        stopped_tokens = [i for i in list(tokens) if not i in stop_words]
        self.eg_wordlist = [i for i in stopped_tokens if len(i) > 1]
        self.makeTop20Word(self.eg_wordlist)
        self.makeWordCloud(self.eg_wordlist)

    def flatten(self, l):
        flatList = []
        for elem in l:
            if type(elem) == list:
                for e in elem:
                    flatList.append(e)
            else:
                flatList.append(elem)
        return flatList

    def makeKrWordList(self):

        hannanum = Hannanum()
        temp = []
        for i in range(len(self.lines)):
            temp.append(hannanum.nouns(self.lines[i]))

        word_list = self.flatten(temp)

        self.kr_wordlist = pd.Series([x for x in word_list if len(x) > 1])
        self.makeTop20Word(self.kr_wordlist)
        self.makeWordCloud(self.kr_wordlist)

    def makeTop20Word(self, wordlist):
        keys = pd.Series(wordlist).value_counts().head(20).keys()
        values = pd.Series(wordlist).value_counts().head(20).values

        for i in range(len(keys)):
            self.plainTextEdit.appendPlainText("{} : {}개".format(keys[i], values[i]))

    def makeWordCloud(self, wordlist):

        font_path = '/Library/Fonts/AppleGothic.ttf'

        wordcloud = WordCloud(font_path=font_path, width=800, height=800, background_color="white")

        count = Counter(wordlist)
        wordcloud = wordcloud.generate_from_frequencies(count)

        def __array__(self):
            return self.to_array()

        def to_array(self):
            return np.array(self.to_image())

        array = wordcloud.to_array()

        fig = plt.figure()
        plt.imshow(array, interpolation="bilinear")
        self.canvas = FigureCanvas(fig)
        self.canvas.draw()
        self.verticalLayout.addWidget(self.canvas)
        self.canvas.show()

    def makeImgWordCloud(self, wordlist):
        font_path = '/Library/Fonts/AppleGothic.ttf'

        count = Counter(wordlist)

        wc = WordCloud(font_path=font_path, mask=self.mask, background_color="white")

        wc = wc.generate_from_frequencies(count)

        image_color = ImageColorGenerator(self.mask)

        fig = plt.figure(figsize=(8, 8))
        plt.imshow(wc.recolor(color_func=image_color), interpolation="bilinear")
        plt.axis("off")
        self.canvas = FigureCanvas(fig)
        self.canvas.draw()
        self.verticalLayout_2.addWidget(self.canvas)
        self.canvas.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    you_viewer_main = Main()
    you_viewer_main.show()
    app.exec_()
