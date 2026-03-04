# 🏦 QuickBooks IES Enterprise Data Auditor
**A specialized utility for high-volume Intuit Enterprise Suite migrations.**

### 🚀 Live Tool: [https://qb-ies-fixer.streamlit.app/]

### 🛠️ What it solves:
- **Smart-Split Addresses:** Automatically handles the 41-character IES limit without losing data.
- **Entity Scrubbing:** Fixes forbidden characters (colons, quotes) that crash imports.
- **Audit Logging:** Identifies duplicate names and malformed emails before you hit 'Import'.
- **Zip-Code Restoration:** Restores leading zeros for Northeast/International postal codes.

### 💼 Professional Services
Looking for a full-scale historical data migration (Invoices, Bills, Journal Entries)? 
DM me for custom IES integration support.

## 📖 How to Use the Auditor
1. **Export** your customer list from your current CRM (Salesforce, HubSpot, etc.) as a CSV or Excel file.
2. **Upload** the file to the [IES Data Auditor](https://muuustafaa03-qb-ies-fixer.streamlit.app).
3. **Map your columns** using the sidebar on the left. The tool will try to guess them automatically, but you can double-check them.
4. **Review the Audit Log** for warnings about duplicate names or invalid emails.
5. **Download** the "IES-Ready" file. 
6. **Import** into QuickBooks Enterprise. When prompted for "Address Line 1" and "Address Line 2," map them to the original address column and the new `Address Line 2 (Fixed)` column created by the tool.
