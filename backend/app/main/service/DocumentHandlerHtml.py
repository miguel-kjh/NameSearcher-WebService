from app.main.service.DocumentHandler import DocumentHandler
from app.main.util.fileUtils import markInHtml,encode
from app.main.service.languageBuilder import LanguageBuilder
from app.main.util.heuristicMeasures import MEASURE_TO_COLUMN_KEY_REFERS_TO_NAMES,MEASURE_FOR_TEXTS_WITHOUT_CONTEXTS
from app.main.util.semanticWordLists import listOfVectorWords
from app.main.util.dataPickerInTables import DataPickerInTables

import re
import pandas as pd
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from enum import Enum,unique
from typing import Text

@unique
class TableToken(Enum):
        NONE = 0
        HEAD = 1
        ROW = 2

class TokenHtml:
        def __init__(self,listOfText:list,isTable:TableToken):
            self.text = listOfText
            self.isTable = isTable

class TokenizerHtml:
    def __init__(self, soup:BeautifulSoup):
        self.soup = soup
        self.blacklist = ['[document]', 'noscript', 'header','style',
                     'html', 'meta', 'head', 'input', 'script', 'link', 
                     'lang', 'code','th', 'td']

    def getToken(self) -> TokenHtml:
        def giveParentName(label) -> str:
            auxLable = label
            while auxLable.parent.name != '[document]':
                if auxLable.parent.name in ['th','td']:
                    return auxLable.parent.name
                auxLable = auxLable.parent
            return label.parent.name
        
        labelList  = list(filter(lambda label: label and label != "\n", self.soup.find_all(text=True)))
        tags       = list(map(lambda label: giveParentName(label),labelList))
        #print(tags)
        headList   = []
        rowList    = []
        lenHead    = 0
        for index,htmlLabel in enumerate(zip(labelList,tags)):
            label,tag = htmlLabel
            if tag not in self.blacklist:
                lenHead = 0
                headList.clear()
                rowList.clear()
                yield TokenHtml([str(label)],TableToken.NONE)

            elif tag == 'th':
                headList.append(str(label))
                lenHead = len(headList)
                try:
                    if tags[index+1] == 'th':
                        continue
                    aux = headList[:]
                    headList.clear()
                    yield TokenHtml(aux,TableToken.HEAD)
                except IndexError:
                    aux = headList[:]
                    headList.clear()
                    yield TokenHtml(aux,TableToken.HEAD)

            elif tag == 'td':
                rowList.append(str(label))
                try:
                    if tags[index+1] == 'td' and len(rowList) < lenHead:
                        continue
                    aux = rowList[:]
                    rowList.clear()
                    yield TokenHtml(aux,TableToken.ROW)
                except IndexError:
                    aux = rowList[:]
                    rowList.clear()
                    yield TokenHtml(aux,TableToken.ROW)

class DocumentHandlerHtml(DocumentHandler):

    def __init__(self, path: Text, destiny: str = "", isUrl:bool = False):
        super().__init__(path, destiny=destiny)
        if not isUrl:
            with open(self.path, "r", encoding="utf8") as f:
                self.soup = BeautifulSoup(f.read(), "lxml")
        else:
            self.soup = BeautifulSoup(path, "lxml")

    def locateNames(self, sentence):
        newSentence = ''
        index = 0
        for name in re.finditer(self.regexName,sentence):
            newSentence += sentence[index:name.start()] + markInHtml(name.group())
            index = name.end()
        if index <= len(sentence) - 1:
            newSentence += sentence[index:]

        return newSentence

    def encodeNames(self, sentence):
        newSentence = ""
        index = 0
        for name in re.finditer(self.regexName,sentence):
            newSentence += sentence[index:name.start()] + encode(name.group())
            index = name.end()
        if index <= len(sentence) - 1:
            newSentence += sentence[index:]
        
        return newSentence

    def documentsProcessing(self):
        formatter = HTMLFormatter(self.encodeNames)
        listNames,idCards = self.giveListNames()
        listNames = list(set(listNames))
        listNames.sort(
                key=lambda value: len(value),
                reverse=True
            )
        data = []
        data[len(data):] = listNames
        data[len(data):] = idCards
        self.regexName = "|".join(data)
        with open(self.destiny, "w") as f:
            f.write(self.soup.prettify(formatter=formatter))
    
    def documentTagger(self):
        formatter = HTMLFormatter(self.locateNames)
        listNames,idCards = self.giveListNames()
        listNames = list(set(listNames))
        listNames.sort(
                key=lambda value: len(value),
                reverse=True
            )
        data = []
        data[len(data):] = listNames
        data[len(data):] = idCards
        self.regexName = "|".join(data)
        with open(self.destiny, "w") as f:
            f.write(self.soup.prettify(formatter=formatter))

    def giveListNames(self) -> tuple:
        def cleanPicker():
            if not picker.isEmpty():
                listNames[len(listNames):] = picker.getAllNames(self.dataSearch.checkNamesInDB,MEASURE_FOR_TEXTS_WITHOUT_CONTEXTS)
                picker.clear()

        listNames = []
        idCards = []
        picker = DataPickerInTables()
        tokenizer = TokenizerHtml(self.soup)
        for token in tokenizer.getToken():
            if token.isTable == TableToken.NONE:
                if LanguageBuilder().hasContex(token.text[0]):
                    names,cards = self.dataSearch.searchPersonalData(token.text[0])
                    listNames[len(listNames):] = [name['name'].replace("\n", "") for name in names]
                    idCards[len(idCards):]     = [card['name'] for card in cards]
                elif self.dataSearch.isName(token.text[0]):
                    listNames.append(token.text[0])
                cleanPicker()
            elif token.isTable == TableToken.HEAD:
                #print(token.text)
                cleanPicker()
                keys = list(filter(lambda text: list(
                        filter(lambda x:LanguageBuilder().semanticSimilarity(text,x) > MEASURE_TO_COLUMN_KEY_REFERS_TO_NAMES,
                        listOfVectorWords)), token.text))
                if keys:
                    #print(keys)
                    for key in keys:
                        picker.addIndexColumn(token.text.index(key))
            elif token.isTable == TableToken.ROW:
                #print(token.text)
                for index in picker.getIndexesColumn():
                    try:
                        picker.addName(index,token.text[index])
                    except IndexError:
                        continue
                for index,token in enumerate(token.text):
                    if not index in picker.getIndexesColumn() and self.dataSearch.isDni(token):
                        idCards.append(token)
        return listNames,idCards