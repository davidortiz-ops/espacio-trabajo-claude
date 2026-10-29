#!/usr/bin/env python3
"""Conoce la carpeta donde se instaló el skill antes de la entrevista: qué
archivos hay, de qué tipo, de cuándo, qué se repite (pistas de tareas
habituales), qué documentos leer primero y su texto, y qué skills hay en la
carpeta sin instalar en `.claude/skills/`.

No modifica nada, salvo con --instalar-skills, que copia cada skill sin
instalar a `.claude/skills/<nombre>/` (el original no se toca).

    (sin argumentos)      resumen legible, con un extracto de cada documento
    --json                todo el detalle
    --texto RUTA          el texto completo de un archivo (también .docx, .xlsx,
                          .pptx, .odt), para leer lo que Read no abre
    --skills              solo las skills sin instalar (código 1 si hay alguna)
    --instalar-skills     las instala; las que chocan con una ya instalada
                          distinta se reportan y no se tocan

Los archivos que parecen claves o contraseñas se listan pero nunca se leen.
Código de salida: 0 bien; con --skills o --instalar-skills, 1 si queda alguna
sin instalar.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402
import inventario  # noqa: E402

OMITIR = {".git", "node_modules", ".venv", "venv", "__pycache__", comun.ESTADO, "dist", "build",
          ".next", ".cache", ".idea", ".vscode", ".svn", ".hg", "$RECYCLE.BIN", "System Volume Information"}
TIPOS = {
    "documento": {".md", ".txt", ".docx", ".doc", ".odt", ".rtf", ".pdf"},
    "hoja": {".xlsx", ".xlsm", ".xls", ".ods", ".csv", ".tsv"},
    "presentacion": {".pptx", ".ppt", ".odp", ".key"},
    "datos": {".json", ".yaml", ".yml", ".xml", ".sql", ".db", ".sqlite", ".parquet"},
    "pagina": {".html", ".htm"},
    "codigo": {".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".php", ".rb", ".go", ".java", ".cs", ".r",
               ".ipynb", ".sh", ".ps1", ".css", ".scss", ".vue", ".svelte"},
    "imagen": {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".psd", ".ai", ".fig", ".tif", ".tiff",
               ".heic", ".bmp", ".eps", ".indd"},
    "audio-video": {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "comprimido": {".zip", ".rar", ".7z", ".tar", ".gz", ".skill"},
}
TIPO_DE = {ext: t for t, exts in TIPOS.items() for ext in exts}
PARA_LEER = ("documento", "hoja", "presentacion", "pagina", "datos")
TEXTO_PLANO = {".md", ".txt", ".csv", ".tsv", ".json", ".yaml", ".yml", ".xml", ".sql", ".html", ".htm",
               ".rtf"} | TIPOS["codigo"]
OFFICE = {".docx", ".xlsx", ".xlsm", ".pptx", ".odt", ".ods", ".odp"}
SENSIBLE = re.compile(r"(^\.env|\.pem$|\.key$|\.p12$|\.pfx$|\.kdbx$|^id_(rsa|ed25519|ecdsa)|credencial|credential"
                      r"|secret|secreto|password|contrase|clave|token)", re.I)
PRIORIDAD = re.compile(r"(readme|leeme|brief|manual|gu[ií]a|contrato|propuesta|alcance|requisit|objetiv|plan"
                       r"|instructiv|procedimiento|pol[ií]tica|norma|presentaci|resumen|acta|perfil|cargo)", re.I)
MAX_ARCHIVOS = 20000
MAX_LEER = 300          # documentos con extracto
EXTRACTO = 600
MAX_TEXTO = 200_000
MAX_ZIP = 50 * 1024 * 1024


# ---------------------------------------------------------------- recorrido

def _sensible(rel: str) -> bool:
    return rel.split("/")[0] == "credenciales" or bool(SENSIBLE.search(PurePosixPath(rel).name))


def recorrer(raiz: Path) -> tuple[list[dict], list[Path], bool]:
    """(archivos de la persona, SKILL.md fuera de su sitio, si se cortó por tamaño)."""
    archivos, skill_md, cortado = [], [], False
    propio = comun.SKILL.resolve()
    for actual, dirs, nombres in os.walk(raiz):
        d = Path(actual)
        rel_d = d.relative_to(raiz).as_posix()
        dentro_claude = rel_d == ".claude" or rel_d.startswith(".claude/")
        dirs[:] = sorted(x for x in dirs if x not in OMITIR and (d / x).resolve() != propio
                         and not (rel_d == ".claude" and x == "espacio"))
        if "SKILL.md" in nombres and rel_d != ".":
            # Una skill: sus archivos son de la skill, no documentos de la persona.
            partes = (rel_d + "/SKILL.md").split("/")
            if not (len(partes) == 4 and partes[:2] == [".claude", "skills"]):
                skill_md.append(d / "SKILL.md")
            dirs[:] = []
            continue
        for n in sorted(nombres):
            p = d / n
            rel = p.relative_to(raiz).as_posix()
            if dentro_claude or rel in (comun.CONFIG, "respuestas-espacio.json") or rel.startswith(comun.DOCS + "/"):
                continue
            if len(archivos) >= MAX_ARCHIVOS:
                cortado = True
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            ext = p.suffix.lower()
            archivos.append({"ruta": rel, "tipo": "posible-clave" if _sensible(rel) else TIPO_DE.get(ext, "otro"),
                             "ext": ext, "bytes": st.st_size,
                             "fecha": comun.hoy(dt.date.fromtimestamp(st.st_mtime)), "_mtime": st.st_mtime})
    return archivos, skill_md, cortado


# ---------------------------------------------------------------- texto

def _xml_texto(xml: str, parrafo: str) -> str:
    xml = re.sub(parrafo, "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")):
        xml = xml.replace(a, b)
    return re.sub(r"\n\s*\n+", "\n", xml).strip()


def _office(p: Path) -> str:
    ext = p.suffix.lower()
    with zipfile.ZipFile(p) as z:
        nombres = z.namelist()
        leer = lambda n: z.read(n).decode("utf-8", errors="replace")  # noqa: E731
        if ext == ".docx":
            return _xml_texto(leer("word/document.xml"), r"</w:p>")
        if ext in (".odt", ".ods", ".odp"):
            return _xml_texto(leer("content.xml"), r"</text:p>|</table:table-row>")
        if ext == ".pptx":
            def num(n):
                m = re.search(r"(\d+)\.xml$", n)
                return int(m.group(1)) if m else 0
            diapos = sorted((n for n in nombres if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=num)
            return "\n\n".join(f"[Diapositiva {i}]\n" + _xml_texto(leer(n), r"</a:p>")
                               for i, n in enumerate(diapos, 1))
        hojas = re.findall(r'<sheet [^>]*name="([^"]+)"', leer("xl/workbook.xml")) if "xl/workbook.xml" in nombres else []
        celdas = _xml_texto(leer("xl/sharedStrings.xml"), r"</si>") if "xl/sharedStrings.xml" in nombres else ""
        return ("Hojas: " + ", ".join(hojas) + "\n" if hojas else "") + celdas


def texto(p: Path, rel: str) -> str | None:
    """El texto de un archivo, o None si no se puede sacar con la biblioteca estándar."""
    if _sensible(rel):
        return None
    ext = p.suffix.lower()
    try:
        if ext in OFFICE:
            return _office(p)[:MAX_TEXTO]
        if ext in TEXTO_PLANO:
            with p.open("r", encoding="utf-8", errors="replace") as f:
                t = f.read(MAX_TEXTO)
            return _xml_texto(t, r"</p>|<br\s*/?>|</h\d>|</li>") if ext in (".html", ".htm") else t
    except (OSError, KeyError, zipfile.BadZipFile, ValueError):
        return None
    return None


def _extracto(t: str) -> str:
    return " ".join(t.split())[:EXTRACTO]


# ---------------------------------------------------------------- análisis

def _patron(nombre: str) -> str:
    base = comun.sin_acentos(PurePosixPath(nombre).stem.lower())
    base = re.sub(r"\b(" + "|".join(comun.MESES) + r")[a-z]*\b", " ", base)
    base = re.sub(r"\b(v|version|final|copia|copy)\b", " ", base)
    base = re.sub(r"[\d_\-\.\s()\[\]]+", " ", base).strip()
    return "-".join(base.split())


def repetidos(archivos: list[dict]) -> list[dict]:
    grupos: dict[str, list[dict]] = {}
    for a in archivos:
        if a["tipo"] in ("codigo", "otro", "posible-clave"):
            continue
        clave = _patron(a["ruta"])
        if len(clave) >= 3:
            grupos.setdefault(clave, []).append(a)
    res = []
    for clave, xs in grupos.items():
        if len(xs) >= 3:
            xs = sorted(xs, key=lambda a: a["_mtime"])
            res.append({"patron": clave, "archivos": len(xs), "desde": xs[0]["fecha"], "hasta": xs[-1]["fecha"],
                        "ejemplo": xs[-1]["ruta"]})
    return sorted(res, key=lambda r: -r["archivos"])[:15]


def _prioridad(a: dict) -> tuple:
    nombre = PurePosixPath(a["ruta"]).name
    return (0 if PRIORIDAD.search(nombre) else 1, a["ruta"].count("/"), -a["_mtime"])


def explorar(raiz: Path, extractos: bool = True) -> dict:
    archivos, skill_md, cortado = recorrer(raiz)
    por_tipo: dict[str, int] = {}
    carpetas: dict[str, int] = {}
    for a in archivos:
        por_tipo[a["tipo"]] = por_tipo.get(a["tipo"], 0) + 1
        if "/" in a["ruta"]:
            primera = a["ruta"].split("/")[0]
            carpetas[primera] = carpetas.get(primera, 0) + 1
    docs = sorted((a for a in archivos if a["tipo"] in PARA_LEER), key=_prioridad)
    leer = []
    for i, a in enumerate(docs):
        item = {k: a[k] for k in ("ruta", "tipo", "fecha", "bytes")}
        if a["ext"] == ".pdf":
            item["como"] = "Read"
        elif a["ext"] in OFFICE:
            item["como"] = "--texto"
        elif a["ext"] in TEXTO_PLANO:
            item["como"] = "Read"
        else:
            item["como"] = "no-legible"
        if extractos and i < MAX_LEER and item["como"] != "no-legible" and a["ext"] != ".pdf":
            t = texto(raiz / a["ruta"], a["ruta"])
            if t:
                item["extracto"] = _extracto(t)
        leer.append(item)
    fechas = sorted(archivos, key=lambda a: a["_mtime"])
    return {
        "raiz": str(raiz), "archivos": len(archivos), "cortado": cortado,
        "por_tipo": dict(sorted(por_tipo.items(), key=lambda x: -x[1])),
        "carpetas": dict(sorted(carpetas.items(), key=lambda x: -x[1])),
        "sueltos_en_raiz": [a["ruta"] for a in archivos if "/" not in a["ruta"]][:40],
        "desde": fechas[0]["fecha"] if fechas else None, "hasta": fechas[-1]["fecha"] if fechas else None,
        "recientes": [a["ruta"] for a in fechas[::-1][:10]],
        "repetidos": repetidos(archivos),
        "para_leer": leer,
        "posibles_claves": [a["ruta"] for a in archivos if a["tipo"] == "posible-clave"],
        "skills_sin_instalar": skills_sin_instalar(raiz, skill_md, archivos),
    }


def documentos(raiz: Path) -> list[str]:
    """Rutas de los documentos que el montaje exige haber revisado."""
    return [a["ruta"] for a in recorrer(raiz)[0] if a["tipo"] in PARA_LEER]


# ---------------------------------------------------------------- skills sin instalar

def _nombre_skill(texto_md: str, respaldo: str) -> str:
    return comun.slug(inventario.frontmatter(texto_md).get("name") or respaldo, largo=50)


def _zip_skills(p: Path) -> list[dict]:
    try:
        if p.stat().st_size > MAX_ZIP:
            return []
        with zipfile.ZipFile(p) as z:
            res = []
            for n in z.namelist():
                if PurePosixPath(n).name == "SKILL.md":
                    base = str(PurePosixPath(n).parent)
                    base = "" if base == "." else base
                    md = z.read(n).decode("utf-8", errors="replace")
                    res.append({"md": md, "base": base,
                                "respaldo": PurePosixPath(base).name if base else p.stem})
            return res
    except (OSError, zipfile.BadZipFile, KeyError):
        return []


def skills_sin_instalar(raiz: Path, skill_md: list[Path] | None = None,
                        archivos: list[dict] | None = None) -> list[dict]:
    if skill_md is None or archivos is None:
        archivos, skill_md, _ = recorrer(raiz)
    instaladas = raiz / ".claude" / "skills"
    res, vistos = [], set()

    def agregar(nombre: str, origen: str, tipo: str, md: str, base: str = "") -> None:
        if nombre in vistos or nombre == comun.SKILL.name:
            return
        vistos.add(nombre)
        destino = instaladas / nombre
        estado = "conflicto" if destino.exists() else "sin-instalar"
        if estado == "conflicto":
            # Ya instalada desde este origen (o una copia idéntica): no queda nada por hacer.
            iguales = (inventario._huella(destino) == inventario._huella(raiz / origen) if tipo == "carpeta"
                       else (destino / "SKILL.md").is_file()
                       and (destino / "SKILL.md").read_text(encoding="utf-8", errors="replace") == md)
            if iguales:
                return
        res.append({"nombre": nombre, "origen": origen, "tipo": tipo, "base": base,
                    "destino": f".claude/skills/{nombre}", "estado": estado})

    for p in skill_md:
        md = p.read_text(encoding="utf-8", errors="replace")
        agregar(_nombre_skill(md, p.parent.name), p.parent.relative_to(raiz).as_posix(), "carpeta", md)
    for a in archivos:
        if a["ext"] in (".zip", ".skill"):
            for s in _zip_skills(raiz / a["ruta"]):
                agregar(_nombre_skill(s["md"], s["respaldo"]), a["ruta"], "comprimido", s["md"], s["base"])
    return res


def instalar(raiz: Path, s: dict) -> str:
    destino = raiz / s["destino"]
    if destino.exists():
        return "conflicto: ya hay una skill distinta con ese nombre; decide con la persona"
    if s["tipo"] == "carpeta":
        shutil.copytree(raiz / s["origen"], destino, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        return "instalada"
    prefijo = s["base"] + "/" if s["base"] else ""
    with zipfile.ZipFile(raiz / s["origen"]) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(prefijo):
                continue
            rel = PurePosixPath(info.filename[len(prefijo):])
            if rel.is_absolute() or ".." in rel.parts or "__pycache__" in rel.parts:
                continue
            p = destino / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(z.read(info))
    return "instalada"


# ---------------------------------------------------------------- salida

def legible(r: dict) -> str:
    if not r["archivos"] and not r["skills_sin_instalar"]:
        return "La carpeta está vacía: todo saldrá de la entrevista."
    out = [f"Carpeta: {r['raiz']}",
           f"{r['archivos']} archivos" + (f" (se cortó en {MAX_ARCHIVOS})" if r["cortado"] else "")
           + (f", del {r['desde']} al {r['hasta']}" if r["desde"] else "")]
    if r["por_tipo"]:
        out.append("Por tipo: " + ", ".join(f"{t} {n}" for t, n in r["por_tipo"].items()))
    if r["carpetas"]:
        out.append("Carpetas de primer nivel: " + ", ".join(f"{c}/ ({n})" for c, n in list(r["carpetas"].items())[:20]))
    if r["sueltos_en_raiz"]:
        out.append("Sueltos en la raíz: " + ", ".join(r["sueltos_en_raiz"][:20]))
    if r["recientes"]:
        out.append("Lo más reciente: " + ", ".join(r["recientes"][:5]))
    if r["repetidos"]:
        out.append("\nSe repite (pistas de tareas habituales):")
        out += [f"  - {x['patron']}: {x['archivos']} archivos, del {x['desde']} al {x['hasta']} (p. ej. {x['ejemplo']})"
                for x in r["repetidos"]]
    if r["skills_sin_instalar"]:
        out.append("\nSkills en la carpeta sin instalar en .claude/skills/ (obligatorio instalarlas):")
        out += [f"  - {s['nombre']} ← {s['origen']}" + (" [CONFLICTO con una instalada distinta]"
                                                         if s["estado"] == "conflicto" else "")
                for s in r["skills_sin_instalar"]]
        out.append("  → python <skill>/scripts/explorar.py --instalar-skills")
    if r["posibles_claves"]:
        out.append("\nNo se leyeron (pueden tener claves): " + ", ".join(r["posibles_claves"][:20]))
    if r["para_leer"]:
        out.append(f"\nDocumentos para leer ({len(r['para_leer'])}, en orden de prioridad):")
        for d in r["para_leer"]:
            como = {"Read": "", "--texto": " [texto completo: explorar.py --texto]",
                    "no-legible": " [no se puede leer como texto]"}[d["como"]]
            out.append(f"  - {d['ruta']} ({d['tipo']}, {d['fecha']}){como}")
            if d.get("extracto"):
                out.append(f"      {d['extracto']}")
    return "\n".join(out)


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Conoce la carpeta antes de la entrevista")
    ap.add_argument("--raiz")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--texto")
    ap.add_argument("--skills", action="store_true")
    ap.add_argument("--instalar-skills", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    if a.texto:
        p = Path(a.texto)
        p = p if p.is_absolute() else raiz / p
        try:
            rel = p.resolve().relative_to(raiz).as_posix()
        except ValueError:
            print("Ese archivo está fuera de la carpeta del espacio.", file=sys.stderr)
            return 2
        t = texto(p, rel)
        if t is None:
            print("No se pudo sacar el texto de ese archivo (si es PDF o imagen, ábrelo con Read).", file=sys.stderr)
            return 2
        print(t)
        return 0
    if a.skills or a.instalar_skills:
        lista = skills_sin_instalar(raiz)
        if a.instalar_skills:
            for s in lista:
                print(f"{s['nombre']}: {instalar(raiz, s)} ({s['origen']} → {s['destino']})")
            lista = skills_sin_instalar(raiz)
        if a.json:
            print(json.dumps(lista, ensure_ascii=False, indent=2))
        elif not a.instalar_skills:
            print("\n".join(f"{s['nombre']} ← {s['origen']} ({s['estado']})" for s in lista)
                  or "Todas las skills de la carpeta están instaladas.")
        return 1 if lista else 0
    r = explorar(raiz)
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else legible(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
