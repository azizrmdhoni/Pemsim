"""
Pertanyaan 10(b): setelah repair, berapa lama antrian kembali normal?

Metode: satu run panjang (4.000.000 menit, kasus C, seed 21). Ambil kerusakan yang
"terisolasi" (tidak ada kerusakan lain 1.500 menit sebelum dan 900 menit sesudahnya),
lalu rata-ratakan profil panjang antrian pada 0..800 menit setelah repair selesai.
Antrian dianggap "normal" bila kembali ke Lq M/M/1 = 2,25 (+/- 0,5).
Keluaran: gambar_05_pemulihan_antrian.png dan hasil_pemulihan_antrian.json.
"""
import os
import sys
import json
import bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model_satu_mesin import simulate, case_kwargs

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 12.5,
                     'axes.titleweight': 'bold', 'axes.labelsize': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': 0.25, 'axes.axisbelow': True,
                     'legend.frameon': False})
BLUE, RED, GREEN, GREY = '#1F4E79', '#C00000', '#70AD47', '#7F7F7F'

T = 4000000
rl = simulate(**case_kwargs('C', 1000, 50), T=T, seed=21, record=True)
qs = rl['q_series']
ts = np.array([a for a, b in qs])
qv = np.array([b for a, b in qs])
dn = rl['down_intervals']

def q_at(t):
    # Panjang antrian pada waktu t (nilai terakhir sebelum atau tepat pada t).
    j = bisect.bisect_right(ts, t) - 1
    return qv[max(j, 0)]

taus = np.arange(0, 801, 10)          # menit sejak repair selesai
profs, durs = [], []
for i in range(1, len(dn) - 1):
    a, b = dn[i]                       # kerusakan ke-i: mulai a, selesai diperbaiki b
    # syarat "terisolasi": tidak ada kerusakan lain yang mengganggu profil pemulihan
    if a - dn[i - 1][1] > 1500 and dn[i + 1][0] - b > 900 and b + 800 < T:
        profs.append([q_at(b + x) for x in taus])
        durs.append(b - a)
profs = np.array(profs)
durs = np.array(durs)
prof = profs.mean(0)                   # profil rata-rata semua kerusakan terisolasi
long_ = durs >= 50                     # kerusakan panjang (>= 50 menit)
prof_long = profs[long_].mean(0)
n = len(profs)

pre = np.mean([q_at(dn[i][0] - 1) for i in range(1, len(dn) - 1)
               if dn[i][0] - dn[i - 1][1] > 1500])          # antrian sesaat sebelum rusak
thr = 2.25 + 0.5                                              # batas "kembali normal"
rec_all = [x for x, p in zip(taus, prof) if p <= thr]
rec_long = [x for x, p in zip(taus, prof_long) if p <= thr]
print('kerusakan terisolasi:', n, ' rata-rata lama rusak:', round(durs.mean(), 1))
print('antrian sesaat sebelum rusak:', round(pre, 2), ' antrian saat repair selesai:', round(prof[0], 2))
print('waktu pemulihan (semua):', rec_all[0] if rec_all else 'belum pulih dalam 800 menit')
print('waktu pemulihan (kerusakan panjang):', rec_long[0] if rec_long else 'belum pulih dalam 800 menit')
json.dump(dict(n=n, q0=float(prof[0]), rec=int(rec_all[0]) if rec_all else None,
               recl=int(rec_long[0]) if rec_long else None, pre=float(pre),
               qlong0=float(prof_long[0]), nlong=int(long_.sum())), open('hasil_pemulihan_antrian.json', 'w'))

# gambar
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.axhspan(2.25 - 0.5, 2.25 + 0.5, color=GREEN, alpha=0.25, lw=0,
           label='Kisaran normal (Lq ≈ 2,25 ± 0,5)')
ax.plot(taus, prof_long, color=RED, lw=2, ls='--', label='Kerusakan panjang (≥ 50 menit)')
ax.plot(taus, prof, color=BLUE, lw=2.6, label='Rata-rata semua kerusakan')
ax.axvline(600, color=GREY, ls=':', lw=1.5)
ax.text(612, 6.3, '± 500–700 menit:\nantrian kembali\nke kisaran normal', fontsize=10, va='top')
ax.set_xlabel('Waktu sejak repair selesai (menit)')
ax.set_ylabel('Rata-rata part di antrian')
ax.set_xlim(0, 800)
ax.set_ylim(0, 12.5)
ax.set_title(f'Pemulihan antrian setelah repair ({n} kerusakan terisolasi)', loc='left')
ax.legend(loc='upper right')
fig.savefig('gambar_05_pemulihan_antrian.png', dpi=220, bbox_inches='tight',
            pad_inches=0.15, facecolor='white')
plt.close(fig)
