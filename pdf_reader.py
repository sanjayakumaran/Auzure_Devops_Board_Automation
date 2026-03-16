import re
import fitz

def pdf_reader(path):
    return fitz.open(file_path)

def read_pages(pdf):
    pages_list = []
    for page in pdf:
        text = page.get_text()
        text = text.replace("\u200b", "")
        pages_list.append(text)
    return pages_list

def extract_parent_name(text):
    pattern = r"Partner Security Bulletin:\s*(.*?\d{4})"

    match = re.search(pattern, text, re.S)

    if match:
        result = match.group(1).strip()
        result = result.replace("\n", " ")
        return result

    return None

def extract_cve_id(text):
    pattern = r"CVE-\d{4}-\d+"
    key = re.findall(pattern, text)
    return key[0]

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

def extract_text_without_watermark(page):
    clean_text = set()
    blocks = page.get_text("dict")["blocks"]

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if abs(line["dir"][1]) > 0.1:
                    continue
                text = span["text"].replace("\u200b", "")
                text_list = text.split(" ")
                for i in text_list:
                    clean_text.add(i)
    return clean_text

def extract_tables(pdf):
    clean_table = []
    for page in pdf:
        tables = page.find_tables()
        for table in tables:
            data = table.extract()
            header = data[0]
            if "\u200bVector\u200b" in header:
                valid_text = extract_text_without_watermark(page)
                for row in data:
                    cleaned_row = []
                    for cell in row:
                        cell = cell.replace("\u200b", "")
                        words = cell.split()
                        filtered_words = [w for w in words if w in valid_text]
                        cleaned_row.append(" ".join(filtered_words))
                    clean_table.append(cleaned_row)
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
        key = extract_cve_id(key)
        dict[key] = value
    return dict

file_path = input("Enter PDF file path: ")

pdf = pdf_reader(file_path)
page_list = read_pages(pdf)

entire_text = extract_all_text_without_watermark(pdf)
parent_name = extract_parent_name(entire_text)
print("parent_name:", parent_name, "\n")
table = extract_tables(pdf)
feature_dict = table_dict(table)

for key, value in feature_dict.items():
    print(f"{key}:")
    print("{")
    for k, v in value.items():
        print(f"{k}: {v}")
    print("}\n")
