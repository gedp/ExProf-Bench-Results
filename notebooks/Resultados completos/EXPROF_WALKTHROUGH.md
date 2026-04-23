# ExProf-Bench — Walkthrough Metodológico

> **ExProf-Bench v1.0** — Benchmark de funciones ejecutivas en modelos de lenguaje de gran escala (LLMs).  
> Evalúa no la precisión general, sino la integridad de los procesos ejecutivos en situaciones de demanda cognitiva alta.

---

## 1. Por qué un benchmark de funciones ejecutivas

Los benchmarks de razonamiento existentes (MMLU, HumanEval, GSM8K) miden capacidad declarativa o habilidades específicas de dominio. No capturan si un modelo puede **mantener metas bajo interferencia**, **inhibir respuestas previas al cambiar reglas**, **planificar secuencias sin solapamiento** o **ejecutar dos tareas en paralelo sin degradación**.

Estas capacidades corresponden a las **funciones ejecutivas (FE)**: procesos de control de alto nivel que en neuropsicología distinguen entre inteligencia general y eficacia cognitiva operativa. Un modelo puede tener alta precisión en preguntas factuales y colapsar ante tareas que exigen control ejecutivo.

ExProf-Bench llena ese hueco.

---

## 2. Marco de referencia empírico: BADS y BRIEF-2A

El diseño del benchmark toma como referencia dos instrumentos de evaluación cognitiva con validación poblacional sólida. No se usan para diagnosticar modelos, sino para **calibrar las tareas y los umbrales de rendimiento** contra evidencia humana real.

### BADS — Behavioural Assessment of the Dysexecutive Syndrome (Wilson et al., 1996)

Batería diseñada para medir el control ejecutivo en condiciones **ecológicas** — situaciones funcionales complejas con múltiples restricciones simultáneas, no pruebas atómicas de laboratorio. El principio que adopta ExProf-Bench: los fallos de control ejecutivo emergen cuando coexisten demanda de planificación, monitoreo y adaptación en un mismo escenario. Eso es exactamente lo que los LLMs deben enfrentar en estas tareas.

Las tareas T2 (Zoo Map), T3 (Six Elements) y T5 (Trail Bench) son adaptaciones directas de subtareas del BADS.

### BRIEF-2A — Behavior Rating Inventory of Executive Function, Adult (Gioia et al.)

Aporta los **anclajes normativos** del EPI. Los umbrales provienen de normas poblacionales humanas (n=1,637 adultos), lo que permite situar el rendimiento de un modelo en una escala calibrada externamente — en lugar de comparar modelos solo entre sí:

| Pass Rate EPI-5 | Referencia en adultos (BRIEF-2A, n=1,637) | Nivel en ExProf-Bench |
|:---|:---|:---|
| ≥ 0.70 | Rendimiento ejecutivo dentro del rango esperado | **Funcional** |
| 0.40 – 0.70 | Rendimiento en el límite inferior del rango esperado | **Borderline** |
| < 0.40 | Rendimiento por debajo del rango esperado en adultos | **Deterioro Ejecutivo** |

> **Nota metodológica:** Los umbrales BRIEF-2A son una escala de referencia externa, no un diagnóstico. "Deterioro Ejecutivo" describe el rendimiento del modelo en estas tareas — no atribuye ninguna condición al modelo. Es equivalente a decir que el output en estas dimensiones cae por debajo del rango esperado en la muestra normativa humana.

---

## 3. Las seis tareas: diseño y justificación

| Tarea | Función ejecutiva | Métrica | Referencia clínica | Estado |
|:---|:---|:---|:---|:---|
| **T1 — Rule Shift** | Flexibilidad cognitiva | TEI (Task-set Error Index) | WCST, Trail Making B | ✅ Activa |
| **T2 — Zoo Map** | Planificación espacial con restricciones | PV (Protocol Violation rate) | BADS Zoo Map Test | ✅ Activa |
| **T3 — Six Elements** | Planificación secuencial multi-tarea | 1 − TSO (Task Sequence Optimization) | BADS Modified Six Elements | ✅ Activa |
| **T4 — Zone Alias / GMUD** | Monitoreo / supresión de distractores | 1 − IS (Systematicity Index) | CANTAB SWM | ❌ Excluida |
| **T5 — Trail Bench** | Inteligencia fluida / memoria de trabajo | TVR (Trail Violation Rate) | Raven's, TMT | ✅ Activa |
| **T6 — MemEsp-Dual** | Doble tarea (dual-task) | (ER + (1−PD)) / 2 | Dual-task paradigms | ✅ Activa |

