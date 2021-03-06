import os,sys
from yahoo_dataset_parser import YahooQuestionsParser, ANSWER, QUESTION
from lxml import etree

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.analysis import StemmingAnalyzer
from queryLog import getSessionWithQuery
from Whoosh import loadIndex, loadCollector, loadQueryParser


def IndexYahooQuestionsWithWhoosh(input_folder_name, output_folder_name):
  stem_analyzer = StemmingAnalyzer()

  index_schema = Schema(question_tokens=TEXT(analyzer=stem_analyzer,
                                      stored=False,
                                      phrase=False),
                        question_text=TEXT(analyzer=stem_analyzer,
                                      stored=True,
                                      phrase=False),
                        answers=TEXT(analyzer=stem_analyzer,
                                     stored=False,
                                     phrase=False))

  if not os.path.exists(output_folder_name):
    os.mkdir(output_folder_name)

  questions_index = create_in(output_folder_name,
                              schema=index_schema,
                              indexname=output_folder_name)
  index_writer = questions_index.writer()

  indexed_question_count = 0
  parser = etree.XMLParser(target=YahooQuestionsParser(),encoding = 'utf-8',recover = True );
  for ifile in os.listdir(input_folder_name):
    ifile = input_folder_name + '/' + ifile
    print 'Parsing ', ifile;
    for question_tokens, question_answer_dict  in etree.parse(ifile, parser).items():
      # Create a whoosh document.
      index_writer.add_document(question_tokens=unicode(question_tokens),
                                question_text = unicode('\t'.join(question_answer_dict[QUESTION])),
                                answers=unicode('\t'.join(question_answer_dict[ANSWER])))
      indexed_question_count += 1
      if indexed_question_count % 5000 == 0:
        print 'Indexed ', indexed_question_count
  try:
    index_writer.commit()
    questions_index.close()
  except Exception as err:
    print err


def SearchYahooQuestionsWithWhoosh(input_file, index_folder, index_name,
                                   questions_limit, output_file):
  # Open the index.
  questions_index, questions_searcher = loadIndex(index_folder, index_name)
  # Load the collector.
  questions_collector = loadCollector(questions_searcher, questions_limit, 20)
  # Search on question field for now.
  query_parser = loadQueryParser(questions_index, 'question_tokens')

  # Open the file to write the query and top questions_limit questions.
  out = open(output_file, 'w')

  for line in open(input_file, 'r'):
    query = line.strip()
    query_object = query_parser.parse(unicode(query))
    try:
      questions_searcher.search_with_collector(query_object,
                                               questions_collector)
    except TimeLimit:
      print 'ERROR: Very Long query as input.', query

    results = questions_collector.results()
    for document in results:
      question_list = document['question_text'].split('\t');
      for question in queston_list:
        out.write(query + '\t' + question + '\n')
  out.close()


def main(argv):
  IndexYahooQuestionsWithWhoosh(argv[1], argv[2])


if __name__ == '__main__':
  main(sys.argv)
