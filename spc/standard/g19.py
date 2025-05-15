import datetime

from reportlab.lib import colors
from reportlab.lib.fonts import tt2ps
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageTemplate, Frame, Paragraph, PageBreak, Table, TableStyle, Spacer, KeepTogether, \
    FrameBreak, NextPageTemplate, NotAtTopPageBreak, IndexingFlowable, NullActionFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.tableofcontents import SimpleIndex

from spc.standard.doc import SPCDocument, SPCChapter, SPCTitle, SPCItem, SPCList, SPCImage, TotalPage


class G19Image(SPCImage):
    def __init__(self, caption, filename, reference, image_index):
        super().__init__(caption, filename, reference, image_index)
        self.caption = f'Рисунок {image_index} - {caption}'
        self.caption_alignment = TA_CENTER


class G19List(SPCList):
    def __init__(self, start, on_replace):
        super().__init__(start, ')', on_replace=on_replace)
        self.leftIndent = 21 * mm

    def get_letter(self, index):
        pass


class G19Chapter(SPCChapter):
    def __init__(self, level, text, index):
        super().__init__(level, text, TA_LEFT)
        self.text = f'{index} {text}'
        self.indent = 10 * mm

    def replace_special(self):
        pass


class G19Specification(SPCItem):
    def __init__(self):
        self.__data = [['Обозначение', 'Наименование', 'Примечание']]
        super().__init__()

    def append(self, row):
        if len(row) != 3:
            raise Exception('row size must 3')
        self.__data.append(row)

    def build(self, font_name, font_size):
        style_table = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, font_size),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ]
        )
        # specials = ['Документация', 'Комплексы']
        # for row in self.__data:
        #     if row[1] in specials:

        table = Table(self.__data, colWidths=[80 * mm, 70 * mm, 30 * mm], style=style_table, repeatRows=1)
        result = [table]
        return result

    def replace_special(self):
        pass


class G19ChangeRegistrationSheet(SPCItem):
    def build(self, font_name, font_size):
        style_table = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, font_size),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('GRID', (0, 0), (-1, 2), 2, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('SPAN', (0, 0), (9, 0)),
            ('SPAN', (0, 1), (4, 1)),
            ('ALIGN', (0, 0), (-1, 2), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 2), 'MIDDLE'),
            ('SPAN', (5, 2), (5, 1)),
            ('SPAN', (6, 2), (6, 1)),
            ('SPAN', (7, 2), (7, 1)),
            ('SPAN', (8, 2), (8, 1)),
            ('SPAN', (9, 2), (9, 1)),
        ])
        data = [
            ['Лист регистрации изменений', '', '', '', '', '', '', '', '', ''],
            ['Номера листов(страниц)', '', '', '', '', 'Всего\nлистов\n(страниц)\nв докум', '№\nдокумента',
             'Входящий\n№ сопрово\nдительного\nдокумента\nи дата', 'Подп.', 'Да\nта'],
            ['Изм.', 'изменен\nных', 'заменен\nных', 'новых', 'анули\nрован\nных', '', '', '', '', ''],
            [],
            [],
            [],
            [],[],[],[],[],[],[], [],[],[],[],[],[],[], [],[],[],[],[],[],[], [],[],[],[],[],[]
        ]
        table = Table(data, colWidths=[10*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 25*mm, 25*mm, 15*mm, 12*mm],
                      style=style_table)
        return [table]

    def replace_special(self):
        pass


