# Entrevista inicial

Objetivo: conocer a la persona y su trabajo lo suficiente para decidir la
arquitectura de carpetas y preparar el entorno, **sin cansarla**. La
entrevista va **después** de leer la carpeta (SKILL.md, paso 2): lo que la
persona ya haya dicho en la conversación o lo que digan sus documentos se da
por respondido y no se pregunta dos veces.

Reglas de la entrevista:

- **Casi todo se elige, no se escribe.** Las preguntas van con
  `AskUserQuestion` y opciones armadas con lo que ya se sabe (la carpeta, su
  hoja de vida, el cargo). Las preguntas abiertas son como mucho dos, y se
  responden en una línea.
- **Nada de respuestas largas o complejas.** Si la persona escribe mucho, no
  le pidas más: resume tú y confírmalo con una opción.
- **Cada pregunta dice para qué sirve**, en pocas palabras, en la misma
  pregunta o en su descripción.

## 1. Apertura — por qué se pregunta y qué pasa con los datos

Un solo mensaje corto, antes de la primera pregunta. Adapta el tono, pero
conserva las tres ideas: para qué sirve, qué puede compartir y qué pasa con
sus datos.

> Voy a preparar tu espacio de trabajo. Para ayudarte bien en tu cargo
> necesito entender qué haces, qué entregas y qué sabes hacer: así sé qué
> temas dominar, cómo ordenar tus carpetas y qué tareas puedo hacer contigo
> desde el primer día. Son unas pocas preguntas, casi todas para elegir.
>
> Si quieres ahorrar preguntas, compárteme lo que tengas a mano (todo es
> opcional):
> - **Tu hoja de vida en PDF**, para saber qué habilidades tienes y cuáles
>   debo aportar yo.
> - **Tu perfil de LinkedIn descargado en PDF** (en tu perfil: «Más» →
>   «Guardar en PDF»). El enlace solo a veces funciona, porque LinkedIn no
>   deja ver los perfiles sin iniciar sesión.
> - **Un enlace o documento del proyecto** (sitio web, presentación,
>   propuesta, brief).
>
> Puedes arrastrar el archivo a esta ventana o dejarlo en tu carpeta. Lo que
> me compartas lo uso solo para ayudarte en tu trabajo: queda guardado en tu
> carpeta, no se publica y no lo comparto con otras personas. No me pases
> contraseñas ni claves.

Sobre los datos, di solo lo que es cierto: lo que la persona comparte se
procesa en esta conversación con Claude para poder ayudarle, se guarda en su
carpeta y no se publica ni se envía a nadie más. **No prometas** que «la IA
no lo ve»: la ve, porque es la que la lee. Si pregunta por el tratamiento de
sus datos por parte del servicio de Claude, remítela a la política de
privacidad de su cuenta o de su organización.

Con lo que comparta:

- **Hoja de vida o perfil de LinkedIn:** sacar solo lo profesional (cargo
  actual, experiencia, estudios, habilidades, herramientas, idiomas, sector).
  Nunca se guardan su documento de identidad, teléfono, dirección, fecha de
  nacimiento ni nada personal. Las habilidades van a `perfil.habilidades`.
  Al comparar con la investigación del rol (paso 4): lo que el rol exige y la
  persona ya domina se trata con lenguaje de par; lo que exige y no aparece
  en su perfil va a `perfil.conocimientos`, para que Claude lo aporte.
- **Un enlace:** leerlo (si no se puede abrir, decirlo en una frase y seguir).
  Lo útil del proyecto va al bloque `carpeta` como cualquier otro documento.
- Si no comparte nada, se sigue sin insistir.

## 2. Preguntas abiertas — como mucho dos, de una línea

Solo lo que ni la carpeta ni los archivos respondieron, en un mensaje normal
y con un ejemplo de lo corto que puede ser:

> 1. **¿Cuál es tu cargo?** (por ejemplo: «coordinadora de compras»)
> 2. **¿En qué proyecto vas a trabajar aquí y qué quieres lograr?** En una
>    frase (por ejemplo: «el informe mensual de ventas para la gerencia»).

Si ya se saben por la carpeta o la hoja de vida, no se preguntan: se
confirman en la primera `AskUserQuestion` («Entendí que eres … y que el
proyecto es …» · «Sí, es así» · «No exactamente»; con «No exactamente», una
línea para corregir).

## 3. Preguntas para elegir — dos `AskUserQuestion` como mucho

Hasta cuatro preguntas por llamada y de dos a cuatro opciones cada una (la
herramienta agrega «Otro» para escribir). Las opciones se arman con lo que ya
se sabe: las tareas que se repiten en la carpeta, las habituales del cargo
(con lo que ya sepas de él; la investigación a fondo del paso 4 puede sumar
otras, que se confirman en la propuesta), los tipos de archivo que usa y su
hoja de vida. Omite las que ya estén respondidas.

