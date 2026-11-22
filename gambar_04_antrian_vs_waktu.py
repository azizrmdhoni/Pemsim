"""
Satu replikasi kasus C (semua acak, kerusakan jarang), 100.000 menit, seed 7.
  Panel (a): seluruh run, area merah = mesin sedang rusak/diperbaiki.
  Panel (b): pembesaran di sekitar antrian terpanjang.
Pertanyaan 10(b): apakah terlihat kapan kerusakan terjadi? Antrian naik tajam di area merah.

menghasilkan gambar_04_antrian_waktu.png
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from model_satu_mesin import simulate, case_kwargs

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 12.5,
                     'axes.titleweight': 'bold', 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.grid': True, 'grid.alpha': 0.25,
                     'axes.axisbelow': True, 'legend.frameon': False})
BLUE, RED = '#1F4E79', '#C00000'

# record=True -> simulate() ikut mengembalikan deret waktu antrian dan interval rusak
r = simulate(**case_kwargs('C', 1000, 50), T=100000, seed=7, record=True)
ts = np.array([a for a, b in r['q_series']])      # waktu perubahan antrian
qv = np.array([b for a, b in r['q_series']])      # panjang antrian setelah perubahan
dn = r['down_intervals']                           # [(awal rusak, akhir repair), ...]
print('jumlah kerusakan dalam 100.000 menit:', len(dn))
print('antrian maksimum:', qv.max(), 'pada menit', round(ts[np.argmax(qv)]))

fig, ax = plt.subplots(2, 1, figsize=(8.4, 6.4), gridspec_kw=dict(hspace=0.55))

# panel (a): seluruh run
ax[0].step(ts, qv, where='post', lw=0.8, color=BLUE)
for a, b in dn:
    ax[0].axvspan(a, b, color=RED, alpha=0.55, lw=0)
ax[0].set_xlim(0, 100000)
ax[0].set_ylim(0, qv.max() * 1.25)
ax[0].set_xlabel('Waktu simulasi (menit)')
ax[0].set_ylabel('Part di antrian')
ax[0].set_title('(a) Seluruh run 100.000 menit', loc='left')
# legenda diletakkan DI LUAR area plot (sebaris dengan judul) agar tidak menimpa garis merah
ax[0].legend(handles=[Patch(color=BLUE, label='Jumlah part di antrian'),
                      Patch(color=RED, alpha=0.55, label='Mesin rusak / diperbaiki')],
             loc='lower right', bbox_to_anchor=(1.0, 1.13), ncol=2, fontsize=9.5)

# panel (b): pembesaran di sekitar antrian terpanjang
tp = ts[np.argmax(qv)]
w0, w1 = tp - 2300, tp + 1700
ax[1].step(ts, qv, where='post', lw=1.4, color=BLUE)
for a, b in dn:
    ax[1].axvspan(a, b, color=RED, alpha=0.55, lw=0)
ax[1].set_xlim(w0, w1)
ax[1].set_ylim(0, qv.max() * 1.15)
ax[1].set_xlabel('Waktu simulasi (menit)')
ax[1].set_ylabel('Part di antrian')
ax[1].set_title('(b) Pembesaran di sekitar antrian terpanjang', loc='left')
# keterangan di area kosong (tanpa panah agar tidak memotong pita merah dan kurva)
ax[1].text(39320, qv.max() * 1.08, 'pita merah =\nmesin rusak;\nantrian naik',
           fontsize=9, va='top', ha='left',
           bbox=dict(boxstyle='square,pad=0.2', fc='white', ec='none', alpha=0.9))

fig.savefig('gambar_04_antrian_waktu.png', dpi=220, bbox_inches='tight',
            pad_inches=0.15, facecolor='white')
plt.close(fig)
