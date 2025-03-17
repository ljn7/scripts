import unicodedata
import pandas as pd
import logging
import grapheme


LANGUAGE = {
    'hindi': 3,
    'marathi': 4,
    'gujarati': 5,
    'odia': 6,
    'bengali': 7
}

MAPPING = {
    'cls': 1,
    'ipa': 2
}

logging.basicConfig(level=logging.INFO)


def load_mapping_table(mapping_file, mapping_sheet_name, language='marathi', mapping_type='cls'):
    """
    Load the mapping table from Excel file
    """
    try:
        # Explicitly specify Sheet1 for mapping
        df = pd.read_excel(mapping_file, sheet_name=mapping_sheet_name, header=None)
        source_chars = df.iloc[:, MAPPING[mapping_type]]
        target_chars = df.iloc[:, LANGUAGE[language]]
        
        mapping_dict = {}
        for src, tgt in zip(source_chars, target_chars):
            if pd.notna(src) and pd.notna(tgt) and src != '-' and tgt != '-':
                mapping_dict[tgt] = src
                
        logging.info(f"Loaded {len(mapping_dict)} valid mappings from Sheet1")
        return mapping_dict
    except Exception as e:
        logging.error(f"Error loading mapping file Sheet1: {e}")
        raise

def process_text(text, char_mapping):
    """
    Process text and count character occurrences
    """
    # Replace spaces with underscores
    text = text.replace(' ', '_')  # Replace spaces with underscores
    text = unicodedata.normalize("NFC", text)  # Normalize text

    result = []
    char_counts = {}
    mapped_characters = set()

    # Iterate over graphemes instead of individual characters
    for g_cluster in grapheme.graphemes(text):
        if g_cluster == '_':
            result.append('_')
        elif g_cluster in char_mapping:
            mapped_char = char_mapping[g_cluster]
            result.append(mapped_char)
            # Track mapped character and count
            char_counts[mapped_char] = char_counts.get(mapped_char, 0) + 1
            mapped_characters.add(g_cluster)  # Store original grapheme
        else:
            result.append(g_cluster)  # Keep unmapped graphemes unchanged

    # Convert character counts to string format (e.g., "ax:2, k:1")
    char_counts_str = ', '.join(f"{char}:{count}" for char, count in char_counts.items())
    # Store mapped characters as a comma-separated string (e.g., "कि, गे")
    mapped_chars_str = ', '.join(grapheme.graphemes(''.join(mapped_characters)))

    return ' '.join(result), char_counts_str, mapped_chars_str

def process_file(input_file, mapping_file, input_sheet_name, mapping_sheet_name, output_file, language, column_index=1):
    """
    Process entire file using mapping table and track character counts
    """
    try:
        char_mapping = load_mapping_table(mapping_file, mapping_sheet_name, language)
        char_counts = {}
        
        # Read from TestSet sheet
        df = pd.read_excel(input_file, sheet_name=input_sheet_name, header=None)
        
        processed_data = df.iloc[:, column_index].apply(
            lambda x: process_text(str(x), char_mapping)
        )

        df['processed_text'], df['char_counts'], df['mapped_characters'] = zip(*processed_data)

        # # Process specified column
        # df['processed_text'] = df.iloc[:, column_index].apply(
        #     lambda x: process_text(str(x), char_mapping, char_counts)
        # )
        
        # Save to new Excel file with processed text
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='ProcessedTestSet', index=False, header=False)
        
        # # Save character counts
        # sorted_counts = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
        
        # logging.info("\nCharacter occurrences:")
        # with open(f'char_counts_{language}.txt', 'w', encoding='utf-8') as f:
        #     for char, count in sorted_counts:
        #         log_line = f"{char} -> {count} times"
        #         logging.info(log_line)
        #         f.write(log_line + '\n')
                
        logging.info(f"\nProcessed text saved to '{output_file}' in sheet 'ProcessedTestSet'")
        # logging.info(f"Character counts saved to char_counts_{language}.txt")
        
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise

if __name__ == "__main__":
    print("Please make sure that the input file is in the same directory as this script")
    print("This program converts Hindi/Marathi text to CLS text")
    print("Enter the following details:")
    language = input("Enter the language (hindi/marathi): ")
    mapping_file = input("Enter the mapping file name without an extension: ") + ".xlsx"  # Changed extension
    mapping_sheet_name = input("Enter the mapping sheet name: ")
    input_file = input("Enter the input file name without an extension (.xlsx): ") + ".xlsx"  # Changed extension
    input_sheet_name = input("Enter the input sheet name: ")
    output_file = input("Enter the output file name without an extension (.xlsx): ") + "_" + language + ".xlsx"  # Changed extension
    column_index = int(input("Enter the column index of input file to process: "))
    
    process_file(input_file, mapping_file, input_sheet_name, mapping_sheet_name, output_file, language, column_index)