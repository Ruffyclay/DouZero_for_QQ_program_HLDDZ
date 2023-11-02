# -*- coding: utf-8 -*-
# Created by: Ruffy
import time

import cv2
import numpy as np
import pyautogui
import win32api
import win32con
import win32gui

import screen_tools
import Aconfig_file


# 统计字符出现的次数
def count_characters(text):
    char_count = {}
    for char in text:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1
    return char_count


# 拿来计算牌的位置的
def find_leftmost_position(char, string):
    for i, c in enumerate(string):
        if c == char:
            return i
    return -1


# 无法对窗口发送点击事件....原因不明
def left_click_in_window(handle, x, y, delay=0.1):
    print(handle, x, y)
    lParam = win32api.MAKELONG(x, y)
    win32gui.PostMessage(handle, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lParam)


# 使用Pyautogui进行模糊定位点击按钮
def click_image_in_window(template_image, window_class='', window_title='', confidence=0.8, mode='click'):
    # 查找窗口句柄
    if window_title == '' or window_class == '':
        window_title = Aconfig_file.window_title
        window_class = Aconfig_file.window_class
    handle = win32gui.FindWindow(window_class, window_title)
    if handle == 0:
        print(f"未找到窗口：{window_title}")
        return None
    # 如果找到了就进行进一步的分析和查找
    left, top, _, _ = win32gui.GetWindowRect(handle)
    screenshot, _ = screen_tools.take_screenshot(window_title, window_class)
    screenshot = np.array(screenshot)
    template_cv = cv2.cvtColor(np.array(template_image), cv2.COLOR_RGB2BGR)
    result = pyautogui.locate(needleImage=template_cv, haystackImage=screenshot, confidence=confidence)
    if result is not None and mode == 'click':
        click_x = left + result[0]
        click_y = top + result[1] - result[3] // 2
        # print(click_x, click_y)
        original_mouse_x, original_mouse_y = pyautogui.position()
        pyautogui.click(click_x, click_y)
        # 点击完后将鼠标送回到原处
        pyautogui.moveTo(original_mouse_x, original_mouse_y)
    # 返回坐标
    elif result is not None and mode == 'check':
        click_x = left + result[0]
        click_y = top + result[1] - result[3] // 2
        # print(click_x, click_y)
        return click_x, click_y  # 返回x, y作参考
    return None


# 普通的xy点击，主要点击指定程序内部
def click_in_window(x, y):
    img, pos = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    original_mouse_x, original_mouse_y = pyautogui.position()
    if x != 0 and y != 0:
        pyautogui.click(x + pos[0], y + pos[1])
    pyautogui.moveTo(original_mouse_x, original_mouse_y)


# 只能用在排序好的情况下，从大到小的顺序或从小到大，乱的手牌可能出现bug，需要重新调整
def select_card(out_card_str='pass', hand_card='', temp_dic=''):
    if temp_dic == '' and hand_card == '':
        print(f'请传入手牌参考图列表或传入手牌!')
        return ''
    if hand_card == '':
        img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        img = np.array(img.crop(Aconfig_file.my_card_area))
        hand_card = screen_tools.check_img(img, temp_dic)
    flag_normal = True  # 过程检测标志符
    card_num_list = []
    temp_hand_cards = hand_card
    last_card_chr = ''  # 记录最后一次出现的手牌
    max_num = 0  # 用于计算卡牌定位的偏移，防止出现多次选择同一张卡牌
    for out_card in out_card_str:
        if out_card in hand_card:
            first_pos = find_leftmost_position(out_card, hand_card)
            # 如果现在出的牌和之前的牌相同则编号+=1
            # print(last_card_chr)
            if last_card_chr == out_card:
                max_num += 1
            else:
                max_num = 0
            if first_pos != -1:  # 如果找到了则删除这一个字符
                last_card_chr = out_card
                card_num_list.append(first_pos + max_num)
        else:
            print('错误，要出的牌不在手牌中!')
            flag_normal = False
            break
    if flag_normal:
        for out_card in out_card_str:
            temp_hand_cards = temp_hand_cards.replace(out_card, '', 1)
        hand_card = temp_hand_cards
    # print(f'出牌偏移位置列表: {card_num_list}')
    # print(f'剩余手牌: {hand_card}')
    return card_num_list, hand_card


