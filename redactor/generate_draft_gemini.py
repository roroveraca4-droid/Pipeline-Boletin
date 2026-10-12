import os
import sys
import glob
from datetime import datetime
from google import genai
from google.genai import types

# 1. Configuración de Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")

SKILL_FILE = os.path.join(BASE_DIR, "SKILL_REDACTOR.md")
EDITORIAL_FILE = os.path.join(BASE_DIR, "EDITORIAL_RULES.md")
DESIGN_FILE = os.path.join(BASE_DIR, "DESIGN_GUIDELINES.md")

os.makedirs(DRAFTS_DIR, exist_ok=True)

# 2. Configuración de API Key
GEMINI_API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("❌ Error: Falta la GEMINI_API_KEY.")
    sys.exit(1)

# Inicializar el NUEVO cliente de Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

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

# 3. Preparar Prompts
system_instruction = f"""
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

print("⚡ Generando borrador con el nuevo SDK de Gemini...")

try:
    # 4. Llamada a Gemini usando el nuevo formato
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4,
        ),
    )
    
    draft_content = response.text

    # 5. Guardar el archivo
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"draft_{date_str}.md"
    output_path = os.path.join(DRAFTS_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(draft_content)

    print(f"✅ Borrador generado exitosamente en: drafts/{output_filename}")

except Exception as e:
    print(f"❌ Error al consultar la API de Gemini: {e}")
    sys.exit(1)
