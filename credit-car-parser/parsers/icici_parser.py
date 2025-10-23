from .base_parser import BaseParser
import re

class ICICIParser(BaseParser):
    def parse(self):
        self.extract_text()
        
        return {
            'bank': 'ICICI Bank',
            'card_last_4_digits': self.extract_card_number(),
            'statement_date': self.extract_statement_date(),
            'payment_due_date': self.extract_due_date(),
            'total_amount_due': self.extract_total_due(),
            'minimum_amount_due': self.extract_minimum_due()
        }
    
    def extract_card_number(self):
        # Look for any pattern like "4375 XXXX XXXX 4000"
        match = re.search(r'(\d{4})\s+XXXX\s+XXXX\s+(\d{4})', self.text)
        if match:
            return match.group(2)  # Return last 4 digits
        return "Not Found"
    
    def extract_statement_date(self):
        # Look for date in DD/MM/YYYY format near "Statement Date"
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if 'Statement Date' in line:
                # Check current line and next few lines for date
                for j in range(i, min(i + 5, len(lines))):
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[j])
                    if date_match:
                        return date_match.group(1)
        
        # Fallback: search anywhere for date pattern
        match = re.search(r'(\d{2}/\d{2}/\d{4})', self.text)
        if match:
            return match.group(1)
        
        return "Not Found"
    
    def extract_due_date(self):
        # Look for "Due Date" followed by date
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if 'Due Date' in line:
                # Check current line and next few lines
                for j in range(i, min(i + 5, len(lines))):
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[j])
                    if date_match:
                        return date_match.group(1)
        
        return "Not Found"
    
    def extract_total_due(self):
        # In ICICI statement, look for "Your Total Amount Due" specifically
        # The structure shows: "Your Total Amount Due" on one line, then amount on next line
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Your Total Amount Due' in line:
                # Check next few lines for the amount
                for j in range(i + 1, min(i + 5, len(lines))):
                    # Look for amounts, but skip if it's the Minimum Amount Due section
                    if 'Minimum Amount Due' not in lines[j]:
                        amount_match = re.search(r'([\d,]+\.\d{2})', lines[j])
                        if amount_match:
                            amount = self.clean_amount(amount_match.group(1))
                            # Make sure it's the larger amount (Total > Minimum typically)
                            try:
                                if float(amount.replace(',', '')) > 200:  # Reasonable threshold
                                    return amount
                            except:
                                pass
        
        # Fallback: Look for larger amount in the statement
        amounts = re.findall(r'([\d,]+\.\d{2})', self.text)
        if amounts:
            cleaned = []
            for amt in amounts:
                clean = self.clean_amount(amt)
                try:
                    cleaned.append((float(clean), clean))
                except:
                    pass
            
            if cleaned:
                cleaned.sort(reverse=True)
                # Return largest reasonable amount
                for val, amt in cleaned:
                    if 100 < val < 100000:  # Reasonable range
                        return amt
        
        return "Not Found"
    
    def extract_minimum_due(self):
        # In ICICI, the amount appears BEFORE "Minimum Amount Due" label
        lines = self.text.split('\n')
        
        for i, line in enumerate(lines):
            if 'Minimum Amount Due' in line:
                # Check the PREVIOUS line (amount comes before label in ICICI)
                if i > 0:
                    amount_match = re.search(r'([\d,]+\.\d{2})', lines[i-1])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
                
                # Also check current line
                amount_match = re.search(r'([\d,]+\.\d{2})', line)
                if amount_match:
                    return self.clean_amount(amount_match.group(1))
                
                # Check next line as fallback
                if i < len(lines) - 1:
                    amount_match = re.search(r'([\d,]+\.\d{2})', lines[i+1])
                    if amount_match:
                        return self.clean_amount(amount_match.group(1))
        
        return "Not Found"