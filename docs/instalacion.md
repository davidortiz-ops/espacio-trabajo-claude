# Instalación paso a paso

Sigue los pasos en orden. Cada comando se copia completo, se pega en la
terminal y se ejecuta con Enter. Toma unos minutos.

Antes de empezar necesitas tener [Claude Code](https://claude.com/claude-code)
instalado.

## Paso 1. Abre la terminal

La terminal es una ventana donde se escriben comandos.

**En Windows:** presiona la tecla Windows, escribe `PowerShell` y presiona
Enter. Sabes que estás en el lugar correcto si la línea empieza con `PS`, por
ejemplo `PS C:\Users\TuNombre>`.

**En Mac:** presiona Cmd + Espacio, escribe `Terminal` y presiona Enter.

## Paso 2. Entra en tu carpeta de trabajo

Puede ser cualquier carpeta, donde tú quieras: una nueva o una que ya tenga
tus archivos. Tus archivos se respetan. La ruta de los ejemplos no existe:
cámbiala por la de tu carpeta. Si no sabes cuál es, salta al paso 3: el
instalador te la pregunta.

**En Windows:** escribe `cd`, un espacio y la ruta de tu carpeta entre
comillas:

```powershell
cd "C:\ruta\de\tu\carpeta"
```

Atajo: abre la carpeta en el Explorador de archivos, haz clic en la barra de
dirección, escribe `powershell` y presiona Enter. PowerShell se abre ya dentro
de ella.

**En Mac:** escribe `cd` y un espacio, arrastra la carpeta desde el Finder
hasta la ventana de Terminal y presiona Enter:

```bash
cd "/ruta/de/tu/carpeta"
```

## Paso 3. Instala el skill Primer Paso

En la misma terminal, dentro de tu carpeta:

**En Windows:**

```powershell
irm https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.ps1 | iex
```

**En Mac** (solo en Mac: en Windows este comando falla):

```bash
curl -fsSL https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.sh | bash
```

El instalador revisa si tienes Git, Python, Node.js y Playwright. Si falta
alguno, te pregunta «¿Instalo … ahora?»: responde `S` y Enter. Al final verás
«Listo: Primer Paso quedó instalado».

## Paso 4. Abre Claude y escribe «empezar»

En la misma terminal:

```
claude
```

Si Claude Code te pregunta si confías en la carpeta, elige la opción que dice
que sí. Luego escribe `empezar` y presiona Enter.

Primero Claude lee lo que ya hay en tu carpeta: documentos, hojas de cálculo y
presentaciones. Si encuentra skills sin instalar, las instala. No mueve ni
cambia tus archivos, y no abre los que pueden tener claves. Después te cuenta
lo que entendió y te pregunta solo lo que falte: tu cargo, tu proyecto, qué
quieres lograr, tus tareas habituales y las herramientas que usas. Responde
con tus palabras; no hace falta que sea largo.

Mientras tanto investiga tu rol y al final te muestra una propuesta. Léela y
responde «Sí, prepáralo» o pide los cambios que quieras.

## Paso 5. Termina tu arranque

Claude te dice cuánto te falta para quedar al 100 %. Escribe `sigamos` y te
acompaña en lo siguiente. La primera tarea real la hacen juntos y, al
terminarla, te pregunta cuánto te habría tomado a mano.

## Cada día, para volver a trabajar

Abre la terminal (paso 1), entra a tu carpeta (paso 2) y abre Claude:

```
claude
```

Claude te recuerda dónde quedaste. Para una tarea habitual escribe `/` y el
nombre de su atajo.

## Para actualizarlo

Repite el paso 3 dentro de tu carpeta. Se actualiza el skill y tu trabajo
queda intacto.

## Si algo falla

| Lo que ves | Qué hacer |
|---|---|
| `No se encuentra ningún parámetro que coincida con el nombre del parámetro 'fsSL'` (o `parameter name 'fsSL'`) | Estás en Windows con el comando de Mac. Usa el de Windows: `irm … \| iex` |
| `'irm' no se reconoce como un comando interno o externo` (o `'irm' is not recognized`) | Estás en CMD, no en PowerShell. Vuelve al paso 1 y abre PowerShell |
| `irm: command not found` o `iex: command not found` | Estás en Mac (o en Git Bash) con el comando de Windows. Usa el de Mac: `curl … \| bash` |
| `cd: no such file or directory`, `No se encuentra la ruta de acceso` o `Cannot find path` | Escribiste la ruta del ejemplo, que no existe. Pon la de tu carpeta, o salta al paso 3: el instalador te la pregunta |
| El instalador pregunta por tu carpeta | Estás en tu carpeta personal. Escribe la ruta de tu carpeta de trabajo, o arrástrala a la ventana, y presiona Enter; si no existe, te ofrece crearla |
| `claude: command not found` o `'claude' no se reconoce` | Falta instalar Claude Code, o hay que cerrar y volver a abrir la terminal después de instalarlo |
| Claude no responde a «empezar» | Escribe `/primeros-pasos` o cierra y vuelve a abrir Claude en tu carpeta |
| Falta un programa después de instalarlo | Cierra y vuelve a abrir la terminal |

Si nada de esto lo resuelve, copia el mensaje exacto que ves y compártelo con
quien te está acompañando.