**Primera llamada — su trabajo**

| Pregunta | Tipo | Opciones (ejemplos) | Para qué se usa |
|---|---|---|---|
| ¿Cuáles de estas tareas haces habitualmente? | selección múltiple | 3 o 4 tareas concretas deducidas, con su frecuencia en la descripción | `perfil.tareas`; cada una tiene su atajo |
| ¿Qué entregas con más frecuencia? | selección múltiple | Informes o documentos · Hojas de cálculo o tableros · Presentaciones · Código o automatizaciones | Categorías de entregables y arquitectura |
| ¿Qué herramientas usas en tu día a día? | selección múltiple | Las que se deducen de la carpeta, del cargo y de la hoja de vida | `perfil.herramientas`, accesos y programas |
| ¿Qué temas debo dominar para ayudarte? | selección múltiple | 3 o 4 temas del oficio que no aparezcan como fortaleza en su perfil | `perfil.conocimientos` |

**Segunda llamada — cómo quiere trabajar**

| Pregunta | Opciones | Para qué se usa |
|---|---|---|
| ¿Cuántos proyectos vas a llevar en este espacio? | Uno solo · Varios (clientes, cuentas o iniciativas distintas) | `arquitectura.modo` |
| ¿Para quién es principalmente lo que produces? | Clientes externos · Mi equipo o mi jefe · Solo para mí · Público (publicaciones, comunidad) | `perfil.destinatarios`; pesa en la arquitectura y en el tono |
| ¿Cómo prefieres que te hable? | Directo y sin tecnicismos · Técnico, conozco las herramientas · Con explicaciones paso a paso | `trato` |
| ¿Quieres que lleve un historial de versiones de los archivos? | Sí (recomendado) · No | `git` |

Si eligió «Varios», pide en un mensaje corto los nombres de los proyectos
que ya sabe (se pueden agregar después). Si en una respuesta eligió «Otro» y
escribió algo largo, resúmelo tú en una línea; no hagas más preguntas
abiertas.

## 4. Inferir sin preguntar

- **Idioma:** el de la conversación.
- **Credenciales:** de las herramientas mencionadas, deduce qué accesos van a
  hacer falta y propón nombres de variable (`CRM_TOKEN`,
  `NUBE_CREDENCIALES`…) con una línea de para qué sirve cada uno.
  Solo nombres: **nunca valores**.
- **Arquitectura:** con `references/arquitecturas.md` (objetivo + tareas +
  destinatarios + modo + lineamientos del rol + lo que ya hay en el repositorio).
- **Programas:** de las tareas, las herramientas y la investigación del rol,
  deduce qué programas deben estar instalados (lenguajes, entornos de
  ejecución, utilidades de línea de comandos, bibliotecas) y cómo comprobar
  cada uno. Solo los que una tarea concreta necesite.
- **Conocimientos:** normaliza la lista (temas concretos, no frases largas).
- **Tareas:** cada una con `tarea`, `frecuencia` (si la dijo) y `entrega`
  (qué produce). De aquí salen las categorías de entregables y, a futuro, los
  candidatos a skill.

## 5. Confirmación

Muestra la propuesta en lenguaje sencillo (ver SKILL.md, paso 6) y pregunta
con `AskUserQuestion`: «Sí, prepáralo» · «Quiero cambiar algo» · «Ahora no».
Sin un «Sí, prepáralo» en esta conversación no se escribe nada.

## 6. Esquema de `respuestas-espacio.json`

Se escribe en la raíz con `Write`; `montar.py` lo borra al terminar bien.

