import streamlit as st
import pandas as pd
import altair as charting

# --- KONFIGURASI HALAMAN  ---
st.set_page_config(
    page_title="Employee Satisfaction Analysis",
    page_icon="📊", # Menggunakan ikon grafik
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DATA LOADING ---
# Menggunakan st.cache_data untuk menghindari pemuatan ulang data pada setiap interaksi
@st.cache_data
def load_data():
    """Memuat data Employee Satisfaction dari URL publik (RAW GitHub)."""
    
    # URL data RAW dari repositori GitHub
    url = "https://raw.githubusercontent.com/Herdvair/Employee-Satisfaction/main/assignment_employee_survey.csv" 
    
    try:
        df = pd.read_csv(url) 
        # Membersihkan baris dengan nilai yang hilang untuk demo analisis awal
        df.dropna(inplace=True)
        return df
    
    except Exception as e:
        return pd.DataFrame() # Mengembalikan DataFrame kosong jika gagal

# Panggil fungsi load_data()
df = load_data()


# --- APP TITLE AND DESCRIPTION ---
st.title("📊 Analisis Kepuasan Karyawan")
st.markdown("""
Dashboard ini menyajikan *Exploratory Data Analysis (EDA)* berdasarkan hasil survei kepuasan kerja.

Dataset yang memuat informasi tentang karyawan di sebuah perusahaan(seperti usia, jenis kelamin, dan tingkat jabatan) serta berbagai *faktor kunci yang memengaruhi kepuasan*, meliputi:

* *Work-Life Balance*
* *Workload* (Beban Kerja)
* *Stress Level* (Tingkat Stres)
* *Work Environment* (Lingkungan Kerja)
* *Sleep Hours* (Jam Tidur)

Gunakan sidebar dan filter yang tersedia untuk eksplorasi lebih dalam.
""")

# --- TAMPILAN DATA AWAL ---
if not df.empty:
    
    SATISFACTION = 'job_satisfaction' 
    DEPARTMENT = 'dept'              
    
    
    required_cols = [SATISFACTION, DEPARTMENT]
    
    if not all(col in df.columns for col in required_cols):
        st.error(f"Kolom yang anda butuhkan tidak ada. Harap periksa kembali apakah kolom '{SATISFACTION}' atau '{DEPARTMENT}' benar-benar ada di dataset Anda.")
        st.subheader("Pratinjau Data (5 Baris Teratas)")
        st.dataframe(df.head())
        st.info(f"Total baris data yang berhasil dimuat: {len(df)}")
        st.stop()

    # --- 1. DASHBOARD JOB SATISFACTION RATE ---
    st.markdown("---")
    st.header("Employee Satisfaction Rate")
    
    # Hitung metrik
    avg_satisfaction = df[SATISFACTION].mean()
    total_karyawan = len(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Rata-rata Skor Kepuasan", 
            value=f"{avg_satisfaction:.2f}",
        )
    
    with col2:
        st.metric(label="Total Responden", value=total_karyawan)
        
    with col3:
        # Menghitung standar deviasi sebagai indikator variasi
        st.metric(label="Variasi Skor", value=f"{df[SATISFACTION].std():.2f}")


    # --- 2. DISTRIBUSI SKOR ---
    st.markdown("---")
    st.header("Distribusi Skor Kepuasan Karyawan")
    
    # Membuat histogram menggunakan Altair
    chart = charting.Chart(df).mark_bar().encode(
        x=charting.X(SATISFACTION, bin=True, title="Skor Kepuasan"),
        y=charting.Y('count()', title="Jumlah Karyawan"),
        tooltip=[SATISFACTION, 'count()']
    ).properties(
        title='Frekuensi Skor Kepuasan'
    ).interactive() # Memungkinkan zoom dan pan
    
    st.altair_chart(chart, use_container_width=True)
    
    st.info("""
    *Insight:* Berdasarkan proporsi skor kepuasan, sebagian besar karyawan (*41%) memberikan skor **4, yang menunjukkan bahwa mereka merasa puas dengan pekerjaannya. Skor ini menjadi yang paling dominan dibandingkan kategori lainnya. Tingkat ketidakpuasan (skor 1 dan 2) relatif rendah (23%* gabungan), mengindikasikan suasana kerja yang stabil.
    """)
    

    # --- 3. Analisis Antar variabel ---
    st.markdown("---")
    st.header("Analisis Hubungan Antar Variabel & Segmentasi")

    # --- Fungsi Visualisasi Altair ---
    def make_mean_chart(df, x_col, y_col, chart_type='bar', title=''):
        """Membuat chart Altair untuk rata-rata suatu faktor."""
        
        df_agg = df.groupby(x_col)[y_col].mean().reset_index()
        
        base = charting.Chart(df_agg).encode(
            x=charting.X(x_col, title=x_col.replace('_', ' ')),
            y=charting.Y(y_col, title=f"Rata-rata {y_col.replace('_', ' ')}")
        ).properties(title=title)
        
        if chart_type == 'scatter':
             return base.mark_circle(size=80, color='#9b59b6').encode(
                 tooltip=[x_col, charting.Tooltip(y_col, format='.2f')]
             ).interactive()
        elif chart_type == 'bar':
             return base.mark_bar(color='#2980b9').encode(
                 tooltip=[x_col, charting.Tooltip(y_col, format='.2f')]
             ).interactive()
        elif chart_type == 'line':
             return base.mark_line(color='#c0392b', point=True).encode(
                 tooltip=[x_col, charting.Tooltip(y_col, format='.2f')]
             ).interactive()
        return base

    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Work Life Balanced", "Workload", "Stress", "Job Level", "Departemen", "Hubungan Antar Variabel"
    ])
    
    with tab1: # Work-Life Balance
        st.subheader("Pengaruh Work-Life Balance (WLB) terhadap Kepuasan Kerja")
        st.altair_chart(
            make_mean_chart(df, 'wlb', SATISFACTION, 'scatter', 'Rata-rata Skor Kepuasan berdasarkan Work Life Balance'), 
            use_container_width=True
        )
        st.info("""
        *Insight:* Visualisasi menunjukkan adanya *korelasi positif* antara skor Work Life Balance (WLB) dan rata-rata Kepuasan Karyawan. Semakin tinggi skor WLB, semakin tinggi pula tingkat kepuasan. Karyawan dengan skor *WLB 5* memiliki rata-rata kepuasan tertinggi (*3.79), sedangkan skor **WLB 1* memiliki rata-rata terendah (*2.91*).
        """)

    with tab2: # Workload (Beban Kerja)
        st.subheader("Distribusi Beban Kerja (Workload) per Departemen")
        
        # Hitung rata-rata Workload per Departemen
        df_wl_dept = df.groupby(DEPARTMENT)['workload'].mean().reset_index()
        df_wl_dept.columns = [DEPARTMENT, 'Rata_Rata_Workload']
        
        chart_wl = charting.Chart(df_wl_dept).mark_bar(color='#f39c12').encode(
            x=charting.X(DEPARTMENT, title="Departemen"),
            y=charting.Y('Rata_Rata_Workload', title="Rata-rata Beban Kerja"),
            tooltip=[DEPARTMENT, charting.Tooltip('Rata_Rata_Workload', format='.2f')]
        ).properties(
            title='Distribusi Beban Kerja Rata-rata per Departemen'
        ).interactive()
        
        st.altair_chart(chart_wl, use_container_width=True)
        st.info("""
        *Insight:* Beban kerja antar departemen relatif merata (*2.81 hingga 3.12). **Departemen Marketing* memiliki rata-rata beban kerja tertinggi (*3.12*), mengindikasikan tanggung jawab yang besar. Pemantauan berkala diperlukan untuk menghindari kelelahan.
        """)
        
    with tab3: # Stress
        st.subheader("Pengaruh Stress terhadap Kepuasan Kerja")
        st.altair_chart(
            make_mean_chart(df, 'stress', SATISFACTION, 'line', 'Pengaruh Stress terhadap Kepuasan Kerja'), 
            use_container_width=True
        )
        st.info("""
        *Insight:* Terdapat *hubungan negatif yang jelas* antara tingkat stres dan rata-rata kepuasan kerja. Ketika tingkat stres rendah (skor 1), rata-rata kepuasan kerja tertinggi (*3.56), dan menurun secara konsisten hingga **2.56* pada stres skor 5. Hal ini menunjukkan pentingnya manajemen dan dukungan psikologis di tempat kerja.
        """)
        
    with tab4: # Job Level
        st.subheader("Pengaruh Job Level (Posisi Jabatan) terhadap Kepuasan Kerja")
        if 'job_level' in df.columns:
            st.altair_chart(
                make_mean_chart(df, 'job_level', SATISFACTION, 'bar', 'Pengaruh Job Level dengan Kepuasan Kerja'), 
                use_container_width=True
            )
            st.info("""
            *Insight:* Tingkat kepuasan kerja relatif stabil di seluruh jenjang jabatan (*3.31 hingga 3.41). Level **Mid* memiliki rata-rata tertinggi (*3.41), sementara level **Lead* memiliki rata-rata terendah (*3.31*). Perlu dilakukan evaluasi dukungan kerja untuk posisi Lead.
            """)
        else:
            st.warning("Kolom 'Job_Level' tidak ditemukan di dataset Anda. Analisis ini dilewati.")

    with tab5: # Segmentasi Departemen
        st.subheader("Segmentasi Karyawan berdasarkan Rata-rata Kepuasan Departemen")
        
        df_dept_sat = df.groupby(DEPARTMENT)[SATISFACTION].mean().reset_index()
        df_dept_sat.columns = [DEPARTMENT, 'Rata_Rata_Kepuasan']
        
        chart_dept = charting.Chart(df_dept_sat).mark_bar(color='#3498db').encode(
            x=charting.X('Rata_Rata_Kepuasan', title="Rata-rata Skor Kepuasan"),
            y=charting.Y(DEPARTMENT, title="Departemen"),
            tooltip=[DEPARTMENT, charting.Tooltip('Rata_Rata_Kepuasan', format='.2f')]
        ).properties(
            title='Segmentasi Karyawan berdasarkan Departemen'
        ).interactive()
        
        st.altair_chart(chart_dept, use_container_width=True)
        st.info("""
        *Insight:* *Sales (3.48)* dan *Operations (3.46)* memiliki rata-rata kepuasan tertinggi. *Departemen IT* memiliki rata-rata terendah (*3.29*). Perbedaan ini menunjukkan adanya variasi budaya kerja atau dukungan tim antar departemen.
        """)
            
    with tab6: # Korelasi Matriks
        st.subheader("Heatmap Korelasi Pearson")
        
        try:
            # Seleksi hanya kolom numerik dan hitung korelasi
            df_numeric = df.select_dtypes(include=['number'])
            corr_df = df_numeric.corr().stack().reset_index(name='Korelasi')
            corr_df.columns = ['Faktor_1', 'Faktor_2', 'Korelasi']
            
            # Membuat Heatmap interaktif menggunakan Altair
            heatmap = charting.Chart(corr_df).mark_rect().encode(
                x=charting.X('Faktor_1:N', title=None),
                y=charting.Y('Faktor_2:N', title=None),
                color=charting.Color('Korelasi:Q', scale=charting.Scale(range='diverging', domain=(-1, 1))),
                tooltip=['Faktor_1', 'Faktor_2', charting.Tooltip('Korelasi', format='.2f')]
            ).properties(
                title="Korelasi Matriks Semua Variabel Numerik"
            ).interactive()
            
            st.altair_chart(heatmap, use_container_width=True)
            
            st.info("""
            *Wawasan Utama dari Heatmap:*
            1. *Work-life balance* memiliki korelasi positif sedang (*0.3*) dengan Kepuasan.
            2. *Workload* memiliki korelasi negatif sedang (-0.3**) dengan Kepuasan.
            3. *Stress* memiliki korelasi negatif lemah (-0.2**) dengan Kepuasan.
            4. *Work environment* dan *Sleep hours* menunjukkan korelasi positif lemah (*0.2*).
            """)
            
        except Exception as e:
            st.error(f"Gagal memvisualisasikan Heatmap korelasi. Pastikan semua kolom faktor berupa tipe data numerik.")


# --- TAMPILAN DATA AWAL & FILTER SAMPING ---
st.sidebar.header("Pratinjau dan Filter")

if not df.empty:
    # Filter dan tampilan data di sidebar
    st.sidebar.subheader("Pratinjau Data Awal")
    st.sidebar.dataframe(df.head())
    st.sidebar.info(f"Total baris data yang dianalisis: {len(df)}")

    if DEPARTMENT in df.columns:
        st.sidebar.header("Filter Analisis")
        departments = df[DEPARTMENT].unique()
        selected_department = st.sidebar.selectbox("Pilih Departemen", departments)
        
        filtered_df = df[df[DEPARTMENT] == selected_department]
        st.subheader(f"Data Filter untuk Departemen: {selected_department}")
        st.dataframe(filtered_df.head(10)) 
    else:
         st.sidebar.info(f"Kolom '{DEPARTMENT}' tidak ditemukan. Harap sesuaikan nama kolom data Anda.")
else:
    st.warning("Tidak ada data yang tersedia untuk analisis karena proses pemuatan gagal. Mohon periksa URL atau delimiter Anda.")
