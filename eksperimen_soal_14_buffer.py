"""
(a) Buffer tak terbatas, 480 jam, 10 replikasi -> di mana terjadi penumpukan?
(b) Buffer terbatas, total 15 lembar, 1.000 jam, 10 replikasi tiap alokasi
    -> pembagian buffer mana yang memaksimalkan produksi?
Hasil disimpan ke hasil_soal_14.json.
"""
import os
import sys
import json
import itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from model_lini_4_press import simulate

R = {}

# (a) buffer tak terbatas
reps = [simulate(T=480 * 60, seed=300 + i) for i in range(10)]
R['a'] = dict(
    tput=float(np.mean([r['tput'] for r in reps])),                    # produksi rata-rata/jam
    tput_sd=float(np.std([r['tput'] for r in reps], ddof=1)),
    bavg=[float(np.mean([r['bavg'][k] for r in reps])) for k in range(3)],   # isi rata-rata buffer
    bmax=[float(np.mean([r['bmax'][k] for r in reps])) for k in range(3)],   # isi maksimum buffer
    util=[[float(np.mean([r['util'][i][s] for r in reps])) for s in range(5)]
          for i in range(4)],                                          # utilisasi [mesin][keadaan]
    scrap=[float(np.mean([r['scrap'][i] for r in reps])) for i in range(4)],
    out=float(np.mean([r['out'] for r in reps])))

# Isi buffer pada beberapa panjang run: bila terus naik berarti hulu lebih cepat dari hilir,
# dan angka "isi rata-rata" bukan ukuran buffer yang layak (bahan analisis (a)).
for H in [60, 120, 240, 480]:
    rs = [simulate(T=H * 60, seed=300 + i) for i in range(5)]
    R[f'bavg_{H}'] = [float(np.mean([r['bavg'][k] for r in rs])) for k in range(3)]

# (b) buffer terbatas
# Tiap buffer diuji pada 3 ukuran di sekitar titik awal (3,5,7). Kombinasi penuh 3x3x3 = 27,
# tetapi total harus 15 lembar sehingga hanya 7 kombinasi yang memenuhi.
L1, L2, L3 = [1, 3, 5], [3, 5, 7], [5, 7, 9]
combos = [c for c in itertools.product(L1, L2, L3) if sum(c) == 15]
print('kombinasi:', combos, len(combos))

B = {}
for c in combos:
    # seed 400..409 sama untuk semua alokasi (common random numbers) agar
    # perbandingan antar alokasi lebih tajam (lihat analisis_berpasangan_soal_14.py untuk uji berpasangan)
    rs = [simulate(caps=c, T=1000 * 60, seed=400 + i) for i in range(10)]
    t = [r['tput'] for r in rs]
    B[str(c)] = dict(
        caps=c,
        tput=float(np.mean(t)),                                       # produksi/jam
        hw=float(1.96 * np.std(t, ddof=1) / np.sqrt(len(t))),         # setengah lebar CI 95%
        util=[[float(np.mean([r['util'][i][s] for r in rs])) for s in range(5)] for i in range(4)],
        bavg=[float(np.mean([r['bavg'][k] for r in rs])) for k in range(3)],
        scrap=[float(np.mean([r['scrap'][i] for r in rs])) for i in range(4)])
    print(c, round(B[str(c)]['tput'], 2), '+-', round(B[str(c)]['hw'], 2))
R['b'] = B

# Pembanding: produksi buffer tak terbatas pada panjang run yang sama (1.000 jam)
rs = [simulate(T=1000 * 60, seed=400 + i) for i in range(10)]
R['unl1000'] = float(np.mean([r['tput'] for r in rs]))

json.dump(R, open('hasil_soal_14.json', 'w'), indent=1)
print('hasil (a):', R['a'])
print('buffer tak terbatas, 1000 jam:', R['unl1000'])
