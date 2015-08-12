import unittest
from lxml import etree
from yahoo_dataset_parser import YahooQuestionsParser
from queryLog import normalizeWithStopWordRemoval


class TestParser(unittest.TestCase):
  def setUp(self):
    self.parser = etree.XMLParser(target=YahooQuestionsParser());

  def test_empty_xml_parse(self):
    self.assertEqual(etree.parse('', self.parser), {});

  def test_parse_one_question(self):
    expected = {
        normalizeWithStopWordRemoval('Why are yawns contagious?'.lower()):
        [normalizeWithStopWordRemoval('body when'.lower())]
    }
    ofile = open('parser_test.xml','w');
    ofile.write('<document><uri>432470</uri> <subject>Why are yawns contagious?</subject>\
    <content> When people yawn, you see that other people in the room yawn, too. Why is that?</content>\
    <bestanswer>When your body </bestanswer></document>');
    ofile.close();
    self.assertDictEqual(etree.parse('parser_test.xml',  self.parser), expected)

  def test_parse_multiple_questions(self):
    expected = {
        normalizeWithStopWordRemoval('Why are yawns contagious?'.lower()):
        [normalizeWithStopWordRemoval('body when'.lower())],
        normalizeWithStopWordRemoval('What\'s the best way to heat up a cold hamburger '.lower()):
        [normalizeWithStopWordRemoval('If you must eat a heated In & Out hamburger'.lower())]
    }
    ofile = open('parser_test.xml','w');
    ofile.write('<document><uri>432470</uri><subject>Why are yawns contagious?</subject>\
                                 <content> When people yawn, you see that other people in the room yawn, too. Why is that?</content>\
                                 <bestanswer>When your body </bestanswer></document><vespaadd><document type="wisdom"><uri>800062</uri>\
                                 <subject> What\'s the best way to heat up a cold hamburger (In & Out)?</subject>\
                                 <content> What\'s the best way to heat up a cold hamburger (In & Out)? </content>\
                                 <bestanswer> If you must eat a heated In & Out hamburger then</bestanswer></vespaadd></document>');
    ofile.close();


if __name__ == '__main__':
  unittest.main()
