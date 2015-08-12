# Code for indexing dbpedia content with whoosh.
def indexRdf(ontDict, catDict, inLinks, redirect, entityIndexPath):

  ischema = Schema(resource = KEYWORD(stored = True), ont = ID(stored = True), \
    category = KEYWORD(stored=True), inlink = KEYWORD(stored=True), content = TEXT)

  if not os.path.exists(entityIndexPath):
    os.mkdir(entityIndexPath)

  eIndex = create_in(entityIndexPath, schema=ischema, indexname='eIndex')
  ewriter = eIndex.writer()

  for entry, categoryList in catDict.iteritems():
    #resource, ontPath, Category
    newEntry = entry.replace('_', ' ')
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
      eredirect = ('   '.join(redirect[entry])).replace('_', ' ')

    try:
      if eOnt and einlink and eredirect:
        ewriter.add_document(resource=unicode(newEntry),
                             ont=unicode(eOnt),
                             category=unicode(categoryString),
                             inlink=unicode(einlink),
                             content=unicode(eredirect + '   ' + newEntry))
      elif eOnt and eredirect:
        ewriter.add_document(resource=unicode(newEntry),
                             ont=unicode(eOnt),
                             category=unicode(categoryString),
                             content=unicode(eredirect + '   ' + newEntry))
      elif einlink and eredirect:
        ewriter.add_document(resource=unicode(newEntry),
                             inlink=unicode(einlink),
                             category=unicode(categoryString),
                             content=unicode(eredirect + '   ' + newEntry))
      elif eOnt and einlink:
        ewriter.add_document(resource=unicode(newEntry),
                             ont=unicode(eOnt),
                             category=unicode(categoryString),
                             inlink=unicode(einlink),
                             content=unicode(newEntry))
      elif eOnt:
        ewriter.add_document(resource=unicode(newEntry),
                             ont=unicode(eOnt),
                             category=unicode(categoryString),
                             content=unicode(newEntry))
      elif einlink:
        ewriter.add_document(resource=unicode(newEntry),
                             inlink=unicode(einlink),
                             category=unicode(categoryString),
                             content=unicode(newEntry))
      elif eredirect:
        ewriter.add_document(resource=unicode(newEntry),
                             category=unicode(categoryString),
                             content=unicode(newEntry + '   ' + eredirect))
      else:
        ewriter.add_document(resource=unicode(newEntry),
                             category=unicode(categoryString),
                             content=unicode(newEntry))

    except Exception as err:
      print 'Entry ::: ', entry, 'Category ::: ', categoryString, 'Ont ::: ', eOnt
      print err

    try:
      ewriter.commit()
      eIndex.close()
      ewriter.close()

    except Exception as err:
      print err


def indexLinks(inlinkFile, indexName, indexPath):
  linkschema = Schema(resource=TEXT(stored=True), inlinks=TEXT(stored=True))
  lIndex = create_in(indexPath, schema=linkschema, indexname=indexName)
  lwriter = lIndex.writer()

  for line in open(inlinkFile, 'r'):
    split = line.strip().split('\t')
    eid = split[0].replace('_', ' ')
    inlinks = '\t'.join(split[1:])
    try:
      lwriter.add_document(resource=unicode(eid), inlinks=unicode(inlinks))
    except Exception as err:
      print eid, 'problem in indexing'
    try:
      lwriter.commit()
      lIndex.close()
      lwriter.close()

    except Exception as err:
      print err

