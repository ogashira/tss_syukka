import glob
import pdfplumber
import shutil


class CheckHatumono:

    def __init__(self)-> None:
        pass

    def copy_coa(self, lot: str, mksk: str, output_path: str, 
                                            is_metal: bool)-> bool:
        """
        初物でないCoaが櫻田フォルダにあればoutput_pathにコピーする
        コピーできたらTrueを、できなかったらFalseを返す
        """
        could_copy_coa: bool = False 

        directory = r'//192.168.1.247/共有/営業課ﾌｫﾙﾀﾞ/testreport/櫻田/'
        path = directory + '*' + lot + '*' + mksk + '.pdf'
        if is_metal:
            path = directory + '*' + lot + '*' + '.pdf'
         
        
        files = glob.glob(path)
        if len(files) > 0:
            for file in files:
                if not self.check_is_hatumono(file): # 初物でなかったらコピー
                    shutil.copy(file, output_path)
                    could_copy_coa = True
                    break

        return could_copy_coa



    def check_is_hatumono(self, pdf_path)-> bool:
        
        is_hatumono = False
        target_text = "初物 要チェック"

        with pdfplumber.open(pdf_path) as pdf:

            # 1ページずつループ
            for i, page in enumerate(pdf.pages):
                # ページからテキストを抽出
                text = page.extract_text()
                
                # テキストが存在し、かつターゲット文字列が含まれているか
                if text and target_text in text:
                    is_hatumono = True
        
        return is_hatumono
