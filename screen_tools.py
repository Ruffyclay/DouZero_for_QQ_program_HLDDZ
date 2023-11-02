# -*- coding: utf-8 -*-
# Created by: Ruffy
import time
from ctypes import windll

import cv2
import numpy as np
import win32gui
import win32ui
from PIL import Image, ImageGrab
import Aconfig_file


# 获取指定程序的图像并返回 参数顺序是title class 写反了
def take_screenshot(window_title, window_class):
    region = None
    try_count = 3
    success = False
    while try_count > 0 and not success:
        try:
            try_count -= 1
            hwnd = win32gui.FindWindow(window_class, window_title)
            if hwnd == 0:
                print(f"窗口未找到: {window_title}")
                return None, (0, 0)
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top
            screen_zoom_rate = 1  # Replace with your desired zoom rate

            width = int(width / screen_zoom_rate)
            height = int(height / screen_zoom_rate)

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            im = Image.frombuffer(  # 无用功罢了
                "RGB",
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'RGBX', 0, 1)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if region is not None:
                im = im.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))

            im = im.resize((1796, 1047))
            im = im.convert("RGB")  # Convert to RGB format

            if result:
                success = True
                return im, (left, top)
                # return im
        except Exception as e:
            print("截图时出现错误:", repr(e))
            time.sleep(0.2)

    return None, (0, 0)


# 用来识别牌或某个标志
def check_img(image, temp_dic, return_mode='card', resize_info=1, threshold=0.9, max_distance=10):
    cards_str = ''
    turn_check = False
    if return_mode == 'card':
        for templ_name, templ_img in temp_dic.items():
            height, width, c = templ_img.shape

            # 缩放到原来的指定倍数
            new_width = int(templ_img.shape[1] * resize_info)
            new_height = int(templ_img.shape[0] * resize_info)

            # 缩放图像
            templ_img = cv2.resize(templ_img, (new_width, new_height))
            # cv2.imshow('serch_img', image)
            # cv2.imshow('deserch_img',templ_img)
            # cv2.waitKey(0)

            results = cv2.matchTemplate(image, templ_img, cv2.TM_CCOEFF_NORMED)
            loc = np.where(results >= threshold)

            merged_loc = []
            for pt in zip(*loc[::-1]):
                if not merged_loc:
                    merged_loc.append(pt)
                else:
                    last_pt = merged_loc[-1]
                    if abs(pt[0] - last_pt[0]) < max_distance and abs(pt[1] - last_pt[1]) < max_distance:
                        merged_loc[-1] = ((pt[0] + last_pt[0]) // 2, (pt[1] + last_pt[1]) // 2)
                    else:
                        merged_loc.append(pt)

            num = 0
            if len(merged_loc) > 1:
                num = 2
            elif len(merged_loc):
                num = 1
            # 同一种花色最多两张牌
            if num == 1:
                cards_str += templ_name[-1]
            elif num == 2:
                cards_str += templ_name[-1] + templ_name[-1]
            if num != 0:
                turn_check = True
            for pt in merged_loc:
                top_left = pt
                bottom_right = (top_left[0] + width, top_left[1] + height)
                cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(image, templ_name, top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        new_width = int(temp_dic.shape[1] * resize_info)
        new_height = int(temp_dic.shape[0] * resize_info)
        # 缩放图像
        temp_dic = cv2.resize(temp_dic, (new_width, new_height))
        results = cv2.matchTemplate(image, temp_dic, cv2.TM_CCOEFF_NORMED)
        loc = np.where(results >= threshold)
        merged_loc = []
        for pt in zip(*loc[::-1]):
            if not merged_loc:
                merged_loc.append(pt)
            else:
                last_pt = merged_loc[-1]
                if abs(pt[0] - last_pt[0]) < max_distance and abs(pt[1] - last_pt[1]) < max_distance:
                    merged_loc[-1] = ((pt[0] + last_pt[0]) // 2, (pt[1] + last_pt[1]) // 2)
                else:
                    merged_loc.append(pt)
        if len(merged_loc) > 0:
            return True
        else:
            return False
    # 测试专用
    # cv2.imshow("Detection Results", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return cards_str


# 用来查找特定的模板内容的，返回最左边的x,y坐标 模板 原图 区域
def find_template_in_region(template_image, search_image, region, threshold=0.75):
    template_cv = template_image
    x1, y1, x2, y2 = region
    # print(region)
    search_region = search_image[y1:y2, x1:x2]
    result = cv2.matchTemplate(search_region, template_cv, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # cv2.imshow('',search_region)
    # cv2.waitKey(0)
    if max_val >= threshold:
        match_x = x1 + max_loc[0]
        match_y = y1 + max_loc[1]
        # print(f"Template matched at: ({match_x}, {match_y})")

        h, w = template_image.shape[:2]
        top_left = (match_x - x1, match_y - y1)
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(search_region, top_left, bottom_right, (0, 255, 0), 2)

        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2

        # cv2.circle(search_region, (center_x, center_y), 5, (0, 0, 255), -1)

        # cv2.imshow('Matched Area', search_region)
        # cv2.waitKey(0)

        return center_x // 1.1, (center_y + region[1]) // 1.1
    else:
        return 0, 0


def calculate_image_similarity(image1, image2, threshold=0.9):
    # Convert images to grayscale
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('',image2)
    # cv2.waitKey(0)
    # Calculate template matching result
    result = cv2.matchTemplate(gray_image1, gray_image2, cv2.TM_CCOEFF_NORMED)

    # Get maximum value and location
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Compare max_val with threshold
    if max_val >= threshold:
        return True
    else:
        return False


def show_wind(area=None):
    img, _ = take_screenshot(Aconfig_file.window_title, Aconfig_file.window_class)
    if area is None:
        img = np.array(img)
    else:
        img = np.array(img.crop(area))
    cv2.imshow('截图', img)
    cv2.waitKey(0)
