# REGLAS DE DISEÑO Y MAQUETACIÓN VISUAL (B2B)

## 1. Higiene Visual y Prohibiciones (Escaneabilidad)
- **CERO EMOJIS:** Está ESTRICTAMENTE PROHIBIDO el uso de cualquier tipo de emoji (como 🚀, 🤖, 📊, 💡, etc.) en todo el documento. Restan seriedad y causan rechazo en la audiencia corporativa.
- **Micro-párrafos:** Un ejecutivo debe poder escanear el texto rápidamente. Los párrafos deben tener un máximo de 2 a 3 líneas (1 a 2 oraciones). NUNCA generes bloques densos de texto.
- **Sin artefactos de Markdown:** Prohibido dejar viñetas vacías o saltos de línea rotos (`\n - \n`). Todo guion de viñeta (`- `) debe tener texto inmediatamente después.

## 2. Tipografía y Énfasis
- **Negritas tácticas en viñetas:** Cuando uses listas, las primeras 3 a 5 palabras de cada viñeta deben ir en **negrita** para resumir el punto principal, seguidas de dos puntos (:) o un guion y luego la explicación.
  - *Ejemplo correcto:* `- **La barrera del costo:** El entrenamiento de modelos superó los...`
- **Separadores limpios:** Usa la línea divisoria (`---`) ÚNICAMENTE para separar una noticia completa de otra. Nunca la uses dentro del cuerpo de una misma historia.

## 3. Reglas de Imágenes y Gráficas
- **Cantidad moderada:** El boletín debe ser ligero. Usa un máximo de 2 a 3 imágenes en total por publicación.
- **Citas Obligatorias:** Toda imagen extraída de la web o gráfica de datos insertada DEBE tener su cita en la línea inmediatamente inferior, escrita en formato de cursiva.
  - *Formato exacto requerido:* `*(Fuente: [Nombre de la Empresa o Autor])*`
- **Integración fluida:** No anuncies las imágenes con texto como "Aquí tienes una imagen". Simplemente inserta el código de la imagen en Markdown en el lugar adecuado.

## 4. Estandarización de Números, Monedas y Métricas
- **Monedas Unificadas:** Usa siempre el código ISO seguido del número y la magnitud (ej. `USD 150M`, `EUR 25k`). No mezcles símbolos como `$` o `€` con palabras sueltas.
- **Magnitudes Ejecutivas:** 
  - Miles = `k` (ej. `USD 50k`)
  - Millones = `M` (ej. `USD 12M`)
  - Miles de millones = `B` (ej. `USD 1.5B`)
- **Multiplicadores y Porcentajes:** Sin espacio entre el número y la "x" (ej. `2.3x`). El símbolo de porcentaje va pegado al número (ej. `15%`).
