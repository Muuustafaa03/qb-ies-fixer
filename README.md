# 🏦 QuickBooks IES Enterprise Data Auditor
**A specialized utility for high-volume Intuit Enterprise Suite migrations.**

### 🚀 Live Tool: [https://muuustafaa03-qb-ies-fixer.streamlit.app/]

### 🛠️ What it solves:
- **Smart-Split Addresses:** Automatically handles the 41-character IES limit without losing data.
- **Entity Scrubbing:** Fixes forbidden characters (colons, quotes) that crash imports.
- **Audit Logging:** Identifies duplicate names and malformed emails before you hit 'Import'.
- **Zip-Code Restoration:** Restores leading zeros for Northeast/International postal codes.
- **State Normalization:** Converts full state names (e.g., "New York") to 2-letter codes (NY).

### 💼 Professional Services
Looking for a full-scale historical data migration (Invoices, Bills, Journal Entries)? 
DM me for custom IES integration support.

---

## 📖 How to Use the Auditor

1. **Export** your customer list from your current CRM (Salesforce, HubSpot, etc.) as a CSV or Excel file.
2. **Upload** the file to the [IES Data Auditor](https://muuustafaa03-qb-ies-fixer.streamlit.app).
3. **Map your columns** using the sidebar on the left.
    - **Pro Tip: Tax Status:** To standardize your tax data, select your tax column in the "Taxable Status" dropdown. The tool will convert values like "1", "True", or "Taxable" into a clean "Yes/No" for QuickBooks.
4. **Review the Audit Log** for warnings about duplicate names or invalid emails.
5. **Download** the "IES-Ready" file. 

### ⚠️ IMPORTANT: The "Zip Code Trap"
**Do not open the downloaded CSV in Excel before importing to QuickBooks.** Excel automatically removes "leading zeros" from zip codes (e.g., it changes `02108` back to `2108`). To keep your data clean, download the file from this tool and upload it **directly** into QuickBooks Enterprise.

6. **Import into QuickBooks:** When mapping fields, use the new `Address Line 2 (Fixed)` column created by the tool to ensure no address data is truncated.