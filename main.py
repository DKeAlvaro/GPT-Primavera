from src.exam_converter import convert_all_exams
from src.file_downloader import download_exams, download_solutions, make_directories
from src.solution_reader import merge_solutions_csv
from src.config import PRINT_FLAG

if __name__ == "__main__":
    # make_directories()
    # download_exams(print_flag=PRINT_FLAG)
    # download_solutions(print_flag=PRINT_FLAG)
    # merge_solutions_csv()
    
    convert_all_exams("examenes")
