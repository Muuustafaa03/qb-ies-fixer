import streamlit as st
import pandas as pd
import io
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="IES Enterprise Data Auditor", page_icon="🏦", layout="wide")

def smart_split_address(address):
    address = str(address).strip()
    if len(address) <= 41 or address.lower() == 'nan' or address == '':
        return address, ""
    split_index = address.rfind(' ', 0, 41)
    if split_index == -1: split_index = 41
    return address[:split_index].strip(), address[split_index:].strip()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None

# --- UI ---
st.title("🏦 QuickBooks IES Enterprise Data Auditor")
st.markdown("### The ultimate pre-migration tool for high-volume customer data.")

uploaded_file = st.file_uploader("Upload Complex Enterprise Export", type=['csv', 'xlsx'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    all_cols = df.columns.tolist()

    # --- SIDEBAR MAPPING ---
    st.sidebar.header("Data Mapping")
    def detect(keys): return next((c for c in all_cols if any(k in c.lower() for k in keys)), all_cols[0])
    
    t_name = st.sidebar.selectbox("Display Name (Unique)", all_cols, index=all_cols.index(detect(['name', 'customer'])))
    t_comp = st.sidebar.selectbox("Legal Company Name", all_cols, index=all_cols.index(detect(['company', 'legal'])))
    t_addr = st.sidebar.selectbox("Street Address", all_cols, index=all_cols.index(detect(['addr', 'street'])))
    t_zip = st.sidebar.selectbox("Zip/Postal", all_cols, index=all_cols.index(detect(['zip', 'postal'])))
    t_email = st.sidebar.selectbox("Email Address", all_cols, index=all_cols.index(detect(['email', 'mail'])))

    if st.button("🚀 Execute Enterprise Audit & Fix"):
        log = []
        fixes_count = 0
        
        # 1. Name & Company Scrubbing
        original_names = df[t_name].copy()
        df[t_name] = df[t_name].astype(str).str.replace(':', '-').str.replace('"', '')
        if not df[t_name].equals(original_names):
            log.append("🧹 **Name Scrubbing:** Fixed colons/quotes in Display Names.")
            fixes_count += 1

        if t_comp:
            df[t_comp] = df[t_comp].astype(str).apply(lambda x: x[:50] if len(x) > 50 else x)
            log.append("📏 **Company Limit:** Enforced 50-char limit on Legal Entities.")
            fixes_count += 1

        # 2. Smart Address Split
        l2_col = "Address Line 2 (Fixed)"
        new_l1, new_l2 = [], []
        for _, row in df.iterrows():
            l1, l2 = smart_split_address(row[t_addr])
            new_l1.append(l1); new_l2.append(l2)
        
        df[t_addr] = new_l1
        if l2_col not in df.columns:
            df.insert(df.columns.get_loc(t_addr) + 1, l2_col, new_l2)
        else: df[l2_col] = new_l2
        if any(new_l2): log.append("🔄 **Address Split:** Multi-line addresses preserved via overflow.")
        fixes_count += 1

        # 3. Zip Padding
        df[t_zip] = df[t_zip].astype(str).str.split('.').str[0].str.zfill(5)
        df[t_zip] = df[t_zip].replace('00nan', '')
        log.append("🔢 **Zip Formatting:** Corrected leading zeros.")

        # 4. Email Audit
        if t_email:
            invalid = df[df[t_email].apply(lambda x: not is_valid_email(x) and str(x) != 'nan')]
            if not invalid.empty:
                log.append(f"📧 **Email Audit:** Flagged {len(invalid)} malformed records for review.")

        # 5. Duplicate Detection
        dupes = df[df.duplicated(subset=[t_name], keep=False)]
        if not dupes.empty:
            log.append(f"🚨 **DUPLICATE ALERT:** Found {len(dupes)} identical names. These will block your import.")

        # --- RESULTS ---
        st.divider()
        st.header("📊 Audit Results")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Fixes Applied", fixes_count)
            st.write("### 📜 Change Log")
            for entry in log: st.markdown(entry)
        with c2:
            st.write("### ⬇️ Download QB-Ready Data")
            output = io.StringIO()
            df.to_csv(output, index=False)
            st.download_button("Download IES_MIGRATION_READY.csv", output.getvalue(), "IES_READY.csv", "text/csv")
        
        st.write("### 🔍 Live Preview of Cleaned Data")
        st.dataframe(df)

else:
    st.info("Upload the 'Complex Enterprise' CSV to see the tool handle 10+ columns simultaneously.")