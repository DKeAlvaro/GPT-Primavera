import fitz
import csv
import os
import re
from src.config import CURR_YEAR, FASES, SOLUTIONS_DIR

def get_solutions_csv(pdf_path, fase=None):
    try:
        # Extract year from pdf path using regex
        year_match = re.search(r'\\(\d{4})\\', pdf_path)
        if not year_match:
            print(f"Warning: Could not extract year from pdf path: {pdf_path}")
            return None
        year = year_match.group(1)
        
        # If fase not provided, try to extract it from filename (e.g., soluciones_fase2.pdf)
        if fase is None:
            fase_match = re.search(r'fase(\d)', pdf_path)
            if fase_match:
                fase = int(fase_match.group(1))
            else:
                fase = "unknown"

        doc = fitz.open(pdf_path)
        solutions = []
        
        for page in doc:
            tabs = page.find_tables()
            if not tabs.tables:
                continue
                
            for tab in tabs:
                table_data = tab.extract()
                
                # Verify table structure
                if len(table_data) < 2 or len(table_data[0]) != 8:
                    print(f"Warning: Unexpected table structure in page {page.number + 1}")
                    continue
                    
                # Check headers
                headers = table_data[0]
                if not (headers[0] == 'Nivel I' and headers[2] == 'Nivel II' and 
                       headers[4] == 'Nivel III' and headers[6] == 'Nivel IV'):
                    print(f"Warning: Unexpected format in {pdf_path}")
                    continue
                
                # Extract solutions row by row
                for row in table_data[1:]:
                    if len(row) != 8:  # Skip incomplete rows
                        continue
                    # Get question number from first column
                    question_number = row[0]
                    solutions.append({
                        'question_number': question_number,
                        'nivel1': row[1],
                        'nivel2': row[3],
                        'nivel3': row[5],
                        'nivel4': row[7],
                        'fase': fase,
                        'anio': year
                    })
        
        if not solutions:
            print(f"Warning: No valid solutions found in {pdf_path}")
            return None
        
        print(f"Successfully parsed solutions for {year} fase {fase}")
            
        # Create CSV in the same directory as PDF
        csv_name = f'soluciones_{year}_fase{fase}.csv'
        csv_path = os.path.join(os.path.dirname(pdf_path), csv_name)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['question_number', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'fase', 'anio'])
            writer.writeheader()
            writer.writerows(solutions)
        
        return csv_path
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None
    
def merge_solutions_csv():
    solutions = []
    for year in range(2002, CURR_YEAR):
        year_dir = os.path.join(SOLUTIONS_DIR, str(year))
        if not os.path.exists(year_dir):
            continue
            
        for file in os.listdir(year_dir):
            if file.startswith("soluciones_") and file.endswith(".csv"):
                csv_path = os.path.join(year_dir, file)
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Fix any potential encoding issues in existing files
                        if 'año' in row:
                            row['anio'] = row.pop('año')
                        elif 'aï¿½o' in row:
                            row['anio'] = row.pop('aï¿½o')
                        solutions.append(row)
                print(f"Added solutions from {csv_path}")

    if not solutions:
        print("No solutions found in any year!")
        return

    output_path = os.path.join(SOLUTIONS_DIR, "soluciones_all.csv")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question_number', 'nivel1', 'nivel2', 'nivel3', 'nivel4', 'fase', 'anio'])
        writer.writeheader()
        writer.writerows(solutions)
    print(f"Successfully merged all solutions into {output_path}")

if __name__ == "__main__":
    pass