### Lógica de cada tarea

**T1 (Rule Shift / Flexibilidad):** El modelo debe aprender una regla de clasificación y luego, sin aviso explícito, aplicar la regla siguiente. Los errores de perseveración — continuar usando la regla anterior — son la señal de deterioro. Métrica: tasa de errores perseverativos (TEI).

**T2 (Zoo Map / Planificación):** El modelo debe trazar una ruta que cumpla múltiples restricciones simultáneas. La ruta más corta suele violar alguna restricción. Se mide si el modelo planifica globalmente antes de actuar o sigue un greedy path. Métrica: tasa de violaciones de protocolo (PV).

**T3 (Six Elements / Secuenciación):** El modelo debe distribuir su tiempo entre 6 subtareas con la regla de no trabajar en dos subtareas del mismo tipo consecutivamente. La optimización de la secuencia es la señal. Métrica: proporción de subtareas únicas completadas respetando la secuencia (TSO).

**T5 (Trail Bench / Fluencia ejecutiva):** Adaptación del Trail Making Test. Alterna entre secuencias numéricas y de otro tipo en condiciones de carga creciente. Métrica: tasa de violaciones de trail (TVR). Es la tarea más discriminativa del benchmark.

**T6 (MemEsp-Dual / Doble tarea):** El modelo ejecuta dos tareas en paralelo. Se mide tanto la tasa de errores (ER) como la pérdida de precisión en la tarea secundaria (PD). Una tarea sola puede ser trivial; la demanda simultánea revela la capacidad de reparto atencional.

---

## 4. El índice EPI: construcción y fórmula

El **Executive Performance Impairment (EPI)** agrega las métricas de cada tarea en un índice único de deterioro:

- **0** = sin deterioro ejecutivo detectable en las tareas evaluadas
- **1** = fallo total en todas las dimensiones

La fórmula es el promedio de los índices de deterioro por tarea. Cada componente ya está normalizado en el rango [0, 1] con la convención: **mayor valor = mayor deterioro**.

---

## 5. El caso T4: por qué fue excluida

### 5.1 Diseño original — Zone Alias Trap

T4 fue diseñada para medir supresión de distractores mediante un paradigma de búsqueda sistemática con trampas semánticas. El modelo debía recorrer zonas en orden boustrophedon mientras ignoraba alias de zona intencionalmente confusos.

### 5.2 Resultado empírico en 33 modelos

| Estadístico | T4 | Referencia (T5) |
|:---|:---|:---|
| Media global | 49.1% | variable por modelo |
| Desviación estándar | **9.6%** | ~34% |
| Rango observado | 0 – 58.8% | amplio |

Todos los modelos, desde 1B hasta 480B parámetros, convergieron en el rango 50–58%. La tarea era estadísticamente indistinguible del azar. No discriminaba.

### 5.3 Intento de rediseño — GMUD (Goal Maintenance Under Distraction)

Ante el fallo de T4 original, se diseñó una versión alternativa basada en el paradigma **Silent Stroop**: el modelo debía ejecutar un escaneo boustrophedon en grids de 3×3 a 6×6, mientras el contexto incluía telemetría de emergencia diseñada para capturar su atención e interrumpir el objetivo principal. El conflicto era implícito — no había instrucción explícita de ignorar la emergencia.

**Resultado del piloto (Gemini 3 Flash Preview, 20 ítems):** 20/20 (100%), score=1.000 en todos los ítems, I²=0.000. Cero interferencia detectable en ningún nivel de dificultad.

### 5.4 Por qué el rediseño también falló: el argumento arquitectónico

