from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
SOURCE = BASE / "capas_climaticas_renderizadas"
OUTPUT = SOURCE / "00_previsualizacion_capas_climaticas_pomca.png"

PANELS = [
    (
        "22_evapotranspiracion_pomca_render.png",
        "Evapotranspiración anual",
        "894–1.145 mm/año",
    ),
    (
        "23_temperatura_pomca_render.png",
        "Temperatura media",
        "10,5–24,8 °C · negro: sin datos",
    ),
    (
        "24_precipitacion_pomca_render.png",
        "Precipitación media anual",
        "1.438–5.809 mm/año",
    ),
]


def font(name: str, size: int):
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


title_font = font("seguisb.ttf", 38)
panel_font = font("seguisb.ttf", 25)
detail_font = font("segoeui.ttf", 20)
footer_font = font("segoeui.ttf", 18)

images = [Image.open(SOURCE / item[0]).convert("RGB") for item in PANELS]
panel_w, panel_h = 580, 586
margin, gap = 42, 24
header_h, caption_h, footer_h = 88, 84, 70
canvas_w = margin * 2 + panel_w * 3 + gap * 2
canvas_h = header_h + panel_h + caption_h + footer_h

canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
draw = ImageDraw.Draw(canvas)

heading = "POMCA río Aburrá · previsualización de capas climáticas"
box = draw.textbbox((0, 0), heading, font=title_font)
draw.text(((canvas_w - (box[2] - box[0])) / 2, 22), heading, fill="#17202a", font=title_font)

for index, (image, (_, label, detail)) in enumerate(zip(images, PANELS)):
    x = margin + index * (panel_w + gap)
    y = header_h
    fitted = image.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
    canvas.paste(fitted, (x, y))
    draw.rectangle((x, y, x + panel_w - 1, y + panel_h - 1), outline="#4b5563", width=2)

    label_box = draw.textbbox((0, 0), label, font=panel_font)
    label_x = x + (panel_w - (label_box[2] - label_box[0])) / 2
    draw.text((label_x, y + panel_h + 13), label, fill="#111827", font=panel_font)

    detail_box = draw.textbbox((0, 0), detail, font=detail_font)
    detail_x = x + (panel_w - (detail_box[2] - detail_box[0])) / 2
    draw.text((detail_x, y + panel_h + 49), detail, fill="#4b5563", font=detail_font)

footer = (
    "Vista renderizada del MapServer del Área Metropolitana del Valle de Aburrá · "
    "MAGNA-SIRGAS / Colombia Bogotá zone (EPSG:21897) · no equivale al ráster numérico original."
)
footer_box = draw.textbbox((0, 0), footer, font=footer_font)
draw.text(
    ((canvas_w - (footer_box[2] - footer_box[0])) / 2, canvas_h - 43),
    footer,
    fill="#374151",
    font=footer_font,
)

canvas.save(OUTPUT, optimize=True)
print(OUTPUT)
