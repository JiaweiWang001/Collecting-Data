#!/opt/local/bin/python

import imaplib
import sys, signal
from avro import schema, datafile, io
import os, re
import email
import inspect, pprint
import getopt
import time
#from lepl.apps.rfc3696 import Email

class Email(object):
  def __init__(self):
    if len(email) > 7:
      if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    return False

class EmailUtils(object):
  
  def __init__(self):
    """This class contains utilities for parsing and extracting structure from raw UTF-8 encoded emails"""
    self.is_email = Email()
  
  def strip_brackets(self, message_id):
    return str(message_id).strip('<>')
  
  def parse_date(self, date_string):
    tuple_time = email.utils.parsedate(date_string)
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", tuple_time)
    return iso_time
  
  def get_charset(self, raw_email):
    if(type(raw_email)) is str:
      raw_email = email.message_from_string(raw_email)
    else:
      raw_email = raw_email
    charset = None
    for c in raw_email.get_charsets():
      if c != None:
        charset = c
        break
    return charset
  
  # '1011 (X-GM-THRID 1292412648635976421 RFC822 {6499}' --> 1292412648635976421
  def get_thread_id(self, thread_string):
    p = re.compile('\d+ \(X-GM-THRID (.+) RFC822.*')
    m = p.match(thread_string)
    return m.group(1)
   
  def parse_addrs(self, addr_string):
    if(addr_string):
      addresses = email.utils.getaddresses([addr_string])
      validated = []
      for address in addresses:
        address_pair = {'real_name': None, 'address': None}
        if address[0]:
          address_pair['real_name'] = address[0]
        if self.is_email(address[1]):
          address_pair['address'] = address[1]
        if not address[0] and not self.is_email(address[1]):
          pass
        else:
          validated.append(address_pair)
      if(len(validated) == 0):
        validated = None
      return validated
  
  def process_email(self, msg, thread_id):
    subject = msg['Subject']
    body = get_body(msg)
    
    # Without handling charsets, corrupt avros will get written
    charsets = msg.get_charsets()
    charset = None
    for c in charsets:
      if c != None:
        charset = c
        break
    
    if charset:
      subject = subject.decode(charset)#.encode('utf-8')
      body = body.decode(charset)#.encode('utf-8')
    else:
      return {}, charset
    
    avro_parts = {
      'message_id': strip_brackets(msg['Message-ID']),
      'thread_id': get_thread_id(thread_id),
      'in_reply_to': strip_brackets(msg['In-Reply-To']),
      'subject': subject,
      'date': parse_date(msg['Date']),
      'body': body,
      'froms': parse_addrs(msg['From']),
      'tos': parse_addrs(msg['To']),
      'ccs': parse_addrs(msg['Cc']),
      'bccs': parse_addrs(msg['Bcc']),
      'reply_tos': parse_addrs(msg['Reply-To'])
    }
    return avro_parts, charset
  
  def get_body(self, msg):
    body = ''
    if msg:
      for part in msg.walk():
        if part.get_content_type() == 'text/plain':
          body += part.get_payload()
    return body
    
    #if not avro_parts.has_key('froms'):
    #  return 'FROM', {}, charset
    
    #msg = email.message_from_string(raw_email)
    #avro_parts, charset = process_email(msg, thread_id)
