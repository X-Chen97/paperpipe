from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal, Dict, Any
from pdf_tools import extract_abstract_pymupdf
from pdf_tools import extract_abstract_unstructured

@dataclass
class AbstractExtractionResult:
    """Container for abstract extraction results."""
    text: Optional[str]
    method: str
    success: bool
    error: Optional[str] = None

class PDFParser:
    """PDF parser for extracting abstracts using different methods."""
    
    def __init__(self):
        self.extraction_methods = {
            'pymupdf': extract_abstract_pymupdf,
            'unstructured': extract_abstract_unstructured
        }
    
    def extract_abstract(self,
                        pdf_path: str | Path,
                        method: Literal['pymupdf', 'unstructured'] = 'unstructured',
                        fallback: bool = True,
                        **kwargs) -> AbstractExtractionResult:
        """
        Extract abstract from PDF using specified method.
        
        Parameters:
        -----------
        pdf_path : str | Path
            Path to the PDF file
        method : Literal['pymupdf', 'unstructured']
            Extraction method to use
        fallback : bool
            Whether to try alternative method if first method fails
        **kwargs
            Additional arguments passed to extraction methods
            
        Returns:
        --------
        AbstractExtractionResult
            Container with extraction results and metadata
        """
        if isinstance(pdf_path, str):
            pdf_path = Path(pdf_path)
            
        if not pdf_path.exists():
            return AbstractExtractionResult(
                text=None,
                method=method,
                success=False,
                error="File not found"
            )
            
        try:
            abstract = self.extraction_methods[method](pdf_path, **kwargs)
            
            # If primary method fails and fallback is enabled, try alternative
            if abstract is None and fallback:
                alt_method = 'unstructured' if method == 'pymupdf' else 'pymupdf'
                try:
                    abstract = self.extraction_methods[alt_method](pdf_path, **kwargs)
                    if abstract is not None:
                        return AbstractExtractionResult(
                            text=abstract,
                            method=alt_method,
                            success=True
                        )
                except Exception as e:
                    # If both methods fail, return result from primary method
                    pass
                    
            return AbstractExtractionResult(
                text=abstract,
                method=method,
                success=abstract is not None
            )
            
        except Exception as e:
            return AbstractExtractionResult(
                text=None,
                method=method,
                success=False,
                error=str(e)
            )

def main():
    """Command-line interface for PDF abstract extraction."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Extract abstracts from academic PDF papers.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to the PDF file'
    )
    
    parser.add_argument(
        '-m', '--method',
        type=str,
        choices=['pymupdf', 'unstructured'],
        default='unstructured',
        help='Method to use for extraction'
    )
    
    parser.add_argument(
        '--no-fallback',
        action='store_true',
        help='Disable fallback to alternative method if primary method fails'
    )
    
    parser.add_argument(
        '-x', '--x-tolerance',
        type=int,
        default=20,
        help='X-axis tolerance for unstructured method'
    )
    
    args = parser.parse_args()
    
    # Initialize parser and extract abstract
    pdf_parser = PDFParser()
    result = pdf_parser.extract_abstract(
        args.pdf_path,
        method=args.method,
        fallback=not args.no_fallback,
        x_tolerance=args.x_tolerance
    )
    
    # Handle results
    if result.success:
        print(f"\nAbstract extracted using {result.method} method:\n")
        print(result.text)
        sys.exit(0)
    else:
        print(f"\nError: Failed to extract abstract: {result.error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()