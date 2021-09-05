import CWBOpendata
from bs4 import BeautifulSoup
import datetime
from flask import Flask

### func ###
# 輸入降雨機率資料到html
def PoP2html(tr,series):
    date_tds=tr.find_all('td')
    for i,td in enumerate(date_tds):
        td.string=series[i]


# 取得星期幾
def get_week_day(date):
    week_day_dict = {
    0 : '星期一',
    1 : '星期二',
    2 : '星期三',
    3 : '星期四',
    4 : '星期五',
    5 : '星期六',
    6 : '星期日',
    }
    day = date.weekday()
    return week_day_dict[day]


### 程式開始 ###
farmerInfo = Flask(__name__)

@farmerInfo.route('/farmerInfo.html')
def farmer_info():
    # 載入網頁樣板
    with open('template.html','r',encoding='utf-8') as temp_file:
        temp_html=temp_file.read()
    soup = BeautifulSoup(temp_html,'html.parser')

    # 處理當天日期
    today = f'今日  {datetime.date.today()}    {get_week_day(datetime.date.today())}'
    soup.find('h1',id='today').string = today

    # 處理降雨機率資料
    df = CWBOpendata.get_PoP6h()
    PoP2html(soup.find('tr',id='date'),df['startTime'])
    PoP2html(soup.find('tr',id='HH'),df['HH'])
    PoP2html(soup.find('tr',id='PoP'),df['elementValue'])

    # 處理價格資料
    with open('vegprice.html','r',encoding='utf-8') as vegprice_file:
        vegprice=vegprice_file.read()
    soup_price=BeautifulSoup(vegprice,'html.parser')
    soup.find('div',id='price').append(soup_price)

    # 回傳當日查詢靜態網頁
    return soup.prettify()

if __name__ == '__main__':
    farmerInfo.run(host='0.0.0.0',port=80)