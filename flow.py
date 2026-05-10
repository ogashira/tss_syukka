import json
import pprint
import sys
from re import I
from typing import List, Dict, Any, Set, Tuple
from instance_factory import InstanceFactory


def start()-> None:
    
    syukka_date = input('出荷日を入力してください (例: 20260930): ')

    InstanceFactory.get_sql_server_effit()

    sumi = InstanceFactory.get_fetchUriageSumi(syukka_date)
    sumi_col, sumi_data = sumi.fetch_data()

    
    unsoutaiou = InstanceFactory.get_fetchUnsoutaiouToke()
    unsoutaiou_col, unsoutaiou_data = unsoutaiou.fetch_data()

    createJson = InstanceFactory.get_createJson()
    sumi_dict:List[Dict[str,Any]] = \
            createJson.create_dict_from_list(sumi_col, sumi_data)
    sumi_json_str = createJson.create_json_str(sumi_dict)

    createUnsouSet = InstanceFactory.get_createUnsouSet()
    unsouSet: Set[Tuple] = set()
    # unsouSet { ('U0001', '1', 'y'), ('U0001', '1', '')......}
    try:
        unsouSet = createUnsouSet.create_unsouSet(sumi_data, sumi_col,
                                                unsoutaiou_data, unsoutaiou_col)
    except IndexError as e:
        print(e)
        sys.exit(1)
    except KeyError as e:
        sys.exit(1)

    unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
    unsouSet_dict = createJson.create_dict_from_set(unsouSet_col, unsouSet)

    print(sumi_data)
    print('*********************************************************')
    pprint.pprint(unsouSet_dict)



    









    InstanceFactory.delete_cnxn