class G19NotificationSheet(SPCTitle):
    def __init__(self, company, caption, doc_type, approve, agrees):
        super().__init__(company, caption, doc_type)
        self.__approve = approve
        self.__agrees = agrees

    def build(self, font_name, font_size):
        style_center = ParagraphStyle(name='title_center', fontName=font_name, fontSize=font_size,
                                      alignment=TA_CENTER)
        style_right = ParagraphStyle(name='title_left', fontName=font_name, fontSize=font_size, alignment=TA_RIGHT)
        result = []
        # field 1
        if self.company:
            result.append(Paragraph(self.company, style=style_center))
        result.append(FrameBreak())
        # field 2
        data = [
            ['', 'УТВЕРЖДАЮ'],
            ['', self.__approve.job_name],
            ['', f'_______________{self.__approve.name}'],
            ['', '_______________20__г.']
        ]
        style_table = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, font_size),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # ('GRID', (0, 0), (-1, 2), 2, colors.black),
            # ('BOX', (0, 0), (-1, -1), 2, colors.black)
        ])
        col_width = (A4[0] - (50 * mm)) / 2
        table = Table(data, colWidths=[col_width, col_width], style=style_table)
        result.append(table)

        result.append(FrameBreak())
        # field 3
        result.append(Paragraph(f'{self.caption}', style=style_center))
        result.append(FrameBreak())
        # field 4
        result.append(Paragraph(f'ЛИСТ УТВЕРЖДЕНИЯ<br/><br/>{self.document_type}', style=style_center))
        result.append(FrameBreak())
        # filed 5
        # не заполняют
        result.append(FrameBreak())
        # field 6
        data = [['', 'СОГЛАСОВАНО']]
        for person in self.__agrees:
            # data.append(['', person.job_name])
            # data.append(['', f'_______________{person.name}'])
            # data.append(['', '_______________20__г.'])
            data.append(['', f'{person.job_name}\n_______________{person.name}\n_______________20__г.'])
            data.append(['', ''])

        style_table = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, font_size),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # ('GRID', (0, 0), (-1, 2), 2, colors.black),
            # ('BOX', (0, 0), (-1, -1), 2, colors.black)
        ])
        col_width = (A4[0] - (50 * mm))/2
        table = Table(data, colWidths=[col_width, col_width], style=style_table, repeatRows=1)
        result.append(table)
        result.append(FrameBreak())
        # field 7
        _7 = Paragraph(str(datetime.datetime.now().date().year), style=style_center)
        result.append(_7)
        result.append(FrameBreak())
        # field 8
        # field 9
        # field 10
        _10 = Paragraph('Литера', style=style_right)
        result.append(_10)
        return result


class G19ApprovalSheet(SPCItem):
    def build(self, font_name, font_size):
        return []


class G19Title(SPCTitle):
    def __init__(self, company, caption, doc_type, approve_doc):
        super().__init__(company, caption, doc_type)
        self.__approve_doc = approve_doc
        self.__page_count = 0

    @property
    def page_count(self):
        return self.__page_count

    @page_count.setter
    def page_count(self, v):
        self.__page_count = v

    def build(self, font_name, font_size):
        style_center = ParagraphStyle(name='title_center', fontName=font_name, fontSize=font_size,
                                      alignment=TA_CENTER)
        style_left = ParagraphStyle(name='title_left', fontName=font_name, fontSize=font_size)
        style_right = ParagraphStyle(name='title_left', fontName=font_name, fontSize=font_size, alignment=TA_RIGHT)
        style_3 = ParagraphStyle(name='3', parent=style_center, spaceBefore=40 * mm)
        style_4 = ParagraphStyle(name='4', parent=style_center, spaceBefore=10 * mm)
        style_5 = ParagraphStyle(name='5', parent=style_center, spaceBefore=20 * mm, spaceAfter=120 * mm)
        style_7 = ParagraphStyle(name='7', parent=style_center, spaceBefore=1 * mm, spaceAfter=1 * mm)
        result = [NotAtTopPageBreak('title')]

        # field 1
        if self.company:
            result.append(Paragraph(self.company, style=style_center))
        result.append(Paragraph(f'Утвержден<br/>{self.__approve_doc}', style=style_left))
        result.append(FrameBreak())
        # field 2
        # не заполняют
        result.append(FrameBreak())
        # field 3
        result.append(Paragraph(f'{self.caption}', style=style_center))
        result.append(FrameBreak())
        # field 4
        result.append(Paragraph(self.document_type, style=style_center))
        result.append(FrameBreak())
        # filed 5
        result.append(TotalPage(font_name, font_size))
        result.append(FrameBreak())
        # result.append(_5)
        # field 6
        # не заполняют
        result.append(FrameBreak())
        # field 7
        _7 = Paragraph(str(datetime.datetime.now().date().year), style=style_7)
        result.append(_7)
        result.append(FrameBreak())
        # field 8
        # field 9
        # field 10
        _10 = Paragraph('Литера', style=style_right)
        result.append(_10)
        result.append(PageBreak('portrait'))

        return result


