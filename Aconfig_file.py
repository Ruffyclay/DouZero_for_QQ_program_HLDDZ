# -*- coding: utf-8 -*-
# Created by: Ruffy
import collections
import os
import cv2

'''
    事先声明，基本上涉及到截图的都是用两点式，UI设计的是一点加高度与宽度
'''

# DouZero必须要的区域
AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
              8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
              12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}
# 参考牌专属
card_super = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
all_cards = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2', 'D', 'X']
pass_list = ['DX']  # 可以快速忽略的牌型
big_boom_list = ['2', 'A', 'K']  # 三个里面占两个就通过
big_boom_list_two = ['2', 'A', 'K']  # 或者有四2 四A也可以通过
small_cards_list = ['T', '9', '8', '7', '6', '5', '4', '3']

# 手牌素材库路径 使用函数生成列表来加载，懒得写，乐
my_card_path = r'./pic_resource/Hand_card'
out_card_path = r'./pic_resource/card_out'
Other_btn_path = './pic_resource/Other'
AD_close_path = r'./pic_resource/AD_close'
dp_path = r'./pic_resource/three_cards_pic'

# 截图和控制程序的标题和窗口类型
window_title = '雷电模拟器'
window_class = 'LDPlayerMainFrame'

# 基础分析部分
my_card_area = (10, 670, 1607, 782)  # 我的手牌区域
my_out_card_area = (7, 652, 1645, 740)  # 我要出的手牌区域
three_card_area_A = (796, 44, 945, 129)  # 三张底牌 A部分
three_card_area_B = (895, 54, 1050, 127)  # 三张底牌 B部分
main_area = (196, 69, 1440, 741)  # 游戏主要区域
btn_check_area = (520, 540, 1335, 600)  # 游戏主要检查区域
dp_threshold = 0.85  # 底牌置信度
upper_card_area = (200, 200, 900, 489)  # 上家出牌区域
upper_card_rate = 1  # 上家出牌缩放程度
lower_card_area = (900, 200, 1500, 489)  # 下家出牌区域
lower_card_rate = 1  # 下家出牌缩放程度
btn_area = (278, 522, 1335, 615)  # 游戏过程中按钮区域

landlord_up_area = (144, 333, 172, 382)  # 地主在上的区域
landlord_down_area = (1573, 333, 1599, 381)  # 地主在下的区域

# 其他参数
card_pixels_x = 80  # 卡牌之间的x轴之间的像素距离 用屏幕工具测量出来的
select_card_fix = 5  # 当AI为地主的时候，手牌>18且出现点击不准确的问题可适当调整
card_select_area = (0, 686, 1753, 712)  # 牌点击的位置
card_select_fix_pix = -25  # (card_select_area(x1, y1, x2, y2)中的y1向下偏移的参数（点击的位置）)
game_title_area = (500, 143, 1100, 313)  # 游戏结束标志区域 用来检测胜利状态的 一般 不用
changbtn_area = (700, 863, 1236, 970)  # 继续游戏开始按钮
end_game_area = (1150, 50, 1480, 160)  # 游戏结束检测标志位 追踪专用
AD_time = 60  # 等待广告时长（秒）
left_jiabei = (3, 579, 142, 625)  # 左边玩家加倍标志区域
right_jiabei = (1594, 579, 1718, 625)  # 右边玩家加倍标志区域
left_player = (80, 316)  # 左边玩家的头像点击位置
right_player = (1521, 323)  # 右边玩家头像的点击位置
auto_round_pass = (687, 489, 899, 582)  # 系统自动跳过区域
auto_tip_pass = (737, 846, 839, 900)  # 系统提示无法出牌区

mingpai_win_rate = 0.93  # 当自己为地主时，第一次出牌得分为多少时明牌? 默认要平均牌才行

count_check = 4  # 如果没有无法出牌的提示，校验多少次？
check_delay = 0.1  # 校验时间间隔
get_AD_gift = False  # 是否开启广告领豆子模式?
chaojia_continue = True  # 是否开启有超级加倍才进行游戏模式？
Famer_mode = 'resnet'


