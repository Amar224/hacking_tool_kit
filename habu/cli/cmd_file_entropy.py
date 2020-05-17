#!/usr/bin/env python3

import click
#import matplotlib #.pyplot.hist
#from habu.lib.xor import xor
import matplotlib.pyplot as plt

@click.command()
#@click.option('-k', default='0', help='Encryption key')
@click.option('-i', type=click.File('rb'), default='-', help='Input file (default: stdin)')
@click.option('-o', type=click.File('wb'), default='-', help='Output file (default: stdout)')
def cmd_file_entropy(i, o):
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

    #for b in i.read():
    #    print(b)
    #    #print(int.from_bytes(b, byteorder='big'))

    oc = { i:0 for i in range(0,256) }

    for b in [x for x in i.read()]:
        oc[b] += 1

    for k,v in sorted(oc.items(), key=lambda item: item[1]):
        print(k, v)

    plt.hist(oc.values(), bins=256, range=(0, 256), histtype='step')
    plt.show()



if __name__ == '__main__':
    cmd_file_entropy()

