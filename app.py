"""
Fact-Checking Web App

A Streamlit application that extracts claims from PDFs and verifies them
against live web data using AI.
"""

import streamlit as st
import os
from dotenv import load_dotenv

from src.pdf_extractor import extract_text_from_pdf
from src.claim_extractor import extract_claims
from src.verifier import verify_claims
from src.models import VerificationStatus

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Fact Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .status-verified {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .status-inaccurate {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .status-false {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .claim-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stat-box {
        text-align: center;
        color: white;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
</style>
""", unsafe_allow_html=True)


def get_status_emoji(status: VerificationStatus) -> str:
    """Get emoji for verification status."""
    return {
        VerificationStatus.VERIFIED: "✅",
        VerificationStatus.INACCURATE: "⚠️",
        VerificationStatus.FALSE: "❌",
        VerificationStatus.PENDING: "⏳"
    }.get(status, "❓")


def get_status_color(status: VerificationStatus) -> str:
    """Get color for verification status."""
    return {
        VerificationStatus.VERIFIED: "green",
        VerificationStatus.INACCURATE: "orange",
        VerificationStatus.FALSE: "red",
        VerificationStatus.PENDING: "gray"
    }.get(status, "gray")


def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 Fact Checker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a PDF and verify claims against live web data</p>', unsafe_allow_html=True)
    
    # Sidebar for API keys
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        groq_key = st.text_input(
            "Groq API Key (FREE)",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="Get a FREE key at console.groq.com"
        )
        
        tavily_key = st.text_input(
            "Tavily API Key",
            type="password",
            value=os.getenv("TAVILY_API_KEY", ""),
            help="Enter your Tavily API key for web search"
        )
        
        st.markdown("---")
        st.markdown("### 📖 How it works")
        st.markdown("""
        1. **Upload** a PDF document
        2. **Extract** claims automatically
        3. **Verify** against live web data
        4. **Review** the results
        """)
        
        st.markdown("---")
        st.markdown("### 🏷️ Status Legend")
        st.markdown("✅ **Verified** - Claim matches current data")
        st.markdown("⚠️ **Inaccurate** - Outdated or slightly wrong")
        st.markdown("❌ **False** - No evidence or contradicted")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Drag and drop a PDF file",
            type=["pdf"],
            help="Upload a PDF document to extract and verify claims"
        )
    
    with col2:
        st.subheader("📊 Quick Stats")
        if "results" in st.session_state and st.session_state.results:
            results = st.session_state.results
            verified = sum(1 for r in results if r.status == VerificationStatus.VERIFIED)
            inaccurate = sum(1 for r in results if r.status == VerificationStatus.INACCURATE)
            false = sum(1 for r in results if r.status == VerificationStatus.FALSE)
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            stat_col1.metric("Total Claims", len(results))
            stat_col2.metric("Verified", verified, delta=None)
            stat_col3.metric("Inaccurate", inaccurate, delta=None)
            stat_col4.metric("False", false, delta=None)
        else:
            st.info("Upload a PDF to see verification statistics")
    
    # Process button
    if uploaded_file is not None:
        if not groq_key or not tavily_key:
            st.error("⚠️ Please enter both API keys in the sidebar to proceed.")
        else:
            if st.button("🔍 Analyze Document", type="primary", use_container_width=True):
                process_document(uploaded_file, groq_key, tavily_key)
    
    # Display results
    if "results" in st.session_state and st.session_state.results:
        display_results(st.session_state.results)


def process_document(uploaded_file, openai_key: str, tavily_key: str):
    """Process the uploaded PDF and verify claims."""
    
    with st.spinner("Processing document..."):
        # Step 1: Extract text
        progress_bar = st.progress(0, text="Extracting text from PDF...")
        
        try:
            pdf_bytes = uploaded_file.read()
            pages = extract_text_from_pdf(pdf_bytes)
            
            if not pages:
                st.error("Could not extract any text from the PDF.")
                return
            
            st.success(f"✅ Extracted text from {len(pages)} page(s)")
            
            # Show text preview for debugging
            with st.expander("📄 Preview extracted text"):
                for page_num, text in pages[:3]:  # Show first 3 pages
                    st.markdown(f"**Page {page_num}:**")
                    st.text(text[:1000] + "..." if len(text) > 1000 else text)
                    st.markdown("---")
            
        except Exception as e:
            st.error(f"Error extracting PDF: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return
        
        # Step 2: Extract claims
        progress_bar.progress(33, text="Identifying claims...")
        
        try:
            claims = extract_claims(pages, openai_key)
            
            if not claims:
                st.warning("No verifiable claims found in the document. Check the debug output above for details.")
                return
            
            st.success(f"✅ Found {len(claims)} verifiable claim(s)")
            
            # Show extracted claims for debugging
            with st.expander("📝 Preview extracted claims"):
                for i, claim in enumerate(claims[:5], 1):
                    st.markdown(f"**Claim {i}:** {claim.text[:200]}...")
                    st.markdown(f"*Type: {claim.claim_type}*")
                    st.markdown("---")
            
        except Exception as e:
            st.error(f"Error extracting claims: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return
        
        # Step 3: Verify claims
        progress_bar.progress(66, text="Verifying claims against web data...")
        
        def update_progress(current, total, claim_text):
            progress = 66 + int((current / total) * 34)
            progress_bar.progress(progress, text=f"Verifying claim {current}/{total}...")
        
        try:
            results = verify_claims(claims, openai_key, tavily_key, update_progress)
            st.session_state.results = results
            progress_bar.progress(100, text="Complete!")
            st.success("✅ Verification complete!")
            
        except Exception as e:
            st.error(f"Error verifying claims: {str(e)}")
            return


def display_results(results):
    """Display verification results."""
    
    st.markdown("---")
    st.subheader("📋 Verification Results")
    
    # Filter options
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Verified", "Inaccurate", "False"]
        )
    
    # Filter results
    filtered_results = results
    if status_filter != "All":
        status_map = {
            "Verified": VerificationStatus.VERIFIED,
            "Inaccurate": VerificationStatus.INACCURATE,
            "False": VerificationStatus.FALSE
        }
        filtered_results = [r for r in results if r.status == status_map[status_filter]]
    
    # Display each result
    for i, result in enumerate(filtered_results, 1):
        status = result.status
        emoji = get_status_emoji(status)
        color = get_status_color(status)
        
        with st.expander(f"{emoji} Claim {i}: {result.claim.text[:80]}...", expanded=(status != VerificationStatus.VERIFIED)):
            
            # Status badge
            st.markdown(f"**Status:** :{color}[{status.value}]")
            
            # Claim details
            st.markdown("**📝 Claim:**")
            st.markdown(f"> {result.claim.text}")
            
            if result.claim.context:
                st.markdown("**📖 Context:**")
                st.markdown(f"_{result.claim.context}_")
            
            st.markdown(f"**📄 Page:** {result.claim.page_number}")
            st.markdown(f"**🏷️ Type:** {result.claim.claim_type.title()}")
            
            st.markdown("---")
            
            # Verification details
            st.markdown("**🔍 Analysis:**")
            st.markdown(result.explanation)
            
            if result.correct_info:
                st.markdown("**✏️ Correct Information:**")
                st.info(result.correct_info)
            
            # Confidence
            confidence_pct = int(result.confidence * 100)
            st.markdown(f"**📊 Confidence:** {confidence_pct}%")
            st.progress(result.confidence)
            
            # Sources
            if result.sources:
                st.markdown("**🔗 Sources:**")
                for source in result.sources:
                    st.markdown(f"- [{source.title}]({source.url})")


if __name__ == "__main__":
    main()
