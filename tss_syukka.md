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
class SumiData{
    - _uriages: List~Uriage~
    + add_sumiData_myself(List~Dict[str,Any])
    + add_unsouSet_myself(Set~Tuple~)
}
class Uriage{
    - _yusyutu_dict: Dict[Tuple,str]
    - _factory:str
    - _得意先コード: str etc...
    - _calc_cans()int
    - _calc_yusyutu_mukesaki()str
    + add_sumiData_myself(List~Dict[str,Any])
    + add_unsouSet_myself(Set~Tuple~)
}
Main --> flow
flow --> InstanceFactory
InstanceFactory --> IFetchDataForList
IFetchDataForList <|.. FetchUriageSumiForPacking
IFetchDataForList <|.. FetchUriageSumi
IFetchDataForList <|.. FetchUnsoutaiouToke
flow --> SumiData
SumiData o-- Uriage
```
