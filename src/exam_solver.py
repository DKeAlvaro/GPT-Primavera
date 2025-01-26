import io
from PIL import Image
import base64
import requests
import fitz
import csv
import os
import json
import re
from src.config import CURR_YEAR, TEST_PATHS, OPENAI_API_KEY, SOLUTIONS_DIR, ANSWERS_DIR, NIVELES, EXAMS_DIR
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def process_pdf_page(pdf_path, page_number):
    try:
        base64_image = get_pdf_page(pdf_path, page_number)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Return a dictionary question number -> answer (A, B, C, D, E) for each question in the image, nothing else, no formatting, no quotation marks. If there are no questions in the image, return None."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content, response.usage.prompt_tokens, response.usage.completion_tokens
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, 0, 0
    
def clean_response_to_json(response):
    """Convert the GPT response to valid JSON."""
    try:
        # Remove any whitespace and newlines
        response = response.replace(" ", "").replace("\n", "")
        
        # If it's already valid JSON, return it
        try:
            return json.loads(response)
        except:
            pass
            
        # Extract the dictionary content (remove outer braces temporarily)
        response = response.strip("{}")
        
        # Split into key-value pairs
        pairs = response.split(",")
        
        # Format each pair properly
        formatted_pairs = []
        for pair in pairs:
            key, value = pair.split(":")
            formatted_pairs.append(f'"{key.strip()}":"{value.strip()}"')
        
        # Reconstruct the JSON string
        json_str = "{" + ",".join(formatted_pairs) + "}"
        
        return json.loads(json_str)
        
    except Exception as e:
        print(f"Error cleaning response: {str(e)}")
        print(f"Original response: {response}")
        return None
    
def get_year_answers(year):
    """Process all exams for a given year and create a combined answers file."""
    answers_dict = {}  # Dictionary to store answers by question number
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Process each nivel
    for nivel in NIVELES:
        nivel_num = nivel[-1]  # Extract number from nivel string
        pdf_path = os.path.join(EXAMS_DIR, str(year), f"{nivel}_fase2.pdf")
        
        if not os.path.exists(pdf_path):
            print(f"No exam found for {year} {nivel}")
            continue
            
        print(f"\nProcessing {year} {nivel}...")
        
        # Process each page of the exam
        pdf_document = fitz.open(pdf_path)
        for page_number in range(len(pdf_document)):
            # Get image dimensions
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap(dpi=300)
            width, height = pix.width, pix.height
            
            # Process page
            result, prompt_tokens, completion_tokens = process_pdf_page(pdf_path, page_number)
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            
            print(f"Page {page_number + 1} result:", result)

            if result and result.lower() != "none":
                page_answers = clean_response_to_json(result)
                if page_answers:
                    # Create or update answer rows
                    for question_num, answer in page_answers.items():
                        if question_num not in answers_dict:
                            answers_dict[question_num] = {
                                'question_number': str(question_num),
                                'nivel1': '',
                                'nivel2': '',
                                'nivel3': '',
                                'nivel4': '',
                                'fase': '2',  # Hardcoded as we're only processing fase 2
                                'anio': str(year),
                                'image_width': width,
                                'image_height': height,
                                'page_number': str(page_number + 1)  # Adding page number (1-indexed)
                            }
                        # Update the specific nivel's answer
                        answers_dict[question_num][f'nivel{nivel_num}'] = answer
                else:
                    print(f"Failed to parse answers for {nivel} page {page_number}")
    
    if not answers_dict:
        print(f"No answers found for year {year}")
        return None
    
    # Convert dictionary to sorted list of answers
    all_answers = list(answers_dict.values())
    all_answers.sort(key=lambda x: int(x['question_number']))
    
    # Add total tokens to all rows
    for answer in all_answers:
        answer['prompt_tokens'] = total_prompt_tokens
        answer['completion_tokens'] = total_completion_tokens
    
    # Create output directory if it doesn't exist
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    
    # Save all answers to CSV
    output_path = os.path.join(ANSWERS_DIR, f"respuestas_{year}.csv")
    fieldnames = ['question_number', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'fase', 'anio', 
                 'image_width', 'image_height', 'page_number', 'prompt_tokens', 'completion_tokens']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_answers)
    
    print(f"\nSuccessfully created {output_path}")
    print(f"Total tokens used - Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}")
    return output_path

