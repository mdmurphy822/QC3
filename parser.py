from docx import Document
import os
import re

def parse_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text(path, filename):
    ext = os.path.splitext(filename)[-1].lower()
    if ext == ".docx":
        return parse_docx(path)
    elif ext == ".txt":
        return parse_txt(path)
    else:
        return ""

def extract_questions(raw_text):
    pattern = r'\n?\d+\..*?(?=\n\d+\.|\Z)'
    return re.findall(pattern, raw_text, re.DOTALL)

def format_question_block(question_text, index):
    lines = question_text.strip().split("\n")
    question_line = lines[0]
    options = lines[1:]
    formatted = []
    formatted.append("//MULTIPLE CHOICE QUESTION TYPE")
    formatted.append("//Options must include text in column3")
    formatted.append("NewQuestion\tMC")
    formatted.append("ID\t")
    formatted.append("Title\t")
    formatted.append(f"QuestionText\t{question_line.strip()}")
    formatted.append("Points\t1")
    formatted.append("Difficulty\t1")
    formatted.append("Image\t")
    for opt in options:
        weight = "0"
        if "*" in opt or "(correct)" in opt.lower():
            weight = "100"
        opt_clean = opt.replace("*", "").replace("(correct)", "").strip()
        formatted.append(f"Option\t{weight}\t{opt_clean}")
    formatted.append("Hint\t")
    formatted.append("Feedback\t")
    return "\n".join(formatted)

def parse_quiz_file(path, filename):
    raw_text = extract_text(path, filename)
    questions = extract_questions(raw_text)
    output_blocks = [format_question_block(q, idx) for idx, q in enumerate(questions, 1)]
    return "\n\n".join(output_blocks)
