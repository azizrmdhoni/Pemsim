"""
    Bahan baku (tak terbatas) -> Shear -> [Buffer 1] -> Punch -> [Buffer 2]
                              -> Form -> [Buffer 3] -> Bend -> produk jadi

Asumsi pemodelan (sesuai soal)
  * Waktu proses lembar = 1/laju (konstan).
  * Waktu ke kerusakan (TTF) eksponensial, dihitung dari WAKTU MESIN SEDANG MEMPROSES
    (busy time). Mesin yang menganggur, terblokir, atau ganti die tidak "aus".
  * Waktu repair Uniform(rata-rata - 5, rata-rata + 5) menit.
  * Saat rusak: 20% lembar yang sedang diproses dibuang (scrap); 80% diproses ulang
    dari awal setelah repair.
  * Ganti die 25 menit (konstan), dilakukan di antara dua lembar setelah N lembar
    selesai diproses.
  * Buffer terbatas: bila buffer hilir penuh, lembar yang selesai TETAP di dalam mesin
    dan mesin terblokir (state BLOCK) sampai ada ruang.
  * Mesin yang buffer hulunya kosong menganggur (starved), dicatat sebagai IDLE.

Pendekatan simulasi: event scheduling dengan antrian prioritas (heapq).
Jenis kejadian: 'kick' (awal), 'done' (selesai proses), 'fail' (rusak),
                'repair' (selesai repair), 'diedone' (selesai ganti die).
"""
import heapq
import numpy as np

# parameter soal
NAMES = ['Shear', 'Punch', 'Form', 'Bend']
RATE = [4.5, 5.5, 3.8, 3.2]          # lembar per menit
MTTF = [100, 90, 180, 240]           # rata-rata waktu ke kerusakan (menit)
MTTR = [8, 10, 9, 20]                # rata-rata waktu repair (menit)
NDIE = [500, 400, 750, 600]          # jumlah lembar antar penggantian die
TDIE = 25.0                          # lama ganti die (menit)

# keadaan mesin. Urutan ini juga menjadi indeks kolom hasil utilisasi `util`.
IDLE, BUSY, DOWN, DIE, BLOCK = range(5)
INF = 10 ** 9                        # kapasitas buffer "tak terbatas"