```json
{
  "idioma": "es",
  "trato": "Directo y sin tecnicismos; explicar las decisiones en una frase.",
  "git": true,
  "perfil": {
    "nombre": "opcional",
    "cargo": "Analista de operaciones",
    "area": "Operaciones",
    "proyecto": "Tablero de indicadores logísticos",
    "objetivo": "Que la gerencia vea cada lunes el cumplimiento de entregas y los cuellos de botella.",
    "destinatarios": "Mi jefe y la gerencia de operaciones",
    "habilidades": ["Hojas de cálculo avanzadas (tablas dinámicas)", "Gestión de inventarios", "Inglés intermedio"],
    "conocimientos": ["Indicadores logísticos (OTIF, lead time)", "Hojas de cálculo y limpieza de datos", "Normas de la empresa sobre datos de clientes"],
    "tareas": [
      {"tarea": "Actualizar el tablero semanal", "frecuencia": "semanal", "entrega": "tablero + resumen de 1 página"},
      {"tarea": "Investigar causas de retrasos", "frecuencia": "cuando hay alertas", "entrega": "informe corto"}
    ],
    "herramientas": ["Hoja de cálculo", "Sistema de gestión (exporta CSV)", "Correo"]
  },
  "arquitectura": {
    "tipo": "analisis-de-datos",
    "modo": "unico",
    "por_que": "El trabajo es transformar exportes del ERP en indicadores periódicos: datos crudos inmutables, análisis reproducible y reportes por fecha.",
    "carpetas": [
      {"ruta": "datos/crudos/", "para": "Exportes originales del ERP, sin modificar"},
      {"ruta": "datos/procesados/", "para": "Datos limpios y transformados, regenerables"},
      {"ruta": "analisis/", "para": "Consultas, cuadernos y scripts del análisis"}
    ]
  },
  "rutas": {
    "contexto": "contexto/",
    "entregables": "reportes/",
    "investigacion": "investigacion/",
    "memoria_global": "memoria/",
    "bitacora_peticiones": "bitacora-peticiones.md"
  },
  "credenciales": [
    {"variable": "ERP_USUARIO", "para": "Usuario de solo lectura para exportar del ERP"}
  ],
  "programas": [
    {"nombre": "Intérprete del lenguaje de análisis", "para": "Correr los scripts de limpieza y cálculo",
     "comprobar": "<comando> --version", "instalar": "Instalador oficial (URL de la fuente oficial)"}
  ],
  "carpeta": {
    "fecha": "29-oct-2026",
    "resumen": "Exportes semanales del ERP desde enero y un tablero en hoja de cálculo que se actualiza cada lunes.",
    "aprendido": ["El tablero se envía a la gerencia de operaciones", "Los exportes llegan en CSV con la misma estructura"],
    "documentos": [
      {"archivo": "Manual del tablero.docx", "aporta": "Cómo se calcula cada indicador y a quién se envía"},
      {"archivo": "tablero.xlsx", "aporta": "Las hojas e indicadores actuales"}
    ],
    "sin_leer": [
      {"archivos": "exportes/", "motivo": "Exportes semanales con la misma estructura; se leyó el más reciente"}
    ]
  },
  "investigacion_rol": { "…": "ver references/investigar-rol.md § 6" },
  "skills_existentes": { "…": "solo si el repositorio ya tenía skills: references/skills-existentes.md § 5" }
}
```

`carpeta`: lo que se aprendió de la carpeta antes de la entrevista. Obligatorio
en el primer montaje si `explorar.py` encontró documentos: cada uno debe estar
en `documentos` (con `archivo` y `aporta`) o cubierto por `sin_leer`
(`archivos` es una ruta, una carpeta terminada en `/` o un patrón como
`fotos/*.jpg`, siempre con `motivo`). Además, `montar.py` no acepta el
montaje mientras haya skills en la carpeta sin instalar en `.claude/skills/`.

`programas`: cada uno con `nombre`, `para` y `comprobar` (el comando que
muestra su versión; su primera palabra debe ser el ejecutable, que
`verificar.py` busca en el sistema). `instalar` es opcional: la fuente oficial
o la orden del gestor de paquetes. Para una biblioteca o un complemento que no
es un ejecutable propio, `comprobar` es el comando de la herramienta que lo
carga.

Modo multiproyecto: `"modo": "multiproyecto"`, un bloque
`"proyectos": {"base": "proyectos", "lista": ["cliente-a", "cliente-b"]}` y
rutas con `<proyecto>`: `contexto`, `entregables` (`proyectos/<proyecto>/`),
`bitacora_peticiones` y `memoria_proyecto` (por ejemplo
`proyectos/<proyecto>/memoria/`). La memoria
global se queda en la raíz. Las carpetas extra pueden llevar `<proyecto>` si
son por proyecto.

Reglas que valida `montar.py` (código 2 si no se cumplen): perfil con cargo,
proyecto, objetivo y al menos una tarea; `investigacion_rol` completa (ver
`references/investigar-rol.md`); cada programa con `nombre`, `para` y
`comprobar`; rutas relativas, sin `..`, fuera de
`.claude/`, `.git/` y `.espacio/`; cada carpeta extra con `ruta` y `para`;
nombres de proyecto en minúsculas con guiones y hasta 30 caracteres; que cada
carpeta deje sitio a sus archivos sin pasar de 6 niveles ni 150 caracteres
(`references/arquitecturas.md`, «Silos»); variables de credenciales en
MAYÚSCULAS y sin campo `valor`. Las fechas siempre en formato `DD-mmm-YYYY`
con el mes abreviado: `10-oct-2026`.
