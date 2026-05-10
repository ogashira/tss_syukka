from typing import List, Dict, Any, Set, Tuple
import json
from decimal import Decimal


class CreateJson:
    def __init__(self)-> None:
        pass


    def create_json_str(self, data: List[Dict[str,Any]])-> object:
        # データがDecimalの場合はfloatに変換する
        json_str = json.dumps(data, ensure_ascii= False, default=self.default_method)
        return json_str


    def default_method(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable_oga')


    def create_dict_from_list(self, col: List[str], 
                    data: List[List[Any]])-> List[Dict[str, Any]]:

        list_dict: List[Dict[str,Any]] = []
        for line in data:
            inner_dict = dict(zip(col, line))
            list_dict.append(inner_dict)


        return list_dict

        
    def create_dict_from_set(self, col: List[str], 
                    data: Set[Tuple[str]])-> List[Dict[str, str]]:

        list_dict: List[Dict[str,str]] = []
        for line in data:
            inner_dict = dict(zip(col, line))
            list_dict.append(inner_dict)


        return list_dict
