from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING, Any, List
import platform
import sys
from decimal import Decimal
from create_yusyutu_dict import CreateYusyutuDict
from fetch_data_for_list import IFetchDataForList

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from recorder import Recorder
    from create_json import CreateJson
    from create_unsouSet import CreateUnsouSet
    from list_to_dict import ListToDict


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

    @classmethod
    def get_sql_server_effit(cls) -> None:
        if cls._sqlServerEffit is None:
            cls._setup_sql_path()
            from sql_server import SqlServer as SqlServerEffit
            cls._sqlServerEffit = SqlServerEffit()
            cls._cnxn_effit = cls._sqlServerEffit.get_cnxn()

    @classmethod
    def delete_cnxn(cls) -> None:
        if cls._sqlServerTss:
            cls._sqlServerTss.close()
        if cls._sqlServerEffit:
            cls._sqlServerEffit.close()


    @classmethod
    def get_fetchUnsoutaiouToke(cls) -> IFetchDataForList:
        from fetch_data_for_list import FetchUnsoutaiouToke
        ins_name: str = 'fetchUnsoutaiouToke'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
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
    def get_createJson(cls) -> "CreateJson":
        from create_json import CreateJson
        ins_name: str = 'createJson'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateJson()
        return cls._instances[ins_name]


    @classmethod
    def get_createUnsouSet(cls) -> "CreateUnsouSet":
        from create_unsouSet import CreateUnsouSet
        ins_name: str = 'createunsouSet'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateUnsouSet()
        return cls._instances[ins_name]


    @classmethod
    def get_createYusyutuDict(cls) -> "CreateYusyutuDict":
        from create_yusyutu_dict import CreateYusyutuDict
        ins_name: str = 'createYusyutuDict'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = CreateYusyutuDict()
        return cls._instances[ins_name]




    @classmethod
    def get_listToDict(cls) -> "ListToDict":
        from list_to_dict import ListToDict
        ins_name: str = 'listToDict'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = ListToDict()
        return cls._instances[ins_name]


