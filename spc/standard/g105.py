from reportlab.lib.fonts import tt2ps
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import getFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageTemplate, Frame

from spc.standard.doc import SPCDocument
from spc.standard.g105_no_border import G105Title


class G105Doc(SPCDocument):
    def __init__(self, filename, font, font_family, debug=False):
        super().__init__(filename, font, font_family)

        pageTemplates = [
            PageTemplate(id='portrait', frames=[
                Frame(20 * mm, 20 * mm, A4[0] - 25 * mm, A4[1] - 30 * mm, showBoundary=debug)
            ], onPage=self.onPage),
            PageTemplate(id='landscape', frames=[
                Frame(20 * mm, 20 * mm, A4[1] - 25 * mm, A4[0] - 30 * mm, showBoundary=debug)
            ], onPage=self.onPage, pagesize=landscape(A4))
        ]
        self.addPageTemplates(pageTemplates=pageTemplates)
        self.__is_title = False
        self.__page_count = 0
        self.__document_type = ''

    def check(self, item):
        return True

    def save(self):
        for item in self.items:
            if isinstance(item, G105Title):
                self.__is_title = True
                self.__document_type = item.document_type
            item.replace_special()
        super().save()

    def onPage(self, canvas, doc):
        self.__page_count += 1
        x = 20 * mm
        y = 5 * mm
        if self.pageTemplate.id == 'portrait':
            width = A4[0]
            height = A4[1]
        else:
            width = A4[1]
            height = A4[0]

        font_name = tt2ps(self.font_name, 0, 1)
        canvas.setFont(font_name, 10)
        canvas.line(x, y, x, height - y)
        canvas.line(width - y, y, width - y, height - y)

        canvas.line(x, y, width - y, y)
        canvas.line(x, height - y, width - y, height - y)

        # left stamp
        canvas.line(13 * mm, 5 * mm, 13 * mm, 150 * mm)
        canvas.line(8 * mm, 5 * mm, 8 * mm, 150 * mm)

        canvas.line(8 * mm, 5 * mm, 20 * mm, 5 * mm)
        canvas.line(8 * mm, 30 * mm, 20 * mm, 30 * mm)
        canvas.line(8 * mm, 65 * mm, 20 * mm, 65 * mm)
        canvas.line(8 * mm, 90 * mm, 20 * mm, 90 * mm)
        canvas.line(8 * mm, 115 * mm, 20 * mm, 115 * mm)
        canvas.line(8 * mm, 150 * mm, 20 * mm, 150 * mm)

        canvas.rotate(90)
        canvas.drawString(20, -35, 'Инв. № подп.')
        canvas.drawString(90, -35, 'Подп. и дата')
        canvas.drawString(190, -35, 'Взам. инв. №')
        canvas.drawString(260, -35, 'Инв. № дубл.')
        canvas.drawString(330, -35, 'Подп. и дата')
        canvas.rotate(-90)

        if self.__is_title and doc.page == 1:
            return
        if self.__is_title and doc.page == 2 or doc.page == 1:
            canvas.line(A4[0] - 190 * mm, 45 * mm, A4[0] - 5 * mm, 45 * mm)
            canvas.line(A4[0] - 190 * mm, 30 * mm, A4[0] - 5 * mm, 30 * mm)

            canvas.line(A4[0] - 125 * mm, 40 * mm, A4[0] - 190 * mm, 40 * mm)
            canvas.line(A4[0] - 125 * mm, 35 * mm, A4[0] - 190 * mm, 35 * mm)
            canvas.line(A4[0] - 125 * mm, 30 * mm, A4[0] - 190 * mm, 30 * mm)
            canvas.line(A4[0] - 125 * mm, 25 * mm, A4[0] - 190 * mm, 25 * mm)
            canvas.line(A4[0] - 125 * mm, 20 * mm, A4[0] - 190 * mm, 20 * mm)
            canvas.line(A4[0] - 125 * mm, 15 * mm, A4[0] - 190 * mm, 15 * mm)
            canvas.line(A4[0] - 125 * mm, 10 * mm, A4[0] - 190 * mm, 10 * mm)

            canvas.line(A4[0] - 125 * mm, 5 * mm, A4[0] - 125 * mm, 45 * mm)
            canvas.line(A4[0] - 135 * mm, 5 * mm, A4[0] - 135 * mm, 45 * mm)
            canvas.line(A4[0] - 150 * mm, 5 * mm, A4[0] - 150 * mm, 45 * mm)
            canvas.line(A4[0] - 173 * mm, 5 * mm, A4[0] - 173 * mm, 45 * mm)

            canvas.line(A4[0] - 183 * mm, 30 * mm, A4[0] - 183 * mm, 45 * mm)

            canvas.drawString(A4[0] - 134 * mm, 31 * mm, 'Дата')
            canvas.drawString(A4[0] - 149 * mm, 31 * mm, 'Подп.')
            canvas.drawString(A4[0] - 172 * mm, 31 * mm, '№ докум.')
            canvas.drawString(A4[0] - 182 * mm, 31 * mm, 'Лист')
            canvas.drawString(A4[0] - 190 * mm, 31 * mm, 'Изм.')

            canvas.line(A4[0] - 55 * mm, 20 * mm, A4[0] - 5 * mm, 20 * mm)
            canvas.line(A4[0] - 55 * mm, 25 * mm, A4[0] - 5 * mm, 25 * mm)

            canvas.line(A4[0] - 55 * mm, 5 * mm, A4[0] - 55 * mm, 30 * mm)
            canvas.line(A4[0] - 40 * mm, 20 * mm, A4[0] - 40 * mm, 30 * mm)
            canvas.line(A4[0] - 25 * mm, 20 * mm, A4[0] - 25 * mm, 30 * mm)

            canvas.drawString(A4[0] - 54 * mm, 26 * mm, 'Лит.')
            canvas.drawString(A4[0] - 39 * mm, 26 * mm, 'Лист')
            canvas.drawCentredString(A4[0] - 15 * mm, 26 * mm, 'Листов')
            canvas.drawCentredString(A4[0] - 35 * mm, 21 * mm, str(canvas.getPageNumber()))
            canvas.drawCentredString(A4[0] - 15 * mm, 21 * mm, str(self.__page_count))
        else:
            canvas.line(width - 190 * mm, 20 * mm, width - 5 * mm, 20 * mm)
            canvas.line(width - 15 * mm, 13 * mm, width - 5 * mm, 13 * mm)

            canvas.line(width - 190 * mm, 5 * mm, width - 190 * mm, 20 * mm)

            canvas.line(width - 15 * mm, 5 * mm, width - 15 * mm, 20 * mm)
            canvas.drawString(width - 14 * mm, 15 * mm, 'Лист')
            canvas.drawCentredString(width - 10 * mm, 8 * mm, str(canvas.getPageNumber()))

            canvas.line(width - 125 * mm, 5 * mm, width - 125 * mm, 20 * mm)
            canvas.line(width - 135 * mm, 5 * mm, width - 135 * mm, 20 * mm)
            canvas.line(width - 150 * mm, 5 * mm, width - 150 * mm, 20 * mm)
            canvas.line(width - 173 * mm, 5 * mm, width - 173 * mm, 20 * mm)
            canvas.line(width - 183 * mm, 5 * mm, width - 183 * mm, 20 * mm)

            canvas.line(width - 190 * mm, 10 * mm, width - 125 * mm, 10 * mm)
            canvas.line(width - 190 * mm, 15 * mm, width - 125 * mm, 15 * mm)

            canvas.drawString(width - 134 * mm, 6 * mm, 'Дата')
            canvas.drawString(width - 149 * mm, 6 * mm, 'Подп.')
            canvas.drawString(width - 172 * mm, 6 * mm, '№ докум.')
            canvas.drawString(width - 182 * mm, 6 * mm, 'Лист')
            canvas.drawString(width - 190 * mm, 6 * mm, 'Изм.')

            # canvas.drawString(A4[0] - 125 * mm, 6 * mm, self.__document_type)
        canvas.drawString(width - 35 * mm, 1 * mm, 'Формат A4')
        canvas.drawString(width - 95 * mm, 1 * mm, 'Копировал')
