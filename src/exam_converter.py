import os
import fitz
import json
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def convert_exam(file_path, output_path=None):
    """
    Convierte un PDF de examen a JSON usando Gemini-3-flash (SDK google-genai).
    
    :param file_path: Ruta al archivo PDF.
    :param output_path: (Opcional) Ruta donde guardar el archivo .json resultante.
    :return: Lista de diccionarios con las preguntas.
    """
    
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Abrir PDF con PyMuPDF
    print(f"Procesando PDF: {file_path}...")
    doc = fitz.open(file_path)
    total_pages = len(doc)
    
    full_exam_data = []

    prompt = """
    Analiza esta imagen de un examen en español. Extrae todas las preguntas de opción múltiple 
    y devuélvelas en un formato JSON estructurado.
    
    Reglas:
    1. Si hay ecuaciones matemáticas o símbolos científicos, represéntalos fielmente (usa LaTeX si es necesario).
    2. Si la página no contiene preguntas, devuelve: {"preguntas": []}.
    3. Mapea las opciones a: option_a, option_b, option_c, option_d, option_e.
    4. Si una opción no existe, pon null.
    5. Identifica si la pregunta requiere una imagen del PDF (ej. un gráfico, figuras geométricas, tablas visuales) para ser respondida.
       - requires_image: true si el contenido visual es indispensable, false si es solo texto.
       - image_description: Si requires_image es true, intenta describir la imagen detalladamente en texto (ej. "Un triángulo rectángulo con lados A y B"). Si no hay imagen, pon null.
    
    Esquema:
    {
      "preguntas": [
        {
          "q_number": number,
          "question": "texto",
          "requires_image": boolean,
          "image_description": "texto descriptivo o null",
          "option_a": "texto",
          "option_b": "texto",
          "option_c": "texto",
          "option_d": "texto",
          "option_e": "texto o null"
        }
      ]
    }
    """

    for i in range(total_pages):
        print(f"Analizando página {i+1}/{total_pages}...")
        
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("jpeg")

        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
            ],
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        print("--- DEBUG: Respuesta Cruda ---")
        print(response.text)
        print("-------------------------------")

        try:
            page_json = json.loads(response.text)
            full_exam_data.extend(page_json.get('preguntas', []))
        except json.JSONDecodeError:
            print(f"Error en formato JSON en página {i+1}. Saltando...")
            print("--- Respuesta cruda de la IA (JSON inválido) ---")
            print(response.text)
            print("------------------------------------------------")

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(full_exam_data, f, indent=4, ensure_ascii=False)
        print(f"Proceso completado. Archivo guardado en: {output_path}")

    return full_exam_data

def convert_all_exams(base_dir="examenes"):
    """
    Busca recursivamente todos los PDFs en base_dir y los convierte a JSON.
    """
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                json_path = os.path.splitext(pdf_path)[0] + ".json"
                
                if not os.path.exists(json_path):
                    print(f"\nConversión necesaria para: {pdf_path}")
                    try:
                        convert_exam(pdf_path, output_path=json_path)
                    except Exception as e:
                        print(f"Error procesando {pdf_path}: {e}")
                else:
                    print(f"Saltando {pdf_path}, el JSON ya existe.")

if __name__ == "__main__":
    convert_all_exams("examenes")