#!/usr/bin/env python3
import os
import sys
import re
import time
import argparse
import textwrap
import smtplib
import json
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr
from email import encoders
import fcntl
import mimetypes


server = None
server_on = False
def _server_send(smtp, port, timeout, tlayer, debuginfo,
                 from_addr, passwd, to, msg, hold=False):
    global server,server_on
    if not server_on:
        # server para
        para = {'host': smtp,
                'port': port,
                'timeout': timeout}
        # create server
        if port in (25, 465, 587):
            if port == 465:
                server = smtplib.SMTP_SSL(**para)
            else:
                server = smtplib.SMTP(**para)
        else:
            if tlayer in ('plain', 'tls'):
                server = smtplib.SMTP(**para)
            else:  # ssl
                server = smtplib.SMTP_SSL(**para)
        # debuginfo
        if debuginfo:
            if sys.version.split()[0][:3] >= '3.5':
                server.set_debuglevel(2)
            else: server.set_debuglevel(1)
        if port == 587 or tlayer == 'tls':
                server.starttls()
        server.login(from_addr, passwd)
        server_on = True
    # do send
    server.sendmail(from_addr, to, msg.as_string())
    if not hold:
        server.quit()
        server_on = False


def _get_msg_to(subject, text, contype, attas, to, cc, bcc, from_addr):
    # construct the mail
    msg = MIMEMultipart('mixed')
    msg.attach(MIMEText(text, contype, 'utf-8'))
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ';'.join(to)
    msg['Cc'] = ';'.join(cc)
    to.extend(cc)
    to.extend(bcc)
    # attachments
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
    return msg,to


def check_addr(addr):
    """check addr for literal formation only
    There has to be one @ and one . at lease, space is unacceptable."""
    if re.match('^[^\s]+@[^.\s]+(\.[^.\s]+)+$', addr): return True
    else: return False


def pInt(string):
    try:
        num = int(string)
        if num < 0:
            raise argparse.ArgumentTypeError(
                        'Port must be a positive integer.')
    except argparse.ArgumentTypeError:
        raise
    except Exception as e:
        raise argparse.ArgumentTypeError(repr(e))
    else:
        return num


