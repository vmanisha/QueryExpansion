import os
import sys
from lxml import etree
from queryLog import normalizeWithStopWordRemoval

import unittest

# Since the data is just question and best answer it should not be very big.
# Hence storing all the data in dictionary.
ANSWER = 'answer'
QUESTION = 'question'


class YahooQuestionsParser(object):

  def __init__(self):
    self.questions = {}
    self.is_question = self.is_subject = self.is_best_answer = False
    self.curr_question = None
    self.curr_clean_question = None

  def start(self, tag, attrib):
    if tag == 'document':
      self.is_question = True
    if tag == 'subject':
      self.is_subject = True
    if tag == 'bestanswer':
      self.is_best_answer = True

  def end(self, tag):
    if tag == 'document':
      self.is_question = False
      self.curr_question = None
      self.curr_clean_question = None
      if len(self.questions) % 50000 == 0:
        print 'Parsed ', len(self.questions), 'questions.'

    if tag == 'subject':
      self.is_subject = False

    if tag == 'bestanswer':
      self.is_best_answer = False
    pass

  def data(self, data):
    data = data.lower().strip()
    if self.is_question:
      # A new question.
      if self.is_subject:
        clean_question = normalizeWithStopWordRemoval(data)
        if len(clean_question) > 3:
          # Dint find the question.
          if clean_question not in self.questions:
            self.questions[clean_question
                          ] = {ANSWER: set([]),
                               QUESTION: set([data])}
          # Found the question.
          if data not in self.questions[clean_question][QUESTION]:
            self.questions[clean_question][QUESTION].add(data)

          self.curr_clean_question = clean_question
          self.curr_question = data

      # Answer for current question.
      if self.is_best_answer:
        clean_answer = normalizeWithStopWordRemoval(data)
        if (self.curr_clean_question in self.questions
           ) and (clean_answer not in
                  self.questions[self.curr_clean_question][ANSWER]):
          self.questions[self.curr_clean_question][ANSWER].add(clean_answer)

  def close(self):
    return self.questions


def main(argv):
  # Instantiate the parser.
  parser = etree.XMLParser(target=YahooQuestionsParser())
  questions = etree.parse(argv[1], parser)
  print 'Number of questions  ', len(questions)


if __name__ == '__main__':
  main(sys.argv)