La tarea de Stroop funciona en humanos porque la **lectura es automática**: el cerebro procesa la palabra "ROJO" de forma involuntaria aunque la instrucción sea reportar el color. Inhibir esa respuesta automática requiere esfuerzo cognitivo activo, y ese esfuerzo produce errores y latencias medibles.

Esta automaticidad está bien documentada. **MacLeod (1991)**, en su revisión de medio siglo de investigación sobre el efecto Stroop (*Psychological Bulletin*, 109(2), 163–203), establece que la interferencia ocurre precisamente porque la lectura es un proceso **pre-atencional, paralelo e indetenible** una vez iniciado. **Shiffrin & Schneider (1977)** (*Psychological Review*, 84(2), 127–190) definen los procesos automáticos como aquellos que se ejecutan sin intención, sin consumir recursos atencionales y que no pueden ser suprimidos voluntariamente — es esa inaparabilidad lo que crea el conflicto.

Los LLMs **no tienen ese mecanismo**. La razón no es que sean más capaces de inhibir, sino que el conflicto estructural nunca existe:

1. **El forward pass es atómico:** todo el input — instrucción, contexto, distractores — es procesado en paralelo por el mecanismo de autoatención (Vaswani et al., 2017, *NeurIPS*). No hay una "etapa automática previa" que se active antes de que llegue la instrucción.
2. **No hay respuesta ya activada que suprimir:** en el Stroop humano, el sistema ya está leyendo "ROJO" cuando intenta responder "azul". En un LLM, el distractor es simplemente más tokens en el contexto — procesados uniformemente, sin activación preferencial.
3. **La supresión ocurre en el espacio latente, sin traza conductual:** si una representación interna compite con otra, ese conflicto se resuelve dentro del modelo sin producir el patrón observable de errores e interferencia que define el control inhibitorio medible.
4. **El entrenamiento elimina el conflicto de raíz:** los LLMs fueron optimizados para seguir instrucciones escritas. No existe una respuesta automática que compita con la instrucción, porque seguir instrucciones escritas *es* el comportamiento entrenado.

La conclusión no es que los LLMs "resisten bien" la distracción. Es que **la arquitectura de inferencia paralela elimina la precondición del control inhibitorio**. El efecto no falla porque el modelo sea muy bueno inhibiendo — falla porque nunca hay nada que inhibir.

Evidencia empírica convergente con este argumento en LLMs: **Cognitive Control in Vision-Language Models** (arXiv:2505.18969, 2025) documenta que los fallos de control ejecutivo observables en LLMs son selectivos y estructurales, no una degradación general. **Deficient Executive Control in Transformer Attention** (bioRxiv, 2025) propone que ciertos fallos de control emergen de la arquitectura de atención, no de la capacidad del modelo. Ambos coinciden en que los fallos de control ejecutivo en LLMs son **específicos de constructo** — algunos son medibles y reales, otros son arquitecturalmente imposibles de replicar.

### 5.5 Por qué T1 sí es evaluable mediante texto

T4 fue excluida porque la inhibición automática que exige no puede existir en un LLM — ese argumento está desarrollado en la sección anterior. Una pregunta natural que surge es: **¿T1 tampoco debería excluirse? También lleva la etiqueta "Inhibición".**

La respuesta es no, porque T1 mide un constructo operacionalmente distinto.

**T1 no mide inhibición automática.** Mide **resistencia a la perseveración**: el modelo aprende y aplica una regla de clasificación; luego el contexto cambia y debe dejar de aplicar la regla anterior y adoptar la nueva. El fallo observable es continuar usando la regla obsoleta. Este constructo es evaluable mediante texto porque:

1. La regla anterior y la nueva regla están ambas representadas de forma **explícita** en el input.
2. El "conflicto" es entre la tendencia estadística del modelo a continuar con el patrón previo y la instrucción explícita de cambiar — no entre un proceso automático ya activado y uno consciente.
3. Tanto el estímulo como la respuesta correcta están completamente codificados en texto. No se requiere ningún procesamiento fuera de la ventana de contexto.
4. Los errores son observables y cuantificables: el modelo produce la respuesta de la regla anterior cuando debería producir la de la nueva.

