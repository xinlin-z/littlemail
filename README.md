# maily
A cmd-line SMTP email sending tool in Python

The purpose of making maily is to have a very simple and easy-to-use cmd-line
SMTP email sending tool in pure Python. It's also my practice project.

I would get rid of complicated tools such as mail, mailx in Linux
unconsciously. So, please don't blame me.

**中文参考：https://www.pynote.net/archives/2308**

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
    The default --contype is plain, html is also support.
    --cc and --bcc are for other receivers.
    The default --port is 587, you can also set it to 25, 465 or others, with
    --tlayer option if needed.

    One more thing, there three ways to fill the email's content:
    (a), fill --content options in cmd-line;
    (b), $ python3 maily.py ..... < content.txt
    (c), $ echo your_content | python3 maily.py ...

### sub-command: infile

    $ python3 maily.py infile msg.json

    All of the parameters needed are in a single json file. msg.json is
    an example for you. Some items in json are optional.
    So, if you put more than one msg under one account, or you set more
    than one account, you will get batch mode. The SMTP server will hold
    automatically until the last msg for each account.

## Version

* **2020-09-08 V0.19**
    - bugfix version

* **2020-08-21 V0.18**
    - add infile sub-command
    - refactor and bugfix

* **2020-07-24 V0.17**
    - add --tlayer option in inline sub-command to support customized port
    - bugfix

* **2020-07-22 V0.16**
    - first release with inline sub-command



