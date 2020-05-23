#載入所需的程式庫
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

#載入港交所最新通告網頁，再以BeautifulSoup拆解其html結構
page = requests.get("http://www.hkexnews.hk/listedco/listconews/mainindex/SEHK_LISTEDCO_DATETIME_TODAY_C.HTM")
soup = BeautifulSoup(page.content, 'html.parser')

#以tag tr 及 class開首為row，載入通告列表中的每一項目
announcement=soup.find_all('tr', class_=re.compile(r"^row"))

#設定列表以載入通告不同選項
date_tags=[]           #載入日期及時間
date1_tags=[]          #把date_tags的日期及時間以空格分開 
code_tags=[]           #載入股票編號
name_tags=[]           #載入公司名稱
title_tags=[]          #載入通告類別
title2_tags=[]         #載入通告標題
link_tags=[]           #載入通告鏈結

#以迴路將資料載入各個選項變數
for i in range(len(announcement)):
        date_tags.append(announcement[i].select('td')[0].get_text())
        code_tags.append(announcement[i].select('td')[1].get_text())
        name_tags.append(announcement[i].select('td')[2].get_text())
        title_tags.append(announcement[i].find(id='hdLine').get_text())
        title2_tags.append(announcement[i].find(class_='news').get_text())
        link_tags.append(announcement[i].find('a')['href'])

#將date_tags中的日期及時間中間加入空格，並輸入到date1_tags
for i in date_tags:
    tmp=i[:-5]+" "+i[-5:]
    date1_tags.append(tmp)

#在通告鏈結中加回港交所的域名        
for i in range(len(link_tags)):
    link_tags[i]='http://www.hkexnews.hk'+link_tags[i]

#將所有資料輸入到一個資料列表變數
announce_table = pd.DataFrame({
        "日期": date1_tags, 
        "股票編號": code_tags, 
        "公司名稱": name_tags, 
        "通告類別": title_tags,
        "標題": title2_tags,
        "連結": link_tags
    })

#讀入要追蹤的股票編號表
target=['00763','00316','00358','00941','02628','00006']

#在資料列表中篩選出相關通告並列印
target_table=announce_table.loc[announce_table['股票編號'].isin(target)]
print(target_table)

#若要以其他準則篩選，如通告類別為盈利警告，亦可以下列程式篩出
print(announce_table.loc[announce_table['通告類別'].str.contains("盈利警告")])

#以下為電郵程式，先載入相關程式庫
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

pd.set_option('display.max_colwidth', -1)  #防止程式自行省略太長的網址鏈結

#以gmail作示範，設定輸出電郵地址及密碼
gmail_user = 'sender@gmail.com'  
gmail_password = 'XXXXXXXX'

#設定送件人、收件人、電郵題目及電郵內文
sent_from = 'sender@gmail.com'
to = 'receiver@gmail.com'  
subject = '上市公司通告篩選器'  


msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = sent_from
msg['To'] = to

#電郵內文為將篩選結果target_table化做html格式

html='''\
<html>
  <head></head>
  <body>
'''+target_table.to_html(index=False)+'''\
</body>
</html>
'''

body = MIMEText(html, 'html')
msg.attach(body)

#送出電郵
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.ehlo()
server.login(gmail_user, gmail_password)
server.sendmail(sent_from, to, msg.as_string())
server.quit()
