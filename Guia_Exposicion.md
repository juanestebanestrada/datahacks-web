# Dossier y Guión de Exposición Extendido: Plataforma DataHacks — Mundial 2026

Este documento está diseñado como una guía exhaustiva y un guión paso a paso para tu presentación. Contiene el discurso que puedes utilizar, explicaciones técnicas profundas y la coreografía exacta de lo que debes mostrar en pantalla, desde el código fuente hasta la interfaz de usuario.

---

## 1. Introducción
**Guión sugerido:**
"Buenos días a todos. Hoy quiero presentarles un proyecto que nace en la intersección de dos de las industrias más grandes y apasionantes del mundo: el fútbol y la ciencia de datos. En 2026, seremos testigos del Mundial de la FIFA más grande de la historia, organizado por Estados Unidos, Canadá y México. Pasaremos de 32 a 48 selecciones, con un total de 104 partidos. 
Esta expansión exponencial no solo significa más fútbol, sino un volumen de datos masivo generado cada segundo de juego. Hoy en día, cada pase, cada carrera y cada disparo se mide a través de coordenadas espaciales. Sin embargo, los datos crudos no sirven de nada si no se pueden interpretar. Es aquí donde entra **DataHacks / ScoutingMundial**, una plataforma integral y dinámica de analítica deportiva. Nuestra solución unifica la recolección de datos, el modelado probabilístico y una interfaz visual impactante, permitiendo a periodistas, cuerpos técnicos y aficionados comprender el juego a un nivel táctico sin precedentes."

## 2. Descripción del Problema
**Guión sugerido:**
"Para entender el valor de DataHacks, debemos mirar los problemas actuales en la industria de la analítica deportiva:
1. **La fragmentación de la información:** Los datos de rendimiento están secuestrados en plataformas cerradas y dispersas (SofaScore, FotMob, StatsBomb, Opta). Un analista pierde horas extrayendo y limpiando estos datos.
2. **Complejidad en la traducción del dato:** El fútbol moderno habla de métricas avanzadas como los *Goles Esperados (xG)* o el *Peligro Esperado (xT)*. Pero, ¿cómo le explicamos esto a una audiencia general? Existe una barrera gigantesca entre las matemáticas puras y la narrativa deportiva.
3. **Carencia de predicciones científicas:** La gran mayoría de los análisis previos a un partido en los medios tradicionales se basan en opiniones subjetivas, emociones o historiales caducos. Se ignora por completo el uso de modelos estadísticos y de Inteligencia Artificial para pronosticar escenarios reales."

## 3. Objetivos
**Guión sugerido:**
"Frente a este panorama, nuestro proyecto se trazó los siguientes objetivos:
*   **Objetivo General:** Desarrollar un ecosistema digital (una Landing Page comercial y un Dashboard analítico) que recolecte, modele y divulgue datos tácticos del Mundial 2026 utilizando herramientas de Data Science e Inteligencia Artificial Generativa.
*   **Objetivos Específicos:**
    *   Integrar en tiempo real múltiples fuentes de datos y APIs deportivas.
    *   Implementar modelos matemáticos (como la Distribución de Poisson Bivariada y simulaciones de Monte Carlo) para proyectar probabilidades en los partidos.
    *   Traducir modelos espaciales en gráficos interactivos fácilmente comprensibles (mapas de calor, radares, diagramas de tiros).
    *   Generar un diseño web de vanguardia (glassmorphism y neon-cyberpunk) que cautive al usuario final."

## 4. Justificación
**Guión sugerido:**
"¿Por qué es vital este proyecto hoy? Estamos viviendo la revolución del *Data-Driven Football*. Los clubes gastan millones en departamentos de análisis, y los medios de comunicación compiten por quién ofrece la mejor cobertura técnica. DataHacks democratiza estas herramientas. 
A nivel de negocio, automatizar el análisis táctico reduce los tiempos de producción de contenido de horas a simples milisegundos. Un creador de contenido puede utilizar nuestra plataforma en el descanso de un partido para generar de inmediato un hilo de Twitter o un guión para TikTok sustentado en matemáticas. Es la combinación perfecta entre eficiencia tecnológica, rigor científico y consumo de entretenimiento digital."

