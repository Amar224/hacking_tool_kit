#!/usr/bin/env python3

import logging

import click

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from habu.lib.iface import search_iface
from scapy.all import IP, TCP, RandShort, conf, send, sr1


@click.command()
@click.argument('ip')
@click.option('-p', 'port', default=80, help='Port to use (default: 80)')
@click.option('-c', 'count', default=5, help='How many packets to send/receive (default: 5)')
@click.option('-i', 'iface', default=None, help='Interface to use')
@click.option('-g', 'graph', is_flag=True, default=False, help='Graph (requires matplotlib)')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose output')
def cmd_tcp_isn(ip, port, count, iface, graph, verbose):
    """Create TCP connections and print the TCP initial sequence
    numbers for each one.

    \b
    $ sudo habu.tcp.isn -c 5 www.portantier.com
    1962287220
    1800895007
    589617930
    3393793979
    469428558

    Note: You can get a graphical representation (needs the matplotlib package)
    using the '-g' option to better understand the randomness.
    """

    conf.verb = False

    if iface:
        iface = search_iface(iface)
        if iface:
            conf.iface = iface['name']
        else:
            logging.error('Interface {} not found. Use habu.interfaces to show valid network interfaces'.format(iface))
            return False

    isn_values = []

    for _ in range(count):
        pkt = IP(dst=ip)/TCP(sport=RandShort(), dport=port, flags="S")
        ans = sr1(pkt, timeout=0.5)
        if ans:
            send(IP(dst=ip)/TCP(sport=pkt[TCP].sport, dport=port, ack=ans[TCP].seq + 1, flags='A'))
            isn_values.append(ans[TCP].seq)
            if verbose:
                ans.show2()

    if graph:

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("To graph support, install matplotlib")
            return 1

        plt.plot(range(len(isn_values)), isn_values, 'ro')
        plt.show()

    else:

        for v in isn_values:
            print(v)

    return True


if __name__ == '__main__':
    cmd_tcp_isn()
