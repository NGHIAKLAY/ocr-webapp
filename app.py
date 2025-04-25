import streamlit as st, requests, base64, os, json

st.set_page_config(page_title="OCR trích xuất văn bản", layout="centered")

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("logo.png", width=80)
with col_title:
    st.markdown("<h1 style='color:#ff4b4b;margin-top:18px'>🧠 OCR với Google Vision</h1>", unsafe_allow_html=True)

# ---------- Hàm OCR  ----------
@st.cache_data(show_spinner=False, ttl=3600)
def ocr_with_google_vision(image_bytes: bytes, api_key: str) -> str:
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    payload = {
        "requests": [{
            "image": {"content": base64.b64encode(image_bytes).decode()},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {"languageHints": ["vi", "en"]}
        }]
    }
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GCV lỗi {r.status_code}: {r.text[:200]}")
    data = r.json()
    return data["responses"][0].get("fullTextAnnotation", {}).get("text", "")

# ---------- Giao diện nhập liệu ----------
st.subheader("Thông tin người gửi")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("👤 Tên nhân viên", placeholder="VD: Nguyễn Văn A")
with col2:
    doc_type = st.selectbox("📄 Loại tài liệu", ["Hoá đơn", "Đơn hàng", "Phiếu giao", "Khác"])

uploaded = st.file_uploader("📷 Chọn ảnh (.jpg/.png, ≤4 MB)", type=["jpg", "jpeg", "png"])
api_key = st.text_input("🔑 Google Vision API key", type="password", value=st.secrets.get("GCV_API_KEY", ""))

# ---------- Xử lý ----------
if uploaded:
    st.image(uploaded, use_container_width=True)
    if not api_key:
        st.warning("Nhập API key trước khi OCR.")
    elif uploaded.size > 4*1024*1024:
        st.error("Ảnh vượt 4 MB – Vision API không nhận.")
    else:
        with st.spinner("Đang nhận diện văn bản từ ảnh..."):
            try:
                text = ocr_with_google_vision(uploaded.read(), api_key)
                if text:
                    st.success("🎉 Thành công!")
                    st.text_area("📋 Kết quả nhận dạng:", text, height=300)
                    st.download_button("⬇️ Tải TXT", text, file_name="ocr.txt")
                else:
                    st.info("Không tìm thấy văn bản trong ảnh.")
            except Exception as e:
                st.error(str(e))
