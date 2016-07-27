# -*- coding: utf-8 -*-
'''Imports
'''
import re
from utils import SYMB
import urllib
from lxml import etree
import sys
import os
'''Variables
'''
RSTR = 'resource/'
OSTR = 'ontology/'

DSTR = 'dbpedia'



def loadInstances(instanceFile):
  resourceOntDict = {}
  oTitle = None
  oOnt = None
  oLine = None
  #index the two files
  #Load the title, ontology from the instanceFile
  ifile = open(instanceFile, 'r')
  for line in ifile:
    split = line.strip().lower().split(' ')
    #get the title
    cTitle = split[0][split[0].rfind(RSTR) + 9:-1]
    #get the ontology
    if split[2].find(DSTR) > -1:
      cOnt = split[2][split[2].rfind('/') + 1:-1]
      #if same title
      if oTitle == None and oOnt == None:
        oOnt = line
      elif cTitle == oTitle:
        #merge the ontology
        oOnt = cOnt + '/' + oOnt
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


def loadInstancesInList(instanceFile):
  resourceCatDict = {}
  #print resourceOntDict
  ifile = open(instanceFile, 'r')
  i = 0
  for line in ifile:
    split = line.lower().strip().split(' ')
    dbpediaURL = urllib.unquote_plus(split[0])
    try:
      dbpediaURL = dbpediaURL.decode('utf-8').encode('unicode-escape')
      cTitle = dbpediaURL[dbpediaURL.rfind(RSTR) + 9:-1]
      #if cTitle not in split[0]:
      #    print split[0], cTitle
      cCat = split[2][split[2].rfind('/') + 1:-1]
      if len(cTitle) > 1 and len(cCat) > 1:
        if cTitle not in resourceCatDict:
          resourceCatDict[cTitle] = []
        resourceCatDict[cTitle].append(cCat)
      i += 1
    except:
      print dbpediaURL
    #else:
    #        print 'Error in Category :: ',line, cTitle, cCat
  ifile.close()
  print 'Completed', i, ' node instances'
  return resourceCatDict


def loadCategories(categoriesFile):
  resourceCatDict = {}
  #print resourceOntDict
  ifile = open(categoriesFile, 'r')
  i = 0
  for line in ifile:
    split = line.lower().strip().split(' ')
    dbpediaURL = urllib.unquote_plus(split[0])
    try:
      dbpediaURL = dbpediaURL.decode('utf-8').encode('unicode-escape')
      cTitle = dbpediaURL[dbpediaURL.rfind(RSTR) + 9:-1]
      #if cTitle not in split[0]:
      #    print split[0], cTitle
      cCat = split[2][split[2].rfind(':') + 1:-1]
      if len(cTitle) > 1 and len(cCat) > 1:
        if cTitle not in resourceCatDict:
          resourceCatDict[cTitle] = []
        resourceCatDict[cTitle].append(cCat)
      i += 1
    except:
      print dbpediaURL
    #else:
    #        print 'Error in Category :: ',line, cTitle, cCat
  ifile.close()
  print 'Completed', i, ' node categories'
  return resourceCatDict


def loadOntology(ontFile, filterCat=None):
  parentSet = set()
  cat = set()
  tree = etree.fromstring(open(ontFile, 'r').read())
  for element in tree:
    cname = None
    pname = None
    #	print element.tag, element.attrib
    if 'Class' in element.tag:
      cname = element.attrib.values()[0]
      cname = cname[cname.rfind('/') + 1:].lower()

    for child in element.getchildren():
      if 'subClass' in child.tag:
        pname = child.attrib.values()[0]
        pname = pname[pname.rfind('/') + 1:].lower()
      #print child.tag, child.attrib

    if cname and pname:
      parentSet.add((cname, pname))
      cat.add(cname)
      cat.add(pname)
  return cat, set(), parentSet
  #print element
  #context = etree.iterparse(StringIO(open(ontFile,'r').read()))
  #for action, elem in context:
  #print("%s: %s" % (action, elem.tag))


