from pathlib import Path
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re


INPUT_FILE = Path(r"/home/arshix/projects/multihop_rag/data/mplus_topics.xml")
OUTPUT_DIR = Path(r"/home/arshix/projects/multihop_rag/data/extracted")


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def clean_text(text):
    if not text:
        return ""

    soup = BeautifulSoup(
        text,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def safe_filename(text):
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    return text.strip("_")


print(f"Reading: {INPUT_FILE}")

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

print(f"Root element: {root.tag}")

count = 0

# MedlinePlus topics are represented by health-topic elements
topics = root.findall(".//health-topic")

print(f"Found {len(topics)} health topics")


for topic in topics:

    title = topic.attrib.get(
        "title",
        ""
    )

    url = topic.attrib.get(
        "url",
        ""
    )

    if not title:
        continue

    # Extract all text contained in this topic
    text_parts = []

    for element in topic.iter():

        if element.text:
            text_parts.append(
                element.text
            )

    full_text = clean_text(
        " ".join(text_parts)
    )

    filename = safe_filename(title)

    if not filename:
        continue

    output_file = (
        OUTPUT_DIR /
        f"{filename}.txt"
    )

    content = f"""TITLE:
{title}

SOURCE:
MedlinePlus

URL:
{url}

CONTENT:
{full_text}
"""

    output_file.write_text(
        content,
        encoding="utf-8"
    )

    count += 1

    if count % 100 == 0:
        print(
            f"Extracted {count} documents..."
        )


print()
print("=" * 50)
print(f"Extracted {count} medical documents")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 50)