"""Small helpers on top of python-pptx so every slide shares one layout."""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

INK = RGBColor(0x0b, 0x0b, 0x0b)
INK2 = RGBColor(0x52, 0x51, 0x4e)
MUTED = RGBColor(0x89, 0x87, 0x81)
BLUE = RGBColor(0x1c, 0x5c, 0xab)
ORANGE = RGBColor(0xeb, 0x68, 0x34)
SURFACE = RGBColor(0xfc, 0xfc, 0xfb)
PANEL = RGBColor(0xf0, 0xef, 0xec)
WHITE = RGBColor(0xff, 0xff, 0xff)

W, H = 13.333, 7.5


class Deck:
    def __init__(self, footer):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(W), Inches(H)
        self.footer = footer
        self.n = 0

    def slide(self, title=None, kicker=None):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.n += 1
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = SURFACE
        if title:
            bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6),
                                     Inches(0.55), Inches(0.12), Inches(0.75))
            bar.fill.solid()
            bar.fill.fore_color.rgb = ORANGE
            bar.line.fill.background()
            if kicker:
                self.text(s, kicker, 0.9, 0.38, 11.5, 0.35, size=13, color=MUTED)
            self.text(s, title, 0.9, 0.62 if kicker else 0.5, 11.8, 0.8,
                      size=30, bold=True)
        self.text(s, self.footer, 0.6, 7.0, 9, 0.3, size=11, color=MUTED)
        self.text(s, str(self.n), 12.1, 7.0, 0.7, 0.3, size=11, color=MUTED,
                  align="right")
        return s

    def text(self, s, text, x, y, w, h, size=18, bold=False, color=INK,
             align="left", anchor="top", italic=False):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
                              "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"left": 1, "center": 2, "right": 3}[align]
            r = p.add_run()
            r.text = line
            f = r.font
            f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, "Calibri"
            f.color.rgb = color
        return box

    def bullets(self, s, items, x, y, w, h, size=19, gap=10):
        """items: strings, or (lead, rest) tuples where lead is set in bold."""
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(gap)
            lead, rest = item if isinstance(item, tuple) else ("", item)
            for txt, bold in ((lead, True), (rest, False)):
                if not txt:
                    continue
                r = p.add_run()
                r.text = txt
                r.font.size, r.font.bold, r.font.name = Pt(size), bold, "Calibri"
                r.font.color.rgb = INK
        return box

    def panel(self, s, x, y, w, h, color=PANEL):
        shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                 Inches(y), Inches(w), Inches(h))
        shp.adjustments[0] = 0.06
        shp.fill.solid()
        shp.fill.fore_color.rgb = color
        shp.line.fill.background()
        return shp

    def image(self, s, path, x, y, w=None, h=None):
        return s.shapes.add_picture(path, Inches(x), Inches(y),
                                    Inches(w) if w else None,
                                    Inches(h) if h else None)

    def table(self, s, rows, x, y, w, h, col_widths=None, size=14,
              highlight_rows=(), numeric=True):
        shape = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                   Inches(w), Inches(h))
        t = shape.table
        if col_widths:
            for i, cw in enumerate(col_widths):
                t.columns[i].width = Inches(cw)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                cell = t.cell(r, c)
                cell.text = str(val) or " "
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.04)
                par = cell.text_frame.paragraphs[0]
                par.alignment = 1 if c == 0 or not numeric else 3
                f = par.runs[0].font
                f.size, f.name = Pt(size), "Calibri"
                f.bold = r == 0 or r in highlight_rows
                f.color.rgb = WHITE if r == 0 else INK
                cell.fill.solid()
                cell.fill.fore_color.rgb = (BLUE if r == 0 else
                                            RGBColor(0xfd, 0xe9, 0xdf)
                                            if r in highlight_rows else
                                            SURFACE if r % 2 else PANEL)
        return shape

    def save(self, path):
        self.prs.save(path)


def to_pdf(pptx_path, pdf_path):
    """Export through PowerPoint (Windows only)."""
    import win32com.client
    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(pptx_path, ReadOnly=True, WithWindow=False)
        pres.SaveAs(pdf_path, 32)   # 32 = ppSaveAsPDF
        pres.Close()
    finally:
        app.Quit()
