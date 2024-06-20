from typing import List, Literal

import mistletoe
import reportlab.platypus
import yaml

from spc.standard.doc import SPC, SCPImage, SPCParagraph, SPCChapter, SPCList, SPCTable, SPCItem
from spc.standard.g105 import G105Doc
from spc.standard.g105_no_border import G105NoBorderDoc, G105Chapter, G105Table, G105Title, G105List
from spc.standard.simple import SimpleDoc, SimpleTitle


class SimplePDFCreate:
    def __init__(self):
        self.__standard = ''
        self.__chapter_count = 0
        self.__table_count = 0
        self.__doc = None

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            spc = SPC(**data['spc'])
            fonts = {}
            font_family = {spc.config.font.family: {}}
            for item in spc.config.font.fonts:
                fonts[item.name] = item.filename
                font_family[spc.config.font.family][item.type] = item.name
            self.__standard = spc.config.standard

            doc = self.create_document(spc.config.output, fonts, font_family, spc.config.standard)
            doc.set_font(spc.config.font.family)
            doc.set_font_size(spc.config.font.size)
            self.__doc = doc

            if spc.config.standard == 'simple':
                doc.append(SimpleTitle(spc.title.caption))
            else:
                doc.append(G105Title(spc.title.company, spc.title.caption,
                                     spc.title.doc_type, spc.title.approve, spc.title.agrees))

            if len(spc.config.table_of_content):
                doc.set_table_of_content(spc.config.table_of_content)

            for item in spc.items:
                if item.type == 'image':
                    doc.append(SCPImage(caption='', filename=item.name, reference=''))
                elif item.type == 'markdown':
                    _items = self.__load_markdown(item.name)
                    for _item in _items:
                        doc.append(_item)
            return doc

    def __load_paragraph(self, parent: mistletoe.block_token.Paragraph):
        text = ''
        for child in parent.children:
            if isinstance(child, mistletoe.span_token.RawText):
                item: mistletoe.span_token.RawText
                text += child.content
            elif isinstance(child, mistletoe.span_token.LineBreak):
                child: mistletoe.span_token.LineBreak
                if not child.soft:
                    text += '<br/>'
                else:
                    text += ' '
            elif isinstance(child, mistletoe.span_token.Strong):
                child: mistletoe.span_token.Strong
                text += f'<b>{child.children[0].content}</b>'
            elif isinstance(child, mistletoe.span_token.Emphasis):
                child: mistletoe.span_token.Emphasis
                text += '<i>'
                for item in child.children:
                    if isinstance(item, mistletoe.span_token.RawText):
                        text += item.content
                    elif isinstance(item, mistletoe.span_token.LineBreak):
                        if not item.soft:
                            text += '<br/>'
                        else:
                            text += ' '
                text += '</i>'
            else:
                raise Exception(child)
        return SPCParagraph(text, self.__doc.on_replace)

    def __load_list(self, parent: mistletoe.block_token.List, sub_list=0):
        if self.__standard == 'simple':
            result = SPCList(parent.start)
        else:
            result = G105List(parent.start, sub_list)
        for child in parent.children:
            child: mistletoe.block_token.ListItem
            for item in child.children:
                if isinstance(item, mistletoe.block_token.Paragraph):
                    result.append(self.__load_paragraph(item))
                elif isinstance(item, mistletoe.block_token.List):
                    result.append(self.__load_list(item, sub_list + 1))
        return result

    def __load_table(self, parent: mistletoe.block_token.Table):
        header = [h.children[0].content for h in parent.header.children]
        columns = ['str' for _i in parent.header.children]
        if self.__standard == 'simple':
            table = SPCTable(header, columns)
        else:
            table = G105Table(header, columns, self.__table_count+1)
        self.__table_count = self.__table_count + 1
        for row in parent.children:
            items = [v.children[0].content for v in row.children]
            table.append(items)
        return table

    def __load_markdown(self, filename):
        items = []
        chapters = {}
        table = None
        with open(filename, 'r', encoding='utf-8') as file:
            md_doc = mistletoe.Document(file)
            for child in md_doc.children:
                if isinstance(child, mistletoe.block_token.Paragraph):
                    result = self.__load_paragraph(child)
                    if table and result.text[0] == ':':
                        table.set_caption(result.text[1:])
                    else:
                        items.append(result)
                elif isinstance(child, mistletoe.block_token.Heading):
                    child: mistletoe.block_token.Heading
                    if self.__standard == 'simple':
                        items.append(SPCChapter(child.level, child.children[0].content))
                    else:
                        if child.level == 1:
                            if child.level not in chapters:
                                chapters[child.level] = 1
                            else:
                                v = chapters[child.level] + 1
                                chapters = {child.level: v}
                            self.__chapter_count += 1
                        else:
                            if child.level not in chapters:
                                chapters[child.level] = 1
                            else:
                                c = {}
                                for key in chapters.keys():
                                    if key <= child.level:
                                        c[key] = chapters[key]
                                chapters = c
                                chapters[child.level] = chapters[child.level] + 1
                        index = ''
                        for key, item in chapters.items():
                            if key == 1:
                                index += f'{item}'
                            elif key == 2:
                                index += f'.{item}.'
                            else:
                                index += f'{item}.'
                        items.append(G105Chapter(child.level, child.children[0].content, index))
                elif isinstance(child, mistletoe.block_token.List):
                    result = self.__load_list(child)
                    items.append(result)
                elif isinstance(child, mistletoe.block_token.Table):
                    table = self.__load_table(child)
                    items.append(table)
                else:
                    raise Exception(child)
        return items

    def save(self):
        pass

    def create_document(self, filename, font, font_family, standard: Literal['simple', 'g105', 'g105_no_border'] = 'simple'):
        standards = {
            'g105': G105Doc,
            'g105_no_border': G105NoBorderDoc,
            'simple': SimpleDoc
        }
        # return standards[standard](filename, font, True)
        return standards[standard](filename, font, font_family, False)
