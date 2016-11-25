# -*- coding: utf-8 -*-
from glob import glob
import locale
import threading
import base64
import sys
import codecs
import re
from quopri import decodestring
from datetime import datetime
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def get_subject(line, encoding, cipher):
    prefix = '=\?' + encoding +'\?\w{1}\?'
    suffix = '?=?'
    line = (re.search(r'Subject: (.*?) from', line)).group(1)
    line = re.sub(re.compile(prefix), '', line)
    subject = line.replace(suffix, '').replace(' ', '').replace('?', '')
    if cipher == 'B':
        lenx = (len(subject) // 4)*4
        decoded = base64.b64decode(subject[:lenx])
    if cipher == 'Q':
        if re.search(r'=\w{0,1}$', subject):
            subject = re.sub(r'=\w{0,1}$', '', subject)
        decoded = decodestring(subject)
    if encoding != 'utf-8':
        decoded = decoded.decode(encoding)
    else:
        try:
            decoded = unicode(decoded, "utf-8", 'ignore')
        except:
            print("ERROR while parsing: ", subject, encoding, cipher)
            raise ValueError("Error while decoding subject: maybe mixed encoding/cipher")
    return decoded


def get_date(line, max):
    logdate = re.search(r'^\w{3} \d{2} \d{2}:\d{2}:\d{2}', line).group(0)
    with setlocale('C'):
        date_object = datetime.strptime(logdate, '%b %d %H:%M:%S')
    if date_object >= datetime.strptime(max, '%b %d %H:%M:%S'):
        return True
    else:
        return False


def is_subject_get_encoding(line):
    encoding  = ''
    cipher = ''
    #TO DO: mixed encoding line = 'Subject: =?utf-8?b?W1NlbnRyeV0gW1NlbnRyeSBFbGJhXSBGQVRBTDog0J3QtSDQvdCw0LnQtNC1?=? =?utf-8?b?0L0g0L/QsNGA0LDQvNC10YLRgCAnbW9kZScsIGFuZCB0aGUgbWVzc2FnZSB3?=? =?utf-8?q?as_=5BUnhandled_exception=5D?= from'
    if 'Subject:' in line:
        mixed = re.search(r'Subject: =\?(.*?)\?(\w)\?', line)
        if mixed:
            encoding = mixed.group(1)
            cipher = mixed.group(2)
    return encoding, cipher


def main(in_files, out_file, pattern, max_date):
    listing = glob(in_files)
    for file_log in listing:
        with open(file_log, mode='r') as f:
            for line in f:
                encoding, cipher = is_subject_get_encoding(line)
                if encoding and cipher:
                    try:
                        subject = get_subject(line, encoding, cipher)
                        try:
                            if pattern in subject:
                                if get_date(line, max_date):
                                    with open(out_file, 'a') as outfile:
                                        outfile.write("%s \n" % str(line))
                        except:
                            print("Error while date comparsion")
                    except:
                        continue

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
pattern = 'поступило требование'
pattern = unicode(pattern, "utf-8")
in_files = 'C:\\MINELOGS\\maillog*'
out_file = 'C:\\MINELOGS\\matched_subject.log'
max_date = 'Nov 24 01:00:00'
main(in_files, out_file, pattern, max_date)