class G19Appendix(SPCItem):
    def __init__(self, caption, appendix_index):
        super().__init__()
        self.appendix_index = appendix_index

    def build(self, font_name, font_size):
        style = ParagraphStyle(name='appendix', fontName=font_name, fontSize=font_size)
        return [Paragraph(f'ПРИЛОЖЕНИЕ {self.appendix_index}', style=style)]

    def replace_special(self):
        pass


class G19(SPCDocument):
    def __init__(self, filename, font, font_family, debug):
        super().__init__(filename, font, font_family)

        pageTemplates = [
            PageTemplate(id='title', frames=[
                Frame(20 * mm, A4[1] - 25 * mm, A4[0] - 30 * mm, 20 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 85 * mm, A4[0] - 30 * mm, 60 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 125 * mm, A4[0] - 30 * mm, 40 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 145 * mm, A4[0] - 30 * mm, 20 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 160 * mm, A4[0] - 30 * mm, 15 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 265 * mm, A4[0] - 30 * mm, 105 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 275 * mm, A4[0] - 30 * mm, 10 * mm, showBoundary=debug),
                Frame(20 * mm, A4[1] - 285 * mm, A4[0] - 30 * mm, 10 * mm, showBoundary=debug)

                # Frame(20 * mm, (5 + 2*93) * mm, A4[0] - 25 * mm, 93 * mm, showBoundary=debug),
                # Frame(20 * mm, (5+93) * mm, A4[0] - 25 * mm, 93 * mm, showBoundary=debug),
                # Frame(20 * mm, 5 * mm, A4[0] - 25 * mm, 93 * mm, showBoundary=debug)
            ], onPage=self.onPage),
            PageTemplate(id='portrait', frames=[
                Frame(20 * mm, 15 * mm, A4[0] - 30 * mm, A4[1] - 40 * mm, showBoundary=debug)
            ], onPage=self.onPage),
            PageTemplate(id='landscape', frames=[
                Frame(20 * mm, 15 * mm, A4[1] - 30 * mm, A4[0] - 40 * mm, showBoundary=debug)
            ], onPage=self.onPage, pagesize=landscape(A4)),
        ]

        self.addPageTemplates(pageTemplates=pageTemplates)

        self.__doc_type = ''
        self.__page_count = 0
        self.__pass = 0
        self.setProgressCallBack(self.onProgress)

    def onProgress(self, param, value):
        print(f'{param} - {value}')
        if param == 'PASS':
            self.__pass = value
        elif param == 'PAGE' and self.__pass == 1:
            self.__page_count = value
        elif param == 'FINISHED':
            for item in self.flowable:
                if isinstance(item, TotalPage):
                    item.page_count = self.__page_count

    def check(self, item):
        if isinstance(item, G19Title):
            self.__doc_type = item.document_type
        return True

    def save(self):
        if not isinstance(self.items[0], G19NotificationSheet):
            self.append(G19ChangeRegistrationSheet())
        for item in self.items:
            item.replace_special()
        print('save')
        super().save()

    def beforeDocument(self):
        print('beforeDocument')

    def onPage(self, canvas, doc):
        width = A4[0]
        height = A4[1]

        if doc.page == 1:
            font_name = tt2ps(self.font_name, 0, 1)
            canvas.setFont(font_name, 10)
            # left stamp
            canvas.line(20 * mm, 5 * mm, 20 * mm, 150 * mm)
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
        else:
            canvas.setFont(self.font_name, 12)
            canvas.drawString(width/2, height-15, str(doc.page))
            canvas.drawCentredString(width / 2, height - 25, self.__doc_type)
