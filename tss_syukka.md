# tss_syukkaについて
## システム概要
### 動作環境
- OS  
    - Windows11(main.py)
- インストール先
    - 尾頭PC WSL2(Ubuntu)で開発
### 構築システム
- メインシステム: Python3.10
- Windowsスクリプト(   )
### ソースコード
GitHub Publicリポジトリで公開</br>
[GitHub_ https://github.com/ogashira/tss_syukka](https://github.com/ogashira/tss_syukka)
### 起動方法
##### tss_syukka
- `Winボタン+R -> tss_syukka入力 -> Enter`または`cmdにて、 pushd \\wsl$\Ubuntu\home\oga\projects\tss_syukka\`デイレクトリ内にて`python main.py`で実行
### 動作

### クラス図
```mermaid
---
title: Interface:IFetchDataForList
---
classDiagram
direction LR 

class Main{
    + main()None
}
class flow{
    + start()
}
class InstanceFactory{
    - _sqlServerTss: Any
    - _sqlServerEffit: Any
    - _cnxn_tss
    - _cnxn_effit
    - _instances: Dict~str,Any
    + _setup_sql_path()None
    + get_sql_server_tss()None
    + etc.....
}
class IFetchDataForList{
    <<interface>>
    + fetch_data()Tuple[List, List~List~str~~]*
}
class FetchUriageSumiForPacking{
    - cnxn: object
    - syukka_date: str
    + fetch_data()pd.DataFrame
}
class FetchUriageSumi{
    - cnxn: object
    - syukka_date: str
    + fetch_data()pd.DataFrame
}
class FetchCalenderUnsouya{
    - cnxn:object
    - minYM
    - maxYM
    + fetch_data()pd.DataFrame
}
class FetchCalenderToyo{
    - cnxn:object
    - minYM
    - maxYM
    + fetch_data()pd.DataFrame
}
class FetchProductCan{
    - cnxn:object
    + fetch_data()pd.DataFrame
}
class FetchTnju{
    - cnxn:object
    + fetch_data()pd.DataFrame
}
class FetchUnsoutaiouHonsya{
    - cnxn:object
    + fetch_data()pd.DataFrame
}
class FetchUnsoutaiouToke{
    - cnxn:object
    + fetch_data()pd.DataFrame
}
class FetchSyukkaListCoa{
    + fetch_data()pd.DataFrame
}
class FetchSyukkaListSiteiDenpyo{
    + fetch_data()pd.DataFrame
}
Main --> flow
flow --> InstanceFactory: "生成を依頼"

InstanceFactory --> IFetchDataForList : "戻り値の型"
InstanceFactory --> FetchUriageSumiForPacking
InstanceFactory --> FetchUriageSumi
InstanceFactory --> FetchCalenderUnsouya
InstanceFactory --> FetchCalenderToyo
InstanceFactory --> FetchProductCan
InstanceFactory --> FetchTnju
InstanceFactory --> FetchUnsoutaiouHonsya
InstanceFactory --> FetchUnsoutaiouToke
InstanceFactory --> FetchSyukkaListCoa
InstanceFactory --> FetchSyukkaListSiteiDenpyo

FetchUriageSumiForPacking ..|> IFetchDataForList
FetchUriageSumi ..|> IFetchDataForList
FetchUnsoutaiouToke ..|> IFetchDataForList
```
```mermaid
---
title: Interface:IExcelOutput
---
classDiagram
direction TB 

class Main{
    + main()None
}
class flow{
    + start()
}
class InstanceFactory{
    - _sqlServerTss: Any
    - _sqlServerEffit: Any
    - _cnxn_tss
    - _cnxn_effit
    - _instances: Dict~str,Any
    + _setup_sql_path()None
    + get_sql_server_tss()None
    + etc.....
}
class CreateTssBat{
    _ excel_outputs: List[Dict[str,Any]] 
    "AnyにIExcelOutputを含む"
    - recorder: Recorder
    + create_tssBat():None
}
class IExcelOutput{
    <<interface>>
    + create_tssBat(str,str,str=""):None
}
class SyukkaJissekiSyoukai{
    - _uriages:List~UriageForSyukkaJisseki~
    - _createJson:CreateJson
    - _unsouSet_col:List~str~
    - _createDictFromList:CreateDictFromDict
    - _recorder:Recorder
    - _sumi_json_str:str
    - _unsouSet_json_str:str
    - _factoryName:str
    - _syukkaKoujou:str
    + create_tssBat(str, str, str=""):result
    + collect_uriage_for_coa(Dict[str,List['UriageForSyukkajisseki]]
    - _get_factoryName(str):str
    - _get_syukkaKoujou(str):str
    - _create_sumi_dict(List[Dict[str,Any]])
    - _create_sumi_json_str()str
    - _create_unsouSet(Set[Tuple]):None
    - _create_unsouSet_json_str()str
}
class AllPackings{
    - _uriages:List~UriageForPacking~
    - _packingForDenpyos:List~PackingForDenpyo~
    - _createJson:CreateJson
    - _factoryName
    - _createDictFromList:CreateDictFromDict
    - _recorder: Recorder
    - _packing_json_str:str
    + create_tssBat(str,str,str="")result
    - _get_factoryName(str)str
    - _create_packing_dict(List[Dict[str,Any]])None
    - _create_packing_json_str()str
}
class PackingForDenpyo{
    - _tokuiCD_tpl:Tuple[str,...]
    - _uriageForPackings:List~UriageForPacking~
    - _createJson:CreateJson
    - _create_packing_dict(List[Dict[str,Any]])None
    - _calc_sumWeight()Decimal
    - _set_sumWeight_to_uriageForPacking()None
}
class HsCoa{
    - _uriage:UriageForSyukkajisseki
    - _checkHatumono:CheckHatumono
    + create_tssBat(str, str, str=""):result
}
class MhsCoa{
    - _uriage:UriageForSyukkaJisseki
    - _checkHatumono:CheckHatumono
    + create_tssBat(str, str, str=""):result
}
class KoitoCoa{
    - _uriage:UriageForSyukkaJisseki
    - _checkHatumono:CheckHatumono
    + create_tssBat(str, str, str=""):result
}
class UriageForSyukkaJisseki{
    - _factory
    - _得意先コード etc...
    - _yusyutu_dict:Dict
    + add_sumiData_myself(List[Dict[str,Any]])None
    + add_unsouSet_myself(Set[Tuple])None
    + add_myself_for_coa(Dict[str[List[UriageForSyukkaJisseki]]None
    + create_hsCoa(str,str,ChechHatumono)None
    + create_mhsCoa(str,str,ChechHatumono)None
    + create_koitoCoa(str,ChechHatumono)None
    - _get_honban_for_coa()str
    - _get_mksk()str
    - _calc_cans()int
    - _calc_yusyutu_mukesaki()str
}
class UriageForPacking{
    - _factory:str
    - _依頼先:str
    - _得意先コード etc...
    - _yusyutu_dict: Dict
    + create_setPacking(set[Tuple])None
    + add_packingDict_myself(Tuple[str,...], Dict[Tuple[str,...], List[UriageForPacking]])
    + add_packing_myself(List[Dict[str,Any]])None
    + plus_myWeight(Decimal)Decimal
    + set_sumWeight(Decimal)None #setter
    - _get_factory_name()str
    - _calc_cans()int
    - _calc_hinban()str
    - _calc_weight()Decimal
    - _calc_yusyutu_mukesaki()str
    - _add_to_yoteiSouko
}
class IAddToYoteiSouko{
    <<interface>>
    + add_to_yoteiSouko(List[str], *args):None*
}
class AddForCoa{
    - _tenpCoa_dicts:List[Dict[str,Any]]
    + add_to_yoteiSouko(List[str], *args):None*
}
class AddForSiteiDenpyo{
    - _tenpSitei_dicts:List[Dict[str,Any]]
    + add_to_yoteiSouko(List[str], *args):None
}
class AddForEigyosyo{
    + add_to_yoteiSouko(List[str], *args):None
}
class AddForDohai{
    + add_to_yoteiSouko(List[str], *args):None
}
class AddForWeekdayDiff{
    - _list_YMD:List[str]
    - _dict_unso_holiday:Dict[str,str]
    - _dict_toyo_holiday:Dict[str,str]
    + add_to_yoteiSouko(List[str], *args):None
}

Main --> flow
flow --> InstanceFactory: "生成を依頼"

%%InstanceFactory --> UriageForPacking
%%InstanceFactory --> UriageForSyukkaJisseki
%%InstanceFactory --> SyukkaJissekiSyoukai
%%InstanceFactory --> AllPackings
%%InstanceFactory --> IExcelOutput: "戻り値の型"
InstanceFactory --> CreateTssBat
%%InstanceFactory --> HsCoa
%%InstanceFactory --> MhsCoa

CreateTssBat o-- IExcelOutput
IExcelOutput <|.. HsCoa
IExcelOutput <|.. MhsCoa
IExcelOutput <|.. KoitoCoa
IExcelOutput <|.. SyukkaJissekiSyoukai
IExcelOutput <|.. AllPackings
AllPackings "1" o--> ">1" PackingForDenpyo
SyukkaJissekiSyoukai "1" o-- ">1" UriageForSyukkaJisseki
HsCoa ">0" o-- "1" UriageForSyukkaJisseki
MhsCoa ">0" o-- "1" UriageForSyukkaJisseki
KoitoCoa ">0" o-- "1" UriageForSyukkaJisseki
AllPackings "1"  o-- ">1" UriageForPacking
PackingForDenpyo "1" o-- ">1" UriageForPacking
```
1. flowは、InstanceFactoryからIFetchDataForListクラスのインスタンスをもらって必要なデータを得る。
1. flowは、SyukkaJissekiSyoukai_toke, SyukkaJissekiSyoukai_honsyaのインスタンスを得る。これらインスタンスはUriageForSyukkajissekiのインスタンスのリスト(toke, honsya)を持っている。
1. flowは、AllPackings_honsya,AllPackings_tokeのインスタンスを得る。AllPackingsはUriageForPackingのインスタンスのリストを持っている。
1. AllPackingsは必要なUriageForPackingのインスタンスを渡して、PackingForDenpyoのインスタンスのリストを作って保持する。
1. PackingForDenpyoインスタンスは国内は「得意先コード、納入先コード」毎に、輸出は「得意先コード、納入先コード、注番」毎に存在する。
1. flowはHsCoa,MhsCoaクラスのインスタンスを得る。これらインスタンスはUriageForSyukkaJissekiのインスタンスのリストを持つ。
1. SyukkaJissekiSyoukai_toke, SyukkaJissekiSyoukai_honsya,AllPackings_toke, AllPackings_toke,HsCoa,MhsCoaはIExcelOutputインターフェースの実装であり、CreateTssBatクラスが保持している。
1. flowはCreateTssBatのインスタンスを生成し、create_tssBatメソッドを呼び出して、「出荷実績照会」、「業務_packing」、「検査成績書」を作成する。

