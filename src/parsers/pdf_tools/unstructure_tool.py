import io
from typing import List, Optional
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from unstructured.partition.pdf import partition_pdf
from .utils import clean_text, is_abstract_header

def parse_pdf_unstructured(file_path: Path):
    """Parse PDF using unstructured library."""
    reader = PdfReader(str(file_path))
    page = reader.pages[0]
    
    writer = PdfWriter()
    writer.add_page(page)
    
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    
    return partition_pdf(
        file=buffer,
        include_metadata=True,
        strategy="hi_res"
    )

def extract_abstract_unstructured(pdf_path: Path,
                                x_tolerance: int = 20) -> Optional[str]:
    """
    Extract abstract from PDF using unstructured library.
    
    Parameters:
    -----------
    pdf_path : Path
        Path to the PDF file
    x_tolerance : int
        Horizontal alignment tolerance in pixels
        
    Returns:
    --------
    Optional[str]
        Extracted abstract text if found, None otherwise
    """
    elements = parse_pdf_unstructured(pdf_path)
    
    # Find abstract header
    abstract_header = None
    for element in elements:
        if is_abstract_header(str(element)):
            abstract_header = element
            break
            
    if not (abstract_header and hasattr(abstract_header, 'metadata')):
        return None
        
    header_coords = abstract_header.metadata.coordinates
    if not header_coords:
        return None
        
    # Get header coordinates
    header_left_x = header_coords.points[0][0]
    header_right_x = header_coords.points[3][0]
    header_bottom_y = header_coords.points[1][1]
    
    # Find closest aligned block
    closest_distance = float('inf')
    closest_block = None
    
    for element in elements:
        if not (hasattr(element, 'metadata') and element.metadata.coordinates):
            continue
            
        block_coords = element.metadata.coordinates
        block_left_x = block_coords.points[0][0]
        block_right_x = block_coords.points[3][0]
        block_top_y = block_coords.points[0][1]
        
        # Check alignment
        if (block_top_y < header_bottom_y or
            block_left_x > header_left_x + x_tolerance or
            block_right_x < header_right_x - x_tolerance):
            continue
            
        distance = block_top_y - header_bottom_y
        if distance < closest_distance:
            block_height = block_coords.points[1][1] - block_coords.points[0][1]
            header_height = header_coords.points[1][1] - header_coords.points[0][1]
            if block_height > 2 * header_height:
                closest_distance = distance
                closest_block = element
                
    return clean_text(str(closest_block)) if closest_block else None