from typing import Dict, TYPE_CHECKING, Any, List, Tuple
import platform
import sys
from IExcel_output import IExcelOutput, SyukkaJissekiSyoukai, AllPackings, \
        HsCoa, MhsCoa, KoitoCoa
from IAdd_to_yoteiSouko import AddForCoa, AddForSiteiDenpyo, AddForEigyosyo, \
        AddForDohai, AddForWeekdayDiff, IAddToYoteiSouko
from fetch_data_for_list import IFetchDataForList

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from create_json import CreateJson
    from create_dict_from_list import CreateDictFromList
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from uriage_for_packing import UriageForPacking
    from recorder import Recorder
    from create_tss_bat import CreateTssBat
    from check_hatumono import CheckHatumono


class InstanceFactory:
    '''
    各モジュールのインポートは必要な時にメソッド内で行う。
    冒頭でまとめてやると実行速度が急激に遅くなったため
    '''

    _sqlServerTss: Any = None
    _sqlServerEffit: Any = None
    _cnxn_tss = None
    _cnxn_effit = None

    _instances: Dict[str, Any] = {}

    @classmethod
    def _setup_sql_path(cls) -> None:
        """SQLサーバー用モジュールのパスを通す (一度だけ実行)"""
        if 'sql_path_setup' in cls._instances:
            return
            
        shared_folder_path: str = r'./'
        if platform.system() == 'Linux':
            shared_folder_path = \
                r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
        elif platform.system() == 'Windows':
            shared_folder_path = \
                r'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
        
        if shared_folder_path not in sys.path:
            sys.path.append(shared_folder_path)
        cls._instances['sql_path_setup'] = True

    @classmethod
    def get_sql_server_tss(cls) -> None:
        if cls._sqlServerTss is None:
            cls._setup_sql_path()
            from sql_server_tss_addmin import SqlServer as SqlServerTss 
            cls._sqlServerTss = SqlServerTss()
            cls._cnxn_tss = cls._sqlServerTss.get_cnxn()

    # TODO テストが終わったら、sql_server_testをsql_serverに戻す
    @classmethod
    def get_sql_server_effit(cls) -> None:
        if cls._sqlServerEffit is None:
            cls._setup_sql_path()
            from sql_server_test import SqlServer as SqlServerEffit
            cls._sqlServerEffit = SqlServerEffit()
            cls._cnxn_effit = cls._sqlServerEffit.get_cnxn()

    @classmethod
    def delete_cnxn(cls) -> None:
        if cls._sqlServerTss:
            cls._sqlServerTss.close()
        if cls._sqlServerEffit:
            cls._sqlServerEffit.close()


    @classmethod
    def get_recorder(cls, mydir) -> "Recorder":
        from recorder import Recorder
        ins_name: str = 'recorder'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = Recorder(mydir)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchTyuzan(cls, syukka_date) -> IFetchDataForList:
        from fetch_data_for_list import FetchTyuzan
        ins_name: str = 'fetchTyuzan'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchTyuzan(cls._cnxn_effit, syukka_date)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchUnsoutaiouToke(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchUnsoutaiouToke
        ins_name: str = 'fetchUnsoutaiouToke'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchUnsoutaiouToke(cls._cnxn_effit)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchUnsoutaiouHonsya(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchUnsoutaiouHonsya
        ins_name: str = 'fetchUnsoutaiouHonsya'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchUnsoutaiouHonsya(cls._cnxn_effit)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchUriageSumi(cls, syukka_date) -> IFetchDataForList:
        from fetch_data_for_list import FetchUriageSumi
        ins_name: str = 'fetchUriageSumi'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchUriageSumi(cls._cnxn_effit, 
                                                       syukka_date)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchUriageSumiForPacking(cls, syukka_date) -> IFetchDataForList:
        from fetch_data_for_list import FetchUriageSumiForPacking
        ins_name: str = 'fetchUriageSumiForPacking'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchUriageSumiForPacking(
                                              cls._cnxn_effit, syukka_date)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchSyukkaListSiteiDenpyo(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchSyukkaListSiteiDenpyo
        ins_name: str = 'fetchSyukkaListSiteiDenpyo'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchSyukkaListSiteiDenpyo()
        return cls._instances[ins_name]


    @classmethod
    def get_fetchSyukkaListCoa(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchSyukkaListCoa
        ins_name: str = 'fetchSyukkaListCoa'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchSyukkaListCoa()
        return cls._instances[ins_name]


    @classmethod
    def get_fetchProductCan(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchProductCan
        ins_name: str = 'fetchProductCan'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchProductCan(cls._cnxn_effit)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchTnju(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchTnju
        ins_name: str = 'fetchTnju'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchTnju(cls._cnxn_effit)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchCalenderUnsouya(cls, syukka_date: str) -> IFetchDataForList:
        from fetch_data_for_list import FetchCalenderUnsouya
        ins_name: str = 'fetchCalenderUnsouya'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchCalenderUnsouya(
                                  cls._cnxn_effit, syukka_date)
        return cls._instances[ins_name]


    @classmethod
    def get_fetchCalenderToyo(cls, syukka_date: str) -> IFetchDataForList:
        from fetch_data_for_list import FetchCalenderToyo
        ins_name: str = 'fetchCalenderToyo'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchCalenderToyo(
                                  cls._cnxn_effit, syukka_date)
        return cls._instances[ins_name]


    @classmethod
    def get_createJson(cls) -> "CreateJson":
        from create_json import CreateJson
        ins_name: str = 'createJson'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateJson()
        return cls._instances[ins_name]


    @classmethod
    def get_createDictFromList(cls) -> "CreateDictFromList":
        from create_dict_from_list import CreateDictFromList
        ins_name: str = 'createDictFromList'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateDictFromList()
        return cls._instances[ins_name]


    @classmethod
    def get_uriagesHonsyaToke(cls, 
                                sumi_dicts: List[Dict[str,Any]],
                                yusyutu_dicts: Dict[str, Dict[Tuple,str]],
                                tenpCoa_dicts: List[Dict[str,Any]],
                                recorder: "Recorder") -> Tuple:
        # sumi_dicts = [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
        # tenpCoa_dicts =[{'得意先ｺｰﾄﾞ':'T1020', '納入先コード':None, .....},{.....}....] 
        from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
        ins_name: str = 'uriagesHonsyaToke'
        uriages_honsya: List[UriageForSyukkaJisseki] = []
        uriages_toke: List[UriageForSyukkaJisseki] = []
        #Uriageインスタンス生成し、uriages_toke, uriages_honsyaに分ける
        if ins_name not in cls._instances:
            for sumi_dict in sumi_dicts:
                if sumi_dict['factory_name'] == '@0001':
                    uriage_instance: UriageForSyukkaJisseki = \
                        UriageForSyukkaJisseki(sumi_dict, 
                                               yusyutu_dicts['honsya'], 
                                               tenpCoa_dicts, 
                                               recorder)
                    uriages_honsya.append(uriage_instance)
                else:
                    uriage_instance: UriageForSyukkaJisseki = \
                        UriageForSyukkaJisseki(sumi_dict, 
                                               yusyutu_dicts['toke'], 
                                               tenpCoa_dicts, 
                                               recorder)
                    uriages_toke.append(uriage_instance)

            cls._instances[ins_name] = (uriages_honsya, uriages_toke)

        return cls._instances[ins_name]

    
    @classmethod
    def get_syukkaJissekiSyoukai(cls, 
                                 uriages: List["UriageForSyukkaJisseki"],
                                 createJson: "CreateJson",
                                 factory_name: str,
                                 unsouSet_col: List[str],
                                 createDictFromLIst: "CreateDictFromList",
                                 recorder: "Recorder"
                                 ) -> IExcelOutput:
        syukkaJissekiSyoukai: IExcelOutput = SyukkaJissekiSyoukai(
                uriages,
                createJson,
                factory_name,
                unsouSet_col,
                createDictFromLIst,
                recorder)
        return  syukkaJissekiSyoukai

    
    @classmethod
    def get_uriageForPackingsHonsyaToke(cls, 
                                sumi_for_packing_dicts: List[Dict[str,Any]],
                                yusyutu_dicts: Dict[str, Dict[Tuple,str]],
                                leadTime_dicts: Dict[str, Dict[Tuple,int]],
                                productCan_dic: Dict[str,str],
                                tnju_dic: Dict[str,Any], 
                                recorder: "Recorder",
                                addToYoteiSoukos: Dict[str, IAddToYoteiSouko]
                                )-> Tuple:
        #yusyutu_dict = {('T0060', 'H172'): 'y', ('T0060', ''): '',.....}
        # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
        from uriage_for_packing import UriageForPacking
        ins_name: str = 'uriagePackingsHonsyaToke'
        uriageForPackings_toke: List[UriageForPacking] = []
        uriageForPackings_honsya: List[UriageForPacking] = []
        if ins_name not in cls._instances:
            for sumi_for_packing_dict in sumi_for_packing_dicts:
                if sumi_for_packing_dict['factory_name'] == '@0001':
                    uriageForPacking_instance: UriageForPacking = \
                        UriageForPacking(sumi_for_packing_dict, 
                                         yusyutu_dicts['honsya'],
                                         leadTime_dicts['honsya'],
                                         productCan_dic,
                                         tnju_dic,
                                         recorder,
                                         addToYoteiSoukos)
                    uriageForPackings_honsya.append(uriageForPacking_instance)
                else:
                    uriageForPacking_instance: UriageForPacking = \
                        UriageForPacking(sumi_for_packing_dict, 
                                         yusyutu_dicts['toke'],
                                         leadTime_dicts['toke'],
                                         productCan_dic,
                                         tnju_dic,
                                         recorder,
                                         addToYoteiSoukos)
                    uriageForPackings_toke.append(uriageForPacking_instance)

            cls._instances[ins_name] = (uriageForPackings_honsya, 
                                            uriageForPackings_toke)

        return cls._instances[ins_name]


    @classmethod
    def get_allPackings(cls, 
                         uriageForPackings: List["UriageForPacking"],
                         createJson: "CreateJson",
                         factory_name: str,
                         createDictFromLIst: "CreateDictFromList",
                         recorder: "Recorder"
                         ) -> IExcelOutput:

        allPackings: AllPackings = AllPackings(
                uriageForPackings,
                createJson,
                factory_name,
                createDictFromLIst,
                recorder)

        return  allPackings

    
    @classmethod
    def get_hsCoa(cls, uriage: "UriageForSyukkaJisseki",
                  checkHatumono: "CheckHatumono"
                         ) -> IExcelOutput:

        hsCoa: IExcelOutput = HsCoa(uriage, checkHatumono)

        return  hsCoa

    
    @classmethod
    def get_mhsCoa(cls, uriage: "UriageForSyukkaJisseki",
                  checkHatumono: "CheckHatumono"
                         ) -> IExcelOutput:

        mhsCoa: IExcelOutput = MhsCoa(uriage, checkHatumono)

        return  mhsCoa

    
    @classmethod
    def get_koitoCoa(cls, uriage: "UriageForSyukkaJisseki",
                     checkHatumono: "CheckHatumono"
                         ) -> IExcelOutput:

        koitoCoa: IExcelOutput = KoitoCoa(uriage, checkHatumono)

        return  koitoCoa


    @classmethod
    def get_checkHatumono(cls) -> "CheckHatumono":
        from check_hatumono import CheckHatumono
        ins_name: str = 'checkHatumono'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CheckHatumono()
        return cls._instances[ins_name]


    @classmethod
    def get_createTssBat(cls, excel_outputs_args:List[Dict[str,Any]],
                         recorder: "Recorder") -> "CreateTssBat":
        from create_tss_bat import CreateTssBat
        ins_name: str = 'createTssBat'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateTssBat(excel_outputs_args, recorder)
        return cls._instances[ins_name]


    @classmethod
    def get_addForCoa(cls, tenpCoa_dicts:List[Dict[str,Any]]
                              )-> IAddToYoteiSouko:
        addForCoa: IAddToYoteiSouko = AddForCoa(tenpCoa_dicts)
        return addForCoa


    @classmethod
    def get_addForSiteiDenpyo(cls, tenpSitei_dicts:List[Dict[str,Any]] 
                              )-> IAddToYoteiSouko:
        addForSiteiDenpyo: IAddToYoteiSouko = AddForSiteiDenpyo(tenpSitei_dicts)
        return addForSiteiDenpyo


    @classmethod
    def get_addForEigyosyo(cls)-> IAddToYoteiSouko:
        addForEigyosyo: IAddToYoteiSouko = AddForEigyosyo()
        return addForEigyosyo


    @classmethod
    def get_addForDohai(cls)-> IAddToYoteiSouko:
        addForDohai: IAddToYoteiSouko = AddForDohai()
        return addForDohai


    @classmethod
    def get_addForWeekdayDiff(cls, list_YMD: List[str], 
                 dict_unso_holiday: Dict[str, str], 
                 dict_toyo_holiday)-> IAddToYoteiSouko:
        addForWeekdayDiff: IAddToYoteiSouko = AddForWeekdayDiff( list_YMD, 
                                        dict_unso_holiday, dict_toyo_holiday)
        return addForWeekdayDiff


