from spc.standard.doc import SPCDocument, SPCTitle


class G732Title(SPCTitle):
    def build(self, font_name, font_size):
        result = []
        return result


class G732Doc(SPCDocument):
    def check(self, item):
        pass
