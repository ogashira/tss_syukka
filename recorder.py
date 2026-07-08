import os
import unicodedata
from decimal import Decimal
from typing import List, Any


class Recorder(object):

    def __init__ (self, mydir: str)-> None:
        self._path = os.path.join(mydir, "log.txt")

        
    def out_log (self, txt, rtn=''):
        print('{}{}'.format(txt, rtn))


    def out_log_df(self, df, title:str):
        print(title)
        print(df)

        
    def out_file (self, txt, rtn=''):

        with open(self._path, 'a') as f:
            print('{}{}'.format(txt, rtn), file = f)


    def out_file_from_list(self, list:List[str], title:str)-> None:
        '''
        一次元リストからファイルに出力する
        １要素、１行ずつ表示する
        '''
        # (リスト)の中身を全て文字列に変換する
        list_str = [str(item) for item in list]
        txt = '\n'.join(list_str)

        with open(self._path, 'a') as f:
            print(f'\n{title}\n{txt}\n', file = f)
        

    def out_file_from_list_list(self, lists:List[List], title:str)-> None:
        '''
        二次元リストをファイルに出力する。
        innerリストはカンマ区切りで、１行ずつ表示する
        '''
        row_txts:List = [] 
        for list in lists:
            # (リスト)の中身を全て文字列に変換する
            list_str = [str(item) for item in list]
            row_txt = ','.join(list_str)
            row_txts.append(row_txt)
                
        txt = '\n'.join(row_txts)
        with open(self._path, 'a') as f:
            print(f'\n{title}\n{txt}', file = f)


    def out_txt_from_list_list(self, lists:List[List])-> str:
        '''
        二次元リストをファイルに出力する。
        innerリストはカンマ区切りで、１行ずつ表示する
        '''
        row_txts:List = [] 
        for list in lists:
            # (リスト)の中身を全て文字列に変換する
            list_str = [str(item) for item in list]
            row_txt = ','.join(list_str)
            row_txts.append(row_txt)
                
        txt = '\n'.join(row_txts)

        return txt


    def out_csv (self, df, filePath):
        df.to_csv(filePath, encoding='cp932')



    def _get_east_asian_width(self, text):
        """文字列の表示幅（半角=1、全角=2）を計算する"""
        return sum(2 if unicodedata.east_asian_width(c) in "FWA" else 1 for c in str(text))

    def _pad_text(self, text, width, align="left"):
        """全角半角を考慮して、指定された表示幅になるようスペースで埋める"""
        if type(text)== Decimal:
            text_str = str(float(text))
        else:
            text_str = str(text)
        current_width = self._get_east_asian_width(text_str)
        pad_size = max(0, width - current_width) # 不足している幅（スペースの数）
        
        if align == "right":
            return " " * pad_size + text_str
        else:
            return text_str + " " * pad_size

    def outLogFile_to_sameNumberOfChara(self, cols: List[str], 
                                        data: List[List[Any]])-> None:

        col_widths = [12, 8, 8, 8, 20, 9, 9]
        txt = ''

        #txt += f'{col[0]:<12} | {col[1]:<8} | {col[2]:<8} | {col[3]:<8} | {col[4]:<20} | {col[5]:>6} | {col[6]:>6}\n'
        txt += " | ".join(self._pad_text(col, width) for col, width in zip(cols, col_widths))
        txt += " | "
        txt += "\n"
        
        for row in data:

            txt += " | ".join(self._pad_text(item, width) for item, width in zip(row, col_widths))
            txt += " | "
            txt += "\n"
        
        self.out_log(txt, '\n')
        self.out_file(txt, '\n')

        
