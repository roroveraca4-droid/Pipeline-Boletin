import os
import re
import json
import glob
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")

os.makedirs(CHARTS_DIR, exist_ok=True)

draft_files = glob.glob(os.path.join(DRAFTS_DIR, "draft_*.md"))
if not draft_files:
    print("No hay borradores para analizar gráficos.")
    exit(1)

latest_draft = max(draft_files, key=os.path.getctime)
with open(latest_draft, "r", encoding="utf-8") as f:
    content = f.read()

json_pattern = re.compile(r'```json\s*(\{.*?"chart_data".*?\})\s*```', re.DOTALL)
match = json_pattern.search(content)

if not match:
    print("No se detectaron datos para graficar en este borrador.")
    exit(0)

print("Datos detectados. Generando gráfico estilo B2B...")

try:
    json_str = match.group(1)
    chart_info = json.loads(json_str)["chart_data"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fondo_color = '#151522' 
    fig.patch.set_facecolor(fondo_color)
    ax.set_facecolor(fondo_color)
    
    etiquetas = list(chart_info["data"].keys())
    valores = list(chart_info["data"].values())
    
    barras = ax.bar(etiquetas, valores, color='white', width=0.45)
    
    for espina in ['top', 'right', 'left']:
        ax.spines[espina].set_visible(False)
    ax.spines['bottom'].set_color('#555555')
    
    ax.set_yticks([])
    ax.tick_params(axis='x', colors='white', labelsize=12, bottom=False)
    
    unidad = chart_info.get("unit", "")
    sufijo = chart_info.get("suffix", "")
    for barra in barras:
        alto = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2, alto + (max(valores)*0.02),
                f"{unidad} {alto}{sufijo}", ha='center', color='white', 
                fontsize=14, fontweight='bold')
                
    plt.text(0, 1.15, chart_info.get("title", "DATOS CLAVE"), color='white', fontsize=22, fontweight='bold', transform=ax.transAxes)
    plt.text(0, 1.07, chart_info.get("subtitle", ""), color='#a0a0a0', fontsize=12, transform=ax.transAxes)
    plt.text(1, -0.1, f"FUENTE: {chart_info.get('source', 'ND')}", color='#a0a0a0', fontsize=10, transform=ax.transAxes, ha='right')
    
    chart_filename = f"chart_{os.path.basename(latest_draft).replace('.md', '.png')}"
    chart_path = os.path.join(CHARTS_DIR, chart_filename)
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=150)
    print(f"Gráfico generado en: {chart_path}")
    
    placeholder_md = f"\n\n*(Gráfico generado localmente en la carpeta charts/. Recuerda subir el archivo {chart_filename} a Beehiiv)*\n\n"
    new_content = content[:match.start()] + placeholder_md + content[match.end():]
    
    with open(latest_draft, "w", encoding="utf-8") as f:
        f.write(new_content)

except Exception as e:
    print(f"Error al generar la gráfica: {e}")
