from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageTemplate, Frame, Paragraph, PageBreak
from reportlab.lib.enums import TA_CENTER

from spc.standard.doc import SPCDocument, SPCTitle, SPCPageTemplate, SPCTableOfContent


class SimpleTitle(SPCTitle):
    def __init__(self, caption):
        super().__init__('', caption, '')

    def build(self, font_name, font_size):
        style = ParagraphStyle(name='Title', fontName=font_name, fontSize=font_size, alignment=TA_CENTER)
        return [Paragraph(f'{self.caption}', style=style), PageBreak()]


class SimpleDoc(SPCDocument):
    def __init__(self, filename, font, font_family, debug=False):
        super().__init__(filename, font, font_family)
        pageTemplates = [
            PageTemplate(id='portrait', frames=[
                Frame(20 * mm, 15 * mm, A4[0] - 25 * mm, A4[1] - 30 * mm, showBoundary=debug)
            ],
                         onPage=self.onPage)
        ]
        self.addPageTemplates(pageTemplates=pageTemplates)

    def check(self, item):
        return True

    def onPage(self, canvas, doc):
        canvas.saveState()

        canvas.drawString(A4[0] / 2, 5 * mm, f'{doc.page}')

        canvas.restoreState()