---

## 5. Diseño Básico y Funcionalidad de la Aplicación Web
**Guión sugerido:**
"Para resolver este reto, diseñamos una arquitectura híbrida de dos capas, pensando en dos tipos de usuarios distintos:
1.  **El Frontend Público (La cara comercial):** Una Landing Page construida puramente con HTML, CSS y JavaScript. Su propósito es la velocidad, el impacto visual inmediato (con paletas oscuras y colores neón) y la captación de usuarios. Aquí mostramos resúmenes, perfiles tácticos y análisis de grupos.
2.  **El Backend Analítico (La sala de máquinas):** Una aplicación construida en Python usando el framework **Streamlit**. Este es un panel de control interactivo donde los analistas pueden correr modelos estadísticos, filtrar datos, ajustar parámetros de Goles Esperados y simular torneos enteros sin escribir una línea de código."

## 6. Características de la Aplicación (Backend y Frontend)

**Énfasis en Tecnologías:**
*   **Frontend (La Experiencia Visual):** "En la web principal, prescindimos de frameworks pesados para garantizar tiempos de carga ínfimos. Utilizamos CSS3 puro con variables dinámicas para lograr efectos *glassmorphism* (cristal esmerilado). Integramos bibliotecas ligeras como **Chart.js** para dibujar gráficos de radar dinámicos y usamos APIs de banderas (FlagCDN) para renderizar SVG en alta resolución."
*   **Backend (El Poder de Procesamiento):** "En el núcleo, usamos **Python 3.12**. Aquí es donde ocurre la magia:
    *   **Concurrencia:** Utilizamos `ThreadPoolExecutor` para hacer llamadas asíncronas a APIs de fútbol. Esto significa que podemos descargar datos de 5 partidos simultáneamente sin bloquear la aplicación.
    *   **Ciencia de Datos:** Empleamos bibliotecas como `pandas` para manipular enormes DataFrames de eventos de StatsBomb, y `scipy.stats` para calcular funciones de probabilidad de Poisson que alimentan nuestros simuladores.
    *   **Streamlit:** Este framework nos permite levantar una aplicación de datos reactiva. Cada vez que movemos un *slider* (deslizador) en la aplicación, el script de Python se recalcula en fracciones de segundo y actualiza los gráficos sin necesidad de peticiones AJAX o recargas de página."

---

## 7. Demostración de la Aplicación

*(Esta es la sección interactiva. Aquí seguirás una coreografía en tu computadora frente al público).*

### A. Nombre de la Aplicación
"Nuestra plataforma se presenta bajo el concepto **DataHacks: Mundial 2026 Tactical Dashboard**."

### B. Actividades de Inicio (Demostración de Código y Terminal)
"Antes de ver la cara bonita del proyecto, quiero mostrarles cómo opera el cerebro de la aplicación desde el entorno de desarrollo."

1.  **Abre Visual Studio Code:** 
    "Aquí podemos ver la estructura del proyecto. Tenemos nuestra carpeta de la página web (`website/`) con sus archivos HTML y CSS, y nuestros scripts de Python para el modelado matemático y la conexión de datos."
2.  **Muestra la Terminal y la Conexión a la API de la FIFA:**
    "En el fútbol, la velocidad del dato lo es todo. Voy a correr un script desde la terminal que se conecta en tiempo real a una API externa de fútbol para extraer el flujo de datos. Observen:"
    *Ejecuta en la terminal:* `python test_fifa_api.py`
    *(Espera que la terminal imprima los JSON y resultados)*.
    "Como pueden ver, nuestra aplicación está recibiendo estructuras JSON con la información de los eventos, la cual nuestro Backend luego procesa y limpia."
