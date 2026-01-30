import os
import logging
import fitz  

from docx2python import docx2python
from docx2pdf import convert
from docx import Document
import os
import pdfplumber
from pathlib import Path
import zipfile

logger = logging.getLogger(__name__)



# ------------------- DOCX -> PDF -------------------

def docx_to_pdf(docx: str) -> str:
    pdf = Path(docx).with_suffix(".pdf")
    convert(str(docx), str(pdf))
    return str(pdf)


# ------------------- DOCX ORIGIN DETECTION -------------------

def detect_docx_origin(docx_path: str) -> str:
    """
    Heuristic classifier:
      - PDF_CONVERTED_DOCX
      - ORIGINAL_DOCX
      - DOC_TO_DOCX
    """
    doc = Document(docx_path)

    paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    total_paras = len(paras)

    if total_paras == 0:
        return "ORIGINAL_DOCX"

    word_counts = [len(p.split()) for p in paras]
    short_lines = sum(1 for wc in word_counts if wc <= 3)
    short_ratio = short_lines / max(total_paras, 1)

    avg_words = sum(word_counts) / max(len(word_counts), 1)

    no_punct_lines = sum(1 for p in paras if p and p[-1] not in ".!?:;)")
    no_punct_ratio = no_punct_lines / max(total_paras, 1)

    table_count = len(doc.tables)

    xml_score = 0
    try:
        with zipfile.ZipFile(docx_path, "r") as z:
            doc_xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

        if ("lastRenderedPageBreak" in doc_xml) or ('w:type="page"' in doc_xml):
            xml_score += 2

        if ("txbxContent" in doc_xml) or ("framePr" in doc_xml) or ("posH" in doc_xml) or ("posV" in doc_xml):
            xml_score += 2

        if doc_xml.count("<w:tbl") >= 3:
            xml_score += 1

        if doc_xml.count("<w:br") >= 20:
            xml_score += 1

    except Exception:
        pass

    score = xml_score

    if short_ratio >= 0.55:
        score += 2
    elif short_ratio >= 0.40:
        score += 1

    if avg_words < 6 and total_paras > 60:
        score += 1

    if no_punct_ratio >= 0.70 and total_paras > 50:
        score += 1

    if table_count >= 3:
        score += 1

    joined = "\n".join(paras).lower()
    if any(x in joined for x in ["adobe", "acrobat", "converted from pdf", "evaluation warning"]):
        score += 1

    if score >= 4:
        return "PDF_CONVERTED_DOCX"

    times_new_roman_hits = 0
    for p in doc.paragraphs:
        for r in p.runs:
            if r.font.name and "Times New Roman" in str(r.font.name):
                times_new_roman_hits += 1
                if times_new_roman_hits >= 10:
                    return "DOC_TO_DOCX"

    return "ORIGINAL_DOCX"


