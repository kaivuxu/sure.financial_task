from .base_parser import BaseParser
import re

class KotakParser(BaseParser):
    def parse(self):
        self.extract_text()
        
        return {
            'bank': 'Kotak Mahindra Bank',
            'card_last_4_digits': self.extract_card_number(),
            'statement_date': self.extract_statement_date(),
            'payment_due_date': self.extract_due_date(),
            'total_amount_due': self.extract_total_due(),
            'minimum_amount_due': self.extract_minimum_due()
        }
    
    def extract_card_number(self):
        # Kotak format: "414767XXXXXX6705"
        patterns = [
            r'(\d{6})X+(\d{4})',
            r'Card.*?(\d{6})X+(\d{4})'
        ]
        
        match = re.search(r'\d{6}X+(\d{4})', self.text)
        if match:
            return match.group(1)
        
        return "Not Found"
    
    def extract_statement_date(self):
        # Kotak format: "Statement Date 1-Mar-2023"
        patterns = [
            r'Statement Date\s*[\r\n]+.*?(\d{1,2}-[A-Z][a-z]{2}-\d{4})',
            r'Statement Date\s+(\d{1,2}-[A-Z][a-z]{2}-\d{4})',
            r'Statement Period\s+\d+-[A-Z][a-z]+-\d+\s+To\s+(\d{1,2}-[A-Z][a-z]{2}-\d{4})'
        ]
        
        for pattern in patterns:
            result = self.extract_with_regex(pattern)
            if result != "Not Found":
                return result
        
        return "Not Found"
    
    def extract_due_date(self):
        # Kotak format: "Due Date 19-Mar-2023"
        patterns = [
            r'Due Date\s*[\r\n]+.*?(\d{1,2}-[A-Z][a-z]{2}-\d{4})',
            r'Due Date\s+(\d{1,2}-[A-Z][a-z]{2}-\d{4})'
        ]
        
        for pattern in patterns:
            result = self.extract_with_regex(pattern)
            if result != "Not Found":
                return result
        
        return "Not Found"
    
    def extract_total_due(self):
        # Kotak format: "Total Amount Due (Rs.) 478,387.66"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Total Amount Due' in line:
                # Check same line
                amount_match = re.search(r'([\d,]+\.?\d*)', line)
                if amount_match:
                    amount = self.clean_amount(amount_match.group(1))
                    try:
                        if float(amount) > 100:  # Reasonable threshold
                            return amount
                    except:
                        pass
                
                # Check next line
                if i < len(lines) - 1:
                    amount_match = re.search(r'([\d,]+\.?\d*)', lines[i+1])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
        
        return "Not Found"
    
    def extract_minimum_due(self):
        # Kotak corporate cards don't have minimum due (paid by corporate)
        # Look for "Minimum Amount Due" or "Minimum Payment Due"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Minimum' in line and 'Due' in line:
                # Check same and next lines
                for j in range(i, min(i + 3, len(lines))):
                    amount_match = re.search(r'([\d,]+\.?\d*)', lines[j])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
        
        # For corporate cards, return a note
        if 'corporate' in self.text.lower():
            return "N/A (Corporate Card)"
        
        return "Not Found"