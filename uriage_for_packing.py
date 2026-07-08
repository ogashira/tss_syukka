from __future__ import annotations 
from decimal import Decimal
from recorder import Recorder
from IAdd_to_yoteiSouko import IAddToYoteiSouko
'''
全ての型ヒントの判定を遅延評価する。UriageForPacking自信のクラス名を型ヒントとして
使っているので、エラーを出さないため。 61行目
'''
from typing import Dict, Any, Tuple, Set, List

class UriageForPacking:
    def __init__(self, dict_data: Dict[str,Any], 
                 yusyutu_dict: Dict[Tuple, str],
                 leadTime_dict: Dict[Tuple, int],
                 productCan_dic: Dict[str,str],
                 tnju_dic: Dict[str, Any], recorder:Recorder,
                 addToYoteiSoukos: Dict[str, IAddToYoteiSouko])-> None:

        #yusyutu_dict = {('T0060', 'H172'):'y', ('T0060', ''):'',.....}
        self._yusyutu_dict = yusyutu_dict
        self._leadTime_dict = leadTime_dict
        self._productCan_dic = productCan_dic
        self._tnju_dic = tnju_dic
        self._recorder = recorder
        self._addToYoteiSoukos = addToYoteiSoukos
        self._factory: str = dict_data['factory_name']
        self._依頼先: str = dict_data['依頼先']
        self._得意先コード: str = dict_data['得意先コード']
        self._納入先コード: str = dict_data['納入先コード']
        self._納入先名称１: str = dict_data['納入先名称１']
        self._売り品番: str = dict_data['売り品番']
        self._品名: str = dict_data['品名']
        self._得意先注文ＮＯ: str = dict_data['得意先注文ＮＯ']
        self._備考: str = dict_data['備考']
        self._出荷日: str = dict_data['出荷日']
        self._納期: str = dict_data['納期']
        self._受注数量: int = dict_data['uriKosu']
        self._受注単位: str = dict_data['受注単位']

        add: int = 0
        if not (dict_data['add'] == ' ' or dict_data['add'] == ''):
            add = int(dict_data['add'])
        self._add: int = add  # 空白なら0, それ以外はintにキャストする

        self._振替元品番: str = dict_data['motoHinCD']

        self._振替元数量: int = 0
        if dict_data['motoSu'] is not None:
            self._振替元数量: int = dict_data['motoSu']

        self._売り金額: int = dict_data['uriKin']
        self._売り単価: int = dict_data['uriTnk']
        self._輸出向先: str = self._calc_yusyutu_mukesaki()
        self._cans: int = self._calc_cans()
        self._出荷: str = self._get_factory_name() # 土気出荷、本社出荷
        self._hinban: str = self._calc_hinban()
        self._weight: Decimal = self._calc_weight()
        self._sumWeight:Decimal = Decimal('0')
        self._出荷予定倉庫 = self._add_to_yoteiSouko()


    def _get_factory_name(self)-> str:
        if self._factory == '@0001':
            return '本社出荷'
        return '土気出荷'

    def _calc_cans(self)-> int:
        if self._受注単位 != 'CN':
            return self._振替元数量
        return self._受注数量

    def _calc_hinban(self)-> str:
        if self._受注単位 != 'CN':
            return self._振替元品番
        if self._振替元品番 is not None: # Noneではなく、２文字以上の文字があったら
            if len(self._振替元品番) > 2:
                return self._振替元品番
        return self._売り品番

    def _calc_weight(self)-> Decimal:
        weight: Decimal = Decimal('0')
        can_name = self._productCan_dic.get(self._hinban, '')
        can_weight = self._tnju_dic.get(can_name, Decimal('0')) 
        net = self._tnju_dic.get(self._hinban, Decimal('0'))

        if can_weight == Decimal('0'):
            txt = f'{self._売り品番} の容器の重量が求められません'
            self._recorder.out_log(txt)
            self._recorder.out_file(txt)
        if net == Decimal('0'):
            txt = f'{self._売り品番} の重量が求められません'
            self._recorder.out_log(txt)
            self._recorder.out_file(txt)

        weight = (can_weight + net) / 1000

        return weight

    def _calc_yusyutu_mukesaki(self)-> str:
        yusyutu_mukesaki = ''
        nonyu_code = self._納入先コード
        # effitからfetchした納入先コードが' 'の場合は''にする
        # unsoutaiouデータは''なので。def create_yusyutuDictで''にしてある。
        if nonyu_code ==  ' ':
            nonyu_code = ''
        tmpTuple = (self._得意先コード, nonyu_code)
        yusyutu_mukesaki = self._yusyutu_dict[tmpTuple]

        return yusyutu_mukesaki


    def create_setPacking(self, setPacking: Set[Tuple]) -> None:
        tmpTuple: Tuple = ()
        if self._輸出向先 == 'y':
            tmpTuple = (self._得意先コード, self._納入先コード, 
                        self._得意先注文ＮＯ)
            setPacking.add(tmpTuple)
            return
        tmpTuple = (self._得意先コード, self._納入先コード)
        setPacking.add(tmpTuple)


    def add_packingDict_myself(self, packing: Tuple[str,...], 
                packingDict:Dict[Tuple[str,...], List[UriageForPacking]])-> None:
        '''
        packing -> ('T1210', 'IDK05', 'IDC4446') や、 ('T3820', ' ')など...
        '''

        if len(packing) == 3:
            if (packing[0] == self._得意先コード 
                and packing[1] == self._納入先コード 
                and packing[2] == self._得意先注文ＮＯ):
                if packing not in packingDict:
                    packingDict[packing] = [self]
                else:
                    packingDict[packing].append(self)


        if len(packing) == 2:
            if (packing[0] == self._得意先コード 
                and packing[1] == self._納入先コード):
                if packing not in packingDict:
                    packingDict[packing] = [self]
                else:
                    packingDict[packing].append(self)


    def _add_to_yoteiSouko(self)-> List[str]:
        '''
        addToYoteiSoukos['coa'] = addForCoa
        addToYoteiSoukos['siteiDenpyo'] = addForSiteiDenpyo
        addToYoteiSoukos['eigyosyo'] = addForEigyosyo
        addToYoteiSoukos['dohai'] = addForDohai
        addToYoteiSoukos['weekdayDiff'] = addForWeekdayDiff
        '''
        yoteiSoukos: List[str] = []

        self._addToYoteiSoukos['weekdayDiff'].add_to_yoteiSouko(
                            yoteiSoukos, self._出荷日, self._納期,
                            self._得意先コード, self._納入先コード,
                            self._leadTime_dict)
        self._addToYoteiSoukos['dohai'].add_to_yoteiSouko(
                            yoteiSoukos, self._納期)
        self._addToYoteiSoukos['eigyosyo'].add_to_yoteiSouko(
                            yoteiSoukos, self._備考)
        self._addToYoteiSoukos['siteiDenpyo'].add_to_yoteiSouko(
                            yoteiSoukos, self._得意先コード, self._納入先コード)
        self._addToYoteiSoukos['coa'].add_to_yoteiSouko(
                            yoteiSoukos, self._得意先コード, self._納入先コード,
                            self._hinban)

        return yoteiSoukos


    def add_packing_myself(self, dic_list: List[Dict[str, Any]])->None:
        tmp_dict = {
                '依頼先':         self._依頼先,
                'cans':           self._cans,
                '総重量':         self._sumWeight,
                '得意先コード':   self._得意先コード,
                '納入先コード':   self._納入先コード,
                '納入先名称１':   self._納入先名称１,
                '品名':           self._品名,
                '得意先注文ＮＯ': self._得意先注文ＮＯ,
                '備考':           self._備考,
                '納期':           self._納期,
                '出荷':           self._出荷,
                '出荷予定倉庫':   self._出荷予定倉庫, 
                'add':            self._add
                }
        dic_list.append(tmp_dict)


    def plus_myWeight(self, sumWeight) -> Decimal:
        sumWeight += self._weight * self._cans
        return sumWeight

    def set_sumWeight(self, sumWeight) -> None:
        self._sumWeight = sumWeight



