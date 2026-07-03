from typing import TYPE_CHECKING, List, Dict, Any


if TYPE_CHECKING:
    from IExcel_output import IExcelOutput
    from recorder import Recorder

class CreateTssBat:
    '''Contextクラス'''
    def __init__(self, excel_outputs:List[Dict[str,Any]],
                 recorder: "Recorder")-> None:
        self._excel_outputs = excel_outputs
        self._recorder = recorder


    def create_tssBat(self)-> None:

        for innerDic in self._excel_outputs:
            exe_path: str = innerDic['exe_path']
            output_path: str = innerDic['output_path']
            barcodeFolder: str = innerDic['barcodeFolder']
            excel_output: IExcelOutput = innerDic['excel_output']
            output_name: str = innerDic['output_name']
            

            txt = (f'{output_name}を作成します')
            self._recorder.out_log(txt)
            self._recorder.out_file(txt)

            excel_output.create_tssBat(exe_path, 
                                                output_path, 
                                                barcodeFolder)
