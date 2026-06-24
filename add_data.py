#! python
# -*- coding: utf-8 -*-

import openpyxl
import pandas as pd
import os
import platform


class AddData(object):

    def __init__(self):

    #成績表、指定伝票ﾃﾞｰﾀの取得
        pf = platform.system()
        if pf == 'Windows':
            mypath = r'//192.168.1.247/共有/営業課ﾌｫﾙﾀﾞ/櫻田/☆☆☆/売上処理(水野課長用)/' \
                     r'出荷時添付リスト(20200731時点最新版).xlsx'
        elif pf == 'Linux':
            mypath = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/櫻田/☆☆☆/売上処理(水野課長用)/' \
                     r'出荷時添付リスト(20200731時点最新版).xlsx'
        else:
            mypath = r'../master/出荷時添付リスト(20200731時点最新版).xlsx'
            
        wb = openpyxl.load_workbook(mypath, data_only=True)

        ws = wb['成績表']
        
        #二次元ﾘｽﾄにする
        self.coa_list = []
        for row in ws.rows:
            rows = []
            for cell in row:
                if cell.value is None:
                    cell.value = ''
                rows.append(cell.value)
            self.coa_list.append(rows)
        

        ws = wb['指定伝票']
        
        #二次元ﾘｽﾄにする
        self.sitei_denpyou = []
        for row in ws.rows:
            rows = []
            for cell in row:
                if cell.value is None:
                    cell.value = ''
                rows.append(cell.value)
            self.sitei_denpyou.append(rows)


    def get_coa(self, df_row):
        tokui_code = df_row['得意先コード']
        nounyuu_code = df_row['納入先コード']
        hinban =  df_row['hinban']

        if pd.isnull(nounyuu_code):
            nounyuu_code = None

        yoteisouko_list = df_row['出荷予定倉庫']

        for line in self.coa_list:
            if tokui_code == line[0] and nounyuu_code == line[1] and hinban == line[3]:
                yoteisouko_list.append('成')
                break


        for line in self.sitei_denpyou:
            if tokui_code == line[0] and nounyuu_code == line[1]:
                yoteisouko_list.append('指')
                break


        return yoteisouko_list

