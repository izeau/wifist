# wifist

A simple Python script to reconnect to Wifirst, based on [Wifirst_keepalive](/Tulux/Wifirst_keepalive) by [Tulux](/Tulux).

## usage

You may need to install `lxml` first, simply run `pip install lxml`.

```
usage: wifist.py [-h] [-v] [-d DELAY] login password

A simple script to reconnect to Wifirst.

positional arguments:
  login                 your Wifirst login (e-mail address)
  password              your Wifirst password

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         make me say stuff
  -d DELAY, --delay DELAY
                        delay between attempts, in seconds (default: 10)
```
