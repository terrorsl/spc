from abc import ABC, abstractmethod
from hashlib import sha1
from typing import Literal, Optional, List, Union

import reportlab.platypus
import yaml
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Paragraph, Image, PageBreak, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


class SCPItem(ABC):
    @abstractmethod
    def build(self, font_name):
        pass


class SCPImage(SCPItem):
    def __init__(self, caption, filename, reference):
        self.__caption = caption
        self.__filename = filename
        self.__reference = reference

    def build(self, font_name):
        style = ParagraphStyle(name='', fontName=font_name)
        caption = f''
        return [Image(filename=self.__filename), Paragraph(caption)]


class SPCList(SCPItem):
    def __init__(self, start, afterbullet='.'):
        self.__items = []
        self.__start = start
        self.__after = afterbullet

    def append(self, item):
        self.__items.append(item)

    def build(self, font_name):
        result = []
        style = ParagraphStyle(name='_Heading1',
                               fontName=font_name,
                               # alignment=TA_CENTER,
                               bulletIndent=15 * mm, #+ (15 * mm if not self.__start else 0),
                               bulletFontName=font_name,
                               # bulletFontSize=self.font_size,
                               # leading=22,
                               spaceAfter=6)
        for index, item in enumerate(self.__items):
            if isinstance(item, SPCParagraph):
                if not self.__start:
                    bullet = '-'
                else:
                    bullet = f'{self.__start+index}{self.__after}'
                result.append(Paragraph(f'<bullet>{bullet}</bullet>{item.text}', style=style))
            elif isinstance(item, SPCList):
                # result.append(Paragraph('<bullet>1</bullet>test'))
                result += item.build(font_name)
        return result


class SPCTable(SCPItem):
    def __init__(self):
        self.__header = ['%', '1', '2', '3', 'День', 'Месяц']
        self.__columns = ['str', 'color', 'str', 'str', 'int', 'span']
        self.__data = [
            ['%', 'Время труда и отдыха', 'Самочувствие', 'Предкпреждение', 'День', 'Месяц'],
            [56, 'yellow', '2', '3', 1, 'Январь'],
            [56, 'yellow', '2', '3', 2, 'Январь'],
            [56, 'yellow', '2', '3', 3, 'Январь'],
            [59, 'yellow', '2', '3', 4, 'Январь'],
            [59, 'yellow', '2', '3', 5, 'Январь'],
            [67, 'green', '2', '3', 6, 'Январь'],
            [67, 'green', '2', '3', 7, 'Январь'],
            [67, 'green', '2', '3', 8, 'Январь'],
            [67, 'green', '2', '3', 9, 'Январь'],
            [67, 'green', '2', '3', 10, 'Январь'],
            [67, 'green', '2', '3', 11, 'Январь'],
            [67, 'green', '2', '3', 12, 'Январь'],
            [67, 'green', '2', '3', 13, 'Январь'],
            [67, 'green', '2', '3', 14, 'Январь'],
            [67, 'green', '2', '3', 15, 'Январь'],
            [67, 'green', '2', '3', 16, 'Январь'],
            [67, 'green', '2', '3', 17, 'Январь'],
            [67, 'green', '2', '3', 18, 'Январь'],
            [67, 'green', '2', '3', 19, 'Январь'],
            [67, 'green', '2', '3', 20, 'Январь'],
            [67, 'green', '2', '3', 21, 'Январь'],
            [81, 'darkgreen', '2', '3', 22, 'Январь'],
            [81, 'darkgreen', '2', '3', 23, 'Январь'],
            [81, 'darkgreen', '2', '3', 24, 'Январь'],
            [81, 'darkgreen', '2', '3', 25, 'Январь'],
            [81, 'darkgreen', '2', '3', 26, 'Январь'],
            [81, 'darkgreen', '2', '3', 27, 'Январь'],
            [81, 'darkgreen', '2', '3', 28, 'Январь'],
            [81, 'darkgreen', '2', '3', 29, 'Январь'],
            [81, 'darkgreen', '2', '3', 30, 'Январь'],
            [81, 'darkgreen', '2', '3', 31, 'Январь'],
            [81, 'darkgreen', '2', '3', 1, 'Февраль'],
            [81, 'darkgreen', '2', '3', 2, 'Февраль'],
            [81, 'darkgreen', '2', '3', 3, 'Февраль'],
            [81, 'darkgreen', '2', '3', 4, 'Февраль'],
            [81, 'darkgreen', '2', '3', 5, 'Февраль'],
            [81, 'darkgreen', '2', '3', 6, 'Февраль'],
            [81, 'darkgreen', '2', '3', 7, 'Февраль'],
            [81, 'darkgreen', '2', '3', 8, 'Февраль'],
            [81, 'darkgreen', '2', '3', 9, 'Февраль'],
            [81, 'darkgreen', '2', '3', 10, 'Февраль'],
            [81, 'darkgreen', '2', '3', 11, 'Февраль'],
            [81, 'darkgreen', '2', '3', 12, 'Февраль'],
            [81, 'darkgreen', '2', '3', 13, 'Февраль'],
            [81, 'darkgreen', '2', '3', 14, 'Февраль'],
            [81, 'darkgreen', '2', '3', 15, 'Февраль'],
            [81, 'darkgreen', '2', '3', 16, 'Февраль'],
            [81, 'darkgreen', '2', '3', 17, 'Февраль'],
            [81, 'darkgreen', '2', '3', 18, 'Февраль'],
            [81, 'darkgreen', '2', '3', 19, 'Февраль'],
            [81, 'darkgreen', '2', '3', 20, 'Февраль'],
            [81, 'darkgreen', '2', '3', 21, 'Февраль'],
            [81, 'darkgreen', '2', '3', 22, 'Февраль'],
            [81, 'darkgreen', '2', '3', 23, 'Февраль'],
            [81, 'darkgreen', '2', '3', 24, 'Февраль'],
            [81, 'darkgreen', '2', '3', 25, 'Февраль'],
            [81, 'darkgreen', '2', '3', 26, 'Февраль'],
            [81, 'darkgreen', '2', '3', 27, 'Февраль'],
            [81, 'darkgreen', '2', '3', 28, 'Февраль'],
            [81, 'darkgreen', '2', '3', 29, 'Февраль'],
            [81, 'darkgreen', '2', '3', 1, 'Март'],
            [81, 'darkgreen', '2', '3', 2, 'Март'],
            [81, 'darkgreen', '2', '3', 3, 'Март'],
            [69, 'green', '2', '3', 4, 'Март'],
            [69, 'green', '2', '3', 5, 'Март'],
            [69, 'green', '2', '3', 6, 'Март'],
            [69, 'green', '2', '3', 7, 'Март'],
            [69, 'green', '2', '3', 8, 'Март'],
        ]

    def build(self, font_name):
        table_style = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (5, 0), (5, -1), 'MIDDLE')
        ])

        for col, cvalue in enumerate(self.__columns):
            if cvalue == 'color':
                _len = len(self.__data)
                for row in range(1, _len):
                    rvalue = self.__data[row]
                    if rvalue[col] == 'yellow':
                        table_style.add('BACKGROUND', (col, row), (col, row), colors.yellow)
                    elif rvalue[col] == 'green':
                        table_style.add('BACKGROUND', (col, row), (col, row), colors.green)
                    elif rvalue[col] == 'darkgreen':
                        table_style.add('BACKGROUND', (col, row), (col, row), colors.darkgreen)
                    rvalue[col] = ''
                    self.__data[row] = rvalue
            elif cvalue == 'span':
                start = 1
                _len = len(self.__data) - 1
                for row in range(1, _len):
                    rcurrent = self.__data[row][col]
                    rnext = self.__data[row+1][col]
                    if rcurrent != rnext:
                        table_style.add('SPAN', (col, start), (col, row))
                        start = row + 1
                table_style.add('SPAN', (col, start), (col, _len))

        table = Table(data=self.__data, repeatRows=1)
        table.setStyle(table_style)
        return [table]


