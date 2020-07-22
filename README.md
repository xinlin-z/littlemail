# maily
A cmd-line SMTP email sending tool in Python

The purpose of making maily is to have a very simple and easy-to-use cmd-line
SMTP email sending tool in pure Python. It's also my practice project.

I would get rid of complicated tools such as mail, mailx in Linux
unconsciously. So, please don't blame me.


## How to Use
There are enough info in help.

    $ pytyon3 maily.py -h
    $ python3 maily.py inline -h

### sub-command: inline
Maily will send a single email out in inline mode for each command.

    $ python3 maily.py inline --subject a_title --content test_content
      --to to@qq.com --fromaddr from@qq.com --passwd your_password
      --smtp smtp.qq.com

    You can also specify -a for attachments.
    The default --contype is plain.
    --cc and --bcc are for other receivers.
    The default --port is 587, you can also set it to 25 or 465.

    One more thing, there three ways to fill the email's content:
    (a), fill --content options in cmd-line;
    (b), $ python3 maily.py ..... < content.txt
    (c), $ echo your_content | python3 maily.py ...

## Version

* **2020-07-22 V0.16**
    - first release with inline sub-command



