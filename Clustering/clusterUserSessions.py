import os, sys


#format -- userid \t query:freq, query:freq \t url:freq, url: freq


def loadSessions(iFile, outFile):
    sameList = {}
    for line in iFile:
        split = line.strip().split('\t')
        uid = split[0]
        #first merge the one line queries
        if ',' not in split[1]:
            #only one query
            query = split[1][:split[1].find(':')]
            freq = int(split[1][split[1].find(':')+1:])
            #len
            if len(split) > 2:
                link = split[2][:split[2].rfind(':')]
                lfreq =  int(split[2][split[2].rfind(':')+1:])
            key = uid+'_'+query
            if key not in sameList:
                sameList[key] = {'count':0,'link' : {}}

            sameList[key]['count']+= freq
            if len(split) > 2:
                sameList[key]['link'][link] = lfreq if link not in sameList[key]['link'] else sameList[key]['link'][link] + lfreq

        else:
            outFile.write(line)

    for key, fdict in sameList.iteritems():
        string = key[:key.find('_')] + '\t' + key[key.find('_')+1:] + ':'+str(fdict['count']) + '\t'
        string += ', '.join('{0}:{1}'.format(x,str(y)) for x,y in fdict['link'].iteritems())
        outFile.write(string+'\n')


def main(args):

    if not os.path.exists(args[2]):
        os.mkdir(args[2])
    for fileName in os.listdir(args[1]):
        ofile = open(args[2]+'/'+fileName,'w')
        ifile = open(args[1]+'/'+fileName, 'r')
        loadSessions(ifile,ofile)
        ifile.close()
        ofile.close()


if __name__ == '__main__':
    main(sys.argv)
