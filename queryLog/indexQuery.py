import os
import sys

#for indexing
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from queryLog import getSessionWithQuery


def main(argv):
  ischema = Schema(session=TEXT(stored=True, phrase=False))
  if not os.path.exists(argv[2]):
    os.mkdir(argv[2])
  qindex = create_in(argv[2], schema=ischema, indexname=argv[2])
  writer = qindex.writer()

  i = 0
  for sess in getSessionWithQuery(argv[1], 1500):
    #print sess
    string = ' '.join(sess)
    try:
      writer.add_document(session=unicode(string.decode(
          'unicode_escape').encode('ascii', 'ignore')))
    except Exception as err:
      print sess, 'problem in indexing'
      print err, err.args
    i += 1
    if i % 100000 == 0:
      print i

  writer.commit()
  qindex.close()


if __name__ == '__main__':
  main(sys.argv)
