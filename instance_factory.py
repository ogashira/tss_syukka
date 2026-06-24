from typing import Dict, TYPE_CHECKING, Any, List, Tuple
import platform
import sys
from IExcel_output import IExcelOutput, SyukkaJissekiSyoukai, AllPackings, \
        HsCoa, MhsCoa, KoitoCoa
from fetch_data_for_list import IFetchDataForList

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from create_json import CreateJson
    from create_dict_from_list import CreateDictFromList
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from uriage_for_packing import UriageForPacking
    from recorder import Recorder


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
    def get_fetchUnsoutaiouToke(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchUnsoutaiouToke
        ins_name: str = 'fetchUnsoutaiouToke'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = FetchUnsoutaiouToke()
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
                                yusyutu_dict: Dict[Tuple,str],
                                tenpCoa_dicts: List[Dict[str,Any]],
                                recorder: "Recorder") -> Tuple:
        #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        # sumi_dicts = [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
        # tenpCoa_dicts =[{'得意先ｺｰﾄﾞ':'T1020', '納入先コード':None, .....},{.....}....] 
        from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
        ins_name: str = 'uriagesHonsyaToke'
        uriages_honsya: List[UriageForSyukkaJisseki] = []
        uriages_toke: List[UriageForSyukkaJisseki] = []
        #Uriageインスタンス生成し、uriages_toke, uriages_honsyaに分ける
        if ins_name not in cls._instances:
            for sumi_dict in sumi_dicts:
                uriage_instance: UriageForSyukkaJisseki = \
                        UriageForSyukkaJisseki(sumi_dict, 
                                    yusyutu_dict, tenpCoa_dicts, recorder)
                if sumi_dict['factory_name'] == '@0001':
                    uriages_honsya.append(uriage_instance)
                    continue
                uriages_toke.append(uriage_instance)

            cls._instances[ins_name] = (uriages_honsya, uriages_toke)

        return cls._instances[ins_name]

    
    @classmethod
    def get_syukkaJissekiSyoukai(cls, 
                                 uriages: List["UriageForSyukkaJisseki"],
                                 createJson: "CreateJson",
                                 factory_name: str,
                                 unsouSet_col: List[str],
                                 createDictFromLIst: "CreateDictFromList"
                                 ) -> IExcelOutput:
        syukkaJissekiSyoukai: IExcelOutput = SyukkaJissekiSyoukai(
                uriages,
                createJson,
                factory_name,
                unsouSet_col,
                createDictFromLIst)
        return  syukkaJissekiSyoukai

    
    @classmethod
    def get_uriageForPackingsHonsyaToke(cls, 
                                sumi_for_packing_dicts: List[Dict[str,Any]],
                                yusyutu_dict: Dict[Tuple,str],
                                productCan_dic: Dict[str,str],
                                tnju_dic: Dict[str,Any], 
                                recorder: "Recorder") -> Tuple:
        #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        # [{'得意先コード':'T1020', '納入先コード':' ', .....},{.....}....]
        from uriage_for_packing import UriageForPacking
        ins_name: str = 'uriagePackingsHonsyaToke'
        uriageForPackings_toke: List[UriageForPacking] = []
        uriageForPackings_honsya: List[UriageForPacking] = []
        if ins_name not in cls._instances:
            for sumi_for_packing_dict in sumi_for_packing_dicts:
                uriageForPacking_instance: UriageForPacking = \
                        UriageForPacking(sumi_for_packing_dict, 
                                         yusyutu_dict,
                                         productCan_dic,
                                         tnju_dic,
                                         recorder)
                if sumi_for_packing_dict['factory_name'] == '@0001':
                    uriageForPackings_honsya.append(uriageForPacking_instance)
                    continue
                uriageForPackings_toke.append(uriageForPacking_instance)

            cls._instances[ins_name] = (uriageForPackings_honsya, 
                                            uriageForPackings_toke)

        return cls._instances[ins_name]


    @classmethod
    def get_allPackings(cls, 
                         uriageForPackings: List["UriageForPacking"],
                         createJson: "CreateJson",
                         factory_name: str,
                         createDictFromLIst: "CreateDictFromList"
                         ) -> IExcelOutput:

        allPackings: AllPackings = AllPackings(
                uriageForPackings,
                createJson,
                factory_name,
                createDictFromLIst)

        return  allPackings

    
    @classmethod
    def get_hsCoa(cls, uriage: "UriageForSyukkaJisseki"
                         ) -> IExcelOutput:

        hsCoa: HsCoa = HsCoa(uriage)

        return  hsCoa

    
    @classmethod
    def get_mhsCoa(cls, uriage: "UriageForSyukkaJisseki"
                         ) -> IExcelOutput:

        mhsCoa: MhsCoa = MhsCoa(uriage)

        return  mhsCoa

    
    @classmethod
    def get_koitoCoa(cls, uriage: "UriageForSyukkaJisseki"
                         ) -> IExcelOutput:

        koitoCoa: KoitoCoa = KoitoCoa(uriage)

        return  koitoCoa
