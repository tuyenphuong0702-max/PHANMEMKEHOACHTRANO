import streamlit as st
import pandas as pd
import calendar
from datetime import date
from io import BytesIO
 
# =====================================================
# 1. CẤU HÌNH ỨNG DỤNG
# =====================================================
st.set_page_config(
   page_title="Lập kế hoạch trả nợ",
   page_icon="🏦",
   layout="wide"
)
 
st.title("🏦 BẢNG KẾ HOẠCH TRẢ NỢ VAY")
st.write(
   "Tính tiền gốc, tiền lãi theo dư nợ thực tế, "
   "lãi suất ưu đãi và lãi suất thông thường."
)
 
st.divider()
 
 
# =====================================================
# 2. HÀM XỬ LÝ NGÀY THÁNG
# =====================================================
def cong_thang(ngay, so_thang):
   """
   Cộng số tháng vào một ngày.
   Nếu tháng đích không có ngày tương ứng,
   sử dụng ngày cuối tháng.
   """
   tong_thang = ngay.month - 1 + so_thang
 
   nam_moi = ngay.year + tong_thang // 12
   thang_moi = tong_thang % 12 + 1
 
   ngay_toi_da = calendar.monthrange(
       nam_moi, thang_moi
   )[1]
 
   ngay_moi = min(ngay.day, ngay_toi_da)
 
   return date(nam_moi, thang_moi, ngay_moi)
 
 
def ngay_thu_no_dau_tien(ngay_giai_ngan, ngay_thu_no):
   """
   Tìm ngày thu nợ đầu tiên.
 
   - Nếu ngày thu nợ lớn hơn ngày giải ngân:
     thu nợ lần đầu trong cùng tháng.
   - Nếu ngày thu nợ nhỏ hơn hoặc bằng ngày giải ngân:
     thu nợ lần đầu vào tháng kế tiếp.
   """
   nam = ngay_giai_ngan.year
   thang = ngay_giai_ngan.month
 
   ngay_trong_thang = min(
       ngay_thu_no,
       calendar.monthrange(nam, thang)[1]
   )
 
   ngay_du_kien = date(nam, thang, ngay_trong_thang)
 
   if ngay_du_kien > ngay_giai_ngan:
       return ngay_du_kien
 
   return cong_thang(ngay_du_kien, 1)
 
 
def tinh_lai_theo_giai_doan(
   ngay_bat_dau,
   ngay_ket_thuc,
   du_no,
   lai_suat_uu_dai,
   lai_suat_thong_thuong,
   ngay_ket_thuc_uu_dai
):
   """
   Tính lãi theo số ngày thực tế trên dư nợ đầu kỳ.
 
   Quy ước:
   - Lãi suất năm chia 365 ngày.
   - Tính lãi từ ngày bắt đầu đến ngày kết thúc,
     không tính trùng ngày kết thúc.
   - Ưu đãi áp dụng trước ngày kết thúc ưu đãi.
   - Lãi suất thông thường áp dụng từ ngày kết thúc
     ưu đãi trở đi.
   """
   if ngay_ket_thuc <= ngay_bat_dau:
       return 0.0, 0, 0
 
   so_ngay_uu_dai = 0
   so_ngay_thong_thuong = 0
 
   if ngay_bat_dau < ngay_ket_thuc_uu_dai:
       moc_chuyen_lai = min(
           ngay_ket_thuc,
           ngay_ket_thuc_uu_dai
       )
 
       so_ngay_uu_dai = max(
           0,
           (moc_chuyen_lai - ngay_bat_dau).days
       )
 
   if ngay_ket_thuc > ngay_ket_thuc_uu_dai:
       moc_bat_dau_thong_thuong = max(
           ngay_bat_dau,
           ngay_ket_thuc_uu_dai
       )
 
       so_ngay_thong_thuong = max(
           0,
           (
               ngay_ket_thuc
               - moc_bat_dau_thong_thuong
           ).days
       )
 
   tien_lai_uu_dai = (
       du_no
       * lai_suat_uu_dai / 100
       * so_ngay_uu_dai / 365
   )
 
   tien_lai_thong_thuong = (
       du_no
       * lai_suat_thong_thuong / 100
       * so_ngay_thong_thuong / 365
   )
 
   tong_lai = tien_lai_uu_dai + tien_lai_thong_thuong
 
   return (
       tong_lai,
       so_ngay_uu_dai,
       so_ngay_thong_thuong
   )
 
 
# =====================================================
# 3. NHẬP THÔNG TIN KHOẢN VAY
# =====================================================
st.subheader("1. Thông tin khoản vay")
 
col1, col2, col3 = st.columns(3)
 
with col1:
   so_tien_vay = st.number_input(
       "Số tiền vay (VNĐ)",
       min_value=1_000_000,
       value=800_000_000,
       step=10_000_000,
       format="%d"
   )
 
   thoi_han_vay = st.number_input(
       "Thời hạn vay (tháng)",
       min_value=1,
       max_value=600,
       value=60,
       step=1
   )
 
