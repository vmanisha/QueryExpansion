# -*- coding: utf-8 -*-

'''
Imports
'''
from whoosh.index import create_in
from whoosh.fields import Schema, ID, KEYWORD, TEXT
import os
import re
from utils import SYMB
import urllib

'''
Variables
'''
RSTR='resource/'
DSTR='dbpedia'


def indexRdf(ontDict, catDict, inLinks ,redirect, entityIndexPath):

        ischema = Schema(resource = KEYWORD(stored = True), ont = ID(stored = True), \
        category = KEYWORD(stored=True), inlink = KEYWORD(stored=True), content = TEXT)

	if not os.path.exists(entityIndexPath):
                os.mkdir(entityIndexPath)

	eIndex = create_in(entityIndexPath,schema=ischema, indexname ='eIndex')
        ewriter = eIndex.writer()

	for entry, categoryList in catDict.iteritems():
        	#resource, ontPath, Category
                newEntry = entry.replace('_',' ')
                categoryString = ' '.join(categoryList)
                #categoryString = categoryString.replace('_',' ')
		eOnt = None
		einlink = None
		eredirect = None

		if entry in ontDict:
			eOnt = ontDict[entry]
		#add a document
		if entry in inLinks:
			einlink = inLinks[entry]
		
		if entry in redirect:
			eredirect = ('   '.join(redirect[entry])).replace('_',' ')
		
		try :
			if eOnt and einlink and eredirect:
                        	ewriter.add_document(resource = unicode(newEntry) , ont = unicode(eOnt), category = unicode(categoryString), inlink=unicode(einlink), content = unicode(eredirect + '   '+ newEntry))
			elif eOnt and eredirect:
                        	ewriter.add_document(resource = unicode(newEntry) ,  ont = unicode(eOnt),category = unicode(categoryString), content = unicode(eredirect + '   '+ newEntry))
			elif einlink and eredirect:
                        	ewriter.add_document(resource = unicode(newEntry) ,  inlink = unicode(einlink), category = unicode(categoryString), content = unicode(eredirect + '   '+ newEntry))
			elif eOnt and einlink:
                        	ewriter.add_document(resource = unicode(newEntry) , ont = unicode(eOnt), category = unicode(categoryString), inlink=unicode(einlink), content = unicode(newEntry))
			elif eOnt:
                        	ewriter.add_document(resource = unicode(newEntry) ,  ont = unicode(eOnt), category = unicode(categoryString),content = unicode(newEntry))
			elif einlink:
                        	ewriter.add_document(resource = unicode(newEntry) ,  inlink = unicode(einlink), category = unicode(categoryString) , content = unicode(newEntry))
			elif eredirect:
                        	ewriter.add_document(resource = unicode(newEntry) ,  category = unicode(categoryString), content = unicode(newEntry + '   '+ eredirect))
			else:
                        	ewriter.add_document(resource = unicode(newEntry) , category = unicode(categoryString),content = unicode(newEntry))
								
                except Exception as err:
                        print 'Entry ::: ',entry,'Category ::: ', categoryString, 'Ont ::: ', eOnt
                        print err

        try:
        	ewriter.commit()
                eIndex.close()
                ewriter.close()

        except Exception as err:
                print err
	

def indexLinks(inlinkFile, indexName, indexPath):
	linkschema = Schema (resource = TEXT (stored = True), inlinks = TEXT (stored = True))
	lIndex = create_in(indexPath,schema=linkschema, indexname =indexName)
        lwriter = lIndex.writer()
		
	for line in open(inlinkFile,'r'):
		split = line.strip().split('\t')
		eid = split[0].replace('_',' ')
		inlinks = '\t'.join(split[1:])
		try :
                       		lwriter.add_document(resource=unicode(eid) ,inlinks=unicode(inlinks))
		except Exception as err :
			print eid, 'problem in indexing'
        try:
        	lwriter.commit()
                lIndex.close()
                lwriter.close()

        except Exception as err:
                print err


def loadInstances(instanceFile):
        resourceOntDict = {}
        oTitle = None
        oOnt = None
        oLine = None
        #index the two files
        #Load the title, ontology from the instanceFile
        ifile = open(instanceFile,'r')
        for line in ifile:
                split = line.strip().lower().split(' ')
                #get the title
                cTitle = split[0][split[0].rfind(RSTR)+9:-1]
                #get the ontology
                if split[2].find(DSTR) > -1:
                        cOnt = split[2][split[2].rfind('/')+1:-1]
                        #if same title
                        if oTitle == None and oOnt == None:
                                oOnt =  line
                        elif cTitle == oTitle:
                                #merge the ontology
                                oOnt = cOnt +'/'+ oOnt
                        else:
                                #store the old title and ont
                                if len(oTitle) < 2:
                                        print 'Error in ontology ::: ', line, oLine, cOnt, oOnt, cTitle, oTitle
                                else:
                                        resourceOntDict[oTitle] = oOnt
                                oOnt = cOnt
                        oTitle = cTitle
                        oLine = line

        ifile.close()
	return resourceOntDict



