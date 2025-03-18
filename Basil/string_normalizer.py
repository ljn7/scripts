import re
from typing import Dict

class TextProcessor:
    def __init__(self):
        # Basic number mappings
        self.ordinals = {
            0: "zeroth",
            1: "first",
            2: "second",
            3: "third",
            4: "fourth",
            5: "fifth",
            6: "sixth",
            7: "seventh",
            8: "eighth",
            9: "ninth",
            10: "tenth",
            11: "eleventh",
            12: "twelfth",
            13: "thirteenth",
            14: "fourteenth",
            15: "fifteenth",
            16: "sixteenth",
            17: "seventeenth",
            18: "eighteenth",
            19: "nineteenth",
            20: "twentieth",
            30: "thirtieth",
            40: "fortieth",
            50: "fiftieth",
            60: "sixtieth",
            70: "seventieth",
            80: "eightieth",
            90: "ninetieth",
        }
        self.units = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
            11: "eleven",
            12: "twelve",
            13: "thirteen",
            14: "fourteen",
            15: "fifteen",
            16: "sixteen",
            17: "seventeen",
            18: "eighteen",
            19: "nineteen",
        }

        self.tens = {
            2: "twenty",
            3: "thirty",
            4: "forty",
            5: "fifty",
            6: "sixty",
            7: "seventy",
            8: "eighty",
            9: "ninety",
        }

        # Indian numbering system scales
        self.scales = {
            "crore": 10000000,
            "lakh": 100000,
            "thousand": 1000,
            "hundred": 100,
        }

        # Currency symbols
        self.currency_symbols = {
            "Rs": "Rupees",
            "Rs.": "Rupees",
            "₹": "Rupees",
            "$": "Dollars",
            "€": "Euros",
            "£": "Pounds",
        }

        # Symbols to convert to words
        self.symbols = {
            "%": "percent",
            "@": "at",
            "&": "and",
            "+": "plus",
            "=": "equals",
            "/": "per",
            "#": "number",
            "*": "asterisk",
            "°": "degrees",
            "§": "section",
            "¶": "paragraph",
            "©": "copyright",
            "®": "registered",
            "™": "trademark",
            "~": "approximately",
            "^": "power",
            "<": "less than",
            ">": "greater than",
            "≤": "less than or equal to",
            "≥": "greater than or equal to",
            "±": "plus or minus",
            "≈": "approximately equal to",
            "≠": "not equal to",
            "∞": "infinity",
        }

        # Letter-number prefix mappings
        self.letter_prefixes = {
            "Q": "Quarter",
            "P": "Phase",
            "V": "Version",
            "Ch": "Chapter",
            "Fig": "Figure",
            "Sec": "Section",
            "App": "Appendix",
            "Vol": "Volume",
            "Pg": "Page",
            "Rev": "Revision",
            "ID": "ID",
            "No": "Number",
            "Ref": "Reference",
            "Table": "Table",
            "Type": "Type",
            "Level": "Level",
            "Grade": "Grade",
            "Stage": "Stage",
            "Step": "Step",
            "Part": "Part",
        }

        self.measurement_units = {
            "°C": "degrees celsius",
            "°F": "degrees fahrenheit",
            "m": "metres",
            "cm": "centimetres",
            "mm": "millimetres",
            "km": "kilometres",
            "g": "grams",
            "kg": "kilograms",
            "mg": "milligrams",
            "l": "litres",
            "ml": "millilitres",
            "B": "bytes",
            "KB": "kilobytes",
            "MB": "megabytes",
            "GB": "gigabytes",
            "TB": "terabytes",
            "Hz": "hertz",
            "kHz": "kilohertz",
            "MHz": "megahertz",
            "GHz": "gigahertz",
            "m²": "square metres",
            "cm²": "square centimetres",
            "mm²": "square millimetres",
        }

        # Modified abbreviations: note the addition of the specific pattern for "Govt.of"
        self.abbreviations = {
            r"\bMr\.?(?=\s|$|[,;:])": "Mister",
            r"\bMrs\.?(?=\s|$|[,;:])": "Misses",
            r"\bMs\.?(?=\s|$|[,;:])": "Miss",
            r"\bDr\.?(?=\s|$|[,;:])": "Doctor",
            r"\bProf\.?(?=\s|$|[,;:])": "Professor",
            r"\bHon'ble\.?(?=\s|$|[,;:])": "Honourable",
            r"\bSr\.?(?=\s|$|[,;:])": "Senior",
            r"\bJr\.?(?=\s|$|[,;:])": "Junior",
            r"\bSt\.?(?=\s|$|[,;:])": "Saint",
            r"\bRev\.?(?=\s|$|[,;:])": "Reverend",
            r"\bFr\.?(?=\s|$|[,;:])": "Father",
            r"\bSmt\.?(?=\s|$|[,;:])": "Srimati",
            r"\bSh\.?(?=\s|$|[,;:])": "Shri",
            r"\bEr\.?(?=\s|$|[,;:])": "Engineer",
            r"\bAr\.?(?=\s|$|[,;:])": "Architect",
            r"\bCol\.?(?=\s|$|[,;:])": "Colonel",
            r"\bGen\.?(?=\s|$|[,;:])": "General",
            r"\bCapt\.?(?=\s|$|[,;:])": "Captain",
            r"\bMaj\.?(?=\s|$|[,;:])": "Major",
            r"\bLt\.?(?=\s|$|[,;:])": "Lieutenant",
            r"\bSgt\.?(?=\s|$|[,;:])": "Sergeant",
            # Specific pattern for Govt.of (no whitespace between the dot and 'of')
            r"\bGovt\.?of": "Government of",
            r"\bGovt\.?(?=\s|\b)": "Government",
            r"\bDept\.(?=\s|\b)": "Department",
            r"\bOrg\.(?=\s|\b)": "Organization",
            r"\bUniv\.(?=\s|\b)": "University",
            r"\bLtd\.(?=\s|\b)": "Limited",
            r"\bPvt\.(?=\s|\b)": "Private",
            r"\bDist\.(?=\s|\b)": "District",
            r"\bHwy\.(?=\s|\b)": "Highway",
            r"\bAve\.(?=\s|\b)": "Avenue",
            r"\bRd\.(?=\s|\b)": "Road",
            r"\bInc\.(?=\s|\b)": "Incorporated",
            r"\bCo\.(?=\s|\b)": "Company",
            r"\bBros\.(?=\s|\b)": "Brothers",
            r"\bEst\.(?=\s|\b)": "Established",
            r"\bMfg\.(?=\s|\b)": "Manufacturing",
            r"\bRegd\.(?=\s|\b)": "Registered",
            r"\bNo\.(?=\s|\b)": "Number",
            r"\bJan\.(?=\s|\b)": "January",
            r"\bFeb\.(?=\s|\b)": "February",
            r"\bMar\.(?=\s|\b)": "March",
            r"\bApr\.(?=\s|\b)": "April",
            r"\bJun\.(?=\s|\b)": "June",
            r"\bJul\.(?=\s|\b)": "July",
            r"\bAug\.(?=\s|\b)": "August",
            r"\bSept\.(?=\s|\b)": "September",
            r"\bOct\.(?=\s|\b)": "October",
            r"\bNov\.(?=\s|\b)": "November",
            r"\bDec\.(?=\s|\b)": "December",
        }

        self.number_lookup = self._generate_lookup_table()

    def _roman_to_int(self, roman: str) -> int:
        """
        Convert a Roman numeral string to its integer value.
        """
        roman = roman.upper()
        roman_map = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        total = 0
        prev_value = 0
        for char in reversed(roman):
            value = roman_map.get(char, 0)
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value
        return total

    def _handle_roman_numeral(self, match: re.Match) -> str:
        roman_str = match.group(0)
        text = match.string
        start = match.start()

        # If the token is not fully uppercase, assume it is a name or word and return it unchanged.
        if roman_str != roman_str.upper():
            return roman_str

        # Check for a valid Roman numeral using a well-known regex.
        valid_roman_pattern = (
            r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
        )
        if not re.match(valid_roman_pattern, roman_str.upper()):
            # If the numeral is invalid, return it unchanged.
            return roman_str

        # Define a set of titles that indicate a regnal or papal name.
        titles = {
            "King",
            "Queen",
            "Pope",
            "Emperor",
            "Empress",
            "Czar",
            "Cardinal",
            "Bishop",
            "Saint",
            "Patriarch",
            "Caliph",
            "Sheikh",
            "Khan",
            "Sultan",
            "Rajah",
            "Maharaja",
            "Maharani",
        }

        # Get the immediate surrounding words.
        preceding_text = text[:start].strip()
        preceding_words = preceding_text.split()
        after_text = text[match.end() :].strip()
        after_words = after_text.split()

        # Special handling for the token "I".
        if roman_str.upper() == "I":
            # If there's no title context (or if it's clearly used as a pronoun), return "I" unchanged.
            if not (
                preceding_words and any(word in titles for word in preceding_words)
            ):
                return roman_str

        # For a one-letter token...
        if len(roman_str) == 1:
            if (after_words and len(after_words[0]) == 1) or (
                preceding_words and len(preceding_words[-1]) == 1
            ):
                return roman_str
            if preceding_words and any(word in titles for word in preceding_words):
                number = self._roman_to_int(roman_str)
                return self._process_ordinal(number)
            number = self._roman_to_int(roman_str)
            return self._process_number(number)

        # For tokens longer than one letter, if a title is present, convert ordinally.
        if preceding_words and any(word in titles for word in preceding_words):
            number = self._roman_to_int(roman_str)
            return self._process_ordinal(number)

        # Default: convert as a cardinal number.
        number = self._roman_to_int(roman_str)
        return self._process_number(number)

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

    def _handle_abbreviations(self, text: str) -> str:
        """Normalize common abbreviations."""
        for pattern, replacement in self.abbreviations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _handle_numeric_ordinal(self, match: re.Match) -> str:
        """Convert numeric ordinals (e.g., 1st, 2nd, 3rd) to ordinal words explicitly."""
        number = int(match.group(1))
        return self._process_ordinal(number)

    def _handle_measurement_units(self, match: re.Match) -> str:
        """Convert numeric measurement units to words explicitly."""
        number_str = match.group(1)
        unit = match.group(2)

        sign_word = ""
        if number_str.startswith("-"):
            sign_word = "minus "
            number_str = number_str[1:]
        elif number_str.startswith("+"):
            sign_word = "plus "
            number_str = number_str[1:]
        else:
            sign_word = ""

        if "." in number_str:
            number_word = self._handle_decimal(number_str)
        else:
            number_word = self._process_number(int(number_str))

        unit_word = self.measurement_units.get(unit, unit)
        return f"{sign_word}{number_word} {unit_word}".strip()

    def _process_number(self, num: int, is_ordinal=False) -> str:
        """Convert number to words using Indian numbering system."""
        if num == 0:
            return self.units[0] if not is_ordinal else self.ordinals[0]

        parts = []
        remaining = num
        for scale, value in sorted(self.scales.items(), key=lambda x: -x[1]):
            if remaining >= value:
                count = remaining // value
                remaining %= value
                if count > 0:
                    part = f"{self._process_number(count)} {scale}"
                    parts.append(part)

        if remaining > 0:
            parts.append(self._process_smaller_number(remaining))

        result = " ".join(parts)

        if is_ordinal:
            return self._process_ordinal(num)
        return result

    def _process_scale_ordinal(self, word: str) -> str:
        """Convert scale words to their ordinal forms explicitly."""
        scale_ordinals = {
            "hundred": "hundredth",
            "thousand": "thousandth",
            "lakh": "lakh",
            "crore": "crore",
        }
        return scale_ordinals.get(word, word + "th")

    def _process_ordinal_word(self, word: str) -> str:
        """Convert a word to its ordinal form."""
        ordinal_exceptions = {
            "one": "first",
            "two": "second",
            "three": "third",
            "four": "fourth",
            "five": "fifth",
            "six": "sixth",
            "seven": "seventh",
            "eight": "eighth",
            "nine": "ninth",
            "ten": "tenth",
            "twenty": "twentieth",
            "thirty": "thirtieth",
            "forty": "fortieth",
            "fifty": "fiftieth",
            "sixty": "sixtieth",
            "seventy": "seventieth",
            "eighty": "eightieth",
            "ninety": "ninetieth",
        }
        if word in ordinal_exceptions:
            return ordinal_exceptions[word]
        if "-" in word:  # handles compound words like "twenty-one"
            tens, ones = word.split("-")
            return f"{tens}-{ordinal_exceptions.get(ones, ones + 'th')}"
        return word + "th"

    def _process_ordinal(self, num: int) -> str:
        """Convert number to its ordinal representation correctly."""
        if num in self.ordinals:
            return self.ordinals[num]
        parts = []
        remaining = num
        for scale, value in sorted(self.scales.items(), key=lambda x: -x[1]):
            if remaining >= value:
                count = remaining // value
                remaining %= value
                if count > 0:
                    if remaining == 0:
                        scale_word = self._process_scale_ordinal(scale)
                        part = f"{self._process_number(count)} {scale_word}"
                    else:
                        part = f"{self._process_number(count)} {scale}"
                parts.append(part)
        if remaining > 0:
            if remaining in self.ordinals:
                parts.append(self.ordinals[remaining])
            else:
                cardinal = self._process_smaller_number(remaining)
                parts.append(self._process_ordinal_word(cardinal))
        return " ".join(parts)

    def _process_smaller_number(self, num: int) -> str:
        """Process numbers under 100."""
        return self.number_lookup[num]

    def _handle_decimal(self, num_str: str) -> str:
        """Handle decimal numbers."""
        try:
            integer_part, decimal_part = num_str.split(".")
            integer_words = self._process_number(int(integer_part))
            decimal_words = " ".join(self.units[int(d)] for d in decimal_part)
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
            decimal = match.group(3) if match.group(3) else ""
            full_prefix = self.letter_prefixes.get(prefix, prefix)
            if decimal:
                number_word = self._handle_decimal(f"{number}{decimal}")
            else:
                number_word = self._process_number(int(number))
            return f"{full_prefix} {number_word}"

        prefix_pattern = "|".join(map(re.escape, self.letter_prefixes.keys()))
        pattern = rf"({prefix_pattern}|[A-Z])(\d+)(\.?\d*)"
        return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)

    def process_text(self, text: str) -> str:
        """Main method to process text containing numbers and symbols."""
        # Remove commas and hyphens from the text
        text = text.replace(",", "").replace("-", " ")
        # Handle known abbreviations explicitly
        text = self._handle_abbreviations(text)
        # Process letter-number combinations first
        text = self._process_letter_number_combination(text)
        # Process percentages
        text = re.sub(r"(\d+(?:\.\d+)?)\s*%", self._handle_percentage, text)
        # Process numeric ordinals explicitly (e.g., 1st, 2nd, 3rd, 4th...)
        text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", self._handle_numeric_ordinal, text)
        # Process measurement units explicitly (e.g., 5°C, 10m, 20cm...)
        unit_pattern = r"([+-]?\d+(?:\.\d+)?)\s*(%s)\b" % "|".join(
            map(re.escape, self.measurement_units.keys())
        )
        text = re.sub(unit_pattern, self._handle_measurement_units, text)
        # Process Roman numerals
        text = re.sub(r"\b[IVXLCDMivxlcdm]+\b", self._handle_roman_numeral, text)
        # Process other symbols
        for symbol, word in self.symbols.items():
            if symbol != "%":  # Skip % as it's already handled
                text = text.replace(symbol, f" {word} ")

        def process_match(match: re.Match) -> str:
            full_match = match.group(0)
            # Handle year ranges
            year_range_pattern = r"(\d{4})-(\d{2})"
            if re.match(year_range_pattern, full_match):
                return self._process_year_range(match)
            # Handle currency
            currency_pattern = r"(Rs\.|₹|\$|€|£)\s*(\d+(?:\.\d+)?)"
            currency_match = re.match(currency_pattern, full_match)
            if currency_match:
                return self._handle_currency(
                    currency_match.group(2), currency_match.group(1)
                )
            # Handle regular numbers and years
            num_pattern = r"(\d+(?:\.\d+)?)(?:\s*(AD|BC|CE|BCE))?"
            num_match = re.match(num_pattern, full_match)
            if num_match:
                num = num_match.group(1)
                suffix = num_match.group(2) or ""
                if "." in num:
                    return f"{self._handle_decimal(num)} {suffix}".strip()
                else:
                    return f"{self._process_number(int(num))} {suffix}".strip()
            return full_match

        # Process numbers and currencies
        pattern = r"(?:Rs\.|₹|\$|€|£)\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?(?:\s*(?:AD|BC|CE|BCE))?|\d{4}-\d{2}"
        text = re.sub(pattern, process_match, text)
        # Clean up extra spaces
        return " ".join(text.split())
