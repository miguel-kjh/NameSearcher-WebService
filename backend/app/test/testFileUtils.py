from app.test.base import BaseTestCase
from app.main.util.fileUtils import *

import unittest

class TestFileUtils(BaseTestCase):

    def test_allowedFile(self):
        self.assertFalse(allowedFile("ddd"))
        self.assertFalse(allowedFile(""))
        self.assertFalse(allowedFile(4))
        self.assertFalse(allowedFile("3327"))
        self.assertTrue(allowedFile(".txt"))
        self.assertFalse(allowedFile("fichero.rar"))
        self.assertTrue(allowedFile("fichero.docx"))
        self.assertTrue(allowedFile("fichero.pdf"))
        self.assertTrue(allowedFile("fichero.csv"))

    def test_giveTypeOfFile(self):
        self.assertEquals(giveTypeOfFile(""), False)
        self.assertEquals(giveTypeOfFile("."), '')
        self.assertEquals(giveTypeOfFile("ddd.txt"), "txt")
        self.assertEquals(giveTypeOfFile("ddd.txt.pdf"), "pdf")
        self.assertEquals(giveTypeOfFile("ddd.txt."), '')
        self.assertEquals(giveTypeOfFile(33), False)
        self.assertEquals(giveTypeOfFile(None), False)

    def test_readPdf(self):
        pathTexts  = 'app/test/data/textos/carta'
        self.assertTrue(len(list(readPdf(pathTexts + "1.pdf"))) > 0)
        self.assertEquals(list(readPdf(pathTexts)), [])
        self.assertEquals(list(readPdf(pathTexts + "1.txt")), [])

    def test_normalizeUnicode(self):
        self.assertEquals(normalizeUnicode("miguel"),"miguel")
        self.assertEquals(normalizeUnicode("ÁNgel"), "ANgel")
        self.assertEquals(normalizeUnicode("dèndsëSD/ñ"), "dendseSD/ñ")
        self.assertEquals(normalizeUnicode("ñ"), "ñ")
        self.assertEquals(normalizeUnicode("ñdddd"), "ñdddd")
        self.assertEquals(normalizeUnicode("dèñdsëSD/ñ"), "deñdseSD/ñ")
        self.assertEquals(normalizeUnicode("ñ"*5), "ñ"*5)
        self.assertEquals(normalizeUnicode(""), "")


if __name__ == '__main__':
    unittest.main()