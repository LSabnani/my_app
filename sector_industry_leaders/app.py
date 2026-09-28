import os
import io
import streamlit as st
import pandas as pd

from data_manager import get_all_sectors, get_industries, fetch_top_stocks
from scraper import generate_pdf_report

st.set_page_config(
    page_title="Sector Industry Leaders Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look and feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .sector-badge {
        background-color: #3B82F6;
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .success-box {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "current_sector_idx" not in st.session_state:
    st.session_state.current_sector_idx = 0

if "sector_data" not in st.session_state:
    st.session_state.sector_data = []  # Stores dicts for current sector

if "all_approved_data" not in st.session_state:
    st.session_state.all_approved_data = []  # Accumulates across all approved sectors

if "sector_approved" not in st.session_state:
    st.session_state.sector_approved = False

if "pdf_generated_path" not in st.session_state:
    st.session_state.pdf_generated_path = None

sectors = get_all_sectors()
current_sector = sectors[st.session_state.current_sector_idx] if st.session_state.current_sector_idx < len(sectors) else None

# Header Section
st.markdown('<div class="main-header">📈 Sector Industry Leaders Agent (v2)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Finviz constituent research, sector review, PDF reporting, & cache management app</div>', unsafe_allow_html=True)

# Sidebar Control
with st.sidebar:
    st.header("⚙️ Agent Controls")
    st.markdown("---")
    st.subheader("Progress Tracker")
    for idx, s in enumerate(sectors):
        if idx < st.session_state.current_sector_idx:
            st.markdown(f"✅ **{s}** (Completed)")
        elif idx == st.session_state.current_sector_idx:
            st.markdown(f"🔄 **{s}** (Active)")
        else:
            st.markdown(f"⏳ {s}")

    st.markdown("---")
    top_n_selection = st.slider("Top Stocks per Industry", min_value=5, max_value=10, value=10)

    # Combined Export Section in Sidebar if approved data exists
    if st.session_state.all_approved_data:
        st.markdown("---")
        st.subheader("📊 Master Combined Export")
        combined_df = pd.DataFrame(st.session_state.all_approved_data)
        
        # CSV Export
        csv_bytes = combined_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Combined CSV",
            data=csv_bytes,
            file_name="All_Sectors_Industry_Leaders.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    if st.button("🗑️ Reset / Clear Cache & Start Over", type="secondary", use_container_width=True):
        st.session_state.current_sector_idx = 0
        st.session_state.sector_data = []
        st.session_state.all_approved_data = []
        st.session_state.sector_approved = False
        st.session_state.pdf_generated_path = None
        st.rerun()

# Main Workspace
if current_sector:
    st.markdown(f"### Current Active Sector: **{current_sector}**")
    
    col_run, col_status = st.columns([1, 2])
    
    with col_run:
        if st.button(f"🚀 Research Sector: {current_sector}", type="primary", use_container_width=True):
            st.session_state.sector_data = []
            st.session_state.sector_approved = False
            st.session_state.pdf_generated_path = None
            
            industries = get_industries(current_sector)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ind in enumerate(industries):
                status_text.text(f"Fetching constituents for: {ind}...")
                symbols = fetch_top_stocks(current_sector, ind, top_n=top_n_selection)
                st.session_state.sector_data.append({
                    "Sector": current_sector,
                    "Industry": ind,
                    "Stock Symbols": ", ".join(symbols)
                })
                progress_bar.progress((i + 1) / len(industries))
                
            status_text.text("Sector extraction complete!")
            st.rerun()

    # Display Extracted Sector Data
    if st.session_state.sector_data:
        df = pd.DataFrame(st.session_state.sector_data)
        
        st.markdown("#### 📋 Captured Constituents Table (Review & Edit)")
        
        # Interactive Data Editor allowing user adjustments before approval
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Sector": st.column_config.TextColumn(disabled=True),
                "Industry": st.column_config.TextColumn("Industry Name", help="Name of industry"),
                "Stock Symbols": st.column_config.TextColumn("Top Stock Symbols", help="Comma-separated stock symbols")
            }
        )

        col_approve, col_pdf, col_next = st.columns(3)

        with col_approve:
            if st.button("✅ Approve Sector Data", type="primary", use_container_width=True):
                st.session_state.sector_approved = True
                
                # Append to master combined dataset
                approved_records = edited_df.to_dict(orient="records")
                st.session_state.all_approved_data.extend(approved_records)
                
                # Create output reports directory
                os.makedirs("output_reports", exist_ok=True)
                pdf_filename = f"output_reports/{current_sector.replace(' ', '_')}_Leaders.pdf"
                
                generate_pdf_report(current_sector, edited_df, pdf_filename)
                st.session_state.pdf_generated_path = pdf_filename
                st.success(f"Sector data approved & PDF generated at `{pdf_filename}`!")

        with col_pdf:
            if st.session_state.pdf_generated_path and os.path.exists(st.session_state.pdf_generated_path):
                with open(st.session_state.pdf_generated_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Sector PDF Report",
                        data=f,
                        file_name=os.path.basename(st.session_state.pdf_generated_path),
                        mime="application/pdf",
                        use_container_width=True
                    )

        with col_next:
            if st.session_state.sector_approved:
                if st.button("➡️ Clear Cache & Proceed to Next Sector", type="primary", use_container_width=True):
                    # Clear session sector cache
                    st.session_state.sector_data = []
                    st.session_state.sector_approved = False
                    st.session_state.pdf_generated_path = None
                    st.session_state.current_sector_idx += 1
                    st.rerun()

else:
    st.balloons()
    st.success("🎉 All sectors have been successfully researched, approved, and exported!")
    
    if st.session_state.all_approved_data:
        st.markdown("### 📊 Download Master Combined Data")
        master_df = pd.DataFrame(st.session_state.all_approved_data)
        st.dataframe(master_df, use_container_width=True)
        
        csv_bytes = master_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Master Combined CSV (All Sectors)",
            data=csv_bytes,
            file_name="All_Sectors_Master_Leaders.csv",
            mime="text/csv",
            type="primary"
        )
        
    if st.button("🔄 Restart Agent Process"):
        st.session_state.current_sector_idx = 0
        st.session_state.sector_data = []
        st.session_state.all_approved_data = []
        st.session_state.sector_approved = False
        st.session_state.pdf_generated_path = None
        st.rerun()
