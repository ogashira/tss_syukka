import csv
import platform
from  datetime import date, timedelta
import warnings
import pandas as pd
from typing import List, Any, Tuple
from abc import ABC, abstractmethod

warnings.filterwarnings('ignore', category=UserWarning)

class IFetchDataForList(ABC):

    @abstractmethod
    def fetch_data(self)-> Tuple[List[str],List[List[Any]]]:
        pass


class FetchUriageSumi(IFetchDataForList):

    def __init__(self, cnxn, syukka_date:str) -> None:
        self.cnxn = cnxn
        self._syukka_date = "'" + syukka_date + "'"
        

    def fetch_data(self) -> Tuple[List[str],List[List[Any]]]:

        cursor = self.cnxn.cursor()

        sqlQuery = ("SELECT RURIDT.RurTokCD AS '得意先コード',"
                    " RURIDT.RurNonyuCD AS '納入先コード',"
                    " RURIHD.RurUnsCD AS 'unsou_code',"
                    " MA_UNS.AitNam1 AS 'unsou',"
                    " RURIDT.RurFreeKBN1 AS 'kubun_no',"
                    " KBN.KbnNam AS 'kubun',"
                    " RURIDT.RurUriDay AS '出荷予定日',"
                    " RURIDT.RurHinCD AS 'hinban',"
                    " RURIDT.RurHinNam AS '品名',"
                    " RURMEI_U2002.RmeLotNo AS 'lot',"
                    " RURMEI_U2002.RmeMSu AS 'cans',"
                    " RURIDT.RurKoSuUp AS '受注数量',"    # <- これが違う
                    " RURIDT.RurKanriTniCD AS '受注単位',"
                    " RURIHD.RurNonyuNam1 AS '納入先名称１',"
                    " RURIDT.RurCMNo AS '得意先注文ＮＯ',"
                    " RURIDT.RurMBiko AS '備考',"
                    " RURMEI.RmeKojFrom AS 'factory_name',"
                    " MA_NONYU.AitRyaku AS '納入先名'"
                    " From dbo.RURIDT"
                    " JOIN dbo.RURMEI"
                    " ON RURIDT.RurUNo = RURMEI.RmeUNo" 
                    " AND RURIDT.RurUGNo = RURMEI.RmeUGNo"
                    " JOIN dbo.RURIHD"
                    " ON RURIDT.RurUNo = RURIHD.RurUNo"
                    " LEFT JOIN dbo.RURMEI_U2002"
                    " ON RURIDT.RurUNo = RURMEI_U2002.RmeUNo"
                    " AND RURIDT.RurUGNo = RURMEI_U2002.RmeUGNo"
                    " AND RURMEI.RmeSeqNo = RURMEI_U2002.RmeSeqNo"
                    " LEFT JOIN dbo.MAITEM AS MA_NONYU"
                    " ON RURIDT.RurTokCD = MA_NONYU.AitCD1"
                    " AND RURIDT.RurNonyuCD = MA_NONYU.AitCD2"
                    " LEFT JOIN(" 
                        " SELECT MAITEM.AitCD1, MAITEM.AitNam1" 
                        " FROM dbo.MAITEM"
                        " WHERE MAITEM.AitAitKBN = 'A'"
                    ")MA_UNS ON RURIHD.RurUnsCD = MA_UNS.AitCD1"
                    " LEFT JOIN("
                        " SELECT MKUBUN.KbnCD, MKUBUN.KbnNam"  
                        " FROM dbo.MKUBUN"
                        " WHERE MKUBUN.KbnKBN = 'V'"
                    ")KBN ON RURIDT.RurFreeKBN1 = KBN.KbnCD"
                    " WHERE RURIDT.RurUriDay =" + self._syukka_date +
                    " AND RURIDT.RurTokCD < 'T6000'"
                    " ORDER BY RURIDT.RurUNo, RURIDT.RurUGNo"
                    )

        data_list: List[List[Any]] = []
        cursor.execute(sqlQuery)

        # 1. カラム名を取得（リスト内包表記）
        # cursor.description は (名前, 型, 表示サイズ, ...) というタプルのリスト
        columns = [column[0] for column in cursor.description]

        # 4. 2次元リストへ変換
        # fetchall() はタプルのリストを返すため、リスト内包表記で各行をリスト化します
        try:
            data_list = [list(row) for row in cursor.fetchall()]
        except Exception:
            print(f'データベースfetch中に予期せぬエラーです fetch_hinban')
        finally:
            cursor.close()
            # cnxnは呼び出しもとでクローズ


        return columns, data_list


class FetchUnsoutaiouToke(IFetchDataForList):

    def __init__(self) -> None:
        pass
        

    def fetch_data(self) -> Tuple[List[str],List[List[Any]]]:
        
        path = r'//192.168.1.247/共有/経理課ﾌｫﾙﾀﾞ/運賃計算関係/unsoutaiou_toke.csv'
        if platform.system() == 'Linux':
            path = r'/mnt/public/経理課ﾌｫﾙﾀﾞ/運賃計算関係/unsoutaiou_toke.csv'
        data = []
        try:
            with open(path, 'r', encoding='cp932') as f: 
                reader = csv.reader(f)
                data = [row for row in reader]
        except Exception as e:
            print('unsoutaiou_tokeのfetchに失敗です')
            print(e)

        columns = data[0]
        data_list = data[1:]
            

        return columns, data_list