def detect_origin_and_ensure_pdf(file_path: str, docx_to_pdf_func) -> dict:
    """
    Returns a routing decision + always a pdf_path.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return {
            "origin": "PDF_ORIGINAL",
            "confidence": "high",
            "pdf_path": str(path),
            "note": "Input is already a PDF."
        }

    if ext == ".docx":
        origin = detect_docx_origin(str(path))

        if origin == "PDF_CONVERTED_DOCX":
            label = "PDF_CONVERTED_TO_DOCX"
            confidence = "high"
            note = "DOCX shows strong PDF conversion artifacts."
        elif origin == "DOC_TO_DOCX":
            label = "LEGACY_DOC_CONVERTED_TO_DOCX"
            confidence = "medium"
            note = "DOCX looks like legacy DOC conversion (heuristic)."
        else:
            label = "ORIGINAL_DOCX"
            confidence = "medium"
            note = "DOCX looks like authored Word document."

        pdf_path = docx_to_pdf_func(str(path))
        return {"origin": label, "confidence": confidence, "pdf_path": str(pdf_path), "note": note}

    if ext == ".doc":
        pdf_path = docx_to_pdf_func(str(path))  # works only if your converter supports .doc
        return {
            "origin": "LEGACY_DOC",
            "confidence": "low",
            "pdf_path": str(pdf_path),
            "note": "Legacy DOC can't be reliably inferred; standardized to PDF."
        }

    raise ValueError(f"Unsupported file type: {ext}")


# ------------------- PDF LAYOUT HELPERS -------------------

def _find_split_x(words, page_width, min_gap_ratio=0.08):
    xs = sorted(w["x0"] for w in words if "x0" in w)
    if len(xs) < 30:
        return None

    largest_gap = 0
    split_x = None
    for a, b in zip(xs, xs[1:]):
        gap = b - a
        if gap > largest_gap:
            largest_gap = gap
            split_x = (a + b) / 2

    if largest_gap < page_width * min_gap_ratio:
        return None

    return split_x


def is_two_column(page, min_gap_ratio=0.08):
    words = page.extract_words() or []
    split_x = _find_split_x(words, page.width, min_gap_ratio=min_gap_ratio)
    if split_x is None:
        return False
    left = [w for w in words if w["x0"] < split_x]
    right = [w for w in words if w["x0"] >= split_x]
    return bool(left) and bool(right)


def words_to_lines(words, y_tol=3):
    if not words:
        return ""
    words = sorted(words, key=lambda w: (round(w["top"] / y_tol), w["x0"]))

    lines, current, current_y = [], [], None
    for w in words:
        y = round(w["top"] / y_tol)
        if current_y is None or y == current_y:
            current.append(w["text"])
            current_y = y
        else:
            lines.append(" ".join(current))
            current = [w["text"]]
            current_y = y

    if current:
        lines.append(" ".join(current))

    return "\n".join(lines)


def read_sequential(page):
    return page.extract_text() or ""


def read_two_column_header_left_then_right(page, header_top=90, y_tol=3, min_gap_ratio=0.08):
    words = page.extract_words() or []
    if not words:
        return ""

    split_x = _find_split_x(words, page.width, min_gap_ratio=min_gap_ratio)
    if split_x is None:
        return read_sequential(page)

    header_words = [w for w in words if w["top"] < header_top]
    body_words = [w for w in words if w["top"] >= header_top]

    left_words = [w for w in body_words if w["x0"] < split_x]
    right_words = [w for w in body_words if w["x0"] >= split_x]

    header_text = words_to_lines(header_words, y_tol=y_tol).strip()
    left_text = words_to_lines(left_words, y_tol=y_tol).strip()
    right_text = words_to_lines(right_words, y_tol=y_tol).strip()

    parts = [p for p in [header_text, left_text, right_text] if p]
    return "\n\n".join(parts).strip()


def read_pdf_layout_aware(pdf_path):
    output = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if is_two_column(page):
                output.append(read_two_column_header_left_then_right(page))
            else:
                output.append(read_sequential(page))
    return "\n\n".join(t for t in output if t.strip()).strip()


# ------------------- DOCX TEXT READERS + QUALITY CHECK -------------------

def _docx2python_text(docx_path: str) -> str:
    """
    docx2python can crash on table-heavy DOCX files. Return "" on failure.
    """
    try:
        doc = docx2python(docx_path)
        text = doc.text
        doc.close()

        if isinstance(text, list):
            return "\n".join(
                " ".join(map(str, row)) if isinstance(row, list) else str(row)
                for row in text if row
            ).strip()

        return str(text).strip()

    except Exception:
        return ""


def _python_docx_text(docx_path: str) -> str:
    """
    Safe fallback using python-docx.
    Reads paragraphs + tables.
    """
    doc = Document(docx_path)

    lines = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            lines.append(t)

    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                ct = (cell.text or "").strip()
                if ct:
                    lines.append(ct)

    # De-dupe preserve order
    seen = set()
    out = []
    for ln in lines:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)

    return "\n".join(out).strip()


def _looks_bad_text(text: str) -> bool:
    """
    Small quality check:
      - too short
      - too many tiny lines (PDF-like wrapping)
    """
    if not text or len(text.strip()) < 200:
        return True

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 5:
        return True

    short = sum(1 for ln in lines if len(ln.split()) <= 2)
    if short / max(len(lines), 1) > 0.55:
        return True

    return False


# ------------------- FILE READER (fixed + safe) -------------------

def extract_text_from_file(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext == ".pdf":
            return read_pdf_layout_aware(file_path)

        if ext in [".docx", ".doc"]:
            meta = detect_origin_and_ensure_pdf(file_path, docx_to_pdf)

            # If it’s PDF-converted or legacy, prefer PDF layout extraction
            if meta["origin"] in ("PDF_CONVERTED_TO_DOCX", "LEGACY_DOC", "LEGACY_DOC_CONVERTED_TO_DOCX"):
                return read_pdf_layout_aware(meta["pdf_path"])

            # ORIGINAL_DOCX: docx2python -> python-docx -> pdf fallback
            text = _docx2python_text(file_path)

            if _looks_bad_text(text):
                text2 = _python_docx_text(file_path)
                if not _looks_bad_text(text2):
                    return text2

            if _looks_bad_text(text):
                return read_pdf_layout_aware(meta["pdf_path"])

            return text

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        return None

    except Exception as e:
        raise Exception(f"Failed to extract text from file: {e}")
