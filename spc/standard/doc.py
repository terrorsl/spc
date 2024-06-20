import re
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


class SPCItem(ABC):
    def __init__(self, on_replace=None):
        self.onReplace = on_replace
        self.__symbol_spesials = {
            '%landscape': PageBreak('landscape'),
            '%portrait': PageBreak('portrait'),
            '%pagebreak': PageBreak()
        }

    @abstractmethod
    def build(self, font_name, font_size):
        pass

    @abstractmethod
    def replace_special(self):
        pass

    def find_special(self, text):
        result = []
        for key, item in self.__symbol_spesials.items():
            span = re.search(key, text)
            if span:
                result.append(item)
        return result

    def find_and_replace(self, text):
        result = re.search(r"%ref\(\w+\)", text)
        if result:
            label = text[result.start(): result.end()]
            s = label.replace('%ref(', '')
            s = s.replace(')', '')
            if self.onReplace:
                index = self.onReplace(s)
                text = text.replace(label, f'<a href="#{s}">{index}</a>')
        return text


class SCPImage(SPCItem):
    def __init__(self, caption, filename, reference):
        self.__caption = caption
        self.__filename = filename
        self.__reference = reference

    def build(self, font_name, font_size):
        style = ParagraphStyle(name='', fontName=font_name)
        caption = f''
        return [Image(filename=self.__filename), Paragraph(caption)]


class SPCList(SPCItem):
    def __init__(self, start, afterbullet='.', is_letter=False, is_sub_list_index=0):
        super().__init__()
        self.__items = []
        self.__start = start
        self.__after = afterbullet
        self.__is_letter = is_letter
        self.__sub_list_index = is_sub_list_index

    def replace_special(self):
        pass

    @property
    def sub_list_index(self):
        return self.__sub_list_index

    @abstractmethod
    def get_letter(self, index):
        pass

    def append(self, item):
        self.__items.append(item)

    def build(self, font_name, font_size):
        result = []
        style = ParagraphStyle(name='_Heading1',
                               fontName=font_name,
                               fontSize=font_size,
                               # alignment=TA_CENTER,
                               bulletIndent=15 * mm + (15 * mm * self.__sub_list_index),
                               bulletFontName=font_name,
                               bulletFontSize=font_size,
                               # leading=22,
                               spaceAfter=6)
        index = 0
        for item in self.__items:
            if isinstance(item, SPCParagraph):
                if not self.__start:
                    bullet = '-'
                elif self.__is_letter:
                    bullet = f'{self.get_letter(self.__start + index)}{self.__after}'
                else:
                    bullet = f'{self.__start+index}{self.__after}'
                result.append(Paragraph(f'<bullet>{bullet}</bullet>{item.text}', style=style))
                index += 1
            elif isinstance(item, SPCList):
                # result.append(Paragraph('<bullet>1</bullet>test'))
                result += item.build(font_name, font_size)
        return result


