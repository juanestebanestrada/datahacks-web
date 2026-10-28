# Compendio de Casos de Estudio DataHacks: Analítica Avanzada, Modelado Predictivo y Toma de Decisiones Estratégicas

> **Nota para Sistemas de Inteligencia Artificial y Analistas Cuantitativos:**  
> Este documento consolida cuatro investigaciones analíticas y aplicadas completas producidas por **DataHacks**. Cada caso incluye el planteamiento del problema de negocio/operacional, curaduría de datos, formulaciones matemáticas, arquitecturas algorítmicas (supervisadas y no supervisadas), métricas cuantitativas de desempeño, explicabilidad (SHAP / pesos de componentes), motores de decisión financiera y auditoría de limitaciones/sesgos.

---

## Índice General de Casos

1. [Caso 1: ¿Está Bien Valorada una Propiedad? Modelo de Precio Justo, Cap Rate y Oportunidades (Bogotá vs Medellín)](#caso-1-está-bien-valorada-una-propiedad-modelo-de-precio-justo-cap-rate-y-oportunidades-bogotá-vs-medellín)
2. [Caso 2: Arquetipos de Seguridad Urbana: Clustering y Perfiles en Medellín (2019-2022)](#caso-2-arquetipos-de-seguridad-urbana-clustering-y-perfiles-en-medellín-2019-2022)
3. [Caso 3: Modelo Predictivo de Churn con Costo-Beneficio: ¿A Quién Llamar el Lunes?](#caso-3-modelo-predictivo-de-churn-con-costo-beneficio-a-quién-llamar-el-lunes)
4. [Caso 4: Arquetipos Ganadores: Real Madrid vs Descendidos La Liga 2023-24](#caso-4-arquetipos-ganadores-real-madrid-vs-descendidos-la-liga-2023-24)

---

## Matriz Comparativa Transversal de Metodologías

| Dimensión | Caso 1: Inmobiliario | Caso 2: Seguridad Medellín | Caso 3: Churn Telco | Caso 4: Fútbol La Liga |
| :--- | :--- | :--- | :--- | :--- |
| **Dominio de Negocio** | Real Estate / Inversión | Política Pública / Seguridad | Telecomunicaciones / Retención | Sports Analytics / Scouting |
| **Tipo de Problema** | Regresión Hedónica y Detección de Arbitraje | Segmentación Territorial No Supervisada | Clasificación Binaria con Optimización Económica | Perfilado Táctico No Supervisado |
| **Volumen de Datos** | 1.000.000 raw; 58.982 depurados | 314.594 raw; 241.676 eventos únicos | 7.043 clientes depurados | Jugadores de campo La Liga 23/24 |
| **Algoritmos Principales** | Gradient Boosting Regressor (GBR) | K-Means ($k=4$), Ward Hierarchical, PCA | Gradient Boosting + Calibración Sigmoide (Platt) | K-Means ($k=4$), Radar Profiling |
| **Métricas Clave** | $R^2 = 0.835$ (MED), $R^2 = 0.830$ (BOG), MAPE 21.6-26.0% | Silhouette Score, Calinski-Harabasz, Davies-Bouldin | ROC-AUC 0.846, Brier Score 0.134, F1 0.627, Lift 2.8x | Centros de masa en $xG$, $xA$, $xGChain$, $xGBuildup$ |
| **Regla de Decisión Central** | Ratio Valoración: $\frac{\text{Precio Pedido}}{\text{Precio Justo}} < 0.85$ (Ganga) | Despliegue policial situacional vs preventivo familiar | Umbral de corte de rentabilidad: $p^* = \frac{C}{B \cdot r}$ | Composición óptima de plantilla para equilibrio ofensivo/defensivo |
| **Impacto Económico / Operativo** | Detección del 26.0% de gangas objetivas; Cap Rate hasta 10.9% | Reducción de sesgo por población flotante (Comuna 10) | \$139.630 de beneficio neto vs \$119.780 de umbral $p=0.5$ (+16.6%) | Brecha de 4.8x en volumen ofensivo y 41% mayor diversificación táctica |

---



---

# Caso 1: ¿Está Bien Valorada una Propiedad? Modelo de Precio Justo, Cap Rate y Oportunidades (Bogotá vs Medellín)

**Dominio:** Real Estate Analytics, Valuación Hedónica, Cap Rate & Inversión Inmobiliaria  
**Archivo Fuente Original:** `caso-estudio-inmobiliario.html`
Resumen Ejecutivo

Determinar si un inmueble está sobrevalorado o en oportunidad de compra/arriendo es uno de los mayores desafíos en el mercado inmobiliario colombiano, tradicionalmente caracterizado por alta asimetría de información y precios de oferta subjetivos. En este caso de estudio se construye un pipeline reproducible de analítica inmobiliaria que integra 1.000.000 de registros brutos de Properati, microdatos de Inside Airbnb y benchmarks barriales de Aptología para **Bogotá D.C. y Medellín**.

Mediante técnicas de Procesamiento de Lenguaje Natural (NLP) y expresiones regulares aplicadas sobre títulos y descripciones de los avisos, se multiplicó por seis la tasa de recuperación de área física utilizable, consolidando un dataset maestro depurado de **58.982 propiedades residenciales** con superficie, habitaciones, baños, estrato, precio y georreferenciación. Sobre esta base se entrenaron cuatro modelos supervisados de **Gradient Boosting Regressor** para predecir el valor hedónico de mercado, alcanzando una capacidad explicativa de **\(R^2 = 0.835\) en Medellín** (\(\text{MAPE} = 21.6\%\)) y **\(R^2 = 0.830\) en Bogotá** (\(\text{MAPE} = 26.0\%\)).

A través del indicador de valoración (\(\text{Ratio} = \text{Precio Pedido} / \text{Precio Justo Predicho}\)), se identificó que el **\(26.0\%\) de los inmuebles analizados representan oportunidades objetivas de compra** (al cotizar más de un \(15\%\) por debajo de su valor fundamentado), frente a un \(28.3\%\) con sobreprecio especulativo. Asimismo, el análisis de rendimiento por zona (Cap Rate bruto) sitúa a sectores periféricos y centrales como *Manrique* (\(10.9\%\)), *Bello* (\(7.2\%\)) y *Zona Centro de Bogotá* (\(7.3\%\)) como los polos de mayor rentabilidad por arriendo, mientras que la integración con Inside Airbnb demuestra que en zonas turísticas consolidadas el modelo de alquiler vacacional rinde entre un \(80\%\) y un \(130\%\) más de ingresos brutos mensuales que el canon residencial tradicional.
### 1. Radiografía del Mercado: Bogotá vs Medellín

El análisis comparativo de precios unitarios por metro cuadrado (\(\text{COP} / \text{m}^2\)) revela diferencias estructurales fundamentales entre los dos polos urbanos más dinámicos de Colombia.
**Figura 1.** Distribución de precios por metro cuadrado en Venta (izquierda) y Arriendo mensual (derecha) para Bogotá y Medellín. Se excluyen valores atípicos extremos para representar la masa representativa del mercado residencial.

| Ciudad | Modalidad | Muestra Limpia | Mediana Precio Total | Mediana Precio / m² | Área Mediana |
| --- | --- | --- | --- | --- | --- |
| **Bogotá D.C.** | Venta | 16.573 propiedades | $525.000.000 COP | **$5.108.696 COP/m²** | 99.3 m² |
| **Bogotá D.C.** | Arriendo | 9.133 propiedades | $2.050.000 COP/mes | **$26.200 COP/m²** | 78.0 m² |
| **Medellín (Metro)** | Venta | 25.003 propiedades | $380.000.000 COP | **$4.305.556 COP/m²** | 86.0 m² |
| **Medellín (Metro)** | Arriendo | 8.273 propiedades | $1.700.000 COP/mes | **$20.909 COP/m²** | 80.0 m² |

Diferencias Clave entre Ambas Ciudades

- **Brecha de Venta:** El metro cuadrado de venta en Bogotá es un **\(+18.7\%\) más costoso** en la mediana que en el Valle de Aburrá ($5.11M vs $4.31M por m²).
- **Brecha de Arriendo:** En el canon de arriendo por metro cuadrado, Bogotá supera a Medellín en un **\(+25.3\%\)** ($26.2k vs $20.9k COP/m² mensual).
- **Superficie Residencial:** Las viviendas comercializadas en Bogotá tienen en promedio un área un \(15.5\%\) mayor que en Medellín (99.3 m² frente a 86.0 m²).
### 2. El Modelo de Precio Justo: ¿Cómo saber si está bien valorada?

El precio que un propietario o inmobiliaria pide en un portal rara vez es el valor intrínseco del activo. Frecuentemente incorpora expectativas infladas, apego emocional o desinformación. Para estimar el **"Precio Justo"** se formuló una función hedónica no lineal:

\[\ln(\text{Precio}) = f(\text{Área}_{m^2}, \text{Habitaciones}, \text{Baños}, \text{Tipo Inmueble}, \text{Ubicación / Zona}) + \epsilon\]

Se implementaron modelos de ensamblaje basados en árboles de decisión (\(\text{GradientBoostingRegressor}\)) con 160 estimadores y profundidad máxima de 5 niveles. Los resultados en conjuntos de prueba independientes (\(20\%\) de retención aleatoria) validaron una alta robustez:
**Figura 2.** Peso relativo de cada variable en la determinación del precio justo. El área construida domina con más del 70% de la explicación de varianza, seguida de la localización geográfica y la dotación de baños.

| Modelo Específico | Capacidad Explicativa (\(R^2\)) | Error Porcentual Medio (MAPE) | Error Absoluto Medio (MAE) |
| --- | --- | --- | --- |
| **Medellín · Venta** | **\(0.835\)** | \(21.6\%\) | $120.423.210 COP |
| **Bogotá · Venta** | **\(0.830\)** | \(26.0\%\) | $212.884.753 COP |
| **Bogotá · Arriendo** | **\(0.798\)** | \(27.2\%\) | $916.029 COP / mes |
| **Medellín · Arriendo** | **\(0.758\)** | \(22.4\%\) | $538.986 COP / mes |
### 3. Detección Sistemática de Oportunidades y Gangas

Una vez entrenado el modelo, se define el **Ratio de Valoración** para cada propiedad individual:

\[\text{Ratio} = \frac{\text{Precio Pedido en Mercado}}{\text{Precio Justo Predicho}}\]

A partir de este ratio, el mercado se segmenta en tres categorías cuantitativas:

- **Ganga / Oportunidad (\(\text{Ratio} < 0.85\)):** El inmueble se ofrece con un descuento de más del \(15\%\) respecto a su valor fundamentado por área, zona y características. Ocurre en el **\(26.0\%\)** de las ofertas.
- **En Precio Justo (\(0.85 \le \text{Ratio} \le 1.15\)):** Cotiza dentro de una banda de tolerancia del \(\pm 15\%\). Concentra el **\(45.7\%\)** de los anuncios.
- **Sobrevalorado (\(\text{Ratio} > 1.15\)):** Presenta un sobreprecio especulativo superior al \(15\%\). Abarca el **\(28.3\%\)** del inventario.
**Figura 3.** Relación entre el Precio Pedido por los vendedores y el Precio Justo calculado por el algoritmo. Los puntos verdes bajo la línea punteada inferior identifican anomalías favorables de mercado: inmuebles con características de alta gama ofrecidos a precio de liquidación.
### 4. Cap Rate y Rendimiento Anual por Zonas

Para responder a la pregunta del inversionista patrimonial: *"¿Dónde es más rentable comprar una vivienda para ponerla en alquiler?"*, se calculó la **Tasa de Capitalización Bruta Anual (Gross Cap Rate)** para cada sector con densidad muestral representativa:

\[\text{Cap Rate} = \frac{\text{Canon Anual Estimado}}{\text{Precio de Compra}} \times 100 = \frac{\text{Mediana Arriendo } \text{m}^2 \times 12}{\text{Mediana Venta } \text{m}^2} \times 100\]
**Figura 4.** Ranking de las zonas con mayor retorno bruto anual por alquiler residencial tradicional. Zonas de estratos 2 y 3 y áreas periféricas exhiben mayores rendimientos porcentuales que los corredores tradicionales de estratos 5 y 6.

| Ciudad | Zona / Barrio | Cap Rate Anual | Venta m² Mediana | Arriendo m² Mediana |
| --- | --- | --- | --- | --- |
| Medellín | **Manrique** | **\(10.92\%\)** | $2.076.923 COP | $18.901 COP |
| Bogotá | **Zona Centro (Santa Fe / Mártires)** | **\(7.25\%\)** | $4.416.667 COP | $26.667 COP |
| Medellín | **Bello** | **\(7.22\%\)** | $2.909.091 COP | $17.500 COP |
| Medellín | **La Candelaria (Centro)** | **\(6.86\%\)** | $3.611.111 COP | $20.652 COP |
| Bogotá | **Zona Sur (Kennedy / Tunjuelito)** | **\(6.81\%\)** | $2.982.456 COP | $16.934 COP |
| Medellín | **San Cristóbal** | **\(6.79\%\)** | $3.368.794 COP | $19.069 COP |
| Bogotá | **Zona Suroccidental (Bosa)** | **\(6.70\%\)** | $3.000.000 COP | $16.738 COP |
| Medellín | **El Poblado** | **\(6.60\%\)** | $5.043.159 COP | $27.758 COP |

La Paradoja de la Rentabilidad Inmobiliaria

Los sectores más prestigiosos (como El Poblado en Medellín o Chapinero Norte en Bogotá) tienen precios de venta por metro cuadrado sumamente elevados, lo que comprime su rentabilidad porcentual anual tradicional al rango del \(5.5\% - 6.6\%\). En contraste, zonas intermedias o populares (Manrique, Bello, Centro) exigen un capital de entrada mucho menor y ofrecen rendimientos porcentuales brutos que superan el \(7.0\% - 10.0\%\) anual.
### 5. El Efecto Airbnb: Alquiler Vacacional vs Tradicional

Utilizando los microdatos oficiales de **Inside Airbnb Bogotá** (alojamientos completos verificados), se calculó la proyección de ingreso mensual considerando una tasa de ocupación realista y conservadora del \(65\%\) (19.5 noches facturadas al mes), comparándola con el canon de arriendo residencial de largo plazo en las mismas zonas.
**Figura 5.** Ingreso bruto mensual proyectado en las 10 localidades y zonas de Bogotá con mayor inventario de Inside Airbnb. En sectores con alta demanda turística y corporativa (Chapinero, Usaquén, Teusaquillo), el alquiler vacacional puede generar entre un \(80\%\) y un \(130\%\) más de ingresos que el alquiler convencional.

Conclusiones para la Toma de Decisiones

- **El Premio por Turismo:** En zonas como *Chapinero*, *Usaquén* y *Candelaria/Centro Histórico*, la tarifa media por noche ($140.000 - $220.000 COP) compensa con creces los costos operativos de limpieza y comisiones de plataforma, generando un flujo de caja bruto mensual de $2.8M a $4.5M COP, frente a cánones tradicionales de $1.6M a $2.5M COP.
- **El Riesgo Operativo:** El modelo Airbnb requiere administración activa, asume el riesgo de estacionalidad y está expuesto a regulaciones de propiedad horizontal (Decreto 1077 y normativas de turismo en copropiedades). Para perfiles conservadores, el arriendo tradicional a largo plazo en zonas intermedias sigue ofreciendo la mejor relación riesgo-retorno.
### 6. Guía de Decisión Estratégica

Con base en los hallazgos empíricos del estudio, se establecen cuatro directrices para los actores del mercado:

1
Para Compradores de Vivienda Propia: Exigir Descuento ante Ratios > 1.15

Casi 3 de cada 10 inmuebles en venta en Bogotá y Medellín tienen sobreprecios injustificados por el algoritmo. Antes de presentar una oferta, compare el precio pedido frente al precio justo predicho según el área real y el metro cuadrado histórico del barrio. Si el ratio supera 1.15, existe margen amplio de negociación a la baja.

2
Para Inversionistas de Rentas Tradicionales: Mirar Zonas Consolidadas de Clase Media

Zonas como Bello, Candelaria, San Cristóbal en Medellín, y Zona Sur y Centro en Bogotá, ofrecen la mejor relación costo de entrada / flujo de caja, con Cap Rates superiores al \(6.8\%\) anual. Evite comprar en estratos 6 únicamente por estatus si el objetivo principal es la rentabilidad sobre el capital invertido.

3
Para Operadores de Airbnb: Focalizarse en Estudios de 1 Alcoba en Polos Centrales

La ventaja comparativa de Airbnb se concentra en apartamentos de 1 y 2 alcobas cerca de corredores culturales, gastronómicos o financieros (Chapinero, Usaquén, Poblado, Laureles). En inmuebles de 3 o más habitaciones para familias, el arriendo tradicional suele ser más estable y menos costoso de operar.
### 7. Fuentes y Datos Abiertos

1. **Properati Colombia Dataset (Kaggle):** Archivo de 1.000.000 de avisos de propiedades residenciales y comerciales en Colombia. Publicado por Julian Usuga / Properati Open Data. URL: Kaggle Dataset
2. **Medellín Properties (Kaggle):** Dataset curado con atributos completos de 9.999 inmuebles del Valle de Aburrá. Publicado por Cesare Grassia. URL: Kaggle Dataset
3. **Inside Airbnb Bogotá (2026):** Microdatos de anuncios turísticos, precios por noche, disponibilidad y cartografía vectorial de barrios en Bogotá D.C. URL: Inside Airbnb Data
4. **Aptología (2026):** Estadísticas de arriendo por barrio, dispersión de precios p90/p10 y estudios de rotación semanal de apartamentos en Colombia. URL: Aptología Datos Abiertos



---

# Caso 2: Arquetipos de Seguridad Urbana: Clustering y Perfiles en Medellín (2019-2022)

**Dominio:** Criminología Cuantitativa, Clustering Territorial, Seguridad Ciudadana y Políticas Públicas  
**Archivo Fuente Original:** `arquetipos-seguridad-medellin.html`
Abstract / Resumen

La formulación de estrategias de seguridad ciudadana a nivel municipal suele apoyarse en agregaciones globales o en clasificaciones univariadas que invisibilizan la marcada heterogeneidad criminológica del territorio. En este artículo se propone un marco analítico reproducible para tipificar las comunas y corregimientos de Medellín mediante técnicas de aprendizaje no supervisado. A partir de 10 fuentes oficiales de microdatos (MEData) que consolidan 314.594 registros entre 2019 y 2023, se implementó un riguroso protocolo de deduplicación de hechos (obteniendo 241.676 eventos únicos), homologación espacial y estandarización de tasas por 100.000 residentes en una ventana homogénea enero–octubre.

Mediante un algoritmo \(K\text{-Means}\) (\(k=4\)) evaluado sobre 9 dimensiones (7 tasas tipológicas transformadas logarítmicamente y 2 proporciones temporales de ocurrencia), complementado con validación cruzada mediante agrupamiento jerárquico de Ward y análisis de componentes principales (PCA), se identificaron cuatro arquetipos territoriales bien diferenciados: **(1) Ladera residencial** (baja incidencia de hurto patrimonial y alta prevalencia de violencia intrafamiliar); **(2) Urbana intermedia** (hurto moderado con alta concentración de sustracción de motocicletas y automotores); **(3) Centro-sur comercial y ocio** (hiperconcentración de hurto a personas y comercios, con baja tasa de homicidios); y **(4) Rural periférico** (volúmenes delictivos absolutos muy bajos pero tasas inestables). La comuna 10 (La Candelaria) fue tratada analíticamente como una entidad atípica exógena debido a la distorsión severa provocada por la población flotante en el denominador residencial.

El análisis evolutivo 2019 \(\to\) 2022 revela una divergencia sustancial frente a la media de la ciudad (\(-2.6\%\)): comunas del arquetipo de ladera residencial como Popular (\(+14\%\)) y San Antonio de Prado (\(+19\%\)), así como Buenos Aires (\(+33\%\)), exhibieron deterioros alarmantes, mientras que zonas comerciales intermedias como Guayabal (\(-14\%\)) y Robledo (\(-10\%\)) experimentaron reducciones sistemáticas. Los hallazgos sugieren abandonar los esquemas homogéneos de patrullaje policial en favor de respuestas diferenciadas: abordaje psicosocial y preventivo intrafamiliar en laderas, frente a intervenciones situacionales y de vigilancia en corredores comerciales y de ocio nocturno.
### 1. Introducción y Contexto Territorial

Medellín, la segunda urbe en relevancia demográfica y económica de Colombia, ha experimentado durante las últimas tres décadas transformaciones estructurales profundas en sus patrones de seguridad pública. No obstante, los análisis basados en cifras agregadas metropolitanas tienden a encubrir dinámicas hiperlocales diametralmente opuestas. Mientras los homicidios y las modalidades de violencia letal han alcanzado mínimos históricos relativos, la percepción de inseguridad se ve condicionada por el comportamiento dispar de delitos de alto impacto patrimonial (hurto a personas, vehículos y residencias) y problemáticas de violencia al interior de los hogares.

Las políticas de despliegue operacional de cuadrantes de policía y programas de inversión social requieren diagnósticos objetivos que trasciendan la simple ordenación unidimensional por número de denuncias. Una comuna no es intrínsecamente "peligrosa" o "segura" de manera homogénea: la naturaleza del riesgo cambia radicalmente según la estructura socioespacial, la densidad de equipamientos urbanos y la dinámica temporal de la actividad humana. El presente estudio responde a la pregunta: *¿Es posible identificar perfiles arquetípicos estables de seguridad urbana en Medellín mediante aprendizaje estadístico no supervisado, y cuáles son las implicaciones prácticas para el diseño de políticas públicas diferenciadas?*
### 2. Adquisición, Limpieza y Preparación de Datos

Para garantizar la reproducibilidad y neutralidad del estudio, se utilizaron exclusivamente repositorios públicos abiertos del ecosistema municipal y nacional.

#### 2.1 Fuentes de Información

- **Delitos de Alto Impacto (MEData):** 10 microbases oficiales correspondientes a homicidios, hurto a personas, hurto en transporte público, hurto a residencias, hurto a establecimientos comerciales, hurto de carros, hurto de motos, lesiones personales dolosas no fatales y solicitudes de medidas de protección por violencia intrafamiliar (VIF).
- **Demografía (DANE / MEData):** Proyecciones poblacionales anuales desagregadas por comuna y corregimiento para los años 2019 y 2020, extrapoladas linealmente para las vigencias 2021 a 2023.
- **Cartografía Vectorial:** Capa oficial GeoJSON de las 16 comunas urbanas y 5 corregimientos de Medellín en sistema de coordenadas WGS84 (\(\text{EPSG:4326}\)).
- **Entorno Urbano (OpenStreetMap):** Puntos de interés georreferenciados correspondientes a establecimientos nocturnos (bares, discotecas), sucursales bancarias/cajeros automáticos, infraestructura educativa y estaciones de policía/CAIs.

#### 2.2 Decisiones Metodológicas de Curaduría

La preparación de registros delictivos presenta desafíos habituales de duplicidad administrativa y sesgos de cobertura que fueron resueltos mediante las siguientes pautas:

| Decisión Metodológica | Justificación Técnica / Impacto Empírico |
| --- | --- |
| **Deduplicación por Hecho Único** | En bases policiales, si en un mismo hurto a residencia se sustraen 4 artículos diferentes, el sistema genera 4 filas idénticas. Se construyó una clave unívoca basada en `dataset + fecha + coordenadas + barrio + modalidad`, pasando de 313.941 filas brutas a **241.676 eventos únicos** (reducción del \(23.0\%\)). |
| **Ventana Homogénea Enero–Octubre** | Dado que la vigencia 2023 en MEData presentaba corte en noviembre, se acotó estrictamente cada año al periodo 1 de enero al 31 de octubre, eliminando distorsiones por longitud desigual de las series. |
| **Exclusión del Año 2020 en el Perfil Base** | Las medidas de confinamiento estricto por la pandemia de COVID-19 alteraron sustancialmente la movilidad ciudadana y las tasas base de criminalidad callejera; 2020 se utiliza para series temporales pero se excluye de la tipificación estructural. |
| **Tratamiento Aislado de La Candelaria (Comuna 10)** | La Candelaria concentra la actividad del centro histórico y administrativo. Con una población residente de \(\approx 85.000\) personas pero más de \(1.200.000\) visitantes diarios, su tasa calculada de hurto a personas superaba los 8.000 por 100k hab. Introducirla en el agrupamiento generaba un cluster unigenerado que colapsaba la varianza del resto de comunas. Se clasificó como caso atípico estructural. |

Nota de Auditoría sobre la Cobertura 2023–2024

En la vigencia 2023, el \(12.1\%\) de los registros de delitos en MEData carece de asignación geográfica de comuna (frente a un margen inferior al \(0.9\%\) observado entre 2019 y 2022). Esto produce anomalías estadísticas artificiales (por ejemplo, corregimientos como Altavista pasan de 156 hurtos a 1 solo caso). En consecuencia, para el modelado de arquetipos y análisis evolutivo riguroso se adoptó como ventana de referencia **2019–2022**.
### 3. Ingeniería de Características y Estandarización

Para cada unidad territorial \(i \in \{1, \dots, 20\}\) y año de análisis \(t\), se computó la tasa bruta anualizada por 100.000 habitantes para cada uno de los 7 delitos:

\[\text{Tasa}_{i, k} = \frac{\sum_{t \in \{2019, 2021, 2022\}} \text{Eventos}_{i, k, t}}{\sum_{t \in \{2019, 2021, 2022\}} \text{Población}_{i, t}} \times 100.000\]

Dada la marcada asimetría positiva en la distribución de las tasas delictivas entre zonas urbanas densas y zonas semirurales, se aplicó una transformación logarítmica \(\ln(1 + \text{Tasa})\) a los 7 delitos evaluados. Adicionalmente, se calcularon dos rasgos temporales extraídos de la microdata:

1. **Proporción Nocturna (\(\text{share\_noche}\)):** Porcentaje de hechos ocurridos entre las 20:00 y las 05:59 horas.
2. **Proporción de Fin de Semana (\(\text{share\_finde}\)):** Porcentaje de hechos registrados durante sábados y domingos.

El vector final resultante de 9 variables fue normalizado mediante z-score (\(\mu=0, \sigma=1\)) antes de suministrarse a los modelos de particionamiento:

\[z_{i, j} = \frac{x_{i, j} - \bar{x}_j}{s_j}\]
### 4. Modelado No Supervisado y Perfil de los Arquetipos

Se implementó un algoritmo \(K\text{-Means}\) con inicialización \(k\text{-means++}\), evaluando soluciones con \(k \in [2, 6]\). Si bien el coeficiente de Silhouette máximo se observó en \(k=2\) (\(0.27\)), dicha partición solo separaba comunas urbanas de corregimientos rurales, perdiendo riqueza operacional. La solución con \(k=4\) arrojó una coherencia interpretativa notable y una concordancia moderada-alta frente al método jerárquico aglomerativo de Ward (Índice de Rand Ajustado, \(\text{ARI} = 0.50\)).

 FIGURA 2: CENTROIDES HEATMAP 

**Figura 1.** Perfil estandarizado de cada cluster (puntuaciones \(z\)) para los 7 delitos analizados y los dos indicadores temporales. Los valores rojos intensos señalan tasas sustancialmente superiores a la media de la ciudad; los azules representan valores por debajo de la media.

A partir de los centroides normalizados y las tasas medias reales, se formalizan los **cuatro arquetipos de seguridad** de Medellín (más el caso atípico de La Candelaria):

| Arquetipo | Comunas y Corregimientos Integrantes | Rasgos Criminológicos Distintivos | Entorno Físico y Servicios |
| --- | --- | --- | --- |
| A. Ladera Residencial | **Popular (1), Santa Cruz (2), Manrique (3), Doce de Octubre (6), San Javier (13), San Cristóbal (60), San Antonio de Prado (80)** | Baja tasa de hurto a personas (\(191\) por 100k), bajo hurto vehicular (\(72\)) y baja sustracción comercial. En contraste, presenta la **tasa más alta de violencia intrafamiliar** (\(202\) por 100k hab). | Estructura urbana de ladera, predominio residencial estratos 1 y 2. Muy baja densidad bancaria (\(0.3\) sucursales/\(\text{km}^2\)) y comercial formal. |
| B. Urbana Intermedia | **Aranjuez (4), Castilla (5), Robledo (7), Villa Hermosa (8), Buenos Aires (9), La América (12), Guayabal (15), Belén (16), Santa Elena (90)** | Niveles medios de hurto a personas (\(739\) por 100k hab), pero la **mayor tasa de hurto de vehículos** (\(235\) por 100k, con predominio de motos). Lesiones dolosas moderadas (\(128\)). | Zonas consolidadas de clases medias (estratos 3 y 4), mixtura de vivienda con corredores viales y comerciales barriales (\(1.2\) bancos/\(\text{km}^2\)). |
| C. Centro-Sur Comercial y Ocio | **El Poblado (14), Laureles-Estadio (11)** | **Máxima concentración de hurto patrimonial:** hurto a personas (\(2.226\) por 100k hab, \(11.6\) veces superior a la ladera), hurto a comercio (\(337\)) y residencias (\(146\)). Sorprendentemente, presenta la **tasa de homicidios más baja** (\(8\) por 100k). | Zonas de alta renta (estratos 5 y 6), hiperdensidad de locales de ocio nocturno (\(5.9\) bares/\(\text{km}^2\)), polos gastronómicos y entidades financieras (\(5.1\) bancos/\(\text{km}^2\)). |
| D. Rural Pequeño | **San Sebastián de Palmitas (50), Altavista (70)** | Conteos delictivos absolutos muy reducidos debido a su baja densidad poblacional. Sin embargo, ante eventos aislados de homicidio, la tasa por 100k experimenta volatilidades extremas. | Extensión territorial predominantemente rural y montañosa, con virtual ausencia de servicios financieros o de vida nocturna registrada. |
| Caso Atípico | **La Candelaria (10 · Centro)** | Tasa total consolidada de delitos \(\approx 11.000\) por 100k residentes (de 3 a 7 veces la magnitud de cualquier otra comuna). | Epicentro neurálgico del Valle de Aburrá. Concentra terminales de transporte masivo, comercio minorista masivo y máxima densidad de servicios urbanos. |

 FIGURA 4: MAPA CARTOGRÁFICO 

**Figura 2.** Distribución espacial de los arquetipos de seguridad en el municipio de Medellín. Azul: Ladera residencial; Naranja: Urbana intermedia; Rojo: Centro-sur comercial y de ocio; Verde: Rural pequeño; Gris: La Candelaria (caso atípico).
### 5. Evolución Temporal y Tendencias (2019 \(\to\) 2022)

Para examinar si los perfiles delictivos obedecen a estructuras estáticas o a procesos en transformación, se calculó la variación porcentual en la tasa delictiva global entre el periodo prepandemia (enero-octubre 2019) y la consolidación post-reactivación (enero-octubre 2022).

 FIGURA 5: TENDENCIAS 

**Figura 3.** Variación porcentual en la tasa de delitos por comuna (enero–octubre 2019 \(\to\) 2022). La línea punteada indica el promedio general de la ciudad (\(-2.6\%\)). Zonas como Buenos Aires, San Antonio de Prado y Popular exhiben crecimientos preocupantes muy por encima de la media municipal.

Divergencia Territorial Crítica

Mientras el total agregado de Medellín registró una leve mejoría de **\(-2.6\%\)** en la tasa delictiva, el comportamiento interno fue asimétrico:

- **Empeoramiento Severo (> 5 pp sobre la ciudad):** Buenos Aires (\(+33\%\)), San Antonio de Prado (\(+19\%\)), Popular (\(+14\%\)), San Cristóbal (\(+13\%\)), Belén (\(+9\%\)) y Doce de Octubre (\(+4.5\%\)). *Nótese que 4 de las 7 comunas del arquetipo de ladera residencial registraron un deterioro pronunciado.*
- **Mejoría Sostenida:** Guayabal (\(-14\%\)), La Candelaria (\(-13.5\%\)) y Robledo (\(-10\%\)).
- **Estabilidad:** Comunas de alta renta como El Poblado (\(-1\%\)) y Laureles-Estadio (\(+2\%\)) mantuvieron sus niveles delictivos estables a lo largo del cuatrienio.
### 6. Discusión y Limitaciones Metodológicas

En consonancia con las mejores prácticas en ciencia de datos y evaluación de políticas públicas, los resultados deben interpretarse bajo las siguientes salvedades:

1. **Estructura de Grupos Moderada:** Los coeficientes de Silhouette (\(0.18\) a \(0.27\)) y la concordancia entre semillas (\(\text{ARI} = 0.43\)) demuestran que los grupos constituyen una tipología descriptiva de valor táctico, no una partición discreta e inflexible. La transición espacial entre comunas intermedias y de ladera es continua.
2. **El Horario no Discrimina entre Arquetipos:** La proporción de hechos en franja nocturna oscila de manera homogénea entre el \(26\%\) y el \(30\%\) en todos los conglomerados; los horarios delictivos se distribuyen de forma similar independientemente del estrato socioeconómico.
3. **Sesgo de Subregistro y Denuncia Diferencial:** Los datos provienen exclusivamente de delitos formalmente denunciados ante Policía o Fiscalía. En comunas con presencia de grupos de delincuencia común organizada (GDCO), la coacción comunitaria reduce la denuncia de delitos cotidianos, pudiendo aparentar artificialmente menores niveles delictivos que en zonas donde la ciudadanía denuncia sistemáticamente.
4. **Distorsión por Población Flotante:** Calcular tasas por residentes per cápita sobrestima el riesgo en zonas receptoras netas de trabajadores y turistas (El Poblado, Laureles, Centro) y subestima el riesgo relativo en comunas dormitorio.
### 7. Implicaciones y Recomendaciones de Política Pública

Los resultados ofrecen una guía empírica para que la Secretaría de Seguridad y Convivencia y la Policía Metropolitana optimicen la asignación de presupuestos y capacidades operativas:

A
Arquetipo Ladera Residencial: Foco Psicosocial y Protección Familiar

Incrementar el patrullaje motorizado preventivo para disuadir hurtos resulta ineficiente en zonas donde el hurto es bajo pero la violencia intrafamiliar y las lesiones personales son críticas. Se recomienda reforzar las comisarías de familia móviles, rutas de atención a la mujer, mediación de conflictos vecinales y sistemas de alerta temprana en Popular, San Cristóbal y San Antonio de Prado (donde las tendencias delictivas van en franco deterioro).

B
Arquetipo Urbana Intermedia: Seguridad Automotriz y Patrullaje de Corredores

La prioridad en comunas intermedias como Aranjuez, Castilla y Belén debe centrarse en el hurto de motocicletas y vehículos mediante cámaras de reconocimiento automático de placas (LPR), control a talleres de autopartes y patrullaje en horarios vespertinos en corredores barriales. Se requiere una auditoría prioritaria sobre la comuna Buenos Aires para determinar las causas de su incremento de \(+33\%\).

C
Arquetipo Centro-Sur: Iluminación, Vigilancia Focalizada y Población Flotante

En El Poblado y Laureles, el hurto a personas y locales comerciales en fines de semana y horarios nocturnos requiere presencia policial mixta (pie y bicicleta), articulación con redes de comerciantes formales, mejora en luminarias y videovigilancia analítica en zonas gastronómicas y de ocio.

D
La Candelaria (Centro): Métrica de Población Flotante y Espacio Público

La medición de seguridad del Centro no puede seguir basándose en los 85.000 residentes censados. La Secretaría de Seguridad debe formular un indicador de delitos por millón de transeúntes / viajes origen-destino para evaluar con rigor el impacto real de las intervenciones policiales.
### 8. Referencias y Repositorios de Datos Abiertos

1. **MEData (Alcaldía de Medellín):** Portal oficial de datos abiertos. Datasets temáticos de *Seguridad y Defensa* (Homicidios, Hurtos, Lesiones y Violencia Intrafamiliar 2019-2023). URL: medata.app.medellin.gov.co
2. **DANE (Departamento Administrativo Nacional de Estadística):** Censo Nacional de Población y Vivienda (CNPV 2018) y Proyecciones de Población a nivel municipal y de comuna.
3. **OpenStreetMap Contributors (2024):** Extracciones vectoriales vía Overpass API de puntos de interés (POIs de ocio, comercio, educación y banca) para el polígono del municipio de Medellín.
4. **MacQueen, J. (1967):** *Some methods for classification and analysis of multivariate observations.* Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability.
5. **Rousseeuw, P. J. (1987):** *Silhouettes: a graphical aid to the interpretation and validation of cluster analysis.* Journal of Computational and Applied Mathematics, 20, 53-65.



---

# Caso 3: Modelo Predictivo de Churn con Costo-Beneficio: ¿A Quién Llamar el Lunes?

**Dominio:** Customer Analytics, Machine Learning Calibrado, Explicabilidad SHAP, Optimización Financiera  
**Archivo Fuente Original:** `caso-estudio-churn-telco.html`

ABSTRACT EJECUTIVO 

Resumen Ejecutivo (Cifra Central)

En la industria de telecomunicaciones, predecir el abandono (*churn*) carece de valor si no responde a la restricción presupuestaria de un área de retención: **contactar cuesta dinero y conceder descuentos a clientes que no se iban a marchar destruye margen**. Optimizar el corte por exactitud estadística (*Accuracy*) o F1-score es una falacia gerencial que ignora los flujos de caja.

**Conclusión Estratégica:** Contactar al **20% de clientes de mayor riesgo** priorizados por nuestro modelo Gradient Boosting Calibrado captura el **50.3% de los abandonos reales** (Lift de \(2.52\times\) sobre el azar), alcanzando un beneficio financiero neto esperado de **+$91.250 USD** en la muestra evaluada con un ROI superior al \(900\%\), frente al costo y desgaste de una campaña masiva indiscriminada.
### 1. Contexto de Negocio: La Decisión del Lunes por la Mañana

Imaginemos la reunión semanal del Comité de Retención de una empresa de telecomunicaciones. El equipo de call center tiene una capacidad limitada de llamadas mensuales y un presupuesto específico para descuentos contractuales. La pregunta operativa no es *"¿qué tan exacto es el modelo de Machine Learning?"*, sino una decisión comercial directa:

- **¿A qué clientes específicos debemos contactar este lunes?**
- **¿Con qué orden de prioridad estricto debemos asignar los agentes de retención?**
- **¿Qué tipo de oferta o intervención contractual tiene sentido para cada perfil de cliente?**
- **¿A partir de qué probabilidad de fuga una llamada deja de ser rentable y destruye dinero?**

Nuestra hipótesis metodológica central plantea que **los clientes que abandonan no constituyen un grupo homogéneo**. Existen patrones conductuales y contractuales radicalmente dispares (arquetipos de fuga) que exigen acciones diferenciadas: no es lo mismo un cliente recién llegado con fibra óptica frustrado por fallas de soporte técnico, que un cliente maduro que busca migrar a un plan con mejor precio.
### 2. Los Datos: Limpieza y Detección de Inconsistencias

Para el desarrollo de este caso de estudio utilizamos el dataset estándar de referencia **Telco Customer Churn** (publicado originalmente por IBM). Consta de **7.043 clientes y 21 atributos** que capturan servicios contratados (internet, telefonía, streaming, soporte técnico, copias de seguridad), términos del contrato (mes a mes, un año, dos años), método de facturación, cargos monetarios (mensuales y acumulados) y la variable objetivo binaria `Churn` (26,54% de abandono).

⚠️ Declaración de Transparencia Metodológica (IBM Synthetic Dataset)

El dataset de IBM está compuesto por registros sintéticos de demostración corporativa. Si bien replica con fidelidad las correlaciones y distribuciones típicas del sector telco, **sirve para demostrar método analítico y rigor de toma de decisiones**, no para extraer conclusiones categóricas sobre el comportamiento de una operadora real sin validación experimental previa.

#### Tratamiento de Inconsistencias y Fuga de Información

Durante la auditoría exploratoria detectamos que la columna `TotalCharges` contenía 11 registros almacenados como cadenas de texto en blanco (`" "`). Al cruzar estos registros descubrimos que correspondían exactamente a **clientes con antigüedad cero meses** (`tenure = 0`), es decir, clientes dados de alta recientemente que aún no habían completado su primer ciclo de facturación.

- Se convirtieron a valor numérico continuo reemplazando los espacios vacíos por `0.0`.
- Se excluyó categóricamente la columna identificadora `customerID` de cualquier matriz de modelado para prevenir sobreajuste o sesgos espurios.
- Para evitar **fuga de información (*data leakage*)**, todas las transformaciones de escala (StandardScaler) y codificación One-Hot se ajustaron exclusivamente dentro de la partición de entrenamiento (\(80\%\)), dejando el conjunto de prueba (\(20\%\), 1.409 clientes) absolutamente intacto hasta la evaluación final.
### 3. Exploración Orientada a Decisiones: ¿Cuándo y Por Qué se Van?

El análisis exploratorio de datos (EDA) no se concibió como un ejercicio descriptivo pasivo, sino como una búsqueda de palancas comerciales accionables. Al segmentar la tasa de abandono frente a factores estructurales, emergieron patrones determinantes:

**Figura 1.** Drivers críticos de abandono en telecomunicaciones. (A) Tasa de churn por tipo de contrato (el contrato mes a mes cuadruplica el riesgo). (B) Riesgo en función de la antigüedad (el 47.7% de los clientes en su primer año abandonan). (C) Vulnerabilidad tecnológica: la fibra óptica sin soporte técnico genera el mayor pico de deserción. (D) Distribución bimodal de cargos mensuales: clientes en abandono concentran sus cuotas entre $70 y $100 USD/mes.

| Factor Estructural | Subgrupo Evaluado | Tasa de Churn | Volumen de Clientes | Diagnóstico Estratégico |
| --- | --- | --- | --- | --- |
| **Tipo de Contrato** | Mes a Mes (Month-to-month) | 42,7% | 3.875 clientes | Fricción nula de salida. Máxima volatilidad y rotación. |
| Un Año (One year) | 11,3% | 1.473 clientes | Estabilidad intermedia. Ventana de riesgo en la renovación. | |
| Dos Años (Two year) | 2,8% | 1.695 clientes | Blindaje contractual. Lealtad estructural muy sólida. | |
| **Internet & Soporte** | Fibra Óptica sin Soporte Técnico | 49,4% | 2.099 clientes | Alta expectativa técnica frustrada por mala asistencia. |
| Fibra Óptica con Soporte Técnico | 22,5% | 1.000 clientes | La presencia de soporte técnico reduce el churn a la mitad. | |
| **Método de Pago** | Cheque Electrónico (Electronic check) | 45,3% | 2.365 clientes | Pago manual sujeto a fricción, demoras y reconsideración. |
| Débito Automático / Tarjeta | 16,1% | 3.066 clientes | Retención pasiva mediante automatización bancaria. | |
### 4. Arquetipos de Abandono: Segmentación No Supervisada

Siguiendo la metodología desarrollada en nuestros estudios previos (fútbol y seguridad urbana), aplicamos **Clustering K-Means** sobre el espacio multidimensional de características transaccionales y de consumo (estandarizado y codificado). La evaluación del Coeficiente de Silueta reveló que la partición en \(k=4\) clústeres optimizaba la cohesión interna y la interpretabilidad de negocio.

**Figura 2.** Perfil de riesgo de los 4 arquetipos de clientes descubiertos mediante K-Means (\(k=4\)). La tasa de deserción varía desde un crítico 53.6% en clientes nuevos con fibra de alto cargo, hasta un mínimo de 4.8% en clientes consolidados de contrato bienal.

Arquetipo 1 · Tasa de Churn: 53.6% (2.736 clientes)
Nuevos Digitales en Riesgo Crítico (Fibra & Sin Soporte)

Clientes con antigüedad muy baja (media de 14 meses), cargos mensuales elevados (\(\approx \$80 - \$90\) USD/mes), contratados bajo modalidad mes a mes y con fibra óptica, pero **sin soporte técnico ni copias de seguridad activadas**. Ante cualquier caída de velocidad o inconveniente de facturación, se marchan de inmediato.

👉 Acción Comercial: Proponer migración a contrato anual con un 20% de descuento durante los primeros 6 meses y una visita de soporte técnico / optimización wifi bonificada.

Arquetipo 2 · Tasa de Churn: 31.2% (682 clientes)
Básicos / Sensibles al Precio (Solo Teléfono / DSL Básico)

Usuarios con consumo reducido (\(\approx \$30 - \$45\) USD/mes), baja complejidad técnica y contratos flexibles. Su riesgo no proviene de la calidad del servicio, sino de ofertas agresivas de competidores *low-cost* en tarifas móviles o telefonía.

👉 Acción Comercial: Plan de fidelización "Tarifa Congelada por 12 meses" con empaquetamiento de telefonía ilimitada sin costo adicional.

Arquetipo 3 · Tasa de Churn: 12.4% (2.099 clientes)
Hogares Multiproducto en Crecimiento (Streaming & Backup)

Clientes maduros (antigüedad de 30 a 50 meses) con alto gasto mensual pero vinculados mediante paquetes familiares (TV por streaming, múltiples líneas telefónicas y contratos a 1 año). El costo de cambiar de operador es alto para ellos.

👉 Acción Comercial: Upgrade gratuito de velocidad de fibra o membresía premium de streaming a cambio de renovar su contrato anual por 24 meses.

Arquetipo 4 · Tasa de Churn: 4.8% (1.526 clientes)
Clientes VIP Consolidados (Bajo Riesgo Estructural)

Antigüedad superior a 55 meses, contratos formales a 2 años y pago automático domiciliado en tarjeta de crédito o débito bancario. Poseen toda la suite tecnológica integrada. Molestarlos con llamadas intrusivas de retención es contraproducente e ineficiente.

👉 Acción Comercial: Monitoreo pasivo. Únicamente comunicaciones de agradecimiento institucional o beneficios de lealtad sin fricción comercial.
### 5. Modelado Predictivo y Calibración de Probabilidades

Para asignar un score continuo individual, entrenamos y comparamos tres familias de clasificadores mediante **validación cruzada estratificada de 5 particiones (5-Fold Stratified CV)** sobre el 80% de los datos:

| Modelo Candidato | ROC-AUC (CV 5-Fold) | PR-AUC (Precision-Recall) | F1-Score | Exactitud (Accuracy) | Rol en la Arquitectura |
| --- | --- | --- | --- | --- | --- |
| **Regresión Logística (L2, C=0.5)** | \(0.8461 \pm 0.0128\) | \(0.6618 \pm 0.0197\) | \(0.5973\) | \(80.46\%\) | Modelo base de referencia lineal e interpretable |
| **Random Forest (200 árboles)** | \(0.8454 \pm 0.0115\) | \(0.6631 \pm 0.0198\) | \(0.5638\) | \(80.17\%\) | Ensamble de bagging no lineal con restricciones de profundidad |
| **Gradient Boosting Classifier** | **\(0.8447 \pm 0.0112\)** | **\(0.6571 \pm 0.0177\)** | **\(0.5829\)** | **\(80.14\%\)** | Modelo seleccionado para ensamble boosting y calibración |

En problemas con desbalance de clases (\(26.5\%\) positivos), el área bajo la curva Precision-Recall (**PR-AUC**) es la métrica rectora, pues penaliza fuertemente a los modelos que generan falsas alarmas masivas. Ambos ensambles superan holgadamente la línea base aleatoria (\(0.265\)).

#### ¿Por Qué Calibrar las Probabilidades? (Brier Score)

Un modelo de árbol (Random Forest o Gradient Boosting) tiende a comprimir o distorsionar las probabilidades en los extremos debido al agrupamiento de hojas terminales. Si el modelo dice que un cliente tiene una probabilidad de fuga de \(p = 0.70\), necesitamos que en la realidad, de cada 100 clientes con ese score, exactamente 70 terminen abandonando el servicio. **Si las probabilidades no están calibradas, el cálculo de los flujos de caja y el beneficio esperado será matemáticamente erróneo.**

Implementamos calibración logística de **Escalado de Platt (Sigmoid)** mediante validación cruzada interna (`CalibratedClassifierCV`), alcanzando un **Brier Score de 0.1360**.

**Figura 3.** Diagrama de confiabilidad y distribución de probabilidades calibradas. El modelo calibrado (línea verde) se ajusta con notable precisión a la diagonal de calibración perfecta, asegurando que las probabilidades asignadas reflejen fielmente el riesgo actuarial de deserción.

**Figura 4.** Curvas de Ganancia Acumulada (Cumulative Gains) y Lift por decil en el conjunto de prueba independiente (\(N=1.409\)). Contactando al 20% de mayor riesgo (Deciles 1 y 2) se intercepta al 50.3% de los desertores totales, con un Lift de 2.86x en el primer decil.
### 6. Explicabilidad con Valores SHAP: ¿Qué Empuja a Cada Cliente?

Para traducir las predicciones del modelo en argumentos de retención para los agentes telefónicos, calculamos las contribuciones marginales de Shapley mediante **TreeExplainer** sobre el 100% de la partición de prueba:

**Figura 5.** Gráfico de resumen SHAP (Beeswarm). Los puntos rojos indican valores altos de la característica; desplazamientos a la derecha indican mayor propensión al abandono. El contrato mes a mes y la baja antigüedad son las variables dominantes que empujan a los clientes hacia la deserción.

- **Contrato Mes a Mes (`Contract_Month-to-month`):** Es el vector de mayor peso positivo. La ausencia de compromiso formal actúa como un acelerador de la fuga cuando se combina con un aumento en las tarifas.
- **Antigüedad del Cliente (`tenure`):** Valores bajos (puntos azules a la derecha) elevan drásticamente la probabilidad de churn. Una vez que el cliente supera la barrera de los 24 meses, el efecto protector se consolida.
- **Fibra Óptica (`InternetService_Fiber optic`):** Genera un desplazamiento positivo hacia el churn debido al choque entre tarifas altas y calidad de servicio percibida cuando no se acompaña de soporte técnico.
- **Método de Pago (`PaymentMethod_Electronic check`):** Representa una fuente constante de fricción transaccional. La recomendación inmediata es incentivar la domiciliación bancaria.
### 7. El Motor de Costo-Beneficio: Decidir con Dinero

El núcleo distintivo de este trabajo consiste en abandonar los umbrales arbitrarios de probabilidad (\(p \ge 0.5\)) y encontrar el punto de corte exacto que **maximiza el beneficio neto de la compañía**.

Formulación Matemática del Beneficio Financiero Esperado

 \[E[\text{Beneficio Neto}_i] = p_i \cdot s \cdot (V_i - o) - c\]

Donde \(p_i\) es la probabilidad calibrada de churn, \(s\) es la tasa de éxito de la oferta de retención, \(V_i\) es el valor de permanencia retenida (Cargo Mensual \(\times\) 12 meses), \(o\) es el costo de la oferta activada, y \(c\) es el costo unitario de contactar.

#### Supuestos Base de la Campaña

- **Valor del Cliente Retenido (\(V_i\)):** Se define como el flujo de caja bruto salvado en un horizonte de 12 meses (\(\text{MonthlyCharges}_i \times 12\)). En promedio equivale a \(\approx \$780\) USD.
- **Costo Unitario de Contacto (\(c\)):** \(\$5.00\) USD por cliente contactado (tiempo de agente telefónico, línea y gestión operativa). Se incurre siempre que se contacte al usuario.
- **Costo de la Oferta de Retención (\(o\)):** \(\$18.00\) USD en bonos de servicio o descuento comercial, pero *únicamente se desembolsa si el cliente acepta la oferta y decide quedarse*.
- **Efectividad de Retención (\(s\)):** Supuesto base de \(s = 30\%\) de aceptación de la oferta de permanencia.

**Figura 6.** Curva de Retorno Financiero vs Umbral de Decisión (\(p\)). El umbral óptimo irrestricto se sitúa en \(p^* = 0.03\), donde se maximiza el beneficio neto total. Sin embargo, bajo restricciones de capacidad operativa de call center, la curva de ganancia acumulada demuestra que concentrar los recursos en el Top 20% captura más del 50% de las fugas con el menor costo y riesgo operativo.

#### Comparativa de las Tres Estrategias

Evaluamos las tres posibles políticas de gestión sobre el conjunto de prueba independiente (\(1.409\) clientes):

| Estrategia Operativa | Clientes Contactados | Costo de Campaña | Beneficio Neto Estimado | ROI Financiero | Veredicto Ejecutivo |
| --- | --- | --- | --- | --- | --- |
| **1. No Hacer Nada (Status Quo)** | 0 clientes (\(0\%\)) | $0 USD | $0 USD | 0% | Se pierden todos los clientes en abandono de forma pasiva. |
| **2. Campaña Masiva (Contactar a Todos)** | 1.409 clientes (\(100\%\)) | $9.083 USD | $90.942 USD | 1.001% | Despilfarro operativo. Molesta a clientes 100% leales y canibaliza ofertas. |
| **3. Modelo Focalizado Óptimo** | **1.213 clientes (\(86.1\%\))** | **$8.080 USD** | **$91.250 USD** | **1.129%** | **Ahorra más de $1.000 USD en costos innecesarios y captura el 99.5% de abandonos.** |
| **4. Enfoque de Capacidad Crítica (Top 20%)** | 282 clientes (\(20.0\%\)) | $2.428 USD | $52.140 USD | **2.147%** | **Máxima eficiencia de call center: captura el 50.3% del churn total con una fracción del costo.** |

**Figura 7.** Matriz de sensibilidad financiera. Se evalúa el beneficio neto máximo variando la tasa de éxito de la oferta (\(s\) entre 10% y 50%) frente al costo unitario de contacto (\(c\) entre $2 y $15 USD). La rentabilidad de la campaña se mantiene positiva y robusta en todos los escenarios realistas.

 8. SIMULADOR INTERACTIVO DE COSTO-BENEFICIO 

⚡ Simulador Interactivo de Campaña de Retención

Ajusta los supuestos de negocio y la capacidad operativa para recalcular en tiempo real el beneficio neto esperado, el costo de campaña y el retorno sobre la inversión (ROI):

Tasa de Éxito Oferta (s):
30%

Costo de Contacto (c):
$5 USD

Costo de la Oferta (o):
$18 USD

Horizonte Retenido:
12 meses

+$91,250
Beneficio Neto Test

$8,080
Costo Total Campaña

1,129%
ROI Proyectado

1,213
Clientes a Contactar
### 8. Auditoría Ética y Equidad Algorítmica

En la ciencia de datos aplicada a negocios, la responsabilidad ética es un requisito imperativo. El dataset contiene variables demográficas sensibles: `gender` (género) y `SeniorCitizen` (adultos mayores \(\ge 65\) años). Sometimos el modelo a una auditoría de impacto dispar para responder dos preguntas cruciales:

| Variable Protegida | Subgrupo | Tasa Real de Churn | Probabilidad Media Asignada | % Clasificado de Alto Riesgo | Diagnóstico de Paridad |
| --- | --- | --- | --- | --- | --- |
| **Género (gender)** | Femenino (Female) | 28,1% | 26,9% | 87,2% | Paridad Plena (Diferencia < 2%) |
| Masculino (Male) | 25,1% | 26,7% | 85,0% | | |
| **Adultos Mayores (SeniorCitizen)** | No Adulto Mayor (0) | 23,3% | 24,4% | 84,5% | Riesgo Intrínseco Mayor (Refleja el doble de rotación) |
| Adulto Mayor (1) | 44,1% | 39,4% | 94,6% | | |

**Decisión de Gobierno de Datos:** Aunque los adultos mayores sufren una mayor tasa histórica de abandono (debido a barreras digitales y plataformas de soporte automatizadas que no se adaptan a ellos), **las variables de género y edad no deben utilizarse como reglas de exclusión comercial ni de discriminación en precios**. Por ello, recomendamos enfocar las intervenciones exclusivamente en variables conductuales y transaccionales (contrato, servicios y soporte).

 10. LISTA PRIORIZADA "A QUIÉN LLAMAR EL LUNES" 

### 9. Entregable Operativo: "A Quién Llamar el Lunes"

A continuación se presenta un extracto representativo de la **lista priorizada de clientes para el área de retención**, clasificada en orden descendente por su *Beneficio Neto Esperado*:

| ID Cliente | Arquetipo Asignado | Prob. Churn Calibrada | Cargo Mensual | Antigüedad | Beneficio Esperado | Acción Prescrita para el Agente |
| --- | --- | --- | --- | --- | --- | --- |
| `7569-NMVOZ` | Nuevos Digitales Riesgo Crítico | 87.4% | $108.50 USD | 4 meses | **+$335.20 USD** | Oferta contrato anual con 20% desc. + auditoría técnica gratuita |
| `3655-SNQYZ` | Nuevos Digitales Riesgo Crítico | 84.1% | $99.20 USD | 3 meses | **+$290.40 USD** | Migración a plan fibra garantizada con soporte técnico bonificado |
| `8984-EYUSA` | Hogares Multiproducto | 68.2% | $89.50 USD | 18 meses | **+$210.15 USD** | Upgrade de streaming y doble velocidad por renovación a 24 meses |
| `4412-TWVOZ` | Básicos Sensibles al Precio | 52.3% | $45.10 USD | 8 meses | **+$78.90 USD** | Plan de retención "Tarifa Congelada" por 12 meses + bundle móvil |
| `1024-KMDEF` | Clientes VIP Consolidados | 3.2% | $115.00 USD | 62 meses | $0.00 USD | Monitoreo pasivo. No llamar (evitar canibalización y molestia) |

📥 Descargar Lista Completa Priorizada (.CSV)
### 10. Limitaciones y Protocolo para Piloto A/B

Un modelo de Machine Learning es una herramienta de asociación probabilística, **no un experimento causal**. Predecir quién tiene alto riesgo de abandonar no garantiza qué acción específica lo convencerá de quedarse. Desplegar una campaña masiva basándose ciegamente en correlaciones puede incurrir en dos errores severos:

1. **Efecto "Despertar al Perro Dormido" (Sleeping Dog effect):** Clientes en riesgo que reciben una llamada telefónica pueden recordar que tienen un contrato costoso y decidir cancelar en ese mismo instante.
2. **Gasto Inútil en No-Salva-Bles:** Clientes que ya mudaron de domicilio a una zona sin cobertura de red no pueden ser retenidos con ningún descuento.

Protocolo Recomendado: Prueba Piloto con Grupo de Control
Diseño Experimental A/B antes del Despliegue a Escala

Recomendamos seleccionar una muestra de **1.000 clientes de alto riesgo** priorizados por el modelo y dividirlos aleatoriamente:

- **Grupo Tratamiento (80% · 800 clientes):** Reciben la llamada con la oferta de retención optimizada.
- **Grupo de Control (20% · 200 clientes):** Se mantienen en monitoreo pasivo sin intervención alguna.

La diferencia en la tasa de permanencia entre ambos grupos al cabo de 90 días proporcionará la verdadera **tasa de éxito causal (\(s\))** y el retorno financiero neto exacto antes de comprometer el presupuesto total de la compañía.
### 11. Fuentes y Referencias

1. **IBM Telco Customer Churn Dataset:** Repositorio oficial de datos sintéticos de telecomunicaciones para analítica predictiva. IBM Community & Kaggle Data Repository.
2. **Platt, J. (1999):** *Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods*. Advances in Large Margin Classifiers.
3. **Lundberg, S. M., & Lee, S. I. (2017):** *A Unified Approach to Interpreting Model Predictions (SHAP)*. Advances in Neural Information Processing Systems (NeurIPS 30).
4. **Verbeke, W., Dejaeger, K., Martens, D., Hur, J., & Baesens, B. (2012):** *New insights into churn prediction in the telecommunication sector: A profit-driven approach*. European Journal of Operational Research, 218(1), 211-229.
5. **Brier, G. W. (1950):** *Verification of forecasts expressed in terms of probability*. Monthly Weather Review, 78(1), 1-3.



---

# Caso 4: Arquetipos Ganadores: Real Madrid vs Descendidos La Liga 2023-24

**Dominio:** Sports Analytics, Métricas Avanzadas de Fútbol (xG, xA, Buildup, Chain), Perfiles Tácticos  
**Archivo Fuente Original:** `arquetipos-futbol-real-madrid.html`
### 1. Introducción y Planteamiento del Problema

La composición del equipo es un factor crítico para el éxito deportivo en el fútbol profesional. Sin embargo, las organizaciones frecuentemente invierten recursos significativos en jugadores individuales sin comprender realmente qué perfiles o arquetipos de jugadores son los que verdaderamente ganan títulos.

La pregunta fundamental a la que nos enfrentamos es: *¿Existe un patrón identificable en los tipos de jugadores que poseen los equipos campeones versus los que descienden?* En la temporada 2023-24 de La Liga de España, el **Real Madrid conquistó el título**, mientras que **Almería, Cádiz y Granada descendieron**. ¿Cuál fue la diferencia fundamental en la composición de sus plantillas?

Hipótesis Central del Estudio

Los equipos ganadores no necesariamente tienen jugadores "mejores" de forma individual, sino que poseen una **combinación equilibrada y complementaria de diferentes arquetipos tácticos**. Este enfoque permite a las directivas tomar decisiones objetivas e informadas sobre qué tipos de perfiles se necesitan desarrollar o fichar.

El objetivo final es proporcionar **recomendaciones estratégicas fundamentadas en datos** que guíen futuras decisiones de transferencias, rotaciones tácticas y construcción de plantilla. Al identificar qué arquetipos están sobrerrepresentados en campeones y cuáles faltan en equipos descendidos, establecemos un marco de referencia de valor estratégico.
### 2. Exploración de Datos y Análisis

Se analizaron **489 jugadores de La Liga 2023-24** con más de 500 minutos de participación activa. El conjunto de datos incluye 27 jugadores del Real Madrid (Campeón), 74 jugadores de equipos descendidos (Almería, Cádiz, Granada) y 388 jugadores de los restantes equipos del campeonato.

Todas las métricas fueron normalizadas a **90 minutos de juego (P90)** para permitir comparaciones equitativas independientemente del volumen de minutos en cancha. Se calcularon variables avanzadas derivadas: *Goals por 90 minutos*, *Expected Goals (xG)*, *Asistencias (xA)*, *Expected Assists*, *Pases Clave (Key Passes)*, *xG Chain (goles en cadena)* y *xG Buildup (goles en fase de construcción)*.

**Figura 1:** Scatter Plot: Goals vs xG Buildup normalizado por 90 minutos, coloreado por arquetipo táctico, contrastando marcadores de Campeón (○) vs Descendidos (×).

El análisis exploratorio reveló patrones categóricos en la distribución de arquetipos. Los equipos ganadores (Real Madrid) exhiben una composición altamente especializada con fuerte peso en arquetipos ofensivos y creativos, mientras que los descendidos padecen una **sobrerrepresentación masiva de defensores puros (270 de 489 jugadores, 55%)** con mínima capacidad de aporte en ataque.

**Figura 2:** Radar Chart multidimensional evaluando el perfil distintivo de cada uno de los 4 arquetipos identificados en 5 métricas clave.

**Figura 3:** Distribución poblacional de arquetipos en La Liga 2023-24: Defensivo/Soporte (198), Distribuidor (82), Finalizador (71), Creador (58).

**Figura 4:** Probabilidad condicional de presencia en el equipo campeón por arquetipo.

#### Cuadro 1: Probabilidad de cada Arquetipo en Campeón vs Descendidos

| Arquetipo | Total Muestra | En Campeón | En Descendidos | % en Campeón |
| --- | --- | --- | --- | --- |
| **Distribuidor (Build-up / Medio)** | 8 | 8 | 0 | 100.0% |
| **Creador (Asistidor / Winger)** | 9 | 8 | 1 | 88.9% |
| **Finalizador (Goleador)** | 2 | 2 | 4 | 33.3% |
| **Defensivo / Soporte** | 18 | 2 | 16 | 11.1% |

**Figura 5:** Matriz de características (Heatmap) demostrando perfiles complementarios y disjuntos entre arquetipos tácticos.

El Hallazgo Crítico: Peligro en Fase de Construcción

Las métricas de construcción de juego resultaron decisivas: el equipo campeón generó **94.7% más xG Buildup por 90 minutos** que los equipos descendidos (0.387 vs 0.198). Esto comprueba que el Real Madrid no se limitaba a convertir ocasiones aisladas, sino que dominaba sistemáticamente la gestación del peligro colectivo.

#### Cuadro 2: Estadísticas Promedio — Campeón vs Descendidos

| Métrica Normalizada | Campeón (Real Madrid) | Descendidos (Almería, Cádiz, Granada) | Ventaja Competitiva |
| --- | --- | --- | --- |
| **xG Buildup / 90** | 0.521 | 0.147 | +252.7% |
| **xG Chain / 90** | 0.741 | 0.254 | +191.0% |
| **xA / 90** | 0.153 | 0.072 | +111.0% |
| **xG / 90** | 0.189 | 0.108 | +74.3% |
| **Key Passes / 90** | 1.173 | 0.673 | +74.2% |
### 3. Estrategia y Métodos de Ciencia de Datos

Para descubrir los arquetipos naturales sin introducir sesgos subjetivos de posiciones nominales (e.g. "lateral" o "extremo"), se implementó el algoritmo de aprendizaje no supervisado **K-Means Clustering** sobre 5 variables normalizadas: *Goals/90*, *Assists/90*, *xG Chain/90*, *xG Buildup/90* y *Key Passes/90*.

- **Preprocesamiento:** Escalado con `StandardScaler` para garantizar varianza unitaria y evitar que métricas con escalas numéricas mayores distorsionen el cálculo de distancias euclidianas.
- **Selección de Clústeres:** Se seleccionaron `k = 4` clústeres mediante el método del codo (Elbow Method) y el coeficiente Silhouette, equilibrando interpretabilidad y captura de varianza.
- **Reducción de Dimensionalidad:** Se aplicó **PCA (Principal Component Analysis)** para proyectar el espacio vectorial en dos componentes principales, explicando más del 80% de la varianza combinada.

**Figura 6:** PCA: Espacios de Arquetipos en 2D (● = Otros | ★ = Campeón Real Madrid | × = Descendidos).

La visualización PCA evidenció que los futbolistas del Real Madrid (★) se dispersan en **todos los cuadrantes del espacio dimensional**, lo que refleja máxima diversidad funcional y complementariedad. Por el contrario, los jugadores de equipos descendidos (×) se concentran densamente en una zona restrictiva de baja creación y baja finalización.
### 4. Resultados y Explicación en Contexto Organizacional

El modelo agrupó a los futbolistas en 4 arquetipos con comportamientos netamente diferenciados:

- **Finalizadores (Goleadores):** 83 jugadores en la liga (30.1% presentes en el campeón). Especializados en conversión de ocasiones (0.40 Goals/90) con modesta contribución asociativa.
- **Creadores (Asistidores / Wingers):** 109 jugadores (35.8% en el campeón). Generadores de juego decisivo y desequilibrio (0.10 Assists/90, 0.18 xG Buildup/90, 1.97 Key Passes/90).
- **Distribuidores (Build-up / Mediocampistas):** 27 jugadores (18.5% en el campeón). Especialistas en la iniciación progresiva y circulación limpia de la posesión.
- **Defensivos / Soporte:** 270 jugadores (únicamente 16.7% en el campeón). Roles con nulo o mínimo impacto ofensivo. Los descendidos dependieron de ellos en un **55% de sus minutos**.
### 5. Discusión y Decisiones Estratégicas para la Organización

A partir de estos hallazgos, se formulan cuatro directrices operativas y estratégicas aplicables a direcciones deportivas y cuerpos técnicos:

1
Reorientar la Filosofía de Fichajes: De la "Superestrella Individual" a la "Composición de Arquetipos"

Invertir recursos masivos en un delantero de 30 goles resulta inútil si el equipo no genera volumen de juego. Es sustancialmente más eficiente asegurar una plantilla con 4-5 Finalizadores que sumen colectivamente 2-3 goles/90, 3-4 Creadores que garanticen asistencias y suficientes Distribuidores para sostener la fluidez ofensiva. Los criterios de scouting deben responder a: *¿Qué arquetipo específico equilibra nuestra distribución actual?*

2
Implementar Rotaciones Estratégicas Basadas en Complementariedad

Los Defensivos Puros aportan solidez pero limitan la producción ofensiva si saturan el once inicial. Las alineaciones deben diseñarse para garantizar un umbral mínimo de Creadores y Distribuidores en cancha en todo momento, evitando esquemas sobrepoblados de perfiles no contributivos en construcción.

3
Identificar Ineficiencias de Mercado: "Jugadores Ganadores en Equipos Descendidos"

Futbolistas con perfiles cuantitativos de Creador o Distribuidor que militan en equipos que pierden la categoría suelen sufrir depreciación injustificada en su cotización de mercado. Representan oportunidades de adquisición con alto ROI, ya que poseen aptitudes probadas en la máxima categoría a la espera de un contexto colectivo favorable.

4
Instituir Métricas de Construcción (xG Buildup) como KPI Primario de Rendimiento

Evaluar el rendimiento exclusivamente por goles o victorias inmediatas conduce a sesgos por varianza de muestra pequeña. El `xG Buildup/90` precede a las anotaciones y predice la sostenibilidad del modelo de juego a mediano y largo plazo. Los clubes deben establecer metas internas cuantitativas (ej. *generar ≥ 0.45 xG Buildup/90 colectivo*).
### 6. Conclusión General

El análisis en La Liga 2023-24 concluye que el campeonato no es producto del azar ni exclusivo de individualidades aisladas, sino de una **armonía estructural entre arquetipos complementarios**. Mientras el Real Madrid conjugó una máquina generadora de ocasiones (+94.7% xG Buildup) con finalización distribuida (+68.5% Goals), los equipos descendidos colapsaron bajo una estructura defensiva pasiva que hipotecó su producción ofensiva.
### 7. Referencias Bibliográficas

1. **Yoon Hyup Hwang.** (2019). *Hands-On Data Science for Marketing: Improve Your Marketing Strategies with Machine Learning Using Python and R*. Packt Publishing, pp. 186–417.
2. **Kaggle.** (s. f.). Datos abiertos y repositorios comunitarios de fútbol.
3. **Ministerio de Tecnologías de la Información y las Comunicaciones.** (2022). *Datos abiertos Colombia*.
4. **Milgram, A.** (2014). *Why smart statistics are the key to fighting crime*. TED Conferences.
5. **Slavin, K.** (2011). *How algorithms shape our world*. TED Conferences.
6. **Webb, A.** (2013). *How I hacked online dating*. TED Conferences.
7. **Franks, I. M., & Hughes, M.** (2016). *Soccer Analytics: Successful Coaching Through Match Analysis*. Meyer & Meyer Sport.
8. **Winston, W. L., Nestler, S., & Pelechrinis, K.** (2022). *Mathletics: How Gamblers, Managers, and Fans Use Mathematics in Sports*. 2ª ed. Princeton University Press.
9. **Sumpter, D.** (2016). *Soccermatics: Mathematical Adventures in the Beautiful Game*. Bloomsbury Publishing.

