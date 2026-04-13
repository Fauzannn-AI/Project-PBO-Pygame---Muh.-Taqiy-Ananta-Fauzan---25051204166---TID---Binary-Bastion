import pygame
import random
import math
import sys

BACKROUND_W, BACKROUND_H = 640, 320
SCREEN_W, SCREEN_H = 1280, 720
SCALE = SCREEN_W // BACKROUND_W
FPS = 60
NEON_RED, NEON_GREEN, WHITE, BLACK = (255, 7, 58), (57, 255, 20), (255, 255, 255), (0, 0, 0)
DARK_BG, DARK_GRAY, YELLOW = (10, 10, 20), (30, 30, 40), (255, 215, 0)
HP_GREEN, HP_RED, HP_ORANGE = (0, 200, 50), (220, 20, 30), (255, 140, 0)

HACKER_W, HACKER_H = 120, 120
HACKER_X, HACKER_Y = BACKROUND_W // 2 - HACKER_W // 2, BACKROUND_H - HACKER_H
MONITOR_X, COLLISION_Y = BACKROUND_W // 2, 200
GETAR_RINGAN, GETAR_SEDANG = 4, 9

MUSUH_DEFS = {
    "NormalMalware": {"kata": ["PING", "PORT", "DATA", "ROOT", "SYNC", "HASH"], "cepat": 24.0, "rusak": 10, "skor": 10, "warna": (150, 180, 255), "jumlah": 1},

    "FastWorm": {"kata": ["NULL", "WORM", "BUG", "LOG", "HEX"], "cepat": 54.0, "rusak": 5, "skor": 15, "warna": (255, 220, 50), "jumlah": 1},

    "GlitchTrojan": {"kata": ["BACKDOOR", "PAYLOAD", "TROJAN", "EXPLOIT"], "cepat": 20.0, "rusak": 15, "skor": 20, "warna": (255, 80, 255), "jumlah": 1},

    "DDoS_Aggressive": {"kata": ["FLOOD", "PACKET", "SPAM", "DDOS", "BURST"], "cepat": 30.0, "rusak": 10, "skor": 25, "warna": (255, 130, 0), "jumlah": 3},

    "BossRansomware": {"kata": ["ENCRYPT_SYS", "OVERRIDE_ROOT", "KERNEL_PANIC", "ZERO_DAY_XPL", "ROOTKIT_CORE"], "cepat": 11.0, "rusak": 40, "skor": 100, "warna": (255, 40, 40), "jumlah": 1},
}

PILIHAN_MUSUH = list(MUSUH_DEFS.keys())
PELUANG_MUNCUL = [40, 25, 20, 20, 5]

def muncul_di_pinggir():
    posisi = random.choice(("atas", "kiri", "kanan"))
    jarak_tepi = 8
    if posisi == "atas":
        return (random.randint(jarak_tepi, BACKROUND_W - jarak_tepi), jarak_tepi)
    elif posisi == "kiri":
        return (jarak_tepi, random.randint(jarak_tepi, BACKROUND_H - HACKER_H - jarak_tepi))
    else:
        return (BACKROUND_W - jarak_tepi, random.randint(jarak_tepi, BACKROUND_H - HACKER_H - jarak_tepi))

def gambar(path, w, h):
    gambar = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(gambar, (w, h))

class EfekGetar:
    def __init__(self):
        self.kekuatan = 0
        self.sisa_waktu = 0.0

    def mulai(self, kekuatan, durasi=0.25):
        if kekuatan >= self.kekuatan or self.sisa_waktu <= 0.0:
            self.kekuatan = kekuatan
            self.sisa_waktu = durasi

    def jalan(self, dt):
        self.sisa_waktu = max(0.0, self.sisa_waktu - dt)

    def ambil_posisi(self):
        if self.sisa_waktu > 0.0:
            return (
                random.randint(-self.kekuatan, self.kekuatan),
                random.randint(-self.kekuatan, self.kekuatan),
            )
        return (0, 0)

