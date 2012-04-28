#!/usr/bin/env python

import os, sys, getopt
from lepl.apps.rfc3696 import Email

from gmail_slurper import GmailSlurper

def usage(context):
  print """Usage: gmail.py -m <mode: interactive|automatic> -u <username@gmail.com> -p <password> -s <schema_path> -f <imap_folder> -o <output_path>"""

def does_exist(path_string, name):
  if(os.path.exists(path_string)):
    pass
  else:
    print "Error: " + name + ": " + path_string + " does not exist."
    sys.exit(2)

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'm:u:p:s:f:o:')
  except getopt.GetoptError, err:
    # print help information and exit:
    print "Error:" + str(err) # will print something like "option -a not recognized"
    usage("getopt")
    sys.exit(2)
  
  mode = None
  username = None
  password = None
  schema_path = None #'../avro/email.schema'
  imap_folder = None #'[Gmail]/All Mail'
  output_path = None
  arg_check = dict()
  
  for o, a in opts:
    if o == "-m":
      mode = a
      if mode in ('automatic', 'interactive'):
        pass
      else:
        usage('opts')
        sys.exit(2)
      arg_check[o] = 1
    elif o in ("-u"):
      username = a
      arg_check[o] = 1
    elif o in ("-p"):
      password = a
      arg_check[o] = 1
    elif o in ("-s"):
      schema_path = a
      does_exist(schema_path, "filename")
      arg_check[o] = 1
    elif o in ("-f"):
      imap_folder = a
      arg_check[o] = 1
    elif o in ("-o"):
      output_path = a
      arg_check[o] = 1
    else:
      assert False, "unhandled option"

  if(len(arg_check.keys()) >= 6):
    pass
  else:
    usage('numargs')
    sys.exit(2)
  
  if(len(arg_check.keys()) == len(sys.argv[1:])/2):
    pass
  else:
    usage('badargs')
    sys.exit(2)
  
  slurper = GmailSlurper()
  slurper.init_avro(output_path, 1, schema_path)
  slurper.init_imap(username, password)
  status, count = slurper.init_folder(imap_folder)
  if(status == 'OK'):
    if(mode == 'automatic'):
      print "Connected to folder " + imap_folder + " and downloading " + str(count) + " emails..."
      slurper.slurp()  
      slurper.shutdown()
  else:
    print "Problem initializing imap connection."

if __name__ == "__main__":
  main()
