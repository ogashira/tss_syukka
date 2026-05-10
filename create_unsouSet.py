from typing import List, Dict, Any, Tuple, Set
import json
from decimal import Decimal


class CreateUnsouSet:
    def __init__(self)-> None:
        pass


    def create_unsouSet(self, sumi_data: List[List[Any]],
                        sumi_col: List[str],
                        unsoutaiou_data: List[List[Any]],
                        unsoutaiou_col: List[str])-> Set[Tuple]:

        def get_idx(col: List[str], col_name: str)-> int:
            idx: int = -1
            if not col:
                return idx
            if not col_name:
                return idx

            for i, code in enumerate(col):
                if code == col_name:
                    idx = i
                    break
            else:
                idx = -1
            
            return idx


        def create_yusyutu_dict(unsoutaiou_data, unsoutaiou_col)-> Dict[Tuple,str]:

            # 得意先コードと納入先コードのインデックスを求めておく
            yusyutu_dist_idx: int = get_idx(unsoutaiou_col, '輸出向先')
            tokui_idx: int = get_idx(unsoutaiou_col, '得意先コード')
            nonyu_idx: int = get_idx(unsoutaiou_col, '納入先コード')

            # get_idxで-1が返ったらNG
            if yusyutu_dist_idx == -1 or tokui_idx == -1 or nonyu_idx == -1:
                raise IndexError('カラムに輸出向先、得意先コード、納入先コードがありません')

            # yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
            yusyutu_dict: Dict[Tuple,str] = {}
            for line in unsoutaiou_data:
                tokui_nonyu_tpl: Tuple = (line[tokui_idx], line[nonyu_idx])
                yusyutu_dict[tokui_nonyu_tpl] = line[yusyutu_dist_idx]

            return yusyutu_dict


        # unsoutaiou_dataからyusyutu_dictを作る
        # yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        yusyutu_dict: Dict[Tuple,str] = create_yusyutu_dict(unsoutaiou_data,
                                                            unsoutaiou_col)
        
        # sumi_dataのidxを求めておく
        tokui_code_idx: int = get_idx(sumi_col, '得意先コード')
        nonyu_code_idx: int = get_idx(sumi_col, '納入先コード')
        unsou_code_idx: int = get_idx(sumi_col, 'unsou_code')
        kubun_no_idx:   int = get_idx(sumi_col, 'kubun_no')

        unsouSet: Set[Tuple] = set()
        for line in sumi_data:
            tokui_code: str = line[tokui_code_idx]
            nonyu_code: str = line[nonyu_code_idx]
            unsou_code: str = line[unsou_code_idx]
            if unsou_code == ' ':  # 運送屋がなければunsouSetはつくらない
                continue
            kubun_no: str = line[kubun_no_idx]
            if nonyu_code == ' ':
                nonyu_code = ''

            YorN = yusyutu_dict.get((tokui_code, nonyu_code),'noData')
            if YorN == 'noData':
                raise KeyError('得意code、納入codeのタプルがキーにありません')
            tmp:Tuple = (unsou_code, kubun_no, YorN)
                         
            unsouSet.add(tmp)

        return unsouSet
