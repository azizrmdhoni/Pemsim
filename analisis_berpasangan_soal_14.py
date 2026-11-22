"""
Karena semua alokasi memakai seed yang sama (400..409), selisih produksi antar alokasi
dapat dihitung PER SEED lalu dirata-ratakan (uji berpasangan). Selisih ini punya variasi
jauh lebih kecil daripada membandingkan dua rata-rata terpisah.
Juga menguji beberapa alokasi tetangga di luar rancangan 3 ukuran.
Hasil: hasil_soal_14_berpasangan.json dan hasil_soal_14_alokasi_tambahan.json.
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from model_lini_4_press import simulate

combos = [(1, 5, 9), (1, 7, 7), (3, 3, 9), (3, 5, 7), (3, 7, 5), (5, 3, 7), (5, 5, 5)]

# produksi per jam tiap alokasi untuk 10 seed yang sama (1.000 jam per run)
tp = {c: [simulate(caps=c, T=60000, seed=400 + i)['tput'] for i in range(10)] for c in combos}

# selisih terhadap alokasi terbaik (1,5,9): rata-rata dan setengah lebar CI 95%
base = np.array(tp[(1, 5, 9)])
pd = {}
for c in combos:
    d = np.array(tp[c]) - base
    pd[str(c)] = (float(d.mean()),
                  float(1.96 * d.std(ddof=1) / np.sqrt(10)) if c != (1, 5, 9) else 0.0)
    print(c, round(d.mean(), 2), round(pd[str(c)][1], 2))
json.dump(pd, open('hasil_soal_14_berpasangan.json', 'w'))

# uji tambahan: alokasi di sekitar yang terbaik namun di luar rancangan 3 ukuran
extra = {}
for c in [(0, 6, 9), (1, 6, 8), (2, 5, 8), (1, 4, 10), (1, 3, 11)]:
    t = [simulate(caps=c, T=60000, seed=400 + i)['tput'] for i in range(10)]
    extra[str(c)] = float(np.mean(t))
    print('tambahan', c, round(np.mean(t), 2))
json.dump(extra, open('hasil_soal_14_alokasi_tambahan.json', 'w'))