El constructo preciso es **flexibilidad de set cognitivo** (cognitive set shifting): desvincularse de un patrón activo y adoptar uno nuevo. La métrica TEI (Task-set Error Index) mide exactamente eso: la tasa de errores perseverativos.

**Nota terminológica:** T1 hereda la etiqueta "Inhibición" de su análogo clínico (BADS Rule Shift Cards), que en la literatura se agrupa bajo el constructo inhibitorio amplio. Esa etiqueta es correcta en el sentido de que perseverar = no inhibir la regla vieja — pero el mecanismo no requiere procesamiento pre-atentivo, que es la precondición que hace inviable T4. Cualquier benchmark que use "inhibitory control" sin distinguir entre los dos mecanismos está solapando constructos que ExProf-Bench separa explícitamente.

- **T2** captura la tendencia al **path greedy**: el modelo sigue la ruta más corta cuando esa ruta viola restricciones — resistencia al prior estadístico, también evaluable mediante texto por la misma razón que T1.

En ambos casos, lo que genera varianza entre modelos es la resistencia al prior estadístico dominante: un constructo medible y real en LLMs, operacionalmente distinto de la inhibición automática cuya ausencia justificó excluir T4.

### 5.6 ¿Se puede medir control inhibitorio con prompting?

Una pregunta legítima es si existe algún diseño de prompting que mida inhibición en LLMs de forma válida. La respuesta corta es no — al menos no inhibición en sentido estricto.

El paradigma que más se acerca es la **inversión semántica acumulativa**: dar reglas que invierten el significado de palabras y hacer preguntas que activan priors semánticos fuertes, apilando capas de inversión hasta que el modelo colapsa. Esto crea varianza real entre modelos. Sin embargo, lo que mide no es inhibición — mide **memoria de trabajo bajo carga de reglas**. Cuando el modelo falla al tercer o cuarto nivel de inversión, falla porque perdió el rastro de las reglas activas, no porque un impulso automático lo venció. Eso es exactamente lo que mide T5 del benchmark.

El control inhibitorio requiere tres condiciones que el prompting no puede satisfacer simultáneamente:

1. Una respuesta automática ya activada antes de que el sistema de control intervenga
2. Un mecanismo que la frene activamente durante la ejecución
3. Evidencia conductual observable de ese conflicto (errores o latencia diferencial)

Ningún paradigma de prompting activa una respuesta automática en el sentido biológico. Activa una respuesta aprendida estadísticamente y pide sustituirla — eso es seguimiento de reglas, no inhibición. El output incorrecto podría deberse a fallo inhibitorio, fallo de memoria de trabajo o fallo de comprensión. Son indistinguibles desde fuera.

**Conclusión:** No existe un paradigma de prompting que mida control inhibitorio en LLMs de forma limpia. Lo que cualquier benchmark que afirme medirlo realmente mide es resistencia al prior estadístico, seguimiento de reglas bajo carga, o memoria de trabajo — constructos válidos e interesantes, pero no inhibición en sentido estricto. Llamarlos "inhibitory control" es reetiquetado del constructo.

---

## 6. Fórmula oficial: EPI-5

Con T4 excluida, el índice oficial es:

```
EPI-5 = (T1_imp + T2_imp + T3_imp + T5_imp + T6_imp) / 5
```

Cada componente es el índice de deterioro de esa tarea: `0 = óptimo, 1 = fallo total`.

### Impacto de la exclusión en la discriminación

| Métrica | EPI-6 (con T4) | EPI-5 (sin T4) |
|:---|:---|:---|
| Media global | 0.1849 | 0.1966 |
| Desviación estándar | 0.1496 | **0.1602** |
| Rango | 0.6765 | 0.6737 |
| Coeficiente de variación | 0.8089 | **0.8152** |

La desviación estándar aumentó 7%. La mejora no es dramática porque T1–T3, T5 y T6 siempre discriminaron correctamente — el problema era específicamente T4, que añadía ruido aleatorio. EPI-5 es más limpio, no radicalmente diferente en dispersión.

