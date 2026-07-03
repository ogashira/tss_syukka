from typing import List, Dict, Any, Tuple, Set
from get_idx import GetIdx

class CreateDictFromList:
    def __init__(self)-> None:
        pass

    def _list_to_dict_tuple_int(self,
                        unsoutaiou_data: List[List[Any]],
                        unsoutaiou_col: List[str], 
                        toValueCol: str)-> Dict[Tuple,int]:
        '''
        toValueCol : 'isExport' or 'leadTime' 辞書のvalueにする列
        unsoutaiou_dataはeffitA.MDESTN_U2002からfetchしたデータ。
        昔はunsoutaiou_toke.csvを使っていた。その名残で、データが無い場合は
        ''(空文字）であった。MDESTN_U2002になって、''(空文字)か ' '(半角スペース)か
        わからないので、昔のままで、' 'だったら''に変換しておく
        '''

        # 得意先コードと納入先コードのインデックスを求めておく
        value_idx: int = GetIdx.get_idx(unsoutaiou_col, toValueCol)
        tokui_idx: int = GetIdx.get_idx(unsoutaiou_col, 'tokuiCD')
        nonyu_idx: int = GetIdx.get_idx(unsoutaiou_col, 'nonyuCD')

        # get_idxで-1が返ったらNG
        if value_idx == -1 or tokui_idx == -1 or nonyu_idx == -1:
            raise IndexError(f'カラムに{toValueCol}、tokuiCD、nonyuCDがありません')

        dict_tuple_int: Dict[Tuple, int] = {}
        for line in unsoutaiou_data:
            nonyu_cd = line[nonyu_idx]
            if nonyu_cd == ' ':  # 半角スペースは空文字に変換
                nonyu_cd = ''

            tokui_nonyu_tpl: Tuple = (line[tokui_idx], nonyu_cd)
            dict_tuple_int[tokui_nonyu_tpl] = line[value_idx]

        return dict_tuple_int


    def create_yusyutuDict(self, 
                        unsoutaiou_data: List[List[Any]],
                        unsoutaiou_col: List[str], 
                        toValueCol: str)-> Dict[Tuple,str]:

        yusyutu_dict_int: Dict[Tuple,int] = self._list_to_dict_tuple_int(
                                 unsoutaiou_data, unsoutaiou_col, toValueCol)
        # yusyutu_dict_intのvalue: 1 or 0 を　'y' or '' にする

        yusyutu_dict: Dict[Tuple,str] = {}
        for k, v in yusyutu_dict_int.items():
            if v == 0:   # 0 or 1
                is_export = ''
            else:
                is_export = 'y'
            yusyutu_dict[k] = is_export


        return yusyutu_dict


    def create_leadTimeDict(self, 
                        unsoutaiou_data: List[List[Any]],
                        unsoutaiou_col: List[str],
                        toValueCol: str)-> Dict[Tuple,int]:

        leadTime_dict: Dict[Tuple, int] = self._list_to_dict_tuple_int(
                                 unsoutaiou_data, unsoutaiou_col, toValueCol)
        return leadTime_dict


    def create_dicts_from_colAndList(self, col: List[str], 
                              data: List[List[Any]],
                              )-> List[Dict[str, Any]]:
        '''
        カラム名と２次元リストから複数辞書を作ってリストにする。
        '''

        list_dict: List[Dict[str,Any]] = []
        for line in data:
            inner_dict = dict(zip(col, line))
            list_dict.append(inner_dict)

        return list_dict

        
    def create_dict_from_list(self, col: List[str], 
                              data: List[List[Any]],
                              key_name: str,
                              val_name: str
                              )-> Dict[str, Any]:
        '''
        ２次元リストから辞書を作ってリストにする。
        '''

        key_idx: int = GetIdx.get_idx(col, key_name)
        val_idx: int = GetIdx.get_idx(col, val_name)
        # get_idxで-1が返ったらNG
        if key_idx == -1 or val_idx == -1:
            raise IndexError('create_dict_from_list GetIdx == -1 が返りました。'
                                                          '処理を中止します。')

        list_dict: Dict[str,Any] = {} 
        for line in data:
            list_dict[line[key_idx]] = line[val_idx]

        return list_dict

        
    def create_dict_from_set(self, col: List[str], 
                    data: Set[Tuple[str]])-> List[Dict[str, str]]:
        '''
        カラム名とタプルのセットから複数辞書を作ってリストにする。
        col = ['unsou_code','kubun','yusyutu']
        data = {('U0007',1,'y'), ('U0001',1,'y'),('U0001',1,'').....}
        ↑タプルのセット
        output = [{'unsou_code':'U0007','kubun':1,'yusyutu':'y'},{.........},...]
        '''

        list_dict: List[Dict[str,str]] = []
        for line in data:
            inner_dict = dict(zip(col, line))
            list_dict.append(inner_dict)

        return list_dict


    def create_list_YMD(self, calenderCol: List[str], 
                calenderData: List[List[str]], YYYYMM: str, DD: str) -> List[str]:
        '''
        calenderData = [['202606','01','月',' '], ['202606','02','火',' '],..]   
        return = ['20260601', '20260602', ......]
        '''
        idx_YYYYMM = GetIdx.get_idx(calenderCol, YYYYMM)
        idx_DD = GetIdx.get_idx(calenderCol, DD)
        list_YMD:List[str] = []
        for line in calenderData:
            list_YMD.append(f'{line[idx_YYYYMM]}{line[idx_DD]}')

        return list_YMD


    def create_YMD_holiday(self, calenderCol: List[str], 
                           calenderData: List[List[str]], YYYYMM: str, 
                           DD: str, holiday: str)-> Dict[str, str]:
        '''
        calenderData = [['202606','01','月',' '], ['202606','02','火',' '],..]   
        return = {'20260601': ' ', '20260602': '1', ......}
        '''
        idx_YYYYMM = GetIdx.get_idx(calenderCol, YYYYMM)
        idx_DD = GetIdx.get_idx(calenderCol, DD)
        idx_holi = GetIdx.get_idx(calenderCol, holiday)
        dict_YMD_holiday = {}
        for line in calenderData:
            k:str = f'{line[idx_YYYYMM]}{line[idx_DD]}'
            dict_YMD_holiday[k] = line[idx_holi]

        return dict_YMD_holiday



        



