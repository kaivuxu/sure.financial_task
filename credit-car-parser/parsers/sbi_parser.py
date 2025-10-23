from .base_parser import BaseParser
import re

class SBIParser(BaseParser):
    def parse(self):
        self.extract_text()
        
        return {
            'bank': 'SBI Card',
            'card_last_4_digits': self.extract_card_number(),
            'statement_date': self.extract_statement_date(),
            'payment_due_date': self.extract_due_date(),
            'total_amount_due': self.extract_total_due(),
            'minimum_amount_due': self.extract_minimum_due()
        }
    
    def extract_card_number(self):
        # SBI format: "XXXX XXXX XXXX XX51" or similar
        match = re.search(r'XXXX\s+XXXX\s+XXXX\s+(?:XX)?(\d{2,4})', self.text)
        if match:
            return match.group(1)
        return "Not Found"
    
    def extract_statement_date(self):
        # SBI format: "15 Nov 2018" - day month year
        lines = self.text.split('\n')
        
        # Look for "Statement Date" label
        for i, line in enumerate(lines):
            if 'Statement Date' in line:
                # Check next few lines
                for j in range(i, min(i + 5, len(lines))):
                    date_match = re.search(r'(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})', lines[j])
                    if date_match:
                        return date_match.group(1)
        
        # Fallback: search for "for Statement dated"
        match = re.search(r'for\s+Statement\s+dated\s+(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})', self.text)
        if match:
            return match.group(1)
        
        # Another fallback: just find any date in that format
        match = re.search(r'(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})', self.text)
        if match:
            return match.group(1)
        
        return "Not Found"
    
    def extract_due_date(self):
        # Look for "Payment Due Date"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Payment Due Date' in line or 'Due Date' in line:
                # Check next few lines
                for j in range(i, min(i + 5, len(lines))):
                    date_match = re.search(r'(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})', lines[j])
                    if date_match:
                        return date_match.group(1)
        
        # Fallback
        match = re.search(r'Payment\s+Due\s+Date.*?(\d{2}\s+[A-Z][a-z]{2}\s+\d{4})', self.text, re.DOTALL)
        if match:
            return match.group(1)
        
        return "Not Found"
    
    def extract_total_due(self):
        # Look for "Total Amount Due" in ACCOUNT SUMMARY section
        lines = self.text.split('\n')
        
        # Strategy 1: Find in the structured section
        for i, line in enumerate(lines):
            if '*Total Amount Due' in line or 'Total Amount Due' in line:
                # The amount might be on the same line or nearby
                # Look in next 3 lines
                for j in range(i, min(i + 4, len(lines))):
                    # Find amounts like 16,720.00
                    amounts = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', lines[j])
                    if amounts:
                        # Return the first reasonable amount (> 100)
                        for amt in amounts:
                            clean = self.clean_amount(amt)
                            if clean != "Not Found" and float(clean) > 100:
                                return clean
        
        # Strategy 2: Look in ACCOUNT SUMMARY section
        summary_match = re.search(r'ACCOUNT SUMMARY(.*?)(?:Important Messages|TRANSACTIONS)', self.text, re.DOTALL)
        if summary_match:
            summary_text = summary_match.group(1)
            amounts = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', summary_text)
            # Usually Total Amount Due is one of the larger amounts
            if amounts:
                # Clean and convert to float for comparison
                cleaned_amounts = []
                for amt in amounts:
                    cleaned = self.clean_amount(amt)
                    if cleaned != "Not Found":
                        try:
                            cleaned_amounts.append((float(cleaned), cleaned))
                        except:
                            pass
                
                if cleaned_amounts:
                    # Return the second largest (first is usually credit limit)
                    cleaned_amounts.sort(reverse=True)
                    if len(cleaned_amounts) >= 2:
                        return str(cleaned_amounts[1][1])
                    else:
                        return str(cleaned_amounts[0][1])
        
        return "Not Found"
    
    def extract_minimum_due(self):
        # Look for "Minimum Amount Due"
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Minimum Amount Due' in line:
                # Check next few lines
                for j in range(i, min(i + 4, len(lines))):
                    amounts = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', lines[j])
                    if amounts:
                        # Return first reasonable amount
                        for amt in amounts:
                            clean = self.clean_amount(amt)
                            if clean != "Not Found":
                                return clean
        
        return "Not Found"