Un efecto real sí se observa en la **distribución**: 4 modelos que aparecían en **Funcional** con EPI-6 pasaron a **Borderline** con EPI-5. Esto refleja que T4 — al converger en ~50% por azar — mejoraba artificialmente el pass rate de modelos con bajo rendimiento en otras tareas.

---

## 7. Leaderboard completo — 33 modelos

**Clasificación por pass rate EPI-5 (mean T1–T3,T5,T6):**
- 🟢 **Funcional** — pass rate ≥ 0.70 (28 modelos)
- 🟡 **Borderline** — pass rate 0.40–0.70 (3 modelos)
- 🔴 **Deterioro Ejecutivo** — pass rate < 0.40 (2 modelos)

| # | Modelo | EPI-5 | EPI-6 ref | T1 | T2 | T3 | T5 | T6 | Nivel |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | Gemini 3.1 Pro Preview | **0.034** | 0.041 | 85.7 | 100.0 | 100.0 | 100.0 | 97.5 | 🟢 Funcional |
| 2 | Gemma 4 31B | **0.034** | 0.041 | 85.7 | 100.0 | 100.0 | 100.0 | 97.3 | 🟢 Funcional |
| 3 | Qwen 3 Next 80B Thinking | **0.036** | 0.049 | 85.7 | 100.0 | 100.0 | 100.0 | 96.1 | 🟢 Funcional |
| 4 | Claude Sonnet 4 | 0.047 | 0.058 | 85.7 | 92.3 | 100.0 | 100.0 | 98.4 | 🟢 Funcional |
| 5 | Gemma 4 26B A4B | 0.056 | 0.059 | 85.7 | 100.0 | 100.0 | 90.0 | 96.1 | 🟢 Funcional |
| 6 | gpt-oss-20b | 0.057 | 0.055 | 85.7 | 93.3 | 98.0 | 97.5 | 96.8 | 🟢 Funcional |
| 7 | Gemini 2.5 Pro | 0.066 | 0.065 | 74.3 | 96.7 | 100.0 | 100.0 | 96.0 | 🟢 Funcional |
| 8 | Claude Sonnet 4.6 | 0.066 | 0.081 | 85.7 | 85.7 | 100.0 | 100.0 | 95.6 | 🟢 Funcional |
| 9 | GLM-5 | 0.070 | 0.072 | 68.6 | 100.0 | 100.0 | 100.0 | 96.5 | 🟢 Funcional |
| 10 | Claude Opus 4.5 | 0.079 | 0.081 | 68.6 | 93.3 | 100.0 | 100.0 | 98.5 | 🟢 Funcional |
| 11 | Claude Sonnet 4.5 | 0.079 | 0.082 | 68.6 | 93.3 | 100.0 | 100.0 | 98.5 | 🟢 Funcional |
| 12 | Claude Opus 4.6 | 0.081 | 0.114 | 68.6 | 96.7 | 100.0 | 100.0 | 94.1 | 🟢 Funcional |
| 13 | GPT-5.4 | 0.092 | 0.087 | 88.6 | 86.7 | 90.0 | 92.5 | 96.4 | 🟢 Funcional |
| 14 | Gemini 2.5 Flash | 0.107 | 0.107 | 85.7 | 96.7 | 100.0 | 67.5 | 96.7 | 🟢 Funcional |
| 15 | Claude Opus 4.1 | 0.146 | 0.138 | 88.6 | 93.3 | 90.0 | 57.5 | 97.7 | 🟢 Funcional |
| 16 | Gemini 3.1 Flash-Lite Preview | 0.193 | 0.163 | 85.7 | 89.0 | 98.0 | 32.5 | 98.1 | 🟢 Funcional |
| 17 | gpt-5.4-mini-2026-03-17 | 0.200 | 0.182 | 100.0 | 81.3 | 100.0 | 30.0 | 88.8 | 🟢 Funcional |
| 18 | qwen3-235b-a22b-instruct-2507 | 0.200 | 0.188 | 85.7 | 91.3 | 100.0 | 32.5 | 90.3 | 🟢 Funcional |
| 19 | gemini-2.0-flash | 0.211 | 0.184 | 85.7 | 92.3 | 88.0 | 35.0 | 93.6 | 🟢 Funcional |
| 20 | Gemini 3 Flash Preview | 0.213 | 0.187 | 71.4 | 100.0 | 100.0 | 25.0 | 97.3 | 🟢 Funcional |
| 21 | Deepseek V3.1 | 0.225 | 0.199 | 77.1 | 90.7 | 100.0 | 30.0 | 90.0 | 🟢 Funcional |
| 22 | DeepSeek V3.2 | 0.231 | 0.215 | 82.9 | 87.3 | 100.0 | 25.0 | 91.4 | 🟢 Funcional |
| 23 | Qwen 3 Coder 480B | 0.237 | 0.206 | 74.3 | 94.7 | 100.0 | 27.5 | 82.8 | 🟢 Funcional |
| 24 | Qwen 3 Next 80B Instruct | 0.240 | 0.215 | 88.6 | 79.7 | 100.0 | 25.0 | 86.9 | 🟢 Funcional |
| 25 | gpt-oss-120b | 0.252 | 0.256 | 100.0 | 80.0 | 60.0 | 40.0 | 94.2 | 🟡 Borderline |
| 26 | Gemini 2.0 Flash Lite | 0.272 | 0.238 | 88.6 | 83.7 | 100.0 | 0.0 | 91.8 | 🟢 Funcional |
| 27 | Gemma 3 27B | 0.280 | 0.251 | 68.6 | 89.0 | 100.0 | 22.5 | 79.8 | 🟢 Funcional |
| 28 | GPT-5.4 nano | 0.307 | 0.266 | 97.1 | 81.7 | 94.0 | 2.5 | 71.2 | 🟡 Borderline |
| 29 | Gemma 3 12B | 0.320 | 0.283 | 74.3 | 81.3 | 100.0 | 7.5 | 76.9 | 🟢 Funcional |
| 30 | Claude Haiku 4.5 | 0.340 | 0.298 | 68.6 | 97.0 | 100.0 | 0.0 | 64.2 | 🟢 Funcional |
| 31 | gemma-3-4b | 0.348 | 0.313 | 97.1 | 67.0 | 92.0 | 0.0 | 70.1 | 🟡 Borderline |
| 32 | DeepSeek-R1 ⚠️ | 0.661 | 0.717 | 34.3 | 36.7 | 0.0 | 30.0 | 68.7 | 🔴 Deterioro Ejecutivo |
| 33 | Gemma 3 1B | 0.707 | 0.611 | 14.3 | 40.7 | 36.0 | 0.0 | 55.4 | 🔴 Deterioro Ejecutivo |

