from bs4 import BeautifulSoup
import requests


def ekstrasi_data():
    """
    Tanggal: 17 Januari 2022
    Waktu: 07:25:56 WIB
    Magnitudo: 5.4
    Kedalaman: 10 km
    Lokasi: 7.60 LS - 105.90 BT
    Pusat gempa: Pusat gempa berada di laut 84 km BaratDaya Bayah
    Dirasakan: Dirasakan (Skala MMI): II-III Cikembar, II-III Cireunghas, Kab. Sukabumi, II-III Pelabuhanratu, II-III Sumur, II-III Bogor, III Bayah, III Pandeglang, III Cikeusik, III Panimbang, II-III Jakarta Barat, II-III Jakarta Selatan, II-III Tambun
    :return:
    """

    try:
        content = requests.get('https://www.bmkg.go.id/')
    except Exception:
        return None

    soup = BeautifulSoup(content.text, 'html.parser')
    result = soup.find('span', {'class':'waktu'})
    result = result.text.split(', ')
    tanggal = result[0]
    waktu = result[1]

    result = soup.find('div', {'class':'col-md-6 col-xs-6 gempabumi-detail no-padding'})
    result = result.findChildren('li')

    i = 0
    magnitude = None
    kedalaman = None
    lu = None
    bt = None
    lokasi = None
    dirasakan = None

    for res in result:
        if i == 1:
            magnitude = res.text
        elif i == 2:
            kedalaman = res.text
        elif i == 3:
            koordinat = res.text.split(' - ')
            lu = koordinat[0]
            bt = koordinat[1]
        elif i == 4:
            lokasi = res.text
        elif i == 5:
            dirasakan = res.text

        i += 1

    if content.status_code == 200:
        hasil = dict()
        hasil["tanggal"] = tanggal
        hasil["waktu"] = waktu
        hasil["magnitude"] = magnitude
        hasil["kedalaman"] = kedalaman
        hasil["koordinat"] = {'lu': lu, 'bt': bt}
        hasil["lokasi"] = lokasi
        hasil["dirasakan"] = dirasakan

        return hasil
    else:
        return None


def tampilkan_data(result):
    if result is None:
        print('Data tidak ditemukan')
        return

    print("gempa terakhir berdasarkan BMKG")
    print(f"Tanggal {result['tanggal']}")
    print(f"Waktu {result['waktu']}")
    print(f"Magnitude {result['magnitude']}")
    print(f"Kedalaman {result['kedalaman']}")
    print(f"Koordinat: LU={result['koordinat']['lu']}, BT={result['koordinat']['bt']}")
    print(f"Lokasi {result['lokasi']}")
    print(f"Dirasakan {result['dirasakan']}")


if __name__ == "__main__":
    result = ekstrasi_data()
    tampilkan_data (result)