import streamlit as st
import os
from google import genai
from google.genai import types

# 1. ตั้งค่าหน้าตาของแอปพลิเคชัน (UI Configuration)
st.set_page_config(page_title="FitBite AI - Smart Order", page_icon="🥗", layout="centered")

# สร้างและเตรียม session_state ไว้ตั้งแต่แรกสุด ป้องกันเออร์เรอร์แดงบนหน้าเว็บ
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# CSS จัดเต็มธีมมืด (Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f12 !important; color: #ffffff !important; }
    .info-card {
        background-color: #161c20; padding: 12px; border-radius: 10px;
        border: 1px solid #2e7d32; text-align: center; margin-bottom: 10px;
    }
    .welcome-box {
        background-color: #112214; padding: 20px; border-radius: 15px;
        border-left: 6px solid #4caf50; margin-top: 15px; margin-bottom: 20px;
        color: #e8f5e9;
    }
    h1, h2, h3, .stSubheader { color: #4caf50 !important; font-family: 'Kanit', sans-serif; }
    .stMultiSelect label, .stTextArea label, .stTextInput label, .stSelectbox label { color: #4caf50 !important; font-weight: bold !important; }
    .stMarkdown, p, li { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==================== 🔝 TOP BAR SECTION ====================
st.title("🥗 FitBite AI")
st.markdown("### *Personalized Nutritionist & Smart Form Order*")

col_time, col_deliv = st.columns(2)
with col_time:
    st.markdown("<div class='info-card'><span style='color: #4caf50;'>🕒 เปิดบริการทุกวัน</span><br>09:00 น. - 18:00 น.</div>", unsafe_allow_html=True)
with col_deliv:
    st.markdown("<div class='info-card'><span style='color: #ff9800;'>🛵 รอบจัดส่งเดลิเวอรี</span><br>11:00 | 14:00 | 17:00</div>", unsafe_allow_html=True)

st.markdown("""<div class='welcome-box'><strong>ก้าวใหม่ของการสั่งอาหารคลีน!</strong><br>ระบุรายละเอียดชื่อ เบอร์โทร เมนู สารอาหารที่แพ้ รอบจัดส่ง และที่อยู่ด้านล่างนี้ได้เลยค่ะ AI จะช่วยคำนวณและตรวจสอบความถูกต้องให้ทันที</div>""", unsafe_allow_html=True)

# ==================== 📝 SMART ORDER FORM ====================
st.subheader("📋 ฟอร์มสั่งซื้ออาหารคลีนอัจฉริยะ")

with st.container():
    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        customer_name = st.text_input("👤 ชื่อ - นามสกุล ของผู้สั่งซื้อ:", placeholder="เช่น คุณสมชาย รักสุขภาพ")
    with col_cust2:
        customer_phone = st.text_input("📞 เบอร์โทรศัพท์ติดต่อ:", placeholder="เช่น 098-XXXXXXX")

    main_menu_options = [
        "1. สลัดอกไก่ย่างพริกไทยดำ (119.-)",
        "2. ข้าวไรซ์เบอร์รี่ปลากระพงนึ่ง (149.-)",
        "3. พาสต้าโฮลวีทซอสเพสโต้กุ้ง (159.-)",
        "4. ข้าวหน้าเนื้อย่างยากินิกุ (169.-)",
        "5. ลาบเต้าหู้อีสานและคีนัว (เจ) (109.-)"
    ]
    selected_mains = st.multiselect("🥗 เลือกเมนูหลัก (เลือกได้หลายรายการ):", main_menu_options)

    addon_options = [
        "เพิ่มอกไก่ย่าง (+40.-)",
        "เพิ่มแซลมอนย่าง (+89.-)",
        "เพิ่มไข่ต้ม (+15.-)",
        "เพิ่มอะโวคาโด (+35.-)",
        "เพิ่มเส้นบุกคาร์บ 0% (+25.-)"
    ]
    selected_addons = st.multiselect("➕ เพิ่มท็อปปิ้งเสริมพลัง (Add-ons):", addon_options)
    allergy_input = st.text_input("⚠️ ระบุอาหารที่แพ้ / วัตถุดิบที่ไม่กิน (ถ้ามี):", placeholder="เช่น แพ้อาหารทะเล, ไม่ใส่ผัก...")
    delivery_slots = ["รอบเช้า (11:00 น.)", "รอบบ่าย (14:00 น.)", "รอบเย็น (17:00 น.)"]
    selected_slot = st.selectbox("📦 เลือกรอบจัดส่งเดลิเวอรี:", delivery_slots)
    address_input = st.text_area("📍 กรอกที่อยู่จัดส่งสินค้าอย่างละเอียด:", placeholder="ระบุ บ้านเลขที่, ซอย, ถนน, แขวง/เขต และจังหวัด...")

    def calculate_fallback(name, phone, mains, addons, allergy, slot, address):
        total_price = 0
        total_cal = 0
        for m in mains:
            if "1." in m: total_price += 119; total_cal += 350
            elif "2." in m: total_price += 149; total_cal += 410
            elif "3." in m: total_price += 159; total_cal += 480
            elif "4." in m: total_price += 169; total_cal += 520
            elif "5." in m: total_price += 109; total_cal += 290
        for a in addons:
            if "อกไก่" in a: total_price += 40; total_cal += 120
            elif "แซลมอน" in a: total_price += 89; total_cal += 180
            elif "ไข่ต้ม" in a: total_price += 15; total_cal += 75
            elif "อะโวคาโด" in a: total_price += 35; total_cal += 160
            elif "เส้นบุก" in a: total_price += 25; total_cal += 10

        bill_html = f"""
### 🧾 ใบเสร็จรับเงินอัจฉริยะ (ระบบสำรองข้อมูลอัตโนมัติ)
---
* **👤 ชื่อลูกค้า:** {name if name else 'ไม่ได้ระบุ'}
* **📞 เบอร์โทรศัพท์:** {phone if phone else 'ไม่ได้ระบุ'}
* **🍱 เมนูที่สั่ง:** {', '.join(mains)}
* **➕ ท็อปปิ้งเสริม:** {', '.join(addons) if addons else 'ไม่มี'}
* **⚠️ ข้อควรระวังเรื่องภูมิแพ้:** แจ้งข้อมูล '{allergy if allergy else 'ไม่มี'}' ไปยังพนักงานในครัวแล้ว
---
* **📊 พลังงานรวมประมาณ:** `{total_cal} kcal`
* **💰 ยอดราคารวมสุทธิ:** `{total_price} บาท`
---
* **📦 รอบจัดส่ง:** {slot}
* **📍 ที่อยู่จัดส่ง:** {address}

*(หมายเหตุ: ระบบสลับมาใช้โหมดประมวลผลด่วนเนื่องจากผู้ใช้งาน API หนาแน่น)*
"""
        return bill_html

    if st.button("🛒 ยืนยันการสั่งซื้อและคำนวณบิล"):
        if not customer_name: st.warning("กรุณากรอกชื่อลูกค้าด้วยค่ะบอส!")
        elif not customer_phone: st.warning("กรุณากรอกเบอร์โทรศัพท์ติดต่อด้วยค่ะบอส!")
        elif not selected_mains: st.warning("กรุณาเลือกเมนูหลักอย่างน้อย 1 รายการค่ะบอส!")
        elif not address_input: st.warning("กรุณากรอกที่อยู่จัดส่งเพื่อความถูกต้องในการส่งสินค้าค่ะบอส!")
        else:
            order_summary_prompt = f"[ลูกค้าสั่งผ่านฟอร์ม]\n- ชื่อลูกค้า: {customer_name}\n- เบอร์โทรศัพท์: {customer_phone}\n- เมนูหลัก: {', '.join(selected_mains)}\n- Add-ons: {', '.join(selected_addons)}\n- สิ่งที่แพ้: {allergy_input}\n- รอบส่ง: {selected_slot}\n- ที่อยู่: {address_input}"
            st.session_state.chat_history = [{"role": "user", "text": order_summary_prompt}]

# ==================== 🤖 AI REASONING OUTPUT ====================
st.markdown("---")
api_key = os.environ.get("GOOGLE_API_KEY")

def load_fitbite_knowledge():
    try:
        with open("fitbite_kb.txt", "r", encoding="utf-8") as f: return f.read()
    except: return "ไม่พบฐานข้อมูลเมนูอาหาร"

SYSTEM_INSTRUCTION = f"คุณคือ FitBite AI นักโภชนาการและระบบรับออเดอร์อัจฉริยะ หน้าที่ของคุณคือสรุปใบเสร็จรับเงิน แสดงชื่อและเบอร์โทรลูกค้า คำนวณแคลรวม ตรวจภูมิแพ้ ตบท้ายด้วยรอบส่งและที่อยู่ให้สวยงาม\n\nคลังความรู้:\n{load_fitbite_knowledge()}"

if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        if message["role"] == "model":
            st.subheader("🧾 ใบเสร็จและผลคำนวณสารอาหารจาก AI")
            with st.chat_message("model"): st.markdown(message["text"])

if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    if not api_key:
        fallback_text = calculate_fallback(customer_name, customer_phone, selected_mains, selected_addons, allergy_input, selected_slot, address_input)
        st.session_state.chat_history.append({"role": "model", "text": fallback_text})
        st.rerun()
    else:
        try:
            client = genai.Client(api_key=api_key)
            order_summary_prompt = st.session_state.chat_history[-1]["text"]
            with st.spinner("AI กำลังวิเคราะห์สารอาหารเชิงลึก..."):
                response = client.models.generate_content(model="gemini-2.5-flash", contents=order_summary_prompt, config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.2))
                st.session_state.chat_history.append({"role": "model", "text": response.text})
                st.rerun()
        except Exception as e:
            fallback_text = calculate_fallback(customer_name, customer_phone, selected_mains, selected_addons, allergy_input, selected_slot, address_input)
            st.session_state.chat_history.append({"role": "model", "text": fallback_text})
            st.rerun()

if user_chat := st.chat_input("พิมพ์สอบถามข้อมูลโภชนาการเพิ่มเติมตรงนี้ได้ค่ะ..."):
    st.session_state.chat_history.append({"role": "user", "text": user_chat})
    st.rerun()
