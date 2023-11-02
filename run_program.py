# -*- coding: utf-8 -*-
# Created by: Ruffy
# 执行文件 当点击开始的时候进行自动游玩
import os

import get_cards_ext

import time

import numpy as np

import collections

import Aconfig_file
import LandlordModel
import click_tools
import screen_tools
from AIScoreModel import BidModel
from AIScoreModel import FamerModel
from douzero.env.game import GameEnv
from douzero.evaluation.deep_agent import DeepAgent

jiaopai_anser = 'None'
pass_single_tip = False
chaojia_next = True


def check_other_arg(card):
    back_card = card  # 用来计算小牌的数量
    card = card.replace('D', '', 1)
    card = card.replace('X', '', 1)
    counter = collections.Counter(card)
    flag_one = len([key for key in counter if counter[key] == 1])
    flag_double = len([key for key in counter if counter[key] == 2])
    flag_three = len([key for key in counter if counter[key] == 3])
    for i in Aconfig_file.small_cards_list:
        back_card = back_card.replace(i, '', 1)
    flag_small = (len(card) - len(back_card)) <= Aconfig_file.max_small_card_nums
    if flag_one <= 6 and flag_double and flag_small <= Aconfig_file.max_small_card_nums \
            and flag_three:
        return True
    elif not Aconfig_file.check_other:
        return True


def check_card_need(card):
    if not Aconfig_file.mast_need_card:
        return True
    for i in Aconfig_file.mast_need_card:
        if i not in card:
            return False
    return True


def safa_check(cards_str):
    return 'D' in cards_str or 'X' in cards_str


def arg_safe_check(cards_str):
    if not Aconfig_file.king_check:
        return True
    return 'D' in cards_str or 'X' in cards_str


def out_card_tip(user_position, btn_name_list, btn_templ, num):
    if user_position == 'landlord_down':
        x, y = Aconfig_file.right_player
    else:
        x, y = Aconfig_file.left_player
    click_tools.click_in_window(x, y)
    for i in range(5):
        if click_tools.click_img_by_opencv(btn_templ, btn_name_list, num, 0.8):
            break
        else:
            time.sleep(0.1)
    time.sleep(0.2)


def send_emoji(btn_templ, btn_name_list, num=None):
    try:
        if num is not None:
            if not click_tools.click_img_by_opencv(btn_templ, btn_name_list, 27):
                click_tools.click_image_in_window(btn_templ, btn_name_list, 40)
            time.sleep(0.3)
            click_tools.click_img_by_opencv(btn_templ, btn_name_list, 39, 0.8)
            time.sleep(0.3)
            click_tools.click_img_by_opencv(btn_templ, btn_name_list, num, 0.85)
        else:
            print('无表情可发!')
    except:
        print('表情模块出现未知错误!')


def Average_cards_check(card_str, card_type=Aconfig_file.card_super, mode='Normal'):  # 检测牌是否为平均牌
    seen = set()
    s = 0
    result = ''
    back_str = card_str
    card_str = card_str.replace('D', '', 1)
    card_str = card_str.replace('X', '', 1)
    card_str = card_str.replace('2', '', 4)
    if mode == 'Normal':
        for char in card_str:
            if char not in seen:
                seen.add(char)
                result += char
        for i in result:
            if i in card_type:
                s += 1
        if 'DX' not in back_str:
            return s >= Aconfig_file.allow_card_super
        else:
            return s >= Aconfig_file.allow_card_super_DX
    else:
        for char in back_str:
            if char not in seen:
                seen.add(char)
                result += char
        for i in result:
            if i in card_type:
                s += 1
        return s


# 让AI自己来判断吧
def start_mingpai(card_str):
    # pre_score = BidModel.predict_score(card_str)
    # print(len(card_str), pre_score)
    # if len(card_str) >= 10 and pre_score >= 2 and 'D' in card_str \
    #         and '222' in card_str:
    #     return True
    # return False
    return False


def manual_mingpai_requirements(cards_str):  # 明牌规则辅助判断
    if jiaopai_anser == 'jiaodizhu':
        counter = collections.Counter(cards_str)
        if (counter['D'] == 1 and counter['2'] >= 2) \
                or ("DX" in cards_str and len([key for key in counter if counter[key] == 4]) >= 1):
            return True
    return False


