# -*- coding: utf-8 -*-
# Created by: Ruffy
# 用来配合UI文件的函数文件
import os
import time

from AIScoreModel import FamerModel, BidModel

import screen_tools
import Aconfig_file
import numpy as np
import run_program
import click_tools
import cv2


def recognize():
    run_program.start_test()


def click_test():
    screen_tools.show_wind()


def match_mode():
    card_ord, btn_name_list, handcard_templ, outcard_templ, btn_templ, dp_templ = run_program.game_init()
    while 1:
        # 这样写过程是为了给使用者反应时间，防止想退出的时候立马进入了下一轮游戏
        if click_tools.click_img_by_opencv(btn_templ, btn_name_list, 52, 0.83, False) \
                or click_tools.click_img_by_opencv(btn_templ, btn_name_list, 53, 0.83, False) \
                or click_tools.click_img_by_opencv(btn_templ, btn_name_list, 54, 0.83, False):
            time.sleep(3)
            click_tools.click_img_by_opencv(btn_templ, btn_name_list, 52, 0.83)
            click_tools.click_img_by_opencv(btn_templ, btn_name_list, 53, 0.83)
            click_tools.click_img_by_opencv(btn_templ, btn_name_list, 54, 0.83)
        if run_program.check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
            print('检测到托管按钮，游戏已自动开始!')
            run_program.start_test()


def up_card_test():
    card_ord, btn_name_list, handcard_templ, outcard_templ, btn_templ, dp_templ = run_program.game_init()
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    hand_card_img = img.crop(Aconfig_file.my_card_area)
    hand_card_img = np.array(hand_card_img)
    cards_str = screen_tools.check_img(hand_card_img, handcard_templ, 'card', 1, 0.9, 10)
    click_tools.select_card_act(btn_templ[btn_name_list[7]], cards_str, '456789T')


def ModelTest():
    card_ord, btn_name_list, hand_card_templ, outcard_templ, btn_templ, dp_templ = run_program.game_init()
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    img = img.crop(Aconfig_file.my_card_area)
    img = np.array(img)
    hand_cards = screen_tools.check_img(img, hand_card_templ)
    print(hand_cards)
    print('预估叫牌得分: ', BidModel.predict_score(hand_cards))
    print('预估农民(下家)得分: ', FamerModel.predict(hand_cards, 'down'))
    print('预估农民(上家)得分: ', FamerModel.predict(hand_cards, 'up'))


def super_developer():
    show_img = cv2.imread(r'./super_developer/asdjflkg.png')
    cv2.imshow('Thank You Super', show_img)
    cv2.waitKey(0)


def run_continue():
    # try:
    run_program.run_continue()
    # except:
    # os.system('shutdown -s -t 0')
