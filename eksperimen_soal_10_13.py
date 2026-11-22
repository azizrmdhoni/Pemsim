"""
Menjalankan enam kasus (A-F) untuk:
    - tiga kebijakan kerusakan : resume (Soal 10, 11), restart (Soal 12), scrap (Soal 13)
    - dua frekuensi kerusakan  : rendah  (TTF 1000, TTR 50 menit)
                                 tinggi  (TTF 2,    TTR 0,1 menit)
Hasil disimpan ke hasil_soal_10_13.json dan dipakai oleh skrip gambar.
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from model_satu_mesin import simulate, case_kwargs

# (rata-rata TTF, rata-rata TTR) untuk kedua frekuensi kerusakan
FREQ = {'low': (1000, 50), 'high': (2, 0.1)}
res = {}


def agg(c, freq, mode, T=100000, reps=5, seed0=100):
    # Jalankan `reps` replikasi untuk kasus c. Kasus E (semua deterministik) cukup 1
    # replikasi karena hasilnya selalu sama. Seed replikasi ke-i = seed0 + i."""
    tm, rm = FREQ[freq]
    n = 1 if c == 'E' else reps
    return [simulate(**case_kwargs(c, tm, rm), mode=mode, T=T, seed=seed0 + i)
            for i in range(n)]


# 1) Tabel utama: 3 kebijakan x 2 frekuensi x 6 kasus, 5 replikasi x 100.000 menit
for mode in ['resume', 'restart', 'scrap']:
    res[mode] = {}
    for freq in ['low', 'high']:
        res[mode][freq] = {}
        for c in 'ABCDEF':
            rs = agg(c, freq, mode)
            # rata-rata tiap ukuran kinerja antar replikasi
            d = {k: float(np.nanmean([r[k] for r in rs]))
                 for k in rs[0] if k not in ('q_series', 'down_intervals')}
            d['Lq_reps'] = [r['Lq'] for r in rs]           # nilai tiap replikasi
            d['Lq_min'] = min(d['Lq_reps'])
            d['Lq_max'] = max(d['Lq_reps'])
            res[mode][freq][c] = d


# 2) 30 replikasi (resume) untuk selang kepercayaan 95% pada Lq
def robust(ttf_mean, ttr_mean, seed0):
    # Mengembalikan {kasus: (rata-rata Lq, setengah lebar CI 95%)} dari 30 replikasi."""
    out = {}
    for c in 'ABCDEF':
        n = 1 if c == 'E' else 30
        v = [simulate(**case_kwargs(c, ttf_mean, ttr_mean), mode='resume',
                      T=100000, seed=seed0 + i)['Lq'] for i in range(n)]
        out[c] = (float(np.mean(v)),
                  float(1.96 * np.std(v, ddof=1) / np.sqrt(len(v))) if n > 1 else 0.0)
    return out


res['robust30_low'] = robust(1000, 50, 1000)     # frekuensi rendah
res['robust30_high'] = robust(2, 0.1, 2000)      # frekuensi tinggi

# 3) Verifikasi persen waktu down vs panjang run (Soal 11)
# Kedatangan dibuat sangat jarang (1e12) supaya hanya proses kerusakan yang diamati.
# Setiap panjang run diulang 10 kali; dicatat rata-rata, minimum, maksimum.
pd = {}
for freq in ['low', 'high']:
    pd[freq] = {}
    for T in [10000, 100000, 1000000]:
        v = [simulate(arr=('exp', 1e12), svc=('exp', 7.5),
                      ttf=('exp', FREQ[freq][0]), ttr=('exp', FREQ[freq][1]),
                      T=T, seed=3000 + i)['pct_down'] for i in range(10)]
        pd[freq][T] = (float(np.mean(v)), float(np.min(v)), float(np.max(v)))
res['pctdown'] = pd

def tanpa_nan(x):
    # Ganti NaN (ukuran yang tidak terdefinisi, mis. rata-rata dari nol part) dengan None
    # agar file JSON valid; NaN bukan JSON baku.
    if isinstance(x, dict):
        return {k: tanpa_nan(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [tanpa_nan(v) for v in x]
    if isinstance(x, float) and x != x:
        return None
    return x


json.dump(tanpa_nan(res), open('hasil_soal_10_13.json', 'w'), indent=1)

# ringkasan ke layar
for mode in ('resume', 'restart', 'scrap'):
    for freq in res[mode]:
        print(mode, freq, {c: round(res[mode][freq][c]['Lq'], 2) for c in 'ABCDEF'})
print('persen down vs panjang run:', res['pctdown'])
print('30 replikasi, frekuensi rendah :', res['robust30_low'])
print('30 replikasi, frekuensi tinggi :', res['robust30_high'])
