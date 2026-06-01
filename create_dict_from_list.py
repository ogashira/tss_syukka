from typing import List, Dict, Any, Tuple, Set
from get_idx import GetIdx

class CreateDictFromList:
    def __init__(self)-> None:
        pass

    def create_yusyutuDict(self, 
                        unsoutaiou_data: List[List[Any]],
                        unsoutaiou_col: List[str])-> Dict[Tuple,str]:


        # 得意先コードと納入先コードのインデックスを求めておく
        yusyutu_dist_idx: int = GetIdx.get_idx(unsoutaiou_col, '輸出向先')
        tokui_idx: int = GetIdx.get_idx(unsoutaiou_col, '得意先コード')
        nonyu_idx: int = GetIdx.get_idx(unsoutaiou_col, '納入先コード')

        # get_idxで-1が返ったらNG
        if yusyutu_dist_idx == -1 or tokui_idx == -1 or nonyu_idx == -1:
            raise IndexError('カラムに輸出向先、得意先コード、納入先コードがありません')

        # yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        yusyutu_dict: Dict[Tuple,str] = {}
        for line in unsoutaiou_data:
            tokui_nonyu_tpl: Tuple = (line[tokui_idx], line[nonyu_idx])
            yusyutu_dict[tokui_nonyu_tpl] = line[yusyutu_dist_idx]

        return yusyutu_dict


    def create_dict_from_list(self, col: List[str], 
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
