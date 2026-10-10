import os
import sys
import glob
from datetime import datetime
from groq import Groq

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")
SKILL_FILE = os.path.join(BASE_DIR, "SKILL_REDACTOR.md")
TONO_FILE = os.path.join(PROJECT_ROOT, "TONO_DE_VOZ.md")

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

skill_instructions = read_file(SKILL_FILE)
tone_instructions = read_file(TONO_FILE)

source_files = glob.glob(os.path.join(SOURCES_DIR, "*.md"))
if not source_files:
    print("❌ Error: No se encontraron archivos de fuentes en sources/")
    sys.exit(1)

combined_sources = ""
for file_path in source_files:
    file_name = os.path.basename(file_path)
    content = read_file(file_path)
    combined_sources += f"\n\n--- FUENTE: {file_name} ---\n\n{content}"

prompt = f"""
INSTRUCCIONES DE REDACCIÓN:
{skill_instructions}

GUÍA DE TONO Y VOZ:
{tone_instructions}

INFORMACIÓN EXTRAÍDA DE LAS FUENTES:
{combined_sources}

TAREA:
Sintetiza las fuentes y redacta el boletín completo en formato Markdown siguiendo estrictamente las instrucciones y la guía de tono B2B.
"""

print("⚡ Generando borrador con Groq (Llama 3.3 70B)...")

try:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0.3,
    )

    draft_content = completion.choices[0].message.content

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"draft_{date_str}.md"
    output_path = os.path.join(DRAFTS_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(draft_content)

    print(f"✅ Borrador generado exitosamente en: drafts/{output_filename}")

except Exception as e:
    print(f"❌ Error al consultar la API de Groq: {e}")
    sys.exit(1)
