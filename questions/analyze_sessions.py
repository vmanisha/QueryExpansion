import sys
import os
from queryLog import getSessionsByUsers, getUserQueryAsString
from utils import loadFileInList


def WriteCleanSessionsToFile(user_sessions, min_session_length, output_file):
  ofile = open(output_file, 'w')
  for user, session_list in user_sessions.iteritems():
    for session in session_list:
      if len(session) > min_session_length:
        for user_entry in session:
          ofile.write(getUserQueryAsString(user_entry) + '\n')
  ofile.close()


def main(argv):
  queries_to_ignore = loadFileInList(argv[2], 0)
  clean_user_sessions = getSessionsByUsers(argv[1], queries_to_ignore)
  WriteCleanSessionsToFile(clean_user_sessions, 5, argv[3])


if __name__ == '__main__':
  main(sys.argv)
