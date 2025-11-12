# TODO: figure out later 
import os 
import sys
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).parent.parent))
import pdfplumber 
import re
import json 
from typing import List, Dict
from src.config.paths import DATA_DIR, PDF_DIR, ROOT_DIR


class PdfChunker(): 
    """
    A class for parsing PDF files and converting them into structured text chunks.
    
    This class processes PDF files in a specified directory, extracts text content,
    and formats it as markdown while preserving document structure like headings,
    paragraphs, lists, and bold text.
    
    Attributes:
        filepaths (list): List of pdf file paths 
    """
    def __init__(self):
        self.chunks = None  

    def parse_pdf(self, filepath: str) -> str:
        """
        Parse a single PDF file and convert it to markdown format using pdfplumber & heuristic formatting. 
        NOTE: Currently treats each PDF as a single chunk. Tables and images
              are not processed in the current implementation.
        
        Args:
            filepath (str): Path to the PDF file to be parsed
            
        Returns:
            str: Markdown-formatted text content of the entire PDF
        """

        md_text = ""
        heading_font_threshold_main = 18  # large heading (H1)
        heading_font_threshold_sub = 10   # subheading (H2)
        merge_threshold = 18              # vertical distance threshold for merging lines

        bullet_pattern = re.compile(r"^(\*|-|•)\s+")
        numbered_pattern = re.compile(r"^\d+[\.\)]\s+")

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                chars = page.chars
                lines = {}

                # Group characters by approximate y-position
                for c in chars:
                    y = round(c["top"])
                    if y not in lines:
                        lines[y] = []
                    lines[y].append(c)

                # Sort lines top-to-bottom
                sorted_lines = sorted(lines.items(), key=lambda kv: kv[0])

                prev_y = None
                prev_line_type = None
                buffer_line = ""

                for y, line_chars in sorted_lines:
                    # Sort left-to-right within the line
                    line_chars = sorted(line_chars, key=lambda x: x["x0"])
                    line_text = "".join([c["text"] for c in line_chars]).strip()
                    if not line_text:
                        continue

                    # Determine font attributes
                    font_sizes = [c["size"] for c in line_chars]
                    max_font = max(font_sizes)
                    bold = any("Bold" in c["fontname"] for c in line_chars)

                    # Detect list items
                    is_bullet = bool(bullet_pattern.match(line_text))
                    is_numbered = bool(numbered_pattern.match(line_text))

                    # Classify line type
                    if max_font >= heading_font_threshold_main:
                        line_type = "heading_main"
                    elif max_font >= heading_font_threshold_sub:
                        line_type = "heading_sub"
                    elif is_bullet or is_numbered:
                        line_type = "list_item"
                    elif bold:
                        line_type = "bold"
                    else:
                        line_type = "text"

                    # Merge consecutive text lines that belong to the same paragraph
                    if (
                        prev_y is not None
                        and abs(y - prev_y) < merge_threshold
                        and line_type == prev_line_type == "text"
                    ):
                        buffer_line += " " + line_text
                    elif (
                        prev_y is not None
                        and abs(y - prev_y) < merge_threshold
                        and line_type == prev_line_type == "list_item"
                    ):
                        # Continuation of a bullet/numbered list item
                        md_text = md_text.rstrip()
                        md_text += " " + line_text + "\n"
                    else:
                        # Flush the previous buffered paragraph before writing new block
                        if buffer_line:
                            md_text += buffer_line + "\n\n"
                            buffer_line = ""

                        # Write based on line type
                        if line_type == "heading_main":
                            md_text += f"# {line_text}\n\n"
                        elif line_type == "heading_sub":
                            md_text += f"## {line_text}\n\n"
                        elif line_type == "bold":
                            md_text += f"**{line_text}**\n\n"
                        elif line_type == "list_item":
                            md_text += f"{line_text}\n"
                        else:
                            buffer_line = line_text  # start a new paragraph

                    prev_y = y
                    prev_line_type = line_type

                # Flush any remaining buffered text
                if buffer_line:
                    md_text += buffer_line + "\n\n"

        # Cleanup: remove excess blank lines (more than 2)
        md_text = re.sub(r"\n{3,}", "\n\n", md_text)

        return md_text


    def chunk(self, save_results=False) -> Dict[str, dict]: 
        """
        Process all PDF files in the configured directory to create document chunks.

        Args:
            save_results (bool, optional): Whether to save results to JSON file.
                                         Defaults to False.
                                         
        Returns:
            dict: Dictionary of chunks where keys are chunk IDs and values contain:
                - filename: Original PDF filename
                - type: Content type ("example" or "description")
                - text: Extracted and formatted markdown text
        """
        chunks = {}
        # iterate through files in the pdf dir 
        for root, dirs, files in os.walk(PDF_DIR):
            for i, filename in enumerate(files): 
                text_chunk = self.parse_pdf(PDF_DIR / filename)

                if "example" in filename: 
                    text_type = "example"
                else: 
                    text_type = "description"

                name = filename.strip(".pdf")
                chunk_id = f"{name}_chunk_{i+1}"

                chunks[chunk_id] = {
                    "filename": filename, 
                    "type": text_type,
                    "text": text_chunk, 
                }

        if save_results: 
            self.chunks = chunks 

            chunks_dir = ROOT_DIR / "chunks"
            chunks_dir.mkdir(exist_ok=True)
            with open(chunks_dir / "chunks.json", 'w') as f: 
                json.dump(chunks, f)


        return chunks 


# chunker = PdfChunker()
# res = chunker.chunk(save_results=True)

# with open('chunk.txt', 'w') as f: 
#     f.write(res["example_post_chunk_1"]["text"])
#     f.write(res["company_description_chunk_2"]["text"])
