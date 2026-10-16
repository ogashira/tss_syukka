from typing import List, Any, Tuple
import platform
import csv
from get_idx import GetIdx

class ToyoUntin:
    def __init__(self) -> None:
        path: str= ''
        seikyusaki_path = '' 
        tyuukeiari_path  = ''
        tyuukeinasi_path = ''
        self._tyuukeiari: List[List[Any]] = []
        self._tyuukeinasi: List[List[Any]] = []
        self._seikyusaki_col: List[str] = []
        self._seikyusaki_data: List[List[Any]] = []

        if platform.system() == 'Windows':
            path = r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\ﾏｽﾀ\運賃計算関係\toyo_untin'
            seikyusaki_path = path + r'\seikyusaki.csv'
            tyuukeiari_path = path + r'\toyo_untin_tyuukei_ari.csv'
            tyuukeinasi_path = path + r'\toyo_untin_tyuukei_nasi.csv'
        if platform.system() == 'Linux':
            path = r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/運賃計算関係/toyo_untin'
            seikyusaki_path = path + r'/seikyusaki.csv'
            tyuukeiari_path = path + r'/toyo_untin_tyuukei_ari.csv'
            tyuukeinasi_path = path + r'/toyo_untin_tyuukei_nasi.csv'

    
    # ファイルを開く
        try:
            with open(tyuukeiari_path, 'r', encoding='cp932', newline='') as f:
                # 2次元リストとして取得
                self._tyuukeiari = list(csv.reader(f))

            with open(tyuukeinasi_path, 'r', encoding='cp932', newline='') as f:
                # 2次元リストとして取得
                self._tyuukeinasi = list(csv.reader(f))

            with open(seikyusaki_path, 'r', encoding='cp932', newline='') as f:
                # 2次元リストとして取得
                self._seikyusaki_col = next(csv.reader(f))
                # [相手先コード１, 相手先コード２, 相手先名称１, 住所１, 距離(Km), 中継回数]
                self._seikyusaki_data = list(csv.reader(f))
        except FileNotFoundError as e:
            raise FileNotFoundError(f'toyo_untinのファイルが見つかりません。{e}') from e


    def _search_distance_and_tyuukei_count(
                                    self, tokuiCD: str, nonyuCD: str) -> Tuple:
        '''
        nonyuCDは、' ' -> ''に変換されている必要がある。
        '''
        distance: int = 0
        count: int = 0
        tokuiCD_idx: int = GetIdx.get_idx(self._seikyusaki_col, '相手先コード１')
        nonyuCD_idx: int = GetIdx.get_idx(self._seikyusaki_col, '相手先コード２')
        distance_idx: int = GetIdx.get_idx(self._seikyusaki_col, '距離(Km)')
        relay_idx: int = GetIdx.get_idx(self._seikyusaki_col, '中継回数')


        for row in self._seikyusaki_data:
            if row[tokuiCD_idx] == tokuiCD and row[nonyuCD_idx] == nonyuCD:
                distance_str = row[distance_idx]
                count_str = row[relay_idx]

                if count_str != '' and count_str != ' ':
                    count = int(count_str)

                if distance_str != '' and distance_str != ' ':
                    distance = int(distance_str)
                break

        return distance, count


    def get_basic_fee(self, tokuiCD: str, nonyuCD: str, cans: int) -> int:
        fee: int = 0
        distance, relay_count = self._search_distance_and_tyuukei_count(
                                                    tokuiCD, nonyuCD)
        '''
        distanceが0の場合は、請求先リストに載っていないため、運賃計算は行わない
        '''
        if distance == 0:
            return fee

        untin_mtx: List[List[Any]] = self._tyuukeinasi
        if relay_count > 0:
            untin_mtx = self._tyuukeiari

        # 距離のインデックス求める
        idx_dist: int = 0
        # 最後から１まで
        for i in range(len(untin_mtx[0])-1, 0, -1):
            if int(untin_mtx[0][i]) >= distance:
                idx_dist = i
                break

        # 缶数のインデックス求める
        idx_cans: int = 0
        # 最後から１まで
        for i in range(len(untin_mtx)-1, 0, -1):
            if int(untin_mtx[i][0])>= cans:
                idx_cans = i
                break

        fee:int = int(untin_mtx[idx_cans][idx_dist])

        return fee
