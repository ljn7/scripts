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
            'Ref': 'Reference'
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
        # "The overall budget allocation for the development of Scheduled Tribes has risen from Rs 10237.33 crore in 2024-25 to Rs 14925.81 crore in 2025-26",
        # "Growth rate was 15% in Q1 & 17.5% in Q2",
        # "Please contact support@company.com",
        # "Temperature increased by 2.5° & humidity by 5%",
        # "A&B Enterprises made $1525.75 @ their store",
        # "Score: 95/100 = 95%",
        # "Upgrade from V1.0 to V2.1 is complete",
        # "See Fig1 and Fig2 in Ch3",
        # "Phase P1 & P2 are complete",
        # "Table5 shows data from ID123"
        """
        Recognising the need to create an enabling environment whereby Higher Educational Institutions (HEIs) can become institutions of global excellence, autonomy is pivotal to promote and institutionalize excellence in higher education. The regulatory framework has recognized this need and towards this direction, the UGC (Categorisation of Universities (Only) for Grant of Graded Autonomy) Regulations, 2018 have been notified on 12th February, 2018. These regulations are aimed to provide autonomy to the HEIs based on quality benchmarks.   Under these Regulations, Universities having NAAC scrore of 3.51 or above or those who have received a corresponding score/grade from a reputed accreditation agency empanelled by the UGC or have been ranked among top 500 of reputed world rankings are placed in Category-I. Universities having NAAC score of 3.26 and above, upto 3.50 or have received a corresponding accreditation grade/score from a reputed Accreditation Agency empanelled by the UGC are placed in Category-II. The Universities which do not come under the above two categories are placed in Category-III.   Category I & II Universities may hire foreign faculty, without approval of the Commission, who have taught at an institution appearing in top five hundred of any of the world renowned ranking frameworks such as the Times Higher Education World University Rankings or QS  Rankings upto 20% of over and above of their total sanctioned faculty strength. Universities will have the freedom to hire foreign faculty on “tenure/contract” basis as per the terms and conditions approved by their Governing Council/Statutory bodies. Since the recruitment of foreign faculty is over and above the sanctioned strength of an Institution, the implementation of the reservation policy of the Government in teaching positions will not be disturbed.   This information was given by the Minister of State (HRD), Dr. Satya Pal Singh today in a written reply to a Lok Sabha question.

        The draft Higher Education Commission of India Bill, 2018 has been put in public domain on 27.06.2018 for seeking comments and suggestions from educationists, stakeholders and general public before 20.07.2018. As on 19.07.2018, the Ministry has received 9,926 suggestions/comments covering Members of Parliament, State Governments, academicians, teacher unions, Chambers of Commerce, students etc. and appropriate changes are being made in the draft Bill based on the public feedback. The Government has taken several major initiatives in the Higher Education Sector during the last two years. Substantive changes have been made in the basic regulations of the University Grants Commission (UGC). With a view to provide autonomy, promote quality and create an enabling environment whereby Higher Educational Institutions can become institutions of global excellence, UGC has taken several initiatives in the form of Regulations i.e. (i)UGC (Minimum Standards and Procedure for Award of M.PHIL./PH.D Degrees) Regulations, 2016,(ii)UGC (Open and Distance Learning) Regulations, 2017; (iii) UGC (Promotion and Maintenance of Standards of Academic Collaboration between Indian and Foreign Educational Institutions) Regulations, 2016; (iv) UGC (Institutions of Eminence Deemed to be Universities) Regulations, 2017;(v) UGC (Categorization of Universities (only) for Grant of Graded Autonomy) Regulations, 2018 and (vi) the UGC (Conferment of Autonomous Status upon Colleges and Measures for Maintenance of Standards in Autonomous colleges) Regulations, 2018. The Government has also undertaken reforms in National Assessment and Accreditation Council (NAAC). Further, the Government has established an online storehouse of academic awards (degrees, diplomas, certificates, mark-sheets etc.) namely National Academic Depository (NAD) for making available academic awards 24x7 in online mode. 

        """
    ]

    for test in test_cases:
        print(f"Original: {test}")
        print(f"Processed: {processor.process_text(test)}\n")

if __name__ == "__main__":
    main()