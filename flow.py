import platform
from re import I
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, TYPE_CHECKING, Optional
from instance_factory import InstanceFactory
from IExcel_output import IExcelOutput, SyukkaJissekiSyoukai
from create_tss_bat import CreateTssBat

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from uriage_for_packing import UriageForPacking


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
    base_dir = Path(r"\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\01出荷output_TSS_実装中")
    if platform.system() == 'Linux':
        base_dir = Path(r"/mnt/public/営業課ﾌｫﾙﾀﾞ/01出荷output_TSS_実装中")


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
    print(f"正しい出荷日を受け付けました: {syukka_date}")
    return syukka_date


def start()-> None:

    syukka_date = date_input()

    mydir:str = make_dire(syukka_date)
    recorder = InstanceFactory.get_recorder(mydir)

    recorder.out_file(f'出荷日：{syukka_date}', '\n')

    InstanceFactory.get_sql_server_effit()

    sumi = InstanceFactory.get_fetchUriageSumi(syukka_date)
    sumi_data = []
    try:
        sumi_col, sumi_data = sumi.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    if not sumi_data:
        txt = '売上データがありません。処理を中止します'
        recorder.out_log(txt, '\n')
        recorder.out_file(txt, '\n')
        sys.exit(1)

    #unsoutaiouデータを取得
    unsoutaiou = InstanceFactory.get_fetchUnsoutaiouToke()
    try:
        unsoutaiou_col, unsoutaiou_data = unsoutaiou.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
    createDictFromList = InstanceFactory.get_createDictFromList()
    try:
        yusyutu_dict: Dict[Tuple,str] = \
            createDictFromList.create_yusyutuDict(unsoutaiou_data, 
                                                            unsoutaiou_col)
    except IndexError as e:
        recorder.out_log(e, '\n')
        recorder.out_file(e, '\n')
        sys.exit(1)


    # 出荷添付リスト(coa)を取得
    tenpCoa = InstanceFactory.get_fetchSyukkaListCoa()
    try:
        tenpCoa_col, tenpCoa_data = tenpCoa.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    # 出荷添付リスト(sitei_denpyo)を取得
    tenpSiteiDenpyo = InstanceFactory.get_fetchSyukkaListSiteiDenpyo()
    try:
        tenpSitei_col, tenpSitei_data = tenpSiteiDenpyo.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

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
    uriages = InstanceFactory.get_uriagesHonsyaToke(sumi_dicts, yusyutu_dict, 
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
                 createDictFromList
                 )

    # uriages_honsya に要素があったらSyukkaJissekiSyoukai_honsyaのインスタンスを生成
    if uriages_honsya:
        syukkaJissekiSyoukai_honsya = InstanceFactory.get_syukkaJissekiSyoukai( 
                 uriages_honsya, 
                 createJson,
                 '@0001',
                 unsouSet_col,
                 createDictFromList
                 )

    ''' ここから業務_packing>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    sumi_for_packing = InstanceFactory.get_fetchUriageSumiForPacking(syukka_date)
    try:
        sumi_for_packing_col, sumi_for_packing_data = sumi_for_packing.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    ''' productCan, tnjuデータを取得して辞書にする '''
    productCan = InstanceFactory.get_fetchProductCan()
    try:
        productCan_col, productCan_data = productCan.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

    tnju = InstanceFactory.get_fetchTnju()
    try:
        tnju_col, tnju_data = tnju.fetch_data()
    except Exception as e:
        recorder.out_log(f'処理を中止します：{e}', '\n')
        recorder.out_file(f'処理を中止します: {e}', '\n')
        sys.exit(1)

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
    except IndexError as e:
        recorder.out_log(e, '\n')
        recorder.out_file(e, '\n')
        sys.exit(1)


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
                    yusyutu_dict,
                    productCan_dic,
                    tnju_dic,
                    recorder
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
                                createDictFromList)
    # uriageForPacking_honsyaに要素があったらallPackings_honsyaのインスタンスを生成
    if uriageForPackings_honsya:
        allPackings_honsya = InstanceFactory.get_allPackings(
                               uriageForPackings_honsya,
                               createJson,
                               '@0001',
                               createDictFromList)
    
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
    hsCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['nonMetal']:
        for uriage in dic_uriages_for_coa['nonMetal']:
            hsCoas.append(InstanceFactory.get_hsCoa(uriage))
    mhsCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['metal']:
        for uriage in dic_uriages_for_coa['metal']:
            mhsCoas.append(InstanceFactory.get_mhsCoa(uriage))
    koitoCoas: List[IExcelOutput] = []
    if dic_uriages_for_coa['koito']:
        for uriage in dic_uriages_for_coa['koito']:
            koitoCoas.append(InstanceFactory.get_koitoCoa(uriage))


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
                                      '品管シートCoa',
                                      mhsCoa, mhs_coa_path,
                                      output_path, 
                                      barcodeFolder)
    if koitoCoas:
        for koitoCoa in koitoCoas:
            create_excel_outputs_args(excel_outputs_args,
                                      '品管シートCoa',
                                      koitoCoa, koito_coa_path,
                                      output_path, 
                                      barcodeFolder)

    '''
    Contextクラス(CreateTssBat)にexcel_outputs_argsを渡して、
    アウトプットを作ってもらう
    '''
    recorder.out_log('', '\n')
    recorder.out_file('', '\n')

    createTssBat:CreateTssBat = CreateTssBat(excel_outputs_args, recorder)
    createTssBat.create_tssBat()


    InstanceFactory.delete_cnxn
