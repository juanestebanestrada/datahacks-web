"""
core/ai_generator.py — FASE 2: Integración IA Real con Gemini
Usa la nueva SDK oficial: google-genai (gemini-2.0-flash-001).
Reemplaza las plantillas hardcodeadas por llamadas reales a Gemini.
"""
import os
import streamlit as st

try:
    from google import genai as google_genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

try:
    import openai
    _GROK_AVAILABLE = True
except ImportError:
    _GROK_AVAILABLE = False

from config import GEMINI_API_KEY, GROK_API_KEY


def _get_model():
    """Inicializa el cliente Gemini si la key está disponible."""
    if not _GEMINI_AVAILABLE:
        return None, "Librería `google-genai` no instalada. Ejecuta: pip install google-genai"
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY no configurada. Añádela a `secrets_local.json` con clave 'GEMINI_API_KEY'."
    try:
        client = google_genai.Client(api_key=GEMINI_API_KEY)
        return client, None
    except Exception as e:
        return None, f"Error al inicializar Gemini: {e}"


def _get_grok_client():
    """Inicializa el cliente de OpenAI configurado para la API de xAI (Grok)."""
    if not _GROK_AVAILABLE:
        return None, "Librería `openai` no instalada. Ejecuta: pip install openai"
    if not GROK_API_KEY:
        return None, "GROK_API_KEY no configurada. Añádela a `secrets_local.json`."
    try:
        client = openai.OpenAI(
            api_key=GROK_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        return client, None
    except Exception as e:
        return None, f"Error al inicializar Grok: {e}"


def _generate_with_grok(prompt: str) -> tuple[str | None, str | None]:
    """Helper: llama a Grok y retorna (texto, error)."""
    client, err = _get_grok_client()
    if err or client is None:
        return None, err
    try:
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": "Eres un analista experto en datos de fútbol."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"Error de generación (Grok): {str(e)}"


def get_ollama_models() -> list:
    """Consulta la API de Ollama y devuelve una lista de nombres de modelos instalados."""
    import requests
    try:
        url = "http://localhost:11434/api/tags"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [m['name'] for m in models]
    except Exception:
        pass
    return ["llama3"] # Fallback si no hay conexión

def _generate_with_ollama(prompt: str, model: str = "llama3") -> tuple[str | None, str | None]:
    """Helper: llama a Ollama (Local) y retorna (texto, error)."""
    import requests
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            return response.json().get('response'), None
        return None, f"Error Ollama: Código {response.status_code}"
    except Exception as e:
        return None, f"Error de conexión con Ollama: {str(e)}. ¿Está Ollama corriendo?"

def _generate(prompt: str, force_ollama: bool = None, model_ollama: str = None) -> tuple[str | None, str | None]:
    """Helper principal con lógica de prioridad/fallback."""
    
    # Sincronizar con el Centro de Control Global (Session State) si no se pasan parámetros manuales
    if force_ollama is None:
        try:
            force_ollama = st.session_state.get('force_ollama', False)
        except Exception:
            force_ollama = False
    if model_ollama is None:
        try:
            model_ollama = st.session_state.get('model_ollama', 'gemma4:e4b')
        except Exception:
            model_ollama = 'gemma4:e4b'

    # 1. SI SE FUERZA OLLAMA (MODO LOCAL)
    if force_ollama:
        return _generate_with_ollama(prompt, model=model_ollama)

    # 2. INTENTO CON GEMINI
    client_gemini, err_gemini = _get_model()
    err_gemini_gen = ""
    if not err_gemini and client_gemini is not None:
        try:
            response = client_gemini.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text, None
        except Exception as e:
            err_gemini_gen = f"Error Gemini: {str(e)}"
    else:
        err_gemini_gen = err_gemini

    # 3. FALLBACK A GROK
    result_grok, err_grok = _generate_with_grok(prompt)
    if result_grok:
        return result_grok, None
    
    # 4. FALLBACK AUTOMÁTICO A OLLAMA SI TODO LO DEMÁS FALLA
    result_ollama, err_ollama = _generate_with_ollama(prompt, model=model_ollama)
    if result_ollama:
        return result_ollama, None

    combined_error = f"{err_gemini_gen} | {err_grok} | {err_ollama}"
    return None, combined_error


def generar_podcast(tema: str, contexto_estadistico: str = "") -> tuple[str, str | None]:
    """
    Genera un guión de podcast táctico real usando Gemini.
    Returns: (contenido, error)
    """
    datos_ctx = f"Datos estadísticos:\n{contexto_estadistico}" if contexto_estadistico else ""
    prompt = f"""Eres analista táctico experto del FIFA Mundial 2026.
Genera guión de PODCAST ~3 minutos sobre: {tema}\n{datos_ctx}
Formato: Locutor A (datos) y Locutor B (narrativa). Métricas: xG, PPDA, pases progresivos.
Máximo 400 palabras. Termina con pregunta reflexiva."""
    result, err = _generate(prompt)
    if result:
        return f"**🎙️ GUIÓN DE PODCAST — {tema.upper()}**\n\n{result}", None
    return None, err


# ──────────────────────────────────────────────
# PROMPTS DE TONOS EDITORIALES
# ──────────────────────────────────────────────
TONOS_PROMPT = {
    "Científico (Montecarlo)": (
        "Adopta un tono riguroso, formal y basado estrictamente en ciencia de datos, matemáticas, "
        "probabilidades de Poisson, convergencia de simulaciones y métricas avanzadas (xG, PPDA). "
        "Enfócate en la objetividad y la precisión técnica."
    ),
    "El Villano (Polémico)": (
        "Adopta un tono provocador, picante y desafiante de las narrativas populares y el marketing de los jugadores estrella. "
        "Cuestiona el hype de las grandes figuras usando estadísticas duras (como la falta de toques en zonas de peligro) para generar debate "
        "y movilizar a los fanáticos a debatir en los comentarios."
    ),
    "Sleepy Giant (Gemas de Datos)": (
        "Adopta un tono entusiasta, descubridor y revelador. Enfréntate al análisis buscando diamantes en bruto y "
        "selecciones/jugadores infravalorados. Compara sus métricas positivamente con las de grandes potencias mundiales para "
        "demostrar que merecen más atención."
    ),
    "Betting & Value (Especulador)": (
        "Adopta un tono analítico, de inversor inteligente y especulativo. Enfócate en el concepto de apuestas de valor ($EV+$), "
        "encontrando discrepancias matemáticas entre tus modelos probabilísticos y las cuotas de las casas de apuestas."
    )
}


def generar_hilo_x(tema: str, datos: dict = None, tono: str = "Científico (Montecarlo)") -> tuple[str, str | None]:
    """
    Genera un hilo viral de X (Twitter) con Gemini.
    Returns: (contenido, error)
    """
    datos_str = "\n".join([f"- {k}: {v}" for k, v in datos.items()]) if datos else ""
    instruccion_tono = TONOS_PROMPT.get(tono, TONOS_PROMPT["Científico (Montecarlo)"])
    prompt = f"""Eres analista táctico y creador de contenido de fútbol para el FIFA Mundial 2026.
{instruccion_tono}

Crea un hilo viral de 5 tweets sobre: {tema} — FIFA Mundial 2026
{datos_str}

Reglas:
- Máx 280 caracteres por tweet.
- Emojis relevantes: ⚽🔥📊🧠💡.
- Tweet 1: gancho fuerte.
- Tweets 2-4: análisis de datos.
- Tweet 5: llamado a la acción (CTA) y hashtags como #Mundial2026.
- Formato de salida: N/5 texto del tweet."""
    result, err = _generate(prompt)
    if result:
        return f"🧵 HILO IA ({tono}) — {tema}\n\n{result}", None
    return None, err


def generar_dossier_scouting(jugador: str, stats: dict = None) -> tuple[str, str | None]:
    """
    Genera un dosier de scouting profesional con Gemini.
    Returns: (contenido, error)
    """
    stats_str = "\n".join([f"- {k}: {v}" for k, v in stats.items()]) if stats else ""
    prompt = f"""Scout de élite Premier League. Informe pre-Mundial 2026 sobre {jugador}.\n{stats_str}
Secciones: 1.Perfil Táctico 2.Fortalezas Clave 3.Áreas de Mejora 4.Comparativa Histórica 5.Recomendación
Profesional, conciso, basado en evidencia. Máx 300 palabras."""
    result, err = _generate(prompt)
    if result:
        return f"# 📋 DOSIER: {jugador.upper()}\n\n{result}", None
    return None, err


def generar_blog_seo(tema: str, equipo: str = "Grupo K", tono: str = "Científico (Montecarlo)") -> tuple[str, str | None]:
    """
    Genera un artículo de blog SEO-optimizado con Gemini.
    Returns: (contenido, error)
    """
    instruccion_tono = TONOS_PROMPT.get(tono, TONOS_PROMPT["Científico (Montecarlo)"])
    prompt = f"""Redactor SEO de fútbol y analista de datos. Blog Mundial 2026: {tema} (contexto: {equipo}).
{instruccion_tono}

Estructura Markdown: # Título, ## Intro, ## Dato Clave, ## Análisis de Datos, ## Conclusión e IA.
Escribe un artículo de 600-800 palabras. Usa keywords clave: Mundial 2026, xG, táctica. Terminar con un llamado a la acción (CTA)."""
    result, err = _generate(prompt)
    if result:
        return result, None
    return None, err


def generar_trivia(tema: str, n_preguntas: int = 3) -> tuple[list, str | None]:
    """
    Genera preguntas de trivia táctica con Gemini.
    Returns: (lista_preguntas, error)
    """
    import json as _json
    prompt = f"""Genera {n_preguntas} preguntas de trivia táctica sobre {tema} del Mundial 2026.
JSON array: [{{"pregunta":"...","opciones":["A","B","C","D"],"correcta":"...","explicacion":"..."}}]
Solo responde con el JSON, sin markdown."""
    result, err = _generate(prompt)
    if result:
        try:
            text = result.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'): text = text[4:]
            return _json.loads(text.strip()), None
        except Exception:
            pass
    return None, err


def generar_guion_tiktok(tema: str, datos: dict = None, tono: str = "Científico (Montecarlo)") -> tuple[str, str | None]:
    """
    Genera un guión de video corto (60s) para TikTok/Reels con Gemini con estructura de Timeline.
    """
    datos_str = "\n".join([f"- {k}: {v}" for k, v in datos.items()]) if datos else ""
    instruccion_tono = TONOS_PROMPT.get(tono, TONOS_PROMPT["Científico (Montecarlo)"])
    prompt = f"""Creador de contenido viral de fútbol y analista táctico. 
{instruccion_tono}

Escribe un guión de TikTok/Reels de 60 segundos sobre: {tema}
Datos disponibles: {datos_str}

Estructura obligatoria del guión con Timeline (debe tener exactamente estas columnas o filas por bloque):
[Segundos] | [Visual en Pantalla] | [Audio/Voz en Off]

Reglas:
- Primeros 3 segundos: Gancho visual y auditivo muy fuerte y adaptado al tono seleccionado.
- Desarrollo: Usa 1 o 2 datos clave (ej. xG, pases progresivos, PPDA) e indica explícitamente qué gráfico táctico o mapa de la App mostrar en el visual (ej: [Visual: Mapa de Calor vertical 9:16 de {tema}]).
- Final: Llamado a la acción (CTA) dinámico y rápido.
Dinámico, al grano, retención máxima."""
    result, err = _generate(prompt)
    if result:
        return f"🎬 **GUIÓN TIKTOK (60s) [{tono}]**\n\n{result}", None
    return None, err


def generar_guion_youtube(tema: str, datos: dict = None, tono: str = "Científico (Montecarlo)") -> tuple[str, str | None]:
    """
    Genera un guión de video (3-5 min) para YouTube con Gemini con estructura de Timeline y Edición.
    """
    datos_str = "\n".join([f"- {k}: {v}" for k, v in datos.items()]) if datos else ""
    instruccion_tono = TONOS_PROMPT.get(tono, TONOS_PROMPT["Científico (Montecarlo)"])
    prompt = f"""Analista táctico y creador de videos de YouTube.
{instruccion_tono}

Escribe un guión de video largo de YouTube (3 a 5 minutos) estructurado con Timeline preciso sobre: {tema}
Datos de respaldo: {datos_str}

Estructura obligatoria con Timeline de Producción:
Usa el siguiente bloque de formato para cada escena o sección de tiempo (ej. [00:00 - 00:30]):
- **Tiempo:** [Rango de tiempo]
- **Visual/Edición:** [Indicaciones visuales y qué gráfico/mapa del Dashboard Mundial 2026 mostrar en pantalla]
- **Voz en Off/Cámara:** [Texto del presentador o locución]

Reglas:
1. Hook (Intro rápida de 15-30s planteando un misterio, problema táctico o polémica).
2. Contexto de Datos (Explicación conceptual con métricas avanzadas).
3. Análisis Profundo (Indica transiciones, mapas de calor, red de pases o clusters de K-Means de la App).
4. Conclusión y Llamado a la Acción (CTA) de suscripción."""
    result, err = _generate(prompt)
    if result:
        return f"🎥 **GUIÓN YOUTUBE (3-5 min) [{tono}]**\n\n{result}", None
    return None, err



# ──────────────────────────────────────────────
# FALLBACKS (cuando Gemini no está disponible)
# ──────────────────────────────────────────────
def _fallback_podcast(tema):
    return f"""**🎙️ GUIÓN DE PODCAST: {tema.upper()}**

**[Intro Music Fades In]**
**Locutor A:** ¡Bienvenidos al análisis táctico del Mundial 2026! Hoy: *{tema}*.
**Locutor B:** Los datos son claros: las transiciones rápidas y el xG son los indicadores clave.
**Locutor A:** ¿Qué equipo tiene ventaja matemática? Los números apuntan a algo interesante.
**Locutor B:** ¡No te pierdas el análisis completo!
**[Outro]**

> ⚠️ *Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY para activar la IA.*"""


def _fallback_x(tema):
    return f"""🧵 HILO: {tema} ⚽

1/5 ¿Por qué {tema} define el Mundial 2026? Analicemos. 👇
2/5 El xG no miente. Los datos de StatsBomb muestran una tendencia clara. 📊
3/5 Las transiciones son el factor X. El PPDA lo confirma. 🔥
4/5 ¿Quién tiene ventaja táctica? Los números hablan. 🌍
5/5 ¿Qué opinas? #Mundial2026 #GrupoK #AnalisisTactico

> ⚠️ *Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY para activar la IA.*"""


def _fallback_dossier(jugador):
    return f"""# 📋 DOSIER: {jugador.upper()}

## Perfil Táctico
Análisis pendiente de configuración de IA.

## Nota
Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY en secrets_local.json para activar la IA."""


def _fallback_blog(tema):
    return f"""# Análisis del Mundial 2026: {tema}

Artículo en proceso de generación con IA.

> Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY en secrets_local.json para activar la IA."""


def _fallback_trivia(tema):
    return [
        {
            "pregunta": f"¿Cuál es el factor clave de {tema} en el Mundial 2026?",
            "opciones": ["Posesión estática", "Transiciones rápidas", "Juego aéreo", "Fuerza física"],
            "correcta": "Transiciones rápidas",
            "explicacion": f"Las transiciones rápidas son el factor determinante en {tema}. Verifica tu cuota de Gemini para trivia generada por IA."
        }
    ]

def _fallback_tiktok(tema):
    return f"""🎬 **GUIÓN TIKTOK (60s): {tema.upper()}**

**[Visual: Título llamativo con emojis]**
**Voz:** ¿Sabías este dato increíble sobre {tema}? 🤯

**[Visual: Gráfico de barras / Radar]**
**Voz:** Los números no mienten. Las estadísticas muestran un patrón brutal.

**[Visual: Flechas señalando el dato]**
**Voz:** ¡Es por esto que dominarán el Mundial! ¿Qué opinas? ¡Comenta abajo! 👇

> ⚠️ *Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY para activar la IA.*"""


def _fallback_youtube(tema):
    return f"""🎥 **GUIÓN YOUTUBE (3-5 min): {tema.upper()}**

**[0:00-0:15] INTRODUCCIÓN**
**[Visual: Clip dinámico o texto en pantalla]**
**Voz:** Hoy vamos a analizar a fondo: {tema}. Muchos hablan, pero pocos ven los verdaderos datos tácticos.

**[0:15-1:30] CONTEXTO DE DATOS**
**[Visual: Dashboard Mundial 2026 - Pantalla principal]**
**Voz:** Si miramos las métricas avanzadas, notamos un patrón que cambia el juego.

**[1:30-3:00] ANÁLISIS PROFUNDO**
**[Visual: Laboratorio Deep - Gráficos xG y Percentiles]**
**Voz:** Aquí está la prueba. Miren esta gráfica. Las transiciones y la posesión muestran una superioridad táctica clara.

**[3:00-4:00] CONCLUSIÓN**
**[Visual: Pantalla completa al presentador]**
**Voz:** En resumen, los datos nos cuentan la historia oculta detrás del rendimiento. No olvides suscribirte y dejar tu like.

> ⚠️ *Contenido de prueba. Verifica tu configuración o cuota de GEMINI_API_KEY para activar la IA.*"""
