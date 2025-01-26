# GPT-Primavera

![Topics](https://img.shields.io/badge/Topics-AI%20|%20Education%20|%20Mathematics%20|%20PDF%20Processing%20|%20Automation-blue)


<p align="center">
  <img src="logo.png?v=2" alt="GPT-Primavera Logo" width="200"/>
</p>

An automated solver for Concurso Primavera mathematics exams using GPT models. This project downloads exam papers from concursoprimavera.es, processes them, and solves them using OpenAI's GPT models.

## Demo

https://github.com/user-attachments/assets/29a7f3ca-f3e6-4b95-b0d5-444be4a1904c

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
3. Generate statistics
