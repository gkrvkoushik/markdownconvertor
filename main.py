import io
import os
import streamlit as st
from markitdown import MarkItDown, StreamInfo

MAX_FILE_SIZE_MB = 50

st.set_page_config(page_title="Universal File to Markdown", page_icon="📄", layout="centered")

st.title("📄 Universal File to Markdown Converter")
st.write("Upload any supported document (PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, etc.) to convert it into a clean Markdown file.")


@st.cache_resource
def get_converter():
    return MarkItDown()


md = get_converter()

uploaded_file = st.file_uploader("Choose a file", type=None)

if uploaded_file is not None:
    file_name = uploaded_file.name
    base_name, file_ext = os.path.splitext(file_name)
    output_filename = f"{base_name}.md"
    cache_key = f"md_{file_name}_{uploaded_file.size}"

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File exceeds the {MAX_FILE_SIZE_MB}MB limit.")
        st.stop()

    if cache_key not in st.session_state:
        with st.spinner(f"Converting `{file_name}`..."):
            try:
                file_bytes = io.BytesIO(uploaded_file.getvalue())
                stream_info = StreamInfo(extension=file_ext.lower(), filename=file_name)
                result = md.convert_stream(file_bytes, stream_info=stream_info)
                st.session_state[cache_key] = result.markdown
            except ValueError as e:
                st.error(f"Unsupported file format: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Conversion failed: {e}")
                st.stop()

    markdown_text = st.session_state[cache_key]

    st.success("Conversion complete!")
    st.download_button(
        label="⬇️ Download Markdown (.md)",
        data=markdown_text.encode("utf-8"),
        file_name=output_filename,
        mime="text/markdown",
    )

    tab1, tab2 = st.tabs(["Raw Markdown", "Rendered Preview"])
    with tab1:
        st.code(markdown_text, language="markdown")
    with tab2:
        st.markdown(markdown_text)
