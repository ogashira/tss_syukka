from typing import Dict, Any, Tuple, Set, List

class UriageForSyukkaJisseki:
    def __init__(self, dict_data: Dict[str,Any], yusyutu_dict: Dict):

        #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        self._yusyutu_dict = yusyutu_dict
        self._factory: str = dict_data['factory_name']
        self._得意先コード: str = dict_data['得意先コード']
        self._納入先コード: str = dict_data['納入先コード']
        self._unsou_code: str = dict_data['unsou_code'] 
        self._unsou: str = dict_data['unsou']
        self._kubun_no: str = dict_data['kubun_no']
        self._kubun: str = dict_data['kubun']
        self._出荷予定日: str = dict_data['出荷予定日']
        self._hinban: str = dict_data['hinban']
        self._品名: str = dict_data['品名']
        self._lot: str = dict_data['lot']
        self._受注数量: int = dict_data['受注数量']
        self._受注単位: str = dict_data['受注単位']
        self._納入先名称１: str = dict_data['納入先名称１']
        self._得意先注文ＮＯ: str = dict_data['得意先注文ＮＯ']
        self._備考: str = dict_data['備考']
        self._add: int = 1
        self._納入先名: str = dict_data['納入先名']
        self._振替元数量: int = dict_data['振替元数量']
        self._cans: int = self._calc_cans()
        self._輸出向先: str = self._calc_yusyutu_mukesaki()

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

    def add_sumiData_myself(self, dic_list: List[Dict[str, Any]])->None:
        tmp_dict = {
                '得意先コード':     self._得意先コード,
                '納入先コード':     self._納入先コード,
                'unsou_code':       self._unsou_code, 
                'unsou':            self._unsou,
                'kubun_no':         self._kubun_no,
                'kubun':            self._kubun,
                '出荷予定日':       self._出荷予定日, 
                'hinban':           self._hinban,
                '品名':             self._品名,
                'lot':              self._lot,
                'cans':             self._cans,
                '受注数量':         self._受注数量,
                '受注単位':         self._受注単位,
                '納入先名称１':     self._納入先名称１,
                '輸出向先':         self._輸出向先,
                '得意先注文ＮＯ':   self._得意先注文ＮＯ,
                '備考':             self._備考,
                'add':              self._add,
                '納入先名':         self._納入先名
                }
        dic_list.append(tmp_dict)


    def add_unsouSet_myself(self, unsouSet:Set[Tuple])-> None:
        '''
        unsouSetにデータがなければ、出荷実績照会はつくられない。
        unosu_codeが無い、東新油脂向けや、メーカー直送(PI-301など)はunsou_code = ' 'なので、
        出荷実績照会はつくられない
        '''
        if self._unsou_code == ' ': #運送屋がなければunsouSetはつくらない
            return
        tmpTuple = (self._unsou_code, self._kubun_no, self._輸出向先)
        unsouSet.add(tmpTuple)

