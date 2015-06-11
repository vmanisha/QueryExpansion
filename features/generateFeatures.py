# -*- coding: utf-8 -*-
import argparse as ap
from queryLog import getSessionTuples
from queryLog import USER, QUERY, CLICKU
from entity.tag.findEntitiesWithDexter import tagQueryWithDexter, getCatAndTypeInfo
from utils import getNGramsAsList,getDictFromSet
#for each query in log do the following
#store the clicked document
#store the user if present
#store the session
#store entities

def updateDict(udict, val, key):
    if key not in udict:
        udict[key] = {}

    if type(val) == float or type(val) == int:
        udict[key][val] +=1
    if type(val) == list:
        for entry in val:
            updateDict(udict,entry, key)


def main():

    parser = ap.ArguementParser(description = 'Generate features for entity tagged queries')
    parser.add_argument('-i', '--iFile', help='Query log file', required=True)
    parser.add_argument('-o', '--oFile', help='Output feature file', required=True)
    parser.add_argument('-t', '--typeFile', help='DBPedia type file', required=True)
    parser.add_argument('-c', '--catFile', help='DBPedia cat file', required=True)
    parser.add_argument('-u', '--uid', help='User id present or not', required=True,type=bool)
    parser.add_argument('-w', '--wtype', help='Phrase (phrase) or query (query) features', required=True)

    args = parser.parse_args()

    boolUid = args.uid

    #load the category list
    dbCatList = {}

    #load the type list
    dbTypeList = {}

    #query list
    queryList = {}
    #user list
    userList = {}
    #url list
    urlList = {}
    #session list
    sessionList = {}
    #entity List
    entityList = {}
    #category List
    categoryList = {}
    #type list
    typeList = {}


    ipaddress = 'localhost'

    tagURL = 'http://'+ipaddress+':8080/dexter-webapp/api/rest/annotate'

    qid = 1
    sid = 1
    for session in getSessionTuples(args.iFile):
        for entry in session:
            query = entry[QUERY]
            #tag it with dexter and get all 3 parameters
            spotDict = tagQueryWithDexter(query,tagURL)
            updatedSpotDict = getCatAndTypeInfo(spotDict,dbCatList, dbTypeList)

            if args.wtype == 'query':
                #given wtype find the following
                if query not in queryList:
                    queryList[query] = qid

                updateDict(sessionList,sid, qid)

                if boolUid:
                    updateDict(userList, entry[USER], qid)
                if CLICKU in entry:
                    updateDict(urlList, entry[CLICKU],qid)

                for spot in updatedSpotDict['spots']:
                    updateDict(categoryList,spot['cat'], qid)
                    updateDict(typeList,spot['type'], qid)
                    updateDict(entityList,spot['wikiname'],qid)

                qid+=1

            if args.wtype == 'phrase':
                for spot in updatedSpotDict['spots']:
                    splits = query.split(spot)
                    for split in splits:
                        split = split.strip()
                        #remove stop words

                        if len(split) > 1:
                            if split not in queryList:
                                queryList[split] = qid

                            updateDict(sessionList,sid, qid)

                            if boolUid:
                                updateDict(userList, entry[USER], qid)
                            if CLICKU in entry:
                                updateDict(urlList, entry[CLICKU],qid)

                            for spot in updatedSpotDict['spots']:
                                updateDict(categoryList,spot['cat'], qid)
                                updateDict(typeList,spot['type'], qid)
                                updateDict(entityList,spot['wikiname'],qid)
                        qid+=1



        sid+=1


        #write the features to the outfile
        outF = open(args.oFile,'w')

        for query, qid in queryList.items():
            outF.write(query)
            #generate ngrams
            queryVect = getDictFromSet(query.split())
            ngramString = getNGramsAsList(query,3)
            #ngrams = 1
            outF.write('\t'+str(ngramString))
            #query vect = 2
            outF.write('\t'+str(queryVect))


            if qid in urlList:
                outF.write('\t'+str(urlList[qid]))
            else:
                outF.write('\t{}')

            if qid in userList:
                outF.write('\t'+str(userList[qid]))
            else:
                outF.write('\t{}')

            if qid in entityList:
                outF.write('\t'+str(entityList[qid]))
            else:
                outF.write('\t{}')

            if qid in categoryList:
                outF.write('\t'+str(categoryList[qid]))
            else:
                outF.write('\t{}')

            if qid in typeList:
                outF.write('\t'+str(typeList[qid]))
            else:
                outF.write('\t{}')

            if qid in sessionList:
                outF.write('\t'+str(sessionList[qid]))
            else:
                outF.write('\t{}')

            outF.write('\n')

        outF.close()

if __name__ == '__main__':
    main()