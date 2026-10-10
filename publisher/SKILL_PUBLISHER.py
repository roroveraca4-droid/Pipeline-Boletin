import os
import sys
import re
import glob
import requests
import markdown
from dotenv import load_dotenv

# 1. Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")

# Cargar archivo .env si existe en el sistema local
env_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# 2. Obtención flexible de credenciales (Servidor local o GitHub Actions)
API_KEY = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else os.getenv("BEEHIIV_API_KEY", "")
PUB_ID = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() else os.getenv("BEEHIIV_PUBLICATION_ID", "")

if not API_KEY or not PUB_ID:
    print("❌ Error: BEEHIIV_API_KEY o BEEHIIV_PUBLICATION_ID no están configurados.")
    print("Asegúrate de tener el archivo .env o pasar las claves por línea de comandos.")
    sys.exit(1)

# 3. Encontrar el borrador más reciente en drafts/
draft_files = glob.glob(os.path.join(DRAFTS_DIR, "draft_*.md"))
if not draft_files:
    print("❌ Error: No se encontraron archivos de borrador en drafts/")
    sys.exit(1)

latest_draft = max(draft_files, key=os.path.getctime)
print(f"📄 Procesando borrador: {os.path.basename(latest_draft)}")

with open(latest_draft, "r", encoding="utf-8") as f:
    content = f.read()

# 4. Extraer título (# Título) y convertir Markdown a HTML
title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
title = title_match.group(1).strip() if title_match else "Nuevo Boletín de IA"

html_body = markdown.markdown(content)

# 5. Enviar petición a la API v2 de Beehiiv
url = f"https://api.beehiiv.com/v2/publications/{PUB_ID}/posts"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "title": title,
    "subtitle": "Edición automatizada sobre novedades e impacto de IA en Latam",
    "status": "draft",
    "content_type": "html",
    "body": html_body
}

print("🚀 Enviando borrador a Beehiiv...")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if response.status_code in [200, 201]:
        data = response.json()
        post_id = data.get("data", {}).get("id", "N/A")
        print("✅ ¡Borrador creado con éxito en Beehiiv!")
        print(f"📌 ID de la publicación: {post_id}")
        print("Entra a tu panel de Beehiiv para darle el visto bueno final.")
    else:
        print(f"❌ Error al publicar en Beehiiv (HTTP {response.status_code}):")
        print(response.text)
        sys.exit(1)

except Exception as e:
    print(f"❌ Error de conexión con la API de Beehiiv: {e}")
    sys.exit(1)