# 输入卡牌的左边边缘，和卡牌的模板，手牌的长度，要出的牌的字符串
# 第一张牌的位置 + 点击偏移位置 + 张数 x 牌与牌之间的间隔 = 要出牌的位置
def select_card_act(first_card_check_templ, hand_card_str='', out_card_str='', ext_pix=10):
    original_mouse_x, original_mouse_y = pyautogui.position()
    delay = 0.14
    out_card_str_dic = count_characters(out_card_str)
    # 获取程序的截图和左上角位置
    screen_short, pos = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    screen_short = np.array(screen_short)

    # 加载手牌资料 进行出牌时的判断
    my_card_ord = Aconfig_file.generate_poker_list()
    card_templ_img = Aconfig_file.load_img(Aconfig_file.my_card_path, my_card_ord)

    if hand_card_str == '':
        my_card_img, pos = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        my_card_img = np.array(my_card_img.crop(Aconfig_file.my_card_area))
        hand_card_str = screen_tools.check_img(my_card_img, card_templ_img)
    # print(hand_card_str)  # 返回手牌的内容
    # 找出第一张牌的位置多验证几次，防止到自己的回合刚好被遮住
    left_x = 0
    for i in range(3):
        base_x, base_y = screen_tools.find_template_in_region(first_card_check_templ, screen_short,
                                                              Aconfig_file.card_select_area, 0.6)
        if left_x == 0:
            left_x = base_x
        if base_x < left_x:
            left_x = base_x
        time.sleep(delay)
    base_x = left_x
    x1, y1, x2, y2 = Aconfig_file.card_select_area
    base_y = (((y2 - y1) / 2) + y1) / 1.1 + Aconfig_file.card_select_fix_pix
    # pyautogui.click(base_x + pos[0], base_y + pos[1])
    # time.sleep(delay)
    # 出牌顺序
    out_card_list, _ = select_card(out_card_str, hand_card_str, card_templ_img)
    flag_pass = False  # 提牌部分是否通过?
    areod_up_card = ''
    # 循环多次点击手牌
    for all_pos in range(10):
        if flag_pass:
            break
        for i in out_card_list:
            # 先不急着点击手牌，先检查有没有多出来的手牌
            temp_out_img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
            temp_out_img = np.array(temp_out_img.crop(Aconfig_file.my_out_card_area))
            temp_out = screen_tools.check_img(temp_out_img, card_templ_img)
            areod_up_card = temp_out
            x = base_x + ext_pix + (i * Aconfig_file.card_pixels_x) + pos[0]
            if len(hand_card_str) > 18:
                x = base_x + ext_pix + (i * Aconfig_file.card_pixels_x) + pos[0] - i * Aconfig_file.select_card_fix
            # time.sleep(1)
            y = base_y + pos[1]
            # pyautogui.moveTo(x, y)
            temp_out_dic = count_characters(temp_out)
            try:
                if out_card_str_dic[hand_card_str[i]] > temp_out_dic[hand_card_str[i]]:
                    # print(f'ffff: {hand_card_str[i]}')
                    pyautogui.click(x, y)
            except:
                pyautogui.click(x, y)
            time.sleep(delay)
            if temp_out != '':  # 如果有提起来的手牌
                temp_out_pass = temp_out  # 出牌复变量 已出牌 - 要出牌 = 多余牌
                for card_one in out_card_str:
                    temp_out_pass = temp_out_pass.replace(card_one, '', 1)  # 从已经出的牌中去掉要出的牌的内容剩余部分就是多余的牌
                # print(f'要出的牌: {out_card_str},多出的手牌: {temp_out_pass},已出的牌:{temp_out}')
                if temp_out == out_card_str[::-1]:  # AI传输进来要点击的牌顺序要颠倒 如果要出的牌和出牌完全相等则通过
                    flag_pass = True
                    break
                if temp_out_pass == '' and temp_out == out_card_str:  # 如果没有多余的手牌
                    flag_pass = True
                else:  # 存在提起不必要牌的情况
                    temp_out_list, _ = select_card(temp_out_pass, hand_card_str, card_templ_img)
                    # temp_out_pass_len = len(temp_out_pass)  # 计算提起的不要牌的长度
                    # print(f'多出了{temp_out_pass_len}张牌')
                    # 将不要的牌一个个的放置，然后等待
                    for num in temp_out_list:
                        x = base_x + ext_pix + num * Aconfig_file.card_pixels_x + pos[0]
                        if len(hand_card_str) > 18:
                            x = base_x + ext_pix + (num * Aconfig_file.card_pixels_x) + pos[
                                0] - num * Aconfig_file.select_card_fix
                        y = base_y + pos[1]
                        pyautogui.click(x, y)
                        # 验证是否正确的取消放牌
                        for yanzheng in range(1, 5):
                            # 重新截图 查找不必要牌在原手牌中的牌位偏移  列表
                            time.sleep(delay)
                            temp_out_img, _ = screen_tools.take_screenshot(Aconfig_file.window_title,
                                                                           Aconfig_file.window_class)
                            temp_out_img = np.array(temp_out_img.crop(Aconfig_file.my_out_card_area))
                            temp_out = screen_tools.check_img(temp_out_img, card_templ_img)
                            temp_out_pass_two = temp_out  # 出牌复变量 已出牌 - 要出牌 = 多余牌
                            for card_one in out_card_str:
                                temp_out_pass_two = temp_out_pass_two.replace(card_one, '',
                                                                              1)  # 从已经出的牌中去掉要出的牌的内容剩余部分就是多余的牌
                            try:
                                # print(hand_card_str[yanzheng + num] in list(temp_out_pass_two))
                                if len(temp_out_pass_two) >= len(temp_out_pass) and hand_card_str[
                                    yanzheng + num] in list(temp_out_pass_two):
                                    pyautogui.click(x, y)
                                    time.sleep(delay)
                                    x = base_x + ext_pix + (num + yanzheng) * Aconfig_file.card_pixels_x + pos[0]
                                    if len(hand_card_str) > 18:
                                        x = base_x + ext_pix + ((num + yanzheng) * Aconfig_file.card_pixels_x) + pos[
                                            0] - num * Aconfig_file.select_card_fix
                                    y = base_y + pos[1]
                                    pyautogui.click(x, y)
                                else:
                                    break
                            except:
                                pass
    pyautogui.moveTo(original_mouse_x, original_mouse_y)


