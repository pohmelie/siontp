import socket
import time
import asyncio

from .protocol import Packet


DEFAULT_NTP_SERVER = "pool.ntp.org"


def request(host=DEFAULT_NTP_SERVER, port="ntp", *, timeout=10,
            family=socket.AF_INET):
    sockaddr = socket.getaddrinfo(host, port)[0][4]
    try:
        s = socket.socket(family, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.sendto(Packet(transmit_timestamp=time.time()).to_bytes(), sockaddr)
        while True:
            response_packet, src_addr = s.recvfrom(256)
            if src_addr[0] == sockaddr[0]:
                break
    finally:
        s.close()
    p = Packet.from_bytes(response_packet)
    p.destination_timestamp = time.time()
    return p


class _NTPClientProtocol(asyncio.DatagramProtocol):

    def __init__(self, sockaddr):
        self.result = asyncio.Future()
        self.sockaddr = sockaddr

    def connection_made(self, transport):
        self.transport = transport
        data = Packet(transmit_timestamp=time.time()).to_bytes()
        self.transport.sendto(data, self.sockaddr)

    def datagram_received(self, data, addr):
        if addr[0] != self.sockaddr[0]:
            return
        self.result.set_result(data)
        self.transport.close()


async def arequest(host=DEFAULT_NTP_SERVER, port="ntp", *, timeout=10,
                   family=socket.AF_INET):
    coro = _arequest(host, port, family=family)
    return await asyncio.wait_for(coro, timeout)


async def _arequest(host, port="ntp", *, family=socket.AF_INET):
    loop = asyncio.get_event_loop()
    try:
        import aiodns
        resolver = aiodns.DNSResolver(loop=loop)
        ip = (await resolver.gethostbyname(host, family=family)).addresses[0]
        if port == "ntp":
            port = 123
        sockaddr = (ip, port)
    except ImportError:
        sockaddr = (await loop.getaddrinfo(host, port))[0][4]
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: _NTPClientProtocol(sockaddr),
        remote_addr=sockaddr,
        family=family,
    )
    try:
        p = Packet.from_bytes(await protocol.result)
    finally:
        transport.close()
    p.destination_timestamp = time.time()
    return p
