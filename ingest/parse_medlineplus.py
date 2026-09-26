# ingest/parse_medlineplus.py

import re
import xml.etree.ElementTree as ET
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

XML_FILE = Path(
    "data/mplus_topics.xml"
)

OUTPUT_DIR = Path(
    "data/medical/medlineplus"
)


# ============================================================
# Utilities
# ============================================================

def safe_filename(text):
    """
    Convert a title into a safe filename.

    Example:
        "High Blood Pressure" -> "high_blood_pressure.txt"
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    return text.strip("_")


def clean_text(text):
    """
    Clean extracted XML text.
    """

    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# XML parsing
# ============================================================

def parse_medlineplus_xml(
    xml_file=XML_FILE,
    output_dir=OUTPUT_DIR
):
    """
    Parse MedlinePlus XML and generate one .txt
    file per health topic.

    Returns a list of parsed documents.
    """

    xml_file = Path(xml_file)
    output_dir = Path(output_dir)

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not xml_file.exists():
        raise FileNotFoundError(
            f"MedlinePlus XML file not found:\n"
            f"{xml_file.resolve()}"
        )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"Reading XML:\n{xml_file.resolve()}"
    )

    # --------------------------------------------------------
    # Parse XML
    # --------------------------------------------------------

    tree = ET.parse(xml_file)

    root = tree.getroot()

    print(
        f"XML root element: {root.tag}"
    )

    # --------------------------------------------------------
    # Find health topics
    # --------------------------------------------------------

    topics = root.findall(
        ".//health-topic"
    )

    print(
        f"Found {len(topics)} health topics"
    )

    if not topics:
        raise ValueError(
            "No <health-topic> elements were found "
            "in the XML file. The XML structure may be "
            "different from the expected MedlinePlus format."
        )

    # --------------------------------------------------------
    # Extract documents
    # --------------------------------------------------------

    documents = []

    for index, topic in enumerate(
        topics,
        start=1
    ):

        # ----------------------------------------------------
        # Topic metadata
        # ----------------------------------------------------

        title = clean_text(
            topic.attrib.get(
                "title",
                ""
            )
        )

        url = clean_text(
            topic.attrib.get(
                "url",
                ""
            )
        )

        if not title:
            print(
                f"Skipping topic #{index}: "
                f"no title"
            )

            continue

        # ----------------------------------------------------
        # Extract all textual content
        # ----------------------------------------------------

        text_parts = []

        for element in topic.iter():

            if element.text:

                text = clean_text(
                    element.text
                )

                if text:
                    text_parts.append(
                        text
                    )

        content = " ".join(
            text_parts
        )

        # ----------------------------------------------------
        # Generate document ID
        # ----------------------------------------------------

        doc_id = safe_filename(
            title
        )

        if not doc_id:
            print(
                f"Skipping topic #{index}: "
                f"invalid title"
            )

            continue

        # ----------------------------------------------------
        # Create .txt content
        # ----------------------------------------------------

        document_text = f"""TITLE:
{title}

SOURCE:
MedlinePlus

URL:
{url}

CONTENT:
{content}
"""

        # ----------------------------------------------------
        # Write .txt file
        # ----------------------------------------------------

        output_file = (
            output_dir /
            f"{doc_id}.txt"
        )

        output_file.write_text(
            document_text,
            encoding="utf-8"
        )

        # ----------------------------------------------------
        # Store structured document
        # ----------------------------------------------------

        document = {
            "doc_id": doc_id,
            "title": title,
            "source": "MedlinePlus",
            "url": url,
            "content": content,
            "filepath": str(
                output_file
            )
        }

        documents.append(
            document
        )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if index % 100 == 0:

            print(
                f"Processed "
                f"{index}/{len(topics)} topics..."
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        f"Generated {len(documents)} documents"
    )
    print(
        f"Output directory:\n"
        f"{output_dir.resolve()}"
    )
    print("=" * 60)

    return documents


# ============================================================
# Load generated TXT files
# ============================================================

def parse_medline_file(filepath):
    """
    Parse one generated MedlinePlus TXT file.
    """

    filepath = Path(filepath)

    text = filepath.read_text(
        encoding="utf-8"
    )

    def extract(
        field,
        next_field=None
    ):

        if next_field:

            pattern = (
                rf"^{re.escape(field)}:\s*"
                rf"(.*?)"
                rf"^\s*{re.escape(next_field)}:"
            )

        else:

            pattern = (
                rf"^{re.escape(field)}:\s*"
                rf"(.*)"
            )

        match = re.search(
            pattern,
            text,
            re.DOTALL | re.MULTILINE
        )

        if match:

            return match.group(
                1
            ).strip()

        return ""

    return {
        "title": extract(
            "TITLE",
            "SOURCE"
        ),

        "source": extract(
            "SOURCE",
            "URL"
        ),

        "url": extract(
            "URL",
            "CONTENT"
        ),

        "content": extract(
            "CONTENT"
        ),

        "doc_id": filepath.stem,

        "filepath": str(
            filepath
        )
    }


def load_all_docs(
    data_dir=OUTPUT_DIR
):
    """
    Load all generated .txt files.
    """

    data_dir = Path(
        data_dir
    )

    if not data_dir.exists():

        raise FileNotFoundError(
            f"Directory does not exist:\n"
            f"{data_dir.resolve()}"
        )

    docs = []

    files = sorted(
        data_dir.glob("*.txt")
    )

    print(
        f"Found {len(files)} TXT files"
    )

    for filepath in files:

        try:

            doc = parse_medline_file(
                filepath
            )

            if not doc["content"]:

                print(
                    f"Warning: empty content: "
                    f"{filepath}"
                )

                continue

            docs.append(doc)

        except Exception as e:

            print(
                f"Failed to parse "
                f"{filepath}: {e}"
            )

    print(
        f"Loaded {len(docs)} documents"
    )

    return docs


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("MEDLINEPLUS INGESTION")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Step 1: XML → TXT
    # --------------------------------------------------------

    documents = parse_medlineplus_xml()

    # --------------------------------------------------------
    # Step 2: Load generated TXT files
    # --------------------------------------------------------

    loaded_docs = load_all_docs()

    # --------------------------------------------------------
    # Show example
    # --------------------------------------------------------

    if loaded_docs:

        print()
        print("=" * 60)
        print("EXAMPLE DOCUMENT")
        print("=" * 60)

        doc = loaded_docs[0]

        print(
            f"\nDocument ID:\n"
            f"{doc['doc_id']}"
        )

        print(
            f"\nTitle:\n"
            f"{doc['title']}"
        )

        print(
            f"\nSource:\n"
            f"{doc['source']}"
        )

        print(
            f"\nURL:\n"
            f"{doc['url']}"
        )

        print(
            f"\nContent preview:\n"
            f"{doc['content'][:1000]}"
        )

    print()
    print("Done.")