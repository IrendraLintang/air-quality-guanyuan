import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Mengatur tema halaman
st.set_page_config(
    page_title="Dashboard Kualitas Udara",
    page_icon="🌍",
    layout="centered",  # Atur tata letak menjadi terpusat
)

# Fungsi untuk memuat data
@st.cache
def load_data():

    current_directory = os.path.dirname(__file__)
    csv_path = os.path.join(current_directory, 'PRSA_Data_Guanyuan_20130301-20170228.csv')
    
    data = pd.read_csv(csv_path)
    return data

# Fungsi untuk membersihkan dan mempersiapkan data
def preprocess_data(data):
    # Mengisi nilai yang hilang dengan median
    polutan = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    kolom_cuaca = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    
    for kolom in polutan + kolom_cuaca:
        data[kolom].fillna(data[kolom].median(), inplace=True)

    # Membuat kolom datetime
    data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
    
    return data

# Fungsi untuk analisis dan visualisasi
def analyze_data(data):
    # Menghitung rata-rata bulanan dari PM2.5 dan suhu
    data_tren = data.groupby(['year', 'month']).agg({'PM2.5': 'mean', 'TEMP': 'mean'}).reset_index()
    data_tren['tanggal'] = pd.to_datetime(data_tren[['year', 'month']].assign(day=1))

    return data_tren

# Fungsi untuk plotting tren PM2.5
def plot_pm25(data_tren):
    plt.figure(figsize=(8, 4))  # Ukuran chart yang lebih kecil
    plt.plot(data_tren['tanggal'], data_tren['PM2.5'], color='blue', label='PM2.5')
    plt.plot(data_tren['tanggal'], data_tren['TEMP'], color='red', label='Suhu')
    plt.title('Tren PM2.5 dan Suhu dari Waktu ke Waktu')
    plt.xlabel('Tanggal')
    plt.ylabel('Konsentrasi PM2.5 / Suhu (°C)')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# Fungsi untuk menampilkan heatmap korelasi
def plot_correlation_heatmap(data):
    kolom_korelasi_cuaca = ['PM2.5', 'PM10', 'TEMP', 'RAIN', 'WSPM']
    matriks_korelasi_cuaca = data[kolom_korelasi_cuaca].corr()

    plt.figure(figsize=(8, 6))  # Ukuran chart yang lebih kecil
    sns.heatmap(matriks_korelasi_cuaca, annot=True, cmap='coolwarm', center=0)
    plt.title('Korelasi antara PM2.5, PM10 dengan Kondisi Cuaca')
    st.pyplot(plt)

# Fungsi untuk analisis kategori PM2.5
def categorize_pm25(value):
    if value <= 12:
        return 'Good'
    elif value <= 35.4:
        return 'Moderate'
    elif value <= 55.4:
        return 'Unhealthy for Sensitive Groups'
    elif value <= 150.4:
        return 'Unhealthy'
    elif value <= 250.4:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

# Fungsi untuk menghitung distribusi kategori PM2.5
def categorize_pm25_distribution(data):
    data['PM2.5_Category'] = data['PM2.5'].apply(categorize_pm25)
    kategori_count = data['PM2.5_Category'].value_counts()
    return kategori_count

# Setup Dashboard
st.title("Dashboard Kualitas Udara dan Kondisi Cuaca di Guanyuan")

# Memuat dan mempersiapkan data
data = load_data()
data = preprocess_data(data)

# Analisis dan visualisasi
data_tren = analyze_data(data)

# Membuat tab untuk menampilkan berbagai chart
tab1, tab2, tab3, tab4 = st.tabs(["Tren PM2.5", "Heatmap Korelasi", "Distribusi Kualitas Udara", "Data yang Diproses"])

with tab1:
    st.subheader("Tren PM2.5 dan Suhu dari Waktu ke Waktu")
    plot_pm25(data_tren)
    st.write("""
        Grafik ini menunjukkan tren bulanan konsentrasi PM2.5 dan suhu dari tahun ke tahun. 
        Kenaikan atau penurunan PM2.5 dapat mengindikasikan perubahan dalam kualitas udara, 
        sementara suhu dapat mempengaruhi pola cuaca dan kualitas udara.
    """)

with tab2:
    st.subheader("Heatmap Korelasi antara PM2.5, PM10, dan Kondisi Cuaca")
    plot_correlation_heatmap(data)
    st.write("""
        Heatmap ini menunjukkan korelasi antara berbagai polutan udara dan kondisi cuaca. 
        Nilai yang lebih tinggi menunjukkan hubungan yang lebih kuat antara variabel-variabel tersebut.
    """)

with tab3:
    st.subheader("Distribusi Kategori Kualitas Udara berdasarkan PM2.5")
    kategori_pm25 = categorize_pm25_distribution(data)

    plt.figure(figsize=(8, 4))  # Ukuran chart yang lebih kecil
    sns.barplot(x=kategori_pm25.index, y=kategori_pm25.values, palette='viridis')
    plt.title('Distribusi Kategori Kualitas Udara Berdasarkan PM2.5')
    plt.xlabel('Kategori Kualitas Udara')
    plt.ylabel('Jumlah Data')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    st.pyplot(plt)
    st.write("""
        Grafik ini menunjukkan distribusi jumlah data untuk masing-masing kategori kualitas udara 
        berdasarkan konsentrasi PM2.5. Kategori-kategori ini memberikan informasi penting tentang 
        seberapa baik atau buruk kualitas udara di daerah ini.
    """)

with tab4:
    st.subheader("Lima Baris Pertama Data yang Diproses:")
    st.write(data.head())