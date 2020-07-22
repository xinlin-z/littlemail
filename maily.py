#!/usr/bin/env python3
import os
import sys
import re
import argparse
import textwrap
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
        att.add_header('Content-Disposition','attachement',
                       filename = os.path.basename(attas[i]))
        att.add_header('Content-ID', '<%d>'%i)
        att.add_header('X-Attachment-Id', '<%d>'%i)
        with open(attas[i], 'rb') as f:
            att.set_payload(f.read())
        encoders.encode_base64(att)
        msg.attach(att)
    try:
        if port == 465:
            server = smtplib.SMTP_SSL(smtp, port, timeout)
        else:
            server = smtplib.SMTP(smtp, port, timeout)
        if debuginfo:
            if sys.version.split()[0][:3] >= '3.5':
                server.set_debuglevel(2)
            else: server.set_debuglevel(1)
        if port == 587: server.starttls()
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


# contants
VER = 'maily: a cmd-line SMTP email sending tool in Python, V0.16'


def main():
    parser = argparse.ArgumentParser(
                formatter_class = argparse.RawDescriptionHelpFormatter,
                description = VER + textwrap.dedent('''

    Usage Examples:

    1), inline
        $ python3 maily.py inline --subject a_title --content test_content
        --to to@qq.com --fromaddr from@qq.com --passwd your_password
        --smtp smtp.qq.com

        You can also specify -a for attachments.
        The default --contype is plain.
        --cc and --bcc are for other receivers.
        The default --port is 587, you can also set it to 25 or 465.

        One more thing, there three ways to fill the email's content:
        (a), fill --content options in cmd line;
        (b), $ python3 maily.py ..... < content.txt
        (c), $ echo your_content | python3 maily.py ...

        help info for inline:
        $ python3 maily.py inline -h


                ''')
    )
    parser.add_argument('-V', '--version', action='version', version=VER)
    subparser = parser.add_subparsers(dest='subcmd',
                                      title='sub commands')
    parser_inline = subparser.add_parser('inline',
            help='all parameters are specified in cmd line, one email sent '
                 'by each cmd')
    parser_infile = subparser.add_parser('infile',
            help='all parameters are stored in files, support batch mode')
    # subcommand: inline
    parser_inline.add_argument('--subject', required=True,
            help='subject for this email')
    parser_inline.add_argument('--content', default=argparse.SUPPRESS,
            help='email content')
    parser_inline.add_argument('--contype',default='plain',choices=['plain'],
            help='specify the content type, default is plain text')
    parser_inline.add_argument('-a', '--attachment', nargs='+', default=[],
            help='attachments files')
    parser_inline.add_argument('--to', required=True, nargs='+',
            help='addresses of receivers')
    parser_inline.add_argument('--cc', nargs='+', default=[],
            help='addresses of cc (carbon copy)')
    parser_inline.add_argument('--bcc', nargs='+', default=[],
            help='addresses of bcc (blind carbon copy)')
    parser_inline.add_argument('--fromaddr', required=True,
            help='address of sender')
    parser_inline.add_argument('--passwd', required=True,
            help='password of sender email account')
    parser_inline.add_argument('--smtp', required=True,
            help='SMTP server of sender email account')
    parser_inline.add_argument('--port', type=int, default=587,
            choices=[25,465,587],
            help='choose the port for SMTP server, default=587')
    parser_inline.add_argument('--timeout', type=int, default=3,
            help='connection timeout, default=3s')
    parser_inline.add_argument('--debuginfo', action='store_true',
            help='show debug info between SMTP server and maily')
    args = parser.parse_args()
    if args.subcmd == 'inline':
        # check subject
        if args.subject.strip() == '':
            print('Subject can not be empty.')
            sys.exit(1)
        # check content
        if hasattr(args, 'content'):  # argument --content is present
            # stdin must be empyt
            if len(sys.stdin.readlines()) != 0:
                print('content conflict from both cmd argument and stdin.')
                sys.exit(1)
        else:
            setattr(args, 'content', ''.join(sys.stdin.readlines()))
        # check attachment list
        for item in args.attachment:
            if os.path.isfile(item) is False:
                print('Attachement %s is not a file.' % item)
                sys.exit(1)
        # check addresses in to, cc, bcc and fromaddr
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
        if check_addr(args.fromaddr) is False:
            print('%s: address format error in --fromaddr.' % args.fromaddr)
            sys.exit(1)
        # go
        maily(args.subject, args.content, args.attachment,
              args.to, args.cc, args.bcc, args.fromaddr, args.passwd,
              args.smtp, args.port, args.timeout, args.debuginfo)
    else:  # infile
        print('under development')


if __name__ == '__main__':
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    main()


