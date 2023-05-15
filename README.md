[![MasterUpdate](https://github.com/xinlin-z/littlemail/actions/workflows/master_update.yml/badge.svg?branch=master)](https://github.com/xinlin-z/littlemail/actions/workflows/master_update.yml)

* [Intro](#Intro)
* [Installation](#Installation)
* [Usage](#Usage)
* [API](#API)

# Intro

Littlemail is a command-line SMTP email sending tool in pure Python, which
send **one email per command**.

The purpose of this repo is to have a very simple and easy-to-use
command-line SMTP email sending tool in pure Python.
(I think mail or mailx is a bit complicated in use.)

# Installation

```shell
$ pip install littlemail
```

# Usage

Show help and **default values** for a few options:

``` shell
$ python -m littlemail -h
```

Example:

```shell
$ python -m littlemail -s test -c hello -f 12345@qq.com --to 54321@qq.com -p abcde --smtp smtp.qq.com --protocol tls
```

`-c` is optional, which means you can send email with empty content.
And there are two other ways to fill content. Below are examples:

(1) By using echo and pipe, you can insert escape character in command line
into your content:

```shell
$ echo -e 'hello\n\nI am xinlin-z!\n\nBR\nxinlin-z' | python -m littlemail <...>
```

(2) By using input redirection:

```shell
$ python -m littlemail <...> < email.txt
```

`-a` option can accept more than one attachments, like:

```shell
$ python -m littlemail <...> -a afile.tar.gz bfile.py cfile.txt <...>
```

If there is something wrong, try to add `--debug` option to check.

`--to`, `--cc` and `--bcc` options are all support multiple addresses.

`-p` is optional. When it's missing, littlemail tries to get password from
`LITTLEMAIL_PASSWD` environment variable.

# API

There is an API you can invoke to send email in your code:

```python
from littlemail import send_email
```

Have fun! ^___^

