import requests
import pandas

def get_PoP6h():
    '''
    透過氣象局API 取得未來24小時的降雨機率(每6小時一個區間)
    整理並回傳 dataframe 

    example:
        startTime elementValue  HH  
    0  2021-07-28          20%  下午
    1  2021-07-28          30%  晚上
    '''
    # 取得降雨機率資料
    url='https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-025?Authorization=CWB-90F4EAC5-1189-40D7-9C26-7ED182FB7403&locationName=西螺鎮&elementName=PoP6h'
    res=requests.get(url)
    data=res.json()['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][:4]
    
    #整理並回傳dataframe
    dict_time = {'00':'凌晨','06':'早上','12':'下午','18':'晚上'}

    df = pandas.json_normalize(data)
    df['HH']=[dict_time[HH[11:13]] for HH in df['startTime']]
    df['startTime']=[date[:10] for date in df['startTime']]
    df['elementValue']=[PoP[0]['value']+' %' for PoP in df['elementValue']]
    df=df.drop(columns='endTime')

    return df





