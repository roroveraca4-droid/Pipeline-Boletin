import os
import sys
import subprocess

def run_step(command: str, description: str):
    print("\n" + "=" * 50)
    print(f"▶ {description}")
    print("=" * 50)
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Error en la etapa: {description}")
        sys.exit(result.returncode)

def main():
    print("🚀 INICIANDO PIPELINE DE PUBLICACIÓN DE BOLETÍN IA")

    # Cambio a Gemini API Key
    gemini_key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_API_KEY", "")
    beehiiv_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("BEEHIIV_API_KEY", "")
    beehiiv_pub_id = sys.argv[3] if len(sys.argv) > 3 else os.getenv("BEEHIIV_PUB_ID", "")

    if not gemini_key or not beehiiv_key or not beehiiv_pub_id:
        print("❌ Error: Faltan credenciales (GEMINI_API_KEY, BEEHIIV_API_KEY, BEEHIIV_PUB_ID)")
        sys.exit(1)

    # 1. Scraping de URLs
    run_step("python3 scraper/fetch_sources.py", "FASE 1: Web Scraping de Noticias")

    # 2. Redacción y Formato Visual (Actualizado a Gemini)
    run_step(f"python3 redactor/generate_draft_gemini.py '{gemini_key}'", "FASE 2A: Redacción B2B con Gemini 1.5 Flash")
    run_step("python3 redactor/generate_charts.py", "FASE 2B: Generación Visual de Gráficas de Datos")

    # 3. Publicación a Beehiiv API
    run_step(f"python3 publisher/SKILL_PUBLISHER.py '{beehiiv_key}' '{beehiiv_pub_id}'", "FASE 3: Subida de Borrador a Beehiiv")

    print("\n" + "=" * 50)
    print("🎉 PIPELINE FINALIZADO CON ÉXITO")
    print("El borrador ya está disponible en tu panel de Beehiiv.")
    print("=" * 50)

if __name__ == "__main__":
    main()
