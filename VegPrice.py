# coding:utf-8
import pytesseract
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from bs4 import BeautifulSoup

### func ###
# 自動登入
def automatic_login(): 
    driver.find_element_by_id('ctl00_contentPlaceHolder_txtSupplyNo').send_keys('p99582')   #輸入供應代號
    driver.find_element_by_id('ctl00_contentPlaceHolder_txtSupplySub').send_keys('帳號')   # 輸入帳號

    while driver.current_url==url:
        # 取得驗證碼字串
        txtValCode=get_validation_code()
        driver.find_element_by_id('ctl00_contentPlaceHolder_txtPassword').send_keys('密碼')   # 輸入密碼
        driver.find_element_by_id('ctl00_contentPlaceHolder_txtValCode').send_keys(txtValCode)    # 輸入驗證碼
        # 點擊登入按鈕的指令
        driver.find_element_by_id('ctl00_contentPlaceHolder_btnLogin').click()

        time.sleep(0.5)
        # 判斷有提示框時要按確定
        login_alert = EC.alert_is_present()
        if login_alert(driver):
            login_alert(driver).accept()

        # 判斷是否登入成功，成功：結束loop；失敗:繼續下一次登入嘗試
        check_url = EC.url_to_be(target_url)
        if check_url(driver):
            break


# 取得驗證碼
def get_validation_code():
    # 網頁中圖片的定位
    img = driver.find_element_by_id('ctl00_contentPlaceHolder_imageValCode')
    # driver 在 headless 模式下執行時，直接使用網頁中驗證碼的html資料來定位
    # 設定圖片位子和寬高
    location = img.location
    # 返回左上角和右下角的座標
    top,bottom,left,right = location['y'], location['y']+25, location['x'], location['x']+65

    # 截取整張網頁圖片
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    # 將網頁中需要的圖片通過座標裁剪出來
    screenshot = screenshot.crop((left, top, right, bottom))

    # 辨識驗證碼
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    # 將圖片轉化為灰度影像
    screenshot = screenshot.convert('L')
    # 原圖固定為綠底白字，故臨界值為200，將白字變為黑字
    threshold = 200
    table=[]
    for i in range(256):
        if i > threshold:
            table.append(0)
        else:
            table.append(1)

    screenshot = screenshot.point(table,'1')
   
    # 只輸出數字:config參數可設定要辨識的白名單，避免1變成I之類的狀況
    validation_code = pytesseract.image_to_string(screenshot,config='-c tessedit_char_whitelist=0123456789')
    validation_code = validation_code.replace(' ','')
    return validation_code[:4]


# 清除不必要的欄位資料
def clearnColumn(columns):
    for i in [2,3,4,6,11]:
        columns[i].extract()

# 取得價格html table
def get_price_html():
    html = BeautifulSoup(driver.page_source,'html.parser')
    table = html.find('div',id='ctl00_contentPlaceHolder_panel').find_all('table')[1]

    main_title_trs = table.find_all('tr',class_='main_title')
    clearnColumn(main_title_trs[0].find_all('td'))
    main_title_trs[1].extract()
    main_title_trs[2].extract()
    main_title_trs[3].extract()

    table_body_trs = table.find_all('tr',{'class':re.compile('main_main')})
    for tr in table_body_trs:
        clearnColumn(tr.find_all('td'))
    
    return table.prettify()

### 程式開始 ###
# 打開網頁
url = 'https://amis.afa.gov.tw/coop1/CoopVegLogin2.aspx'
target_url = 'https://amis.afa.gov.tw/coop1/CoopVegSupplierTransInfoQuery.aspx'
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('--headless')

driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
driver.get(url)
driver.maximize_window()
time.sleep(0.5)

# 登入
automatic_login()

# 查詢當日價格
driver.find_element_by_id('ctl00_contentPlaceHolder_ucCoopVegFruitMarket_radAllMarket').click() #輸入查詢市場
driver.find_element_by_id('ctl00_contentPlaceHolder_btnQuery').click()
time.sleep(0.5)
alert = EC.alert_is_present()
if alert(driver):
    veg_price = f'<h1 align="center" valign="middle">{alert(driver).text}</h1>'
    alert(driver).accept()
else:
    veg_price = get_price_html()

with open('vegprice.html','w',encoding='utf-8') as file:
    file.write(veg_price)

driver.quit()