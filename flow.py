import platform
from re import I
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, TYPE_CHECKING, Optional, cast
from IAdd_to_yoteiSouko import IAddToYoteiSouko
from fetch_data_for_list import IFetchDataForList
from instance_factory import InstanceFactory
from IExcel_output import IExcelOutput, SyukkaJissekiSyoukai, AllPackings
from create_tss_bat import CreateTssBat
from show_to_excel import ShowToExcel

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from uriage_for_packing import UriageForPacking
    from check_hatumono import CheckHatumono


def create_excel_outputs_args(excel_outputs_args:List[Dict[str,Any]],
                    output_name: str, excelOutput: Optional[IExcelOutput],
                    exe_path:str, output_path:str, barcodeFolder: str)->None:

    if excelOutput is None:
        return

    innerDic: Dict[str, Any] = {}
    innerDic['output_name'] = output_name
    innerDic['excel_output'] = excelOutput
    innerDic['exe_path'] = exe_path
    innerDic['output_path'] = output_path
    innerDic['barcodeFolder'] = barcodeFolder
    excel_outputs_args.append(innerDic)


def make_dire(syukka_date: str)-> str:
    # 1. ベースとなるディレクトリと今日の年月日を設定
    base_dir = Path(r"\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\01出荷output_TSS")
    if platform.system() == 'Linux':
        base_dir = Path(r"/mnt/public/営業課ﾌｫﾙﾀﾞ/01出荷output_TSS")


    # 2. 最初のリクエストフォルダ名を作成
    target_dir = base_dir / syukka_date

    # 3. フォルダがすでに存在する場合、末尾に「_数値」を付与してチェックを繰り返す
    count = 2
    while target_dir.exists():
        target_dir = base_dir / f"{syukka_date}_{count}"
        count += 1

    # 4. 重複しないフォルダ名が確定したら作成する
    target_dir.mkdir(parents=True, exist_ok=True)

    # target_dirを文字列に変換する
    target_dir_str = str(target_dir)

    return target_dir_str


def date_input()-> str:
    while True:
        # 1. ユーザーからの入力を受け取る
        syukka_date = input("出荷日を入力してください(例：20260609) : ")
        
        # 2. 文字数のチェック（必ず8桁であること）
        if len(syukka_date) != 8:
            print("エラー: 8桁の半角数字で入力してください。")
            continue  # ループの先頭に戻る
            
        # 3. 数字以外が混ざっていないか、および日付として正しいかのチェック
        try:
            # 日付形式（YYYYMMDD）に変換できるか検証
            valid_date = datetime.strptime(syukka_date, "%Y%m%d")
            
            # 4. 西暦が 2025年 〜 2100年 の間かチェック
            if 2025 <= valid_date.year <= 2100:
                break  # 条件をすべてクリアしたため、ループを抜ける
            else:
                print("エラー: 西暦は2025年から2100年の間で入力してください。")
                
        except ValueError:
            # 数字以外の文字が混ざっている場合や、存在しない月日（例: 02月30日など）の場合
            print("エラー: 正しい日付（数字のみ）を入力してください。")

    # ループを抜けた後の処理
    print()
    print(f"正しい出荷日を受け付けました: {syukka_date}")
    print()
    print()
    return syukka_date


def data_fetch(instance: IFetchDataForList, recorder)-> Tuple:
    instanceCol: List[Any] = []
    instanceData: List[List[Any]] = []
    try:
        instanceCol, instanceData = instance.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    return instanceCol, instanceData


