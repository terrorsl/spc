import json
from pathlib import Path
from typing import Literal

import mistletoe
import yaml

from pydantic_yaml import parse_yaml_raw_as, to_yaml_str
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration

from spc.spc_yaml import SPC, SPCMain
from spc.standard.doc import SPCParagraph, SPCChapter, SPCList, SPCTable, SPCAppendix, \
    SPCPagebreak, SPCImage
from spc.standard.g105 import G105Doc
from spc.standard.g105_no_border import G105NoBorderDoc, G105Chapter, G105Table, G105Title, G105List, G105Image
from spc.standard.g19 import G19, G19Chapter, G19Title, G19List, G19Image, G19Specification
from spc.standard.simple import SimpleDoc, SimpleTitle


class SimplePDFCreate:
    def __init__(self):
        self.__standard = ''
        self.__chapter_count = 0
        self.__table_count = 0
        self.__image_count = 0
        self.__doc = None
        self.__path = '.'

        self.standards = {
            'g19': {
                'doc': G19,
                'title': G19Title,
                'chapter': G19Chapter,
                'image': G19Image,
                'table': G105Table
            },
            'g2': {
                'doc': G105Doc,
                'title': G105Title,
                'chapter': G105Chapter,
                'image': G105Image,
                'table': G105Table
            },
            'g2_no_border': {
                'doc': G105NoBorderDoc,
                'title': G105Title,
                'chapter': G105Chapter,
                'image': G105Image,
                'table': G105Table
            },
            'simple': {
                'doc': SimpleDoc,
                'title': SimpleTitle,
            }
        }

    def print_scheme(self):
        with open('schema.json', 'w') as file:
            file.write(SPCMain.schema_json(indent=4))
        # config = GenerationConfiguration()
        generate_from_filename('schema.json', 'html/schema.html')
        # print(SPC.schema_json())

    def load(self, filename):
        print(f'open project {filename}')
        with open(filename, 'r', encoding='utf-8') as file:
            path = Path(filename)
            self.__path = path.parent
            data = yaml.safe_load(file)
            print(f'process')
            spc = SPC(**data['spc'])
            fonts = {}
            font_family = {spc.config.font.family: {}}
            for item in spc.config.font.fonts:
                fonts[item.name] = f'{path.parent}/{item.filename}'
                font_family[spc.config.font.family][item.type] = item.name
            self.__standard = spc.config.standard

            print(f'create document')
            doc = self.create_document(f'{self.__path}/{spc.config.output}', fonts, font_family, spc.config.standard)
            doc.set_font(spc.config.font.family)
            doc.set_font_size(spc.config.font.size)
            self.__doc = doc

            title = self.standards[self.__standard]['title']
            if spc.config.standard == 'simple':
                doc.append(title(spc.title.caption))
            elif spc.config.standard == 'g19':
                doc.append(title(spc.title.company, spc.title.caption,
                                 spc.title.doc_type, spc.title.approve))
            else:
                doc.append(title(spc.title.company, spc.title.caption,
                                 spc.title.doc_type, spc.title.approve, spc.title.agrees))

            if len(spc.config.table_of_content):
                doc.set_table_of_content(spc.config.table_of_content)

            print(f'process items')
            for item in spc.items:
                full_path = f'{self.__path}/{item.name}'
                if item.type == 'image':
                    image = self.standards[self.__standard]['image'](caption=item.caption, filename=full_path,
                                                                     reference=item.ref,
                                                                     image_index=self.__image_count+1)
                    self.__image_count += 1
                    doc.append(image)
                elif item.type == 'markdown':
                    _items = self.__load_markdown(full_path)
                    for _item in _items:
                        doc.append(_item)
                elif item.type == 'table':
                    doc.append(self.__load_json_table(full_path))
                elif item.type == 'specification':
                    _items= self.__load_specification(full_path)
                    for _item in _items:
                        doc.append(_item)
                else:
                    raise Exception(f'unknown type {item.type}')

            doc.append(SPCPagebreak())

            print(f'process appendixes')
            for index, item in enumerate(spc.appendixes):
                appendix_name = ''
                self.__table_count = 0
                if self.__standard == 'simple':
                    doc.append(SPCAppendix(appendix_name, item.caption, 'справочное'))
                else:
                    letters = 'АБВГДЕЖИКЛМНПРСТУФХЦШЩЭЮЯ'
                    if index > len(letters):
                        appendix_name = index - len(letters)
                    else:
                        appendix_name = letters[index]
                    name = f'Приложение {appendix_name}'
                    doc.append(SPCAppendix(name, item.caption, item.type))
                for app_item in item.items:
                    if app_item.type == 'image':
                        doc.append(SPCImage(caption='', filename=app_item.name, reference='', image_index=0))
                    elif app_item.type == 'markdown':
                        _items = self.__load_markdown(f'{self.__path}/{app_item.name}')
                        for _item in _items:
                            if self.__standard != 'simple':
                                if isinstance(_item, SPCChapter):
                                    _item.text = f'{appendix_name}.{_item.text}'
                                elif isinstance(_item, G105Table):
                                    _item.table_index = f'{appendix_name}.{_item.table_index}'
                            doc.append(_item)
                    elif app_item.type == 'table':
                        table = self.__load_json_table(app_item.name)
                        table.table_index = f'{appendix_name}.{table.table_index}'
                        doc.append(table)
                doc.append(SPCPagebreak())
            return doc

    def __load_json_table(self, filename):
        with open(filename, 'r') as fp:
            json_data = json.load(fp)
            header = json_data['header']
            formats = json_data['formats']
            columns = json_data['columns']
            if len(formats) != len(columns):
                if isinstance(columns[0], list):
                    for column in columns:
                        if len(formats) != len(column):
                            raise Exception(f'formats and columns{column} must be same size!')
                else:
                    raise Exception(f'formats and columns must be same size!')
            table = self.standards[self.__standard]['table'](None, formats, self.__table_count+1)
            self.__table_count += 1
            table.set_caption(header)
            for span in json_data['span']:
                start = span['start']
                end = span['end']
                table.append_span(start, end)
            for column in columns:
                if isinstance(column, list):
                    table.append(column)
                else:
                    table.append(column)
            for row in json_data['data']:
                table.append(row)
            return table

    def __load_paragraph(self, parent: mistletoe.block_token.Paragraph):
        text = ''
        result = []
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
            elif isinstance(child, mistletoe.span_token.Image):
                result.append(SPCParagraph(text, self.__doc.on_replace))
                text = ''
                reference = child.children[0].content if len(child.children) else '_'
                image = self.standards[self.__standard]['image'](child.title, f'{self.__path}/{child.src}',
                                                                 reference, self.__image_count+1)
                self.__image_count += 1
                result.append(image)
            else:
                raise Exception(child)
        result.append(SPCParagraph(text, self.__doc.on_replace))
        return result

    def __load_list(self, parent: mistletoe.block_token.List, sub_list=0):
        if self.__standard == 'simple':
            result = SPCList(parent.start)
        elif self.__standard == 'g19':
            result = G19List(parent.start, self.__doc.on_replace)
        else:
            result = G105List(parent.start, sub_list)
        for child in parent.children:
            child: mistletoe.block_token.ListItem
            for item in child.children:
                if isinstance(item, mistletoe.block_token.Paragraph):
                    for pi in self.__load_paragraph(item):
                        result.append(pi)
                elif isinstance(item, mistletoe.block_token.List):
                    result.append(self.__load_list(item, sub_list + 1))
        return result

    def __load_table(self, parent: mistletoe.block_token.Table, is_specification=False):
        header = [h.children[0].content for h in parent.header.children]
        columns = ['str' for _i in parent.header.children]
        if self.__standard == 'simple':
            table = SPCTable(header, self.__table_count+1, columns)
        else:
            if is_specification:
                table = G19Specification()
            else:
                table = G105Table(header, columns, self.__table_count+1)
        self.__table_count = self.__table_count + 1
        for row in parent.children:
            items = [v.children[0].content if len(v.children) else '' for v in row.children]
            table.append(items)
        return table

    def __load_specification(self, filename):
        items = []
        with open(filename, 'r', encoding='utf-8') as file:
            md_doc = mistletoe.Document(file)
            for child in md_doc.children:
                if isinstance(child, mistletoe.block_token.Table):
                    table = self.__load_table(child, True)
                    items.append(table)
                print(child)
        return items

    def __load_markdown(self, filename):
        items = []
        chapters = {}
        table = None
        with open(filename, 'r', encoding='utf-8') as file:
            md_doc = mistletoe.Document(file)
            for child in md_doc.children:
                if isinstance(child, mistletoe.block_token.Paragraph):
                    result = self.__load_paragraph(child)
                    if table:
                        if len(result[0].text) and result[0].text[0] == ':':
                            table.set_caption(result[0].text[1:])
                            del result[0]
                            table = None
                    if len(result):
                        items += result
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
                            else:
                                index += f'.{item}'

                        chapter = self.standards[self.__standard]['chapter'](child.level,
                                                                             child.children[0].content, index)
                        items.append(chapter)
                elif isinstance(child, mistletoe.block_token.List):
                    result = self.__load_list(child)
                    items.append(result)
                elif isinstance(child, mistletoe.block_token.Table):
                    table = self.__load_table(child)
                    items.append(table)
                else:
                    raise Exception(child)
        return items

    def create_document(self, filename, font, font_family,
                        standard: Literal['simple', 'g2', 'g2_no_border', 'g19'] = 'simple'):
        return self.standards[standard]['doc'](filename, font, font_family, False)