class KarakterDasar:
    def __init__(self, x, y, cepat):
        self.x = x
        self.y = y
        self.cepat = cepat
        self.hidup = True

class Musuh(KarakterDasar):
    def __init__(self, jenis, font_kata, pengali_cepat=1.0):
        data_musuh = MUSUH_DEFS[jenis]
        awal_x, awal_y = muncul_di_pinggir()
        kecepatan_akhir = data_musuh["cepat"] * pengali_cepat

        super().__init__(float(awal_x), float(awal_y), kecepatan_akhir)

        self.jenis = jenis
        self.kata = random.choice(data_musuh["kata"])
        self.rusak = data_musuh["rusak"]
        self.skor = data_musuh["skor"]
        self.warna = data_musuh["warna"]
        self.font = font_kata
        self.progres = 0
        self.dikunci = False

    def gerak(self, dt):
        dx = MONITOR_X - self.x
        dy = (320 - 10) - self.y
        jarak_total = math.sqrt((dx ** 2) + (dy ** 2))

        nx, ny = dx / jarak_total, dy / jarak_total

        self.x += nx * self.cepat * dt
        self.y += ny * self.cepat * dt

        if self.y >= 210:
            jarak_ekstra = 10
            if (HACKER_X - jarak_ekstra) <= self.x <= (HACKER_X + HACKER_W + jarak_ekstra):
                self.hidup = False
                return True

        if self.y > 320:
            self.hidup = False
            return False

        return False

    def cek_huruf(self, huruf):
        huruf_diminta = self.kata[self.progres]
        if huruf.upper() == huruf_diminta:
            self.progres += 1
            if self.progres >= len(self.kata):
                self.hidup = False
                return "selesai"
            return "benar"
        else:
            self.progres = 0
            self.dikunci = False
            return "salah"

    def gambar(self, layar):
        ix, iy = int(self.x), int(self.y)

        teks_diketik = self.kata[:self.progres]
        teks_belum = self.kata[self.progres:]

        gambar_diketik = self.font.render(teks_diketik, False, WHITE)
        gambar_belum = self.font.render(teks_belum, False, self.warna)

        total_lebar = gambar_diketik.get_width() + gambar_belum.get_width()
        tinggi_teks = max(gambar_diketik.get_height(), gambar_belum.get_height())
        awal_x = ix - total_lebar // 2
        pos_y = iy - tinggi_teks // 2

        pad = 2
        bg_teks = pygame.Surface((total_lebar + pad * 2, tinggi_teks + pad * 2), pygame.SRCALPHA)
        bg_teks.fill((0, 0, 0, 150))
        layar.blit(bg_teks, (awal_x - pad, pos_y - pad))

        layar.blit(gambar_diketik, (awal_x, pos_y))
        layar.blit(gambar_belum, (awal_x + gambar_diketik.get_width(), pos_y))

        warna_titik = NEON_GREEN if self.dikunci else self.warna
        ukuran_titik = 3 if self.jenis == "BossRansomware" else 2
        pygame.draw.circle(layar, warna_titik, (ix, pos_y - 4), ukuran_titik)

        if self.dikunci:
            pygame.draw.rect(
                layar, NEON_GREEN,
                (awal_x - pad, pos_y - pad, total_lebar + pad * 2, tinggi_teks + pad * 2),
                1
            )

    def ambil_posisi_teks(self):
        return (int(self.x), int(self.y))

    def hitung_jarak(self):
        dx = self.x - MONITOR_X
        dy = self.y - COLLISION_Y
        jarak = math.sqrt((dx ** 2) + (dy ** 2))
        return jarak


class Partikel:
    def __init__(self, x, y, warna):
        self.x = x
        self.y = y

        self.vx = random.uniform(-40, 40)
        self.vy = random.uniform(-40, 10)
        self.nyawa = random.uniform(0.2, 0.5)
        self.nyawa_awal = self.nyawa
        self.warna = warna
        self.ukuran = random.randint(1, 2)

    def gerak(self, dt):
        self.nyawa -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.nyawa > 0

    def gambar(self, layar):
        rasio = self.nyawa / self.nyawa_awal
        r = max(1, int(self.ukuran * rasio))
        pygame.draw.circle(layar, self.warna, (int(self.x), int(self.y)), r)


