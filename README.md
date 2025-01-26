# GPT-Primavera

<p align="center">
  <img src="logo.jpg" alt="GPT-Primavera Logo" width="200"/>
</p>

An automated solver for Concurso Primavera mathematics exams using GPT models. This project downloads exam papers from concursoprimavera.es, processes them, and solves them using OpenAI's GPT models.

## What it does

1. Downloads exam papers from concursoprimavera.es
2. Processes them
3. Solves them using OpenAI's GPT models
4. Generates statistics by comparing the answers with the solutions

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GPT-Primavera.git
cd GPT-Primavera
```

2. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY="your_api_key_here" (with quotes)
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You can change the GPT model by modifying the `MODEL` variable in `src/config.py`

## Usage

Run the main script to process and solve all exams:
```bash
python main.py
```

This will:
1. Download exam papers and solutions
2. Process and solve the exams
3. Generate statistics and comparisons

## Directory Structure

- `examenes/`: Downloaded exam papers
- `soluciones/`: Exam solutions
- `respuestas/`: Generated answers
- `estadisticas/`: Statistical analysis
- `src/`: Source code

