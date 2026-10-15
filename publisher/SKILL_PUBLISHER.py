import os
import sys
import glob
import requests
import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")

BEEHIIV_API_KEY = sys.argv[1]
BEEHIIV_PUB_ID = sys.argv[2]
BEEHIIV_API_URL = f"https://api.beehiiv.com/v2/publications/{BEEHIIV_PUB_ID}/posts"

# Buscar el borrador más reciente
draft_files = glob.glob(os.path.join(DRAFTS_DIR, "draft_*.md"))
if not draft_files:
    print("❌ No hay borradores para publicar.")
    sys.exit(1)

latest_draft = max(draft_files, key=os.path.getctime)
with open(latest_draft, "r", encoding="utf-8-sig") as f:
    raw_content = f.read()

# 1. Extraer Título y Subtítulo
title = "Edición de Hoy: Waise Studio"
subtitle = "Lo más relevante en IA"
body_markdown = raw_content

if "[TITULO]:" in raw_content and "---" in raw_content:
    parts = raw_content.split("---", 1)
    meta_part = parts[0]
    body_markdown = parts[1].strip()
    
    for line in meta_part.split('\n'):
        if line.startswith("[TITULO]:"):
            title = line.replace("[TITULO]:", "").strip()
        elif line.startswith("[SUBTITULO]:"):
            subtitle = line.replace("[SUBTITULO]:", "").strip()

# --- NUEVA LIMPIEZA ANTI-CÓDIGO DE IA ---
# Eliminamos las triples comillas que Gemini a veces usa y que rompen el formato
body_markdown = body_markdown.replace("```markdown", "").replace("```", "").strip()

# 2. Calcular Tiempo de Lectura (200 palabras por minuto)
word_count = len(body_markdown.split())
reading_time_mins = max(1, round(word_count / 200))

# 3. Construir el Encabezado (Título Real + Píldora de lectura)
header_html = f"<h1 style='color: #111111; margin-bottom: 8px;'>{title}</h1>"
header_html += f"<p style='color: #888888; font-size: 14px; margin-top: 0;'><em>⏱ Lectura: {reading_time_mins} min</em></p><hr style='border: 1px solid #EAEAEC; margin-bottom: 24px;'>"

# 4. Convertir Markdown a HTML limpio
body_html = markdown.markdown(body_markdown)

# Unimos todo y lo envolvemos en un contenedor estándar y seguro para evitar desbordes
final_content = f"<div style='text-align: left; max-width: 100%; font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333333;'>{header_html}{body_html}</div>"

# 5. Enviar a Beehiiv
headers = {
    "Authorization": f"Bearer {BEEHIIV_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "title": title,
    "subtitle": subtitle,
    "body_content": final_content,
    "status": "draft"
}

response = requests.post(BEEHIIV_API_URL, headers=headers, json=payload)

if response.status_code == 201:
    print("✅ Borrador subido a Beehiiv con formato nativo y centrado.")
else:
    print(f"❌ Error subiendo a Beehiiv: {response.status_code} - {response.text}")
    sys.exit(1)
