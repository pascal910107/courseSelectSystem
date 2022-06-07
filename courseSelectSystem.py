from cv2 import imshow, threshold
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import numpy as np


# 背景執行
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)
# browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

#正常執行
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get('https://course.fcu.edu.tw/')



def captchaConversion1():

    img = Image.open('./captcha_login.png').convert('L')
    table=[]
    for i in range(256):
        if i<127:
            table.append(0)
        else:
            table.append(1)
    img = img.point(table,'1')
    img.save('./out.png')
    # img.show()


    img = Image.open('./out.png')
    pixel_matrix = img.load()
    for column in range(1, 21):
        for row in range(1, 49):
            if pixel_matrix[row, column] == 0 and pixel_matrix[row, column - 1] == 255 and pixel_matrix[row, column + 1] == 255 :
                pixel_matrix[row, column] = 255
            if pixel_matrix[row, column] == 0 and pixel_matrix[row - 1, column] == 255 and pixel_matrix[row + 1, column] == 255:
                pixel_matrix[row, column] = 255
    # img.show()


    pytesseract.pytesseract.tesseract_cmd = r'C:\VSCode\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(img)
    return "".join(list(filter(str.isdigit, text)))


def captchaConversion2():

    dst = cv2.imread('./captcha_login.png')
    ret,thresh = cv2.threshold(dst,127,255,cv2.THRESH_BINARY_INV)
    cv2.imwrite('./out.png', thresh)
    plt.imshow(thresh)
    # plt.show()

    img = Image.open('./out.png').convert('L')
    table=[]
    for i in range(256):
        if i>127:
            table.append(1)
        else:
            table.append(0)
    img = img.point(table,'1')
    img.save('./out.png')
    # img.show()


    image = cv2.imread('./out.png')
    dst = cv2.fastNlMeansDenoisingColored(image, None, 67, 67, 7, 21)
    cv2.imwrite('./out.png', dst)
    plt.imshow(dst)
    # plt.show()
   


    pytesseract.pytesseract.tesseract_cmd = r'C:\VSCode\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(dst)
    text = text.replace('S','5').replace('$','5').replace('e','0')
    return "".join(list(filter(str.isdigit, text)))





def downloadImg():
    img_base64 = browser.execute_script('''
    var ele = arguments[0];
    var cnv = document.createElement('canvas');
    cnv.width = ele.width; cnv.height = ele.height;
    cnv.getContext('2d').drawImage(ele, 0, 0);
    return cnv.toDataURL('image/jpeg').substring(22);
    ''', browser.find_element(By.XPATH, '//*[@id="ctl00_Login1_Image1"]'))
    
    with open("./captcha_login.png", 'wb') as image:
        image.write(base64.b64decode(img_base64))



def fillIn(text):

    username = browser.find_element(By.ID, 'ctl00_Login1_UserName')
    password = browser.find_element(By.ID, 'ctl00_Login1_Password')
    captcha = browser.find_element(By.ID, 'ctl00_Login1_vcode')
    login = browser.find_element(By.ID, 'ctl00_Login1_LoginButton')

    username.send_keys('D0957293')
    password.send_keys('*************')
    captcha.clear()
    captcha.send_keys(text)
    login.click()



def addCourse():
    try:
        add = browser.find_element_by_xpath('//*[@id="ctl00_MainContent_TabContainer1_tabSelected_gvToAdd"]/tbody/tr[2]/td[1]/input')
        add.click()
        # time.sleep(0.5)
        browser.switch_to_alert().accept()
        if browser.find_element_by_xpath('//*[@id="ctl00_MainContent_TabContainer1_tabSelected_lblMsgBlock"]/span').text != '加選成功':
            addCourse()
        else:
            return
    except:
        login()



def selectCourse(courseNum):
    try:
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="ctl00_MainContent_TabContainer1_tabSelected_Label3"]')))
    finally:
        browser.find_element_by_xpath('//*[@id="ctl00_MainContent_TabContainer1_tabSelected_tbSubID"]').send_keys(courseNum)
        addCourse()




def login():
    while 1:
        downloadImg()
        text = captchaConversion1()
        if len(text) != 4:
            text = captchaConversion2()
        
        print(text)
        fillIn(text)
        if browser.current_url != "https://course.fcu.edu.tw/Login.aspx":
            #選課代號
            selectCourse(1234)
            break
            #登入登出迴圈
            # browser.get('https://course.fcu.edu.tw/')


login()