class SPCTable(SPCItem):
    def __init__(self, header, table_index, format_columns):
        # super().__init__()
        self.__header = header
        self.__columns = format_columns
        self.__data = [header]
        self.__caption = ''
        self.__label = '__'
        self.__index = table_index
        # self.__header = ['%', '1', '2', '3', 'День', 'Месяц']
        # self.__columns = ['str', 'color', 'str', 'str', 'int', 'span']
        # self.__data = [
        #     ['%', 'Время труда и отдыха', 'Самочувствие', 'Предкпреждение', 'День', 'Месяц'],
        #     [56, 'yellow', '2', '3', 1, 'Январь'],
        #     [56, 'yellow', '2', '3', 2, 'Январь'],
        #     [56, 'yellow', '2', '3', 3, 'Январь'],
        #     [59, 'yellow', '2', '3', 4, 'Январь'],
        #     [59, 'yellow', '2', '3', 5, 'Январь'],
        #     [67, 'green', '2', '3', 6, 'Январь'],
        #     [67, 'green', '2', '3', 7, 'Январь'],
        #     [67, 'green', '2', '3', 8, 'Январь'],
        #     [67, 'green', '2', '3', 9, 'Январь'],
        #     [67, 'green', '2', '3', 10, 'Январь'],
        #     [67, 'green', '2', '3', 11, 'Январь'],
        #     [67, 'green', '2', '3', 12, 'Январь'],
        #     [67, 'green', '2', '3', 13, 'Январь'],
        #     [67, 'green', '2', '3', 14, 'Январь'],
        #     [67, 'green', '2', '3', 15, 'Январь'],
        #     [67, 'green', '2', '3', 16, 'Январь'],
        #     [67, 'green', '2', '3', 17, 'Январь'],
        #     [67, 'green', '2', '3', 18, 'Январь'],
        #     [67, 'green', '2', '3', 19, 'Январь'],
        #     [67, 'green', '2', '3', 20, 'Январь'],
        #     [67, 'green', '2', '3', 21, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 22, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 23, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 24, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 25, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 26, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 27, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 28, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 29, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 30, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 31, 'Январь'],
        #     [81, 'darkgreen', '2', '3', 1, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 2, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 3, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 4, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 5, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 6, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 7, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 8, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 9, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 10, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 11, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 12, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 13, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 14, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 15, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 16, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 17, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 18, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 19, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 20, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 21, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 22, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 23, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 24, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 25, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 26, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 27, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 28, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 29, 'Февраль'],
        #     [81, 'darkgreen', '2', '3', 1, 'Март'],
        #     [81, 'darkgreen', '2', '3', 2, 'Март'],
        #     [81, 'darkgreen', '2', '3', 3, 'Март'],
        #     [69, 'green', '2', '3', 4, 'Март'],
        #     [69, 'green', '2', '3', 5, 'Март'],
        #     [69, 'green', '2', '3', 6, 'Март'],
        #     [69, 'green', '2', '3', 7, 'Март'],
        #     [69, 'green', '2', '3', 8, 'Март'],
        # ]

    def append(self, row):
        self.__data.append(row)

    @property
    def caption(self):
        return self.__caption

    @property
    def label(self):
        return self.__label

    @property
    def table_index(self):
        return self.__index

    def replace_special(self):
        pass

    def set_caption(self, value):
        x = re.search(r"%label\(\w+\)", value)
        if x:
            label = value[x.start(): x.end()]
            value = value[:x.start()]
            # label = label.replace('%label(', '<a name=\"')
            # label = label.replace(')', '\"/>')
            label = label.replace('%label(', '')
            label = label.replace(')', '')
            self.__label = label
        self.__caption = value

    def build(self, font_name, font_size):
        table_style = TableStyle([
            ('FONT', (0, 0), (-1, -1), font_name, font_size),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            # ('VALIGN', (5, 0), (5, -1), 'MIDDLE')
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


class SPCTitle(SPCItem):
    def __init__(self, company, caption, doc_type):
        self.__company = company
        self.__caption = caption.replace('\n', '<br/>')
        self.__doc_type = doc_type.replace('\n', '<br/>')

    @property
    def company(self):
        return self.__company

    @property
    def caption(self):
        return self.__caption

    @property
    def document_type(self):
        return self.__doc_type

    def replace_special(self):
        pass


class SPCParagraph(SPCItem):
    def __init__(self, text, on_replace):
        super().__init__(on_replace=on_replace)
        self.__text = text
        self.__indent = 15 * mm

    @property
    def indent(self):
        return self.__indent

    @indent.setter
    def indent(self, value):
        self.__indent = value

    def replace_special(self):
        self.__text = self.find_and_replace(self.__text)

    @property
    def text(self):
        return self.__text

    def build(self, font_name, font_size):
        result = self.find_special(self.__text)
        if len(result):
            return result
        style = ParagraphStyle(name="text", fontName=font_name, fontSize=font_size, firstLineIndent=self.__indent)
        return [reportlab.platypus.Paragraph(self.__text, style=style)]


class SPCChapter(SPCItem):
    def __init__(self, level, text, alignment=TA_CENTER):
        self.__level = level
        self.__text = text
        self.__align = alignment
        self.__indent = 0

    @property
    def indent(self):
        return self.__indent

    @indent.setter
    def indent(self, value):
        self.__indent = value

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        self.__text = value

    def build(self, font_name, font_size):
        style = ParagraphStyle(name=f'Heading{self.__level}', fontName=font_name, fontSize=font_size,
                               spaceBefore=5 * mm,
                               spaceAfter=5 * mm,
                               alignment=self.__align,
                               leftIndent=self.__indent
                               )
        bn = sha1(self.__text.encode()).hexdigest()
        item = Paragraph(f'<b>{self.__text}</b><a name="{bn}"/>', style=style)
        item._bookmarkName = bn
        return [item]


class SPCTableOfContent(SPCItem):
    def __init__(self, title):
        self.__title = title

    def replace_special(self):
        pass

    def build(self, font_name, font_size):
        style = ParagraphStyle(name='toc', fontName=font_name, fontSize=font_size, alignment=TA_CENTER)
        p = Paragraph(self.__title, style=style)
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(fontName=font_name, fontSize=font_size, name='Heading1')
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
    size: int
    fonts: List[Font]


class Config(BaseModel):
    standard: Literal['g105', 'g105_no_border', 'simple']
    output: str
    font: FontFamily
    table_of_content: Optional[str] = ''


class Markdown(BaseModel):
    name: str


class Item(BaseModel):
    type: Literal['image', 'markdown']
    name: str


class TitleApprove(BaseModel):
    name: str
    job_name: str


class Title(BaseModel):
    caption: str
    company: str
    doc_type: str
    approve: Union[TitleApprove, str]
    agrees: List[TitleApprove]


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
        self.__font_size = 12

        self.__params = {
            'tables': {},
            'images': {}
        }

    @property
    def font_name(self):
        return self.__font_name

    def set_font(self, font_name):
        self.__font_name = font_name

    def set_font_size(self, size):
        self.__font_size = size

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
                self.canv.addOutlineEntry(text, bn, level)
            else:
                self.notify('TOCEntry', (level, text, self.page))

    @abstractmethod
    def check(self, item):
        pass

    @property
    def items(self):
        return self.__items

    def append(self, item):
        if self.check(item):
            if isinstance(item, SPCTable):
                self.__params['tables'][item.label] = item.table_index
            self.__items.append(item)

    def on_replace(self, label):
        variants = ['images', 'tables']
        for var in variants:
            if label in self.__params[var]:
                return self.__params[var][label]
        return None

    def save(self):
        for item in self.__items:
            self.__flowable += item.build(self.__font_name, self.__font_size)
        self.multiBuild(self.__flowable)
