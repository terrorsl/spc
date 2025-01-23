from typing import List, Optional, Union, Literal

from pydantic import BaseModel, Field, validator, root_validator


class Font(BaseModel):
    name: str
    filename: str
    type: Literal['normal', 'bold', 'italic']


class FontFamily(BaseModel):
    family: str
    size: int
    fonts: List[Font]


class Config(BaseModel):
    standard: Literal['g2', 'g2_no_border', 'simple', 'g19']
    output: str
    font: FontFamily
    table_of_content: Optional[str] = ''


class Item(BaseModel):
    type: Literal['image', 'markdown', 'table', 'specification']
    name: str
    caption: Optional[str]
    ref: Optional[str]

    @root_validator
    def check_type(cls, values):
        if values['type'] == 'image':
            if not values['caption'] or not values['ref']:
                raise ValueError('"caption" and "ref" must be provided')
        elif values['type'] == 'table':
            if not values['ref']:
                raise ValueError('"ref" must be provided')
        return values


class Appendix(BaseModel):
    caption: str
    type: Literal['обязательное', 'справочное', 'рекомендуемое']
    items: List[Item]


class TitleApprove(BaseModel):
    name: str
    job_name: str


class Title(BaseModel):
    caption: str = Field(description="caption")
    company: str = Field(description="company name")
    doc_type: str
    approve: Union[TitleApprove, str] = Field(description="approve person or document")
    agrees: List[TitleApprove]


class ApprovalSheet(BaseModel):
    company: str
    caption: str
    doc_type: str
    approve: TitleApprove
    agrees: List[TitleApprove]


class SPC(BaseModel):
    config: Config = Field()
    title: Title
    # custom_title: str
    items: List[Item]
    appendixes: Optional[List[Appendix]] = []
