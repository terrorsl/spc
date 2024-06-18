from typing import List, Literal

import mistletoe
import reportlab.platypus
import yaml

from spc.standard.doc import SPC, SCPImage, SPCParagraph, SPCChapter, SPCList
from spc.standard.simple import SimpleDoc, SimpleTitle


class SimplePDFCreate:
    def __init__(self):
        pass

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            spc = SPC(**data['spc'])
            fonts = {}
            font_family = {spc.config.font.family: {}}
            for item in spc.config.font.fonts:
                fonts[item.name] = item.filename
                font_family[spc.config.font.family][item.type] = item.name
            doc = self.create_document(spc.config.output, fonts, font_family, spc.config.standard)
            doc.set_font(spc.config.font.family)

            if spc.config.standard == 'simple':
                doc.append(SimpleTitle(spc.title.caption))

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
        return SPCParagraph(text)

    def __load_list(self, parent: mistletoe.block_token.List):
        result = SPCList(parent.start)
        for child in parent.children:
            child: mistletoe.block_token.ListItem
            for item in child.children:
                if isinstance(item, mistletoe.block_token.Paragraph):
                    result.append(self.__load_paragraph(item))
                elif isinstance(item, mistletoe.block_token.List):
                    result.append(self.__load_list(item))
        return result

    def __load_markdown(self, filename):
        items = []
        with open(filename, 'r', encoding='utf-8') as file:
            md_doc = mistletoe.Document(file)
            for child in md_doc.children:
                if isinstance(child, mistletoe.block_token.Paragraph):
                    result = self.__load_paragraph(child)
                    items.append(result)
                elif isinstance(child, mistletoe.block_token.Heading):
                    child: mistletoe.block_token.Heading
                    items.append(SPCChapter(child.level, child.children[0].content))
                elif isinstance(child, mistletoe.block_token.List):
                    result = self.__load_list(child)
                    items.append(result)
                else:
                    raise Exception(child)
        return items

    def save(self):
        pass

    def create_document(self, filename, font, font_family, standard: Literal['simple', 'g105'] = 'simple'):
        standards = {
            # 'g105': G105Doc,
            'simple': SimpleDoc
        }
        # return standards[standard](filename, font, True)
        return standards[standard](filename, font, font_family, False)