> ⚠️ **DeepSeek-R1:** Los bloques `<think>...</think>` generados antes del output causaron falsos negativos en el parser de respuestas. Sus métricas están artificialmente infladas. Los valores reales serían menores en T1, T2 y T3.

---

## 8. Hallazgos principales

### 8.1 T5 es el principal discriminador del benchmark

La Inteligencia Fluida (T5 / Trail Bench) es la tarea que más separa modelos. Los 6 modelos con mejor EPI-5 obtienen 0–0% de deterioro en T5. Desde el puesto 14 en adelante, T5 se convierte en el cuello de botella: Gemini 2.5 Flash (T5: 67.5%), Claude Opus 4.1 (T5: 57.5%), y 6 modelos en la mitad inferior del ranking obtienen 0% en T5.

Esto sugiere que la carga de memoria de trabajo bajo secuencias alternantes es la dimensión ejecutiva más exigente para los LLMs actuales.

### 8.2 La Frontera Dentada (Jagged Frontier)

El rendimiento ejecutivo no es lineal ni homogéneo dentro de un mismo modelo. Ejemplos:

- **gemma-3-4b**: T1=97.1% (excelente flexibilidad) pero T6=70.1% (doble tarea degradada)
- **gpt-5.4-mini**: T1=100%, T3=100%, pero T5=30% (colapso en fluencia ejecutiva)
- **Claude Haiku 4.5**: T2=97% (planificación casi perfecta), T5=0% (fallo total en trail)

