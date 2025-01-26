from src.generate_statistics import generate_statistics
from src.exam_solver import merge_answers, solve_all_exams
from src.solution_reader import merge_solutions_csv
from src.file_downloader import download_exams, download_solutions, make_directories
from src.config import PRINT_FLAG

if __name__ == "__main__":
    make_directories()
    download_exams(print_flag=PRINT_FLAG)
    download_solutions(print_flag=PRINT_FLAG)
    merge_solutions_csv()
    solve_all_exams()
    merge_answers()
    generate_statistics("respuestas/respuestas_all.csv", "soluciones/soluciones_all.csv")
    

