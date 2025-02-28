import re

def normalize_text(text):
    mappings = {
        'ं([कखगघ])': r'ङ्\1',
        'ं([चछजझ])': r'ञ्\1',
        'ं([टठडढण])': r'ण्\1',
        'ं([तथदधन])': r'न्\1',
        'ं([पफबभम])': r'म्\1',
    }

    for pattern, replacement in mappings.items():
        text = re.sub(pattern, replacement, text)

    return text

# Example usage:
content = "कंप, बंब, संभाजी"


output_file = "output.txt"

# Read, normalize, and save the text
# with open(input_file, "r", encoding="utf-8") as infile:
#    content = infile.read()

normalized_content = normalize_text(content)

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write(normalized_content)

print(f"Normalized text saved to {output_file}")
