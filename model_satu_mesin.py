"""
Dipakai untuk Soal 10, 11, 12 dan 13.

Sistem yang dimodelkan
    Part datang secara acak -> antri (FIFO) -> diproses oleh 1 mesin -> keluar.
    Mesin bisa rusak. Kerusakan dihitung berdasarkan WAKTU JAM DINDING (clock time),
    artinya mesin bisa rusak kapan saja, termasuk saat sedang menganggur.

Pendekatan simulasi
    Event scheduling (simulasi event diskrit). Daftar kejadian (event list) disimpan
    sebagai antrian prioritas (heapq) yang diurutkan menurut waktu kejadian.
    Ada 4 jenis kejadian:
        'arr'    : kedatangan part baru
        'end'    : selesai memproses part
        'fail'   : mesin rusak
        'repair' : mesin selesai diperbaiki

Tiga kebijakan bila mesin rusak saat sedang memproses part (parameter `mode`):
    'resume'  : part dilanjutkan setelah repair, sisa waktu proses tetap (Soal 10, 11)
    'restart' : part diproses ulang dari awal (Soal 12)
    'scrap'   : part yang sedang diproses dibuang (Soal 13)

Bilangan acak
    NumPy (PCG64). Ada 4 aliran acak terpisah (kedatangan, waktu proses, waktu ke
    kerusakan, waktu repair) supaya perubahan satu aspek tidak mengacak aspek lain.
    Seed dicatat sehingga hasil dapat diulang persis.
"""
import heapq
import numpy as np

# Distribusi input
def make_dist(kind, mean, rng):
    """Buat fungsi pembangkit nilai acak.
    kind = 'exp'  -> eksponensial dengan rata-rata `mean`
    kind lain ('det') -> konstan sebesar `mean` (deterministik)."""
    if kind == 'exp':
        return lambda: rng.exponential(mean)
    return lambda: mean

