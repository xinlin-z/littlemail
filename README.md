[![MasterUpdate](https://github.com/xinlin-z/littlemail/actions/workflows/master_update.yml/badge.svg?branch=master)](https://github.com/xinlin-z/littlemail/actions/workflows/master_update.yml)

# littlemail

* [Installation](#Installation)
* [Usage](#Usage)
* [API](#API)

Littlemail is a straight-forward command-line SMTP email sending tool
in Python, which sends **one email per command**. (If you send many
emails, every sending will make a new connection with the smtp server.)

## Installation

```shell
$ pip install littlemail
```

## Usage

There is no way to reduce parameters provided in command-line, since
that's the way of email. So, please refer to the inline help for options
you need. Fortunately, many options have default value.

``` shell
$ python -m littlemail -h  # inline help
```

Anyway, here is a minimal example and a few lines of explanation:

```shell
$ python -m littlemail -s test [-c hello] \
                -f 12345@qq.com \
                --to 54321@qq.com \
                --smtp smtp.qq.com [-p abcdefg]
```

`-c` means the email content, which is optional. That means you can
send empty-content email. And this optional parameter enables the
capability of littlemail to get content from pipe (input
redirection), which might be easier for you to construct your message,
such as:

```shell
$ python -m littlemail <...> < my_email_content.txt
```

`-s` represents subject, which is mandatory and cannot be empty.

`-p` stands for password, and it is optional. When it's missing,
littlemail tries to get password from `LITTLEMAIL_PASSWD`
environment variable.

When something goes wrong, try `--debug`.

## API

There is an API you can invoke to send email in your code:

```python
# import
from littlemail import send_email
# signature
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
               debug: bool = False) -> None: ...
```

`api_test.py` is used as an example and testcase for you to try,
have fun! ^___^