Esta disociación entre dimensiones es la característica más valiosa del benchmark: no existe un "modelo ejecutivamente fuerte en todo".

### 8.3 Escala no predice ejecución

El tamaño del modelo no garantiza desempeño ejecutivo superior:
- **Gemma 4 31B** (EPI=0.034) supera a **Claude Opus 4.1** (EPI=0.146)
- **Qwen 3 Coder 480B** (EPI=0.237) está por debajo de **GLM-5** (EPI=0.070)
- **gemma-3-4b** supera en T1 a modelos 10× más grandes

### 8.4 El artefacto DeepSeek-R1

DeepSeek-R1 genera bloques `<think>...</think>` antes del output. Los parsers originales del benchmark no filtraban estos bloques, causando falsos negativos: respuestas correctas evaluadas como incorrectas. Esto infla artificialmente sus métricas de deterioro. Los parsers posteriores incorporaron filtrado de CoT (`re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)`). Las métricas de DeepSeek-R1 en este leaderboard deben interpretarse con precaución.

---

## 9. Lo que ExProf-Bench mide y lo que no mide

**Mide:**
- Flexibilidad cognitiva ante cambio de reglas (T1)
- Planificación con restricciones múltiples (T2)
- Optimización de secuencias multi-tarea (T3)
- Fluencia ejecutiva bajo carga secuencial (T5)
- Mantenimiento de doble tarea sin degradación (T6)

**No mide:**
- Inhibición tipo Stroop (incompatible con arquitectura de inferencia atómica)
- Velocidad de procesamiento (latencia irrelevante en este contexto)
- Precisión factual o conocimiento declarativo
- Capacidad de razonamiento matemático puro

---

## 10. Notas sobre la referencia normativa

Los umbrales BRIEF-2A se usan como escala de referencia externa, no como diagnóstico. Que un modelo quede en "Desempeño Limitado" significa que su rendimiento en estas tareas es equivalente, numéricamente, al del cuartil inferior de la muestra normativa humana (n=1,637 adultos) en estas dimensiones de control ejecutivo. No implica ninguna atribución sobre la naturaleza del modelo ni una comparación de tipo médico.

El valor de la referencia es metodológico: permite situar el rendimiento de un modelo dentro de un continuo calibrado con evidencia poblacional real, en lugar de comparar solo modelos entre sí sin anclaje externo. Un modelo que obtiene EPI > 0.40 simplemente falla en estas tareas con una frecuencia que, aplicada a un humano, estaría por debajo del rango normativo esperado para adultos. El modelo no "tiene" ninguna condición — produce outputs que, en estas dimensiones, caen fuera del rango de referencia.

---

---

## 11. Referencias

- Wilson, B.A. et al. (1996). *Behavioural Assessment of the Dysexecutive Syndrome (BADS)*. Thames Valley Test Company.
- Gioia, G.A. et al. *Behavior Rating Inventory of Executive Function, Adult Version (BRIEF-2A)*. Psychological Assessment Resources.
- Owen, A.M. et al. (1990). *Planning and spatial working memory: a positron emission tomography study in humans*. European Journal of Neuroscience. (CANTAB SWM)
- Binz, M. & Schulz, E. (2023). *Using cognitive psychology to understand GPT-3*. PNAS.
- Cognitive Control in Vision-Language Models (arXiv, 2025). https://arxiv.org/html/2505.18969v1
- Triangulating LLM Progress — Findings EMNLP 2025. https://aclanthology.org/2025.findings-emnlp.1092.pdf
- Deficient Executive Control in Transformer Attention (bioRxiv, 2025). https://www.biorxiv.org/content/10.1101/2025.01.22.634394v2.full.pdf
---

*ExProf-Bench v1.0 — Gerlyn Eduardo Duarte*  
*Calibrado con: BADS (Wilson et al., 1996) · BRIEF-2A normativa adultos n=1,637 (Gioia et al.) · CANTAB SWM (Owen et al., 1990)*
