import os
import csv
from collections import defaultdict
from src.config import STATISTICS_DIR, NIVELES

def calculate_accuracy(answers, solutions):
    """Calculate accuracy between answers and solutions."""
    if not answers or not solutions:
        return None
    # Filter out empty answers and solutions
    valid_pairs = [(a, s) for a, s in zip(answers, solutions) if a and s]
    if not valid_pairs:
        return None
    correct = sum(1 for a, s in valid_pairs if a == s)
    return (correct / len(valid_pairs) * 100)

def generate_concise_statistics(answers_csv, solutions_csv):
    """Generate concise statistics comparing answers with solutions."""
    os.makedirs(STATISTICS_DIR, exist_ok=True)
    
    # Load answers and solutions
    answers_by_year = defaultdict(lambda: defaultdict(dict))
    solutions_by_year = defaultdict(lambda: defaultdict(dict))
    
    # Read answers and solutions
    for csv_file, target_dict in [(answers_csv, answers_by_year), (solutions_csv, solutions_by_year)]:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                year = row['anio']
                for nivel in NIVELES:
                    nivel_num = nivel[-1]
                    if row[f'nivel{nivel_num}']:
                        target_dict[year][nivel][row['question_number']] = row[f'nivel{nivel_num}']
    
    # Generate statistics
    output_path = os.path.join(STATISTICS_DIR, "statistics.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("PRIMAVERA EXAM STATISTICS\n")
        f.write("=" * 30 + "\n\n")
        
        # Calculate and display average accuracy by level across all years
        total_accuracy_by_nivel = defaultdict(list)
        for year in sorted(answers_by_year.keys()):
            for nivel in NIVELES:
                answers = [answers_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                solutions = [solutions_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                accuracy = calculate_accuracy(answers, solutions)
                if accuracy is not None:
                    total_accuracy_by_nivel[nivel].append(accuracy)
        
        f.write("AVERAGE ACCURACY BY LEVEL\n")
        f.write("-" * 25 + "\n")
        for nivel in NIVELES:
            accuracies = [acc for acc in total_accuracy_by_nivel[nivel] if acc is not None]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                f.write(f"{nivel.upper()}: {avg_accuracy:.2f}%\n")
            else:
                f.write(f"{nivel.upper()}: No data available\n")
        
        # Display accuracy by year and level
        f.write("\nACCURACY BY YEAR AND LEVEL\n")
        f.write("-" * 25 + "\n")
        for year in sorted(answers_by_year.keys()):
            f.write(f"\n{year}:\n")
            year_has_data = False
            for nivel in NIVELES:
                answers = [answers_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                solutions = [solutions_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                accuracy = calculate_accuracy(answers, solutions)
                if accuracy is not None:
                    year_has_data = True
                    f.write(f"{nivel.upper()}: {accuracy:.2f}%\n")
                else:
                    f.write(f"{nivel.upper()}: No data available\n")
            if not year_has_data:
                f.write("No valid data for this year\n")
    
    print(f"Statistics have been saved to {output_path}")
    return output_path

def generate_detailed_statistics(answers_csv, solutions_csv):
    """Generate detailed statistics with incorrect answers."""
    os.makedirs(STATISTICS_DIR, exist_ok=True)
    
    # Load answers and solutions
    answers_by_year = defaultdict(lambda: defaultdict(dict))
    solutions_by_year = defaultdict(lambda: defaultdict(dict))
    
    # Read answers and solutions
    for csv_file, target_dict in [(answers_csv, answers_by_year), (solutions_csv, solutions_by_year)]:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                year = row['anio']
                for nivel in NIVELES:
                    nivel_num = nivel[-1]
                    if row[f'nivel{nivel_num}']:
                        target_dict[year][nivel][row['question_number']] = row[f'nivel{nivel_num}']
    
    # Generate statistics
    output_path = os.path.join(STATISTICS_DIR, "detailed_statistics.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("PRIMAVERA EXAM DETAILED STATISTICS\n")
        f.write("=" * 50 + "\n\n")
        
        total_accuracy_by_nivel = defaultdict(list)
        years_with_data = 0
        
        # Process each year
        for year in sorted(answers_by_year.keys()):
            f.write(f"\nYear {year}\n")
            f.write("-" * 20 + "\n")
            
            year_accuracies = []
            year_has_data = False
            
            for nivel in NIVELES:
                answers = [answers_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                solutions = [solutions_by_year[year][nivel].get(str(q), '') for q in range(1, 26)]
                accuracy = calculate_accuracy(answers, solutions)
                
                f.write(f"{nivel.upper()}:\n")
                if accuracy is not None:
                    year_has_data = True
                    year_accuracies.append(accuracy)
                    total_accuracy_by_nivel[nivel].append(accuracy)
                    f.write(f"Accuracy: {accuracy:.2f}%\n")
                    
                    # Show incorrect answers
                    incorrect = []
                    for q in range(1, 26):
                        ans = answers_by_year[year][nivel].get(str(q), '')
                        sol = solutions_by_year[year][nivel].get(str(q), '')
                        if ans and sol and ans != sol:
                            incorrect.append(f"Q{q}: {ans} (correct: {sol})")
                    
                    if incorrect:
                        f.write("Incorrect answers:\n")
                        for inc in incorrect:
                            f.write(f"  {inc}\n")
                else:
                    f.write("No data available\n")
                f.write("\n")
            
            if year_has_data:
                years_with_data += 1
                avg_year_accuracy = sum(year_accuracies) / len(year_accuracies)
                f.write(f"Average year accuracy: {avg_year_accuracy:.2f}%\n")
            else:
                f.write("No valid data for this year\n")
        
        # Overall statistics
        f.write("\nOVERALL STATISTICS\n")
        f.write("=" * 50 + "\n")
        f.write(f"Years with valid data: {years_with_data}\n\n")
        
        f.write("Average accuracy by level:\n")
        for nivel in NIVELES:
            accuracies = [acc for acc in total_accuracy_by_nivel[nivel] if acc is not None]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                f.write(f"{nivel.upper()}: {avg_accuracy:.2f}%\n")
            else:
                f.write(f"{nivel.upper()}: No data available\n")
        
        # Calculate global accuracy only for valid data
        all_accuracies = [acc for accs in total_accuracy_by_nivel.values() for acc in accs if acc is not None]
        if all_accuracies:
            global_accuracy = sum(all_accuracies) / len(all_accuracies)
            f.write(f"\nGlobal accuracy across all years and levels: {global_accuracy:.2f}%\n")
        else:
            f.write("\nNo valid data to calculate global accuracy\n")
    
    print(f"Detailed statistics have been saved to {output_path}")
    return output_path

def generate_statistics(answers_csv, solutions_csv):
    generate_concise_statistics(answers_csv, solutions_csv)
    generate_detailed_statistics(answers_csv, solutions_csv)
