import pandas as pd
import xml.etree.ElementTree as ET
import fire
import os
from datetime import datetime
from xml.dom import minidom  

def convert_to_xml(input_file: str, output_file: str = None):
    """
    Converts an Excel file with UID, Reference, Hypothesis, and WER columns to a pretty-indented XML file.
    Skips metric/footer rows.
    
    Args:
        input_file (str): Path to the input .xlsx file.
        output_file (str, optional): Output XML file path. If not provided, it's generated automatically.
    """
    # Load Excel
    df = pd.read_excel(input_file)

    df = df[df["UID"].notna() & df["Reference"].notna() & df["Hypothesis"].notna()]

    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{base_name}_output_{timestamp}.xml"

    root = ET.Element("transcript")

    for _, row in df.iterrows():
        uid = str(row["UID"]).strip()

        if uid.lower() in ["metric", "overall wer", "language code", "value"]:
            continue

        reference = str(row["Reference"]).strip()
        hypothesis = str(row["Hypothesis"]).strip()
        wer = str(row["WER"]).strip()

        row_elem = ET.SubElement(root, "row")

        hyp_elem = ET.SubElement(row_elem, "hypothesis", isEdited="0")
        hyp_elem.text = hypothesis

        ref_elem = ET.SubElement(row_elem, "words", isEdited="0")
        ref_elem.text = reference

        audio_elem = ET.SubElement(row_elem, "audio-filename")
        audio_elem.text = f"{uid}.wav"

        tag_elem = ET.SubElement(row_elem, "tag", isEdited="0")
        tag_elem.text = ""

        comment_elem = ET.SubElement(row_elem, "comments", isEdited="0")
        comment_elem.text = ""

        wer_elem = ET.SubElement(row_elem, "wer")
        wer_elem.text = wer

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="\t")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✅ Indented XML written to: {output_file}")

if __name__ == "__main__":
    fire.Fire(convert_to_xml)