3.  **Lanzamiento de la App Streamlit:**
    "Ahora, vamos a levantar el motor analítico."
    *Ejecuta en la terminal:* `streamlit run app.py`
    "En este momento, Python está compilando el entorno web reactivo de Streamlit en un puerto local."

### C. Descripción de los Módulos
"La aplicación se divide en varios módulos clave:
*   **Módulo de Eventos (Shot Maps):** Donde trazamos las coordenadas X,Y de cada tiro, calculando su peligro inminente (xG).
*   **Simulador Poisson:** Una calculadora donde metemos el rendimiento histórico de dos equipos, y mediante una distribución probabilística, nos dice el porcentaje exacto de victoria, empate o derrota.
*   **Dashboard Táctico:** Perfiles generados que cruzan la estadística con la evaluación visual."

### D. Ejecución (Navegación en Vivo)
1.  **Muestra la Landing Page Comercial:**
    Abre el archivo `index.html` en el navegador.
    "Esta es la entrada para el público general. Noten el diseño inmersivo, los gráficos tipo radar que muestran el balance de las selecciones y la fluidez de las animaciones."
2.  **El Caso del Grupo K:**
    "Hagamos un ejercicio práctico. Supongamos que somos periodistas cubriendo el Grupo K. Hacemos clic en esta sección..."
    *(Haz clic en el enlace del Grupo K para abrir `grupo_k.html`)*.
    "Inmediatamente, el sistema nos carga el análisis técnico de los equipos de este grupo: Portugal, Colombia, Congo DR y Uzbekistán.
    Aquí pueden observar las **Imágenes de Perfiles Tácticos** que la plataforma maneja para cada equipo. Si bajamos, encontramos la **Comparativa General de Atributos** calculada numéricamente: Ataque, Defensa, Posesión. 
    Finalmente, miren la sección del análisis cualitativo: el sistema desgrana las fortalezas y debilidades de Portugal como favorito, y las oportunidades de Colombia. Todo este texto está fundamentado en los datos y procesado por nuestro orquestador."
3.  **Muestra la App de Streamlit:**
    Ve a la pestaña del navegador donde se abrió `localhost:8501`.
    "Y aquí tenemos la vista de ingeniería de datos. Desde esta plataforma interactiva, un analista de datos de un cuerpo técnico podría jugar con las variables en tiempo real, filtrar jugadores, y obtener conclusiones matemáticas inmediatas que alimentarán la página pública que acabamos de ver."

### E. Cierre
"En resumen, acabamos de ver cómo pasamos de un código en Visual Studio y llamadas a una API en una terminal negra, a un dashboard estadístico robusto, para terminar entregando un producto visualmente atractivo y comercializable para el público final."

---

## 8. Conclusiones
**Guión sugerido:**
"Para concluir esta presentación, quiero dejar tres mensajes clave:
1.  **La Sinergia Tecnológica:** Hemos demostrado que separar la arquitectura en un Frontend comercial super rápido (HTML/CSS/JS) y un Backend analítico profundo (Python/Streamlit) es la forma más escalable de manejar aplicaciones de datos modernas. No sacrificamos ni el diseño ni el poder de cálculo matemático.
2.  **El Fin del Análisis Subjetivo:** Con la implementación de simulaciones de Monte Carlo y el cálculo de Goles Esperados, demostramos que el fútbol sí puede y debe medirse. Al aportar un marco estadístico sólido, eliminamos el sesgo periodístico tradicional.
3.  **El Futuro de los Medios:** Herramientas como DataHacks representan el futuro del periodismo deportivo y del análisis táctico. Quien pueda procesar esta inmensa ola de datos del Mundial 2026 de la forma más rápida y visualmente atractiva, dominará la atención de las audiencias. 

Muchas gracias por su atención, estoy abierto a cualquier pregunta sobre el código, la arquitectura o el modelado."
