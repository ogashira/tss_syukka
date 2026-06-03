import json
import pprint
import subprocess
import sys
import pprint
from re import I
from typing import List, Dict, Any, Set, Tuple
from get_idx import GetIdx
from instance_factory import InstanceFactory
from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
from uriage_for_packing import UriageForPacking
from excel_output import IExcelOutput, SyukkaJissekiSyoukai, AllPackings


def start()-> None:

    syukka_date = input('出荷日を入力してください (例: 20260930): ')

    InstanceFactory.get_sql_server_effit()

    sumi = InstanceFactory.get_fetchUriageSumi(syukka_date)
    sumi_col, sumi_data = sumi.fetch_data()

    #unsoutaiouデータを取得
    unsoutaiou = InstanceFactory.get_fetchUnsoutaiouToke()
    unsoutaiou_col, unsoutaiou_data = unsoutaiou.fetch_data()

    #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
    createDictFromList = InstanceFactory.get_createDictFromList()
    yusyutu_dict = createDictFromList.create_yusyutuDict(unsoutaiou_data, 
                                                            unsoutaiou_col)
    #sumi_col, sumi_dataを辞書にする
    # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
    sumi_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dict_from_list(sumi_col, sumi_data)

    #Uriageインスタンス生成し、uriages_toke, uriages_honsyaに分ける
    uriages_toke: List[UriageForSyukkaJisseki] = []
    uriages_honsya: List[UriageForSyukkaJisseki] = []
    for sumi_dict in sumi_dicts:
        uriage_instance: UriageForSyukkaJisseki = UriageForSyukkaJisseki(sumi_dict, yusyutu_dict)
        if sumi_dict['factory_name'] == '@0001':
            uriages_honsya.append(uriage_instance)
            continue
        uriages_toke.append(uriage_instance)

    createJson = InstanceFactory.get_createJson()
    syukkaJissekiSyoukais: List[IExcelOutput] = []
    unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
    syukkaJissekiSyoukai_honsya: IExcelOutput = None
    syukkaJissekiSyoukai_toke: IExcelOutput = None
    # uriages_tokeに要素があったらsmiData_tokeのインスタンスを生成
    if uriages_toke:
        syukkaJissekiSyoukai_toke = SyukkaJissekiSyoukai(uriages_toke,
                                                         createJson,
                                                         '@0002',
                                                         unsouSet_col,
                                                         createDictFromList)
        syukkaJissekiSyoukais.append(syukkaJissekiSyoukai_toke)

    # uriages_honsya に要素があったらsmiData_honsyaのインスタンスを生成
    if uriages_honsya:
        syukkaJissekiSyoukai_honsya = \
                                 SyukkaJissekiSyoukai(uriages_honsya, 
                                                      createJson,
                                                      '@0001',
                                                      unsouSet_col,
                                                      createDictFromList)
        syukkaJissekiSyoukais.append(syukkaJissekiSyoukai_honsya)

    exe_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoSkJsBat\ToyoKogyoSkJsBat.exe'

    output_path = r'C:\Users\toyo-pc12\Desktop'
    barcodeFolder = r'C:\Users\toyo-pc12\Desktop' 

    for syukkaJissekiSyoukai in syukkaJissekiSyoukais:
        result = syukkaJissekiSyoukai.create_tssBat(exe_path,
                                                         output_path,
                                                         barcodeFolder)
        print (f'returncode= {result.returncode}')


    ''' ここから業務_packing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    sumi_for_packing = InstanceFactory.get_fetchUriageSumiForPacking(syukka_date)
    sumi_for_packing_col, sumi_for_packing_data = sumi_for_packing.fetch_data()

    #TODO
    pprint.pprint(sumi_for_packing_data)

    #sumi_for_packing_col, sumi_for_packing_dataを辞書にする
    # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
    sumi_for_packing_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dict_from_list(sumi_for_packing_col, 
                                                     sumi_for_packing_data)
    #UriageForPackingインスタンス生成し、uriageForPackings_toke, uriageForPackings_honsyaに分ける
    uriageForPackings_toke: List[UriageForPacking] = []
    uriageForPackings_honsya: List[UriageForPacking] = []
    for sumi_for_packing_dict in sumi_for_packing_dicts:
        uriageForPacking_instance: UriageForPacking = \
                UriageForPacking(sumi_for_packing_dict, yusyutu_dict)
        if sumi_for_packing_dict['factory_name'] == '@0001':
            uriageForPackings_honsya.append(uriageForPacking_instance)
            continue
        uriageForPackings_toke.append(uriageForPacking_instance)

    createJson = InstanceFactory.get_createJson()
    allPackings: List[IExcelOutput] = []
    allPackings_honsya: IExcelOutput = None
    allPackings_toke: IExcelOutput = None
    # uriageForPacking_tokeに要素があったらsmiData_tokeのインスタンスを生成
    if uriageForPackings_toke:
        allPackings_toke = AllPackings(uriageForPackings_toke,
                               createJson,
                               '@0002',
                               createDictFromList)
        allPackings.append(allPackings_toke)
    # uriageForPacking_honsyaに要素があったらsmiData_tokeのインスタンスを生成
    if uriageForPackings_honsya:
        allPackings_honsya = AllPackings(uriageForPackings_honsya,
                               createJson,
                               '@0001',
                               createDictFromList)
        allPackings.append(allPackings_honsya)
    
    exe_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoPackingBat\ToyoKogyoPackingBat.exe'
    myFolder = r'C:\Users\toyo-pc12\Desktop'

    if allPackings_toke is not None:
        result = allPackings_toke.create_tssBat(exe_path, myFolder)

    if allPackings_honsya is not None:
        result = allPackings_honsya.create_tssBat(exe_path, myFolder)

    InstanceFactory.delete_cnxn