def get_exam_answers(pdf_path):
    """Process a single exam PDF and create its answers file."""
    # Extract year and nivel from path
    match = re.search(r'\\(\d{4})\\nivel(\d)_fase(\d)', pdf_path)
    if not match:
        print(f"Error: Could not extract year and level from path: {pdf_path}")
        return
    
    year, nivel, fase = match.groups()
    answers = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    # Process each page
    pdf_document = fitz.open(pdf_path)
    for page_number in range(len(pdf_document)):
        # Get image dimensions
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap(dpi=300)
        width, height = pix.width, pix.height
        
        # Process page
        result, prompt_tokens, completion_tokens = process_pdf_page(pdf_path, page_number)
        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens
        
        print(f"Page {page_number + 1} result:", result)

        if result and result.lower() != "none":
            page_answers = clean_response_to_json(result)
            if page_answers:
                # Create answer rows
                for question_num, answer in page_answers.items():
                    answer_row = {
                        'question_number': str(question_num),
                        'nivel1': answer if nivel == '1' else '',
                        'nivel2': answer if nivel == '2' else '',
                        'nivel3': answer if nivel == '3' else '',
                        'nivel4': answer if nivel == '4' else '',
                        'fase': fase,
                        'anio': year,
                        'image_width': width,
                        'image_height': height,
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens
                    }
                    answers.append(answer_row)
            else:
                print(f"Failed to parse answers for page {page_number}")
    
    if not answers:
        print(f"No answers found in {pdf_path}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    
    # Save answers to CSV
    output_path = os.path.join(ANSWERS_DIR, f"respuestas_{year}_nivel{nivel}_fase{fase}.csv")
    fieldnames = ['question_number', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'fase', 'anio', 
                 'image_width', 'image_height', 'prompt_tokens', 'completion_tokens']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(answers)
    
    print(f"Successfully created {output_path}")
    print(f"Total tokens used - Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}")
    return output_path

def merge_answers():
    """Merge all year answer CSV files into a single CSV file."""
    all_answers = []
    fieldnames = ['question_number', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'fase', 'anio', 
                 'image_width', 'image_height', 'page_number', 'prompt_tokens', 'completion_tokens']
    
    # Iterate through all CSV files in the answers directory
    for year in range(2002, CURR_YEAR):
        csv_path = os.path.join(ANSWERS_DIR, f"respuestas_{year}.csv")
        if os.path.exists(csv_path):
            print(f"Processing answers from {year}...")
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_answers.extend(list(reader))
        else:
            print(f"No answers found for {year}")
    
    if not all_answers:
        print("No answer files found!")
        return None
        
    # Sort by year and question number
    all_answers.sort(key=lambda x: (int(x['anio']), int(x['question_number'])))
    
    # Save merged answers to CSV
    output_path = os.path.join(ANSWERS_DIR, "respuestas_all.csv")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_answers)
    
    print(f"\nSuccessfully created {output_path}")
    print(f"Total answers: {len(all_answers)}")
    return output_path

def get_pdf_page(pdf_path, page_number):
    pdf_document = fitz.open(pdf_path)    
    page = pdf_document.load_page(page_number)
    pix = page.get_pixmap(dpi=300)
    image_bytes = pix.tobytes("png")
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    return base64_image


def test_images_from_pdf(test_paths, page_number):
    for path in test_paths:
        base64_image = get_pdf_page(path, page_number)
        image_bytes = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_bytes))
        print(f"Image dimensions: {image.size[0]}x{image.size[1]} pixels")
        image.show()
        print(process_pdf_page(path, page_number))
    
def solve_all_exams():

    for year in range(2002, CURR_YEAR):
        get_year_answers(year)
    
if __name__ == "__main__":
    test_images_from_pdf(TEST_PATHS, 0)