class SPCTitle(SCPItem):
    def __init__(self, company, caption):
        self.__company = company
        self.__caption = caption

    @property
    def company(self):
        return self.__company

    @property
    def caption(self):
        return self.__caption


class SPCParagraph(SCPItem):
    def __init__(self, text):
        self.__text = text

    @property
    def text(self):
        return self.__text

    def build(self, font_name):
        style = ParagraphStyle(name="text", fontName=font_name, firstLineIndent=15)
        return [reportlab.platypus.Paragraph(self.__text, style=style)]


class SPCChapter(SCPItem):
    def __init__(self, level, text):
        self.__level = level
        self.__text = text
        self.__align = TA_CENTER

    def build(self, font_name):
        style = ParagraphStyle(name=f'Heading{self.__level}', fontName=font_name, fontSize=14,
                               spaceBefore=5 * mm,
                               spaceAfter=5 * mm,
                               alignment=self.__align
                               )
        bn = sha1(self.__text.encode()).hexdigest()
        item = Paragraph(f'<b>{self.__text}</b><a name="{bn}"/>', style=style)
        item._bookmarkName = bn
        return [item]


class SPCTableOfContent(SCPItem):
    def __init__(self, title):
        self.__title = title

    def build(self, font_name):
        style = ParagraphStyle(name='toc', fontName=font_name, alignment=TA_CENTER)
        p = Paragraph(self.__title, style=style)
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(fontName=font_name, name='Heading1')
        ]
        return [p, toc, PageBreak()]


class SPCPageTemplate:
    def __init__(self, id, pagesize):
        self.__page_template = reportlab.platypus.PageTemplate(id, pagesize=pagesize)


class Font(BaseModel):
    name: str
    filename: str
    type: Literal['normal', 'bold', 'italic']


class FontFamily(BaseModel):
    family: str
    fonts: List[Font]


class Config(BaseModel):
    standard: Literal['g105', 'simple']
    output: str
    font: FontFamily
    table_of_content: Optional[str] = ''


class Markdown(BaseModel):
    name: str


class Item(BaseModel):
    type: Literal['image', 'markdown']
    name: str


class Title(BaseModel):
    caption: str
    company: str


class SPC(BaseModel):
    config: Config = Field()
    title: Title
    # custom_title: str
    items: List[Item]


class SPCDocument(ABC, BaseDocTemplate):
    def __init__(self, filename, font: dict, font_family: dict):
        BaseDocTemplate.__init__(self, filename)
        self.__items = []
        self.__flowable = []
        for key, value in font.items():
            pdfmetrics.registerFont(TTFont(key, value))
        for key, value in font_family.items():
            registerFontFamily(key, normal=value['normal'], bold=value['bold'], italic=value['italic'])
        self.__font_name = ''

    def set_font(self, font_name):
        self.__font_name = font_name

    def set_table_of_content(self, title):
        self.append(SPCTableOfContent(title))

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                level = 0
            elif style == 'Heading2':
                level = 1
            else:
                return
            bn = getattr(flowable, '_bookmarkName', None)
            if bn:
                self.notify('TOCEntry', (level, text, self.page, bn))
            else:
                self.notify('TOCEntry', (level, text, self.page))

    @abstractmethod
    def check(self, item):
        pass

    def append(self, item):
        if self.check(item):
            self.__items.append(item)

    def save(self):
        for item in self.__items:
            self.__flowable += item.build(self.__font_name)
        self.multiBuild(self.__flowable)
