from abc import ABC, abstractmethod
from typing import List, Dict, Any
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class AddForJikai:
    '''
    次回請求 '次'　を　追記する
    出荷日基準で求めた〆日と、納期基準で求めた〆日が違っていたら、次回請求

    code : 
    from test import *
    add = AddForJikai()
    add.add_to_yoteiSouko('20260724', '20260727', '25')
                            出荷日       納期     〆日

    次回請求の場合は     return '次' 
    次回請求でない場合は return 'hoge'
    '''
    def __init__(self)-> None:
        pass

    def add_to_yoteiSouko(self, *args) -> str:
        returnTxt = 'hoge'
        syukkabi = args[0]
        nouki = args[1]
        close_day = args[2]

        def calc_closeDate(stdDate: datetime.datetime, close_day:str)-> str:       
            '''
            stdDate:基準日（出荷日または納期) 
            2026/7/29現在は締め日が'1'の顧客は無いが、今後発生した時、
            effitAが'01'と管理するか、'1'と管理するか分からない。
            '''
            std_day:str = str(stdDate.day) # '1', '31', '25','20',...
            
            if close_day == '31':  #締めが31なら納期の月の末尾
                closeDate: datetime.datetime = (
                    (stdDate + relativedelta(months=1)).replace(day=1) 
                    - timedelta(days=1)
                    )
            elif close_day == '1' or close_day == '01':  #締めが1日なら、
                if std_day =='1':
                    closeDate = stdDate  #が基準日が1日なら、基準日と同じ日、
                else:                   #それ以外は、基準日の翌月の1日
                    closeDate = (stdDate + relativedelta(months=1)).replace(day=1) 
            else: 
                #締めが1日でも31日でもない場合は、
                #締め日が基準日以上だったら、基準日の月の締め日、
                if int(close_day) - int(std_day) >= 0 :  
                    closeDate = stdDate.replace(day= int(close_day))
                else:
                    #締め日の方が小さかったら、基準日の翌月の締め日。                                   
                    closeDate = (
                        (stdDate + relativedelta(months=1))
                        .replace(day= int(close_day)))

            return closeDate.strftime('%Y/%m/%d')

        #close_day: str = self._close_days[tokuiCD]
        d_syukkabi = datetime.datetime.strptime(syukkabi, '%Y%m%d')
        d_nouki = datetime.datetime.strptime(nouki, '%Y%m%d')

        closeDate_on_syukkabi = calc_closeDate(d_syukkabi, close_day)
        closeDate_on_nouki = calc_closeDate(d_nouki, close_day)

        if closeDate_on_syukkabi != closeDate_on_nouki:
            returnTxt = '次'

        return returnTxt