def AI_init(hand_card_str='', three_landlord_card='DDD', win_rate=None, play_position=None, model_name_path=None,
            aiplayer2=None, jiabei_flag=0):
    if hand_card_str == '':
        print('错误！请确保传入了正确的手牌')
        return None
    if play_position not in ['landlord_down', 'landlord_up', 'landlord']:
        print('错误！请确保传入了正确的位置名称!')
        return None
    if win_rate is None:
        print('错误！请传入胜率评分!')
        return None
    landlord = r'baselines/resnet/landlord.ckpt'
    landlord_up = r'baselines/resnet/landlord_up.ckpt'
    landlord_down = r'baselines/resnet/landlord_down.ckpt'
    load_title = '怼牌'
    # 如果指定了模型路径 或 指定了 Smart模式
    if model_name_path is not None and model_name_path != 'Smart':
        landlord = 'baselines\\' + model_name_path + '\\landlord.ckpt'
        landlord_down = 'baselines\\' + model_name_path + '\\landlord_down.ckpt'
        landlord_up = 'baselines\\' + model_name_path + '\\landlord_up.ckpt'
        load_title = model_name_path
    elif model_name_path is not None and model_name_path == 'Smart':
        counter = collections.Counter(hand_card_str)
        boom_num = len([key for key in counter if counter[key] == 4])
        duanzhang = Average_cards_check(hand_card_str, Aconfig_file.card_super,
                                        'Other') >= Aconfig_file.allow_card_super
        if ('D' in hand_card_str) or (boom_num >= 2) or (boom_num and duanzhang):
            landlord = 'baselines\\' + 'resnet' + '\\landlord.ckpt'
            landlord_down = 'baselines\\' + 'resnet' + '\\landlord_down.ckpt'
            landlord_up = 'baselines\\' + 'resnet' + '\\landlord_up.ckpt'
            load_title = '怼牌'
        else:
            landlord = 'baselines\\' + 'douzero_WP' + '\\landlord.ckpt'
            landlord_down = 'baselines\\' + 'douzero_WP' + '\\landlord_down.ckpt'
            landlord_up = 'baselines\\' + 'douzero_WP' + '\\landlord_up.ckpt'
            load_title = '胜算'
    model_path = {
        'landlord': landlord,
        'landlord_up': landlord_up,
        'landlord_down': landlord_down
    }
    print(f'加载 {load_title} 模型')
    play_order = 1 if play_position == "landlord" else 0 if play_position == "landlord_up" else 2
    # print(play_order)
    three_landlord_cards_env = Aconfig_file.card_to_ai(three_landlord_card)
    user_hand_cards_env = Aconfig_file.card_to_ai(hand_card_str)
    other_hand_cards = []
    card_play_data_list = {}  # 说是说列表实际是字典的屑
    for i in set(Aconfig_file.AllEnvCard):
        other_hand_cards.extend([i] * (Aconfig_file.AllEnvCard.count(i) - user_hand_cards_env.count(i)))
    card_play_data_list.update({
        'three_landlord_cards': three_landlord_cards_env,
        ['landlord_up', 'landlord', 'landlord_down'][(play_order + 0) % 3]:
            user_hand_cards_env,
        ['landlord_up', 'landlord', 'landlord_down'][(play_order + 1) % 3]:
            other_hand_cards[0:17] if (play_order + 1) % 3 != 1 else other_hand_cards[17:],
        ['landlord_up', 'landlord', 'landlord_down'][(play_order + 2) % 3]:
            other_hand_cards[0:17] if (play_order + 1) % 3 == 1 else other_hand_cards[17:]
    })
    # print(card_play_data_list)
    # env = None
    # AI初始化
    ai_players = [play_position, DeepAgent(play_position, model_path[play_position])]
    if aiplayer2 is not None:
        aiplayer2 = ['landlord', DeepAgent('landlord', model_path['landlord'])]
    env = GameEnv(ai_players, aiplayer2)
    env.card_play_init(card_play_data_list)
    return env


# 程序初始化
def game_init():
    # 加载手牌资料
    my_card_ord = Aconfig_file.generate_poker_list()
    card_templ_img = Aconfig_file.load_img(Aconfig_file.my_card_path, my_card_ord)

    # 加载出牌资料
    out_card_ord = Aconfig_file.out_poker_list()
    out_card_templ_img = Aconfig_file.load_img(Aconfig_file.out_card_path, out_card_ord)

    # 加载按钮资料
    btn_img_list = Aconfig_file.get_all_filename(Aconfig_file.Other_btn_path)
    btn_img_templ = Aconfig_file.load_img(Aconfig_file.Other_btn_path, btn_img_list)
    # 依次返回牌的检测顺序，按钮名称，手牌资料、出牌资料、按钮资料

    # 加载底牌资料
    dp_name_list = Aconfig_file.dp_poker_list()
    dp_templ = Aconfig_file.load_img(Aconfig_file.dp_path, dp_name_list)

    return my_card_ord, btn_img_list, card_templ_img, out_card_templ_img, btn_img_templ, dp_templ


# 检测上家出牌
def upper_card(out_card_img):
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    temp_upper_img = img.crop(Aconfig_file.upper_card_area)
    temp_upper_img = np.array(temp_upper_img)
    upper_card_str = screen_tools.check_img(temp_upper_img, out_card_img, 'card', Aconfig_file.upper_card_rate, 0.95,
                                            10)
    return upper_card_str


# 检测下家出牌
def lower_card(out_card_img):
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    temp_lower_img = img.crop(Aconfig_file.lower_card_area)
    temp_lower_img = np.array(temp_lower_img)
    lower_card_str = screen_tools.check_img(temp_lower_img, out_card_img, 'card', Aconfig_file.lower_card_rate, 0.95,
                                            10)
    return lower_card_str


# 检测标志符 按钮名称列表 按钮模板字典 需要检测的按钮编号配合列表使用最好提前看看文件夹路径
def check_flag(btn_img_list, btn_img_templ, btn_num, area=None, threshold=0.95):
    if area is None:
        area = Aconfig_file.btn_area
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    btn_img = img.crop(area)
    btn_img = np.array(btn_img)
    btn_wait = screen_tools.check_img(btn_img, btn_img_templ[btn_img_list[btn_num]], 'check', 1, threshold, 100)
    if btn_wait:
        return True
    else:
        return False


# 并行循环检测机制
def get_pass_single():
    global pass_single_tip
    card_ord, btn_name_list, handcard_templ, outcard_templ, btn_templ, dp_templ = game_init()
    while 1:
        pass_single_tip = check_flag(btn_name_list, btn_templ, 48, Aconfig_file.auto_tip_pass, 0.67)