with col2:
   lai_suat_uu_dai = st.number_input(
       "Lãi suất ưu đãi (%/năm)",
       min_value=0.0,
       max_value=100.0,
       value=7.0,
       step=0.1,
       format="%.2f"
   )
 
   thoi_gian_uu_dai = st.number_input(
       "Thời gian ưu đãi (tháng)",
       min_value=0,
       max_value=int(thoi_han_vay),
       value=min(12, int(thoi_han_vay)),
       step=1
   )
 
with col3:
   lai_suat_thong_thuong = st.number_input(
       "Lãi suất thông thường (%/năm)",
       min_value=0.0,
       max_value=100.0,
       value=11.0,
       step=0.1,
       format="%.2f"
   )
 
   ngay_giai_ngan = st.date_input(
       "Ngày giải ngân",
       value=date.today(),
       format="DD/MM/YYYY"
   )
 
ngay_thu_no = st.number_input(
   "Ngày thu nợ hàng tháng (1–31)",
   min_value=1,
   max_value=31,
   value=25,
   step=1
)
 
st.caption(
   "Ngày thu nợ được hiểu là ngày trong tháng. "
   "Nếu tháng đó không có ngày tương ứng, "
   "hệ thống tự động lấy ngày cuối tháng."
)
 
st.info(
   "Quy tắc: Gốc trả đều theo số tiền vay ban đầu. "
   "Lãi tính theo dư nợ đầu kỳ thực tế và số ngày "
   "thực tế/365. Kỳ đầu có thể ngắn hơn một tháng."
)
 
