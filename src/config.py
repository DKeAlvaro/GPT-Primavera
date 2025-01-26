DOWNLOAD_URL = "https://www.concursoprimavera.es/php/download.php"
MAIN_URL = "https://www.concursoprimavera.es"
NIVELES = ["nivel1", "nivel2", "nivel3", "nivel4"]
FASE = 2
CURR_YEAR = 2024 
EXAMS_DIR = "examenes"
SOLUTIONS_DIR = "soluciones"
STATISTICS_DIR = "estadisticas"
ANSWERS_DIR = "respuestas"
PRINT_FLAG = True
TEST_PATHS = [
    r"examenes\2002\nivel4_fase2.pdf", # Double column page
    r"examenes\2002\nivel3_fase2.pdf"
]
from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


