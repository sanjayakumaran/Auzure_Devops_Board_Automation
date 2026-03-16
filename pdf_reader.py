import re
import fitz

def pdf_reader(path):
    return fitz.open(file_path)

def extract_parent_name(text):
    pattern = r"Partner Security Bulletin:\s*(.*?\d{4})"

    match = re.search(pattern, text, re.S)

    if match:
        result = match.group(1).strip()
        result = result.replace("\n", " ")
        return result

    return None

def extract_all_text_without_watermark(pdf):
    clean_text = []
    for page in pdf:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if abs(line["dir"][1]) > 0.1:
                        continue
                    clean_text.append(span["text"].replace("\u200b", ""))
    return "\n".join(clean_text)


def extract_clean_table(page, tabs):

    tab = tabs[0]
    table_data = []

    for row_obj in tab.rows:
        current_row = []
        for cell_bbox in row_obj.cells:
            if cell_bbox is None:
                current_row.append("")
                continue

            cell_dict = page.get_text("dict", clip=cell_bbox)
            cell_text_parts = []

            for block in cell_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if abs(line["dir"][1]) > 0.1:
                            continue

                        for span in line["spans"]:
                            cell_text_parts.append(span["text"])

            # Join parts and clean up whitespace
            clean_cell_content = " ".join(cell_text_parts).strip()
            clean_cell_content=clean_cell_content.replace("\u200b", "")
            current_row.append(clean_cell_content)

        table_data.append(current_row)

    return table_data

def find_table(pdf, header_text="Severity"):
    header_text = "\u200b"+header_text+"\u200b"
    clean_table = []
    for page in pdf:
        tables = page.find_tables()
        for table in tables:
            data = table.extract()
            header = data[0]
            if header_text in header:
                clean_table = extract_clean_table(page, tables)
    return clean_table

def table_dict(table):
    dict = {}
    for row in range(1, len(table)):
        value = {}
        for col in range(1, len(table[row])):
            k = table[0][col]
            v = table[row][col]
            value[k] = v
        key = table[row][0]
        dict[key] = value
    return dict

file_path = input("Enter PDF file path: ")

pdf = pdf_reader(file_path)

entire_text = extract_all_text_without_watermark(pdf)
parent_name = extract_parent_name(entire_text)
print("parent_name:", parent_name, "\n")
table = find_table(pdf)
feature_dict = table_dict(table)

for key, value in feature_dict.items():
    print(f"{key}:")
    print("{")
    for k, v in value.items():
        print(f"{k}: {v}")
    print("}\n")