# =====================================================
# 4. NÚT LẬP KẾ HOẠCH TRẢ NỢ
# =====================================================
if st.button(
   "📊 LẬP BẢNG KẾ HOẠCH TRẢ NỢ",
   type="primary",
   use_container_width=True
):
 
   # Ngày hết ưu đãi tính từ ngày giải ngân
   ngay_het_uu_dai = cong_thang(
       ngay_giai_ngan,
       int(thoi_gian_uu_dai)
   )
 
   # Xác định ngày trả nợ đầu tiên
   ngay_thu_no_dau = ngay_thu_no_dau_tien(
       ngay_giai_ngan,
       int(ngay_thu_no)
   )
 
   # Tiền gốc trả đều; kỳ cuối điều chỉnh phần dư do làm tròn
   tien_goc_co_so = (
       float(so_tien_vay) / int(thoi_han_vay)
   )
 
   du_no_dau_ky = float(so_tien_vay)
   ngay_dau_ky = ngay_giai_ngan
 
   danh_sach = []
 
   # =================================================
   # 5. TÍNH TỪNG KỲ TRẢ NỢ
   # =================================================
   for ky in range(1, int(thoi_han_vay) + 1):
 
       # Ngày đến hạn của kỳ
       ngay_den_han = cong_thang(
           ngay_thu_no_dau,
           ky - 1
       )
 
       # Số ngày của kỳ trả nợ
       so_ngay = (
           ngay_den_han - ngay_dau_ky
       ).days
 
       # Tiền gốc kỳ này
       if ky < int(thoi_han_vay):
           tien_goc = min(
               tien_goc_co_so,
               du_no_dau_ky
           )
       else:
           # Kỳ cuối trả hết dư nợ còn lại
           tien_goc = du_no_dau_ky
 
       # Tiền lãi theo dư nợ đầu kỳ thực tế
       (
           tien_lai,
           so_ngay_uu_dai,
           so_ngay_thong_thuong
       ) = tinh_lai_theo_giai_doan(
           ngay_bat_dau=ngay_dau_ky,
           ngay_ket_thuc=ngay_den_han,
           du_no=du_no_dau_ky,
           lai_suat_uu_dai=float(lai_suat_uu_dai),
           lai_suat_thong_thuong=float(
               lai_suat_thong_thuong
           ),
           ngay_ket_thuc_uu_dai=ngay_het_uu_dai
       )
 
       # Tổng tiền phải thanh toán
       tong_thanh_toan = tien_goc + tien_lai
 
       # Dư nợ sau khi trả gốc
       du_no_cuoi_ky = max(
           0.0,
           du_no_dau_ky - tien_goc
       )
 
       danh_sach.append({
           "Kỳ": ky,
           "Ngày trả nợ": ngay_den_han,
           "Ngày đầu kỳ": ngay_dau_ky,
           "Số ngày tính lãi": so_ngay,
           "Dư nợ đầu kỳ (VNĐ)": round(
               du_no_dau_ky, 2
           ),
           "Lãi suất ưu đãi (ngày)": so_ngay_uu_dai,
           "Lãi suất thông thường (ngày)": (
               so_ngay_thong_thuong
           ),
           "Tiền gốc (VNĐ)": round(tien_goc, 2),
           "Tiền lãi (VNĐ)": round(tien_lai, 2),
           "Tổng phải trả (VNĐ)": round(
               tong_thanh_toan, 2
           ),
           "Dư nợ cuối kỳ (VNĐ)": round(
               du_no_cuoi_ky, 2
           )
       })
 
       # Chuyển sang kỳ tiếp theo
       du_no_dau_ky = du_no_cuoi_ky
       ngay_dau_ky = ngay_den_han
 
   # =================================================
   # 6. TẠO DATAFRAME
   # =================================================
   df = pd.DataFrame(danh_sach)
 
   # =================================================
   # 7. HIỂN THỊ TỔNG QUAN KHOẢN VAY
   # =================================================
   tong_goc = df["Tiền gốc (VNĐ)"].sum()
   tong_lai = df["Tiền lãi (VNĐ)"].sum()
   tong_thanh_toan = df["Tổng phải trả (VNĐ)"].sum()
 
   st.divider()
   st.subheader("2. Tổng quan khoản vay")
 
   c1, c2, c3, c4 = st.columns(4)
 
   c1.metric(
       "Số tiền vay",
       f"{so_tien_vay:,.0f} VNĐ"
   )
 
   c2.metric(
       "Tổng tiền gốc",
       f"{tong_goc:,.0f} VNĐ"
   )
 
   c3.metric(
       "Tổng tiền lãi",
       f"{tong_lai:,.0f} VNĐ"
   )
 
   c4.metric(
       "Tổng phải trả",
       f"{tong_thanh_toan:,.0f} VNĐ"
   )
 
   st.write(
       f"**Ngày giải ngân:** "
       f"{ngay_giai_ngan.strftime('%d/%m/%Y')}"
   )
 
   st.write(
       f"**Ngày kết thúc ưu đãi:** "
       f"{ngay_het_uu_dai.strftime('%d/%m/%Y')}"
   )
 
   st.write(
       f"**Ngày thu nợ kỳ đầu:** "
       f"{ngay_thu_no_dau.strftime('%d/%m/%Y')}"
   )
 
   # =================================================
   # 8. HIỂN THỊ BẢNG KẾ HOẠCH TRẢ NỢ
   # =================================================
   st.divider()
   st.subheader("3. Chi tiết kế hoạch trả nợ")
 
   # Bảng hiển thị ngày theo định dạng Việt Nam
   df_hien_thi = df.copy()
 
   df_hien_thi["Ngày trả nợ"] = (
       df_hien_thi["Ngày trả nợ"].apply(
           lambda x: x.strftime("%d/%m/%Y")
       )
   )
 
   df_hien_thi["Ngày đầu kỳ"] = (
       df_hien_thi["Ngày đầu kỳ"].apply(
           lambda x: x.strftime("%d/%m/%Y")
       )
   )
 
   st.dataframe(
       df_hien_thi,
       use_container_width=True,
       hide_index=True
   )
 
   # =================================================
   # 9. BIỂU ĐỒ DƯ NỢ
   # =================================================
   st.subheader("4. Biểu đồ dư nợ")
 
   df_bieu_do = df[
       ["Kỳ", "Dư nợ cuối kỳ (VNĐ)"]
   ].set_index("Kỳ")
 
   st.line_chart(df_bieu_do)
 
   # =================================================
   # 10. XUẤT FILE EXCEL
   # =================================================
   st.divider()
   st.subheader("5. Xuất kế hoạch trả nợ")
 
   excel_buffer = BytesIO()
 
   with pd.ExcelWriter(
       excel_buffer,
       engine="openpyxl"
   ) as writer:
 
       df.to_excel(
           writer,
           index=False,
           sheet_name="Ke_hoach_tra_no"
       )
 
       # Thêm trang tổng quan
       df_tong_quan = pd.DataFrame({
           "Thông tin": [
               "Số tiền vay (VNĐ)",
               "Thời hạn vay (tháng)",
               "Lãi suất ưu đãi (%/năm)",
               "Thời gian ưu đãi (tháng)",
               "Lãi suất thông thường (%/năm)",
               "Ngày giải ngân",
               "Ngày thu nợ hàng tháng",
               "Ngày hết ưu đãi",
               "Tổng tiền gốc (VNĐ)",
               "Tổng tiền lãi (VNĐ)",
               "Tổng phải trả (VNĐ)"
           ],
           "Giá trị": [
               so_tien_vay,
               int(thoi_han_vay),
               lai_suat_uu_dai,
               int(thoi_gian_uu_dai),
               lai_suat_thong_thuong,
               ngay_giai_ngan.strftime("%d/%m/%Y"),
               int(ngay_thu_no),
               ngay_het_uu_dai.strftime("%d/%m/%Y"),
               tong_goc,
               tong_lai,
               tong_thanh_toan
           ]
       })
 
       df_tong_quan.to_excel(
           writer,
           index=False,
           sheet_name="Tong_quan"
       )
 
   st.download_button(
       label="📥 TẢI BẢNG KẾ HOẠCH TRẢ NỢ EXCEL",
       data=excel_buffer.getvalue(),
       file_name="ke_hoach_tra_no.xlsx",
       mime=(
           "application/vnd.openxmlformats-officedocument."
           "spreadsheetml.sheet"
       ),
       use_container_width=True
   )
 
st.caption(
   "Lưu ý: Đây là bảng tính theo quy ước đã thiết lập. "
   "Lịch tính lãi, ngày nghỉ, quy tắc làm tròn và "
   "cách chuyển lãi suất thực tế có thể khác theo "
   "hợp đồng tín dụng của ngân hàng."
)
