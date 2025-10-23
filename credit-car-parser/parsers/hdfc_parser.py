from .base_parser import BaseParser
import re

class HDFCParser(BaseParser):
    def parse(self):
        self.extract_text()
        
        return {
            'bank': 'HDFC Bank',
            'card_last_4_digits': self.extract_card_number(),
            'statement_date': self.extract_statement_date(),
            'payment_due_date': self.extract_due_date(),
            'total_amount_due': self.extract_total_due(),
            'minimum_amount_due': self.extract_minimum_due()
        }
    
    def extract_card_number(self):
        # HDFC format: "4695 25XX XXXX 3458" or "Card No: 4695 25XX XXXX 3458"
        match = re.search(r'(\d{4})\s*\d*X+\s*X+\s*(\d{4})', self.text)
        if match:
            return match.group(2)
        
        return "Not Found"
    
    def extract_statement_date(self):
        # Multiple strategies for different formats
        
        # Strategy 1: "Statement Date:12/03/2023" or "Statement Date: 12/03/2023"
        match = re.search(r'Statement\s+Date\s*:\s*(\d{2}/\d{2}/\d{4})', self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Strategy 2: Look for date pattern near "Statement Date" text
        match = re.search(r'Statement\s+Date[:\s]*(\d{2}/\d{2}/\d{4})', self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Strategy 3: In compact format - date might be right before/after "Statement"
        # Pattern: "12/03/2023" somewhere in first part of document
        dates = re.findall(r'(\d{2}/\d{2}/\d{4})', self.text[:500])
        if dates:
            # Usually first or second date is statement date
            return dates[0]
        
        return "Not Found"
    
    def extract_due_date(self):
        # HDFC format: "Payment Due Date" followed by "01/04/2023"
        # In the structured format, it appears as second date
        lines = self.text.split('\n')
        
        # Strategy 1: Look for explicit label
        for i, line in enumerate(lines):
            if 'Payment Due Date' in line:
                # Check same line and next lines
                for j in range(i, min(i + 3, len(lines))):
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', lines[j])
                    if date_match:
                        return date_match.group(1)
        
        # Strategy 2: In structured format, due date is usually second date after statement date
        dates = re.findall(r'(\d{2}/\d{2}/\d{4})', self.text)
        if len(dates) >= 2:
            # Usually dates[0] is statement date, dates[1] is due date
            return dates[1]
        
        return "Not Found"
    
    def extract_total_due(self):
        # Strategy 1: Look for "Total Dues" with amount
        match = re.search(r'Total\s+Dues[:\s]*([\d,]+\.00)', self.text, re.IGNORECASE)
        if match:
            return self.clean_amount(match.group(1))
        
        # Strategy 2: In the compact format, look for pattern after dates
        # Format: "12/03/202301/04/2023 38,935.008,935.00..." or "01/04/2023 22,935.00 22,935.00"
        # After the two dates, first large amount is total dues
        match = re.search(r'\d{2}/\d{2}/\d{4}\s*\d{2}/\d{2}/\d{4}\s*([\d,]+\.00)', self.text)
        if match:
            amount = self.clean_amount(match.group(1))
            try:
                if float(amount) > 100:  # Reasonable threshold
                    return amount
            except:
                pass
        
        # Strategy 3: Look for "Total Dues" in Account Summary section
        match = re.search(r'Total\s+Dues.*?([\d,]+\.00)', self.text, re.IGNORECASE | re.DOTALL)
        if match:
            return self.clean_amount(match.group(1))
        
        # Strategy 4: Find reasonable amounts in first 1000 chars
        amounts = re.findall(r'([\d,]+\.00)', self.text[:1000])
        for amt in amounts:
            cleaned = self.clean_amount(amt)
            try:
                val = float(cleaned)
                # Total dues typically between 1000 and 100000
                if 500 < val < 100000:
                    return cleaned
            except:
                pass
        
        return "Not Found"
    
    def extract_minimum_due(self):
        # Strategy 1: Look for "Minimum Amount Due" with amount
        match = re.search(r'Minimum\s+Amount\s+Due[:\s]*([\d,]+\.00)', self.text, re.IGNORECASE)
        if match:
            return self.clean_amount(match.group(1))
        
        # Strategy 2: In compact format after dates and total due
        # Format: "01/04/2023 22,935.00 22,935.00" (due_date total_due min_due)
        # Or: "01/04/2023 38,935.008,935.00" (concatenated)
        match = re.search(r'\d{2}/\d{2}/\d{4}\s*([\d,]+\.00)\s*([\d,]+\.00)', self.text)
        if match:
            # Second amount is usually minimum due
            return self.clean_amount(match.group(2))
        
        # Strategy 3: Sometimes amounts are concatenated like "38,935.008,935.00"
        match = re.search(r'([\d,]+\.00)([\d,]+\.00)', self.text[:1000])
        if match:
            # Second amount in pair is often minimum due
            amt1 = self.clean_amount(match.group(1))
            amt2 = self.clean_amount(match.group(2))
            try:
                val1 = float(amt1)
                val2 = float(amt2)
                # Minimum is usually smaller than or equal to total
                if val2 <= val1 and val2 > 100:
                    return amt2
                # Unless they're the same (full payment required)
                elif val1 == val2:
                    return amt2
            except:
                pass
        
        # Strategy 4: Look in table structure
        match = re.search(r'Minimum\s+Amount\s+Due.*?([\d,]+\.00)', self.text, re.IGNORECASE | re.DOTALL)
        if match:
            return self.clean_amount(match.group(1))
        
        # Strategy 5: Get total due and look for smaller amount nearby
        total_str = self.extract_total_due()
        if total_str != "Not Found":
            try:
                total_val = float(total_str)
                amounts = re.findall(r'([\d,]+\.00)', self.text[:1000])
                for amt in amounts:
                    cleaned = self.clean_amount(amt)
                    try:
                        val = float(cleaned)
                        # Minimum is between 5% and 100% of total
                        if val <= total_val and val >= (total_val * 0.05):
                            return cleaned
                    except:
                        pass
            except:
                pass
        
        return "Not Found"