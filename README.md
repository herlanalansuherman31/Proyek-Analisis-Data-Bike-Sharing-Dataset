# Dashboard Bike Sharing

Dashboard interaktif dibuat menggunakan Streamlit dan data `dashboard/main_data.csv`.

## Dashboard online

Buka dashboard di [herlanbikeanalysis.streamlit.app](https://herlanbikeanalysis.streamlit.app/).

## Instalasi

Jalankan perintah berikut dari folder utama proyek:

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan dashboard

```powershell
python -m streamlit run dashboard/dashboard.py
```

Setelah aplikasi berjalan, buka [http://localhost:8501](http://localhost:8501) di browser. URL ini hanya dapat diakses dari komputer yang menjalankan aplikasi.

Pastikan `dashboard/main_data.csv` tersedia di samping `dashboard.py`. Gunakan pemilih rentang tanggal di sidebar bersama filter musim, kondisi cuaca, dan tipe pengguna (terdaftar/kasual); semua filter diterapkan pada ringkasan dan grafik analisis. Beberapa grafik tetap berfokus pada periode tertentu (2011, 2012, atau Q3 2012), sehingga dapat menampilkan pesan tanpa data jika rentang tanggal yang dipilih tidak mencakup periode tersebut. Data harian dideduplikasi berdasarkan `instant_day` agar tidak terhitung berulang.

## Isi dashboard

- Ringkasan total dan rata-rata penyewaan, persentase pengguna terdaftar, serta hari tersibuk.
- Tren penyewaan harian sesuai filter tahun dan bulan.
- Pengaruh cuaca dan pola penyewaan per jam pada hari kerja dibanding hari libur.
- Volume penyewaan per musim di 2012 dan pengguna kasual/terdaftar per bulan di 2011.
- Korelasi suhu yang terasa dengan total penyewaan harian pada Q3 2012.
