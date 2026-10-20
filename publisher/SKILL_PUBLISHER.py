import os
import sys
import glob
import requests
import markdown
import re  # <-- IMPORTANTE: Añadimos esta librería para buscar la imagen

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

# --- LIMPIEZA EXTREMA ANTI-CÓDIGO Y ANTI-ESPACIOS ---
body_markdown = body_markdown.replace("```markdown", "").replace("```", "").strip()

lineas_limpias = []
for linea in body_markdown.split('\n'):
    lineas_limpias.append(linea.lstrip())
body_markdown = '\n'.join(lineas_limpias)

# 2. Calcular Tiempo de Lectura
word_count = len(body_markdown.split())
reading_time_mins = max(1, round(word_count / 200))

# 3. Construir el Encabezado
header_html = f"<h1 style='color: #111111; margin-bottom: 8px;'>{title}</h1>"
header_html += f"<p style='color: #888888; font-size: 14px; margin-top: 0;'><em>⏱ Lectura: {reading_time_mins} min</em></p><hr style='border: 1px solid #EAEAEC; margin-bottom: 24px;'>"

# 4. Convertir Markdown a HTML
body_html = markdown.markdown(body_markdown)

# Parche de seguridad
body_html = body_html.replace("<pre>", "").replace("</pre>", "").replace("<code>", "").replace("</code>", "")

# --- NUEVA AUTOMATIZACIÓN DE THUMBNAIL ---
# Buscamos la URL de la primera imagen dentro del HTML generado
thumbnail_url = ""
match_img = re.search(r'src=["\']([^"\']+)["\']', body_html)
if match_img:
    thumbnail_url = match_img.group(1)

# 5. Unimos todo
final_content = f"{header_html}{body_html}"

# Borramos texto basura de gráficos locales por si acaso
final_content = final_content.replace("*(Gráfico generado localmente en la carpeta charts/. Recuerda subir el archivo", "")
final_content = final_content.replace("(Gráfico generado localmente", "")
final_content = final_content.replace("a Beehiiv)*", "").replace("a Beehiiv)", "")

# 6. Enviar a Beehiiv
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

# Si encontramos una imagen, la agregamos como portada oficial para el SEO y Feed
if thumbnail_url:
    payload["thumbnail_url"] = thumbnail_url

response = requests.post(BEEHIIV_API_URL, headers=headers, json=payload)

if response.status_code == 201:
    print(f"✅ Borrador subido a Beehiiv. Portada configurada: {'Sí' if thumbnail_url else 'No'}")
else:
    print(f"❌ Error subiendo a Beehiiv: {response.status_code} - {response.text}")
    sys.exit(1)
