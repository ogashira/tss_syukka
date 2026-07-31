import subprocess
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Set, Tuple
from decimal import Decimal
from recorder import Recorder


if TYPE_CHECKING:
    from create_json import CreateJson
    from uriage_for_packing import UriageForPacking
    from uriage_for_syukkaJisseki import UriageForSyukkaJisseki
    from create_dict_from_list import CreateDictFromList
    from check_hatumono import CheckHatumono


class IExcelOutput(ABC):
    @abstractmethod
    def create_tssBat(self, exe_path: str, 
                           output_path: str, 
                           barcodeFolder: str = "")-> None:
        pass


class SyukkaJissekiSyoukai(IExcelOutput):
    def __init__(self, uriages: List["UriageForSyukkaJisseki"], 
                 createJson: "CreateJson",
                 factory_name:str,
                 unsouSet_col: List[str],
                 createDictFromList: "CreateDictFromList",
                 recorder: Recorder
                 )->None:

        self._uriages: List[UriageForSyukkaJisseki] = uriages
        self._createJson: CreateJson = createJson
        #unsouSet_col = [ 'unsou_code', 'kubun_no', 'yusyutu' ]
        self._unsouSet_col: List[str] = unsouSet_col
        self._createDictFromList = createDictFromList
        self._recorder = recorder

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


    def create_tssBat(self, exe_path: str, output_path: str, 
                           barcodeFolder: str = "")-> None:

        output_name = f'出荷実績照会_{self._factoryName}'

        if self._unsouSet_json_str == '[]':
            result_txt = f'{output_name}はありませんでした'
            self._recorder.out_log(result_txt, '\n')
            self._recorder.out_file(result_txt, '\n')
            return

        args = [
                self._unsouSet_json_str,
                self._sumi_json_str,
                output_path,
                self._factoryName,
                self._syukkaKoujou,
                barcodeFolder
                ]

        result = subprocess.run([exe_path] + args, capture_output=True, text=True)
        returncode: int = result.returncode

        code_txt = f'{output_name}のreturncode = {returncode}'
        self._recorder.out_log(code_txt, '\n')
        self._recorder.out_file(code_txt, '\n')


    def collect_uriage_for_coa(self,
        dic_uriages_for_coa: Dict[str,List['UriageForSyukkaJisseki']])-> None:
        '''
        dic_uriages_for_coa = 
        {'koito':[........], 'metal': [......], 'nonMetal': [.......]} 
        mkskがあるuriage_for_syukkaJissekiを集めて
        dic_uriages_for_coaに入れる
        '''
        for uriage in self._uriages:
            uriage.add_myself_for_coa(dic_uriages_for_coa)



class AllPackings(IExcelOutput):

    def __init__(self, uriages: List["UriageForPacking"], 
                 createJson: "CreateJson",
                 factory_name:str,
                 createDictFromList: "CreateDictFromList",
                 recorder: Recorder
                 )->None:
        self._uriages: List[UriageForPacking] = uriages
        self._createJson = createJson
        self._factoryName = self._get_factoryName(factory_name)
        self._createDictFromList = createDictFromList
        self._recorder = recorder

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
            packingForDenpyo: PackingForDenpyo = \
                    PackingForDenpyo(key_tuple, val_list, createJson)
            self._packingForDenpyos.append(packingForDenpyo)

        self._packing_json_str: str = self._create_packing_json_str()


    def show_uriKin_for_excel(self, ws, myborder)-> None:
        for denpyo in self._packingForDenpyos:
            denpyo.show_uriKin_to_excel(ws, myborder)


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

    
    def create_tssBat(self, exe_path: str, output_path: str, 
                                barcodeFolder: str = "") -> None:
        output_name = f'{self._factoryName}業務_packing'

        args = [
                output_path,
                self._packing_json_str,
                self._factoryName
                ]


        result = subprocess.run([exe_path] + args, capture_output=True, text=True)
        returncode: int = result.returncode

        code_txt = f'{output_name}のreturncode = {returncode}'
        self._recorder.out_log(code_txt, '\n')
        self._recorder.out_file(code_txt, '\n')



