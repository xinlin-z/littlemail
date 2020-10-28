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

You can also specify -a for one or more attachments.
The default --contype is plain, html is supported and you are
responsible to feed html string for --content.
--cc and --bcc are for other receivers, optional.
The default --port is 587, you can also set it to 25, 465 or others,
with --tlayer option if needed.

One more thing, there are two ways to fill the email's content:

(a), fill --content in cmd line;

(b), use pipe:

    $ python3 maily.py ..... < content.txt
    $ echo your_content | python3 maily.py ...

help info for inline:

    $ python3 maily.py inline -h

### sub-command: infile

    $ python3 maily.py infile msg.json

All of the parameters needed are in a single JSON file.
File msg.json in this repo is an example for you.
If you put more than one email in one account, or you gather more
than one account in your json file, you get Batch Mode. In these
cases, the SMTP server will be hold automatically until the last email
sended for each account.

## Version

* **2020-10-28 V0.21**
    - even more checks for infile
    - change type to contype for infile

* **2020-10-09 V0.20**
    - more check done to json file for infile subcommand
    - change content to an array of string for infile subcommand

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