# 专门点击游戏中广告按钮的 使用OpenCV 精准定位关闭按钮
def close_AD(AD_templ=None, break_img=None):
    if AD_templ is None:
        AD_name_list = Aconfig_file.get_all_filename(Aconfig_file.AD_close_path)
        AD_templ = Aconfig_file.load_img(Aconfig_file.AD_close_path, AD_name_list)
    time.sleep(0.4)
    screen_img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    screen_img = np.array(screen_img)
    for i in AD_templ:
        img = np.array(AD_templ[i])
        height, width, channels = screen_img.shape
        if break_img is not None:
            break_imgserch = np.array(break_img)
            x, y = screen_tools.find_template_in_region(break_imgserch, screen_img, (0, 0, width, height))
            if x != 0 and y != 0:
                break
        x, y = screen_tools.find_template_in_region(img, screen_img, (0, 0, width, height))
        click_in_window(x, y)
        # click_image_in_window(AD_templ[i])


def click_img_by_opencv(btn_templ, btn_name_list, num, threshold=0.75, click=True):
    screen_img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    screen_img = np.array(screen_img)
    img = np.array(btn_templ[btn_name_list[num]])
    height, width, _ = screen_img.shape
    x, y = screen_tools.find_template_in_region(img, screen_img, (0, 0, width, height), threshold)
    if click:
        click_in_window(x, y)
    if x != 0 and y != 0:
        return True
    else:
        return False
    # click_image_in_window(btn_templ[num])
