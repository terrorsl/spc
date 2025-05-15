# Simple PDF Create

Позволяет облегчить процесс создания докуметов, отчетов в формате PDF.

состоит из двух частей:
1. библиотека для python, позволяет встроить в свое приложение
2. исполняемого файла

Как использовать:
создайте сценарий в формате YAML

Пример файла сценария
``` yaml
spc:
  config:
    standard: "simple"
    output: "test.pdf"
    font:
      family: "Times New Roman"
      fonts: [
        {name: "Times New Roman", filename: "Times New Roman.ttf", type: "normal"},
        {name: "Times New Roman Bold", filename: "Times New Roman Bold.ttf", type: "bold"},
        {name: "Times New Roman Italic", filename: "Times New Roman Italic.ttf", type: "italic"},
      ]
    font_size: 12
    table_of_content: "Содержание"
  title:
    company: ""
    caption: "Система прогнозирования Жизни Человека"
  items:
    - {type: "markdown", name: "test.md"}
    - {type: "image", name: "test.jpg"}
```
Запустите исполнител
```console
spd --filename test.yaml
```

``` python
from spc import SimplePDFCreate

spc = SimplePDFCreate()
doc = spc.load(args.filename)
doc.save()
```