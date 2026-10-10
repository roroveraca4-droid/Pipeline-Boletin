import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Directorios y Archivos de Trabajo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SOURCES_DIR = os.path.join(PROJECT_ROOT, "sources")
IMAGES_DIR = os.path.join(SOURCES_DIR, "images")
LOG_FILE = os.path.join(BASE_DIR, "SCRAPER_LOGS.md")
URLS_FILE = os.path.join(BASE_DIR, "urls.txt")

os.makedirs(SOURCES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

def log_event(status: str, url: str, message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"| {timestamp} | {status} | {url} | {message} |\n"
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# SCRAPER EXECUTION LOGS\n\n")
            f.write("| Timestamp | Status | URL | Message |\n")
            f.write("|---|---|---|---|\n")
            
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', name)[:50]

def download_image(img_url: str, article_slug: str) -> str:
    try:
        response = requests.get(img_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            parsed = urlparse(img_url)
            ext = os.path.splitext(parsed.path)[1]
            if not ext or len(ext) > 5:
                ext = ".jpg"
                
            img_name = f"{article_slug}_{datetime.now().strftime('%H%M%S')}{ext}"
            img_path = os.path.join(IMAGES_DIR, img_name)
            
            with open(img_path, "wb") as f:
                f.write(response.content)
            return f"images/{img_name}"
    except Exception as e:
        log_event("WARNING", img_url, f"Failed to download image: {str(e)}")
    return ""

def scrape_article(url: str):
    url = url.strip()
    if not url or url.startswith("#"):
        return

    print(f"🔍 Extrayendo artículo: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            log_event("ERROR", url, f"HTTP Status Code {response.status_code}")
            print(f"❌ Error HTTP {response.status_code} en {url}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        title_tag = soup.find("h1")
        title = title_tag.get_text().strip() if title_tag else "Sin Titulo"
        slug = sanitize_filename(title)
        
        img_rel_path = ""
        meta_img = soup.find("meta", property="og:image")
        if meta_img and meta_img.get("content"):
            img_url = urljoin(url, meta_img["content"])
            img_rel_path = download_image(img_url, slug)
            
        paragraphs = soup.find_all("p")
        clean_text = []
        for p in paragraphs:
            txt = p.get_text().strip()
            if len(txt) > 50:
                clean_text.append(txt)
                
        body = "\n\n".join(clean_text)
        
        if not body:
            log_event("WARNING", url, "No main content extracted.")
            print(f"⚠ Contenido insuficiente extraído de {url}")
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{date_str}_{slug}.md"
        file_path = os.path.join(SOURCES_DIR, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f'title: "{title}"\n')
            f.write(f'source_url: "{url}"\n')
            f.write(f'date_extracted: "{datetime.now().strftime("%Y-%m-%d %H:%M")}"\n')
            f.write(f'has_images: {"true" if img_rel_path else "false"}\n')
            f.write("---\n\n")
            f.write(f"# {title}\n\n")
            if img_rel_path:
                f.write(f"![Imagen Principal]({img_rel_path})\n\n")
            f.write(f"**Fuente:** [{url}]({url})\n\n---\n\n")
            f.write(body)
            
        log_event("SUCCESS", url, f"Saved as {file_name}")
        print(f"✅ Artículo guardado: sources/{file_name}")

    except Exception as e:
        log_event("CRITICAL", url, str(e))
        print(f"❌ Error crítico en {url}: {e}")

if __name__ == "__main__":
    print("--- INICIANDO EXTRACCIÓN DE NOTICIAS ---")
    urls = []
    
    # 1. Si le pasas una URL por comandos en terminal
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    # 2. Si existe urls.txt, lee las URLs guardadas ahí
    elif os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
    if not urls:
        print(f"❌ No hay URLs. Agrega enlaces en {URLS_FILE} o pásalas directamente en la terminal.")
        sys.exit(1)
        
    for target_url in urls:
        scrape_article(target_url)
