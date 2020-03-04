#!/usr/bin/env python3
import os
import sys
import re
import argparse
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr
from email import encoders
import fcntl
import mimetypes


def maily(subject, text, attas, 
          to, cc, bcc, from_addr, passwd, 
          smtp, port, timeout, debuginfo):
    msg = MIMEMultipart('mixed')
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ';'.join(to)
    msg['Cc'] = ';'.join(cc)
    to.extend(cc)
    to.extend(bcc)
    for i in range(len(attas)):
        ftype, encoding = mimetypes.guess_type(attas[i])
        if (ftype is None 
              or encoding is not None):
            ftype = 'application/octet-stream'
        maintype, subtype = ftype.split('/')
        att = MIMEBase(maintype, subtype)
        att.add_header('Content-Disposition','attachement',filename=attas[i])
        att.add_header('Content-ID', '<%d>'%i)
        att.add_header('X-Attachment-Id', '<%d>'%i)
        with open(attas[i], 'rb') as f:
            att.set_payload(f.read())
        encoders.encode_base64(att)
        msg.attach(att)
    try:
        server = smtplib.SMTP_SSL(smtp, port, timeout)
        if debuginfo: server.set_debuglevel(2)
        server.login(from_addr, passwd)
        server.sendmail(from_addr, to, msg.as_string())
        server.quit()
    except Exception as e:
        print(repr(e))
        sys.exit(1)


def check_addr(addr):
    """check addr for literal formation only
    There has to be one @ and one . at lease, space is unacceptable."""
    if re.match('^[^\s]+@[^.\s]+(\.[^.\s]+)+$', addr): return True
    else: return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', required=True,
            help='subject for this email')
    parser.add_argument('--content', default=argparse.SUPPRESS,
            help='email content')
    parser.add_argument('--contype', default='plain', choices=['plain'],
            help='specify the content type, default is plain text')
    parser.add_argument('-a', '--attachment', nargs='+', default=[], 
            help='attachments files')
    parser.add_argument('--to', required=True, nargs='+',  
            help='addresses of receivers')
    parser.add_argument('--cc', nargs='+', default=[],  
            help='addresses of cc (carbon copy)')
    parser.add_argument('--bcc', nargs='+', default=[], 
            help='addresses of bcc (blind carbon copy)')
    parser.add_argument('--fromaddr', required=True,
            help='address of sender')
    parser.add_argument('--passwd', required=True,
            help='password of sender email account')
    parser.add_argument('--smtp', required=True,
            help='SMTP server of sender email account, '
                 'only support SSL/TSL connection')
    parser.add_argument('--port', type=int, default=465,  
            help='customize the port for SMTP server, default=465')
    parser.add_argument('--timeout', type=int, default=3,  
            help='connection timeout, default=3s')
    parser.add_argument('--debuginfo', action='store_true',  
            help='show debug info between SMTP server and maily')
    args = parser.parse_args()
    # check subject
    if args.subject.strip() == '':
        print('Subject can not be empty.')
        sys.exit(1)
    # check content
    if hasattr(args, 'content'):  # argument --content is present
        # stdin must be empyt
        if len(sys.stdin.readlines()) != 0:
            print('Conflict content from both --content argument and stdin.')
            sys.exit(1)
    else:
        setattr(args, 'content', ''.join(sys.stdin.readlines()))
    # content tail
    if args.contype == 'plain':
        args.content += \
          '\n\n\n\n--------\n'\
          'This email was sent by maily (https://github.com/xinlin-z/maily),'\
          ' which is a simple command line SMTP email sending tool in Python.'
    # check attachment list
    for item in args.attachment:
        if os.path.isfile(item) is False:
            print('Attachement %s is not a file.' % item)
            sys.exit(1)
    # check address list to, cc, bcc
    for addr in args.to:
        if check_addr(addr) is False:
            print('%s: address format error in --to list.' % addr)
            sys.exit(1)
    for addr in args.cc:
        if check_addr(addr) is False:
            print('%s: address format error in --cc list.' % addr)
            sys.exit(1)
    for addr in args.bcc:
        if check_addr(addr) is False:
            print('%s: address format error in -bcc list.' % addr)
            sys.exit(1)
    # go
    maily(args.subject, args.content, args.attachment,
          args.to, args.cc, args.bcc, args.fromaddr, args.passwd, 
          args.smtp, args.port, args.timeout, args.debuginfo)
    

if __name__ == '__main__':
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    main()