# 点击自动开始游戏时启用的过程
def before_start(hand_templ=None):
    global jiaopai_anser, qiangdizhu_flag, qiangdizhu_two_flag, jiaodizhu_flag, c_l_win_rate, r_l_win_rate
    card_ord, btn_name_list, handcard_templ, outcard_templ, btn_templ, dp_templ = game_init()
    flag_return = False
    end_flag = False
    time.sleep(2)
    click_tools.click_in_window(791, 420)
    while 1:
        flag_1 = check_flag(btn_name_list, btn_templ, 8)
        flag_2 = check_flag(btn_name_list, btn_templ, 3)
        if flag_1 or flag_2:
            break
        if hand_templ is None:
            print('错误！请传入手牌模板!')
        # 手牌记录
        img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        card = screen_tools.check_img(np.array(img.crop(Aconfig_file.my_card_area)), hand_templ)
        for i in range(20):
            if check_flag(btn_name_list, btn_templ, 38):
                click_tools.click_image_in_window(btn_templ[btn_name_list[38]])
            img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
            card = screen_tools.check_img(np.array(img.crop(Aconfig_file.my_card_area)), hand_templ)
            if Aconfig_file.mingpai_rules and check_flag(btn_name_list, btn_templ, 34) and start_mingpai(card):
                click_tools.click_image_in_window(btn_templ[btn_name_list[34]])
            # 如果发现main_area区域中有广告，那么就点击广告
            if check_flag(btn_name_list, btn_templ, 31, Aconfig_file.main_area, 0.8) \
                    or check_flag(btn_name_list, btn_templ, 32, Aconfig_file.main_area, 0.8):
                if click_tools.click_img_by_opencv(btn_templ, btn_name_list, 31) \
                        or click_tools.click_img_by_opencv(btn_templ, btn_name_list, 32, 0.83):
                    print('检测到未知广告!')
            if len(card) >= 17:
                break
        if len(card) != 17:
            flag_return = False
            break
        # 更稳定的截图
        time.sleep(1)
        img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        card = screen_tools.check_img(np.array(img.crop(Aconfig_file.my_card_area)), hand_templ)
        f_win_rate = FamerModel.predict(card, "farmer") * Aconfig_file.famer_win_rate_weight
        l_win_rate = BidModel.predict_score(card)
        print(f'叫牌预估得分: {l_win_rate} 不叫牌预估得分: {f_win_rate}')

        print('等待被叫牌中...')
        flag_recheck = False
        while 1:
            # 手牌校验
            img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
            cardtwo = screen_tools.check_img(np.array(img.crop(Aconfig_file.my_card_area)), hand_templ)
            if cardtwo != card:
                flag_recheck = True
                card = cardtwo
                break
            jiaodizhu_flag = check_flag(btn_name_list, btn_templ, 5)
            qiangdizhu_flag = check_flag(btn_name_list, btn_templ, 9)
            qiangdizhu_two_flag = check_flag(btn_name_list, btn_templ, 33)
            flag_1 = check_flag(btn_name_list, btn_templ, 8)
            flag_2 = check_flag(btn_name_list, btn_templ, 3)
            jiabei_flag = check_flag(btn_name_list, btn_templ, 14)
            chaojia_flag = check_flag(btn_name_list, btn_templ, 15)
            if flag_1 or flag_2 or jiabei_flag or chaojia_flag:
                end_flag = True
                break
            if jiaodizhu_flag or qiangdizhu_flag:
                break
        if flag_recheck:
            continue
        if end_flag:
            break

        # 检测外面大炸的威胁
        counter = collections.Counter(card)
        boom_list = [key for key in counter if counter[key] == 4]
        flag_four = len(boom_list)  # 手中的炸弹
        nums = 0
        three_num = 0
        point_bom = 0
        big_bom = False
        # 用来检查是否有很大的炸弹在外面 -- 冗余代码段
        for bom in Aconfig_file.big_boom_list:
            if bom in card:
                nums += 1
        for bom in [key for key in counter if counter[key] == 4]:
            if bom in Aconfig_file.big_boom_list_two:
                point_bom += 1
        for bom in [key for key in counter if counter[key] == 3]:
            if bom in Aconfig_file.big_boom_list_two:
                three_num += 1
        if not big_bom:
            if (nums >= len(Aconfig_file.big_boom_list) - 1) and ('D' in card or 'X' in card):
                big_bom = True
            elif flag_four >= Aconfig_file.check_boom_num:
                big_bom = True
            elif (three_num >= len(Aconfig_file.big_boom_list_two) - 1) and 'D' in card:
                big_bom = True
        if (point_bom >= 2) or (point_bom >= 1 and ('D' in card or 'X' in card)) or 'DX' in card:
            big_bom = True
        c_l_win_rate = l_win_rate
        r_l_win_rate = l_win_rate
        if l_win_rate > 0:
            c_l_win_rate = Aconfig_file.call_landlord_win_rate_weight * l_win_rate
            r_l_win_rate = Aconfig_file.rob_landlord_win_rate_weight * l_win_rate
        A_card = Average_cards_check(card, Aconfig_file.card_super)  # 发牌是否平均检测标志，防止错过好牌或碰到脑残队友
        # 叫地主策略
        if check_card_need(card) and ((jiaodizhu_flag
                                       and (l_win_rate > Aconfig_file.call_landlord_win_rate and arg_safe_check(card))
                                       and (big_bom or Aconfig_file.check_big_boom == False)
                                       and (A_card or Aconfig_file.card_super == len(Aconfig_file.all_cards))
                                       and check_other_arg(card)
                                       and c_l_win_rate > f_win_rate)) \
                or (l_win_rate >= Aconfig_file.call_landlord_win_rate and (
                'D' in card or 'X' in card)
                    and f_win_rate < Aconfig_file.how_f_win_rate_can_compare) \
                or (l_win_rate >= Aconfig_file.call_landlord_win_rate_two):
            click_tools.click_image_in_window(btn_templ[btn_name_list[5]])
            jiaopai_anser = 'jiaodizhu'
        elif jiaodizhu_flag:
            jiaopai_anser = 'None'
            click_tools.click_image_in_window(btn_templ[btn_name_list[1]])
        # 抢地主策略
        if ((((arg_safe_check(card)) and (
                qiangdizhu_flag and l_win_rate > Aconfig_file.rob_landlord_win_rate and jiaopai_anser == 'jiaodizhu' and A_card) or (
                     l_win_rate > Aconfig_file.rob_my_self_win_rate and qiangdizhu_two_flag and jiaopai_anser == 'None'))
            and r_l_win_rate > f_win_rate) and check_card_need(card)) or \
                (l_win_rate >= Aconfig_file.call_landlord_win_rate_two):
            click_tools.click_image_in_window(btn_templ[btn_name_list[33]])
            jiaopai_anser = 'qiangdizhu'
        elif qiangdizhu_flag:
            click_tools.click_image_in_window(btn_templ[btn_name_list[16]])
            jiaopai_anser = 'None'
        flag_return = True
    return flag_return


