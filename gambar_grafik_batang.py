"""
Membaca hasil simulasi dari hasil_soal_10_13.json dan hasil_soal_14.json (dibuat eksperimen_soal_10_13.py dan eksperimen_soal_14_buffer.py),
sehingga angka pada grafik selalu sama dengan angka pada tabel laporan.
(Gambar 4 dan 5 dibuat oleh gambar_04_antrian_vs_waktu.py dan gambar_05_pemulihan_antrian.py; flowchart oleh gambar_diagram_alur.py.)
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Liberation Serif'      # huruf serif, seperti dokumen Word
plt.rcParams['font.size'] = 10
BLUE, ORANGE = '#2E75B6', '#ED7D31'

res = json.load(open('hasil_soal_10_13.json'))
r14 = json.load(open('hasil_soal_14.json'))

# Lq pada Tabel 1 buku Banks (rata-rata 5 replikasi), sebagai pembanding
BOOK = {'A': 2.31, 'B': 3.26, 'C': 4.11, 'D': 3.24, 'E': 0.52, 'F': 1.13}
CASES = list('ABCDEF')

def koma(v, d=2):
    # Format angka dengan koma desimal.
    return f'{v:.{d}f}'.replace('.', ',')

def rapikan(ax):
    # Hilangkan garis atas dan kanan agar grafik bersih.
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)

def batang_berpasangan(fn, a, b, label_a, label_b):
    # Grafik batang berpasangan untuk enam kasus A-F.
    # Label angka berada di atas batang dengan ukuran kecil supaya tidak saling menimpa;
    # legenda diletakkan di atas plot, di luar area batang.
    fig, ax = plt.subplots(figsize=(6.6, 3.5), dpi=200)
    w = 0.34
    for i in range(6):
        ax.bar(i - w / 2 - 0.01, a[i], w, color=BLUE)
        ax.bar(i + w / 2 + 0.01, b[i], w, color=ORANGE)
        ax.text(i - w / 2 - 0.01, a[i] + 0.06, koma(a[i]), ha='center', va='bottom', fontsize=7.5)
        ax.text(i + w / 2 + 0.01, b[i] + 0.06, koma(b[i]), ha='center', va='bottom', fontsize=7.5)
    ax.set_xticks(range(6))
    ax.set_xticklabels(CASES)
    ax.set_ylabel('Rata-rata jumlah part di antrian (Lq)')
    ax.set_ylim(0, 4.6)
    ax.set_xlim(-0.6, 5.6)
    ax.yaxis.grid(True, color='#dddddd', lw=0.6)
    ax.set_axisbelow(True)
    rapikan(ax)
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    fig.legend(handles, [label_a, label_b], loc='upper center', ncol=2, frameon=False,
               bbox_to_anchor=(0.55, 1.0))
    fig.subplots_adjust(top=0.88, bottom=0.12, left=0.11, right=0.98)
    fig.savefig(fn)
    plt.close(fig)

# Gambar 3 (Soal 10)
# Simulasi 30 replikasi (kerusakan jarang) vs angka di buku.
low30 = [res['robust30_low'][c][0] for c in CASES]
batang_berpasangan('gambar_03_lq_vs_buku.png', low30, [BOOK[c] for c in CASES],
                   'Simulasi (30 replikasi)', 'Buku (Tabel 1)')

# Gambar 6 (Soal 11)
# Kerusakan jarang vs sering, 30 replikasi masing-masing.
high30 = [res['robust30_high'][c][0] for c in CASES]
batang_berpasangan('gambar_06_lq_rendah_vs_tinggi.png', low30, high30,
                   'Frekuensi rendah', 'Frekuensi tinggi')

# Gambar 9 (Soal 13)
# Yield bila part dibuang saat mesin rusak: bagus = done / (done + scrap).
pilihan = [('low', 'C', 'C, jarang'), ('high', 'C', 'C, sering'),
           ('low', 'F', 'F, jarang'), ('high', 'F', 'F, sering')]
bagus = []
for f, c, _ in pilihan:
    d = res['scrap'][f][c]
    bagus.append(100 * d['done'] / (d['done'] + d['scrap']))
fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
for i, g in enumerate(bagus):
    ax.bar(i, g, 0.6, color=BLUE)
    ax.bar(i, 100 - g, 0.6, bottom=g, color=ORANGE)
    # label ditaruh di atas batang (bukan di dalam) karena sebagian segmen sangat tipis
    ax.text(i, 103, f'Bagus {koma(g, 1)}%\nScrap {koma(100 - g, 1)}%',
            ha='center', va='bottom', fontsize=8)
ax.set_xticks(range(4))
ax.set_xticklabels([p[2] for p in pilihan])
ax.set_ylim(0, 120)
ax.set_yticks(range(0, 101, 20))
ax.set_ylabel('Persen part')
rapikan(ax)
handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
fig.legend(handles, ['Part bagus', 'Part dibuang (scrap)'], loc='lower center', ncol=2, frameon=False)
fig.subplots_adjust(top=0.97, bottom=0.25, left=0.11, right=0.98)
fig.savefig('gambar_09_yield_scrap.png')
plt.close(fig)

# Gambar 12 (Soal 14)
# Pembagian waktu tiap press pada alokasi buffer terbaik (1,5,9).
# Urutan keadaan di model_lini_4_press.py: [IDLE, BUSY, DOWN, DIE, BLOCK].
util = r14['b']['(1, 5, 9)']['util']
mesin = ['Shear', 'Punch', 'Form', 'Bend']
# (indeks keadaan, nama pada legenda, warna) dalam urutan susunan batang dari kiri ke kanan
susunan = [(1, 'Proses', '#2E75B6'), (2, 'Down', '#C00000'), (3, 'Ganti die', '#FFC000'),
           (0, 'Starved', '#A6A6A6'), (4, 'Blocked', '#ED7D31')]
fig, ax = plt.subplots(figsize=(6.9, 3.2), dpi=200)
for r, nama in enumerate(mesin):
    y = 3 - r
    kiri = 0
    for idx, _, warna in susunan:
        v = 100 * util[r][idx]
        if v > 0:
            ax.barh(y, v, 0.62, left=kiri, color=warna)
            if v >= 5:                                    # segmen kecil tidak diberi label
                ax.text(kiri + v / 2, y, koma(v, 1), ha='center', va='center', fontsize=8,
                        color='white' if idx in (1, 2) else 'black')
        kiri += v
    # nilai "down" yang segmennya sempit ditulis di sisi kanan batang
    ax.text(101.5, y, f'down {koma(100 * util[r][2], 1)}%', ha='left', va='center',
            fontsize=8, color='#C00000')
ax.set_yticks([3, 2, 1, 0])
ax.set_yticklabels(mesin)
ax.set_xlim(0, 118)
ax.set_xticks(range(0, 101, 20))
ax.set_xlabel('Persen waktu')
ax.set_ylim(-0.6, 3.6)
rapikan(ax)
handles = [plt.Rectangle((0, 0), 1, 1, color=w) for _, _, w in susunan]
fig.legend(handles, [n for _, n, _ in susunan], loc='upper center', ncol=5, frameon=False,
           bbox_to_anchor=(0.45, 1.0), fontsize=8.5)
fig.subplots_adjust(top=0.88, bottom=0.17, left=0.09, right=0.98)
fig.savefig('gambar_12_utilisasi_press.png')
plt.close(fig)

print('Yield bagus (%):', [round(g, 1) for g in bagus])
