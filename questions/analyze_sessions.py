import sys;
import os;
from queryLog import getSessionsByUsers


def WriteCleanSessionsToFile(user_sessions, min_session_length, ofile):
  ofile = open(output_file,'w');
  for user, session_list in user_sessions.iteritems():
    for session in session_list:
      if len(session) > min_session_length:
        ofile.write("\t".join(session.values())+'\n');
  ofile.close();
  
def main(argv):
  clean_user_sessions = getSessionsByUsers(argv[1]);
  WriteCleanSessionsToFile(clean_user_sessions,5,argv[2]);


if __name__ == '__main__':
  app.run()
