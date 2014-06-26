import os
import sys
import re
from tools import SYMB
#for indexing
from whoosh.index import create_in
from whoosh.fields import Schema, KEYWORD




def main(argv):
        ischema = Schema(title = KEYWORD, content = KEYWORD(stored=True))
        if not os.path.exists(argv[2]):
                os.mkdir(argv[2])
        index = create_in(argv[2],schema=ischema, indexname =argv[3])
        writer = index.writer()

	RSTR = '/resource'
	i=0
	for line in open(argv[1],'r'):
		split = line.strip().lower().split('>')
		tit = split[0][split[0].rfind(RSTR)+9:].replace('_',' ')
		abstract = split[-1][split[-1].find('"')+1:split[-1].rfind('"')]
		abstract = abstract.decode('unicode_escape').encode('ascii','ignore')
		abstract = re.sub(SYMB,' ',abstract)
		abstract = re.sub('\s+',' ',abstract)
		try :
			if len(tit) > 3 and len(abstract) >3:
				writer.add_document(title=unicode(tit) ,content=unicode(tit+' '+abstract))
		except Exception as err :
			print tit, 'problem in indexing', err
		i+=1
		if i%100000==0:
			print i
	writer.commit()
	index.close()
		
	
if __name__ == '__main__':
	main(sys.argv)
