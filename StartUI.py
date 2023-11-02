# -*- coding: utf-8 -*-
# Created by: Ruffy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

import LandlordModel
import main_start


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Made by Ruffy 幻影加入QQ群: 725673735")
        self.setGeometry(100, 100, 520, 400)

        self.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")

        # 按钮名称 位置长宽，链接的函数  -- 单局运行
        recognize_button = QPushButton("单局模式", self)
        recognize_button.setGeometry(100, 80, 100, 40)
        recognize_button.clicked.connect(main_start.recognize)

        # 截图
        recognize_button = QPushButton("截图", self)
        recognize_button.setGeometry(0, 80, 100, 40)
        recognize_button.clicked.connect(main_start.click_test)

        # 关闭广告测试
        recognize_button = QPushButton("比赛模式", self)
        recognize_button.setGeometry(0, 120, 100, 40)
        recognize_button.clicked.connect(main_start.match_mode)

        # 模型评分测试
        recognize_button = QPushButton("模型评分测试", self)
        recognize_button.setGeometry(100, 120, 100, 40)
        recognize_button.clicked.connect(main_start.ModelTest)

        # 连续运行测试
        recognize_button = QPushButton("多局模式", self)
        recognize_button.setGeometry(200, 80, 100, 40)
        recognize_button.clicked.connect(main_start.run_continue)

        # 提牌测试
        recognize_button = QPushButton("提牌测试", self)
        recognize_button.setGeometry(200, 120, 100, 40)
        recognize_button.clicked.connect(main_start.up_card_test)

        # 打赏通道
        recognize_button = QPushButton("支持作者QwQ", self)
        recognize_button.setGeometry(0, 160, 100, 40)
        recognize_button.clicked.connect(main_start.super_developer)


if __name__ == "__main__":
    LandlordModel.init_model("baselines/douzero_WP/landlord.ckpt"
                             "")
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
