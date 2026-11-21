# 📄 MarkItDown Studio

> **Universal document and file-to-Markdown converter powered by Microsoft MarkItDown and Streamlit.**

MarkItDown Studio transforms everyday documents, spreadsheets, presentations, audio recordings, images, and web pages into clean, structured, and token-efficient **Markdown**. It is designed specifically for researchers, developers, and AI engineers building LLM applications, RAG pipelines, and automated document workflows.

---

## ✨ Key Features

- **Universal Format Ingestion**: Convert virtually any common file type (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.html`, `.csv`, `.json`, `.xml`, `.mp3`, `.wav`, `.jpg`, `.png`, `.zip`).
- **Web URL Conversion**: Extract clean, readable Markdown directly from any public webpage or online document via direct URL ingestion.
- **Batch Processing & ZIP Export**: Convert multiple files in a single pass and download individual `.md` files or a packaged `.zip` archive.
- **Smart 200-Word Preview**: Previews are capped at the first 200 words to ensure instant UI rendering and prevent browser lagging on long documents, while the full file is preserved for download.
- **Multi-Tab Document Inspector**:
  - **Rendered Preview**: Formatted typography, links, and tables (capped at 200 words).
  - **Raw Markdown**: Line-numbered syntax highlighting (capped at 200 words).
  - **Document Insights & Analytics**: Full document statistics (total words, characters, lines, headings, tables, and estimated LLM tokens).
  - **LLM Prompt Template Generator**: Instantly generate structured prompts wrapping the extracted document for immediate use in ChatGPT, Claude, Gemini, or local models.
- **Responsive Dual-Mode UI**: Built with native Streamlit components adhering to modern accessibility and UX standards, featuring automatic light and dark mode support.
- **High File Size Limits**: Preconfigured for files up to **150 MB** per document.
- **Local & Privacy-First Execution**: Files are processed in-memory and on your local machine without sending document contents to third-party conversion servers.

---

## 📂 Supported Formats

| Category | File Extensions | Description & Capabilities |
| :--- | :--- | :--- |
| **Documents** | `.pdf`, `.docx`, `.rtf`, `.txt`, `.epub` | Preserves headings, bold/italic formatting, lists, tables, and hyperlinks. |
| **Spreadsheets** | `.xlsx`, `.xls`, `.csv`, `.tsv` | Converts tabular data into clean GitHub-flavored Markdown tables. |
| **Presentations** | `.pptx` | Extracts slide titles, speaker notes, and bullet points into ordered slide sections. |
| **Web & Markup** | `.html`, `.htm`, Web URLs | Strips navigation boilerplate, scripts, and ads, keeping the core article body. |
| **Data & Code** | `.json`, `.xml` | Parses structured data and renders it in readable, hierarchical Markdown code blocks. |
| **Media & Audio** | `.mp3`, `.wav` | Automated speech-to-text transcription via MarkItDown's audio pipeline. |
| **Images** | `.jpg`, `.jpeg`, `.png` | Extracts metadata, EXIF details, and embedded text. |
| **Archives** | `.zip` | Unpacks supported documents inside the archive and converts each one. |

---

## 🛠️ Tech Stack & Architecture

- **Core Engine**: [Microsoft MarkItDown](https://github.com/microsoft/markitdown) (`markitdown>=0.1.0`)
- **Frontend / UI**: [Streamlit](https://streamlit.io/) (`streamlit>=1.40.0`)
- **Package & Dependency Management**: [Astral uv](https://github.com/astral-sh/uv) / Python `3.12+`
- **Theming**: Native Streamlit theme token system with Inter & JetBrains Mono typography

---

## 🚀 Getting Started

### Prerequisites

- Python `3.12` or later
- [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### 1. Clone & Navigate to Project

```bash
git clone https://github.com/<your-username>/markitdown-app.git
cd markitdown-app
```

### 2. Install Dependencies

Using **uv** (recommended):
```bash
uv sync
```

Or using **pip**:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r pyproject.toml
```

### 3. Run the Application

Using **uv**:
```bash
uv run streamlit run main.py
```

Or with active virtual environment:
```bash
streamlit run main.py
```

The application will launch in your default web browser at `http://localhost:8501`.

---

## 💡 Why Markdown for LLMs & RAG?

Feeding raw binary formats (PDFs, PPTXs, Word documents) directly into Large Language Models often leads to:
1. **Token Bloat**: Binary noise, styling tags, XML schemas, and base64 embeds consume massive portions of your context window.
2. **Loss of Hierarchy**: Standard text extraction flattens headings, subheadings, and tables into unstructured blobs.
3. **Chunking Errors**: Vector databases and RAG chunkers perform significantly better when splitting on semantic Markdown dividers (`#`, `##`, `###`, tables, and lists).

**MarkItDown Studio** provides the cleanest intermediate representation, allowing you to feed maximum knowledge to models with minimum token cost.

---

## ⚙️ Configuration

Application options are configured in `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 150         # Maximum upload size in megabytes
enableStaticServing = false

[browser]
gatherUsageStats = false

[runner]
fastReruns = true
```

To modify the maximum file upload threshold, change `maxUploadSize` in `.streamlit/config.toml` and update `MAX_FILE_SIZE_MB` in `main.py`.

---

## 📁 Project Structure

```text
markitdown-app/
├── .streamlit/
│   └── config.toml           # Theme, server limits, and runtime configuration
├── main.py                   # Main Streamlit application and conversion pipeline
├── pyproject.toml            # Project metadata and package dependencies
├── uv.lock                   # Deterministic lockfile for reproducible builds
└── README.md                 # Project documentation and guide
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit pull requests to enhance format support and UI features.

---

## 📄 License

This project is licensed under the MIT License. Powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).
