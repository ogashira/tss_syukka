import subprocess
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Set, Tuple

if TYPE_CHECKING:
    from create_json import CreateJson
    from uriage_for_packing import UriageForPacking
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from create_dict_from_list import CreateDictFromList


class IExcelOutput(ABC):
    @abstractmethod
    def create_excelOutput(self, exe_path: str, 
                           output_path: str, 
                           barcodeFolder: str = "")->object:
        pass


class SyukkaJissekiSyoukai(IExcelOutput):
    def __init__(self, uriages: List["UriageForSyukkaJisseki"], 
                 createJson: "CreateJson",
                 factory_name:str,
                 unsouSet_col: List[str],
                 createDictFromList: "CreateDictFromList"
                 )->None:

        self._uriages: List[UriageForSyukkaJisseki] = uriages
        self._createJson: CreateJson = createJson
        #unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
        self._unsouSet_col: List[str] = unsouSet_col
        self._createDictFromList = createDictFromList

        self._sumi_json_str: str = self._create_sumi_json_str()
        self._unsouSet_json_str: str = self._create_unsouSet_json_str()

        self._factoryName = self._get_factoryName(factory_name)
        self._syukkaKoujou = self._get_syukkaKoujou(factory_name)


    def _get_factoryName(self, factory_name)-> str:
        if factory_name == '@0001':
            return '本社'
        return '土気'

    def _get_syukkaKoujou(self, factory_name)-> str:
        if factory_name == '@0001':
            return '出荷工場：@0001 本社工場'
        return '出荷工場：@0002 土気工場'

    def _create_sumi_dict(self, 
                          sumi_dicts: List[Dict[str, Any]])-> None:
        for uriage in self._uriages:
            uriage.add_sumiData_myself(sumi_dicts)
            

    def _create_sumi_json_str(self) -> str:  
        sumi_dicts: List[Dict[str, Any]] = []
        self._create_sumi_dict(sumi_dicts)
        return self._createJson.create_json_str(sumi_dicts)

        
    def _create_unsouSet(self, unsouSet:Set[Tuple])->None:
        for uriage in self._uriages:
            uriage.add_unsouSet_myself(unsouSet)
        

    def _create_unsouSet_json_str(self)-> str:
        unsouSet:Set[Tuple] = set()
        self._create_unsouSet(unsouSet)
        unsouSet_dict: List[Dict[str,str]] = \
                self._createDictFromList.create_dict_from_set(
                                               self._unsouSet_col, 
                                               unsouSet
                                               )
        return self._createJson.create_json_str(unsouSet_dict)


    def create_excelOutput(self, exe_path: str, output_path: str, 
                           barcodeFolder: str = "")->object:
        args = [
                self._unsouSet_json_str,
                self._sumi_json_str,
                output_path,
                self._factoryName,
                self._syukkaKoujou,
                barcodeFolder
                ]

        result = subprocess.run([exe_path] + args, capture_output=True, text=True)
        print(f'unsouSet_{self._factoryName}: {self._unsouSet_json_str}')

        return result


class AllPackings(IExcelOutput):

    def __init__(self, uriages: List["UriageForPacking"], 
                 createJson: "CreateJson",
                 factory_name:str,
                 createDictFromList: "CreateDictFromList"
                 )->None:
        self._uriages: List[UriageForPacking] = uriages
        self._createJson = createJson
        self._factoryName = self._get_factoryName(factory_name)
        self._createDictFromList = createDictFromList

        setPacking = set()
        for uriage in uriages:
            uriage.create_setPacking(setPacking)
        '''setPacking
        {('T1210', 'IDK05', 'IDC4446'), ('T3820', ' '), ('T2880', 'H172'), ('T1039', ' '), ('T3500', 'H189'), ('T0320', ' '), ('T0060', ' '), ('T0020', ' ')}
        '''
        listPacking = list(setPacking)
        sortedPacking = sorted(listPacking)
        
        # packingタプルとUriageForPackingリストの辞書を作る
        packingDict:Dict[Tuple[str], List[UriageForPacking]] = {}
        for packing in sortedPacking:
            for uriage in uriages:
                uriage.add_packingDict_myself(packing, packingDict)


        # PackingForDenpyoのインスタンスを作る
        self._packingForDenpyos: List[PackingForDenpyo] = []
        for key_tuple, val_list in packingDict.items():
            packingForDenpyo: IExcelOutput = \
                    PackingForDenpyo(key_tuple, val_list, createJson)
            self._packingForDenpyos.append(packingForDenpyo)

        self._packing_json_str: str = self._create_packing_json_str()



    def _get_factoryName(self, factory_name)-> str:
        if factory_name == '@0001':
            return '本社'
        return '土気'


    def _create_packing_dict(self, packing_dicts: List[Dict[str, Any]])->None:
        for packingForDenpyo in self._packingForDenpyos:
            packingForDenpyo._create_packing_dict(packing_dicts)
        

    def _create_packing_json_str(self) -> str:  
        packing_dicts: List[Dict[str, Any]] = []
        self._create_packing_dict(packing_dicts)
        return self._createJson.create_json_str(packing_dicts)

    
    def create_excelOutput(self, exe_path: str, output_path: str, barcodeFolder: str = "") -> object:
        args = [
                output_path,
                self._packing_json_str,
                self._factoryName,
                ]

        result = subprocess.run([exe_path] + args, capture_output=True, text=True)
        print(f'packing_{self._factoryName}: {self._packing_json_str}')

        return result


class PackingForDenpyo(IExcelOutput):

    def __init__(self, tokuiCD_tpl: Tuple[str,...], 
                 uriageForPackings: List["UriageForPacking"],
                 createJson:"CreateJson") -> None:
        self._tokuiCD_tpl = tokuiCD_tpl
        self._uriageForPackings = uriageForPackings
        self._createJson = createJson


    def _create_packing_dict(self, 
                          packing_dicts: List[Dict[str, Any]])-> None:
        for uriage in self._uriageForPackings:
            uriage.add_packing_myself(packing_dicts)

        add_dict = {
                '依頼先':         '<<<<<',
                'cans':           '<<<<<',
                '総重量':         '<<<<<',
                '得意先コード':   '<<<<<',
                '納入先コード':   '<<<<<',
                '納入先名称１':   '<<<<<',
                '品名':           '<<<<<',
                '得意先注文ＮＯ': '<<<<<',
                '備考':           '<<<<<',
                '納期':           '<<<<<',
                '出荷':           '<<<<<',
                '出荷予定倉庫':   '<<<<<',
                'add':            '<<<<<'
                }

        packing_dicts.append(add_dict)

            

    def create_excelOutput(self, exe_path: str, output_path: str, barcodeFolder: str = "") -> object:
        pass