def loadSkosCategories(categoriesFile, filterCat=None):
  broadSet = set()
  relatedSet = set()
  cats = set()
  #print resourceOntDict
  ifile = open(categoriesFile, 'r')
  i = 0
  for line in ifile:
    broad = 'core#broader' in line
    related = 'core#related' in line
    #if  broad:
    split = line.lower().strip().split(' ')
    c1 = split[0]
    #c1 = urllib.unquote_plus(split[0])
    #c1 = c1.encode('UTF-8').encode('unicode-escape')
    c1 = c1[c1.rfind(RSTR) + 9:-1]
    c1 = c1[c1.rfind(':') + 1:]
    c2 = split[2]
    #c2 = urllib.unquote_plus(split[2])
    #c2 = c2.encode('UTF-8').encode('unicode-escape')
    c2 = c2[c2.rfind(RSTR) + 9:-1]
    c2 = c2[c2.rfind(':') + 1:]
    #print c1, c2

    if len(c1) > 1 and len(c2) > 1 and filterCat and (c1 in filterCat or c2 in
                                                      filterCat):
      if broad:
        broadSet.add((c1, c2))
      if related:
        relatedSet.add((c1, c2))
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


def loadCategoryTitles(categoriesFile):
  resourceCatDict = {}
  #print resourceOntDict
  ifile = open(categoriesFile, 'r')
  i = 0
  for line in ifile:
    split = line.lower().strip().split(' ')
    cTitle = split[0][split[0].rfind(RSTR) + 9:-1].replace('_', ' ')
    cCat = split[2][split[2].rfind(':') + 1:-1]
    if len(cTitle) > 1 and len(cCat) > 1:
      if cCat not in resourceCatDict:
        resourceCatDict[cCat] = []
      resourceCatDict[cCat].append(cTitle)
    #print 'Adding', cTitle, 'to', cCat
    i += 1
    #else:
    #        print 'Error in Category :: ',line, cTitle, cCat
  ifile.close()
  print 'Loaded', i, ' node categories'
  return resourceCatDict


def loadInlinks(fileName):
  inlink = {}
  i = 0
  for line in open(fileName, 'r'):
    index = line.find('\t')
    inlink[line[0:index]] = line[index + 1:].strip().replace('\t', ' ')
    i += 1
  print 'Loaded ', i, ' node inlinks'
  return inlink


def loadRedirects(fileName):

  redirect = {}
  i = 0
  for line in open(fileName, 'r'):
    split = line.strip().lower().split(' ')
    redir = split[0][split[0].rfind(RSTR) + 9:-1]
    title = split[-1][split[-1].rfind(RSTR) + 9:-1]
    if title not in redirect:
      redirect[title] = set()
    redirect[title].add(redir)
    i += 1
  print 'Loaded ', i, 'redirects'
  return redirect


def loadAbstracts(fileName):
  abstracts = {}
  i = 0
  for line in open(fileName, 'r'):
    split = line.strip().lower().split('>')
    title = split[0][split[0].rfind(RSTR) + 9:].replace('_', ' ')
    abstract = split[-1][split[-1].find('"') + 1:split[-1].rfind('"')]
    abstract = abstract.decode('unicode_escape').encode('ascii', 'ignore')
    abstract = re.sub(SYMB, ' ', abstract)
    abstracts[title] = abstract
    i += 1
  print 'Loaded ', i, 'abstracts'
  return abstracts


if __name__ == '__main__':
  argv = sys.argv
  loadOntology(argv[1])
#instance = loadInstances(argv[1])
#categories = loadCategories(argv[2])
#inlinks = loadInlinks(argv[3])
#redirects = loadRedirects(argv[4])
#idDict, inLinks, outLinks = loadLinks(argv[1])
#indexRdf(instance, categories, inlinks, redirects, 'eRIndex')
#indexLinks(idDict, inLinks, outLinks, 'lIndex')