class GameMain:
    def __init__(self, layar_luar, layar_dalam):
        self.layar_luar = layar_luar
        self.layar_dalam = layar_dalam
        self.getar = EfekGetar()
        self.font_info = pygame.font.Font(None, 18)
        self.font_musuh = pygame.font.Font(None, 22)
        self.font_skor = pygame.font.Font(None, 28)
        self.skor_tertinggi = 0
        self.muat_gambar()
        self.mulai_ulang()

    def muat_gambar(self):
        self.bg = {
            "iddle": gambar("asset/bg_iddle.png", BACKROUND_W, BACKROUND_H),
            "benar": gambar("asset/bg_benar.png", BACKROUND_W, BACKROUND_H),
            "salah": gambar("asset/bg_salah.png", BACKROUND_W, BACKROUND_H),
        }
        self.hacker = {
            "iddle": gambar("asset/hacker_iddle.png", HACKER_W, HACKER_H),
            "typing": gambar("asset/hacker_typing.png", HACKER_W, HACKER_H),
            "salah": gambar("asset/hacker_salah.png", HACKER_W, HACKER_H),
        }

    def mulai_ulang(self):
        self.hp, self.skor = 100, 0
        self.daftar_musuh, self.daftar_partikel = [], []
        self.musuh_aktif = None
        self.waktu_muncul, self.jeda_muncul = 0.0, 3.5
        self.waktu_main, self.pengali_cepat = 0.0, 1.0
        self.status_layar, self.waktu_layar = "iddle", 0.0
        self.waktu_garis, self.target_garis = 0.0, None
        self.kalah, self.kotak_coba = False, None

    def kesulitan(self):
        level = int(self.waktu_main // 15)
        self.jeda_muncul = max(0.7, 3.5 - level * 0.3)
        self.pengali_cepat = 1.0 + level * 0.15

    def bikin_musuh(self):
        jenis_pilihan = random.choices(PILIHAN_MUSUH, weights=PELUANG_MUNCUL, k=1)[0]
        data = MUSUH_DEFS[jenis_pilihan]

        jumlah_bikin = 1
        if data["jumlah"] > 1:
            jumlah_bikin = random.randint(2, data["jumlah"])

        for _ in range(jumlah_bikin):
            self.daftar_musuh.append(Musuh(jenis_pilihan, self.font_musuh, self.pengali_cepat))

    def atur_tampilan(self, status, durasi):
        if status == "benar" and self.status_layar == "salah":
            return
        self.status_layar = status
        self.waktu_layar = durasi

    def tekan_tombol(self, karakter):
        if self.kalah == True or karakter == "":
            return

        karakter = karakter.upper()
        if self.musuh_aktif != None:
            hasil = self.musuh_aktif.cek_huruf(karakter)

            if hasil == "benar":
                self.atur_tampilan("typing", 0.0)
                self.waktu_garis = 0.1
                self.target_garis = self.musuh_aktif.ambil_posisi_teks()

            elif hasil == "selesai":
                self.musuh_mati(self.musuh_aktif)
                self.musuh_aktif = None

            elif hasil == "salah":
                self.musuh_aktif = None
                self.getar.mulai(GETAR_SEDANG, 0.3)
                self.atur_tampilan("salah", 0.5)
                self.waktu_garis = 0.0
                self.target_garis = None

        else:
            musuh_cocok = []
            for m in self.daftar_musuh:
                if m.kata[m.progres] == karakter:
                    musuh_cocok.append(m)

            if not musuh_cocok:
                return

            sasaran = musuh_cocok[0]
            jarak_terdekat = sasaran.hitung_jarak()

            for m in musuh_cocok:
                if m.hitung_jarak() < jarak_terdekat:
                    sasaran = m
                    jarak_terdekat = m.hitung_jarak()

            sasaran.dikunci = True
            self.musuh_aktif = sasaran

            hasil = self.musuh_aktif.cek_huruf(karakter)
            if hasil == "benar":
                self.atur_tampilan("typing", 0.0)
                self.waktu_garis = 0.1
                self.target_garis = self.musuh_aktif.ambil_posisi_teks()

    def musuh_mati(self, target_musuh):
        self.skor += target_musuh.skor
        self.getar.mulai(GETAR_RINGAN, 0.15)
        self.atur_tampilan("benar", 0.3)
        self.waktu_garis = 0.0
        self.target_garis = None

        for _ in range(10):
            self.daftar_partikel.append(Partikel(target_musuh.x, target_musuh.y, target_musuh.warna))

    def jalan_game(self, dt):
        if self.kalah:
            return

        self.waktu_main += dt
        self.kesulitan()

        self.waktu_muncul += dt
        if self.waktu_muncul >= self.jeda_muncul:
            self.waktu_muncul = 0.0
            self.bikin_musuh()

        if self.status_layar in ("salah", "benar") and self.waktu_layar > 0:
            self.waktu_layar -= dt
            if self.waktu_layar <= 0:
                self.waktu_layar = 0.0
                if self.musuh_aktif != None:
                    self.status_layar = "typing"
                else:
                    self.status_layar = "iddle"

        if self.waktu_garis > 0:
            self.waktu_garis -= dt
            if self.waktu_garis <= 0:
                self.target_garis = None

        self.getar.jalan(dt)

        partikel_baru = []
        for p in self.daftar_partikel:
            masih_hidup = p.gerak(dt)
            if masih_hidup == True:
                partikel_baru.append(p)
        self.daftar_partikel = partikel_baru

        musuh_tembus = []
        musuh_hancur = []

        for m in self.daftar_musuh:
            if m.hidup == False:
                musuh_hancur.append(m)
                continue

            kena_monitor = m.gerak(dt)
            if kena_monitor == True:
                musuh_tembus.append(m)

        for m in musuh_tembus:
            self.hp -= m.rusak
            self.getar.mulai(GETAR_SEDANG, 0.3)
            self.atur_tampilan("salah", 0.5)
            if m == self.musuh_aktif:
                self.musuh_aktif = None

        musuh_baru = []

        for m in self.daftar_musuh:
            if m in musuh_tembus:
                continue
            if m in musuh_hancur:
                continue

            musuh_baru.append(m)

        self.daftar_musuh = musuh_baru

        if self.hp <= 0:
            self.hp = 0
            self.kalah = True
            if self.skor > self.skor_tertinggi:
                self.skor_tertinggi = self.skor
            self.getar.kekuatan = 0
            self.getar.sisa_waktu = 0

    def gambar_semua(self):
        layar = self.layar_dalam

        if self.status_layar == "benar":
            layar.blit(self.bg["benar"], (0, 0))
        elif self.status_layar == "salah":
            layar.blit(self.bg["salah"], (0, 0))
        else:
            layar.blit(self.bg["iddle"], (0, 0))

        if self.kalah:
            self.gambar_kalah(layar)
        else:
            self.gambar_main(layar)

        ox, oy = self.getar.ambil_posisi()
        layar_besar = pygame.transform.scale(layar, (SCREEN_W, SCREEN_H))
        self.layar_luar.fill(BLACK)
        self.layar_luar.blit(layar_besar, (ox, oy))

    def gambar_main(self, layar):
        if self.waktu_garis > 0 and self.target_garis != None:
            pygame.draw.line(layar, NEON_GREEN, (MONITOR_X, COLLISION_Y - 2), self.target_garis, 1)

        for p in self.daftar_partikel:
            p.gambar(layar)

        for m in self.daftar_musuh:
            m.gambar(layar)

        status_hacker = "iddle"
        if self.status_layar == "salah":
            status_hacker = "salah"
        elif self.musuh_aktif != None or self.status_layar in ("typing", "benar"):
            status_hacker = "typing"

        layar.blit(self.hacker[status_hacker], (HACKER_X, HACKER_Y))
        self.gambar_info(layar)

    def gambar_info(self, layar):
        teks_hi = self.font_info.render("HIGH SCORE: " + str(self.skor_tertinggi), False, NEON_RED)
        teks_sc = self.font_info.render("SCORE: " + str(self.skor), False, NEON_RED)
        layar.blit(teks_hi, (3, 2))
        layar.blit(teks_sc, (3, 2 + teks_hi.get_height() + 1))

        lebar_bar, tinggi_bar = 64, 5
        pos_x = BACKROUND_W - lebar_bar - 3
        pos_y = 3

        rasio = self.hp / 100.0
        isi_bar = max(0, int(lebar_bar * rasio))

        warna_bar = HP_GREEN
        if rasio <= 0.25:
            warna_bar = HP_RED
        elif rasio <= 0.5:
            warna_bar = HP_ORANGE

        pygame.draw.rect(layar, DARK_GRAY, (pos_x, pos_y, lebar_bar, tinggi_bar))
        if isi_bar > 0:
            pygame.draw.rect(layar, warna_bar, (pos_x, pos_y, isi_bar, tinggi_bar))
        pygame.draw.rect(layar, WHITE, (pos_x, pos_y, lebar_bar, tinggi_bar), 1)

        teks_hp = self.font_info.render("HP " + str(self.hp), False, WHITE)
        layar.blit(teks_hp, (pos_x, pos_y + tinggi_bar + 1))

    def gambar_kalah(self, layar):
        hitam_transparan = pygame.Surface((BACKROUND_W, BACKROUND_H), pygame.SRCALPHA)
        hitam_transparan.fill((0, 0, 0, 190))
        layar.blit(hitam_transparan, (0, 0))

        tengah_x = BACKROUND_W // 2

        teks_skor = self.font_skor.render("SCORE   " + str(self.skor), False, WHITE)
        teks_best = self.font_skor.render("BEST    " + str(self.skor_tertinggi), False, YELLOW)

        layar.blit(teks_skor, (tengah_x - teks_skor.get_width() // 2, 65))
        layar.blit(teks_best, (tengah_x - teks_best.get_width() // 2, 80))

        pygame.draw.line(layar, DARK_GRAY, (tengah_x - 40, 96), (tengah_x + 40, 96), 1)

        teks_coba = self.font_skor.render("[ TRY AGAIN ]", False, NEON_GREEN)
        pos_x = tengah_x - teks_coba.get_width() // 2
        pos_y = 105
        layar.blit(teks_coba, (pos_x, pos_y))

        self.kotak_coba = pygame.Rect(pos_x, pos_y, teks_coba.get_width(), teks_coba.get_height())

    def saat_klik(self, posisi_mouse):
        if self.kalah == True and self.kotak_coba != None:
            mx = posisi_mouse[0] // 2
            my = posisi_mouse[1] // 2.25

            if self.kotak_coba.collidepoint((mx, my)):
                self.mulai_ulang()


def main():
    pygame.init()
    pygame.display.set_caption("Binary Bastion")
    layar_luar = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    layar_dalam = pygame.Surface((BACKROUND_W, BACKROUND_H))
    jam = pygame.time.Clock()
    game_kita = GameMain(layar_luar, layar_dalam)
    sedang_jalan = True

    while sedang_jalan:
        dt = jam.tick(FPS) / 1000.0
        if dt > 0.05:
            dt = 0.05

        for acara in pygame.event.get():
            if acara.type == pygame.QUIT:
                sedang_jalan = False

            elif acara.type == pygame.KEYDOWN:
                if acara.key == pygame.K_ESCAPE:
                    sedang_jalan = False

                elif game_kita.kalah == False:
                    huruf = acara.unicode
                    if huruf and (huruf.isalpha() or huruf == "_"):
                        game_kita.tekan_tombol(huruf)

            elif acara.type == pygame.MOUSEBUTTONDOWN and acara.button == 1:
                game_kita.saat_klik(acara.pos)

        game_kita.jalan_game(dt)
        game_kita.gambar_semua()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

main()