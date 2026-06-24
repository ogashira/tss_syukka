#! python
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
import pandas as pd
import os
import platform


class LeadTime(object):

    def __init__(self):

        # 配達日数ﾃﾞｰﾀの取得
        pf = platform.system()
        if pf == 'Windows':
            mypath = (
                r'//192.168.1.247/共有/受注check/master/order_nounyuusaki.csv'
            )
        elif pf == 'Linux':
            mypath = r'/mnt/public/受注check/master/order_nounyuusaki.csv'
        else:
            mypath = r'../master/selfMade/order_nounyuusaki.csv'

        nounyuusaki_file = open(mypath, encoding = 'cp932')

        file_reader = csv.reader(nounyuusaki_file)
        nounyuusaki_l = list(file_reader)
        nounyuusaki_file.close()


        #二次元ﾘｽﾄにする
        self.nounyuusaki = []
        for row in nounyuusaki_l:
            rows = []
            rows.append(row[0])       # 得意先コード
            if row[1]=='' or row[1] is None:
                rows.append('')  # 納入先コード空白は''にする
            else:
                rows.append(row[1])       # 納入先コード
            rows.append(row[3])       # 配達日数
            rows.append(row[5])       # 納入先名称
            self.nounyuusaki.append(rows)
            

        # 0列:年月日,1列:東洋休日, 2列:運送屋休日
        if pf == 'Windows':
            mypath = r'//192.168.1.247/共有/受注check/master/order_holiday.csv'
        elif pf == 'Linux':
            mypath = r'/mnt/public/受注check/master/order_holiday.csv'
        else:
            mypath = r'../master/selfMade/order_holiday.csv'

        eigyou_file = open(mypath, encoding = 'cp932')
        
        nounyuusaki_file = open(mypath, encoding = 'cp932')

        file_reader = csv.reader(eigyou_file)
        header = next(file_reader)
        self.unsou_eigyoubi = list(file_reader)
        eigyou_file.close()


        # **/**/** の形にする
        for row in self.unsou_eigyoubi:
            time_data = datetime.strptime(row[0], '%Y/%m/%d')
            row[0] = time_data.strftime('%Y/%m/%d') 
            del row[1]  # ２列目の曜日は削除する。




    def get_youbi(self, df_row):

        tokui_code = df_row['得意先コード']
        nounyuu_code = df_row['納入先コード']
        syukkabi = df_row['出荷予定日']
        nouki = df_row['納期']
        syukkayotei = df_row['出荷予定倉庫']


        # 配達日数を求める
        nissuu = 0
        for line in self.nounyuusaki:
            if (
            line[0] == tokui_code  and line[1] == nounyuu_code
            ) or (
            line[0] == tokui_code and line[1] == '' and pd.isnull(nounyuu_code)
            ):
                nissuu = int(line[2])

        # 納期から遡って出荷日を求める。
        # 運送屋休日は配達日数に数えない。出荷日が東洋休日だったら遡って東洋営業日まで
        # 戻る。出荷日が出荷予定日よりも後（大きい）だったら「曜日違い」とする。
        # 0列:年月日,1列:東洋休日, 2列:運送屋休日


        '''unsou_eigyoubi
        [['2026/01/01', '休', '休'], ['2026/01/02', '休', '休'], .......]
        '''


        for i in range(len(self.unsou_eigyoubi)):
            if self.unsou_eigyoubi[i][0]== syukkabi:
                syukka_idx = i                          #出荷日予定日のindex
            if self.unsou_eigyoubi[i][0] == nouki:
                nouki_idx = i                           #納期のindex
                break
                

        while nissuu > 0 :
            if self.unsou_eigyoubi[nouki_idx - 1][2] == '休':
                nouki_idx -= 1
            else:
                nouki_idx -= 1
                nissuu -= 1
        while self.unsou_eigyoubi[nouki_idx][1] == '休' or self.unsou_eigyoubi[nouki_idx][2] == '休':
                nouki_idx -= 1

        calc_syukka_idx = nouki_idx               #納期から計算した出荷すべき日のidx


        if syukka_idx < calc_syukka_idx :
            syukkayotei.append('曜日')

        return syukkayotei
        




        

