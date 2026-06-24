#! python
# -*- coding: utf-8 -*-

import pprint
import pandas as pd
import warnings
from sql_server import SqlServer
from typing import cast

warnings.filterwarnings('ignore', category=UserWarning)




class SqlQuery(object):

    def __init__(self, uriagebi, sengetu):

        self.uriagebi = uriagebi
        self.sengetu = sengetu

        
    # 2021/2/26変換できない文字ℓなどをテキストﾌｧｲﾙなどに書き込むときに
    # エラーが出て半日悩んだ。この関数で変換できない文字を？に変換して解決。
    # 変換できない文字を無視する場合は、
    # replaceの代わりにignoreを使う
    def henkan(self, str_text):
        if type(str_text) == str:
            str_text = str_text.encode('cp932','replace')
            #このままだと出力時に\x90D\x93cのようになって読めないので直す
            str_text = str_text.decode('cp932')
        return str_text



    def get_untin_keisan_sheet(self) -> pd.DataFrame:
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()
        

        # cursor = cnxn.cursor()

        sqlQuery = ("SELECT RJYUCD.RjcTokCD, RJYUCD.RjcNonyuCD, RJYUCH.RjcTokNam1," 
                    " RJYUCH.RjcNonyuNam1, RJYUCH.RjcNonyuNam2, RJYUCD.RjcSKDay,"
                    " RJYUCD.RjcHinCD, RJYUCD.RjcHinNam, RJYUCD.RjcJcSu, RJYUCD.RjcTniCD,"
                    " RJYUCD.RjcCMNo, RJYUCD.RjcJCNo, RJYUCD.RjcJGNo, RJYUCD.RjcMBiko,"
                    " RJYUCD.RjcSokoCD, RJYUCH.RjcHBiko, RJYUCD.RjcNODay"
                    " From dbo.RJYUCD"
                    " LEFT JOIN dbo.RJYUCH"
                    " ON RJYUCD.RjcJCNo = RJYUCH.RjcJCNo"
                    " WHERE RJYUCD.RjcSKDay =" + self.uriagebi)
        df: pd.DataFrame = pd.read_sql(sqlQuery, cnxn)
        df = df.rename(columns={'RjcTokCD': '得意先コード', 'RjcNonyuCD': '納入先コード', 
                                'RjcTokNam1': '得意先名称１','RjcNonyuNam1': '納入先名称１', 
                                'RjcNonyuNam2': '納入先名称２', 'RjcSKDay': '出荷予定日', 
                                'RjcHinCD': '品番', 'RjcHinNam':'品名', 'RjcJcSu':'受注数量', 
                                'RjcTniCD':'受注単位','RjcCMNo': '得意先注文ＮＯ', 
                                'RjcJCNo': '受注ＮＯ', 'RjcJGNo': '受注行ＮＯ', 
                                'RjcMBiko': '備考', 'RjcSokoCD': '出荷予定倉庫', 
                                'RjcHBiko': '備考.1', 'RjcNODay': '納期'})
        df = df.sort_values(['得意先コード','納入先コード'])
        df = df.reset_index(drop = True)

        sql_server.close()

        # henkanに渡して、変換できない文字ℓなどを？に変換する。    
        #df = df.applymap(self.henkan) applymapは廃止される予定なので変更
        df = cast(pd.DataFrame, df.apply(lambda col: col.map(self.henkan), axis=0))


        return df



    def get_uriage_sumi(self):
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()


        sqlQuery = ("SELECT RURIDT.RurUNo, RURIDT.RurUGNo, RuRMEI.RmeSeqNo," 
                    " RURIDT.RurUriDay, RURIDT.RurToriKBN, RURIDT.RurTokCD,"
                    " RURIDT.RurNonyuCD, RURIHD.RurUnsCD, RURIDT.RurFreeKBN1,"
                    " RURIDT.RurSeiYMDY, RURMEI.RmeKojFrom, RURMEI.RmeSokoFrom,"
                    " RURIDT.RurJCNo, RURIDT.RurJGNo, RURMEI.RmeHinCD, RURMEI.RmeKoSuUp,"
                    " RURIDT.RurKanriTniCD, RURMEI_U2002.RmeMHinCD, RURMEI_U2002.RmeMSu,"
                    " RURIDT.RurCMNo, RURIDT.RurMBiko, RURMEI.RmeLotNo, RURIDT.RurNODay"
                    " FROM dbo.RURIDT"
                    " LEFT JOIN dbo.RURMEI"
                    " ON RURIDT.RurUNo = RURMEI.RmeUNo AND RURIDT.RurUGNo = RURMEI.RmeUGNo"
                    " LEFT JOIN dbo.RURIHD"
                    " ON RURIDT.RurUNo = RURIHD.RurUNo"
                    " LEFT JOIN dbo.RURMEI_U2002"
                    " ON RURIDT.RurUNo = RURMEI_U2002.RmeUNO"
                    " AND RURIDT.RurUGNo = RURMEI_U2002.RmeUGNo"
                    " AND RURMEI.RmeSeqNo = RURMEI_U2002.RmeSeqNo"
                    " WHERE RURIDT.RurUriDay =" + self.uriagebi)
        df = pd.read_sql(sqlQuery, cnxn)
        df = df.rename(
           columns={
                'RurUNo':'売上ＮＯ', 
                'RurUGNo':'売上行ＮＯ', 
                'RmeSeqNo':'連番', 
                'RurUriDay':'売上日', 
                'RurToriKBN':'取引区分', 
                'RurTokCD':'得意先コード',
                'RurNonyuCD':'納入先コード', 
                'RurUnsCD':'運送業者', 
                'RurFreeKBN1':'自由使用区分１',
                'RurSeiYMDY':'請求予定年月日', 
                'RmeKojFrom':'出庫元事業所コード', 
                'RmeSokoFrom':'出庫元倉庫',
                'RurJCNo':'受注ＮＯ', 
                'RurJGNo':'受注行ＮＯ', 
                'RmeHinCD':'品番', 
                'RmeKoSuUp':'管理個数',
                'RurKanriTniCD':'管理単位', 
                'RmeMHinCD':'振替元品番', 
                'RmeMSu':'振替元数量',
                'RurCMNo':'得意先注文ＮＯ', 
                'RurMBiko':'備考', 
                'RmeLotNo':'ロットＮＯ', 
                'RurNODay':'納期'
            }
        )
        df = df.sort_values(['売上ＮＯ','売上行ＮＯ','連番'])
        df = df.reset_index(drop = True)

        sql_server.close()

        # henkanに渡して、変換できない文字ℓなどを？に変換する。    
        # df = df.applymap(self.henkan)
        df = df.apply(lambda col: col.map(self.henkan))

        return df



    def get_JDT(self):
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()
        

        sqlQuery = ("SELECT LJYUCD.LjcJcDay, LJYUCD.LjcJCNo" 
                    " FROM dbo.LJYUCD"
                    " WHERE LJYUCD.LjcJcDay >=" + self.sengetu +
                    " AND LJYUCD.LjcJcDay <=" + self.uriagebi +
                    " ORDER BY LJYUCD.LjcJcDay")
        df = pd.read_sql(sqlQuery, cnxn)
        df = df.rename(
           columns={
                'LjcJcDay':'受注日', 
                'LjcJCNo':'受注ＮＯ' 
            }
        )
        df = df.sort_values(['受注日','受注ＮＯ'])
        df = df.reset_index(drop = True)

        sql_server.close()

        # henkanに渡して、変換できない文字ℓなどを？に変換する。    
        # df = df.applymap(self.henkan)
        df = df.apply(lambda col: col.map(self.henkan))
        return df



    def get_genzaiko(self):
        
        souko_dic = {'S0001':'本社倉庫', 'S0021':'土気倉庫', 'S0031':'大阪倉庫'}
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()

        sqlQuery = ("SELECT ZaiHinCD AS '品番', ZaiLotNo AS 'ロットNo',"
                    " ZaiZaiSuG AS '在庫数量（現在）', ZaiBuCD AS '倉庫'"
                    " From dbo.BZAIKO"
                    " WHERE (ZaiBuCD = 'S0001'"
                    " OR ZaiBuCD = 'S0021'"
                    " OR ZaiBuCD = 'S0031')"
                    " AND ZaiZaiSuG > 0"
                    )
        df = pd.read_sql(sqlQuery, cnxn)

        # 倉庫名をS0000から本社倉庫などにする
        df['倉庫'] = df['倉庫'].map(souko_dic)

        sql_server.close()
        return df


    def get_tokuisaki_sime(self):
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()
        
        sqlQuery = ("SELECT TokTokCD AS '得意先コード', TokSimD1 AS '締め日１'"
                    " From dbo.MTOKUI"
                    " WHERE TokTokCD < 'T6000'"
                    )
        df = pd.read_sql(sqlQuery, cnxn)

        df = df.sort_values('得意先コード')
        df = df.reset_index(drop = True)


        sql_server.close()
        return df


    def get_hinban(self):
        sql_server:SqlServer = SqlServer()
        cnxn = sql_server.get_cnxn()
        cur = cnxn.cursor()
        
        sqlQuery = ("SELECT HinHinCD, HinRyaku, HinTju"
                    " From dbo.MHINCD"
                    " ORDER BY HinHinCD"
                    )

        cur.execute(sqlQuery)
        
        hinban_list = [list(row) for row in cur.fetchall()]

        sql_server.close()

        return hinban_list



