from typing import List, Dict, Any, Set, Tuple
import json
from decimal import Decimal



class CreateJson:
    def __init__(self)-> None:
        pass


    def create_json_str(self, data: List[Dict[str,Any]])-> str:
        # データがDecimalの場合はfloatに変換する
        json_str = json.dumps(data, ensure_ascii= False, default=self.default_method)
        return json_str


    def default_method(self, obj):
        '''
        DecimalはJSONにならないのでfloatに変換する
        '''
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable_oga')


    def add_key_for_tupleKey(self, 
                      data: List[Dict[str, Any]],
                      add_key: str,                #輸出向け先
                      add_dict: Dict[Tuple,str],
                      add_dict_key: Tuple[str,str] #('得意先コード','納入先コード')
                      )-> None:
        '''
        辞書のリストdataの辞書部分にadd_keyを追加する。
        追加するvalueはadd_dictのvalue
        add_dictのkeyはタプル(add_dict_key)
        '''
        for line_dict in data:
            tmpTuple = (line_dict[add_dict_key[0]], line_dict[add_dict_key[1]])
            line_dict[add_key] = add_dict.get(tmpTuple, '') 

        
