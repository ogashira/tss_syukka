from __future__ import annotations 
'''
全ての型ヒントの判定を遅延評価する。UriageForPacking自信のクラス名を型ヒントとして
使っているので、エラーを出さないため。 61行目
'''
from typing import Dict, Any, Tuple, Set, List

class UriageForPacking:
    def __init__(self, dict_data: Dict[str,Any], yusyutu_dict: Dict):

        #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        self._yusyutu_dict = yusyutu_dict
        self._factory: str = dict_data['factory_name']
        self._依頼先: str = dict_data['依頼先']
        self._得意先コード: str = dict_data['得意先コード']
        self._納入先コード: str = dict_data['納入先コード']
        self._納入先名称１: str = dict_data['納入先名称１']
        self._品名: str = dict_data['品名']
        self._得意先注文ＮＯ: str = dict_data['得意先注文ＮＯ']
        self._備考: str = dict_data['備考']
        self._納期: str = dict_data['納期']
        self._出荷: str = "土気出荷"                     # 土気出荷、本社出荷
        self._受注数量: int = dict_data['uriKosu']
        self._受注単位: str = dict_data['受注単位']
        self._add: int = 1
        self._振替元数量: int = dict_data['motoSu']
        self._売り金額: int = dict_data['uriKin']
        self._売り単価: int = dict_data['uriTnk']
        self._輸出向先: str = self._calc_yusyutu_mukesaki()
        self._cans: int = self._calc_cans()

    def _calc_cans(self)-> int:
        if self._受注単位 != 'CN':
            return self._振替元数量
        return self._受注数量

    def _calc_yusyutu_mukesaki(self)-> str:
        yusyutu_mukesaki = ''
        nonyu_code = self._納入先コード
        # effitからfetchした納入先コードが' 'の場合は''にする
        # unsoutaiouでーたは''なので。
        if nonyu_code ==  ' ':
            nonyu_code = ''
        tmpTuple = (self._得意先コード, nonyu_code)
        yusyutu_mukesaki = self._yusyutu_dict[tmpTuple]

        return yusyutu_mukesaki

    def create_setPacking(self, setPacking: Set[Tuple]) -> None:
        tmpTuple: Tuple = ()
        if self._輸出向先 == 'y':
            tmpTuple = (self._得意先コード, self._納入先コード, 
                        self._得意先注文ＮＯ)
            setPacking.add(tmpTuple)
            return
        tmpTuple = (self._得意先コード, self._納入先コード)
        setPacking.add(tmpTuple)


    def add_packingDict_myself(self, packing: Tuple[str,...], 
                packingDict:Dict[Tuple[str,...], List[UriageForPacking]])-> None:
        '''
        packing -> ('T1210', 'IDK05', 'IDC4446') や、 ('T3820', ' ')など...
        '''

        if len(packing) == 3:
            if (packing[0] == self._得意先コード 
                and packing[1] == self._納入先コード 
                and packing[2] == self._得意先注文ＮＯ):
                if packing not in packingDict:
                    packingDict[packing] = [self]
                else:
                    packingDict[packing].append(self)


        if len(packing) == 2:
            if (packing[0] == self._得意先コード 
                and packing[1] == self._納入先コード):
                if packing not in packingDict:
                    packingDict[packing] = [self]
                else:
                    packingDict[packing].append(self)

        
        


    def add_packing_myself(self, dic_list: List[Dict[str, Any]])->None:
        tmp_dict = {
                '依頼先':         self._依頼先,
                'cans':           self._cans,
                '総重量':         240,
                '得意先コード':   self._得意先コード,
                '納入先コード':   self._納入先コード,
                '納入先名称１':   self._納入先名称１,
                '品名':           self._品名,
                '得意先注文ＮＯ': self._得意先注文ＮＯ,
                '備考':           self._備考,
                '納期':           self._納期,
                '出荷':           self._出荷,
                '出荷予定倉庫':   [], 
                'add':            self._add
                }
        dic_list.append(tmp_dict)


