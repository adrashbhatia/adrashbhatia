#!/usr/bin/env python3
"""dotify.py - turn a photo into a halftone dot-portrait SVG (Pillow only).

    python scripts/dotify.py assets/my_pic.png -o assets/portrait --cols 80

Transparent areas of the photo stay transparent. In dark mode the SVG inverts
lightness (keeping hue) so the portrait stays readable on a dark README.
"""
import argparse
from PIL import Image, ImageOps

def main():
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("-o", "--out", default="assets/portrait")
    p.add_argument("--cols", type=int, default=80)
    p.add_argument("--gamma", type=float, default=1.0, help=">1 darkens midtones (more face detail)")
    p.add_argument("--cell", type=float, default=5.0)
    p.add_argument("--crop-bottom", type=float, default=0.0, help="fraction of height to cut from the bottom")
    a = p.parse_args()

    im = Image.open(a.image).convert("RGBA")
    im = im.crop((0, 0, im.width, round(im.height * (1 - a.crop_bottom))))
    alpha = im.split()[3]
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    rgb = Image.alpha_composite(bg, im).convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=1)
    rgb = rgb.point(lambda v: int(255 * (v / 255) ** a.gamma))

    rows = round(a.cols * im.height / im.width)
    rgb = rgb.resize((a.cols, rows), Image.LANCZOS)
    alpha = alpha.resize((a.cols, rows), Image.LANCZOS)

    c = a.cell
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.cols*c:.0f} {rows*c:.0f}">',
           '<style>@media (prefers-color-scheme: dark){g{filter:invert(1) hue-rotate(180deg)}}</style><g>']
    for y in range(rows):
        for x in range(a.cols):
            al = alpha.getpixel((x, y)) / 255
            if al < 0.35:
                continue
            r, g, b = rgb.getpixel((x, y))
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            rad = c * (0.18 + 0.36 * (1 - lum) ** 0.6)
            out.append(f'<circle cx="{x*c+c/2:.1f}" cy="{y*c+c/2:.1f}" r="{rad:.2f}" fill="#{r:02x}{g:02x}{b:02x}"/>')
    out.append("</g></svg>")
    open(a.out + ".svg", "w").write("".join(out))
    print("wrote", a.out + ".svg")

if __name__ == "__main__":
    main()
