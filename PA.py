import json
import os
from prettytable import PrettyTable
import pwinput

FILE_AKUN = "akun.json"
FILE_BEASISWA = "beasiswa.json"
FILE_TRANSAKSI = "transaksi.json"

def simpan(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def baca(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return default
    else:
        simpan(path, default)
        return default

akun_data = baca(FILE_AKUN, [])
daftar_beasiswa = baca(FILE_BEASISWA, [])
daftar_transaksi = baca(FILE_TRANSAKSI, [])

def cari_akun_username(usern):
    for a in akun_data:
        if a.get('username') == usern:
            return a
    return None

def cari_akun_nim(nim):
    for a in akun_data:
        if a.get('nim') == nim:
            return a
    return None

def tabel_beasiswa(list_bea):
    t = PrettyTable()
    t.field_names = ["ID","Nama","Program","Potongan%"]
    for b in list_bea:
        t.add_row([b.get('id'), b.get('nama'), b.get('pb',''), b.get('potongan',0)])
    print(t)

def tabel_akun(list_ak):
    t = PrettyTable()
    t.field_names = ["User","NIM","Role","Beasiswa","UKT","Saldo"]
    for u in list_ak:
        user = u.get('username','')
        nim = u.get('nim','')
        role = u.get('role','')
        bea = u.get('beasiswa', [])
        nama_bea = []
        try:
            iter(bea)
            if type(bea).__name__ in ('str','bytes'):
                raise Exception()
            for it in bea:
                try:
                    nama_bea.append(it.get('nama'))
                except Exception:
                    nama_bea.append(str(it))
        except Exception:
            nama_bea = [str(bea)]
        bea_str = ", ".join([x for x in nama_bea if x]) if nama_bea else "-"
        ukt = u.get('ukt')
        try:
            ukt_str = f"Rp {int(ukt):,}" if ukt is not None else "-"
        except Exception:
            ukt_str = str(ukt)
        saldo = u.get('saldo',0)
        try:
            saldo_str = f"Rp {int(saldo):,}"
        except Exception:
            saldo_str = str(saldo)
        t.add_row([user,nim,role,bea_str,ukt_str,saldo_str])
    print(t)

def tabel_transaksi(list_tr):
    t = PrettyTable()
    t.field_names = ["ID","User","Beasiswa","UKT Awal","Diskon%","Bayar"]
    for tr in list_tr:
        t.add_row([tr.get('id'), tr.get('username'), tr.get('nama_beasiswa'), f"Rp {tr.get('ukt_awal'):,}", tr.get('potongan'), f"Rp {tr.get('bayar'):,}"])
    print(t)

def bisa_di_iter(obj):
    try:
        iter(obj)
        if type(obj).__name__ in ('str','bytes'):
            return False
        return True
    except Exception:
        return False

def daftar_baru():
    try:
        nama = input("Buat username: ").strip()
        if not nama:
            print("Username kosong")
            return
        if cari_akun_username(nama):
            print("Username sudah ada")
            return
        pwd = pwinput.pwinput("Password: ", mask='*')
        nim = input("NIM: ")
        try:
            saldo = int(input("Saldo awal (angka): "))
        except Exception:
            print("Saldo harus angka")
            return
        akun_data.append({'username': nama, 'password': pwd, 'nim': nim, 'role':'mahasiswa', 'beasiswa': [], 'saldo': saldo})
        simpan(FILE_AKUN, akun_data)
        print("Akun berhasil dibuat")
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        daftar_baru()
    except EOFError:
        print("\nJangan CTRL+Z")
        daftar_baru()

def masuk():
    try:
        nama = input("Username: ").strip()
        pwd = pwinput.pwinput("Password: ", mask='*')
        a = cari_akun_username(nama)
        if a and a.get('password') == pwd:
            print(f"Halo {nama}, role: {a.get('role')}")
            return a
        print("Username atau password salah")
        return None
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        masuk()
    except EOFError:
        print("\nJangan CTRL+Z")
        masuk()

def admin_lihat_mahasiswa():
    tabel_akun(akun_data)

def admin_tambah_beasiswa_ke_mahasiswa():
    nim = input("Masukkan NIM mahasiswa: ").strip()
    if not nim:
        print("NIM kosong")
        return
    siswa = cari_akun_nim(nim)
    if not siswa:
        print("NIM tidak ditemukan")
        return
    tabel_beasiswa(daftar_beasiswa)
    sid = input("Pilih ID beasiswa: ").strip()
    try:
        sid = int(sid)
    except Exception:
        print("ID harus angka")
        return
    pilih = None
    for b in daftar_beasiswa:
        if b.get('id') == sid:
            pilih = b
            break
    if not pilih:
        print("Beasiswa tidak ada")
        return
    try:
        current = siswa.get('beasiswa')
        if not bisa_di_iter(current):
            if current:
                siswa['beasiswa'] = [current]
            else:
                siswa['beasiswa'] = []
    except Exception:
        siswa['beasiswa'] = []
    ids = []
    try:
        for it in siswa['beasiswa']:
            try:
                ids.append(it.get('id'))
            except Exception:
                pass
    except Exception:
        pass
    if pilih.get('id') in ids:
        print("Beasiswa sudah terdaftar di akun")
        return
    siswa['beasiswa'].append(pilih)
    simpan(FILE_AKUN, akun_data)
    print("Beasiswa ditambahkan ke akun mahasiswa")

def admin_set_ukt():
    try:
        nim = input("Masukkan NIM mahasiswa: ").strip()
        if not nim:
            print("NIM kosong")
            return
        siswa = cari_akun_nim(nim)
        if not siswa:
            print("NIM tidak ditemukan")
            return
        try:
            val = int(input("Masukkan nilai UKT (angka): "))
            if val > 25000000:
                print("UKT Maksimal Rp 25.000.000")
                return
        except Exception:
            print("UKT harus angka")
            return
        siswa['ukt'] = val
        simpan(FILE_AKUN, akun_data)
        print("UKT disimpan untuk mahasiswa")
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        admin_set_ukt()
    except EOFError:
        print("\nJangan CTRL+Z")
        admin_set_ukt()

def admin_hapus_beasiswa():
    try:
        nim = input("Masukkan NIM mahasiswa: ").strip()
        if not nim:
            print("NIM kosong")
            return
        siswa = cari_akun_nim(nim)
        if not siswa:
            print("NIM tidak ditemukan")
            return
        be = siswa.get('beasiswa')
        try:
            if bisa_di_iter(be):
                daftar = list(be)
            else:
                daftar = [be]
        except Exception:
            daftar = [be]
        tabel_beasiswa(daftar)
        try:
            sid = int(input("ID beasiswa yang mau dihapus: ").strip())
        except Exception:
            print("ID harus angka")
            return
        hapus = False
        try:
            for i, it in enumerate(siswa.get('beasiswa', [])):
                try:
                    if it.get('id') == sid:
                        siswa['beasiswa'].pop(i)
                        hapus = True
                        break
                except Exception:
                    try:
                        if int(it) == sid:
                            siswa['beasiswa'].pop(i)
                            hapus = True
                            break
                    except Exception:
                        pass
        except Exception:
            pass
        if hapus:
            simpan(FILE_AKUN, akun_data)
            print("Beasiswa dihapus dari akun")
        else:
            print("Beasiswa tidak ditemukan pada akun tersebut")
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        admin_hapus_beasiswa()
    except EOFError:
        print("\nJangan CTRL+Z")
        admin_hapus_beasiswa()

def admin_edit_beasiswa():
    try:
        nim = input("Masukkan NIM mahasiswa: ").strip()
        if not nim:
            print("NIM kosong")
            return
        siswa = cari_akun_nim(nim)
        if not siswa:
            print("NIM tidak ditemukan")
            return
        be = siswa.get('beasiswa')
        try:
            daftar = list(be) if bisa_di_iter(be) else [be]
        except Exception:
            daftar = [be]
        if not daftar:
            print("Belum ada beasiswa")
            return
        tabel_beasiswa(daftar)
        try:
            sid = int(input("ID beasiswa yang mau diedit: ").strip())
        except Exception:
            print("ID harus angka")
            return
        found = None
        try:
            for idx, it in enumerate(siswa.get('beasiswa', [])):
                try:
                    if it.get('id') == sid:
                        found = (idx, it)
                        break
                except Exception:
                    try:
                        if int(it) == sid:
                            found = (idx, it)
                            break
                    except Exception:
                        pass
        except Exception:
            pass
        if not found:
            print("Beasiswa tidak ditemukan")
            return
        idx, cur = found
        try:
            nama_lama = cur.get('nama','')
            pb_lama = cur.get('pb','')
            pot_lama = cur.get('potongan',0)
        except Exception:
            nama_lama = str(cur)
            pb_lama = ''
            pot_lama = 0
        nama_baru = input(f"Nama baru (enter biar tetap '{nama_lama}'): ").strip()
        pb_baru = input(f"Program baru (enter biar tetap '{pb_lama}'): ").strip()
        pot_baru = input(f"Potongan baru (enter biar tetap '{pot_lama}'): ").strip()
        if pot_baru != '':
            try:
                pot_baru = int(pot_baru)
            except Exception:
                print("Potongan harus angka")
                return
        else:
            pot_baru = pot_lama
        try:
            if nama_baru:
                siswa['beasiswa'][idx]['nama'] = nama_baru
            if pb_baru:
                siswa['beasiswa'][idx]['pb'] = pb_baru
            siswa['beasiswa'][idx]['potongan'] = pot_baru
        except Exception:
            siswa['beasiswa'][idx] = {'id': sid, 'nama': nama_baru or nama_lama, 'pb': pb_baru or pb_lama, 'potongan': pot_baru}
        simpan(FILE_AKUN, akun_data)
        print("Beasiswa diperbarui")
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        admin_edit_beasiswa()
    except EOFError:
        print("\nJangan CTRL+Z")
        admin_edit_beasiswa()

def bayar_ukt(user):
    try:
        bea = user.get('beasiswa')
        ukt = user.get('ukt')
        if ukt is None:
            print("UKT belum diset, minta admin untuk mengisi.")
            return

        if not bea:
            pot = 0
            bayar = ukt * (100 - pot) // 100
            print("\n=== Pembayaran UKT Tanpa Beasiswa ===")
            print(f"UKT awal   : Rp {ukt:,}")
            print(f"Potongan   : {pot}%")
            print(f"Jumlah bayar: Rp {bayar:,}")

            if user.get('saldo', 0) < bayar:
                print("Saldo kamu tidak cukup.")
                return

            user['saldo'] = user.get('saldo', 0) - bayar
            inv = len(daftar_transaksi) + 1
            daftar_transaksi.append({'id': inv, 'username': user.get('username'), 'nama_beasiswa': 'Tidak Ada', 'ukt_awal': ukt, 'potongan': pot, 'bayar': bayar
            })
            simpan(FILE_AKUN, akun_data)
            simpan(FILE_TRANSAKSI, daftar_transaksi)
            print("Pembayaran UKT tanpa beasiswa berhasil.")
            return
        try:
            sid = int(input("Pilih ID beasiswa yang mau dipakai: ").strip())
        except Exception:
            print("ID harus angka")
            return
        pilih = None
        try:
            for b in user.get('beasiswa', []):
                try:
                    if b.get('id') == sid:
                        pilih = b
                        break
                except Exception:
                    pass
        except Exception:
            pass
        if not pilih:
            print("Beasiswa gak ketemu di akunmu")
            return
        pot = pilih.get('potongan',0)
        bayar = ukt * (100 - pot) // 100
        print(f"UKT awal: Rp {ukt:,}")
        print(f"Potongan: {pot}%")
        print(f"Jumlah bayar: Rp {bayar:,}")
        if user.get('saldo',0) < bayar:
            print("Saldo kamu gak cukup")
            return
        user['saldo'] = user.get('saldo',0) - bayar
        inv = len(daftar_transaksi) + 1
        daftar_transaksi.append({'id': inv, 'username': user.get('username'), 'nama_beasiswa': pilih.get('nama'), 'ukt_awal': ukt, 'potongan': pot, 'bayar': bayar})
        simpan(FILE_AKUN, akun_data)
        simpan(FILE_TRANSAKSI, daftar_transaksi)
        print("Pembayaran berhasil")
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        bayar_ukt(user)
    except EOFError:
        print("\nJangan CTRL+Z")
        bayar_ukt(user)

def menu_admin(user):
    try:
        while True:
            print('\n=== Menu Admin ===')
            print('1. Lihat daftar mahasiswa')
            print('2. Tambah beasiswa ke mahasiswa')
            print('3. Edit beasiswa mahasiswa')
            print('4. Hapus beasiswa dari mahasiswa')
            print('5. Set UKT mahasiswa')
            print('0. Logout')
            pilih = input('Pilih: ').strip()
            if pilih == '1':
                tabel_akun(akun_data)
            elif pilih == '2':
                tabel_akun(akun_data)
                admin_tambah_beasiswa_ke_mahasiswa()
            elif pilih == '3':
                tabel_akun(akun_data)
                admin_edit_beasiswa()
            elif pilih == '4':
                tabel_akun(akun_data)
                admin_hapus_beasiswa()
            elif pilih == '5':
                tabel_akun(akun_data)
                admin_set_ukt()
            elif pilih == '0':
                break
            else:
                print('Pilihan nggak valid, coba lagi')
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        menu_admin(user)
    except EOFError:
        print("\nJangan CTRL+Z")
        menu_admin(user)

def menu_mahasiswa(user):
    try:
        while True:
            print('\n=== Menu Mahasiswa ===')
            print('1. Lihat beasiswa')
            print('2. Bayar UKT')
            print('3. Lihat saldo')
            print('4. Lihat invoice saya')
            print('0. Logout')
            pilih = input('Pilih: ').strip()
            if pilih == '1':
                tabel_beasiswa(daftar_beasiswa)
            elif pilih == '2':
                bayar_ukt(user)
            elif pilih == '3':
                print(f"Saldo: Rp {user.get('saldo',0):,}")
            elif pilih == '4':
                my = [x for x in daftar_transaksi if x.get('username') == user.get('username')]
                if not my:
                    print('Belum ada invoice')
                else:
                    tabel_transaksi(my)
            elif pilih == '0':
                break
            else:
                print('Pilihan nggak valid')
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        menu_mahasiswa(user)
    except EOFError:
        print("\nJangan CTRL+Z")
        menu_mahasiswa(user)

def main():
    try:
        while True:
            print('\nPLIISSSS BAAANNGGG ACC BAAAANNNGGGGGG')
            print('\n=== Aplikasi Beasiswa (Gaya Pemula) ===')
            print('1. Login')
            print('2. Daftar')
            print('3. Keluar')
            pilih = input('Pilih: ').strip()
            if pilih == '1':
                user = masuk()
                if user:
                    if user.get('role') == 'admin':
                        menu_admin(user)
                    else:
                        menu_mahasiswa(user)
            elif pilih == '2':
                daftar_baru()
            elif pilih == '3':
                print('Sampai jumpa')
                break
            else:
                print('Pilihan nggak valid')
    except KeyboardInterrupt:
        print("\nJangan CTRL+C")
        main()
    except EOFError:
        print("\nJangan CTRL+Z")
        main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nKeluar')
