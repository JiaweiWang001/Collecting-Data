#!/usr/bin/env python

import imaplib
import sys
from avro import schema, datafile, io
import os
import email
import inspect
import pprint

def init_directory(directory):
  if os.path.exists(directory):
    print '%(directory)s already exists' % {"directory":directory}
  else:
    os.makedirs(directory)
  return directory

def init_avro(output_dir, part_id, schema_path):
  out_filename = '%(output_dir)s/part-%(part_id)s.avro' % \
    {"output_dir": output_dir, "part_id": str(part_id)}
  schema_string = linestring = open(schema_path, 'r').read()
  email_schema = schema.parse(schema_string)
  rec_writer = io.DatumWriter(email_schema)
  df_writer = datafile.DataFileWriter(
    open(out_filename, 'wb'),
    rec_writer,
    email_schema
  )
  return df_writer

def fetch_email(imap, id):
  status, data = imap.fetch(id, '(RFC822)')
  raw_email = data[0][1]
  msg = email.message_from_string(raw_email)
  text_parts = walk_msg(msg)
  avro_parts = process_email(msg)
  return avro_parts

def parse_addrs(addr_string):
  if addr_string:
    ads = email.utils.getaddresses([addr_string])
    final = []
    for a in ads:
      final.append(a[1])
    address = final
  else:
    address = addr_string
  return address

def process_email(msg):  
  avro_parts = {
    'message_id': parse_addrs(msg['Message-ID']),
    'from': parse_addrs(msg['From']),
    'to': parse_addrs(msg['To']),
    'cc': parse_addrs(msg['Cc']),
    'bcc': parse_addrs(msg['Bcc']),
    'reply_to': parse_addrs(msg['Reply-To']),
    'in_reply_to': parse_addrs(msg['In-Reply-To']),
    'subject': parse_addrs(msg['Subject']),
    'date': parse_addrs(msg['Date'])
  }
  return avro_parts

def write_email(writer, email):
  writer.append(email)

def walk_msg(msg):
  for part in msg.walk():
    if part.get_content_type() == "multipart/alternative":
      continue
    yield part.get_payload(decode=1)

# MAIN
if (len(sys.argv) < 4):
  print """Usage: gmail.py <username@gmail.com> <password> <output_directory>"""
  exit(0)

user_name = sys.argv[1]
password = sys.argv[2]
directory = init_directory(sys.argv[3])

pp = pprint.PrettyPrinter(indent=4)

schema_path = '/me/Collecting-Data/src/avro/email.schema'
avro_writer = init_avro(output_dir, 1, schema_path)
imap_folder = '[Gmail]/All Mail'

imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
imap.login(user_name,password)
status, count = imap.select(imap_folder)

email_hash = fetch_email(imap, '5')
avro_writer.append(email_hash)
avro_writer.close()

imap.close()
imap.logout()


