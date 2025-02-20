#!/usr/bin/env python3
"""
Command line SMTP email sending tool in Python!

Author:   xinlin-z
Github:   https://github.com/xinlin-z/littlemail
Blog:     https://cs.pynote.net
License:  MIT
"""
import os
import sys
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes


__all__ = ['send_email']


def _smtp_send(smtp: str,
               port: int,
               timeout: int,
               protocol: str,
               debug: bool,
               fromaddr: str,
               passwd: str,
               addrs: list[str],
               msg: MIMEMultipart) -> None:
    # server parameters
    param = {'host': smtp,
             'port': port,
             'timeout': timeout}
    # create server
    if port in (25, 465, 587):
        if port == 465:
            server = smtplib.SMTP_SSL(**param)  # type: ignore
        else:
            server = smtplib.SMTP(**param)      # type: ignore
    else:
        if protocol in ('plain', 'tls'):
            server = smtplib.SMTP(**param)      # type: ignore
        else:  # ssl
            server = smtplib.SMTP_SSL(**param)  # type: ignore
    # if print debug info
    if debug:
        if sys.version.split()[0][:3] >= '3.5':
            server.set_debuglevel(2)
        else:
            server.set_debuglevel(1)
    if port == 587 or protocol == 'tls':
        server.starttls()
    server.login(fromaddr, passwd)
    server.sendmail(fromaddr, addrs, msg.as_string())
    server.quit()


def _get_msg_addrs(subject: str,
                   text: str,
                   contype: str,
                   alist: list[str],
                   to: list[str],
                   cc: list[str],
                   bcc: list[str],
                   fromaddr: str) -> tuple[MIMEMultipart,list[str]]:
    # construct the mail
    msg = MIMEMultipart('mixed')
    msg.attach(MIMEText(text, contype, 'utf-8'))
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = ';'.join(to)
    msg['Cc'] = ';'.join(cc)
    # attachments
    for i in range(len(alist)):
        ftype, encoding = mimetypes.guess_type(alist[i])
        if (ftype is None
                or encoding is not None):
            ftype = 'application/octet-stream'
        maintype, subtype = ftype.split('/')
        att = MIMEBase(maintype, subtype)
        att.add_header('Content-Disposition','attachement',
                       filename=os.path.basename(alist[i]))
        att.add_header('Content-ID', '<%d>'%i)
        att.add_header('X-Attachment-Id', '<%d>'%i)
        with open(alist[i], 'rb') as f:
            att.set_payload(f.read())
        encoders.encode_base64(att)
        msg.attach(att)
    return msg, (to+cc)+bcc


def send_email(subject: str,
               *,
               text: str = '',
               contype: str = 'plain',
               alist: list[str] = [],
               to: list[str],
               cc: list[str] = [],
               bcc: list[str] = [],
               fromaddr: str,
               smtp: str,
               port: int = 587,
               timeout: int = 3,
               protocol: str = 'tls',
               passwd: str|None,
               debug: bool = False) -> None:
    """ sending email interface """
    # Since it could be called in code,
    # I put the parameters' checking here for both flow.

    # The default [] here is fine,
    # since there is no code to modify the default value.
    # It's either default [] or user input list.

    # subject
    subject = subject.strip()
    if subject == '':
        raise ValueError('Subject can not be empty.')

    # port and protocol
    if protocol not in ('plain','ssl','tls'):
        raise ValueError('Unkown protocol %s.' % protocol)
    if ((port == 25 and protocol != 'plain') or
            (port == 465 and protocol != 'ssl') or
            (port == 587 and protocol != 'tls')):
        raise ValueError('You use a well-known port, but the '
                         'corresponding protocol is wrong.')

    # attachment
    for f in alist:
        if os.path.isfile(f) is False:
            raise ValueError('Attachement %s is not a file.' % f)

    # password
    if not passwd:
        try:
            passwd = os.environ['LITTLEMAIL_PASSWD']
        except KeyError:
            raise ValueError('Password is missing.')
    passwd = passwd.strip()

    # get msg and To addresses
    msg, addrs = _get_msg_addrs(subject,
                                text,
                                contype,
                                alist,
                                to,
                                cc,
                                bcc,
                                fromaddr)
    # go
    _smtp_send(smtp,
               port,
               timeout,
               protocol,
               debug,
               fromaddr,
               passwd,
               addrs,
               msg)


_VER = 'littlemail V0.33 by xinlin-z'\
       ' (https://github.com/xinlin-z/littlemail)'


def _main() -> None:
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=_VER)
    parser.add_argument('-s', '--subject', required=True,
                        help='subject for this email')
    parser.add_argument('-c', '--content', default=argparse.SUPPRESS,
                        help='email content, may be empty')
    parser.add_argument('-t', '--contype', default='plain',
                        choices=['plain', 'html'],
                        help='content type, default is plain')
    parser.add_argument('-a', '--attachment', nargs='+', default=[],
                        help='attached files')
    parser.add_argument('--to', required=True, nargs='+',
                        help='address(es) of receivers')
    parser.add_argument('--cc', nargs='+', default=[],
                        help='address(es) of cc (carbon copy)')
    parser.add_argument('--bcc', nargs='+', default=[],
                        help='address(es) of bcc (blind carbon copy)')
    parser.add_argument('-f', '--fromaddr', required=True,
                        help='address of sender')
    parser.add_argument('-p', '--password',
                        help='password of sender email account')
    parser.add_argument('--smtp', required=True,
                        help='SMTP server of sender email account')
    parser.add_argument('--port', type=int, default=587,
                        help='port number of SMTP server, default is 587')
    parser.add_argument('--protocol', default='tls',
                               choices=['plain','ssl','tls'],
                    help='transportation layer protocol, default is TLS')
    parser.add_argument('--timeout', type=int, default=3,
                    help='connection timeout for smtp server, default is 3s')
    parser.add_argument('--debug', action='store_true',
                    help='show debug info between SMTP server and littlemail')
    args = parser.parse_args()

    # content
    # User input by -c is raw string, \n is 2 char, \\ and n.
    # By echo -e and file redirection, we get normal string.
    if not sys.stdin.isatty():
        if hasattr(args, 'content'):
            raise ValueError('--content(-c) option conflicts with '
                             'redirection. You cannot use both '
                             'simultaneously!')
        setattr(args, 'content', sys.stdin.read())
    else:
        if not hasattr(args, 'content'):
            args.content = ''

    send_email(subject=args.subject,
               text=args.content,
               contype=args.contype,
               alist=args.attachment,
               to=args.to,
               cc=args.cc,
               bcc=args.bcc,
               fromaddr=args.fromaddr,
               smtp=args.smtp,
               port=args.port,
               timeout=args.timeout,
               protocol=args.protocol,
               passwd=args.password,
               debug=args.debug)


if __name__ == '__main__':
    try:
        _main()
    except Exception as e:
        print(str(e))


