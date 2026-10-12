import os
import sys
import glob
import json
import requests
import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")
TEMPLATE_FILE = os.path.join(BASE_DIR, "template.html")

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

# 2. Calcular Tiempo de Lectura (200 palabras por minuto)
word_count = len(body_markdown.split())
reading_time_mins = max(1, round(word_count / 200))
reading_time_text = f"Lectura: {reading_time_mins} min"

# 3. Convertir Markdown a HTML
body_html = markdown.markdown(body_markdown)

# 4. Inyectar todo en la plantilla HTML de Waise Studio
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    html_template = f.read()

# Reemplazamos las variables (puedes cambiar tu Logo URL aquí luego)
final_html = html_template.replace("{{PREHEADER}}", subtitle)
final_html = final_html.replace("{{CONTENT_BODY}}", body_html)
final_html = final_html.replace("{{READING_TIME}}", reading_time_text)
final_html = final_html.replace("{{ISSUE_TAG}}", "EDICIÓN B2B")
final_html = final_html.replace("{{LOGO_URL}}", "https://i.imgur.com/TuLogoAqui.png")

# 5. Enviar a Beehiiv
headers = {
    "Authorization": f"Bearer {BEEHIIV_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "title": title,
    "subtitle": subtitle,
    "web_content": final_html,
    "email_content": final_html,
    "status": "draft"
}

response = requests.post(BEEHIIV_API_URL, headers=headers, json=payload)

if response.status_code == 201:
    print("✅ Borrador renderizado en HTML y subido a Beehiiv con éxito.")
else:
    print(f"❌ Error subiendo a Beehiiv: {response.status_code} - {response.text}")
    sys.exit(1)
