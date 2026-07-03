from abc import ABC, abstractmethod
from typing import List, Dict, Any
import datetime


class IAddToYoteiSouko(ABC):
    @abstractmethod
    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        pass

  
class AddForCoa(IAddToYoteiSouko):
    '''
    必要があれば"成"をappendする
    '''
    def __init__(self, tenpCoa_dicts)-> None:
        self._tenpCoa_dicts = tenpCoa_dicts

    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        tokuiCD = args[0]
        nonyuCD = args[1]
        hinban = args[2]

        if nonyuCD == ' ':
            nonyuCD = ''

        for innerDic in self._tenpCoa_dicts:
            tenp_nonyuCD: str = innerDic['納入先ｺｰﾄﾞ']
            if tenp_nonyuCD is None: # 添付リスト.xlsdの空白はNoneになってる
                tenp_nonyuCD = ''
            if (innerDic['得意先ｺｰﾄﾞ'] == tokuiCD and
                tenp_nonyuCD == nonyuCD and
                innerDic['品番'] == hinban):
                yoteiSoukos.append('成')


class AddForSiteiDenpyo(IAddToYoteiSouko):
    '''
    必要があれば"指"をappendする
    '''
    def __init__(self, tenpSitei_dicts:List[Dict[str,Any]])-> None:
        self._tenpSitei_dicts = tenpSitei_dicts

    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        tokuiCD = args[0]
        nonyuCD = args[1]

        if nonyuCD == ' ':
            nonyuCD = ''

        for innerDic in self._tenpSitei_dicts:
            tenp_nonyuCD = innerDic['納入先ｺｰﾄﾞ']
            if (innerDic['得意先ｺｰﾄﾞ'] == tokuiCD and
                tenp_nonyuCD == nonyuCD):
                yoteiSoukos.append('指')


class AddForEigyosyo(IAddToYoteiSouko):
    '''
    必要があれば"営業所"をappendする
    '''
    def __init__(self)-> None:
        pass

    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        bikou = args[0]
        if bikou.find('支店止め') >= 0 or bikou.find('支店どめ') >= 0 or \
            bikou.find('営業所止め') >= 0 or bikou.find('営業所どめ') >= 0 :
            yoteiSoukos.append('営業所')


class AddForDohai(IAddToYoteiSouko):
    '''
    必要があれば"土配"をappendする
    '''
    def __init__(self)-> None:
        pass

    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        nouki = args[0]
        dt = datetime.date(int(nouki[:4]), int(nouki[4:6]), int(nouki[6:]))

        youbi: int  = dt.weekday() # 0:月～6:日　（土= 5)
        if youbi == 5:
            yoteiSoukos.append('土配')


class AddForWeekdayDiff(IAddToYoteiSouko):
    '''
    必要があれば"曜日違い"をappendする
    '''
    def __init__(self, list_YMD: List[str], 
                 dict_unso_holiday: Dict[str, str], 
                 dict_toyo_holiday: Dict[str, str])-> None:
        self._list_YMD = list_YMD
        self._dict_unso_holiday = dict_unso_holiday # 休日= "1"
        self._dict_toyo_holiday = dict_toyo_holiday

    def add_to_yoteiSouko(self, yoteiSoukos: List[str], *args) -> None:
        syukkabi = args[0]
        nouki = args[1]
        tokuiCD = args[2]
        nonyuCD = args[3]
        leadTime_dict = args[4]
        
        if nonyuCD == ' ':
            nonyuCD = ''
        leadTime: int = leadTime_dict[(tokuiCD, nonyuCD)]

        nouki_idx = self._list_YMD.index(nouki)

        while leadTime > 0:
            if self._dict_unso_holiday[self._list_YMD[nouki_idx -1]] == '1':
                nouki_idx -= 1
                continue 
            nouki_idx -= 1
            leadTime -= 1

        while (self._dict_unso_holiday[self._list_YMD[nouki_idx]] == '1' or
               self._dict_toyo_holiday[self._list_YMD[nouki_idx]] == '1'):
            nouki_idx -= 1

        if self._list_YMD[nouki_idx] != syukkabi:
            yoteiSoukos.append('曜日')


    def test_syukkabi(self, *args) -> str:
        '''
        テスト方法（code）
        python
        from flow_test import *
        add = start()
        出荷日を入力してください： 20270106
        add.test_syukkabi('20270106, 2) # 2 = leadTime
        '''
        nouki = args[0]
        leadTime: int = args[1]

        nouki_idx = self._list_YMD.index(nouki)

        while leadTime > 0:
            if self._dict_unso_holiday[self._list_YMD[nouki_idx -1]] == '1':
                nouki_idx -= 1
                continue 
            nouki_idx -= 1
            leadTime -= 1

        while (self._dict_unso_holiday[self._list_YMD[nouki_idx]] == '1' or
               self._dict_toyo_holiday[self._list_YMD[nouki_idx]] == '1'):
            nouki_idx -= 1

        return self._list_YMD[nouki_idx]