class PackingForDenpyo:

    def __init__(self, tokuiCD_tpl: Tuple[str,...], 
                 uriageForPackings: List["UriageForPacking"],
                 createJson:"CreateJson") -> None:
        '''
        tokuiCD_tpl = ('T1210', 'IDK05', 'IDC4446')または ('T3820', ' ')
        '''
        self._isExport = False 
        if len(tokuiCD_tpl) == 3:
            self._isExport = True
        self._tokuiCD = ' '
        self._nonyuCD = ' '
        self._tyuban  = ' '
        if self._isExport:
            self._tokuiCD = tokuiCD_tpl[0]
            self._nonyuCD = tokuiCD_tpl[1]
            self._tyuban = tokuiCD_tpl[2] # 注文No
        else:
            self._tokuiCD = tokuiCD_tpl[0]
            self._nonyuCD = tokuiCD_tpl[1]
            self._tyuban = ' '


        self._uriageForPackings = uriageForPackings
        self._createJson = createJson

        '''ここで、uriageForPackingsに総重量sumWeightをセットする'''
        self._set_sumWeight_to_uriageForPacking()

        '''売価を求める'''
        self._uriKin = self._calc_sumUriKin()


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


    ''' uriageForPackingに総重量sumWeightを追加する>>>>>>>>>>>>>>>>>'''
    def _calc_sumWeight(self)-> Decimal:
        sumWeight: Decimal = Decimal('0')
        for uriage in self._uriageForPackings:
            sumWeight = uriage.plus_myWeight(sumWeight)
        return sumWeight


    def _set_sumWeight_to_uriageForPacking(self):
        sumWeight: Decimal = self._calc_sumWeight()
        for uriage in self._uriageForPackings:
            uriage.set_sumWeight(sumWeight)

    '''売価を求める(伝票ごと)>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'''
    def _calc_sumUriKin(self)-> Decimal:
        sumUriKin: Decimal = Decimal('0')
        for uriage in self._uriageForPackings:
            sumUriKin = uriage.plus_myUriKin(sumUriKin)

        return sumUriKin


    def show_uriKin_to_excel(self, ws, myborder)-> None:
        
        def put_uriKin_for_export(i:int)-> None:
            if ((ws.cell(i, 4).value == self._tokuiCD and
                 ws.cell(i, 5).value == self._nonyuCD and
                 ws.cell(i, 8).value == self._tyuban) and not 
                (ws.cell(i + 1, 4).value == self._tokuiCD and
                 ws.cell(i + 1, 5).value == self._nonyuCD and
                 ws.cell(i + 1, 8).value == self._tyuban)):
                # CDが同じで下の行が違っていたら
                ws.cell(i, lastCol).value = self._uriKin
                ws.cell(i, lastCol).border = myborder
                ws.cell(i, lastCol).number_format = "#,##" # カンマ表記

        def put_urikin_for_notExport(i:int)-> None:
            if ((ws.cell(i, 4).value == self._tokuiCD and
                 ws.cell(i, 5).value == self._nonyuCD) and not
                (ws.cell(i + 1, 4).value == self._tokuiCD and
                 ws.cell(i + 1, 5).value == self._nonyuCD)):
                # CDが同じで下の行が違っていたら
                ws.cell(i, lastCol).value = self._uriKin
                ws.cell(i, lastCol).border = myborder
                ws.cell(i, lastCol).number_format = "#,##" # カンマ表記

        lastRow: int = ws.max_row
        lastCol: int = ws.max_column
        i: int = 0
        for i in range(2, lastRow + 1):
            if self._isExport:
                put_uriKin_for_export(i)
            else:
                put_urikin_for_notExport(i)




class HsCoa(IExcelOutput):

    def __init__(self, uriage: "UriageForSyukkaJisseki", 
                 checkHatumono: "CheckHatumono")-> None:
        self._uriage = uriage
        self._checkHatumono = checkHatumono

    def create_tssBat(self, exe_path: str, 
                           output_path: str, 
                           barcodeFolder: str = "")-> None:

        self._uriage.create_hsCoa(exe_path, output_path, self._checkHatumono)



class MhsCoa(IExcelOutput):

    def __init__(self, uriage: "UriageForSyukkaJisseki",
                 checkHatumono: "CheckHatumono")-> None:
        self._uriage = uriage
        self._checkHatumono = checkHatumono


    def create_tssBat(self, exe_path: str, 
                           output_path: str, 
                           barcodeFolder: str = "")-> None:

        self._uriage.create_mhsCoa(exe_path, output_path,
                                   self._checkHatumono)


class KoitoCoa(IExcelOutput):

    def __init__(self, uriage: "UriageForSyukkaJisseki",
                 checkHatumono: "CheckHatumono")-> None:
        self._uriage = uriage
        self._checkHatumono = checkHatumono

    def create_tssBat(self, exe_path: str, 
                           output_path: str, 
                           barcodeFolder: str = "")-> None:

        self._uriage.create_koitoCoa(output_path, self._checkHatumono)