# Fungsi utama simulasi
def simulate(arr=('exp', 10), svc=('exp', 7.5), ttf=('exp', 1000), ttr=('exp', 50),
             breakdown=True, mode='resume', T=100000, seed=1, record=False):
    """
    Jalankan SATU replikasi simulasi.

    Parameter
        arr, svc, ttf, ttr : tuple (jenis, rata-rata) untuk waktu antar kedatangan,
                             waktu proses, waktu ke kerusakan (TTF), waktu repair (TTR)
        breakdown          : False -> mesin tidak pernah rusak (kasus A dan B)
        mode               : 'resume' | 'restart' | 'scrap'
        T                  : panjang run (menit)
        seed               : seed bilangan acak (replikasi berbeda = seed berbeda)
        record             : True -> simpan deret waktu antrian dan interval rusak
                             (dipakai untuk grafik antrian vs waktu, Soal 10b)
    Mengembalikan dictionary berisi ukuran kinerja (Lq, persen down, dst.).
    """

    # 4 aliran bilangan acak terpisah
    ra, rs, rf, rr = [np.random.default_rng([seed, k]) for k in range(4)]
    A = make_dist(*arr, ra)    # waktu antar kedatangan
    S = make_dist(*svc, rs)    # waktu proses
    F = make_dist(*ttf, rf)    # waktu sampai kerusakan berikutnya
    R = make_dist(*ttr, rr)    # lama perbaikan

    # event list: elemen = (waktu, nomor urut, jenis, token)
    # nomor urut `cnt` menjamin urutan pasti bila dua kejadian terjadi bersamaan.
    ev = []
    cnt = 0

    def push(t, kind, tok=0):
        nonlocal cnt
        cnt += 1
        heapq.heappush(ev, (t, cnt, kind, tok))

    push(A(), 'arr')                 # kedatangan pertama
    if breakdown:
        push(F(), 'fail')            # kerusakan pertama

    # variabel keadaan sistem
    queue = []                       # waktu datang part-part yang sedang menunggu
    busy = False                     # mesin sedang memproses part?
    down = False                     # mesin sedang diperbaiki?
    rem = 0.0                        # sisa waktu proses part yang sedang dikerjakan
    start = 0.0                      # waktu saat part mulai (atau lanjut) diproses
    tok = 0                          # token: membatalkan kejadian 'end' yang sudah usang
    cur = None                       # catatan part yang sedang diproses

    # penampung statistik
    area_q = 0.0                     # integral jumlah antrian terhadap waktu (untuk Lq)
    last = 0.0                       # waktu terakhir statistik antrian diperbarui
    down_time = 0.0                  # total waktu mesin rusak
    down_start = 0.0                 # awal periode rusak yang sedang berjalan
    n_done = 0                       # part yang selesai
    n_scrap = 0                      # part yang dibuang
    n_arr = 0                        # part yang datang
    svc_times = []                   # waktu layanan tiap part (termasuk downtime)
    dts_per_part = []                # total downtime yang dialami tiap part
    n_fail_parts = []                # jumlah downtime yang dialami tiap part
    fail_events = []                 # lama tiap kejadian rusak
    q_series = [(0, 0)] if record else None   # deret waktu panjang antrian
    down_intervals = []              # (awal, akhir) tiap periode rusak

    def upd(t):
        # Perbarui integral antrian sampai waktu t (dipanggil sebelum keadaan berubah).
        nonlocal area_q, last
        area_q += len(queue) * (t - last)
        last = t

    def begin(t):
        # Mulai memproses part terdepan di antrian, bila mesin bebas dan tidak rusak.
        nonlocal busy, rem, start, tok, cur
        if not queue or down or busy:
            return
        at = queue.pop(0)
        if record:
            q_series.append((t, len(queue)))
        busy = True
        rem = S()
        start = t
        tok += 1
        cur = dict(arr=at, st=t, nd=0, dt=0.0)   # nd = jml downtime, dt = lama downtime
        push(t + rem, 'end', tok)

    # loop utama: ambil kejadian dengan waktu terkecil, majukan jam simulasi
    while ev:
        t, _, kind, k = heapq.heappop(ev)
        if t > T:
            break
        upd(t)

        if kind == 'arr':                      # kedatangan part
            n_arr += 1
            queue.append(t)
            if record:
                q_series.append((t, len(queue)))
            push(t + A(), 'arr')               # jadwalkan kedatangan berikutnya
            begin(t)                           # mulai proses bila mesin bebas

        elif kind == 'end':                    # selesai proses
            if k != tok or not busy:           # kejadian usang (sudah dibatalkan)
                continue
            busy = False
            n_done += 1
            svc_times.append(t - cur['st'])
            dts_per_part.append(cur['dt'])
            n_fail_parts.append(cur['nd'])
            cur = None
            begin(t)                           # ambil part berikutnya

        elif kind == 'fail':                   # mesin rusak
            down = True
            down_start = t
            d = R()                            # lama perbaikan kali ini
            down_intervals.append((t, t + d))
            fail_events.append(d)
            if busy:                           # ada part yang sedang diproses
                tok += 1                       # batalkan kejadian 'end' yang terjadwal
                if mode == 'resume':           # lanjutkan: kurangi sisa waktu proses
                    rem = rem - (t - start)
                    cur['nd'] += 1
                    cur['dt'] += d
                elif mode == 'restart':        # ulang dari awal
                    # proses acak: ambil undian baru; proses konstan: mulai dari nol lagi
                    rem = S() if svc[0] == 'exp' else svc[1]
                    cur['nd'] += 1
                    cur['dt'] += d
                elif mode == 'scrap':          # buang part, mesin jadi kosong
                    n_scrap += 1
                    busy = False
                    cur = None
            push(t + d, 'repair')

        elif kind == 'repair':                 # selesai diperbaiki
            down = False
            down_time += t - down_start
            if breakdown:
                push(t + F(), 'fail')          # jadwalkan kerusakan berikutnya
            if busy:                           # lanjutkan part yang tertunda
                start = t
                tok += 1
                push(t + rem, 'end', tok)
            else:
                begin(t)                       # atau ambil part baru dari antrian

    # penutupan run: lengkapi statistik sampai waktu T
    upd(T)
    if down:
        down_time += T - down_start

    out = dict(
        Lq=area_q / T,                                  # rata-rata jumlah part di antrian
        pct_down=down_time / T,                         # fraksi waktu mesin rusak
        done=n_done, scrap=n_scrap, arrivals=n_arr,
        n_fail=len(fail_events),                        # jumlah kerusakan
        q_end=len(queue),                               # sisa antrian di akhir run
        svc_mean=float(np.mean(svc_times)) if svc_times else float('nan'),
        nd_mean=float(np.mean(n_fail_parts)) if n_fail_parts else float('nan'),
        pct_parts_hit=float(np.mean(np.array(n_fail_parts) > 0)) if n_fail_parts else float('nan'),
        dt_per_part=float(np.mean(dts_per_part)) if dts_per_part else float('nan'),
        dt_per_event=float(np.mean(fail_events)) if fail_events else float('nan'))
    # rata-rata downtime per part, hanya untuk part yang pernah terkena downtime
    hit = [d for d, n in zip(dts_per_part, n_fail_parts) if n > 0]
    out['dt_per_hit_part'] = float(np.mean(hit)) if hit else float('nan')
    # rata-rata lama satu downtime yang dialami part
    out['dur_per_downtime_exp'] = (float(sum(dts_per_part) / sum(n_fail_parts))
                                   if sum(n_fail_parts) > 0 else float('nan'))
    if record:
        out['q_series'] = q_series
        out['down_intervals'] = down_intervals
    return out

# Definisi enam kasus (Tabel 1 buku Banks)
# 'det' = deterministik (konstan), 'exp' = eksponensial.
CASES = {
    'A': dict(label='A. Abaikan breakdown', arr=('exp', 10), svc=('exp', 7.5), breakdown=False),
    'B': dict(label='B. Naikkan service time jadi 8,0', arr=('exp', 10), svc=('exp', 8.0), breakdown=False),
    'C': dict(label='C. Semua random', arr=('exp', 10), svc=('exp', 7.5), ttf='exp', ttr='exp'),
    'D': dict(label='D. Proses random, breakdown deterministik', arr=('exp', 10), svc=('exp', 7.5), ttf='det', ttr='det'),
    'E': dict(label='E. Semua deterministik', arr=('det', 10), svc=('det', 7.5), ttf='det', ttr='det'),
    'F': dict(label='F. Proses deterministik, breakdown random', arr=('det', 10), svc=('det', 7.5), ttf='exp', ttr='exp'),
}

def case_kwargs(c, ttf_mean, ttr_mean):
    # Ubah kode kasus ('A'..'F') + rata-rata TTF/TTR menjadi argumen untuk simulate().
    # Frekuensi rendah : ttf_mean=1000, ttr_mean=50
    # Frekuensi tinggi : ttf_mean=2,    ttr_mean=0.1
    d = CASES[c]
    kw = dict(arr=d['arr'], svc=d['svc'])
    if d.get('breakdown', True) is False:
        kw['breakdown'] = False            # kasus A, B: tanpa kerusakan
    else:
        kw['ttf'] = (d['ttf'], ttf_mean)
        kw['ttr'] = (d['ttr'], ttr_mean)
    return kw
