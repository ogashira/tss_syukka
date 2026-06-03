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
##### soukoidou
- `Winボタン+R -> tss_syukka入力 -> Enter`または`cmdにて、 pushd \\wsl$\Ubuntu\home\oga\projects\tss_syukka\`デイレクトリ内にて`python main.py`で実行
### 動作

### クラス図
```mermaid
---
title: tss_syukka
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
    + _setup_sql_path()None*
    + get_instance()instance*
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
class FetchUnsoutaiouToke{
    + fetch_data()pd.DataFrame
}
class IExcelOutput{
    <<interface>>
    create_excelOutput(str, str, str="")result*
}
class SyukkaJissekiSyoukai{
    - _uriages:List~UriageForSyukkaJisseki~
    - _createJson:CreateJson
    - _unsouSet_col:List~str~
    - _createDictFromList:CreateDictFromDict
    - _sumi_json_str:str
    - _unsouSet_json_str:str
    - _factoryName:str
    - _syukkaKoujou:str
    + create_excelOutput(str, str, str=""):result
    - _create_sumi_dict(List[Dict[str,Any]])
    - _create_sumi_json_str()str
    - _create_unsouSet(Set[Tuple]):None
    - _create_unsouSet_json_str()str
}
class AllPackings{
    - _uriages:List~UriageForPacking~
    - _createJson:CreateJson
    - _factoryName
    - _createDictFromList:CreateDictFromDict
    - _packingForDenpyos:List~PsckingForDenpyo~
    - _packing_json_str:str
    + create_excelOutput(str,str,str="")result
    - _create_packing_dict(List[Dict[str,Any]])None
    - _create_packing_json_str()str
}
class PackingForDenpyo{
    - _tokuiCD_tpl:Tuple[str,...]
    - _uriageForPackings:List~UriageForPacking~
    - _createJson:CreateJson
    + create_excelOutput(str,str,str="")
    - _create_packing_dict(List[Dict[str,Any]])None
}
class UriageForSyukkaJisseki{
    - _factory
    - _得意先コード etc...
    - _yusyutu_dict:Dict
    + add_sumiData_myself(List[Dict[str,Any]])None
    + add_unsouSet_myself(Set[Tuple])None
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
    - _calc_cans()int
    - _calc_yusyutu_mukesaki()str
}
Main --> flow
flow --> InstanceFactory: "生成を依頼"
flow --> IExcelOutput
flow --> TssBat

InstanceFactory --> IFetchDataForList : "戻り値の型"
InstanceFactory --> FetchUriageSumiForPacking
InstanceFactory --> FetchUriageSumi
InstanceFactory --> FetchUnsoutaiouToke
UriageForPacking <-- InstanceFactory
UriageForSyukkaJisseki <-- InstanceFactory

IExcelOutput <-- InstanceFactory : "戻り値の型"
TssBat o--> IExcelOutput
FetchUriageSumiForPacking ..|> IFetchDataForList
FetchUriageSumi ..|> IFetchDataForList
FetchUnsoutaiouToke ..|> IFetchDataForList
SyukkaJissekiSyoukai ..|> IExcelOutput
AllPackings ..|> IExcelOutput
HsCoa ..|> IExcelOutput
MhsCoa ..|> IExcelOutput
AllPackings o--> PackingForDenpyo
UriageForSyukkaJisseki --o SyukkaJissekiSyoukai
UriageForPacking --o AllPackings
UriageForPacking --o  PackingForDenpyo 
```
```mermaid
---
title: tss_syukka
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
    + _setup_sql_path()None*
    + get_instance()instance*
}
class TssBat{
    - excel_output: IExcelOutput
    + create_tssBat()result
}
class IExcelOutput{
    <<interface>>
    create_tssBat(str, str, str="")result*
}
class SyukkaJissekiSyoukai{
    - _uriages:List~UriageForSyukkaJisseki~
    - _createJson:CreateJson
    - _unsouSet_col:List~str~
    - _createDictFromList:CreateDictFromDict
    - _sumi_json_str:str
    - _unsouSet_json_str:str
    - _factoryName:str
    - _syukkaKoujou:str
    + create_tssBat(str, str, str=""):result
    - _create_sumi_dict(List[Dict[str,Any]])
    - _create_sumi_json_str()str
    - _create_unsouSet(Set[Tuple]):None
    - _create_unsouSet_json_str()str
}
class AllPackings{
    - _uriages:List~UriageForPacking~
    - _createJson:CreateJson
    - _factoryName
    - _createDictFromList:CreateDictFromDict
    - _packingForDenpyos:List~PsckingForDenpyo~
    - _packing_json_str:str
    + create_tssBat(str,str,str="")result
    - _create_packing_dict(List[Dict[str,Any]])None
    - _create_packing_json_str()str
}
class PackingForDenpyo{
    - _tokuiCD_tpl:Tuple[str,...]
    - _uriageForPackings:List~UriageForPacking~
    - _createJson:CreateJson
    + create_excelOutput(str,str,str="")
    - _create_packing_dict(List[Dict[str,Any]])None
}
class UriageForSyukkaJisseki{
    - _factory
    - _得意先コード etc...
    - _yusyutu_dict:Dict
    + add_sumiData_myself(List[Dict[str,Any]])None
    + add_unsouSet_myself(Set[Tuple])None
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
    - _calc_cans()int
    - _calc_yusyutu_mukesaki()str
}
Main --> flow
flow --> InstanceFactory: "生成を依頼"
flow --> TssBat
TssBat o--> IExcelOutput

InstanceFactory --> UriageForPacking
InstanceFactory --> UriageForSyukkaJisseki
InstanceFactory --> SyukkaJissekiSyoukai
InstanceFactory --> AllPackings
InstanceFactory --> IExcelOutput: "戻り値の型"


HsCoa ..|> IExcelOutput
MhsCoa ..|> IExcelOutput
SyukkaJissekiSyoukai ..|> IExcelOutput
AllPackings ..|> IExcelOutput
AllPackings o--> PackingForDenpyo
UriageForSyukkaJisseki --o SyukkaJissekiSyoukai
UriageForPacking --o AllPackings
UriageForPacking --o  PackingForDenpyo 
```
1. flowは、InstanceFactoryからIFetchDataForListクラスのインスタンスをもらって必要なデータを得る。
1. flowは、UriageForSyukkaJissekiのインスタンスを生成し、