def simulate(caps=(INF, INF, INF), T=28800.0, seed=1):
    """
    Jalankan SATU replikasi lini press.

    caps : kapasitas ketiga buffer (B1, B2, B3). Default = tak terbatas.
    T    : panjang run (menit). 28.800 menit = 480 jam.
    seed : seed bilangan acak.
    Mengembalikan dict: out (total produksi), tput (lembar/jam), util (fraksi waktu
    tiap keadaan per mesin), bavg/bmax (isi rata-rata/maksimum tiap buffer), scrap.
    """

    # 3 kelompok aliran acak terpisah untuk tiap mesin: kerusakan, repair, keputusan scrap
    rngF = [np.random.default_rng([seed, 10 + i]) for i in range(4)]
    rngR = [np.random.default_rng([seed, 20 + i]) for i in range(4)]
    rngS = [np.random.default_rng([seed, 30 + i]) for i in range(4)]
    pt = [1.0 / r for r in RATE]                 # waktu proses per lembar

    # event list
    ev = []
    cnt = 0

    def push(t, kind, i, tok):
        nonlocal cnt
        cnt += 1
        heapq.heappush(ev, (t, cnt, kind, i, tok))

    # keadaan tiap mesin
    state = [IDLE] * 4                           # keadaan sekarang
    last = [0.0] * 4                             # waktu terakhir keadaan berubah
    tin = [[0.0] * 5 for _ in range(4)]          # total waktu di tiap keadaan
    ttf = [rngF[i].exponential(MTTF[i]) for i in range(4)]   # sisa umur sebelum rusak
    has = [False] * 4                            # mesin sedang memegang sebuah lembar?
    count = [0] * 4                              # lembar sejak ganti die terakhir
    tok = [0] * 4                                # token pembatal kejadian usang

    # buffer dan statistiknya
    buf = [0, 0, 0]                              # isi buffer sekarang
    barea = [0.0] * 3                            # integral isi buffer (untuk rata-rata)
    bmax = [0] * 3                               # isi maksimum
    blast = 0.0                                  # waktu terakhir statistik buffer diperbarui
    out = 0                                      # produksi (lembar keluar dari Bend)
    scrap = [0] * 4                              # lembar dibuang per mesin

    def setst(i, t, s):
        # Ubah keadaan mesin i menjadi s pada waktu t, sambil mencatat lama keadaan lama.
        tin[i][state[i]] += t - last[i]
        last[i] = t
        state[i] = s

    def bupd(t):
        # Perbarui integral isi buffer sampai waktu t (panggil sebelum isi buffer berubah).
        nonlocal blast
        for k in range(3):
            barea[k] += buf[k] * (t - blast)
        blast = t

    def try_start(i, t):
        # Coba mulai memproses lembar di mesin i (hanya bila mesin sedang IDLE).
        if state[i] != IDLE:
            return
        if not has[i]:                           # mesin belum punya lembar -> ambil dulu
            if i == 0:
                has[i] = True                    # Shear: bahan baku tak terbatas
            else:
                if buf[i - 1] == 0:              # buffer hulu kosong -> tetap starved
                    return
                bupd(t)
                buf[i - 1] -= 1
                has[i] = True
                if state[i - 1] == BLOCK:        # mesin hulu yang terblokir kini bisa lanjut
                    unblock(i - 1, t)
        setst(i, t, BUSY)
        tok[i] += 1
        # apakah mesin rusak sebelum lembar ini selesai?
        if ttf[i] < pt[i]:
            push(t + ttf[i], 'fail', i, tok[i])
        else:
            push(t + pt[i], 'done', i, tok[i])

    def after_exit(i, t):
        # Lembar mesin i sudah keluar. Ganti die bila sudah N lembar, kalau tidak lanjut.
        has[i] = False
        if count[i] >= NDIE[i]:
            count[i] = 0
            setst(i, t, DIE)
            push(t + TDIE, 'diedone', i, 0)
        else:
            setst(i, t, IDLE)
            try_start(i, t)

    def deliver(i, t):
        # Coba pindahkan lembar selesai dari mesin i ke buffer hilir. True bila berhasil.
        nonlocal out
        if i == 3:                               # Bend: lembar langsung menjadi produk jadi
            out += 1
            return True
        if buf[i] < caps[i]:                     # masih ada ruang di buffer hilir
            bupd(t)
            buf[i] += 1
            bmax[i] = max(bmax[i], buf[i])
            if state[i + 1] == IDLE:             # mesin hilir yang menunggu bahan segera mulai
                try_start(i + 1, t)
            return True
        return False                             # buffer penuh -> mesin terblokir

    def unblock(i, t):
        # Mesin i yang terblokir mencoba lagi memindahkan lembarnya.
        if deliver(i, t):
            after_exit(i, t)

    # loop utama
    push(0.0, 'kick', 0, 0)                      # pemicu awal: Shear mulai bekerja
    while ev:
        t, _, kind, i, k = heapq.heappop(ev)
        if t > T:
            break
        if kind == 'kick':
            try_start(0, t)

        elif kind == 'done':                     # selesai memproses satu lembar
            if k != tok[i] or state[i] != BUSY:  # kejadian usang
                continue
            ttf[i] -= pt[i]                      # umur sebelum rusak berkurang
            count[i] += 1
            if deliver(i, t):
                after_exit(i, t)
            else:
                setst(i, t, BLOCK)               # buffer hilir penuh

        elif kind == 'fail':                     # mesin rusak saat memproses
            if k != tok[i] or state[i] != BUSY:
                continue
            setst(i, t, DOWN)
            if rngS[i].random() < 0.2:           # 20%: lembar dibuang
                scrap[i] += 1
                has[i] = False
            # (80%: lembar tetap di mesin dan diproses ulang dari awal setelah repair)
            d = rngR[i].uniform(MTTR[i] - 5, MTTR[i] + 5)
            push(t + d, 'repair', i, 0)

        elif kind == 'repair':                   # selesai repair
            ttf[i] = rngF[i].exponential(MTTF[i])    # umur baru sebelum rusak berikutnya
            setst(i, t, IDLE)
            try_start(i, t)

        elif kind == 'diedone':                  # selesai ganti die
            setst(i, t, IDLE)
            try_start(i, t)

    # penutupan run
    bupd(T)
    for i in range(4):
        tin[i][state[i]] += T - last[i]
    util = [[x / T for x in tin[i]] for i in range(4)]
    return dict(out=out, tput=out / (T / 60.0), util=util,
                bavg=[a / T for a in barea], bmax=bmax, scrap=scrap)


if __name__ == '__main__':
    # uji cepat: satu replikasi 480 jam dengan buffer tak terbatas
    print(simulate(T=28800, seed=1))
