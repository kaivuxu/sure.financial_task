from .base_parser import BaseParser
import re

class AxisParser(BaseParser):
    def parse(self):
        self.extract_text()
        
        return {
            'bank': 'Axis Bank',
            'card_last_4_digits': self.extract_card_number(),
            'statement_date': self.extract_statement_date(),
            'payment_due_date': self.extract_due_date(),
            'total_amount_due': self.extract_total_due(),
            'minimum_amount_due': self.extract_minimum_due()
        }
    
    def extract_card_number(self):
        # Axis format: "45145700****5541"
        patterns = [
            r'(\d{8})\*{4}(\d{4})',
            r'Credit Card Number\s*[\r\n]+\s*\d+\*+(\d{4})',
            r'Card No[:\.\s]+\d+\*+(\d{4})'
        ]
        
        # Try to find full pattern first
        match = re.search(r'\d{8}\*{4}(\d{4})', self.text)
        if match:
            return match.group(1)
        
        # Fallback
        for pattern in patterns:
            result = self.extract_with_regex(pattern)
            if result != "Not Found":
                return result
        
        return "Not Found"
    
    def extract_statement_date(self):
        # Axis format: "Statement Generation Date 18/11/2019" or "Statement Period 19/10/2019-18/11/2019"
        patterns = [
            r'Statement Generation Date\s*[\r\n]+\s*(\d{2}/\d{2}/\d{4})',
            r'Statement Period\s*[\r\n]+\s*\d{2}/\d{2}/\d{4}-(\d{2}/\d{2}/\d{4})',
            r'Statement Generation Date\s+(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in patterns:
            result = self.extract_with_regex(pattern)
            if result != "Not Found":
                return result
        
        return "Not Found"
    
    def extract_due_date(self):
        # Axis format: "Payment Due Date 09/12/2019"
        patterns = [
            r'Payment Due Date\s*[\r\n]+\s*(\d{2}/\d{2}/\d{4})',
            r'Payment Due Date\s+(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in patterns:
            result = self.extract_with_regex(pattern)
            if result != "Not Found":
                return result
        
        return "Not Found"
    
    def extract_total_due(self):
        # Axis format: "Total Payment Due 176,674.12 Dr"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Total Payment Due' in line:
                # Amount might be on same line or next line
                amount_match = re.search(r'([\d,]+\.?\d*)\s*Dr', line)
                if amount_match:
                    return self.clean_amount(amount_match.group(1))
                
                # Check next line
                if i < len(lines) - 1:
                    amount_match = re.search(r'([\d,]+\.?\d*)\s*Dr', lines[i+1])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
        
        # Fallback pattern
        match = re.search(r'Total Payment Due\s*[\r\n]*\s*([\d,]+\.?\d*)\s*Dr', self.text)
        if match:
            return self.clean_amount(match.group(1))
        
        return "Not Found"
    
    def extract_minimum_due(self):
        # Axis format: "Minimum Payment Due 21,257.00 Dr"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Minimum Payment Due' in line:
                # Amount might be on same line or next line
                amount_match = re.search(r'([\d,]+\.?\d*)\s*Dr', line)
                if amount_match:
                    return self.clean_amount(amount_match.group(1))
                
                # Check next line
                if i < len(lines) - 1:
                    amount_match = re.search(r'([\d,]+\.?\d*)\s*Dr', lines[i+1])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
        
        # Fallback
        match = re.search(r'Minimum Payment Due\s*[\r\n]*\s*([\d,]+\.?\d*)\s*Dr', self.text)
        if match:
            return self.clean_amount(match.group(1))
        
        return "Not Found"