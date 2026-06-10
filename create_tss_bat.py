from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from IExcel_output import IExcelOutput

class CreateTssBat:
    '''Contextクラス'''
    def __init__(self, excel_outputs:List[Dict[str,Any]])-> None:
        self._excel_outputs = excel_outputs


    def create_tssBat(self)-> Dict[str, int]:

        results_dic: Dict[str, int] = {}
        for innerDic in self._excel_outputs:
            exe_path: str = innerDic['exe_path']
            output_path: str = innerDic['output_path']
            barcodeFolder: str = innerDic['barcodeFolder']
            excel_output: IExcelOutput = innerDic['excel_output']
            output_name: str = innerDic['output_name']

            result = excel_output.create_tssBat(exe_path, 
                                                output_path, 
                                                barcodeFolder)
            results_dic[output_name] = result.returncode

        return results_dic