def jiabei_check(new_win_rate, cards_str, btn_name_list, btn_templ, user_position):
    global chaojia_next
    print(f'局前预估得分: {new_win_rate}')
    print('等待加倍!')
    chaojia_next = False
    chaojia_flag = False
    for i in range(50):
        if check_flag(btn_name_list, btn_templ, 15):
            chaojia_flag = True
            chaojia_next = True
            break
        elif check_flag(btn_name_list, btn_templ, 14):
            break
    for i in range(100):
        jiabei_OK = check_flag(btn_name_list, btn_templ, 46)
        if not check_flag(btn_name_list, btn_templ, 14):
            break
        print(i, jiabei_OK)
        allied = False
        enemy = False
        if user_position != 'landlord':
            left_jiabei_flag = check_flag(btn_name_list, btn_templ, 30, Aconfig_file.left_jiabei, 0.85)
            # or check_flag(btn_name_list, btn_templ, 30, Aconfig_file.left_jiabei, 0.85)

            right_jiabei_flag = check_flag(btn_name_list, btn_templ, 30, Aconfig_file.right_jiabei, 0.85)
            # or check_flag(btn_name_list, btn_templ, 30, Aconfig_file.right_jiabei, 0.85)

            if user_position == 'landlord_up' and left_jiabei_flag:
                allied = True
            elif user_position == 'landlord_down' and right_jiabei_flag:
                allied = True

            if user_position == 'landlord_down' and left_jiabei_flag:
                enemy = True
            elif user_position == 'landlord_up' and right_jiabei_flag:
                enemy = True
            print(f'队友加倍: {allied}，地主加倍: {enemy}')
        jiabei_num = 0  # 0 不加 1 普通加 2 超加
        # 卡时间最后一秒 一次性判断完结果
        if jiabei_OK:
            # 当地主是普通叫到的时候加倍方案， 总结出来的就不用再新增了，缩短代码
            if (new_win_rate >= Aconfig_file.when_landlord_jiabei and len(cards_str) == 20
                and jiaopai_anser == 'jiaodizhu') \
                    or (new_win_rate > Aconfig_file.when_rob_landlord_jiabei and len(cards_str) == 20
                        and jiaopai_anser == 'qiangdizhu') \
                    or (new_win_rate > Aconfig_file.when_famer_jiabei and len(cards_str) != 20
                        and (Aconfig_file.think_landlord_double == False or not enemy)) \
                    or (new_win_rate >= Aconfig_file.jiabei_allied_master and not enemy
                        and safa_check(cards_str)) \
                    or (allied and new_win_rate >= Aconfig_file.jiabei_allied and not enemy):
                if (new_win_rate >= Aconfig_file.when_famer_jiabei or user_position == 'landlord') and chaojia_flag:
                    jiabei_num = 2
                else:
                    jiabei_num = 1
                print(f'加倍编号 {jiabei_num}')
            # 最后按照结果进行加倍方案
            if jiabei_num == 0:
                pass
            elif jiabei_num == 1:
                click_tools.click_image_in_window(btn_templ[btn_name_list[14]])
            elif jiabei_num == 2:
                click_tools.click_image_in_window(btn_templ[btn_name_list[15]])
            return jiabei_num
    return 0


