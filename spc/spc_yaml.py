from typing import List, Optional, Union, Literal

from pydantic import BaseModel, Field


class Font(BaseModel):
    name: str
    filename: str
    type: Literal['normal', 'bold', 'italic']


class FontFamily(BaseModel):
    family: str
    size: int
    fonts: List[Font]


class Config(BaseModel):
    standard: Literal['g105', 'g105_no_border', 'simple', 'g19']
    output: str
    font: FontFamily
    table_of_content: Optional[str] = ''


class Item(BaseModel):
    type: Literal['image', 'markdown', 'table']
    name: str


class Appendix(Item):
    caption: str


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
    pass


class SPC(BaseModel):
    config: Config = Field()
    title: Title
    # custom_title: str
    items: List[Item]
    appendixes: Optional[List[Appendix]] = []