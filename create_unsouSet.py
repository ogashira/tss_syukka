from typing import List, Dict, Any, Tuple, Set
from get_idx import GetIdx


class CreateUnsouSet:
    def __init__(self)-> None:
        pass


    def create_unsouSet(self, sumi_data: List[List[Any]],
                        sumi_col: List[str],
                        yusyutu_dict: Dict[Tuple, str]
                        )-> Set[Tuple]:

        # yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        
        # sumi_dataのidxを求めておく
        tokui_code_idx: int = GetIdx.get_idx(sumi_col, '得意先コード')
        nonyu_code_idx: int = GetIdx.get_idx(sumi_col, '納入先コード')
        unsou_code_idx: int = GetIdx.get_idx(sumi_col, 'unsou_code')
        kubun_no_idx:   int = GetIdx.get_idx(sumi_col, 'kubun_no')

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
