"""
Membuat 6 gambar dengan Matplotlib:
    Gambar 1  : alur proses satu mesin, kebijakan resume       (Soal 10)
    Gambar 2  : logika event scheduling model satu mesin       (Soal 10-13)
    Gambar 7  : alur proses satu mesin, kebijakan restart      (Soal 12)
    Gambar 8  : alur proses satu mesin, kebijakan scrap        (Soal 13)
    Gambar 10 : alur proses lini 4 press                       (Soal 14)
    Gambar 11 : logika simulasi satu press                     (Soal 14)

Aturan gambar supaya garis tidak bertabrakan:
  * semua panah memakai jalur siku-siku (horizontal/vertikal), tanpa panah diagonal;
  * ujung panah selalu tepat di tepi kotak (koordinat tepi dihitung dari pusat +- setengah ukuran);
  * jalur "kembali" (loop) dibuat melewati sisi luar diagram sehingga tidak memotong kotak lain;
  * label diletakkan di ruang kosong di samping garis.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, Polygon, FancyBboxPatch

plt.rcParams['font.family'] = 'Liberation Serif'
LW = 1.3                                  # tebal garis


# alat bantu menggambar
def kanvas(x0, x1, y0, y1, s=0.62):
    # Buat kanvas dengan skala sama di sumbu x dan y (supaya lingkaran/belah ketupat tidak gepeng).
    fig = plt.figure(figsize=((x1 - x0) * s, (y1 - y0) * s))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis('off')
    return fig, ax

def kotak(ax, x, y, w, h, teks, putus=False, fs=9.5, bulat=False):
    # Kotak berpusat di (x,y) dengan lebar w dan tinggi h. putus=True -> garis putus-putus.
    gaya = (0, (4, 3)) if putus else '-'
    if bulat:
        p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.25',
                           fc='white', ec='black', lw=LW, ls=gaya, zorder=2)
    else:
        p = Rectangle((x - w / 2, y - h / 2), w, h, fc='white', ec='black', lw=LW, ls=gaya, zorder=2)
    ax.add_patch(p)
    ax.text(x, y, teks, ha='center', va='center', fontsize=fs, zorder=3, linespacing=1.25)

def oval(ax, x, y, w, h, teks, fs=9.5):
    # Elips untuk titik awal/akhir proses.
    ax.add_patch(Ellipse((x, y), w, h, fc='white', ec='black', lw=LW, zorder=2))
    ax.text(x, y, teks, ha='center', va='center', fontsize=fs, zorder=3, linespacing=1.25)

def belah(ax, x, y, w, h, teks, fs=9):
    # Belah ketupat untuk keputusan (ya/tidak).
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                         closed=True, fc='white', ec='black', lw=LW, zorder=2))
    ax.text(x, y, teks, ha='center', va='center', fontsize=fs, zorder=3, linespacing=1.2)

def panah(ax, titik, kepala=True):
    # Garis siku-siku melalui daftar titik; kepala panah di titik terakhir.
    xs = [p[0] for p in titik]
    ys = [p[1] for p in titik]
    ax.plot(xs, ys, color='black', lw=LW, zorder=1, solid_capstyle='butt', solid_joinstyle='miter')
    if kepala:
        ax.annotate('', xy=titik[-1], xytext=titik[-2], zorder=4,
                    arrowprops=dict(arrowstyle='-|>', color='black', lw=LW, shrinkA=0,
                                    shrinkB=0, mutation_scale=13))

def garis(ax, titik):
    # Garis siku-siku tanpa kepala panah (untuk bus penghubung).
    ax.plot([p[0] for p in titik], [p[1] for p in titik], color='black', lw=LW, zorder=1)

def label(ax, x, y, teks, ha='center', va='center', fs=9.5, miring=True):
    # Teks keterangan (ya/tidak/rusak, dst.).
    ax.text(x, y, teks, ha=ha, va=va, fontsize=fs, style='italic' if miring else 'normal', zorder=5)

# Gambar 1, 7, 8
def alur_satu_mesin(mode, nama_file):
    # Alur proses satu mesin. mode: 'resume' | 'restart' | 'scrap'.
    fig, ax = kanvas(0, 11.6, (-0.9 if mode == 'scrap' else 0.35), 5.0)
    y1, y2 = 4.0, 1.4                      # tinggi baris atas dan baris bawah
    # baris atas: datang -> antrian -> mesin -> selesai
    oval(ax, 1.3, y1, 2.3, 1.6, 'Part datang\n(acak, rata-rata\ntiap 10 menit)', fs=9)
    kotak(ax, 4.0, y1, 2.2, 1.6, 'Antrian FIFO\ndi depan mesin')
    kotak(ax, 6.9, y1, 2.6, 1.6, 'Diproses mesin\n(rata-rata\n7,5 menit)')
    oval(ax, 10.2, y1, 2.4, 1.6, 'Part selesai,\nkeluar dari\nsistem', fs=9)
    panah(ax, [(2.45, y1), (2.9, y1)])
    panah(ax, [(5.1, y1), (5.6, y1)])
    panah(ax, [(8.2, y1), (9.0, y1)])
    # baris bawah: mesin rusak -> perbaikan
    if mode == 'scrap':
        kotak(ax, 5.1, y2, 2.6, 1.7, 'Mesin rusak,\npart yang sedang\ndiproses dibuang',
              putus=True, fs=9)
    else:
        kotak(ax, 5.1, y2, 2.6, 1.7, 'Mesin rusak\n(rata-rata tiap\n1000 menit)', putus=True, fs=9)
    kotak(ax, 8.9, y2, 2.4, 1.7, 'Perbaikan\n(rata-rata\n50 menit)', putus=True, fs=9)
    panah(ax, [(5.9, y1 - 0.8), (5.9, y2 + 0.85)])       # mesin -> rusak
    label(ax, 5.75, 2.75, 'rusak', ha='right')
    panah(ax, [(6.4, y2), (7.7, y2)])                     # rusak -> perbaikan
    # jalur kembali setelah perbaikan
    if mode == 'resume':
        panah(ax, [(7.95, y2 + 0.85), (7.95, y1 - 0.8)])  # kembali ke mesin
        label(ax, 8.1, 2.75, 'lanjutkan sisa proses', ha='left')
    elif mode == 'restart':
        panah(ax, [(7.95, y2 + 0.85), (7.95, y1 - 0.8)])
        label(ax, 8.1, 2.75, 'proses diulang\ndari awal', ha='left')
    else:
        # part dibuang, jadi mesin mengambil part berikutnya dari antrian.
        # Jalur lewat bawah supaya tidak menembus kotak "Mesin rusak".
        panah(ax, [(8.9, y2 - 0.85), (8.9, -0.25), (3.3, -0.25), (3.3, y1 - 0.8)])
        label(ax, 6.1, -0.55, 'mesin selesai diperbaiki, ambil part berikutnya dari antrian')
    fig.savefig(nama_file, dpi=200)
    plt.close(fig)

# Gambar 2
def logika_event():
    # Diagram alir logika event scheduling: ambil event terkecil -> proses -> ulangi.
    fig, ax = kanvas(-0.2, 10.9, -1.0, 13.2, s=0.66)
    cx = 5.0                                              # sumbu tengah
    oval(ax, cx, 12.7, 2.0, 0.8, 'Mulai')
    kotak(ax, cx, 11.5, 6.4, 1.0, 'Set parameter kasus, buat event list,\n'
          'jadwalkan kedatangan dan kerusakan pertama', fs=9)
    kotak(ax, cx, 10.1, 5.0, 1.0, 'Ambil event dengan waktu terkecil,\nmajukan jam simulasi', fs=9)
    panah(ax, [(cx, 12.3), (cx, 12.0)])
    panah(ax, [(cx, 11.0), (cx, 10.6)])
    # percabangan ke 4 jenis event memakai "bus" horizontal (tanpa panah diagonal)
    xs = [1.25, 3.65, 6.05, 8.45]
    y_bus1 = 9.2
    garis(ax, [(cx, 9.6), (cx, y_bus1)])
    garis(ax, [(xs[0], y_bus1), (xs[-1], y_bus1)])
    teks = ['Kedatangan:\npart masuk antrian,\njadwalkan kedatangan\nberikutnya; mulai\nproses bila mesin bebas',
            'Selesai proses:\ncatat statistik,\nambil part berikutnya\ndari antrian',
            'Mesin rusak:\nmesin down.\nResume: simpan sisa\nRestart: ulang\nScrap: part dibuang',
            'Selesai repair:\nmesin aktif lagi,\nlanjutkan atau ambil\npart baru, jadwalkan\nrusak berikutnya']
    yc, hh = 7.2, 2.6
    for x, t in zip(xs, teks):
        panah(ax, [(x, y_bus1), (x, yc + hh / 2)])
        kotak(ax, x, yc, 2.15, hh, t, fs=8)
    # keempat jalur bertemu lagi pada bus kedua
    y_bus2 = 5.0
    for x in xs:
        garis(ax, [(x, yc - hh / 2), (x, y_bus2)])
    garis(ax, [(xs[0], y_bus2), (xs[-1], y_bus2)])
    kotak(ax, cx, 3.9, 5.6, 1.0, 'Perbarui antrian dan statistik,\njadwalkan event baru', fs=9)
    panah(ax, [(cx, y_bus2), (cx, 4.4)])
    belah(ax, cx, 2.35, 3.8, 1.6, 'Waktu simulasi\nhabis?', fs=9)
    panah(ax, [(cx, 3.4), (cx, 3.15)])
    # "belum": kembali ke pengambilan event lewat sisi kanan (di luar semua kotak)
    panah(ax, [(cx + 1.9, 2.35), (10.5, 2.35), (10.5, 10.1), (cx + 2.5, 10.1)])
    label(ax, 8.2, 2.6, 'belum', va='bottom')
    kotak(ax, cx, 0.5, 5.6, 0.9, 'Hitung Lq, persen waktu down, jumlah part,\ndan statistik lain', fs=9)
    panah(ax, [(cx, 1.55), (cx, 0.95)])
    label(ax, cx + 0.2, 1.25, 'sudah', ha='left')
    oval(ax, cx, -0.6, 2.0, 0.7, 'Selesai')
    panah(ax, [(cx, 0.05), (cx, -0.25)])
    fig.savefig('gambar_02_logika_event.png', dpi=200)
    plt.close(fig)

# Gambar 10
def alur_lini_press():
    # Alur proses lini 4 press: dua baris berbentuk huruf S."
    fig, ax = kanvas(0, 11.2, 0.3, 5.9, s=0.66)
    xs1 = [1.1, 3.3, 5.5, 7.7, 9.9]
    y1, y2 = 4.7, 1.6
    oval(ax, xs1[0], y1, 1.9, 1.5, 'Bahan baku\n(tak terbatas)', fs=9)
    kotak(ax, xs1[1], y1, 1.8, 1.5, 'Shear\n4,5 lembar/mnt', fs=9)
    kotak(ax, xs1[2], y1, 1.5, 1.2, 'Buffer 1', putus=True, fs=9, bulat=True)
    kotak(ax, xs1[3], y1, 1.8, 1.5, 'Punch\n5,5 lembar/mnt', fs=9)
    kotak(ax, xs1[4], y1, 1.5, 1.2, 'Buffer 2', putus=True, fs=9, bulat=True)
    panah(ax, [(2.05, y1), (2.4, y1)])
    panah(ax, [(4.2, y1), (4.75, y1)])
    panah(ax, [(6.25, y1), (6.8, y1)])
    panah(ax, [(8.6, y1), (9.15, y1)])
    kotak(ax, 9.9, y2, 1.8, 1.5, 'Form\n3,8 lembar/mnt', fs=9)
    kotak(ax, 7.7, y2, 1.5, 1.2, 'Buffer 3', putus=True, fs=9, bulat=True)
    kotak(ax, 5.5, y2, 1.8, 1.5, 'Bend\n3,2 lembar/mnt', fs=9)
    oval(ax, 3.3, y2, 1.9, 1.5, 'Produk jadi', fs=9)
    panah(ax, [(9.9, y1 - 0.6), (9.9, y2 + 0.75)])        # baris atas -> baris bawah
    panah(ax, [(9.0, y2), (8.45, y2)])
    panah(ax, [(6.95, y2), (6.4, y2)])
    panah(ax, [(4.6, y2), (4.25, y2)])
    ax.text(5.6, 3.15, 'Kotak solid = mesin;  kotak putus-putus = buffer (ruang antar mesin)',
            ha='center', va='center', fontsize=9, style='italic')
    fig.savefig('gambar_10_alur_lini_press.png', dpi=200)
    plt.close(fig)

# Gambar 11
def logika_satu_press():
    # Logika satu mesin press: ambil lembar -> proses -> rusak? -> buffer hilir -> ganti die.
    fig, ax = kanvas(-0.9, 12.6, 0.9, 14.0, s=0.58)
    mx, rx = 4.6, 9.0                 # kolom utama (kiri) dan kolom samping (kanan)
    L = -0.6                          # jalur kembali di sisi kiri
    R1, R2 = 11.3, 11.9               # dua jalur kembali di sisi kanan

    # 1-2. ambil lembar, cek ketersediaan di buffer hulu
    kotak(ax, mx, 13.2, 5.0, 0.9, 'Ambil lembar dari buffer hulu\n(Shear: bahan tak terbatas)', fs=8.5)
    belah(ax, mx, 11.7, 3.6, 1.5, 'Ada lembar\ndi buffer hulu?', fs=8.5)
    panah(ax, [(mx, 12.75), (mx, 12.45)])
    kotak(ax, rx, 11.7, 3.0, 0.9, 'Starved: menunggu\nlembar dari hulu', fs=8.5)
    panah(ax, [(mx + 1.8, 11.7), (rx - 1.5, 11.7)])
    label(ax, (mx + 1.8 + rx - 1.5) / 2, 11.95, 'tidak', fs=8.5)
    panah(ax, [(rx, 12.15), (rx, 12.6), (mx, 12.6)], kepala=False)   # menunggu lalu cek lagi

    # 3. proses lembar
    kotak(ax, mx, 10.0, 5.0, 1.0, 'Proses lembar selama 1/laju menit\n'
          '(umur sebelum rusak berkurang saat memproses)', fs=8.5)
    panah(ax, [(mx, 10.95), (mx, 10.5)])
    label(ax, mx + 0.15, 10.78, 'ya', ha='left', fs=8.5)

    # 4. rusak sebelum selesai? -> repair -> scrap?
    belah(ax, mx, 8.4, 3.8, 1.5, 'Rusak sebelum\nselesai?', fs=8.5)
    panah(ax, [(mx, 9.5), (mx, 9.15)])
    kotak(ax, rx, 8.4, 3.0, 1.0, 'Mesin down: repair\nU(rata-rata ± 5 menit)', fs=8.5)
    panah(ax, [(mx + 1.9, 8.4), (rx - 1.5, 8.4)])
    label(ax, (mx + 1.9 + rx - 1.5) / 2, 8.65, 'ya', fs=8.5)
    belah(ax, rx, 6.6, 3.0, 1.5, 'Lembar scrap?\n(peluang 20%)', fs=8.5)
    panah(ax, [(rx, 7.9), (rx, 7.35)])
    # tidak scrap -> proses diulang dari awal (jalur kanan menuju kotak "Proses lembar")
    panah(ax, [(rx + 1.5, 6.6), (R1, 6.6), (R1, 10.0), (mx + 2.5, 10.0)])
    label(ax, (rx + 1.5 + R1) / 2, 6.85, 'tidak', fs=8.5)
    label(ax, 8.9, 10.27, 'ulang dari awal', fs=8.5)
    # scrap -> lembar dibuang, kembali mengambil lembar baru (jalur paling kanan)
    kotak(ax, rx, 4.9, 3.0, 0.9, 'Lembar dibuang,\nambil lembar baru', fs=8.5)
    panah(ax, [(rx, 5.85), (rx, 5.35)])
    label(ax, rx + 0.15, 5.6, 'ya', ha='left', fs=8.5)
    panah(ax, [(rx + 1.5, 4.9), (R2, 4.9), (R2, 13.2), (mx + 2.5, 13.2)])

    # 5. tidak rusak -> buffer hilir ada ruang?
    belah(ax, mx, 6.6, 3.8, 1.5, 'Buffer hilir\nada ruang?', fs=8.5)
    panah(ax, [(mx, 7.65), (mx, 7.35)])
    kotak(ax, 0.9, 6.6, 2.1, 1.1, 'Blocked: lembar\ntertahan, mesin\nmenunggu ruang\nlalu cek lagi', fs=7.8)
    panah(ax, [(mx - 1.9, 6.6), (1.95, 6.6)])
    label(ax, 2.32, 6.9, 'tidak', fs=8.0)
    kotak(ax, mx, 4.9, 5.0, 1.0, 'Pindahkan lembar ke buffer hilir\n(Bend: produksi bertambah 1)', fs=8.5)
    panah(ax, [(mx, 5.85), (mx, 5.4)])
    label(ax, mx + 0.15, 5.65, 'ya', ha='left', fs=8.5)

    # 6. sudah N lembar sejak ganti die?
    belah(ax, mx, 3.2, 3.8, 1.5, 'Sudah N lembar\nsejak ganti die?', fs=8.5)
    panah(ax, [(mx, 4.4), (mx, 3.95)])
    kotak(ax, rx, 3.2, 3.0, 0.9, 'Ganti die\n25 menit', fs=8.5)
    panah(ax, [(mx + 1.9, 3.2), (rx - 1.5, 3.2)])
    label(ax, (mx + 1.9 + rx - 1.5) / 2, 3.45, 'ya', fs=8.5)
    # kembali ke awal (jalur kiri): dari "ganti die" dan dari cabang "tidak"
    panah(ax, [(rx, 2.75), (rx, 1.7), (L, 1.7), (L, 13.2), (mx - 2.5, 13.2)])
    garis(ax, [(mx - 1.9, 3.2), (L, 3.2)])
    label(ax, 1.9, 3.45, 'tidak', fs=8.5)
    fig.savefig('gambar_11_logika_press.png', dpi=200)
    plt.close(fig)

if __name__ == '__main__':
    alur_satu_mesin('resume', 'gambar_01_alur_resume.png')
    logika_event()
    alur_satu_mesin('restart', 'gambar_07_alur_restart.png')
    alur_satu_mesin('scrap', 'gambar_08_alur_scrap.png')
    alur_lini_press()
    logika_satu_press()
    print('selesai: 6 diagram alur dibuat')
