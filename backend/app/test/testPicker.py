from app.test.base import BaseTestCase
from app.main.util.dataPickerInTables import DataPickerInTables
from app.main.util.heuristicMeasures  import MAXIMUM_NUMBER_OF_POSSIBLE_NAMES_FOR_A_QUERY
from app.main.util.heuristicMeasures  import SAMPLE_DATA_TO_CHOOSE_NAMES


import unittest

class TestPicker(BaseTestCase):

    def test_add_getIndex(self):
        picker = DataPickerInTables()
        self.assertEquals(picker.getIndexesColumn(), [])
        picker.addIndexColumn(4)
        picker.addIndexColumn(3)
        self.assertEquals(picker.getIndexesColumn(), [4,3])
        picker.addIndexesColumn([2,5])
        self.assertEquals(picker.getIndexesColumn(), [4,3,2,5])
        picker.addIndexColumn(4)
        self.assertEquals(picker.getIndexesColumn(), [4,3,2,5])
        picker.addIndexesColumn([])
        self.assertEquals(picker.getIndexesColumn(), [4,3,2,5])
        picker.addIndexesColumn([1,4,3,5])
        self.assertEquals(picker.getIndexesColumn(), [4,3,2,5,1])
        picker.addName(1,"Eugenio")
        picker.addName(1,"Maria")
        self.assertEquals(picker.picker[1]['names'], ["Eugenio","Maria"])
        self.assertEquals(picker.isColumnName(3), True)
        self.assertEquals(picker.isColumnName(10), False)
        picker.clear()
        self.assertEquals(picker.isColumnName(10), False)

    def test_clear_empty(self):
        picker = DataPickerInTables()
        self.assertEquals(picker.isEmpty(), True)
        picker.clear()
        self.assertEquals(picker.isEmpty(), True)
        picker.addIndexColumn(4)
        picker.addIndexColumn(3)
        self.assertEquals(picker.isEmpty(), False)
        picker.clear()
        self.assertEquals(picker.isEmpty(), True)

    def test_names_method(self):
        picker = DataPickerInTables()
        picker.addIndexColumn(1)
        picker.addName(1,"Eugenio")
        picker.addName(1,"Maria")
        self.assertEqual(picker._getNamesSample(1), ['Eugenio', 'Maria'])
        for _ in range(MAXIMUM_NUMBER_OF_POSSIBLE_NAMES_FOR_A_QUERY):
            picker.addName(1,"Miguel")
        self.assertEqual(len(picker._getNamesSample(1)), round(len(picker.picker[1]['names'])*SAMPLE_DATA_TO_CHOOSE_NAMES))


if __name__ == '__main__':
    unittest.main()