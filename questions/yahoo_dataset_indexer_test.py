"""Tests for yahoo_dataset_indexer."""

import yahoo_dataset_indexer
import unittest
from Whoosh import loadIndex, loadCollector, loadQueryParser
from whoosh.fields import Schema, TEXT
import os
from whoosh.analysis import StemmingAnalyzer


class YahooDatasetIndexerTest(unittest.TestCase):

  def test_create_index(self):
    stem_analyzer = StemmingAnalyzer()
    test_folder_to_index = 'test-folder'
    test_index_name = 'test-index'
    if not os.path.exists(test_folder_to_index):
      os.mkdir(test_folder_to_index)

    # Index 1 question.
    ofile = open(test_folder_to_index + '/question_indexer_test.xml', 'w')
    ofile.write(
        '<document><uri>432470</uri> <subject>Why are yawns contagious?</subject>\
    <content> When people yawn, you see that other people in the room yawn, too. Why is that?</content>\
    <bestanswer>When your body </bestanswer></document>')
    ofile.close()

    yahoo_dataset_indexer.IndexYahooQuestionsWithWhoosh(test_folder_to_index,
                                                        test_index_name)
    questions_index, questions_searcher = loadIndex(test_index_name,
                                                    test_index_name)
    # Check the schema.
    expected_schema = Schema(question_tokens=TEXT(analyzer=stem_analyzer,
                                      stored=False,
                                      phrase=False),
                        question_text=TEXT(analyzer=stem_analyzer,
                                      stored=True,
                                      phrase=False),
                        answers=TEXT(analyzer=stem_analyzer,
                                     stored=False,
                                     phrase=False))
    self.assertEqual(expected_schema, questions_index.schema)
    # Check the number of documents.
    self.assertEqual(1, questions_index.doc_count())
    # Check the number of terms in question and answer fields.
    expected_question_terms = ['contagi', 'yawn']
    i = 0
    for question_terms_tuple in questions_index.reader().iter_field('question_tokens'):
      self.assertEqual(question_terms_tuple[0], expected_question_terms[i])
      i += 1
    expected_answer_terms = ['bodi']
    i = 0
    for answer_terms_tuple in questions_index.reader().iter_field('answers'):
      self.assertEqual(answer_terms_tuple[0], expected_answer_terms[i])
      i += 1

  def test_search_index(self):
    pass


if __name__ == '__main__':
  unittest.main()