# 普通经典场参数
call_landlord_win_rate = -0.2  # 自己叫牌最少预估得分
call_landlord_win_rate_two = 1  # 多少分必叫地主? 手上有单王时
rob_my_self_win_rate = 0  # 别人叫牌自己想抢地主时最少预估得分
rob_landlord_win_rate = 0.15  # 自己叫牌但被抢地主时最少预估得分 默认要发牌平均才抢
when_landlord_jiabei = 0.15  # 自己叫地主时多少评分能加倍或超级加倍?
when_famer_jiabei = 1  # 当自己为农民时多少分能加倍或超级加倍?
jiabei_allied = 0.1  # 牌力评分大于多少时并且队友加倍了时可以加倍
jiabei_allied_master = 0.3  # 牌力评分大于多少时并且地主不加倍时可以加倍
when_rob_landlord_jiabei = 0.5  # 当自己地主为抢过来的时候多少评分才能加倍
mingpai_rules = True  # 是否开启明牌规则?
AImodel = 'resnet'  # 默认加载地主模型类型
king_check = False  # 是否考虑王炸可能而进行叫牌行为?
think_landlord_double = False  # 加倍时是否考虑地主加倍?
allow_card_super = len(card_super) - 5  # 平均参考牌，检测断张，如果设置的太大则没有意义
allow_card_super_DX = len(card_super) - 6  # 当有王炸在手时，断张允许程度
check_big_boom = False  # 叫牌时是否考虑大大的炸弹？ K 或 K 以上的炸弹
check_boom_num = 0  # 叫牌时如果上面大炸弹不满足则参考的炸弹数量
mast_need_card = ['2']  # 必须存在的手牌，防止遇到单方面的劣势
check_other = False  # 叫地主时是否进行牌型评估？
max_small_card_nums = 12  # 叫地主时小牌数量不得多于N张
AI_action_fix = False  # 是否进行AI决策纠正?
how_f_win_rate_can_compare = 0.7    # 当农民多少评分时才可以考虑当农民）
famer_win_rate_weight = 0.8  # 当农民胜率权重
call_landlord_win_rate_weight = 5  # 叫地主时胜率权重
rob_landlord_win_rate_weight = 2  # 抢地主时胜率权重


# 整理手牌检测时的顺序，要和游戏一致
def generate_poker_list():
    order = ["3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A", "2"]
    suits = ["mr", "mb"]
    poker_list = ['mrD', 'mbX'] + [suit + card for card in reversed(order) for suit in suits]
    return poker_list


def out_poker_list():
    order = ["3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A", "2"]
    suits = ["or", "ob"]
    poker_list = ['orD', 'obX'] + [suit + card for card in reversed(order) for suit in suits]
    return poker_list


def dp_poker_list():
    order = ["3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A", "2"]
    suits = ["odr", "odb"]
    poker_list = ['odrD', 'odbX'] + [suit + card for card in reversed(order) for suit in suits]
    return poker_list


# 转换函数，将指定的牌字符串转换成AI能看得懂的形式 返回列表
def card_to_ai(cards_str):
    print(cards_str)
    env_card = [RealCard2EnvCard[c] for c in cards_str]
    env_card.sort()
    return env_card


# 遍历文件夹中的所有文件
def load_img(image_folder_path, poker_list):
    loaded_hand_images = {}  # 初始化字典
    missing_images = []

    for card_name in poker_list:
        filename = card_name + ".png" if not card_name.endswith(".png") else card_name
        if '\\' in filename:
            filename = filename.split('\\')[1]
        filepath = os.path.join(image_folder_path, filename)
        # print(f'路径: {filepath}, 文件名: {filename}')
        if os.path.isfile(filepath):
            try:
                img = cv2.imread(filepath)
                loaded_hand_images[card_name] = img
            except Exception as e:
                print(f"无法加载图片 {filename}: {e}")
        else:
            missing_images.append(filename)

    if missing_images:
        print(f"路径:{image_folder_path}中缺少必要的参考图:")
        for missing_image in missing_images:
            print(missing_image)
        print("请确保所有参考图都在指定的文件夹中。")
        return None  # 返回 None 表示加载失败
    return loaded_hand_images


def get_all_filename(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)

    return file_list


def list_files_in_directory(directory):
    try:
        files = os.listdir(directory)
        for file in files:
            print(file)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    card = 'DXAAAAKKKK'
    counter = collections.Counter(card)
    for i in [key for key in counter if counter[key] == 4]:
        if i in big_boom_list:
            print(True)
