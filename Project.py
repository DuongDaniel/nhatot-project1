import streamlit as st
import pandas as pd
from PIL import Image
import os

# Cấu hình trang Streamlit
st.set_page_config(page_title="Nền tảng Nhà Tốt - Phân tích & Dự đoán", page_icon="🏡", layout="wide")

st.title("🏡 Đồ án Nhà Tốt: Dự đoán giá & Phát hiện bất thường")
st.markdown("**Thực hiện bởi:** Quang Dương & Khánh Thư")
st.markdown("---")

# Hàm load data an toàn (tìm cả ở thư mục hiện tại và thư mục 'reports')
@st.cache_data
def load_data(filename):
    if os.path.exists(filename):
         return pd.read_csv(filename)
    elif os.path.exists(os.path.join("reports", filename)):
         return pd.read_csv(os.path.join("reports", filename))
    return pd.DataFrame()

# Hàm hiển thị hình ảnh an toàn
def show_image(filename, caption=""):
    if os.path.exists(filename):
        image = Image.open(filename)
        st.image(image, caption=caption, use_container_width=True)
    elif os.path.exists(os.path.join("reports", filename)):
        image = Image.open(os.path.join("reports", filename))
        st.image(image, caption=caption, use_container_width=True)
    else:
        st.warning(f"Không tìm thấy file ảnh: {filename}")

# Chia giao diện thành 3 tab chính
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan & EDA", "🤖 Mô hình Dự đoán Giá", "🚨 Phát hiện Bất thường"])

# ----------------- TAB 1: EDA -----------------
with tab1:
    st.header("1. Phân tích Dữ liệu Khám phá (EDA)")
    st.write("Tập dữ liệu bao gồm thông tin bất động sản từ 3 quận: Bình Thạnh, Gò Vấp, và Phú Nhuận sau khi đã được làm sạch và chuẩn hóa.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Phân phối Target (Giá bán)")
        show_image("eda_target.png", "Phân phối giá bán bị lệch phải mạnh, cần dùng thang log10")
            
    with col2:
        st.subheader("Tỉ lệ dữ liệu thiếu (Missing values)")
        show_image("eda_missing.png", "Tỉ lệ missing ở các trường dữ liệu")
            
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Biến phân loại (Categorical Features)")
        show_image("eda_categorical.png")
            
    with col4:
        st.subheader("Ma trận tương quan")
        show_image("eda_corr.png", "Mối quan hệ giữa giá và các đặc trưng diện tích, số phòng")
            
    st.subheader("Phân tích Ngôn ngữ Tiếp thị (Wordcloud)")
    show_image("wordcloud_mo_ta.jpg", "Các từ khóa được người bán sử dụng nhiều nhất trong mô tả")

# ----------------- TAB 2: MÔ HÌNH DỰ ĐOÁN -----------------
with tab2:
    st.header("2. Đánh giá Mô hình Dự đoán Giá")
    
    st.subheader("So sánh hiệu năng các mô hình (Scikit-learn vs PySpark)")
    df_sklearn = load_data("results_sklearn.csv")
    df_spark = load_data("results_spark.csv")
    df_baseline = load_data("results_baseline.csv")
    
    if not df_sklearn.empty and not df_spark.empty:
        # Gộp và hiển thị bảng so sánh
        df_all = pd.concat([df_sklearn, df_spark, df_baseline]).sort_values(by="RMSE").reset_index(drop=True)
        st.dataframe(df_all, use_container_width=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        show_image("model_sklearn.png", "Biểu đồ đánh giá các model Scikit-learn")
    with col_m2:
        show_image("bang_so_sanh_model.png", "RMSE và R2 của top các mô hình")
        
    st.subheader("Độ quan trọng của đặc trưng (Feature Importance)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("**Scikit-learn (XGBoost)**")
        show_image("feature_importance_sklearn.png")
    with col_f2:
        st.markdown("**PySpark MLlib (Random Forest)**")
        show_image("feature_importance_spark.png")

    st.subheader("Kiểm tra mức độ bao phủ của khoảng giá")
    df_khoang_gia = load_data("kiem_tra_khoang_gia.csv")
    if not df_khoang_gia.empty:
        st.dataframe(df_khoang_gia, use_container_width=True)

# ----------------- TAB 3: PHÁT HIỆN BẤT THƯỜNG -----------------
with tab3:
    st.header("3. Phát hiện Giá Bất thường (Anomaly Detection)")
    
    st.subheader("Ưu nhược điểm các phương pháp tín hiệu")
    df_uu_nhuoc = load_data("bang_uu_nhuoc_anomaly.csv")
    if not df_uu_nhuoc.empty:
        st.dataframe(df_uu_nhuoc, use_container_width=True)
        
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("Tổng quan Composite Score")
        show_image("anomaly_overview.png", "Phân phối điểm tổng hợp từ 4 tín hiệu")
    with col_a2:
        st.subheader("Độ trùng lặp giữa các tín hiệu (Jaccard)")
        show_image("anomaly_jaccard.png", "Các tín hiệu hoạt động độc lập, giúp giảm cảnh báo giả")
            
    st.subheader("Danh sách Tin đăng Bất thường (Top 5% Composite Score)")
    st.write("Hệ thống đã khoanh vùng các tin đăng có nguy cơ bất thường cao (Ví dụ: Tòa nhà thương mại, văn phòng, khai khống diện tích).")
    df_anomaly = load_data("danh_sach_bat_thuong_top5pct.csv")
    if not df_anomaly.empty:
        # Lọc các cột quan trọng để dễ nhìn trên GUI
        cols_to_show = ['tieu_de', 'gia_ban_ty', 'dien_tich_m2', 'don_gia_trm2', 'quan', 'phuong', 's_ml', 's_resid', 's_pct']
        available_cols = [c for c in cols_to_show if c in df_anomaly.columns]
        st.dataframe(df_anomaly[available_cols].head(100), use_container_width=True)