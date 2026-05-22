import json
import pprint
import subprocess
import sys
from re import I
from typing import List, Dict, Any, Set, Tuple
from get_idx import GetIdx
from instance_factory import InstanceFactory


def start()-> None:

    def to_add_1(data: List[List[Any]])->None:
        for line in data:
            line[16] = 1

    def del_unsouCode_is_blank(data: List[List[Any]], 
                               sumi_col: List[str])-> List[List[Any]]:
        del_data: List[List[Any]] = []

        #unsouCodeのidxを求める
        unsouIdx: int = GetIdx.get_idx(sumi_col, 'unsouCode')

        for line in data:
            if line[unsouIdx] == ' ': # line[unsouIdx] = unsouCode
                continue
            del_data.append(line)

        return del_data

    
    syukka_date = input('出荷日を入力してください (例: 20260930): ')

    InstanceFactory.get_sql_server_effit()

    sumi = InstanceFactory.get_fetchUriageSumi(syukka_date)
    sumi_col, sumi_data = sumi.fetch_data()

    # TODO 後で消す。addに1を入れる
    to_add_1(sumi_data)

    #unsouCodeが' 'のデータは削除する
    sumi_data = del_unsouCode_is_blank(sumi_data, sumi_col)

    
    '''unsoutaiouデータを取得 '''
    unsoutaiou = InstanceFactory.get_fetchUnsoutaiouToke()
    unsoutaiou_col, unsoutaiou_data = unsoutaiou.fetch_data()

    ''' yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}'''
    create_yusyutuDict = InstanceFactory.get_createYusyutuDict()
    yusyutu_dict = create_yusyutuDict.create_yusyutuDict(unsoutaiou_data, 
                                                            unsoutaiou_col)

    createJson = InstanceFactory.get_createJson()
    '''yusyutu_dictを一緒に渡して、'輸出向先キーも追加する' '''
    sumi_dict:List[Dict[str,Any]] = \
            createJson.create_dict_from_list(sumi_col, sumi_data, yusyutu_dict)
    sumi_json_str = createJson.create_json_str(sumi_dict)

    

    createUnsouSet = InstanceFactory.get_createUnsouSet()
    unsouSet: Set[Tuple] = set()
    # unsouSet { ('U0001', '1', 'y'), ('U0001', '1', '')......}
    try:
        unsouSet = createUnsouSet.create_unsouSet(sumi_data, 
                                                  sumi_col, yusyutu_dict)
    except IndexError as e:
        print(e)
        sys.exit(1)
    except KeyError as e:
        sys.exit(1)

    unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
    unsouSet_dict = createJson.create_dict_from_set(unsouSet_col, unsouSet)
    unsouSet_json_str = createJson.create_json_str(unsouSet_dict)

    print(unsouSet_json_str)
    print('*********************************************************')
    print(sumi_json_str)


    exe_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoSkJsBat\ToyoKogyoSkJsBat.exe'

    output_path = r'C:\Users\toyo-pc12\Desktop'
    
    factoryName = "土気"
    syukkaKoujou = "出荷工場：@0002 土気工場"
    barcodeFolder = r'C:\Users\toyo-pc12\Desktop' 


    args = [
            unsouSet_json_str,
            sumi_json_str,
            output_path,
            factoryName,
            syukkaKoujou,
            barcodeFolder
            ]

    InstanceFactory.delete_cnxn

    result = subprocess.run([exe_path] + args, capture_output=True, text=True)

    print(f'returncode= {result.returncode}')










