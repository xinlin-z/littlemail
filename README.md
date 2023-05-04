{toc}

# Intro

Maily is a command-line SMTP email sending tool in pure Python, which
send **one email per command**.

The purpose of maily is to have a very simple and easy-to-use
command-line SMTP email sending tool in pure Python.
(I think mail or mailx is a bit complicated in use.)

## Installation

```shell
$ pip3 install maily
```

## Usage

Show help and **default values** for a few options:

``` shell
$ python3 -m maily -h
```

Example:

```shell
$ python3 -m maily -s test -c hello -f 12345@qq.com --to 54321@qq.com -p abcde --smtp smtp.qq.com --protocol tls
```

`-c` is optional, which means you can send email with empty content.
And there are two other ways to fill content. Below are examples:

(1) By using echo and pipe, you can insert escape character in command line
into your content:

```shell
$ echo -e 'hello\n\nI am xinlin-z!\n\nBR\nxinlin-z' | python3 -m maily <...>
```

(2) By using input redirection:

```shell
$ python3 -m maily <...> < email.txt
```

`-a` option can accept more than one attachments, like:

```shell
$ python3 -m maily <...> -a afile.tar.gz bfile.py cfile.txt <...>
```

If there is something wrong, try to add `--debug` option to check.

Have fun! ^___^

