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

client = genai.Client(api_key=GEMINI_API_KEY)

# Forzamos utf-8-sig para evitar cualquier problema de codificación (Mojibake)
def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:
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

# 3. Prompts Blindados (Forzando el tono y el formato Markdown)
system_instruction = f"""
Eres un periodista de tecnología irreverente, sarcástico y directo de 25 años. Escribes para un boletín B2B estilo 'Morning Brew' dirigido a profesionales en Latam.

REGLAS DE ORO (SI ROMPES ESTO, EL SISTEMA FALLARÁ):
1. FORMATO ESTRICTO: Escribe ÚNICAMENTE en texto plano usando Markdown (##, **, -, etc.). ESTÁ TOTALMENTE PROHIBIDO generar etiquetas HTML (como <h1> o <p>).
2. CERO LENGUAJE CORPORATIVO: Prohibido usar palabras como "adopción efectiva", "escalar iniciativas", "sinergias", "en conclusión".
3. CERO PARÉNTESIS EXPLICATIVOS: Integra la información de forma fluida.
4. TRAMA NARRATIVA: Transforma la noticia en un chisme de industria. Empieza con un gancho humano, explica el problema real sin aburrir, y da el impacto para Latam.

INSTRUCCIONES Y REGLAS DE DISEÑO:
{skill_instructions}
{editorial_rules}
{design_guidelines}
"""

user_prompt = f"""
INFORMACIÓN EXTRAÍDA DE LAS FUENTES:
{combined_sources}

TAREA:
Redacta la edición de hoy siguiendo tu personalidad sarcástica y las Reglas de Oro. Devuelve SOLO el texto en formato Markdown.
"""

print("⚡ Generando borrador con Gemini 3.8 Flash...")

try:
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.6, # Aumentado ligeramente para darle más creatividad y sarcasmo
        ),
    )
    
    draft_content = response.text

    # 5. Guardar el archivo forzando UTF-8 puro
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"draft_{date_str}.md"
    output_path = os.path.join(DRAFTS_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(draft_content)

    print(f"✅ Borrador limpio generado exitosamente en: drafts/{output_filename}")

except Exception as e:
    print(f"❌ Error al consultar la API de Gemini: {e}")
    sys.exit(1)
