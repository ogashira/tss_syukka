import os
from typing import List


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
