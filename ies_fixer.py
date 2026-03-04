import streamlit as st
import pandas as pd
import io
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="IES Migration Auditor Pro", page_icon="🏦", layout="wide")

# --- REFERENCE DATA ---
STATE_MAP = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
    'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
    'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# --- LOGIC ---
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

# --- UI: README / LANDING PAGE ---
st.title("🏦 QuickBooks IES Enterprise Data Auditor")
st.markdown("""
**A specialized utility for high-volume Intuit Enterprise Suite migrations.**

### 🛠️ What it solves:
- **Smart-Split Addresses:** Automatically handles the 41-character IES limit without losing data.
- **Entity Scrubbing:** Fixes forbidden characters (colons, quotes) that crash imports.
- **Audit Logging:** Identifies duplicate names and malformed emails before you hit 'Import'.
- **Zip-Code Restoration:** Restores leading zeros for Northeast/International postal codes.
""")

with st.expander("📖 View Instructions"):
    st.markdown("""
    1. **Export** your customer list from your current CRM as a CSV or Excel file.
    2. **Upload** the file below.
    3. **Map your columns** using the sidebar on the left.
    4. **Review the Audit Log** for warnings.
    5. **Download** the "IES-Ready" file. 
    6. **Import** into QuickBooks. Map "Address Line 1" and "Address Line 2" to the original column and the new `Address Line 2 (Fixed)` column.
    """)

# --- FILE UPLOAD & PREVIEW ---
uploaded_file = st.file_uploader("Upload CRM Export", type=['csv', 'xlsx'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    all_cols = df.columns.tolist()
    
    st.success("File Uploaded Successfully!")
    st.write("### 📄 Raw File Preview")
    st.dataframe(df.head(5)) # Bringing back visibility

    # --- SIDEBAR ---
    st.sidebar.header("Field Mapping")
    def detect(keys): return next((c for c in all_cols if any(k in c.lower() for k in keys)), None)
    
    t_name = st.sidebar.selectbox("Display Name (Unique ID)", all_cols, index=all_cols.index(detect(['name', 'customer'])) if detect(['name', 'customer']) else 0)
    t_comp = st.sidebar.selectbox("Legal Company Name", all_cols, index=all_cols.index(detect(['company', 'legal'])) if detect(['company', 'legal']) else 0)
    t_addr = st.sidebar.selectbox("Street Address", all_cols, index=all_cols.index(detect(['addr', 'street'])) if detect(['addr', 'street']) else 0)
    t_state = st.sidebar.selectbox("State/Province", all_cols, index=all_cols.index(detect(['state', 'prov'])) if detect(['state', 'prov']) else 0)
    t_zip = st.sidebar.selectbox("Zip/Postal", all_cols, index=all_cols.index(detect(['zip', 'postal'])) if detect(['zip', 'postal']) else 0)
    t_email = st.sidebar.selectbox("Email Address", all_cols, index=all_cols.index(detect(['email', 'mail'])) if detect(['email', 'mail']) else 0)
    t_tax = st.sidebar.selectbox("Taxable Status (Optional)", ["None"] + all_cols)

    if st.button("🚀 Execute Enterprise Audit"):
        log = []
        fixes = 0
        
        # PROCESSING
        df[t_name] = df[t_name].astype(str).str.replace(':', '-').str.replace('"', '')
        if t_comp:
            df[t_comp] = df[t_comp].astype(str).apply(lambda x: x[:50] if len(x) > 50 else x)
        if t_state:
            df[t_state] = df[t_state].astype(str).apply(lambda x: STATE_MAP.get(x.title(), x.upper()[:2]))
        
        l2_col = "Address Line 2 (Fixed)"
        new_l1, new_l2 = [], []
        for _, row in df.iterrows():
            l1, l2 = smart_split_address(row[t_addr])
            new_l1.append(l1); new_l2.append(l2)
        df[t_addr] = new_l1
        if l2_col not in df.columns:
            df.insert(df.columns.get_loc(t_addr) + 1, l2_col, new_l2)
        else: df[l2_col] = new_l2

        df[t_zip] = df[t_zip].astype(str).str.split('.').str[0].str.zfill(5)
        
        if t_tax != "None":
            df[t_tax] = df[t_tax].astype(str).apply(lambda x: "Yes" if any(k in x.lower() for k in ['true', '1', 'yes', 'taxable']) else "No")

        # LOGGING
        dupes = df[df.duplicated(subset=[t_name], keep=False)]
        if not dupes.empty:
            log.append(f"🚨 **CRITICAL:** {len(dupes)} duplicate names found.")
        if t_email:
            invalid = df[df[t_email].apply(lambda x: not is_valid_email(x) and str(x) != 'nan')]
            if not invalid.empty:
                log.append(f"📧 **Email Audit:** {len(invalid)} malformed emails flagged.")

        # --- RESULTS ---
        st.divider()
        st.header("📊 Audit Results")
        c1, c2 = st.columns([1, 2])
        with c1:
            for entry in log: st.markdown(entry)
            if not log: st.success("No critical errors found!")
        with c2:
            output = io.StringIO()
            df.to_csv(output, index=False)
            st.download_button("Download IES_READY.csv", output.getvalue(), "IES_READY.csv", "text/csv")
        
        st.write("### 🔍 Processed Data Preview")
        st.dataframe(df)

st.sidebar.markdown("---")
st.sidebar.info("💼 DM for custom IES integration support.")