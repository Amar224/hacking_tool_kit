#!/usr/bin/env python3

import click

from habu.lib.xor import xor


@click.command()
@click.option('-k', default='0', help='Encryption key')
@click.option('-i', type=click.File('rb'), default='-', help='Input file (default: stdin)')
@click.option('-o', type=click.File('wb'), default='-', help='Output file (default: stdout)')
def cmd_crypto_xor(k, i, o):
    """XOR cipher.

    Note: XOR is not a 'secure cipher'. If you need strong crypto you must use
    algorithms like AES. You can use habu.fernet for that.

    Example:

    \b
    $ habu.xor -k mysecretkey -i /bin/ls > xored
    $ habu.xor -k mysecretkey -i xored > uxored
    $ sha1sum /bin/ls uxored
    $ 6fcf930fcee1395a1c95f87dd38413e02deff4bb  /bin/ls
    $ 6fcf930fcee1395a1c95f87dd38413e02deff4bb  uxored
    """

    o.write(xor(i.read(), k.encode()))


if __name__ == '__main__':
    cmd_crypto_xor()

