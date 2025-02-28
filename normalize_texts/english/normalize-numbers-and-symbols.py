import re
from typing import Dict, Optional

class TextProcessor:
    def __init__(self):
        # Basic number mappings
        self.units = {
            0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
            6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
            11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
            15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
            19: 'nineteen'
        }
        
        self.tens = {
            2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty',
            6: 'sixty', 7: 'seventy', 8: 'eighty', 9: 'ninety'
        }
        
        # Indian numbering system scales
        self.scales = {
            'crore': 10000000,
            'lakh': 100000,
            'thousand': 1000,
            'hundred': 100
        }
        
        # Currency symbols
        self.currency_symbols = {
            'Rs': 'Rupees',
            '₹': 'Rupees',
            '$': 'Dollars',
            '€': 'Euros',
            '£': 'Pounds'
        }
        
        # Symbols to convert to words
        self.symbols = {
            '%': 'percent',
            '@': 'at',
            '&': 'and',
            '+': 'plus',
            '=': 'equals',
            '/': 'per',
            '#': 'number',
            '*': 'asterisk',
            '°': 'degrees',
            '§': 'section',
            '¶': 'paragraph',
            '©': 'copyright',
            '®': 'registered',
            '™': 'trademark'
        }
        
        # Letter-number prefix mappings
        self.letter_prefixes = {
            'Q': 'Quarter',
            'P': 'Phase',
            'V': 'Version',
            'Ch': 'Chapter',
            'Fig': 'Figure',
            'Sec': 'Section',
            'App': 'Appendix',
            'Vol': 'Volume',
            'Pg': 'Page',
            'Rev': 'Revision',
            'ID': 'ID',
            'No': 'Number',
            'Ref': 'Reference',
            'Table': 'Table',
            'Type': 'Type',
            'Level': 'Level',
            'Grade': 'Grade',
            'Stage': 'Stage',
            'Step': 'Step',
            'Part': 'Part'
        }
        
        self.number_lookup = self._generate_lookup_table()

    def _generate_lookup_table(self) -> Dict[int, str]:
        """Generate a lookup table for numbers 1-99."""
        lookup = {}
        for i in range(100):
            if i < 20:
                lookup[i] = self.units[i]
            else:
                tens_digit = i // 10
                ones_digit = i % 10
                if ones_digit == 0:
                    lookup[i] = self.tens[tens_digit]
                else:
                    lookup[i] = f"{self.tens[tens_digit]}-{self.units[ones_digit]}"
        return lookup

    def _process_number(self, num: int) -> str:
        """Convert number to words using Indian numbering system."""
        if num == 0:
            return self.units[0]

        parts = []
        remaining = num

        for scale, value in self.scales.items():
            if remaining >= value:
                count = remaining // value
                remaining %= value
                if count > 0:
                    parts.append(f"{self._process_smaller_number(count)} {scale}")

        if remaining > 0:
            parts.append(self._process_smaller_number(remaining))

        return ', '.join(parts)

    def _process_smaller_number(self, num: int) -> str:
        """Process numbers under 100."""
        return self.number_lookup[num]

    def _handle_decimal(self, num_str: str) -> str:
        """Handle decimal numbers."""
        try:
            integer_part, decimal_part = num_str.split('.')
            integer_words = self._process_number(int(integer_part))
            decimal_words = ' '.join(self.units[int(d)] for d in decimal_part)
            return f"{integer_words} point {decimal_words}"
        except ValueError:
            return self._process_number(int(num_str))

    def _process_year_range(self, match: re.Match) -> str:
        """Handle year ranges like 2024-25."""
        full_year = match.group(1)
        short_year = match.group(2)
        
        century = full_year[:2]
        decade = full_year[2:]
        first_year = f"twenty {self.number_lookup[int(decade)]}"
        second_year = f"twenty {self.number_lookup[int(short_year)]}"
        
        return f"{first_year}-{second_year}"

    def _handle_currency(self, amount: str, symbol: str) -> str:
        """Handle currency amounts."""
        currency_name = self.currency_symbols.get(symbol, symbol)
        amount_in_words = self.process_text(amount)
        return f"{currency_name} {amount_in_words}"

    def _handle_percentage(self, match: re.Match) -> str:
        """Handle percentage values."""
        number = match.group(1)
        processed_number = self.process_text(number)
        return f"{processed_number} percent"

    def _process_letter_number_combination(self, text: str) -> str:
        """Handle combinations of letters and numbers."""
        def replace_match(match):
            prefix = match.group(1)
            number = match.group(2)
            decimal = match.group(3) if match.group(3) else ''
            
            full_prefix = self.letter_prefixes.get(prefix, prefix)
            
            if decimal:
                number_word = self._handle_decimal(f"{number}{decimal}")
            else:
                number_word = self._process_number(int(number))
            
            return f"{full_prefix} {number_word}"

        prefix_pattern = '|'.join(map(re.escape, self.letter_prefixes.keys()))
        pattern = rf'({prefix_pattern}|[A-Z])(\d+)(\.?\d*)'
        
        return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)

    def process_text(self, text: str) -> str:
        """Main method to process text containing numbers and symbols."""
        # Process letter-number combinations first
        text = self._process_letter_number_combination(text)
        
        # Process percentages
        text = re.sub(r'(\d+(?:\.\d+)?)\s*%', self._handle_percentage, text)
        
        # Process other symbols
        for symbol, word in self.symbols.items():
            if symbol != '%':  # Skip % as it's already handled
                text = text.replace(symbol, f" {word} ")
        
        def process_match(match: re.Match) -> str:
            full_match = match.group(0)
            
            # Handle year ranges
            year_range_pattern = r'(\d{4})-(\d{2})'
            if re.search(year_range_pattern, full_match):
                return re.sub(year_range_pattern, self._process_year_range, full_match)
            
            # Handle currency
            currency_pattern = r'(Rs|₹|\$|€|£)\s*(\d+(?:\.\d+)?)'
            currency_match = re.match(currency_pattern, full_match)
            if currency_match:
                return self._handle_currency(currency_match.group(2), currency_match.group(1))
            
            # Handle regular numbers and years
            num_pattern = r'(\d+(?:\.\d+)?)\s*(AD|BC|CE|BCE)?'
            num_match = re.match(num_pattern, full_match)
            if num_match:
                num = num_match.group(1)
                suffix = num_match.group(2) or ''
                
                if '.' in num:
                    return f"{self._handle_decimal(num)} {suffix}".strip()
                else:
                    return f"{self._process_number(int(num))} {suffix}".strip()
            
            return full_match

        # Process numbers and currencies
        pattern = r'(?:Rs|₹|\$|€|£)\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?(?:\s*(?:AD|BC|CE|BCE))?|\d{4}-\d{2}'
        text = re.sub(pattern, process_match, text)
        
        # Clean up extra spaces
        return ' '.join(text.split())

def main():
    processor = TextProcessor()
    
    test_cases = [
        "The overall budget allocation for the development of Scheduled Tribes has risen from Rs 10237.33 crore in 2024-25 to Rs 14925.81 crore in 2025-26",
        "Growth rate was 15% in Q1 & 17.5% in Q2",
        "Please contact support@company.com",
        "Temperature increased by 2.5° & humidity by 5%",
        "A&B Enterprises made $1525.75 @ their store",
        "Score: 95/100 = 95%",
        "Upgrade from V1.0 to V2.1 is complete",
        "See Fig1 and Fig2 in Ch3",
        "Phase P1 & P2 are complete",
        "Table5 shows data from ID123"
    ]

    for test in test_cases:
        print(f"Original: {test}")
        print(f"Processed: {processor.process_text(test)}\n")

if __name__ == "__main__":
    main()