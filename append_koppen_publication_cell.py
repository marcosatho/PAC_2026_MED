import json
from pathlib import Path


notebook_path = Path("03_clasifiacion_koppen.ipynb")
notebook = json.loads(notebook_path.read_text(encoding="utf-8"))

marker = "PUBLICACIÓN KÖPPEN-GEIGER EN FORMATO CARTA"
if not any(marker in "".join(cell.get("source", [])) for cell in notebook["cells"]):
    source = f'''# ============================================================
# {marker}
# Mismo estándar editorial de las figuras POMCA
# ============================================================

import runpy
import sys

SCRIPT_PUBLICACION = ROOT / "01_CUADERNOS" / "publicar_koppen_medellin.py"

argumentos_originales = sys.argv[:]
try:
    sys.argv = [str(SCRIPT_PUBLICACION), str(ROOT)]
    runpy.run_path(str(SCRIPT_PUBLICACION), run_name="__main__")
finally:
    sys.argv = argumentos_originales

print("Figura final guardada en:")
print(ROOT / "04_PREVISUALIZACIONES" / "publicacion_carta")
'''
    notebook["cells"].append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source.splitlines(keepends=True),
        }
    )

notebook_path.write_text(
    json.dumps(notebook, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
