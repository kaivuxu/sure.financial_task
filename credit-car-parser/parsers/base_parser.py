import pdfplumber
import re
from abc import ABC, abstractmethod

class BaseParser(ABC):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
        self.pages = []
        
    def extract_text(self):
        """Extract text from all pages of PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            self.pages = pdf.pages
            self.text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return self.text
    
    @abstractmethod
    def parse(self):
        """Each bank parser must implement this method"""
        pass
    
    def extract_with_regex(self, pattern, default="Not Found"):
        """Helper method to extract data using regex"""
        match = re.search(pattern, self.text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else default
    
    def clean_amount(self, amount_str):
    
        if not amount_str or amount_str == "Not Found":
            return "Not Found"
    # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[₹$,\s]', '', amount_str)
    # Ensure it's a valid number
        try:
            float(cleaned)
            return cleaned
        except:
            return "Not Found"
    