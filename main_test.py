import unittest
from urllib3.exceptions import HTTPError
import main as testpgm

class testClassFile(unittest.TestCase):
    def test_get_xml_file_name(self):
        """Tests functioning of get_xml_file function"""
        if self.assertTrue(isinstance(testpgm.get_xml_file_name(),
                                      str)):
            pass
        elif self.assertRaises(FileNotFoundError):
            pass

    def test_get_zip_content(self):
        self.assertRaises(HTTPError,testpgm.get_zip_content,
                          'https://google.com/error')


        







    
