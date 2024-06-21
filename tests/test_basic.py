import unittest

from spc.core import SimplePDFCreate
from spc.standard.doc import SPCTable
from spc.standard.simple import SimpleTitle


class MyTestCase(unittest.TestCase):
    # def test_create(self):
    #     spc = SimplePDFCreate()
    #     font = {'Times New Roman': 'Times New Roman.ttf'}
    #     doc = spc.create_document('test.pdf', font)
    #
    #     doc.set_font('Times New Roman')
    #
    #     title = SimpleTitle()
    #     doc.append(title)
    #
    #     doc.save()
    #     # self.assertEqual(True, False)  # add assertion here

    def test_load(self):
        spc = SimplePDFCreate()
        spc.print_scheme()
        # doc = spc.load('test.yaml')
        # doc.append(SPCTable())
        # doc = spc.load('ИМЕС.00300-04 51-XX.yaml')
        doc = spc.load('ИМЕС.00300-04 51-03.yaml')
        doc.save()
        # font = {'Times New Roman': 'Times New Roman.ttf'}
        # doc = spc.create_document('test.pdf', font)
        #
        # doc.set_font('Times New Roman')
        #
        # doc.load('test.yaml')


if __name__ == '__main__':
    unittest.main()
