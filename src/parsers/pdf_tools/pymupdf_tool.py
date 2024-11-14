from typing import List, Optional
from pathlib import Path
import fitz  # PyMuPDF
from .utils import clean_text, is_abstract_header, filter_abnormal_words, DEFAULT_ABNORMAL_PATTERNS

def get_block_gap(block1: List, block2: List) -> float:
    """Calculate vertical gap between two blocks."""
    return block2[1] - block1[3]  # y0 of block2 - y1 of block1

def find_abstract_block_idx(blocks: List) -> Optional[int]:
    """Find the index of the block containing the abstract header."""
    for i, block in enumerate(blocks):
        if is_abstract_header(block[4]):
            return i
    return None

def extract_abstract_pymupdf(pdf_path: Path,
                           min_words: int = 100,
                           initial_blocks: int = 5,
                           gap_threshold: float = 0.5) -> Optional[str]:
    """
    Extract abstract from PDF using PyMuPDF.
    
    Parameters:
    -----------
    pdf_path : Path
        Path to the PDF file
    min_words : int
        Minimum number of words expected in abstract
    initial_blocks : int
        Number of initial blocks to analyze for gap consistency
        Collect the first 'initial_blocks' blocks without break to avoid inconsistent gaps in the beginning
    gap_threshold : float
        Threshold for gap consistency checking
        
    Returns:
    --------
    Optional[str]
        Extracted abstract text if found, None otherwise
    """
    doc = fitz.open(pdf_path)
    page = doc[0]
    blocks = page.get_text("blocks")
    
    abstract_idx = find_abstract_block_idx(blocks)
    if abstract_idx is None:
        doc.close()
        return None
        
    next_block = blocks[abstract_idx + 1]
    next_block_text = next_block[4]
    
    # Case 1: Next block is complete abstract
    if len(next_block_text.split()) > min_words:
        doc.close()
        return filter_abnormal_words(next_block_text, DEFAULT_ABNORMAL_PATTERNS)
    
    # Case 2: Abstract is split into multiple blocks
    collected_blocks = [blocks[abstract_idx + 1]]
    gaps = []
    current_idx = abstract_idx + 1
    
    while current_idx < len(blocks) - 1 and len(collected_blocks) < initial_blocks:
        current_block = blocks[current_idx]
        next_block = blocks[current_idx + 1]
        gap = get_block_gap(current_block, next_block)
        gaps.append(gap)
        collected_blocks.append(next_block)
        current_idx += 1

    while current_idx < len(blocks) - 1:
        current_block = blocks[current_idx]
        next_block = blocks[current_idx + 1]
        gap = get_block_gap(current_block, next_block)
        
        # Calculate average gap from previous blocks
        avg_gap = sum(gaps) / len(gaps)
        
        # Break if gap deviates significantly from average
        if abs(gap - avg_gap) > gap_threshold * avg_gap:  # 50% threshold
            break
                
        gaps.append(gap)
        collected_blocks.append(next_block)
        current_idx += 1
    
    doc.close()
    return clean_text(' '.join(block[4] for block in collected_blocks))
