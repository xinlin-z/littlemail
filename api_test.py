from littlemail import send_email


# Just fill the 4 line below and run,
# you can test send_email API provided by littlemail!:)
fromaddr = ''
to = ['']
smtp = ''
passwd = ''


send_email('send test', text='test email sent by littlemail!',
                        to=to,
                        fromaddr=fromaddr,
                        smtp=smtp,
                        passwd=passwd,
                        debug=True)

