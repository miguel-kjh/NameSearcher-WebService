from app.main.service.languageBuilder import LanguageBuilder
from app.main.util.heuristicMeasures  import ERROR_RANGE_PERCENTAGE_DB
from app.main.util.fileUtils          import isDni,normalizeUnicode,generateWordsAsString

from abc       import ABC, abstractmethod
from typing    import Text
from itertools import chain
from enum import Enum
import sqlite3 as lite
import re

class PersonalData(Enum):
    names = 1
    idCards = 2
    all = 3

class PersonalDataSearch(ABC):
    def __init__(self):
        self.keywords     = ["DE", "DEL", "EL", "LOS", "TODOS", "Y"]
        self.errorRange   = ERROR_RANGE_PERCENTAGE_DB
        self.connection   = SpanishNamesDB()
        self.regexIdCards = r'\d{2}([\.-]?|\s*)\d{2}([\.-]?|\s*)\d{2}([\.-]?|\s*)\d{2}\s*\w'

    def _convertName(self,name:str) -> list:
        """
        Normalizes and divides a name into words so that it can be 
        searched in the database of names and surnames.
        :param name: string
        :return: list of strings
        """

        normalizeName = normalizeUnicode(str(name)).upper()
        words = list(
            filter(
                lambda n: n not in self.keywords, normalizeName.replace('-', ' ').replace(',','').replace('\'','').split()
                )
            )
        return words

    def _checkNameInSubset(self,name:list, nameSubset:list) -> bool:
        """
        checks the match range of a name with a set of names.
        :param name: list of string
        :param nameSubset: list of string
        :return: boolean
        """

        if not name: return False
        namesFound = list(filter(lambda n: n in nameSubset, name))
        return len(namesFound)/len(name) >= self.errorRange


    def checkNamesInDB(self, names:list) -> list:
        """
        Checks if a list of names belongs to the database of names and surnames.
        It returns a list of names that if they meet the condition.
        :param names: list of string
        :return: list of string
        """
        
        listNames = list(map(lambda x: self._convertName(x), names))
        words     = list(chain.from_iterable(listNames))
        if not words: return []
        nameSubset = []
        
        for strName in generateWordsAsString(list(set(words))):
            try:
                sentence                     = "select distinct names from names where names in %s;" % (strName)
                senteceResult                = self.connection.query(sentence)
                nameSubset[len(nameSubset):] = [queryResult[0] for queryResult in senteceResult.fetchall()]
                sentence                     = "select distinct surnames from surnames where surnames in %s;" % (strName)
                senteceResult                = self.connection.query(sentence)
                nameSubset[len(nameSubset):] = [queryResult[0] for queryResult in senteceResult.fetchall()]
            except lite.OperationalError as identifier:
                print(identifier)

        finalNames = list(
            filter(
                lambda name: self._checkNameInSubset(name,nameSubset), listNames
            )
        )
        return [names[listNames.index(strName)] for strName in finalNames]

    def checkNameInDB(self, fullName: str) -> bool:
        """ 
        Find out if a name belongs in the database.
        :param fullName: string
        :return: boolean
        """

        countWordsInName = 0
        countWordsInDB   = 0
        normalizeName    = normalizeUnicode(fullName).upper()

        for name in normalizeName.replace('-', ' ').replace(',','').split():
            if name not in self.keywords:
                countWordsInName += 1
                try:
                    sentence = "select (select count(*) from surnames where surnames= '%s') OR" \
                    " (select count(*) from names  where names='%s');" % (name, name)
                    senteceResult   = self.connection.query(sentence)
                    countWordsInDB += 1 if senteceResult.fetchone()[0] == 1 else 0
                except lite.OperationalError as identifier:
                    print(identifier)

        return countWordsInName > 0 and countWordsInDB / countWordsInName > self.errorRange

    def isName(self, fullName: str) -> bool:
        """
        Check if a string is a name or not
        :param fullName: string
        :return: boolean
        """

        pattern = re.compile(r'\d')
        if pattern.search(fullName):
            return False
        
        return self.checkNameInDB(fullName)

    def giveIdCards(self, text: str) -> list:
        """
        Return the DNIs in a string.
        :param string: string
        :return: list of strings
        """

        match = map(
                lambda x: x.group(), re.finditer(self.regexIdCards,str(text))
            )
        return list(filter(lambda idCard: isDni(idCard), match))

    @abstractmethod
    def searchPersonalData(self, text: Text, personalData:PersonalData = PersonalData.all) -> tuple:
        pass


class SpanishNamesDB:

    def __init__(self):
        self.connection = lite.connect("spanish_names")
        self.cursor     = self.connection.cursor()

    def query(self, query: str):
        return self.cursor.execute(query)

    def __del__(self):
        self.cursor.close()
        self.connection.close()
