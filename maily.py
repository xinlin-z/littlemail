#!/usr/bin/env python3
"""
Command line SMTP email sending tool in pure Python!

Author:   xinlin-z
Github:   https://github.com/xinlin-z/maily
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
    if debug:
        if sys.version.split()[0][:3] >= '3.5':
            server.set_debuglevel(2)
        else: server.set_debuglevel(1)
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
    to.extend(cc)
    to.extend(bcc)
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
    return msg, to


def send_email(*,
               subject: str,
               text: str,
               contype: str,
               alist: list[str],
               to: list[str],
               cc: list[str],
               bcc: list[str],
               fromaddr: str,
               smtp: str,
               port: int,
               timeout: int,
               protocol: str,
               passwd: str,
               debug: bool) -> None:
    """ Sending Email """
    msg, addrs = _get_msg_addrs(subject,
                                text,
                                contype,
                                alist,
                                to,
                                cc,
                                bcc,
                                fromaddr)
    _smtp_send(smtp,
               port,
               timeout,
               protocol,
               debug,
               fromaddr,
               passwd,
               addrs,
               msg)
    return


_VER = 'V0.31 by xinlin-z with love'\
       ' (https://github.com/xinlin-z/maily)'


def _main() -> None:
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version=_VER)
    parser.add_argument('-s', '--subject', required=True,
                        help='subject for this email')
    parser.add_argument('-c', '--content', default=argparse.SUPPRESS,
                        help='email content, empty is allowed')
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
                        help='port for SMTP server, default is 587')
    parser.add_argument('--protocol', default='tls',
                               choices=['plain','ssl','tls'],
                    help='transportation layer protocol, default is TLS')
    parser.add_argument('--timeout', type=int, default=3,
                    help='connection timeout for smtp server, default is 3s')
    parser.add_argument('--debug', action='store_true',
                    help='show debug info between SMTP server and maily')
    args = parser.parse_args()

    # subject
    if args.subject.strip() == '':
        raise ValueError('--subject(-s) option can not be empty.')

    # content
    # User input by -c is raw string, \n is 2 char, \\ and n.
    # By echo -e and file redirection, we get normal string.
    if not sys.stdin.isatty():
        if hasattr(args, 'content'):
            raise ValueError('--content(-c) option conflicts with '
                             'redirection. You cannot use both!')
        setattr(args, 'content', sys.stdin.read())
    else:
        if not hasattr(args, 'content'):
            args.content = ''

    # attachment
    for item in args.attachment:
        if os.path.isfile(item) is False:
            raise ValueError('Attachement %s is not a file.' % item)

    # transportation layer
    if (args.port not in (25, 465, 587) and
            args.tlayer is None):
        raise ValueError('You have to set the --protocol option, '
                         'since the customized port number is specified.')
    if ((args.port == 25 and args.protocol != 'plain') or
            (args.port == 465 and args.protocol != 'ssl') or
            (args.port == 587 and args.protocol != 'tls')):
        raise ValueError('You use the well-known port, but the '
                         'corresponding --protocol option is wrong.')

    # password
    if args.password is None:
        try:
            args.password = os.environ['MAILY_PASSWD']
        except KeyError:
            raise ValueError('Password is missing.')
    args.password = args.password.strip()

    # good to go
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
    # msg, addrs = _get_msg_addrs(args.subject,
    #                             args.content,
    #                             args.contype,
    #                             args.attachment,
    #                             args.to,
    #                             args.cc,
    #                             args.bcc,
    #                             args.fromaddr)

    # _smtp_send(args.smtp,
    #              args.port,
    #              args.timeout,
    #              args.protocol,
    #              args.debug,
    #              args.fromaddr,
    #              args.password,
    #              addrs,
    #              msg)


if __name__ == '__main__':
    try:
        _main()
    except Exception as e:
        print(str(e))


