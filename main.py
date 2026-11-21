import io
import os
import re
import zipfile
import streamlit as st
from markitdown import MarkItDown, StreamInfo

MAX_FILE_SIZE_MB = 150
PREVIEW_WORD_LIMIT = 200

# ── Page Configuration ──
st.set_page_config(
    page_title="MarkItDown Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def get_converter() -> MarkItDown:
    """Initialize and cache the MarkItDown converter instance."""
    return MarkItDown()


def calculate_metrics(text: str) -> dict[str, int]:
    """Calculate basic statistics and structural metrics from markdown content."""
    lines = text.splitlines()
    words = re.findall(r"\b\w+\b", text)
    headings = [line for line in lines if line.strip().startswith("#")]
    tables = [line for line in lines if re.match(r"^\s*\|.*\|\s*$", line)]
    code_blocks = text.count("```") // 2

    return {
        "words": len(words),
        "characters": len(text),
        "lines": len(lines),
        "headings": len(headings),
        "tables": len(tables),
        "code_blocks": code_blocks,
        "estimated_tokens": int(len(words) * 1.3),
        "reading_time_min": max(1, round(len(words) / 200)),
    }


def truncate_to_words(text: str, max_words: int = PREVIEW_WORD_LIMIT) -> tuple[str, bool]:
    """Truncates text to max_words while preserving original formatting up to the cutoff."""
    words = list(re.finditer(r"\b\w+\b", text))
    if len(words) <= max_words:
        return text, False

    cutoff_idx = words[max_words - 1].end()
    return text[:cutoff_idx].strip(), True


# ── Initialize session state ──
st.session_state.setdefault("results", {})
st.session_state.setdefault("uploader_version", 0)


def reset_session_state() -> None:
    """Clear cached conversions, reset uploader widgets, and reset state."""
    st.session_state["uploader_version"] += 1
    st.session_state["results"] = {}
    for key in list(st.session_state.keys()):
        if key.startswith("md_"):
            del st.session_state[key]


md = get_converter()
current_uploader_version = st.session_state["uploader_version"]
results: dict[str, dict] = st.session_state["results"]

# ── Main Header ──
header_col, action_col = st.columns([5, 1], vertical_alignment="center")
with header_col:
    st.title("Universal document to Markdown converter", anchor=False)
    st.markdown(
        "Convert documents, presentations, spreadsheets, media, and web pages into clean, "
        "structured Markdown ready for LLMs, documentation, and data pipelines."
    )
with action_col:
    if results:
        st.button(
            "Clear all",
            icon=":material/delete_sweep:",
            width="stretch",
            key=f"btn_reset_header_{current_uploader_version}",
            on_click=reset_session_state,
        )

# ── Input Mode Selector ──
source_mode = st.segmented_control(
    "Conversion source",
    options=["Upload files", "Web URL"],
    default="Upload files",
    label_visibility="collapsed",
    key="source_mode",
)

# ── Source 1: File Upload ──
if source_mode == "Upload files":
    uploaded_files = st.file_uploader(
        "Upload files for conversion",
        type=None,
        accept_multiple_files=True,
        help=f"Select one or more files up to {MAX_FILE_SIZE_MB}MB each.",
        key=f"file_uploader_{current_uploader_version}",
    )

    if uploaded_files:
        with st.status("Processing uploaded files...", expanded=False) as status:
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                base_name, file_ext = os.path.splitext(file_name)
                cache_key = f"md_file_{file_name}_{uploaded_file.size}"
                size_mb = uploaded_file.size / (1024 * 1024)

                if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    results[file_name] = {
                        "error": f"File exceeds maximum allowed limit of {MAX_FILE_SIZE_MB}MB.",
                        "size_mb": size_mb,
                        "type": file_ext.lower(),
                    }
                    continue

                if cache_key not in st.session_state:
                    try:
                        file_bytes = io.BytesIO(uploaded_file.getvalue())
                        stream_info = StreamInfo(extension=file_ext.lower(), filename=file_name)
                        conversion_result = md.convert_stream(file_bytes, stream_info=stream_info)
                        markdown_text = conversion_result.markdown or ""
                        doc_title = conversion_result.title or base_name

                        st.session_state[cache_key] = {
                            "markdown": markdown_text,
                            "title": doc_title,
                            "size_mb": size_mb,
                            "type": file_ext.lower(),
                            "output_filename": f"{base_name}.md",
                            "metrics": calculate_metrics(markdown_text),
                        }
                    except Exception as exc:
                        st.session_state[cache_key] = {
                            "error": str(exc),
                            "size_mb": size_mb,
                            "type": file_ext.lower(),
                        }

                results[file_name] = st.session_state[cache_key]

            status.update(label="File processing complete!", state="complete", expanded=False)

# ── Source 2: Web URL ──
else:
    with st.container(border=True):
        st.subheader("Convert webpage from URL", anchor=False)
        st.caption("Extract clean markdown article content directly from any accessible web URL.")

        url_col1, url_col2 = st.columns([4, 1], vertical_alignment="bottom")
        with url_col1:
            input_url = st.text_input(
                "Webpage URL",
                placeholder="https://example.com/article-or-report",
                label_visibility="visible",
                key=f"input_web_url_{current_uploader_version}",
            )
        with url_col2:
            convert_url_btn = st.button(
                "Convert URL",
                icon=":material/travel_explore:",
                type="primary",
                width="stretch",
                key=f"btn_convert_url_{current_uploader_version}",
            )

        if convert_url_btn and input_url.strip():
            target_url = input_url.strip()
            cache_key = f"md_url_{target_url}"

            with st.spinner(f"Fetching and parsing {target_url}..."):
                try:
                    conversion_result = md.convert_url(target_url)
                    markdown_text = conversion_result.markdown or ""
                    doc_title = conversion_result.title or target_url
                    clean_name = re.sub(r"[^\w\-_\. ]", "_", target_url.replace("https://", "").replace("http://", ""))[:40]

                    st.session_state[cache_key] = {
                        "markdown": markdown_text,
                        "title": doc_title,
                        "size_mb": len(markdown_text.encode("utf-8")) / (1024 * 1024),
                        "type": "url",
                        "output_filename": f"{clean_name}.md",
                        "metrics": calculate_metrics(markdown_text),
                    }
                    results[target_url] = st.session_state[cache_key]
                    st.success("Webpage converted successfully!", icon=":material/check_circle:")
                except Exception as exc:
                    results[target_url] = {
                        "error": f"Failed to fetch or convert URL: {exc}",
                        "size_mb": 0.0,
                        "type": "url",
                    }
                    st.error(f"Error converting URL: {exc}", icon=":material/error:")

# ── Results & Workspace ──
if results:
    st.divider()

    successful = {k: v for k, v in results.items() if "markdown" in v}
    failed = {k: v for k, v in results.items() if "error" in v}

    total_words = sum(v["metrics"]["words"] for v in successful.values())
    total_chars = sum(v["metrics"]["characters"] for v in successful.values())

    # Summary Row
    summary_cols = st.columns(4)
    summary_cols[0].metric("Total files", len(results))
    summary_cols[1].metric("Converted successfully", len(successful))
    summary_cols[2].metric("Total words generated", f"{total_words:,}")
    summary_cols[3].metric("Est. total tokens", f"{int(total_words * 1.3):,}")

    # Action Toolbar: Download All & Clear All
    with st.container(horizontal=True, horizontal_alignment="right"):
        if len(successful) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_name, data in successful.items():
                    zf.writestr(data["output_filename"], data["markdown"].encode("utf-8"))
            zip_buffer.seek(0)

            st.download_button(
                label=f"Download all ({len(successful)} files as ZIP)",
                icon=":material/folder_zip:",
                data=zip_buffer,
                file_name="markitdown_export.zip",
                mime="application/zip",
                type="primary",
                key=f"btn_download_zip_{current_uploader_version}",
            )

        st.button(
            "Clear all results",
            icon=":material/delete_sweep:",
            key=f"btn_reset_results_{current_uploader_version}",
            on_click=reset_session_state,
        )

    # File selector when multiple files exist
    file_list = list(results.keys())
    if len(file_list) > 1:
        selected_file = st.selectbox(
            "Select document to inspect",
            options=file_list,
            format_func=lambda name: f"✓ {name}" if "markdown" in results[name] else f"✗ {name} (Error)",
            key=f"select_active_file_{current_uploader_version}",
        )
    else:
        selected_file = file_list[0]

    current_data = results[selected_file]

    # Active Document Display
    if "error" in current_data:
        st.error(
            f"**Conversion failed for `{selected_file}`**\n\n{current_data['error']}",
            icon=":material/error:",
        )
    else:
        doc_metrics = current_data["metrics"]
        preview_text, is_truncated = truncate_to_words(current_data["markdown"], max_words=PREVIEW_WORD_LIMIT)

        with st.container(border=True):
            header_col1, header_col2 = st.columns([3, 1], vertical_alignment="center")
            with header_col1:
                st.subheader(current_data.get("title") or selected_file, anchor=False)
                st.caption(
                    f"File: `{selected_file}` · "
                    f"Size: {current_data['size_mb']:.2f} MB · "
                    f"Type: {current_data['type'].upper()} · "
                    f"Reading time: ~{doc_metrics['reading_time_min']} min"
                )

            with header_col2:
                st.download_button(
                    label="Download Markdown",
                    icon=":material/download:",
                    data=current_data["markdown"].encode("utf-8"),
                    file_name=current_data["output_filename"],
                    mime="text/markdown",
                    type="primary",
                    width="stretch",
                    key=f"dl_active_{selected_file}_{current_uploader_version}",
                )

            metric_cols = st.columns(4)
            metric_cols[0].metric("Words", f"{doc_metrics['words']:,}")
            metric_cols[1].metric("Characters", f"{doc_metrics['characters']:,}")
            metric_cols[2].metric("Lines", f"{doc_metrics['lines']:,}")
            metric_cols[3].metric("Headings", f"{doc_metrics['headings']:,}")

            tab_preview, tab_code, tab_insights, tab_prompt = st.tabs([
                ":material/visibility: Rendered preview",
                ":material/code: Raw markdown",
                ":material/analytics: Document insights",
                ":material/chat: LLM prompt template",
            ])

            with tab_preview:
                if current_data["markdown"].strip():
                    if is_truncated:
                        st.info(
                            f"Displaying 200-word preview ({doc_metrics['words']:,} words in complete file). "
                            "Download the .md file above to view the full document.",
                            icon=":material/visibility:",
                        )
                    st.markdown(preview_text)
                    if is_truncated:
                        st.caption("*(Preview truncated at 200 words)*")
                else:
                    st.info("The file converted successfully, but produced empty text output.", icon=":material/info:")

            with tab_code:
                if is_truncated:
                    st.caption(f"Showing first 200 words of {doc_metrics['words']:,} total words:")
                    code_display = f"{preview_text}\n\n# ... [Preview truncated at 200 words. Download the full file for complete markdown] ..."
                else:
                    code_display = current_data["markdown"]
                st.code(code_display, language="markdown", line_numbers=True)

            with tab_insights:
                stat_col1, stat_col2 = st.columns(2)
                with stat_col1:
                    with st.container(border=True):
                        st.markdown("**Complete document statistics**")
                        st.markdown(f"- **Total words**: {doc_metrics['words']:,}")
                        st.markdown(f"- **Total characters**: {doc_metrics['characters']:,}")
                        st.markdown(f"- **Headings count**: {doc_metrics['headings']}")
                        st.markdown(f"- **Detected table rows**: {doc_metrics['tables']}")
                        st.markdown(f"- **Code blocks**: {doc_metrics['code_blocks']}")
                        st.markdown(f"- **Estimated total tokens**: ~{doc_metrics['estimated_tokens']:,}")
                with stat_col2:
                    with st.container(border=True):
                        st.markdown("**Headings outline**")
                        headings = [
                            line.strip()
                            for line in current_data["markdown"].splitlines()
                            if line.strip().startswith("#")
                        ]
                        if headings:
                            for h in headings[:15]:
                                st.markdown(f"`{h}`")
                            if len(headings) > 15:
                                st.caption(f"... and {len(headings) - 15} more headings")
                        else:
                            st.caption("No markdown headings detected in document.")

            with tab_prompt:
                st.caption("Ready-to-use prompt template for feeding this document into ChatGPT, Claude, Gemini, or local models:")
                prompt_doc = f"{preview_text}\n\n[... Truncated for preview. Replace with full downloaded markdown ...]" if is_truncated else current_data["markdown"]
                prompt_template = (
                    "You are an expert document analyst. Analyze the following document and provide:\n"
                    "1. A concise executive summary (3-5 bullet points)\n"
                    "2. Key insights and takeaways\n"
                    "3. Any action items, dates, or quantitative figures mentioned\n\n"
                    f"--- DOCUMENT START ({current_data['output_filename']}) ---\n"
                    f"{prompt_doc}\n"
                    f"--- DOCUMENT END ---"
                )
                st.code(prompt_template, language="text", line_numbers=False)

else:
    # ── Empty State / Feature Tour ──
    st.divider()
    st.markdown("### Why convert with MarkItDown?")

    tour_col1, tour_col2, tour_col3 = st.columns(3)
    with tour_col1:
        with st.container(border=True):
            st.subheader(":material/layers: Universal format support", anchor=False)
            st.markdown(
                "Convert PDFs, Word documents, Excel spreadsheets, PowerPoint presentations, "
                "audio, and images into clean, structured text in a single workspace."
            )
    with tour_col2:
        with st.container(border=True):
            st.subheader(":material/psychology: LLM & RAG ready", anchor=False)
            st.markdown(
                "Stripped of styling junk, markdown maximizes context window efficiency and retains "
                "semantic hierarchies for embeddings, vector search, and prompting."
            )
    with tour_col3:
        with st.container(border=True):
            st.subheader(":material/bolt: Fast & batch export", anchor=False)
            st.markdown(
                "Process multiple documents simultaneously, inspect detailed metrics, and export "
                "individual Markdown files or a packaged ZIP archive in one click."
            )