# contants
VER = 'maily: a cmd-line SMTP email sending tool in Python, V0.18'


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
        The default --contype is plain, html is supported.
        --cc and --bcc are for other receivers.
        The default --port is 587, you can also set it to 25, 465 or others,
        with --tlayer option if needed.

        One more thing, there three ways to fill the email's content:
        (a), fill --content options in cmd line;
        (b), $ python3 maily.py ..... < content.txt
        (c), $ echo your_content | python3 maily.py ...

        help info for inline:
        $ python3 maily.py inline -h

    2), infile
        $ python3 maily.py infile msg.json

        All of the parameters needed are in a single json file. msg.json is
        an example for you. Some items in json are optional.
        So, if you put more than one msg under one account, or you set more
        than one account, you will get batch mode. The SMTP server will hold
        automatically until the last msg for each account.
    '''),
                epilog = 'maily project page: '
                         'https://github.com/xinlin-z/maily\n'
                         'python note blog: '
                         'https://www.pynote.net'
    )
    parser.add_argument('-V', '--version', action='version', version=VER)
    subparser = parser.add_subparsers(dest='subcmd',
                                      title='sub commands')
    parser_inline = subparser.add_parser('inline',
            help='parameters are specified in cmd line, one email sent '
                 'by each cmd')
    parser_infile = subparser.add_parser('infile',
            help='parameters are stored in json files, support batch mode')
    # subcommand: inline
    parser_inline.add_argument('--subject', required=True,
            help='subject for this email')
    parser_inline.add_argument('--content', default=argparse.SUPPRESS,
            help='email content')
    parser_inline.add_argument('--contype', default='plain',
            choices=['plain', 'html'],
            help='specify the content type, default=plain')
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
    parser_inline.add_argument('--port', type=pInt, default=587,
            help='the port for SMTP server, default=587')
    parser_inline.add_argument('--tlayer', default='tls',
            choices=['plain', 'ssl', 'tls'],
            help='transportation layer protocol when port is '
                 'not well-known, defaut=tls')
    parser_inline.add_argument('--timeout', type=int, default=3,
            help='connection timeout of smtp server, default=3s')
    parser_inline.add_argument('--debuginfo', action='store_true',
            help='show debug info between SMTP server and maily')
    # subcommand: infile
    parser_infile.add_argument('msgfile',
            help='msg file in json format')
    #
    args = parser.parse_args()
    if args.subcmd == 'inline':
        # check subject
        if args.subject.strip() == '':
            raise ValueError('subject option can not be empty.')
        # check content
        if hasattr(args, 'content'):  # argument --content is present
            # stdin must be empyt
            if len(sys.stdin.readlines()) != 0:
                raise ValueError('content conflict from both cmd argument '
                                 'and stdin.')
            # make \n to work, input is raw string
            args.content = args.content.replace('\\n','\n')
        else:
            setattr(args, 'content', ''.join(sys.stdin.readlines()))
        # check attachment list
        for item in args.attachment:
            if os.path.isfile(item) is False:
                raise ValueError('Attachement %s is not a file.' % item)
        # check addresses in to, cc, bcc and fromaddr
        for addr in args.to:
            if check_addr(addr) is False:
                raise ValueError('%s: address format error in --to list.'
                                  % addr)
        for addr in args.cc:
            if check_addr(addr) is False:
                raise ValueError('%s: address format error in --cc list.'
                                  % addr)
        for addr in args.bcc:
            if check_addr(addr) is False:
                raise ValueError('%s: address format error in -bcc list.'
                                  % addr)
        if check_addr(args.fromaddr) is False:
            raise ValueError('%s: address format error in --fromaddr.'
                              % args.fromaddr)
        # transportation layer
        if (args.port not in (25, 465, 587) and
            args.tlayer is None):
            raise ValueError('You have to set the --tlayer option, '
                             'since the customized port is used.')
        if ((args.port == 25 and args.tlayer != 'plain') or
            (args.port == 465 and args.tlayer != 'ssl') or
            (args.port == 587 and args.tlayer != 'tls')):
            raise ValueError('You use the well-known port, but the '
                             'corresponding --tlayer option is wrong.')
        # go
        msg, to = _get_msg_to(args.subject,
                              args.content,
                              args.contype,
                              args.attachment,
                              args.to,
                              args.cc,
                              args.bcc,
                              args.fromaddr)
        _server_send(args.smtp,
                     args.port,
                     args.timeout,
                     args.tlayer,
                     args.debuginfo,
                     args.fromaddr,
                     args.passwd,
                     to,
                     msg)
    else:  # infile
        # check json file, show and count
        with open(args.msgfile) as f:
            emd = json.load(f)
        enum = 0
        for i in range(len(emd)):
            enum += len(emd[i]['msg'])
        print(json.dumps(emd, indent=4))
        print('There are total [%d] emails need to be sent by [%d] accounts.'
               % (enum, len(emd)))
        # check contents of msg json file, set emd object
        for i in range(len(emd)):
            if "fromaddr" not in emd[i]:
                raise ValueError('fromaddr is not found in [%d] account.'
                                  %(i+1,))
            else:
                if check_addr(emd[i]['fromaddr']) is False:
                    raise ValueError('%s: address format error in fromaddr.'
                                      % emd[i]['fromaddr'])
            if "passwd" not in emd[i]:
                raise ValueError('passwd is not found in [%d] account.'
                                  %(i+1,))
            if "server" not in emd[i]:
                raise ValueError('server is not found in [%d] account.'
                                  %(i+1,))
            # the above three items are mandatory, and msg item.
            if "port" not in emd[i]:
                emd[i]['port'] = 587  # default
            if "connect" not in emd[i]:
                emd[i]['connect'] = 'tls'
            if "timeout" not in emd[i]:
                emd[i]['timeout'] = 3
            if "debuginfo" not in emd[i]:
                emd[i]['debuginfo'] = False
            if "interval" not in emd[i]:
                emd[i]['interval'] = 3
            # msg
            for j in range(len(emd[i]['msg'])):
                if "subject" not in emd[i]['msg'][j]:
                    raise ValueError('subject is missing in [%d] account, '
                                     'and [%d] email msg.'% (i+1,j+1))
                if "to" not in emd[i]['msg'][j]:
                    raise ValueError('to addr list is missing in [%d] account, '
                                     'and [%d] email msg.'% (i+1,j+1))
                else:
                    for addr in emd[i]['msg'][j]['to']:
                        if check_addr(addr) is False:
                            raise ValueError(
                                '%s: address format error in to list, '
                                'in [%d] account, [%d] email msg.'
                                % (addr, i+1, j+1))
                if "cc" not in emd[i]['msg'][j]:
                    emd[i]['msg'][j]['cc'] = []
                else:
                    for addr in emd[i]['msg'][j]['cc']:
                        if check_addr(addr) is False:
                            raise ValueError(
                                '%s: address format error in cc list, '
                                'in [%d] account, [%d] email msg.'
                                % (addr, i+1, j+1))
                if "bcc" not in emd[i]['msg'][j]:
                    emd[i]['msg'][j]['bcc'] = []
                else:
                    for addr in emd[i]['msg'][j]['bcc']:
                        if check_addr(addr) is False:
                            raise ValueError(
                                '%s: address format error in bcc list, '
                                'in [%d] account, [%d] email msg.'
                                % (addr, i+1, j+1))
                if "type" not in emd[i]['msg'][j]:
                    emd[i]['msg'][j]['type'] = 'plain'
                if "content" not in emd[i]['msg'][j]:
                    emd[i]['msg'][j]['content'] = ''
                if "attachment" not in emd[i]['msg'][j]:
                    emd[i]['msg'][j]['attachment'] = []
                else:
                    for item in emd[i]['msg'][j]['attachment']:
                        if os.path.isfile(item) is False:
                            raise ValueError(
                                    'Attachement %s is not a file, '
                                    'in [%d] account, [%d] email msg.'
                                    % (item, i+1, j+1))
        # send
        for i in range(len(emd)):
            server_hold = True
            for j in range(len(emd[i]['msg'])):
                if j+1 == len(emd[i]['msg']):
                    server_hold = False
                msg, to = _get_msg_to(emd[i]['msg'][j]['subject'],
                                      emd[i]['msg'][j]['content'],
                                      emd[i]['msg'][j]['type'],
                                      emd[i]['msg'][j]['attachment'],
                                      emd[i]['msg'][j]['to'],
                                      emd[i]['msg'][j]['cc'],
                                      emd[i]['msg'][j]['bcc'],
                                      emd[i]['fromaddr'])
                _server_send(emd[i]['server'],
                             emd[i]['port'],
                             emd[i]['timeout'],
                             emd[i]['connect'],
                             emd[i]['debuginfo'],
                             emd[i]['fromaddr'],
                             emd[i]['passwd'],
                             to,
                             msg,
                             server_hold)
                print('sent...[%d] account [%d] email msg' % (i+1,j+1))
                if i+1 != len(emd) and server_hold:
                    time.sleep(emd[i]['interval'])


if __name__ == '__main__':
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    main()