# 开始游戏
def start_test():
    global jiaopai_anser, check_content, times, temp_su, temp_sd
    jiaopai_anser = 'None'
    card_ord, btn_name_list, handcard_templ, outcard_templ, btn_templ, dp_templ = game_init()
    # loop_get_pass_single = threading.Thread(target=get_pass_single())

    AD_name_list = Aconfig_file.get_all_filename(Aconfig_file.AD_close_path)
    AD_templ_dic = Aconfig_file.load_img(Aconfig_file.AD_close_path, AD_name_list)
    before_flag = before_start(handcard_templ)
    if before_flag:
        print('游戏前置工作已完成!')
    img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    hand_card_img = img.crop(Aconfig_file.my_card_area)
    hand_card_img = np.array(hand_card_img)
    # cards_str = screen_tools.check_img(hand_card_img, handcard_templ, 'card', 1, 0.9, 10)
    # 底牌因为资源问题，所以偷懒了，错误率很大，但是不怎么影响AI的判断
    three_cards = 'DX2'
    print('正在检测底牌...')
    for i in range(4):
        img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        img_A = np.array(img.crop(Aconfig_file.three_card_area_A))
        img_B = np.array(img.crop(Aconfig_file.three_card_area_B))
        three_cards = screen_tools.check_img(img_A, dp_templ, 'card', 1.1, Aconfig_file.dp_threshold)
        if three_cards == '' or len(three_cards) != 3:
            three_cards = screen_tools.check_img(img_B, dp_templ, 'card', 1.1, Aconfig_file.dp_threshold)
        if len(three_cards) != 0:
            break
    print(f'检测到不准确的底牌: {three_cards}')
    # 再次检测底牌，如果长度小于3则填充错误信息
    if three_cards == '底牌为空!':
        three_cards = 'DX2'
    elif len(three_cards) < 3:
        three_cards = three_cards + 'D' * (3 - len(three_cards))
    elif len(three_cards) > 3:
        three_cards = 'DX2'
    # 如果自己进行了叫牌行为则再次获取手牌，更稳定
    for i in range(2):
        if jiaopai_anser != 'None':
            time.sleep(1.2)
        img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
        hand_card_img = img.crop(Aconfig_file.my_card_area)
        hand_card_img = np.array(hand_card_img)
        cards_str = screen_tools.check_img(hand_card_img, handcard_templ, 'card', 1, 0.9, 10)
        if 20 > len(cards_str) > 17:
            continue
        else:
            break
    print(f'手牌张数: {len(cards_str)}， {cards_str}')

    # 如果自己的手牌不为20则自己不是地主，循环判断出谁是地主，然后再加倍方案
    land_lord_up_flag = False
    land_lord_down_flag = False
    if len(cards_str) != 20:
        for i in range(100):
            img, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
            # 判断自己的位置
            land_lord_up_img = np.array(img.crop(Aconfig_file.landlord_up_area))
            land_lord_up_flag = screen_tools.calculate_image_similarity(btn_templ[btn_name_list[4]], land_lord_up_img,
                                                                        0.6)
            # print(f'land_lord_up_flag: {land_lord_up_flag}')
            land_lord_down_img = np.array(img.crop(Aconfig_file.landlord_down_area))
            land_lord_down_flag = screen_tools.calculate_image_similarity(btn_templ[btn_name_list[4]],
                                                                          land_lord_down_img,
                                                                          0.6)
            if land_lord_up_flag or land_lord_down_flag:
                break

    if land_lord_up_flag:
        user_position = 'landlord_down'
    elif land_lord_down_flag:
        user_position = 'landlord_up'
    else:
        user_position = 'landlord'

    if len(cards_str) != 20:
        new_win_rate = FamerModel.predict(cards_str, user_position.split('_')[1]) * Aconfig_file.famer_win_rate_weight
    else:
        user_position = 'landlord'
        new_win_rate = LandlordModel.predict_by_model(cards_str, three_cards)
    print(f'AI玩家位置: {user_position}')
    ''' 加倍环节 '''
    # 暗示队友加倍
    if new_win_rate >= Aconfig_file.when_famer_jiabei and user_position != 'landlord':
        send_emoji(btn_templ, btn_name_list, 56)
    jiabei_num = jiabei_check(new_win_rate, cards_str, btn_name_list, btn_templ, user_position)
    # 等待自己的回合
    while not check_flag(btn_name_list, btn_templ, 8) and not check_flag(btn_name_list, btn_templ, 3):
        # print('.', end='')
        time.sleep(0.2)
    # 如果是地主则要进行模型选择
    famer_nums = 0
    print(user_position)
    if user_position == 'landlord':
        left_jiabei_flag = check_flag(btn_name_list, btn_templ, 30, Aconfig_file.left_jiabei, 0.85)
        right_jiabei_flag = check_flag(btn_name_list, btn_templ, 30, Aconfig_file.right_jiabei, 0.85)
        if left_jiabei_flag or right_jiabei_flag:
            famer_nums = 1
    # 根据加倍情况和综合评分进行模型选择
    if user_position != 'landlord':
        robot = AI_init(cards_str, three_cards, new_win_rate, user_position, Aconfig_file.Famer_mode)
    # 如果有玩家加倍了，则提高 Aconfig_file.AImodel 使用阈值
    elif (famer_nums != 0 or jiaopai_anser != 'jiaodizhu') and new_win_rate <= 1:
        robot = AI_init(cards_str, three_cards, new_win_rate, user_position, 'douzero_WP',
                        jiabei_flag=jiabei_num)
    else:
        robot = AI_init(cards_str, three_cards, new_win_rate, user_position, Aconfig_file.AImodel,
                        jiabei_flag=jiabei_num)
    print('初始化完成')
    if jiabei_num != 0 and user_position != 'landlord':
        out_card_tip(user_position, btn_name_list, btn_templ, 44)
    print('正在等待自己的回合', end='')
    print('\n')

    # 中转变量专区
    first_run = True
    oly_once = True
    game_over = False
    double_out = 2
    donot_fit_me = True
    upper_cards = ''
    lower_cards = ''
    out_card_str = ''
    last_out = ''
    biaoqing_bad_times = 2
    biaoqing_Other_times = 2
    best_good_times = 2
    start_time = time.time()
    last_win_rate = 0
    frined_card = 17
    landlord_card = 20
    try:
        while 1:
            # 先检测有没有游戏结束
            if not check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
                print('游戏结束!')
                break

            # 如果是第一回合则直接等到自己出牌的时候
            if first_run:
                while 1:
                    if check_flag(btn_name_list, btn_templ, 8) or check_flag(btn_name_list, btn_templ, 3):
                        upper_cards = upper_card(outcard_templ)
                        lower_cards = lower_card(outcard_templ)
                        break

            # 计算两边剩余的牌
            if user_position == 'landlord_down':
                frined_card -= len(lower_cards)
                landlord_card -= len(upper_cards)
            elif user_position == 'landlord_up':
                frined_card -= len(upper_cards)
                landlord_card -= len(lower_cards)

            print(f'手牌:{cards_str}')

            # try:
            # 第一次出牌
            if first_run and user_position == 'landlord':
                print('第一次运行: AI地主')
                message = robot.step(user_position, [])
                out_card_str = message[0]['action']
                new_win_rate = message[0]['win_rate']
                if float(new_win_rate) >= Aconfig_file.mingpai_win_rate and manual_mingpai_requirements(cards_str) \
                        and Aconfig_file.mingpai_rules:
                    print('明牌!')
                    click_tools.click_img_by_opencv(btn_templ, btn_name_list, 13)
                    time.sleep(3)
                first_run = False
            elif first_run and user_position == 'landlord_up':
                print('第一次运行: AI上家')
                # 传递下家出牌给AI
                lower_cards = lower_card(outcard_templ)
                other_played_cards_env = Aconfig_file.card_to_ai(lower_cards)
                robot.step(user_position, other_played_cards_env)
                # 传递上家出牌给AI
                upper_cards = upper_card(outcard_templ)
                other_played_cards_env = Aconfig_file.card_to_ai(upper_cards)
                robot.step(user_position, other_played_cards_env)
                message = robot.step(user_position, [])
                out_card_str = message[0]['action']
                first_run = False
            elif first_run and user_position == 'landlord_down':
                print('第一次运行: AI下家')
                # 传递上家出牌给AI
                upper_cards = upper_card(outcard_templ)
                other_played_cards_env = Aconfig_file.card_to_ai(upper_cards)
                robot.step(user_position, other_played_cards_env)
                message = robot.step(user_position, [])
                out_card_str = message[0]['action']
                first_run = False
            elif not first_run:
                # 传递下家出牌给AI
                other_played_cards_env = Aconfig_file.card_to_ai(lower_cards)
                robot.step(user_position, other_played_cards_env)
                # 传递上家出牌给AI
                other_played_cards_env = Aconfig_file.card_to_ai(upper_cards)
                robot.step(user_position, other_played_cards_env)
                message = robot.step(user_position, [])
                out_card_str = message[0]['action']
            # print(message)
            # 根据不同的情况发送对应的表情
            message_backup = message[1]
            one_win_rate = 0
            two_win_rate = 0
            # ----------------暗示专区A----------------------
            for message_action, message_win_rate in message_backup:
                if Average_cards_check(message_action, Aconfig_file.card_super, 'Other') == 1 and len(
                        message_action) == 2 \
                        and two_win_rate == 0:
                    two_win_rate = float(message_win_rate)
                elif len(message_action) == 1 and one_win_rate == 0:
                    # print(message_action)
                    one_win_rate = float(message_win_rate)
            if user_position != 'landlord':
                # 如果出现了不要或要不起的标志再发表情，防止错过牌检测
                if check_flag(btn_name_list, btn_templ, 0) or check_flag(btn_name_list, btn_templ, 8):
                    # 如果地主手上一张牌 自己手上有大王 队友手上 四张牌 就让队友先出单支再自己出对子送他
                    if last_win_rate < 0 < message[0]['win_rate'] and landlord_card == 1 and frined_card <= 4 \
                            and 'D' in cards_str and user_position == 'landlord_up':
                        send_emoji(btn_templ, btn_name_list, 26)
                        time.sleep(2)
                        send_emoji(btn_templ, btn_name_list, 45)
                        time.sleep(2)
                        send_emoji(btn_templ, btn_name_list, 41)
                    # 如果对子的胜率为正 单支的胜率为-则表大哭 表示队友别出单支
                    elif one_win_rate < 0 < two_win_rate and time.time() - start_time >= 15 \
                            and biaoqing_Other_times \
                            and round(message[0]['win_rate'], 4) == two_win_rate:
                        send_emoji(btn_templ, btn_name_list, 42)
                        time.sleep(2)
                        send_emoji(btn_templ, btn_name_list, 26)
                        biaoqing_Other_times -= 1
                        start_time = time.time()
                    # 让队友大胆出牌
                    elif ((message[0]['win_rate'] > 0.9 and Aconfig_file.call_landlord_win_rate < 0.8) or
                          (message[0]['win_rate'] > 1.2)) \
                            and best_good_times:
                        send_emoji(btn_templ, btn_name_list, 36)
                        time.sleep(0.2)
                        best_good_times -= 1
                        start_time = time.time()
                # 省略掉的负面表情攻击
                if user_position != 'landlord' and last_win_rate - message[0]['win_rate'] >= 0.8 and \
                        last_win_rate not in [0, 2000]:
                    out_card_tip(user_position, btn_name_list, btn_templ, 55)
                last_win_rate = message[0]['win_rate']
            # 检查出炸弹牌是否为送牌行为，如果是直接选择游戏结束
            if Aconfig_file.AI_action_fix \
                    and (last_win_rate < 0 and ((Average_cards_check(out_card_str, Aconfig_file.all_cards, 'Other') == 1
                                                 and len(out_card_str) == 4) or (out_card_str == 'XD'))) \
                    and user_position != 'landlord':
                while not check_flag(btn_name_list, btn_templ, 25, Aconfig_file.changbtn_area):
                    click_tools.click_image_in_window(btn_templ[btn_name_list[0]])
                    click_tools.click_image_in_window(btn_templ[btn_name_list[8]])
            show_u = upper_cards
            show_d = lower_cards
            if show_u == '':
                show_u = 'pass'
            if show_d == '':
                show_d = 'pass'
            print(f'{show_u} | {show_d}')

            # 特殊自动出牌区域，防止错过机会被反杀:
            counter = collections.Counter(cards_str)
            flag_si = len([key for key in counter if counter[key] == 4])
            flag_double = len([key for key in counter if counter[key] == 2])

            # 手上纯炸弹时自动出牌 防止resnet脑瘫放牌
            if 'DX' not in cards_str:
                if len(cards_str) == flag_si * 4 and flag_si != 0 and Aconfig_file.AI_action_fix:
                    print('已进入自动出牌模式，防止AI放牌行为!!')
                    while 1:
                        # 重新检测手牌内容
                        counter = collections.Counter(cards_str)
                        if check_flag(btn_name_list, btn_templ, 3, None, 0.8):
                            temp_out = ''
                            for bom in [key for key in counter if counter[key] == 4]:
                                for temp_count in range(4):
                                    temp_out += bom
                                print(f'出牌: {temp_out}')
                                click_tools.select_card_act(btn_templ[btn_name_list[7]], cards_str, temp_out)
                                click_tools.click_image_in_window(btn_templ[btn_name_list[3]])
                                # 更新手牌
                                temp_card = cards_str
                                for cc in temp_out:
                                    temp_card = temp_card.replace(cc, '', 1)
                                cards_str = temp_card
                                break
                        elif check_flag(btn_name_list, btn_templ, 3, None, 0.8):
                            click_tools.click_image_in_window(btn_templ[btn_name_list[8]])
                        # 跳出循环条件
                        elif not check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
                            times += 1
                            time.sleep(0.2)
                            if times >= 8:
                                game_over = True
                                break
                elif Aconfig_file.AI_action_fix and ((flag_si and len(cards_str) == 6)
                                                     or (flag_si and len(cards_str) == 8
                                                         and flag_double == 2)):
                    if lower_cards == '' and upper_cards == '' and user_position == 'landlord':
                        time.sleep(1)
                        print('已进入自动出牌模式，防止AI放牌行为!!')
                        print(f'出牌: {cards_str}')
                        click_tools.select_card_act(btn_templ[btn_name_list[7]], cards_str, cards_str)
                        click_tools.click_image_in_window(btn_templ[btn_name_list[3]])
            # AI出牌区
            times = 0
            if out_card_str != '':
                print(f'出牌: {out_card_str} | 评分: {message[0]["win_rate"]}')
                last_out = out_card_str
                # 等待出牌按钮这样就不用理会过渡动画而导致的出牌按钮延迟的问题
                while not check_flag(btn_name_list, btn_templ, 3, None, 0.8):
                    # 没有托管按钮则游戏结束
                    if not check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
                        times += 1
                        time.sleep(0.5)
                        if times >= 8:
                            print('游戏结束')
                            game_over = True
                            break
                if game_over:
                    break
                click_tools.select_card_act(btn_templ[btn_name_list[7]], cards_str, out_card_str)
                click_tools.click_image_in_window(btn_templ[btn_name_list[3]])
                # 更新手牌
                temp_card = cards_str
                for i in out_card_str:
                    temp_card = temp_card.replace(i, '', 1)
                cards_str = temp_card
                # 等待自己的回合过去
                while check_flag(btn_name_list, btn_templ, 3):
                    pass
            else:
                # Check -- Start
                # 没有托管按钮则游戏结束
                if not check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
                    print('游戏结束')
                    break
                # Program -- Operation
                time.sleep(0.1)
                print(f'出牌: pass | 评分: {message[0]["win_rate"]}')
                click_tools.click_image_in_window(btn_templ[btn_name_list[0]])
                click_tools.click_image_in_window(btn_templ[btn_name_list[8]])
                if game_over:
                    print('游戏结束')
                    break
            # -------------- 暗示专区B -----------------
            if out_card_str != '':
                # 如果手上只剩下王炸或炸弹则给队友倒茶
                if (len(cards_str) == 4 and Average_cards_check(cards_str, Aconfig_file.all_cards,
                                                                'Other') == 1) \
                        or ('DX' in cards_str and len(cards_str) <= 3):
                    out_card_tip(user_position, btn_name_list, btn_templ, 47)
            # 等待自己的回合
            while 1:
                screen_short, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
                screen_short = np.array(screen_short)
                out = screen_tools.find_template_in_region(btn_templ[btn_name_list[51]], screen_short,
                                                           Aconfig_file.btn_check_area, 0.95) != (0, 0)
                tip = screen_tools.find_template_in_region(btn_templ[btn_name_list[48]], screen_short,
                                                           Aconfig_file.auto_tip_pass, 0.75) != (0, 0)
                end_game = screen_tools.find_template_in_region(btn_templ[btn_name_list[28]], screen_short,
                                                                Aconfig_file.end_game_area, 0.9) == (0, 0)
                # print(tip, out, end_game)
                if tip or out:
                    break
                if end_game:
                    times += 1
                    time.sleep(0.5)
                    if times >= 8:
                        print('游戏结束')
                        game_over = True
                        break
            upper_cards = ''
            lower_cards = ''
            if out:
                for ss in range(Aconfig_file.count_check):
                    time.sleep(Aconfig_file.check_delay)
                    temp_su = ''
                    temp_sd = ''

                    u_pass = check_flag(btn_name_list, btn_templ, 22, Aconfig_file.upper_card_area)
                    l_pass = check_flag(btn_name_list, btn_templ, 21, Aconfig_file.lower_card_area)

                    if not u_pass:
                        temp_su = upper_card(outcard_templ)
                    if not l_pass:
                        temp_sd = lower_card(outcard_templ)

                    if len(upper_cards) < len(temp_su):
                        upper_cards = temp_su
                    if len(lower_cards) < len(temp_sd):
                        lower_cards = temp_sd
            else:
                time.sleep(Aconfig_file.check_delay)
                upper_cards = upper_card(outcard_templ)
                lower_cards = lower_card(outcard_templ)
            # 等待跳过当前的提示，防止卡逻辑bug
            while 1:
                screen_short, _ = screen_tools.take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
                screen_short = np.array(screen_short)
                if not screen_tools.find_template_in_region(btn_templ[btn_name_list[48]], screen_short,
                                                            Aconfig_file.auto_tip_pass, 0.75) != (0, 0):
                    break
    except:
        print('记牌错误！已自动托管等待游戏结束!')
        # 尝试关闭广告
        click_tools.click_img_by_opencv(btn_templ, btn_name_list, 28, 0.8)
        while not check_flag(btn_name_list, btn_templ, 25, Aconfig_file.changbtn_area):
            pass
        # 尝试关闭广告
        for i in range(6):
            click_tools.close_AD(AD_templ_dic, btn_templ[btn_name_list[28]])
        click_tools.click_img_by_opencv(btn_templ, btn_name_list, 28, 0.8)
        return True
    # 统一过渡动画
    robot.game_over = True
    for i in range(4):
        time.sleep(1)
        if check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
            print('检测到托管按钮，自动跳过广告检测！')
            return True
    check_good_ad = False
    if Aconfig_file.get_AD_gift:
        check_good_ad = click_tools.click_img_by_opencv(btn_templ, btn_name_list, 24, 0.9)
    if not check_good_ad:
        click_tools.close_AD(AD_templ_dic)
    lingdou = False
    if check_good_ad:
        print('检测到领豆子广告!')
        lingdou = True
        time.sleep(Aconfig_file.AD_time)
        click_tools.click_in_window(92, 90)
    # time.sleep(4)
    for i in range(6):
        if check_flag(btn_name_list, btn_templ, 28, Aconfig_file.end_game_area):
            print('检测到托管按钮，可能是比赛模式，自动跳过关闭广告操作!')
            return True
        click_tools.close_AD(AD_templ_dic, btn_templ[btn_name_list[28]])
        time.sleep(0.8)
        if check_flag(btn_name_list, btn_templ, 25, Aconfig_file.changbtn_area):
            break
    # 领豆子总是会判断错误只好手动加一次判断
    if lingdou:
        time.sleep(1)
        click_tools.close_AD(AD_templ_dic)
    return True