def start()-> None:

    syukka_date = date_input()

    mydir:str = make_dire(syukka_date)
    recorder = InstanceFactory.get_recorder(mydir)

    recorder.out_file(f'出荷日：{syukka_date}', '\n')

    '''自動売上処理の実行 '''
    staffCD = "000240" # 担当者コード
    target_dir = r"\\192.168.1.245\effit_A\BIN"
    exePath = r"\\192.168.1.245\effit_A\BIN\U2002_AUR020B.exe"
    # TODO "toyo_test"を"toyo"に変更する
    command_line = \
      f'{exePath} \'"toyo_2019","1","{staffCD}","{syukka_date}","","","","92"\''
    powershell_path = os.path.join(os.environ['SystemRoot'], 'System32', 
                                  'WindowsPowerShell', 'v1.0', 'powershell.exe')

    result = None
    txt = f'\n売上処理を実行しました。\n'
    try:
        result = subprocess.run(command_line, cwd= target_dir, shell= True, 
                              executable= powershell_path, capture_output=True,
                              text=True, encoding="cp932")
        recorder.out_log(f'result: {result}', '\n')
        recorder.out_file(f'result: {result}', '\n')
    except Exception as e:
        print('自動出荷処理エラーです', e)


    # クラス変数にsql_server_effitのcnxnを格納する
    InstanceFactory.get_sql_server_effit()

    # 注残データを取得
    tyuzan = InstanceFactory.get_fetchTyuzan(syukka_date)
    tyuzan_data = []
    tyuzan_col, tyuzan_data = data_fetch(tyuzan, recorder)
    if tyuzan_data:
        txt += f'以下の注残があります。\n' 
        recorder.out_log(txt, '\n')
        recorder.out_file(txt, '\n')
        recorder.outLogFile_to_sameNumberOfChara(tyuzan_col, tyuzan_data)
    else:
        txt += rf'注残はありません。' 
        recorder.out_file(txt)
        txt += ' ✊️ \n' 
        recorder.out_log(txt, '\n')


    sumi = InstanceFactory.get_fetchUriageSumi(syukka_date)
    sumi_data = []
    sumi_col, sumi_data = data_fetch(sumi, recorder)


    if not sumi_data:
        txt = f'{syukka_date}の売上データがありません。処理を中止します'
        recorder.out_log(txt, '\n')
        recorder.out_file(txt, '\n')
        sys.exit(1)

    #unsoutaiouデータを取得
    unsoutaiou_toke = InstanceFactory.get_fetchUnsoutaiouToke()
    unsoutaiou_toke_col, unsoutaiou_toke_data = \
                                         data_fetch(unsoutaiou_toke, recorder)
    unsoutaiou_honsya = InstanceFactory.get_fetchUnsoutaiouHonsya()
    unsoutaiou_honsya_col, unsoutaiou_honsya_data = \
                                      data_fetch(unsoutaiou_honsya, recorder)

    #yusyutu_toke_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
    #leadTime_toke_dict = {('T0060', 'H172'): 1, ('T0060', ''): 2,.....}
    '''
    yusyutu_dictとleadTime_dictのnonyCDは、''に変換しておく
    '''
    createDictFromList = InstanceFactory.get_createDictFromList()
    try:
        yusyutu_toke_dict: Dict[Tuple,str] = \
            createDictFromList.create_yusyutuDict(unsoutaiou_toke_data, 
                                        unsoutaiou_toke_col, 'isExport')
        yusyutu_honsya_dict: Dict[Tuple,str] = \
            createDictFromList.create_yusyutuDict(unsoutaiou_honsya_data, 
                                        unsoutaiou_honsya_col, 'isExport')
        leadTime_toke_dict: Dict[Tuple,int] = \
            createDictFromList.create_leadTimeDict(unsoutaiou_toke_data, 
                                        unsoutaiou_toke_col, 'leadTime')
        leadTime_honsya_dict: Dict[Tuple,int] = \
            createDictFromList.create_leadTimeDict(unsoutaiou_honsya_data, 
                                        unsoutaiou_honsya_col, 'leadTime')
    except IndexError as e:
        recorder.out_log(e, '\n')
        recorder.out_file(e, '\n')
        sys.exit(1)

    yusyutu_dicts: Dict[str, Dict[Tuple, str]] = {}
    yusyutu_dicts['toke'] = yusyutu_toke_dict
    yusyutu_dicts['honsya'] = yusyutu_honsya_dict

    leadTime_dicts: Dict[str, Dict[Tuple, int]] = {}
    leadTime_dicts['toke'] = leadTime_toke_dict
    leadTime_dicts['honsya'] = leadTime_honsya_dict


    # 出荷添付リスト(coa)を取得
    tenpCoa = InstanceFactory.get_fetchSyukkaListCoa()
    tenpCoa_col, tenpCoa_data = data_fetch(tenpCoa, recorder)

    # 出荷添付リスト(sitei_denpyo)を取得
    tenpSiteiDenpyo = InstanceFactory.get_fetchSyukkaListSiteiDenpyo()
    tenpSitei_col, tenpSitei_data = data_fetch(tenpSiteiDenpyo, recorder)

    # tenpCoa_col, tenpCoa_dataを辞書にする
    tenpCoa_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dicts_from_colAndList(tenpCoa_col, 
                                                            tenpCoa_data)

    # tenpSitei_col, tenpSitei_dataを辞書にする
    tenpSitei_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dicts_from_colAndList(tenpSitei_col, 
                                                            tenpSitei_data)

    #sumi_col, sumi_dataを辞書にする
    # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
    sumi_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dicts_from_colAndList(sumi_col, sumi_data)

    #Uriageインスタンス生成し、uriages_toke, uriages_honsyaに分ける
    uriages = InstanceFactory.get_uriagesHonsyaToke(sumi_dicts, 
                                                    yusyutu_dicts,
                                                    tenpCoa_dicts, recorder)
    uriages_honsya: List["UriageForSyukkaJisseki"] = uriages[0]
    uriages_toke: List["UriageForSyukkaJisseki"] = uriages[1]


    '''SyukkaJissekiSyoukaiのインスタンス生成>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    createJson = InstanceFactory.get_createJson()
    unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
    syukkaJissekiSyoukai_honsya: Optional[IExcelOutput] = None
    syukkaJissekiSyoukai_toke: Optional[IExcelOutput] = None
    # uriages_tokeに要素があったらSyukkajissekiSyoukai_tokeのインスタンスを生成
    if uriages_toke:
        syukkaJissekiSyoukai_toke = InstanceFactory.get_syukkaJissekiSyoukai(
                 uriages_toke,
                 createJson,
                 '@0002',
                 unsouSet_col,
                 createDictFromList,
                 recorder
                 )

    # uriages_honsya に要素があったらSyukkaJissekiSyoukai_honsyaのインスタンスを生成
    if uriages_honsya:
        syukkaJissekiSyoukai_honsya = InstanceFactory.get_syukkaJissekiSyoukai( 
                 uriages_honsya, 
                 createJson,
                 '@0001',
                 unsouSet_col,
                 createDictFromList,
                 recorder
                 )


    

    ''' ここから業務_packing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    sumi_for_packing = InstanceFactory.get_fetchUriageSumiForPacking(syukka_date)
    sumi_for_packing_col, sumi_for_packing_data = data_fetch(sumi_for_packing, 
                                                             recorder)


    ''' productCan, tnju, grossWeightデータを取得して辞書にする '''
    productCan = InstanceFactory.get_fetchProductCan()
    productCan_col, productCan_data = data_fetch(productCan, recorder)

    tnju = InstanceFactory.get_fetchTnju()
    tnju_col, tnju_data = data_fetch(tnju, recorder)

    # 缶込み重量(grossWeight)データ取得
    MHINCDgrossWeight: IFetchDataForList = \
                                         InstanceFactory.get_fetchGrossWeight()
    grossWeight_col, grossWeight_data = data_fetch(MHINCDgrossWeight, recorder)


    try:
        productCan_dic:Dict[str,Any] = \
            createDictFromList.create_dict_from_list(productCan_col, 
                                                     productCan_data, 
                                                     '親品番', 
                                                     '子品番')
        tnju_dic:Dict[str,Any] = \
            createDictFromList.create_dict_from_list(tnju_col, 
                                                     tnju_data,
                                                     'hinban',
                                                     'tnju')
        grossWeight_dic:Dict[str,Any] = \
            createDictFromList.create_dict_from_list(grossWeight_col, 
                                                     grossWeight_data,
                                                     'hinban',
                                                     'grossWeight')
    except IndexError as e:
        recorder.out_log(e, '\n')
        recorder.out_file(e, '\n')
        sys.exit(1)

    # カレンダーデータ取得 AddForWeekdayDiffのインスタンス用
    calenderUnso = InstanceFactory.get_fetchCalenderUnsouya(syukka_date)
    calenderToyo = InstanceFactory.get_fetchCalenderToyo(syukka_date)
    calenderUnsoCol, calenderUnsoData = data_fetch(calenderUnso, recorder)
    calenderToyoCol, calenderToyoData = data_fetch(calenderToyo, recorder)

    # TOKUIデータ取得　closeDayを得る
    fetchTokui: IFetchDataForList = InstanceFactory.get_fetchTokui()
    close_col, close_data = data_fetch(fetchTokui, recorder)
    # close_dataを辞書にする
    close_days:Dict[str, str] = createDictFromList.create_dict_from_list(
            close_col, close_data, 'tokuiCD', 'closeDay')
    # noJikais 次回請求しない得意先コードのリストを作る
    noJikais: List[str] = createDictFromList.create_noJikailist(
                                                   close_col, close_data)

    # calcUntin_dataを取得
    calcUntin_honsya = InstanceFactory.get_fetchCalcUntin(syukka_date, '@0001')
    calcUntin_toke = InstanceFactory.get_fetchCalcUntin(syukka_date, '@0002')
    unsouNameHonsya_col, unsouNameHonsya_data = \
                                          data_fetch(calcUntin_honsya, recorder)
    unsouNameToke_col, unsouNameToke_data = \
                                          data_fetch(calcUntin_toke, recorder)
    # unsouNames_toke:Dict, unsouNames_honsya:Dictを作る
    # {'静岡県焼津市保福島569': '新潟', '愛知県名古屋市xxxxx': 'ケイヒン'...}
    unsouNames_honsya = {}
    unsouNames_toke = {}
    if unsouNameHonsya_data:
        unsouNames_honsya = \
                createDictFromList.create_dict_from_list(unsouNameHonsya_col,
                                                         unsouNameHonsya_data,
                                                         'address',
                                                         'unsouName')
    if unsouNameToke_data:
        unsouNames_toke = \
                createDictFromList.create_dict_from_list(unsouNameToke_col,
                                                         unsouNameToke_data,
                                                         'address',
                                                         'unsouName')

    ''' cnxnの消去>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    InstanceFactory.delete_cnxn
    '''>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''

    #カレンダーデータをlist_YM, dict_unso_holiday, dict_toyo_holidayにする
    # list_YMD = ['20260601', '20260602',..........]
    # dict_unso_holiday = {'20260601':' ', '20260602':'1', ......}
    # dict_toyo_holiday = {'20260601':'1', '20260602':'1', ......}
    list_YMD = createDictFromList.create_list_YMD(calenderToyoCol, 
                                             calenderToyoData, 'YYYYMM', 'DD')
    dict_unso_holiday = createDictFromList.create_YMD_holiday(calenderUnsoCol,
                                  calenderUnsoData, 'YYYYMM', 'DD', 'holiday')
    dict_toyo_holiday = createDictFromList.create_YMD_holiday(calenderToyoCol,
                                  calenderToyoData, 'YYYYMM', 'DD', 'holiday')
    
    # AddToYoteiSoukos辞書にインスタンス５個詰める
    addForWeekdayDiff: IAddToYoteiSouko = InstanceFactory.get_addForWeekdayDiff(
                                          list_YMD, dict_unso_holiday, 
                                          dict_toyo_holiday)
    addForCoa: IAddToYoteiSouko =         InstanceFactory.get_addForCoa(
                                          tenpCoa_dicts)
    addForSiteiDenpyo: IAddToYoteiSouko = InstanceFactory.get_addForSiteiDenpyo(
                                          tenpSitei_dicts)
    addForEigyosyo: IAddToYoteiSouko =    InstanceFactory.get_addForEigyosyo()
    addForDohai: IAddToYoteiSouko =       InstanceFactory.get_addForDohai()
    addForJikai: IAddToYoteiSouko =       InstanceFactory.get_addForJikai(
                                                                     close_days,
                                                                     noJikais)
    addToYoteiSoukos: Dict[str, IAddToYoteiSouko] = {}
    addToYoteiSoukos['coa'] = addForCoa
    addToYoteiSoukos['siteiDenpyo'] = addForSiteiDenpyo
    addToYoteiSoukos['eigyosyo'] = addForEigyosyo
    addToYoteiSoukos['dohai'] = addForDohai
    addToYoteiSoukos['weekdayDiff'] = addForWeekdayDiff
    addToYoteiSoukos['jikai'] = addForJikai


    #sumi_for_packing_col, sumi_for_packing_dataを辞書にする
    # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
    sumi_for_packing_dicts:List[Dict[str,Any]] = \
            createDictFromList.create_dicts_from_colAndList(
                                                     sumi_for_packing_col, 
                                                     sumi_for_packing_data)

    #UriageForPackingインスタンス生成し、uriageForPackings_toke, uriageForPackings_honsyaに分ける
    uriagePackings: Tuple[List, List] = \
            InstanceFactory.get_uriageForPackingsHonsyaToke(
                    sumi_for_packing_dicts, 
                    yusyutu_dicts,
                    leadTime_dicts,
                    productCan_dic,
                    tnju_dic,
                    grossWeight_dic,
                    recorder,
                    addToYoteiSoukos,
                    unsouNames_honsya,
                    unsouNames_toke,
                    )

    uriageForPackings_honsya: List["UriageForPacking"] = uriagePackings[0]
    uriageForPackings_toke: List["UriageForPacking"] = uriagePackings[1]

    '''AllPackingsのインスタンスを生成>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    PackingForDenpyoはAllPackingの中で生成する'''
    allPackings_honsya: Optional[IExcelOutput] = None
    allPackings_toke: Optional[IExcelOutput] = None
    # uriageForPacking_tokeに要素があったらallPackings__tokeのインスタンスを生成
    if uriageForPackings_toke:
        allPackings_toke = InstanceFactory.get_allPackings(
                                uriageForPackings_toke,
                                createJson,
                                '@0002',
                                createDictFromList,
                                recorder)
    # uriageForPacking_honsyaに要素があったらallPackings_honsyaのインスタンスを生成
    if uriageForPackings_honsya:
        allPackings_honsya = InstanceFactory.get_allPackings(
                               uriageForPackings_honsya,
                               createJson,
                               '@0001',
                               createDictFromList,
                               recorder)



    
    '''ここから検査成績書>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    #dic_uriages_for_coa = 
    #{'koito': [........], 'metal': [......], 'nonMetal': [.......]} 
    dic_uriages_for_coa: Dict[str, List[UriageForSyukkaJisseki]] = {}
    dic_uriages_for_coa['koito'] = []
    dic_uriages_for_coa['metal'] = []
    dic_uriages_for_coa['nonMetal'] = []
    if syukkaJissekiSyoukai_honsya is not None:
        if isinstance(syukkaJissekiSyoukai_honsya, SyukkaJissekiSyoukai):
            syukkaJissekiSyoukai_honsya.collect_uriage_for_coa(dic_uriages_for_coa)
    if syukkaJissekiSyoukai_toke is not None:
        if isinstance(syukkaJissekiSyoukai_toke, SyukkaJissekiSyoukai):
            syukkaJissekiSyoukai_toke.collect_uriage_for_coa(dic_uriages_for_coa)
    '''
    syukkaJissekiSyoukai_tokeはIExcelOutputインターフェース型として宣言しているの
    で、collect_uriage_for_coaメソッドはインターフェースには無いためエラーになる。
    そこで、if isinstanceでSyukkaJissekiSyoukai型としてpyrightに認識させる。
    '''
    checkHatumono: "CheckHatumono" = InstanceFactory.get_checkHatumono()

    hsCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['nonMetal']:
        for uriage in dic_uriages_for_coa['nonMetal']:
            hsCoas.append(InstanceFactory.get_hsCoa(uriage, checkHatumono))
    mhsCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['metal']:
        for uriage in dic_uriages_for_coa['metal']:
            mhsCoas.append(InstanceFactory.get_mhsCoa(uriage, checkHatumono))
    koitoCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['koito']:
        for uriage in dic_uriages_for_coa['koito']:
            koitoCoas.append(InstanceFactory.get_koitoCoa(uriage, checkHatumono))


    '''
    syukkaJissekiSyoukai_, allPackings_, hsCoa, mhsCoa, koitoCoa用の
    引数を作って、excel_outputs_argsに詰めていく
    '''
            
    syukkaJisseki_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoSkJsBat\ToyoKogyoSkJsBat.exe'
    packing_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoPackingBat\ToyoKogyoPackingBat.exe'
    hs_coa_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoHsRepBat\ToyoKogyoHsRepBat.exe'
    mhs_coa_path = r'\\192.168.1.247\共有\TSS_System\TssSystem\ToyoKogyo\Bat\ToyoKogyoMhsRepBat\ToyoKogyoMhsRepBat.exe'
    koito_coa_path = ''
    output_path = mydir
    barcodeFolder = mydir

    '''
    excel_outputs_args = 
    [{'output_name':str, 'excel_output':IExcelOutput, 'exe_path':str, 
    'output_path':str, 'barcodeFolder':str}, {....}, {....} ]
    '''

    excel_outputs_args: List[Dict[str,Any]] = []

    create_excel_outputs_args(excel_outputs_args,'出荷実績照会_本社',
                             syukkaJissekiSyoukai_honsya, syukkaJisseki_path,
                             output_path, barcodeFolder)

    create_excel_outputs_args(excel_outputs_args,'出荷実績照会_土気',
                             syukkaJissekiSyoukai_toke, syukkaJisseki_path,
                             output_path, barcodeFolder)

    create_excel_outputs_args(excel_outputs_args,'業務packing_本社',
                             allPackings_honsya, packing_path,
                             output_path, '')

    create_excel_outputs_args(excel_outputs_args,'業務packing_土気',
                             allPackings_toke, packing_path,
                             output_path, '')


    if hsCoas:
        for hsCoa in hsCoas:
            create_excel_outputs_args(excel_outputs_args,
                                      '品管シートCoa',
                                      hsCoa, hs_coa_path,
                                      output_path, 
                                      barcodeFolder)
    if mhsCoas:
        for mhsCoa in mhsCoas:
            create_excel_outputs_args(excel_outputs_args,
                                      'メタル品管シートCoa',
                                      mhsCoa, mhs_coa_path,
                                      output_path, 
                                      barcodeFolder)
    if koitoCoas:
        for koitoCoa in koitoCoas:
            create_excel_outputs_args(excel_outputs_args,
                                      '小糸Coa',
                                      koitoCoa, koito_coa_path,
                                      output_path, 
                                      barcodeFolder)


    '''
    Contextクラス(CreateTssBat)にexcel_outputs_argsを渡して、
    アウトプットを作ってもらう
    '''
    recorder.out_log('', '\n')
    recorder.out_file('', '\n')


    createTssBat:CreateTssBat = \
            InstanceFactory.get_createTssBat(excel_outputs_args, recorder)
    createTssBat.create_tssBat()

    '''業務packingに売上金額を追加する>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    slash: str = r'\\'
    if platform.system() == 'Linux': slash = r'/'
    if allPackings_honsya is not None:
        book_honsya = f'{mydir}{slash}本社業務_packing.xlsx'
        showToExcel = ShowToExcel(book_honsya, allPackings_honsya)
        showToExcel.show_to_excel()
        
    if allPackings_toke is not None:
        book_toke = f'{mydir}{slash}土気業務_packing.xlsx'
        showToExcel = ShowToExcel(book_toke, allPackings_toke)
        showToExcel.show_to_excel()


    txt = 'プログラムは無事終了しました。'
    recorder.out_log(txt, '\n')
    recorder.out_file(txt, '\n')
