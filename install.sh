#!/usr/bin/env bash
# Instala o actualiza el skill Primer Paso (primeros-pasos) en la carpeta actual, sea cual sea su ruta.
#
#   curl -fsSL https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.sh | bash
#
# PRIMEROS_PASOS_ORIGEN=<carpeta> instala desde una copia local (lo usan las pruebas).
set -euo pipefail

REPO="davidortiz-ops/espacio-trabajo-claude"
RAMA="${PRIMEROS_PASOS_RAMA:-main}"
DESTINO_REL=".claude/skills/primeros-pasos"

aviso() { printf '%s\n' "$*"; }
falla() { printf 'No se pudo instalar: %s\n' "$*" >&2; exit 1; }

# Con «curl … | bash» la entrada es el propio script: las preguntas se leen de /dev/tty.
INTERACTIVO=0
if [ -z "${PRIMEROS_PASOS_SIN_PROGRAMAS:-}" ] && { : </dev/tty; } 2>/dev/null; then INTERACTIVO=1; fi

no_sirve() {  # la carpeta personal o la raíz del disco no son una carpeta de trabajo
  [ "$1" = "$(cd "$HOME" && pwd -P)" ] || [ "$1" = "/" ]
}

DESTINO_REPO="$(pwd -P)"
if no_sirve "$DESTINO_REPO"; then
  [ "$INTERACTIVO" = 1 ] || falla "estás en tu carpeta personal. Entra primero a la carpeta donde vas a trabajar y vuelve a ejecutar el comando."
  aviso "Estás en tu carpeta personal, no en una carpeta de trabajo."
  printf '%s' "Escribe la ruta de la carpeta donde vas a trabajar (o arrástrala aquí desde el Finder) y presiona Enter: " > /dev/tty
  IFS= read -r ruta < /dev/tty || falla "no se recibió ninguna carpeta."
  # Al arrastrar, Terminal pone una barra antes de cada espacio y un espacio al final.
  ruta="$(printf '%s' "$ruta" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//' -e "s/^['\"]//" -e "s/['\"]\$//" -e 's/\\\(.\)/\1/g')"
  case "$ruta" in "~"|"~/"*) ruta="$HOME${ruta#?}" ;; esac
  [ -n "$ruta" ] || falla "no se recibió ninguna carpeta."
  if [ ! -d "$ruta" ]; then
    printf '%s [S/n] ' "La carpeta $ruta no existe. ¿La creo?" > /dev/tty
    read -r r < /dev/tty || r=n
    case "$r" in n|N|no|NO|No) falla "la carpeta $ruta no existe." ;; esac
    mkdir -p "$ruta" || falla "no se pudo crear $ruta."
  fi
  DESTINO_REPO="$(cd "$ruta" && pwd -P)" || falla "no se pudo entrar a $ruta."
  if no_sirve "$DESTINO_REPO"; then falla "esa es tu carpeta personal: elige o crea una carpeta para tu trabajo."; fi
  cd "$DESTINO_REPO"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -n "${PRIMEROS_PASOS_ORIGEN:-}" ]; then
  [ -f "$PRIMEROS_PASOS_ORIGEN/skill/SKILL.md" ] || falla "$PRIMEROS_PASOS_ORIGEN no contiene skill/SKILL.md."
  cp -R "$PRIMEROS_PASOS_ORIGEN/skill" "$TMP/skill"
