#! python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sql_query import *
import csv
import pandas as pd
import platform
import pickle



class CloseDate:

    def __init__(self, uriagebi, sengetu):
        
        pf = platform.system()
        if pf == 'Windows' or pf == 'Linux':
            sql = SqlQuery(uriagebi, sengetu)
            tokuisaki_df = sql.get_tokuisaki_sime()
            del sql
            tokuisaki = tokuisaki_df.values.tolist()
            self.closeDate = {}
            for line in tokuisaki:
                if line[0] >= 'T6000':
                    break
                else:
                    self.closeDate[line[0]] = line[1]
        else:
            mypath = r'../master/effitA/tokuisaki.csv'
            tokuisaki_file = open(mypath, encoding='cp932')
            file_reader = csv.reader(tokuisaki_file)
            tokuisaki = list(file_reader)
            tokuisaki_file.close()
        
            del tokuisaki[0:2]

            self.closeDate = {}
            for line in tokuisaki:
                if line[0] >= 'T6000':
                    break
                else:
                    self.closeDate[line[0]] = line[8]


        #self.closeDate : {'T1060':'31', 'T1070':'20' .......}


    def get_closeDate(self, df_row):
        
        tokuisakiCode = df_row['得意先コード']
        syukkabi = str(df_row['出荷予定日'])
        nouki = str(df_row['納期'])


        syukkabi_Y = syukkabi[0:4] #出荷日の年 string
        syukkabi_M = syukkabi[4:6] #出荷日の月 string
        syukkabi_D = syukkabi[6:]  #出荷日の日 string

        # nouki_M = nouki.split('/')[0]  #納期の月 string
        # nouki_D = nouki.split('/')[1]  #納期の日 string
        nouki_M = nouki[4:6]
        nouki_D = nouki[6:]
        nouki_Y = nouki[:4]

        '''
        #nouki_Yを求める
        if int(syukkabi_M) == 12 and int(nouki_M) == 1:
            nouki_Y = str(int(syukkabi_Y) + 1)
        else:
            nouki_Y = syukkabi_Y
        '''

        # 出荷日と納期の年月日を求める 
        syukkabi_YMD = syukkabi_Y + '/' + syukkabi_M + '/' + syukkabi_D
        nouki_YMD = nouki_Y + '/' + nouki_M + '/' + nouki_D
        nouki = datetime.strptime(nouki_YMD, '%Y/%m/%d')
        nouki_YMD = nouki.strftime('%Y/%m/%d')  # nouki_YMDを　**/**/** にする


        close_D = self.closeDate[tokuisakiCode]  #締めの日


        # nouki は　datetaime 
        if close_D == '31':  #締めが31なら納期の月の末尾
            close = (nouki + relativedelta(months=1)).replace(day=1)  \
            - timedelta(days=1)
        elif close_D == '1':  #締めが1日なら、
            if nouki_D =='1':
                close = nouki  #納期が1日なら、納期と同じ日、
            else:                   #それ以外は、納期の翌月の1日
                close = (nouki + relativedelta(months=1)).replace(day=1) 
        else: 
            #締めが1日でも31日でもない場合は、
            #締め日が納期日以上だったら、納期の月の締め日、
            if int(close_D) - int(nouki_D) >= 0 :  
                close = nouki.replace(day= int(close_D))
            else:
                #締め日の方が小さかったら、納期の翌月の締め日。                                   
                close = (nouki + relativedelta(months=1)).replace(day= int(close_D))
                
        week = datetime.strptime(nouki_YMD, '%Y/%m/%d').weekday()
        w_list = ['月','火','水','木','金','土','日']
        weekDay = w_list[week]
        close = close.strftime('%Y/%m/%d')

        return pd.Series([syukkabi_YMD, nouki_YMD, weekDay, close])



    def get_jikai(self, df_row):
        
        tokuisakiCode = df_row['得意先コード']
        syukkabi_YMD = str(df_row['出荷予定日'])
        closeDate_YMD = df_row['closeDate']
        syukkaYoteiSouko = []


        syukkabi_Y = syukkabi_YMD.split('/')[0] #出荷日の年 string
        syukkabi_M = syukkabi_YMD.split('/')[1] #出荷日の月 string
        syukkabi_D = syukkabi_YMD.split('/')[2]   #出荷日の日 string


        close_D = self.closeDate[tokuisakiCode]  #締めの日


        
        closeDate = datetime.strptime(closeDate_YMD, '%Y/%m/%d')
        syukkabi = datetime.strptime(syukkabi_YMD, '%Y/%m/%d')
        if close_D == '31':  #締めが31なら出荷日の月の末尾
            effit_close = (syukkabi + relativedelta(months=1)).replace(day=1)  \
            - timedelta(days=1)
        elif close_D == '1':  #締めが1日なら、
            if syukkabi_D =='1':
                effit_close = syukkabi  #出荷日が1日なら、出荷日と同じ日、
            else:                   #それ以外は、出荷日の翌月の1日
                effit_close = (syukkabi + relativedelta(months=1)).replace(day=1) 
        else: 
            #締めが1日でも31日でもない場合は、
            #締め日が出荷日以上だったら、 出荷日の月の締め日、
            if int(close_D) - int(syukkabi_D) >= 0 :  
                effit_close = syukkabi.replace(day= int(close_D))
            else:
                #締め日の方が小さかったら、出荷日の翌月の締め日。                                   
                effit_close = (syukkabi + relativedelta(months=1)).replace(day= int(close_D))
                

        # data.pickleからﾀﾞｳﾝﾛｰﾄﾞ>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        with open(r'./data.pickle', 'rb') as f:
            data_loaded = pickle.load(f)

        
        # close_dateを変更しないリスト（スタンレー得意先コード）
        nonChange_list = data_loaded['nonChange_list'] 
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # 請求予定日  
        # 得意先がスタンレーの場合はclose_dateは変更しない
        # closeDateがeffit_closeと一致しない且つnonchange_listに載っていなかったら
        # 「次」を記載する
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        if closeDate != effit_close and tokuisakiCode not in nonChange_list:
            syukkaYoteiSouko.append('次')




        return syukkaYoteiSouko


