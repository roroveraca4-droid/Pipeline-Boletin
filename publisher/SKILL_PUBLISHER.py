# --- LIMPIEZA EXTREMA ANTI-CÓDIGO Y ANTI-ESPACIOS ---
# 1. Quitamos comillas de código
body_markdown = body_markdown.replace("```markdown", "").replace("```", "").strip()

# 2. Destruimos cualquier espacio o tabulación al inicio de cada línea (el culpable del margen chueco)
lineas_limpias = []
for linea in body_markdown.split('\n'):
    lineas_limpias.append(linea.lstrip()) # lstrip() elimina los espacios a la izquierda
body_markdown = '\n'.join(lineas_limpias)

# 2. Calcular Tiempo de Lectura (200 palabras por minuto)
word_count = len(body_markdown.split())
reading_time_mins = max(1, round(word_count / 200))

# 3. Construir el Encabezado
header_html = f"<h1 style='color: #111111; margin-bottom: 8px;'>{title}</h1>"
header_html += f"<p style='color: #888888; font-size: 14px; margin-top: 0;'><em>⏱ Lectura: {reading_time_mins} min</em></p><hr style='border: 1px solid #EAEAEC; margin-bottom: 24px;'>"

# 4. Convertir Markdown a HTML limpio
body_html = markdown.markdown(body_markdown)

# 5. Parche de seguridad extra: Si por algún motivo quedó código, le quitamos las etiquetas
body_html = body_html.replace("<pre>", "").replace("</pre>", "").replace("<code>", "").replace("</code>", "")

# Unimos todo y alineamos
final_content = f"<div style='text-align: left; max-width: 100%; font-family: sans-serif; font-size: 16px; line-height: 1.6; color: #333333;'>{header_html}{body_html}</div>"