def run_continue():
    btn_img_list = Aconfig_file.get_all_filename(Aconfig_file.Other_btn_path)
    btn_img_templ = Aconfig_file.load_img(Aconfig_file.Other_btn_path, btn_img_list)
    while 1:
        if start_test():
            next_loop = check_flag(btn_img_list, btn_img_templ, 25, Aconfig_file.changbtn_area)
            if not chaojia_next and Aconfig_file.chaojia_continue:
                print(
                    '没有超级加倍卡了，如果还要继续玩的话请购买超级加倍卡，或在配置文件中将 chaojia_continue 的值修改为 False')
                return None
            if next_loop:
                click_tools.click_img_by_opencv(btn_img_templ, btn_img_list, 23)  # 25继续游戏 23切换对手


# 模型测试
if __name__ == '__main__':
    LandlordModel.init_model('baselines/douzero_WP/landlord.ckpt')
    dz_sl = 0
    nm_sl = 0
    game_over = False
    # 模型加载路径
    landlord_path = 'douzero_WP'
    up_path = 'resnet'
    down_path = 'resnet'
    ''' famer_win_rate(100): WP: 32, 38 | resnet: 32, 40'''
    for posss in range(1):
        game_over = False
        while 1:
            player_1, player_2, player_3, d_p = get_cards_ext.WashAndPush_Card(get_cards_ext.Creat_Card())
            down_p = ''
            up_p = ''
            landlord_p = ''
            ff = -1000
            f1 = BidModel.predict_score(player_1)
            f2 = BidModel.predict_score(player_2)
            f3 = BidModel.predict_score(player_3)
            if f1 > -0.2:
                ff = f1
                landlord_p = player_1 + d_p
                up_p = player_2
                down_p = player_3
            elif f2 > -0.2:
                ff = f2
                landlord_p = player_2 + d_p
                up_p = player_3
                down_p = player_1
            elif f3 > -0.2:
                ff = f3
                landlord_p = player_3 + d_p
                up_p = player_2
                down_p = player_1
            else:
                continue
            landlord_p = get_cards_ext.sort_string(landlord_p)
            dz_yg = LandlordModel.predict_by_model(landlord_p, d_p)
            if 0 > dz_yg > 0.3:  # 过滤地主指定得分区间的牌型
                posss -= 1
                continue
            print('手牌分布:', player_1, player_2, player_3, d_p)
            print(f'局前预估得分:{ff}')
            print(f'地主手牌: {landlord_p}, 底牌: {d_p}')
            print('预估地主得分:', dz_yg)
            break

        ''' 在这里可以重新指定AI手牌: '''
        # d_p = '863'
        # landlord_p = 'X22AAAAQJJT988876633'
        # down_p = 'D2KKKQQQJT9987633'
        # up_p = '2KJTT977655554444'

        landlord = AI_init(landlord_p, d_p, 0.1, 'landlord', landlord_path)
        up = AI_init(up_p, d_p, 0.1, 'landlord_up', up_path)
        down = AI_init(down_p, d_p, 0.1, 'landlord_down', down_path)
        print('初始化完成.')
        first_run = True
        temp_l = None
        temp_d = None
        temp_u = None
        while 1:
            if first_run:
                print(landlord_p, down_p, up_p, d_p)
                temp_l = landlord.step('landlord', [])[0]
                print('地主:', temp_l['action'], temp_l['win_rate'])
                for c in temp_l['action']:
                    landlord_p = landlord_p.replace(c, '', 1)
                out1 = Aconfig_file.card_to_ai(temp_l['action'])
                down.step('landlord_down', out1)
                temp_d = down.step('landlord_down', [])[0]
                print('下家:', temp_d['action'], temp_d['win_rate'])
                for c in temp_d['action']:
                    down_p = down_p.replace(c, '', 1)

                out2 = Aconfig_file.card_to_ai(temp_l['action'])
                out3 = Aconfig_file.card_to_ai(temp_d['action'])
                # print(temp_l['action'], temp_d['action'])
                up.step('landlord_up', out2)
                up.step('landlord_up', out3)
                temp_u = up.step('landlord_up', [])[0]
                print('上家', temp_u['action'], temp_u['win_rate'])
                for c in temp_u['action']:
                    up_p = up_p.replace(c, '', 1)
                first_run = False
                # print(temp_l)
                # break
            else:
                try:
                    while 1:
                        for countpos in ['landlord', 'landlord_down', 'landlord_up']:
                            if countpos == 'landlord':
                                out1 = Aconfig_file.card_to_ai(temp_u['action'])
                                out2 = Aconfig_file.card_to_ai(temp_d['action'])
                                landlord.step(countpos, out2)
                                landlord.step(countpos, out1)
                                # print('fff',out2, out1)
                                temp_l = landlord.step(countpos, [])[0]
                                for i in temp_l['action']:
                                    landlord_p = landlord_p.replace(i, '', 1)
                                print("地主:", temp_l['action'], round(temp_l['win_rate'], 3), f'剩余手牌:{landlord_p}')
                            elif countpos == 'landlord_down':
                                # print(temp_u['action'], temp_l['action'])
                                out1 = Aconfig_file.card_to_ai(temp_u['action'])
                                out2 = Aconfig_file.card_to_ai(temp_l['action'])
                                down.step(countpos, out1)
                                down.step(countpos, out2)
                                temp_d = down.step(countpos, [])[0]
                                # print(11, temp_d)
                                for i in temp_d['action']:
                                    down_p = down_p.replace(i, '', 1)
                                print('下家:', temp_d['action'], round(temp_d['win_rate'], 3), f'剩余手牌: {down_p}')
                            elif countpos == 'landlord_up':
                                out1 = Aconfig_file.card_to_ai(temp_l['action'])
                                out2 = Aconfig_file.card_to_ai(temp_d['action'])
                                up.step(countpos, out1)
                                up.step(countpos, out2)
                                temp_u = up.step(countpos, 2)[0]
                                for i in temp_u['action']:
                                    up_p = up_p.replace(i, '', 1)
                                print('上家:', temp_u['action'], round(temp_u['win_rate'], 3), f'剩余手牌:{up_p}')
                            # time.sleep(0.2)
                            if len(landlord_p) == 0:
                                print('地主胜利!')
                                game_over = True
                                dz_sl += 1
                                break
                            elif len(up_p) == 0 or len(down_p) == 0:
                                print('农民胜利!')
                                game_over = True
                                nm_sl += 1
                                break
                        if game_over:
                            break
                except:
                    print('游戏结束!')
                    break
            if game_over:
                break
    print(f'地主胜利局数:{dz_sl}, 农民胜利局数:{nm_sl}')
