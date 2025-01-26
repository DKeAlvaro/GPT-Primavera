import os
import requests
from src.config import DOWNLOAD_URL, MAIN_URL, NIVELES, FASE, CURR_YEAR, EXAMS_DIR, SOLUTIONS_DIR
from src.solution_reader import get_solutions_csv

def get_file_url(year, fase, nivel):
    payload = {
        "problemas": "1",
        "year": year,
        "fase": fase,
        "nivel": nivel
    }

    with requests.Session() as s:
        s.headers.update({
            "Referer": DOWNLOAD_URL
        })
        response = s.post(DOWNLOAD_URL, data=payload)

        if response.status_code == 200:
            try:
                response_json = response.json()
                href = response_json.get("href")
                if href:
                    return f"{MAIN_URL}{href}"
                else:
                    return None 
            except requests.exceptions.JSONDecodeError:
                return None
        else:
            return None

def make_directories():    
    os.makedirs(EXAMS_DIR, exist_ok=True)
    os.makedirs(SOLUTIONS_DIR, exist_ok=True)
    
    # Create year folders from 2002 to 2024
    for year in range(2002, CURR_YEAR):
        os.makedirs(os.path.join(EXAMS_DIR, str(year)), exist_ok=True)
        os.makedirs(os.path.join(SOLUTIONS_DIR, str(year)), exist_ok=True)

def download_exams(print_flag=False):
    exam_years = sorted([int(f) for f in os.listdir(EXAMS_DIR) if f.isdigit()])
    for year in exam_years:
        custom_print(f"\nYear {year}:", print_flag)
        for nivel in NIVELES:
            url = get_file_url(year, FASE, nivel)
            custom_print(f"  {nivel}: {url}", print_flag)
            if url:
                download_file(url, os.path.join(EXAMS_DIR, str(year), f"{nivel}_fase{FASE}.pdf"))

def download_solutions(print_flag=False):
    exam_years = sorted([int(f) for f in os.listdir(EXAMS_DIR) if f.isdigit()])
    for year in exam_years:
        url = get_file_url(year, FASE, "soluciones")
        if url:
            pdf_path = os.path.join(SOLUTIONS_DIR, str(year), f"soluciones_fase{FASE}.pdf")
            download_file(url, pdf_path)
            get_solutions_csv(pdf_path)

        else:
            custom_print(f"No solutions found for year {year}", print_flag)

def download_file(url, path):
    with requests.Session() as s:
        s.headers.update({
            "Referer": DOWNLOAD_URL
        })

        try:
            response = s.get(url, stream=True)
            response.raise_for_status()

            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False
    
def custom_print(content, print_flag=True):
    if print_flag:
        print(content)

