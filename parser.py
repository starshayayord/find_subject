# -*- coding: utf-8 -*-
from glob import glob
import locale
import threading
import base64
import sys
import codecs
import re
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

def get_subject(line):
    prefix = '=?utf-8?B?'
    suffix = '?=?'
    line = (re.search('Subject: (.*?) from', line)).group(1)
    subject = line.replace(prefix, '').replace(suffix, '').replace(' ', '')
    lenx = (len(subject) // 4)*4
    decoded = base64.b64decode(subject[:lenx])
    return decoded

def get_date(line, max):
    logdate = re.search(r'^\w{3} \d{2} \d{2}:\d{2}:\d{2}', line).group(0)
    with setlocale('C'):
        date_object = datetime.strptime(logdate, '%b %d %H:%M:%S')
    if date_object >= datetime.strptime(max, '%b %d %H:%M:%S'):
        return True
    else:
        return False

def main (in_files, out_file, pattern, max_date):
    listing = glob(in_files)
    for file_log in listing:
        with open(file_log, mode='r') as f:
            for line in f:
                if 'Subject: =?utf-8?B?' in line:
                    subject = get_subject(line)
                    if pattern in subject:
                        if get_date(line, max_date):
                            with open(out_file, 'a') as outfile:
                                outfile.write("%s \n" % str(line))

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
pattern = 'поступило требование'
in_files= 'C:\\MINELOGS\\maillog*'
out_file = 'C:\\MINELOGS\\matched_subject.log'
max_date = 'Nov 24 09:00:00'
main(in_files, out_file, pattern, max_date)