def loadCategories(categoriesFile ):
        resourceCatDict = {}
        #print resourceOntDict
        ifile = open(categoriesFile,'r')
        i = 0
	for line in ifile:
                split = line.lower().strip().split(' ')
                dbpediaURL = urllib.unquote_plus(split[0])
                dbpediaURL = dbpediaURL.encode('UTF-8').encode('unicode-escape')
				
                cTitle = dbpediaURL[dbpediaURL.rfind(RSTR)+9:-1]

                cCat = split[2][split[2].rfind(':')+1:-1]
                if len(cTitle) > 1 and len(cCat) > 1:
                        if cTitle not in resourceCatDict:
                                resourceCatDict[cTitle] = []
                        resourceCatDict[cTitle].append(cCat)
			i += 1
                #else:
                #        print 'Error in Category :: ',line, cTitle, cCat
        ifile.close()
	print 'Completed', i , ' node categories'
        return resourceCatDict

def loadSkosCategories(categoriesFile,filterCat = None):
	broadSet = set()
	relatedSet = set()
	cats = set()
        #print resourceOntDict
        ifile = open(categoriesFile,'r')
        i = 0
	for line in ifile:
                broad =  'core#broader' in line
                related = 'core#related' in line
				#if  broad:
                split = line.lower().strip().split(' ')
                c1 = split[0]
                #c1 = urllib.unquote_plus(split[0])
                #c1 = c1.encode('UTF-8').encode('unicode-escape')
                c1 = c1[c1.rfind(RSTR)+9:-1]
                c1 = c1[c1.rfind(':')+1:]
				
                c2 = split[2]
                #c2 = urllib.unquote_plus(split[2])
                #c2 = c2.encode('UTF-8').encode('unicode-escape')
                c2 = c2[c2.rfind(RSTR)+9:-1]
                c2 = c2[c2.rfind(':')+1:]
                #print c1, c2

                if len(c1) > 1 and len(c2) > 1 and filterCat and (c1 in filterCat or c2 in filterCat):
                            if broad:
                                        broadSet.add((c1, c2))
                            if related:
                                        relatedSet.add((c1,c2))
                            cats.add(c1)
                            cats.add(c2)		

                        	
                        #if cTitle not in resourceCatDict:
                        #        resourceCatDict[cTitle] = []
                        #resourceCatDict[cTitle].append(cCat)
                                 #print line,
                i += 1
                #else:
                #        print 'Error in Category :: ',line, cTitle, cCat
        ifile.close()
	#print 'Completed', i , ' node categories'
        return cats, relatedSet, broadSet

def loadCategoryTitles(categoriesFile ):
        resourceCatDict = {}
        #print resourceOntDict
        ifile = open(categoriesFile,'r')
        i = 0
	for line in ifile:
                split = line.lower().strip().split(' ')
                cTitle = split[0][split[0].rfind(RSTR)+9:-1].replace('_',' ')
                cCat = split[2][split[2].rfind(':')+1:-1]
                if len(cTitle) > 1 and len(cCat) > 1:
                        if cCat not in resourceCatDict:
                                resourceCatDict[cCat] = []
                        resourceCatDict[cCat].append(cTitle)
			#print 'Adding', cTitle, 'to', cCat
			i += 1
                #else:
                #        print 'Error in Category :: ',line, cTitle, cCat
        ifile.close()
	print 'Loaded', i , ' node categories'
	return resourceCatDict

def loadInlinks(fileName):
	inlink = {}
	i = 0
	for line in open(fileName,'r'):
		index = line.find('\t')
		inlink[line[0:index]] = line[index+1:].strip().replace('\t',' ')
		i += 1
	print 'Loaded ',i,' node inlinks'
	return inlink

def loadRedirects(fileName):
	
	redirect = {}
	i = 0
	for line in open(fileName,'r'):
		split = line.strip().lower().split(' ')
		redir = split[0][split[0].rfind(RSTR)+9:-1]	
		title = split[-1][split[-1].rfind(RSTR)+9:-1]
		if title not in redirect:
			redirect[title] = set()
		redirect[title].add(redir)
		i+= 1
	print 'Loaded ', i, 'redirects'
	return redirect


def loadAbstracts(fileName):
	abstracts = {}
	i = 0
	for line in open(fileName,'r'):
		split = line.strip().lower().split('>')
		title = split[0][split[0].rfind(RSTR)+9:].replace('_',' ')
		abstract = split[-1][split[-1].find('"')+1:split[-1].rfind('"')]
		abstract = abstract.decode('unicode_escape').encode('ascii','ignore')
		abstract = re.sub(SYMB,' ',abstract)
		abstracts[title] = abstract
		i+=1
	print 'Loaded ', i, 'abstracts'
	return abstracts
	
	
#instance = loadInstances(argv[1])
#categories = loadCategories(argv[2])
#inlinks = loadInlinks(argv[3])
#redirects = loadRedirects(argv[4])
#idDict, inLinks, outLinks = loadLinks(argv[1])
#indexRdf(instance, categories, inlinks, redirects, 'eRIndex')	
#indexLinks(idDict, inLinks, outLinks, 'lIndex')
	