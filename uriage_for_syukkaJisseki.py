from __future__ import annotations 
import glob
import shutil
import subprocess
from typing import Dict, Any, Tuple, Set, List, Optional
from get_idx import GetIdx
from recorder import Recorder
from check_hatumono import CheckHatumono

class UriageForSyukkaJisseki:
    def __init__(self, dict_data: Dict[str,Any], 
                 yusyutu_dict: Dict[Tuple, str],
                 tenpCoa_dicts: List[Dict[str, Any]],
                 recorder: Recorder)-> None:

        #yusyutu_dict = {('T0060', 'H172'):'y' , ('T0060', ''):'',.....}
        self._yusyutu_dict = yusyutu_dict
        self._tenpCoa_dicts = tenpCoa_dicts
        self._recorder = recorder
        self._factory: str = dict_data['factory_name']
        self._得意先コード: str = dict_data['得意先コード']
        self._納入先コード: str = dict_data['納入先コード']
        self._unsou_code: str = dict_data['unsou_code'] 
        self._unsou: str = dict_data['unsou']
        self._kubun_no: int = int(dict_data['kubun_no']) # TSSアウトプットの引数がintなので
        self._kubun: str = dict_data['kubun']
        self._出荷予定日: str = dict_data['出荷予定日']
        self._hinban: str = dict_data['hinban'] # S6-SV3800-1-U, S6-UV361-U
        self._品名: str = dict_data['品名']
        self._lot: str = dict_data['lot']
        self._受注数量: int = dict_data['受注数量']
        self._受注単位: str = dict_data['受注単位']
        self._納入先名称１: str = dict_data['納入先名称１']
        self._得意先注文ＮＯ: str = dict_data['得意先注文ＮＯ']
        self._備考: str = dict_data['備考']
        self._add: int = dict_data['add']
        self._納入先名: str = dict_data['納入先名']
        self._motoHinCD: str = dict_data['motoHinCD'] # 振替元品番
        self._motoTni: str = dict_data['motoTni']     # 振替元単位
        self._振替元数量: int = dict_data['振替元数量']
        self._cans: int = self._calc_cans()
        self._輸出向先: str = self._calc_yusyutu_mukesaki()
        self._hinban_for_coa: str = self._get_hinban_for_coa()
        self._coa_mksk: str = self._get_mksk()



    def _get_hinban_for_coa(self)-> str:
        hinban_for_coa: str = ''
        if self._受注単位 == 'CN':
            hinban_for_coa = self._hinban
        if self._motoTni == 'CN':
            hinban_for_coa = self._motoHinCD
        return hinban_for_coa


    def _get_mksk(self)-> str:
        mksk: str = ''
        for line_dic in self._tenpCoa_dicts:
            tokuiCD: str = line_dic['得意先ｺｰﾄﾞ']
            nonyuCD: Optional[str] = line_dic['納入先ｺｰﾄﾞ']
            if nonyuCD is None: # 添付リストの納入先コードがNoneなら' 'にする
                nonyuCD = ' '
            
            tenpCoa_hinban: str = line_dic['品番']

            if (tokuiCD == self._得意先コード and
                nonyuCD == self._納入先コード and
                tenpCoa_hinban == self._hinban_for_coa):
                mksk = line_dic['format']

        return mksk


    def _calc_cans(self)-> int:
        if self._受注単位 != 'CN':
            return self._振替元数量
        return self._受注数量

    def _calc_yusyutu_mukesaki(self)-> str:
        yusyutu_mukesaki = ''
        nonyu_code = self._納入先コード
        # effitからfetchした納入先コードが' 'の場合は''にする
        # unsoutaiouでーたは''なので。
        if nonyu_code ==  ' ':
            nonyu_code = ''
        tmpTuple = (self._得意先コード, nonyu_code)
        yusyutu_mukesaki = self._yusyutu_dict[tmpTuple]

        return yusyutu_mukesaki

    def add_sumiData_myself(self, dic_list: List[Dict[str, Any]])->None:
        tmp_dict = {
                '得意先コード':     self._得意先コード,
                '納入先コード':     self._納入先コード,
                'unsou_code':       self._unsou_code, 
                'unsou':            self._unsou,
                'kubun_no':         self._kubun_no,
                'kubun':            self._kubun,
                '出荷予定日':       self._出荷予定日, 
                'hinban':           self._hinban,
                '品名':             self._品名,
                'lot':              self._lot,
                'cans':             self._cans,
                '受注数量':         self._受注数量,
                '受注単位':         self._受注単位,
                '納入先名称１':     self._納入先名称１,
                '輸出向先':         self._輸出向先,
                '得意先注文ＮＯ':   self._得意先注文ＮＯ,
                '備考':             self._備考,
                'add':              self._add,
                '納入先名':         self._納入先名
                }
        dic_list.append(tmp_dict)


    def add_unsouSet_myself(self, unsouSet:Set[Tuple])-> None:
        '''
        unsouSetにデータがなければ、出荷実績照会はつくられない。
        unosu_codeが無い、東新油脂向けや、メーカー直送(PI-301など)はunsou_code = ' 'なので、
        出荷実績照会はつくられない
        '''
        if self._unsou_code == ' ': #運送屋がなければunsouSetはつくらない
            return
        tmpTuple = (self._unsou_code, self._kubun_no, self._輸出向先)
        unsouSet.add(tmpTuple)


    def add_myself_for_coa(self, 
            dic_uriages_for_coa: Dict[str,List[UriageForSyukkaJisseki]])-> None:
        if self._coa_mksk == '':
            return 
        if self._coa_mksk == '小糸':
            dic_uriages_for_coa['koito'].append(self)
            return
        if self._coa_mksk == 'ﾒﾀﾙ':
            dic_uriages_for_coa['metal'].append(self)
            return

        dic_uriages_for_coa['nonMetal'].append(self)


    def create_hsCoa(self, exe_path: str,
                     output_path: str,
                     checkHatumono: CheckHatumono) -> None:
        '''
        HsCoaから呼ばれる。
        成績書を作る
        '''
        if self._coa_mksk == '小糸' or self._coa_mksk == 'ﾒﾀﾙ':
            return

        is_metal: bool = False
        could_copy_coa: bool = checkHatumono.copy_coa(self._lot, 
                                          self._coa_mksk, output_path, is_metal)

        txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})をフォルダにコピーしました。\n'
        if not could_copy_coa:
            txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})が無いので作成します。\n'
            args = [
                    "--mksk", self._coa_mksk,
                    "--lot", self._lot,
                    "--outputdir", output_path
                    ]

            result = subprocess.run([exe_path] + args, capture_output=True, text=True)
            if result.returncode == 1:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 初物ではありません\n' 
            elif result.returncode == 2:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 初物NG です！\n' 
            else:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 成績書作成できません！\n' 
            txt = f'{txt}{add_txt}'
            

        self._recorder.out_log(txt)
        self._recorder.out_file(txt)


    def create_mhsCoa(self, exe_path: str,
                      output_path: str,
                      checkHatumono: CheckHatumono) -> None:
        '''
        MhsCoaから呼ばれる。
        成績書を作る
        '''
        if self._coa_mksk != 'ﾒﾀﾙ':
            return

        is_metal: bool = True
        could_copy_coa: bool = checkHatumono.copy_coa(self._lot, 
                                          self._coa_mksk, output_path, is_metal)

        txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})をフォルダにコピーしました。\n'
        if not could_copy_coa:
            txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})が無いので作成します。\n'

            args = [
                    "--lot", self._lot,
                    "--outputdir", output_path
                    ]

            result = subprocess.run([exe_path] + args, capture_output=True, text=True)

            if result.returncode == 1:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 初物ではありません\n' 
            elif result.returncode == 2:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 初物NG です！\n' 
            else:
                add_txt = f'{self._hinban_for_coa} {self._lot} {self._coa_mksk}: 成績書作成できません！\n' 
            txt = f'{txt}{add_txt}'


        self._recorder.out_log(txt, '\n')
        self._recorder.out_file(txt, '\n')


    def create_koitoCoa(self, output_path: str,
                        checkHatumono: CheckHatumono)-> None:

        if self._coa_mksk != '小糸':
            return

        is_metal: bool = False
        could_copy_coa: bool = checkHatumono.copy_coa(self._lot, 
                                          self._coa_mksk, output_path, is_metal)

        txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})をフォルダにコピーしました。\n'
        if not could_copy_coa:
            txt = f'{self._coa_mksk}向け成績書 {self._hinban_for_coa}({self._lot})がありません。技術部に依頼してください!\n'

        self._recorder.out_log(txt, '\n')
        self._recorder.out_file(txt, '\n')
