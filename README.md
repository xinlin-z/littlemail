* [maily](#maily)
    * [How to Use](#How-to-Use)
    * [Example](#Example)

# maily

A command-line SMTP email sending tool in Python, which send **one email per
command**.

The purpose of maily is to have a very simple and easy-to-use
command-line SMTP email sending tool in pure Python. (I think mail or mailx
is a bit complicated in use.)

## How to Use

``` shell
$ python3 maily.py -h
```

> Please be aware of the default values for options!

## Example

> Some important options are not showed in the examples below!

``` shell
$ python3 maily.py -s 'hi maily' --to to@address.com \
> --fromaddr from@address.com --passwd here_is_passwor \
> --smtp smtp.server.com \
> -c 'your email content goes here!'
```

`maily` also support to fill the content through pipe:

``` shell
$ echo -e 'your content goes here:\n how are you?' | python3 maily.py \
> -s 'hi maily' --to to@address.com --fromaddr from@address.com \
> --passwd here_is_passwor --smtp smtp.server.com 
```

Or:

``` shell
$ python3 maily.py -s 'hi maily' --to to@address.com \
> --fromaddr from@address.com --passwd here_is_passwor \
> --smtp smtp.server.com < email_content.txt
```

Have fun! ^___^


