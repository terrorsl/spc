import reportlab.platypus
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageTemplate, Frame, Paragraph, PageBreak, Table, TableStyle, FrameBreak, KeepTogether, \
    NextPageTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from spc.spc_yaml import TitleApprove
from spc.standard.doc import SPCDocument, SPCChapter, SPCTable, SPCTitle, SPCList, SPCImage


class G105Image(SPCImage):
    def __init__(self, caption, filename, reference, image_index):
        super().__init__(caption=caption, filename=filename, reference=reference, image_index=image_index)
        self.caption = f'Рисунок {image_index} - {caption}'
        self.caption_alignment = TA_CENTER


class G105Title(SPCTitle):
    def __init__(self, company, caption, doc_type, approve, agrees):
        super().__init__(company, caption, doc_type)
        self.__approve = approve
        self.__agrees = agrees

    def build(self, font_name, font_size):
        style = ParagraphStyle(name='title', fontName=font_name, fontSize=font_size, alignment=TA_CENTER,
                               spaceAfter=10 * mm)
        company = Paragraph(f'{self.company}', style=style)
        if isinstance(self.__approve, str):
            data = [['Утвержден', ''], [self.__approve, '']]
        else:
            data = [['СОГЛАСОВАНО', 'УТВЕРЖДАЮ'],
                    [self.__agrees[0].job_name, self.__approve.job_name],
                    [f'__________ {self.__agrees[0].name}', f'__________ {self.__approve.name}'],
                    ['(подпись)', '(подпись)']]
        approve = Table(data, hAlign='CENTER', colWidths=(A4[0] - 40 * mm)/2, spaceAfter=10 * mm, style=TableStyle(
            [
                ('FONT', (0, 0), (-1, -1), font_name, font_size),
                # ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
        ))

        end = [PageBreak()]
        if not isinstance(self.__approve, str) and len(self.__agrees) > 1:
            data = [
                ['СОГЛАСОВАНО', '']
            ]
            if (len(self.__agrees) - 1) % 2:
                self.__agrees.append(TitleApprove(**{'name': '', 'job_name': ''}))

            tableStyle = TableStyle(
                [
                    ('FONT', (0, 0), (-1, -1), font_name, font_size),
                    # ('SPAN', (0, 19), (1, 19)),
                    # ('ALIGN', (0, 19), (1, 19), 'CENTER')
                ]
            )
            for index in range(1, len(self.__agrees)-1, 2):
                if index == 13:
                    data.append(['', ''])
                    data.append(['Продолжение на следующем листе', ''])
                    data.append(['Продолжение титульного листа', ''])
                    tableStyle.add('SPAN', (0, int(index/2)*3+2), (1, int(index/2)*3+2))
                    tableStyle.add('ALIGN', (0, int(index / 2) * 3 + 2), (1, int(index / 2) * 3 + 2), 'CENTER')
                    tableStyle.add('SPAN', (0, int(index / 2) * 3 + 3), (1, int(index / 2) * 3 + 3))
                    tableStyle.add('ALIGN', (0, int(index / 2) * 3 + 3), (1, int(index / 2) * 3 + 3), 'CENTER')
                if len(self.__agrees[index+1].job_name):
                    data.append([self.__agrees[index].job_name, self.__agrees[index + 1].job_name])
                    data.append([f'__________ {self.__agrees[index].name}', f'__________ {self.__agrees[index+1].name}'])
                    data.append(['(подпись)', '(подпись)'])
                else:
                    data.append([self.__agrees[index].job_name, ''])
                    data.append([f'_________ {self.__agrees[index].name}', ''])
                    data.append(['(подпись)', ''])
            table = Table(data, colWidths=(A4[0] - 40 * mm)/2, style=tableStyle)
            if len(self.__agrees) > 12:
                end = [NextPageTemplate('portrait'), table, PageBreak('portrait')]
            else:
                end = [table, PageBreak('portrait')]

        doc_name = Paragraph(f'{self.caption}', style=style)
        doc_type = Paragraph(text=self.document_type, style=style)
        return [company, approve, FrameBreak(), KeepTogether([doc_name, doc_type]), FrameBreak()]+end


class G105Table(SPCTable):
    def __init__(self, header, format_columns, index):
        super().__init__(header, index, format_columns)

    def build(self, font_name, font_size):
        items = []
        if self.caption:
            text = f'Таблица {self.table_index} - {self.caption}<a name=\"{self.label}\"/>'
            items.append(Paragraph(text, style=ParagraphStyle(name='', fontName=font_name, fontSize=font_size,
                                                              spaceBefore=6, spaceAfter=6)))
        items += super().build(font_name, font_size)

        return items


class G105Chapter(SPCChapter):
    def __init__(self, level, text, index):
        super().__init__(level, text, TA_LEFT)
        self.text = f'{index} {text}'
        self.indent = 15 * mm

    def replace_special(self):
        pass


class G105List(SPCList):
    def __init__(self, start, sub_list=False):
        super().__init__(start, ')', True, sub_list)

    def get_letter(self, index):
        if self.sub_list_index:
            return index
        letters = 'abcdefghijklmnopqrstuvwxyz'
        if index > len(letters):
            return index - len(letters)
        return letters[index - 1]


class G105NoBorderDoc(SPCDocument):
    def __init__(self, filename, font, font_family, debug=False):
        super().__init__(filename, font, font_family)

        pageTemplates = [
            PageTemplate(id='portrait', frames=[
                Frame(20 * mm, 15 * mm, A4[0] - 25 * mm, A4[1] - 30 * mm, showBoundary=debug)
            ], onPage=self.onPage),
            PageTemplate(id='landscape', frames=[
                Frame(20 * mm, 15 * mm, A4[1] - 25 * mm, A4[0] - 30 * mm, showBoundary=debug)
            ], onPage=self.onPage, pagesize=landscape(A4))
        ]
        self.addPageTemplates(pageTemplates=pageTemplates)

    def check(self, item):
        return True

    def save(self):
        for item in self.items:
            item.replace_special()
        super().save()

    def onPage(self, canvas, doc):
        canvas.saveState()

        if doc.page > 1:
            if self.pageTemplate.id == 'portrait':
                x = A4[0]
            else:
                x = A4[1]
            canvas.setFont(self.font_name, 12)
            canvas.drawString(x / 2, 5 * mm, f'{doc.page}')

        canvas.restoreState()
