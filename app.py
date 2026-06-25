import streamlit as st
import os
from PIL import Image
import cv2
import numpy as np
from rembg import remove
import io
import time
from concurrent.futures import ThreadPoolExecutor
import base64
import tempfile
import zipfile

# Page configuration dengan tema yang lebih modern
st.set_page_config(
    page_title="Background Remover App",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Modern & Profesional dengan kontras yang lebih baik
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        border-left: 4px solid #4ECDC4;
        padding-left: 1rem;
    }
    
    /* Card Styles */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    /* Button Styles */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .primary-button {
        background: linear-gradient(45deg, #FF6B6B, #ee5a24);
        color: white;
    }
    
    .secondary-button {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
    }
    
    .success-button {
        background: linear-gradient(45deg, #00b894, #00a085);
        color: white;
    }
    
    /* Download Links - PERBAIKAN: Hilangkan hover dan gunakan warna solid */
    .download-link {
        display: block;
        margin: 0.5rem 0;
        padding: 0.75rem 1rem;
        background: #ffffff !important;
        color: #2c3e50 !important;
        border-radius: 8px;
        text-decoration: none;
        text-align: center;
        font-weight: 600;
        border: 2px solid #3498db;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: none !important;
    }
    
    .download-link:hover {
        transform: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        background: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    .download-all-btn {
        background: #27ae60 !important;
        color: white !important;
        font-size: 1.2rem !important;
        padding: 1rem !important;
        border: 2px solid #27ae60 !important;
    }
    
    .download-all-btn:hover {
        background: #219653 !important;
        color: white !important;
        transform: none !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #FF6B6B, #ee5a24);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
        color: white;
    }
    
    /* Sidebar Text Colors - Improved Contrast */
    .sidebar .stRadio label {
        color: #000000 !important;
        font-weight: 600;
    }
    
    .sidebar .stSelectbox label {
        color: white !important;
        font-weight: 600;
    }
    
    .sidebar .stSlider label {
        color: white !important;
        font-weight: 600;
    }
    
    .sidebar .stColorPicker label {
        color: white !important;
        font-weight: 600;
    }
    
    .sidebar .stFileUploader label {
        color: white !important;
        font-weight: 600;
    }
    
    .sidebar .stMarkdown {
        color: white !important;
    }
    
    .sidebar .stMetric {
        color: white !important;
    }
    
    /* Image Preview */
    .image-preview {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .image-preview:hover {
        transform: scale(1.02);
    }
    
    /* Success & Error Messages */
    .success-msg {
        padding: 1.5rem;
        background: linear-gradient(45deg, #00b894, #00a085);
        color: white;
        border-radius: 12px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0, 184, 148, 0.3);
    }
    
    .error-msg {
        padding: 1.5rem;
        background: linear-gradient(45deg, #ff7675, #d63031);
        color: white;
        border-radius: 12px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(255, 118, 117, 0.3);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(45deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Custom Radio Buttons */
    .stRadio > div {
        flex-direction: row;
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: #f8f9fa;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        color: #000000 !important;
        font-weight: 600;
    }
    
    .stRadio > div > label:hover {
        border-color: #4ECDC4;
        transform: translateY(-2px);
        color: #000000 !important;
    }
    
    .stRadio > div > label[data-testid="stRadio"] {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white !important;
        border-color: #4ECDC4;
    }
    
    /* Improved text contrast in main area */
    .main .stMarkdown {
        color: #2c3e50;
    }
    
    .main .stInfo {
        color: #2c3e50;
    }
    
    /* Better contrast for sidebar headers */
    .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6 {
        color: white !important;
    }
    
    /* Improved radio button text in sidebar - FIXED */
    .sidebar .stRadio [data-testid="stMarkdown"] p {
        color: #000000 !important;
        font-weight: 600;
    }
    
    /* White text for sidebar card headers */
    .sidebar-card-header {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-left: 4px solid #4ECDC4;
        padding-left: 1rem;
    }
    
    /* FIX: Radio button text color in sidebar */
    .sidebar .stRadio [data-testid="stMarkdown"] {
        color: #000000 !important;
    }
    
    .sidebar .stRadio [data-testid="stMarkdown"] span {
        color: #000000 !important;
    }
    
    /* Ensure radio button labels are black */
    div[data-testid="stRadio"] label div p {
        color: #000000 !important;
        font-weight: 600;
    }
    
    div[data-testid="stRadio"] label div {
        color: #000000 !important;
    }
    
    /* Styling untuk card download section */
    .download-section-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
</style>
""", unsafe_allow_html=True)

def process_single_image(image_file, bg_color=None, bg_image=None, output_format="PNG"):
    """Process single image with background removal/replacement"""
    try:
        # Read image
        image = Image.open(image_file)
        
        # Remove background
        output_image = remove(image)
        
        # Replace background if specified
        if bg_color or bg_image:
            # Convert to RGBA if needed
            if output_image.mode != 'RGBA':
                output_image = output_image.convert('RGBA')
                
            if bg_color:
                # Create solid color background
                bg = Image.new('RGBA', output_image.size, bg_color)
            else:
                # Use provided background image
                bg = bg_image.resize(output_image.size).convert('RGBA')
            
            # Composite images
            output_image = Image.alpha_composite(bg, output_image)
        
        # Convert format if needed
        if output_format == "JPG" and output_image.mode in ['RGBA', 'LA']:
            # Create white background for JPG
            white_bg = Image.new('RGB', output_image.size, (255, 255, 255))
            white_bg.paste(output_image.convert('RGB'), mask=output_image.split()[-1] if output_image.mode in ['RGBA', 'LA'] else None)
            output_image = white_bg
        
        return output_image, None
    except Exception as e:
        return None, f"Error processing {image_file.name}: {str(e)}"

def get_image_download_link(img, filename, text, format="PNG"):
    """Generate download link for image"""
    buffered = io.BytesIO()
    if format == "JPG":
        img.save(buffered, format="JPEG", quality=95)
        mime_type = "image/jpeg"
        file_extension = "jpg"
    else:
        img.save(buffered, format="PNG")
        mime_type = "image/png"
        file_extension = "png"
    
    # Remove original extension from filename
    base_name = os.path.splitext(filename)[0]
    
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:{mime_type};base64,{img_str}" download="processed_{base_name}.{file_extension}" class="download-link">{text}</a>'
    return href

def create_zip_download(results, output_format):
    """Create a ZIP file containing all processed images"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, img in results:
            # Determine file extension
            file_extension = "jpg" if output_format == "JPG" else "png"
            
            # Convert image to bytes
            img_buffer = io.BytesIO()
            if output_format == "JPG":
                # Ensure image is in RGB mode for JPG
                if img.mode in ('RGBA', 'LA'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ['RGBA', 'LA'] else None)
                    rgb_img.save(img_buffer, format="JPEG", quality=95)
                else:
                    img.save(img_buffer, format="JPEG", quality=95)
            else:
                img.save(img_buffer, format="PNG")
            
            # Remove original extension from filename
            base_name = os.path.splitext(filename)[0]
            clean_filename = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            zip_filename = f"processed_{clean_filename}.{file_extension}"
            zip_file.writestr(zip_filename, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

def get_zip_download_link(zip_buffer, text):
    """Generate download link for ZIP file"""
    zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    href = f'<a href="data:application/zip;base64,{zip_b64}" download="processed_images.zip" class="download-link download-all-btn">{text}</a>'
    return href

def main():
    # Header dengan gradient yang menarik
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 class="main-header">🎨 Background Remover App</h1>
            <p style="font-size: 1.2rem; color: #ffffff; margin-bottom: 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
                AI-Powered Bulk Background Removal & Replacement
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Initialize session state
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = []
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'output_format' not in st.session_state:
        st.session_state.output_format = "PNG"
    if 'zip_file' not in st.session_state:
        st.session_state.zip_file = None
    
    # Sidebar dengan desain modern
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: white; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">⚙️ Configuration</h2>
                <div style="height: 3px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); width: 50px; margin: 0 auto;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Background options dalam card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-card-header">Background Type</div>', unsafe_allow_html=True)
            
            # Gunakan CSS inline untuk memastikan teks radio button berwarna hitam
            st.markdown(
                """
                <style>
                div[data-testid="stRadio"] > label > div:first-child {
                    color: #000000 !important;
                    font-weight: 600;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )
            
            bg_option = st.radio(
                "",
                ["Transparent", "Solid Color", "Custom Image"],
                label_visibility="collapsed"
            )
            
            bg_color = None
            bg_image = None
            
            if bg_option == "Solid Color":
                bg_color = st.color_picker("Choose background color", "#FFFFFF")
                st.markdown('<div class="info-box">🎨 Background color will be applied to all images</div>', unsafe_allow_html=True)
            
            elif bg_option == "Custom Image":
                bg_file = st.file_uploader("Upload background image", type=['png', 'jpg', 'jpeg'])
                if bg_file:
                    bg_image = Image.open(bg_file)
                    st.image(bg_image, caption="Background Image", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Processing options dalam card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-card-header">🚀 Processing Options</div>', unsafe_allow_html=True)
            
            max_workers = st.slider(
                "Parallel workers", 
                1, 8, 4,
                help="More workers = faster processing but more memory usage"
            )
            
            output_format = st.selectbox(
                "Output format", 
                ["PNG", "JPG"],
                help="PNG supports transparency, JPG does not"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Info card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-card-header">📊 System Info</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Python", "3.11.3")
            with col2:
                st.metric("Rembg", "2.0.53")
            
            st.progress(100)  # Placeholder untuk visual
            st.markdown('</div>', unsafe_allow_html=True)

    # Main area dengan layout yang lebih modern
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Upload section dengan card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sub-header" style="color: #2c3e50;">📤 Upload Images</div>', unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                "Choose multiple images (PNG, JPG, JPEG)",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="You can select multiple files at once",
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                st.markdown(f'<div class="success-msg">✅ {len(uploaded_files)} images ready for processing!</div>', unsafe_allow_html=True)
                
                # Preview first few images
                if len(uploaded_files) > 0:
                    st.markdown('<div class="sub-header" style="color: #2c3e50;">📷 Image Preview</div>', unsafe_allow_html=True)
                    preview_cols = st.columns(3)
                    for idx, file in enumerate(uploaded_files[:6]):
                        with preview_cols[idx % 3]:
                            image = Image.open(file)
                            st.image(image, caption=f"{file.name[:15]}...", use_column_width=True)
                    
                    if len(uploaded_files) > 6:
                        st.info(f"📁 ... and {len(uploaded_files) - 6} more images")
            else:
                st.info("👆 Upload images to get started!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Processing section dengan card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sub-header" style="color: #2c3e50;">🎯 Processing</div>', unsafe_allow_html=True)
            
            if uploaded_files:
                # Tombol proses dengan styling khusus
                button_placeholder = st.empty()
                if button_placeholder.button("🚀 Process All Images", type="primary", use_container_width=True):
                    with st.spinner("🔄 Processing images... This may take a while for large batches"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        results = []
                        errors = []
                        
                        # Create a temporary directory for processing
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Process images in parallel
                            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                                futures = []
                                
                                for file in uploaded_files:
                                    future = executor.submit(
                                        process_single_image, 
                                        file, 
                                        bg_color, 
                                        bg_image,
                                        output_format
                                    )
                                    futures.append((file.name, future))
                                
                                # Track progress
                                for i, (filename, future) in enumerate(futures):
                                    result, error = future.result()
                                    
                                    if result:
                                        results.append((filename, result))
                                    else:
                                        errors.append((filename, error))
                                    
                                    # Update progress
                                    progress = (i + 1) / len(futures)
                                    progress_bar.progress(progress)
                                    status_text.text(f"🔄 Processed {i + 1}/{len(futures)} images")
                                    
                                    # Small delay to show progress
                                    time.sleep(0.01)
                        
                        # Create ZIP file
                        zip_buffer = create_zip_download(results, output_format)
                        
                        # Save results to session state
                        st.session_state.processed_results = results
                        st.session_state.processing_complete = True
                        st.session_state.output_format = output_format
                        st.session_state.errors = errors
                        st.session_state.zip_file = zip_buffer
                        
                        # Rerun to update the display
                        st.rerun()
            else:
                st.info("💡 Upload images to enable processing")
                
                # Quick guide
                st.markdown("""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; color: #2c3e50;">
                    <h4 style="color: #2c3e50;">🎯 How to use:</h4>
                    <ol style="color: #6c757d;">
                        <li>📤 Upload images (multiple selection supported)</li>
                        <li>⚙️ Configure background in sidebar</li>
                        <li>🚀 Click 'Process All Images'</li>
                        <li>📥 Download results</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results dari session state
    if st.session_state.processing_complete and st.session_state.processed_results:
        st.markdown("---")
        
        results = st.session_state.processed_results
        output_format = st.session_state.output_format
        errors = st.session_state.errors if hasattr(st.session_state, 'errors') else []
        zip_file = st.session_state.zip_file
        
        # Results header
        st.markdown(
            """
            <div style="text-align: center; margin: 2rem 0;">
                <h2 class="sub-header" style="text-align: center; border: none; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">📥 Processing Results</h2>
                <div style="height: 3px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); width: 100px; margin: 0 auto;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if results:
            st.markdown('<div class="success-msg" style="text-align: center;">✅ Processing completed successfully!</div>', unsafe_allow_html=True)
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card"><div style="font-size: 0.9rem;">Processed</div><div style="font-size: 2rem; font-weight: bold;">' + str(len(results)) + '</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card"><div style="font-size: 0.9rem;">Format</div><div style="font-size: 2rem; font-weight: bold;">' + output_format + '</div></div>', unsafe_allow_html=True)
            with col3:
                failed_count = len(errors) if errors else 0
                st.markdown(f'<div class="metric-card"><div style="font-size: 0.9rem;">Failed</div><div style="font-size: 2rem; font-weight: bold;">{failed_count}</div></div>', unsafe_allow_html=True)
            with col4:
                zip_size = f"{(len(zip_file.getvalue()) / (1024*1024)):.1f} MB" if zip_file else "0 MB"
                st.markdown(f'<div class="metric-card"><div style="font-size: 0.9rem;">ZIP Size</div><div style="font-size: 2rem; font-weight: bold;">{zip_size}</div></div>', unsafe_allow_html=True)
            
            # Download section
            st.markdown('<div class="sub-header" style="text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">📦 Download Results</div>', unsafe_allow_html=True)
            
            download_col1, download_col2 = st.columns([2, 1])
            
            with download_col1:
                st.markdown('<div class="download-section-card">', unsafe_allow_html=True)
                st.markdown("### Download Options")
                
                # Download all button
                if zip_file:
                    st.markdown(
                        get_zip_download_link(
                            zip_file, 
                            f"📦 DOWNLOAD ALL {len(results)} IMAGES AS ZIP FILE"
                        ), 
                        unsafe_allow_html=True
                    )
                
                st.markdown("---")
                st.markdown("### Individual Downloads")
                # Individual downloads dengan scrollable area
                download_container = st.container()
                with download_container:
                    for filename, img in results:
                        st.markdown(
                            get_image_download_link(
                                img, 
                                filename, 
                                f"📥 Download {filename[:20]}...",
                                output_format
                            ), 
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with download_col2:
                st.markdown('<div class="download-section-card">', unsafe_allow_html=True)
                st.markdown("### Quick Actions")
                
                if st.button("🔄 Process New Batch", use_container_width=True, type="secondary"):
                    # Reset session state
                    st.session_state.processed_results = []
                    st.session_state.processing_complete = False
                    st.session_state.zip_file = None
                    st.rerun()
                
                if st.button("📊 Performance Stats", use_container_width=True, type="secondary"):
                    success_rate = (len(results) / (len(results) + len(errors))) * 100 if (len(results) + len(errors)) > 0 else 0
                    st.info(f"**Performance Summary:**\n- Processed: {len(results)} images\n- Format: {output_format}\n- Workers: {max_workers}\n- Success Rate: {success_rate:.1f}%")
                
                st.markdown("---")
                st.markdown("### Tips")
                st.info("💡 **Pro Tip:** For best results with JPG format, use solid color backgrounds")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Processed images preview
            st.markdown('<div class="sub-header" style="text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">🖼️ Processed Preview</div>', unsafe_allow_html=True)
            
            # Grid layout untuk preview images
            preview_cols = st.columns(4)
            for idx, (filename, img) in enumerate(results[:8]):
                with preview_cols[idx % 4]:
                    with st.container():
                        st.markdown('<div class="image-preview">', unsafe_allow_html=True)
                        # Convert to RGB for display if needed
                        display_img = img
                        if display_img.mode == 'RGBA':
                            display_img = display_img.convert('RGB')
                        st.image(display_img, use_column_width=True)
                        st.caption(f"📷 {filename[:15]}...")
                        st.markdown('</div>', unsafe_allow_html=True)
        
        if errors:
            st.markdown('<div class="error-msg">❌ Some images failed to process</div>', unsafe_allow_html=True)
            with st.expander("View Error Details"):
                for filename, error in errors:
                    st.error(f"**{filename}**: {error}")

if __name__ == "__main__":
    main()

# streamlit run app.py