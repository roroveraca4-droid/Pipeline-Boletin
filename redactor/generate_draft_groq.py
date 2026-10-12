import os
import sys
import glob
from datetime import datetime
from groq import Groq

# 1. Configuración de Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")

# Nuevas rutas para los archivos de reglas en la carpeta redactor/
SKILL_FILE = os.path.join(BASE_DIR, "SKILL_REDACTOR.md")
EDITORIAL_FILE = os.path.join(BASE_DIR, "EDITORIAL_RULES.md")
DESIGN_FILE = os.path.join(BASE_DIR, "DESIGN_GUIDELINES.md")

os.makedirs(DRAFTS_DIR, exist_ok=True)

GROQ_API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    print("❌ Error: Falta la GROQ_API_KEY.")
    sys.exit(1)

def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Cargar las instrucciones y reglas actualizadas
skill_instructions = read_file(SKILL_FILE)
editorial_rules = read_file(EDITORIAL_FILE)
design_guidelines = read_file(DESIGN_FILE)

source_files = glob.glob(os.path.join(SOURCES_DIR, "*.md"))
if not source_files:
    print("❌ Error: No se encontraron archivos de fuentes en sources/")
    sys.exit(1)

combined_sources = ""
for file_path in source_files:
    file_name = os.path.basename(file_path)
    content = read_file(file_path)
    combined_sources += f"\n\n--- FUENTE: {file_name} ---\n\n{content}"

# Separación de Prompt de Sistema y Usuario
system_prompt = f"""
Eres el Editor Jefe de un boletín sobre Inteligencia Artificial para profesionales corporativos en Latinoamérica.

INSTRUCCIONES PRINCIPALES (SKILL):
{skill_instructions}

REGLAS EDITORIALES Y DE TONO:
{editorial_rules}

REGLAS DE DISEÑO Y FORMATO:
{design_guidelines}
"""

user_prompt = f"""
INFORMACIÓN EXTRAÍDA DE LAS FUENTES:
{combined_sources}

TAREA:
Sintetiza las fuentes y redacta la edición de hoy del boletín en formato Markdown siguiendo estrictamente las reglas editoriales (estilo Morning Brew) y de diseño del sistema.
"""

print("⚡ Generando borrador con Groq (Llama 3 70B)...")

try:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="llama3-70b-8192", # <--- Actualizado al modelo correcto
        temperature=0.4, 
    )

    draft_content = completion.choices[0].message.content

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"draft_{date_str}.md"
    output_path = os.path.join(DRAF