else
  command -v curl >/dev/null 2>&1 || falla "hace falta curl."
  command -v tar >/dev/null 2>&1 || falla "hace falta tar."
  aviso "Descargando Primer Paso…"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$RAMA" | tar -xz -C "$TMP" \
    || falla "no se pudo descargar de GitHub. Revisa tu conexión."
  mv "$TMP"/*/skill "$TMP/skill" 2>/dev/null || falla "la descarga no trae la carpeta skill/."
fi
find "$TMP/skill" -name '__pycache__' -type d -prune -exec rm -rf {} +

mkdir -p "$DESTINO_REPO/.claude/skills"
if [ -d "$DESTINO_REPO/$DESTINO_REL" ]; then
  ACCION="actualizado"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior"
  mv "$DESTINO_REPO/$DESTINO_REL" "$DESTINO_REPO/$DESTINO_REL.anterior"
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior"
else
  ACCION="instalado"
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
fi

aviso ""
aviso "Listo: Primer Paso quedó $ACCION en $DESTINO_REPO/$DESTINO_REL"

# ---- Programas para trabajar: Git, Python, Node.js y Playwright
tiene_python() {
  for c in python3 python; do
    command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null && return 0
  done
  return 1
}
tiene_node() {
  command -v node >/dev/null 2>&1 || return 1
  [ "$(node --version 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/')" -ge 18 ] 2>/dev/null
}
tiene_playwright() { command -v playwright >/dev/null 2>&1; }
tiene_git() { command -v git >/dev/null 2>&1; }

GESTOR=""
case "$(uname -s)" in
  Darwin) command -v brew >/dev/null 2>&1 && GESTOR="brew" ;;
  *) if command -v apt-get >/dev/null 2>&1; then GESTOR="apt"; elif command -v dnf >/dev/null 2>&1; then GESTOR="dnf"; fi ;;
esac

orden() {  # orden de instalación de un programa con el gestor de este sistema
  case "$1:$GESTOR" in
    git:brew) echo "brew install git" ;;
    git:apt) echo "sudo apt-get install -y git" ;;
    git:dnf) echo "sudo dnf install -y git" ;;
    python:brew) echo "brew install python@3.12" ;;
    python:apt) echo "sudo apt-get install -y python3" ;;
    python:dnf) echo "sudo dnf install -y python3" ;;
    node:brew) echo "brew install node" ;;
    node:apt) echo "sudo apt-get install -y nodejs npm" ;;
    node:dnf) echo "sudo dnf install -y nodejs npm" ;;
    playwright:*) echo "npm install -g playwright; npx playwright install chromium" ;;
  esac
}
descarga() {
  case "$1" in
    git) echo "https://git-scm.com/downloads" ;;
    python) echo "https://www.python.org/downloads/" ;;
    node) echo "https://nodejs.org/" ;;
    playwright) echo "https://playwright.dev/docs/intro" ;;
  esac
}

preguntar() {  # devuelve 0 si la persona acepta
  [ "$INTERACTIVO" = 1 ] || return 1
  printf '%s [S/n] ' "$1" > /dev/tty
  read -r r < /dev/tty || return 1
  case "$r" in n|N|no|NO|No) return 1 ;; *) return 0 ;; esac
}

aviso ""
aviso "Programas para trabajar:"
PENDIENTES=""
for p in git python node playwright; do
  if "tiene_$p"; then
    aviso "  OK     $p"
    continue
  fi
  aviso "  FALTA  $p"
  cmd="$(orden "$p")"
  if [ "$p" = "playwright" ] && ! tiene_node; then cmd=""; fi
  if [ -n "$cmd" ] && preguntar "  ¿Instalo $p ahora? Se ejecutará: $cmd"; then
    if sh -c "$cmd" && "tiene_$p"; then
      aviso "  OK     $p instalado"
      continue
    fi
    aviso "  No se pudo instalar $p."
  fi
  PENDIENTES="$PENDIENTES $p"
done
if [ -n "$PENDIENTES" ]; then
  aviso ""
  aviso "Quedan por instalar:"
  for p in $PENDIENTES; do
    cmd="$(orden "$p")"
    aviso "  $p: ${cmd:-descárgalo de $(descarga "$p")}"
  done
  [ "$(uname -s)" = "Darwin" ] && [ -z "$GESTOR" ] && aviso "  (Con Homebrew, https://brew.sh, se instalan con un solo comando.)"
fi

# ---- Que «empezar», «iniciar» o «configurar» activen el skill
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    aviso ""
    "$c" "$DESTINO_REPO/$DESTINO_REL/scripts/activar.py" --registrar --raiz "$DESTINO_REPO" || true
    break
  fi
done

if [ ! -d "$DESTINO_REPO/.git" ]; then
  aviso "Ojo: esta carpeta no es un repositorio git. Funciona igual, pero te conviene versionarla (git init)."
fi

aviso ""
aviso "Siguiente paso: abre Claude Code en tu carpeta y escribe «empezar»:"
aviso "  cd \"$DESTINO_REPO\"; claude"
