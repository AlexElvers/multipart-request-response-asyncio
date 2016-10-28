#!/usr/bin/env python

import asyncio
import random
import string


class MultipartUDPClient(asyncio.DatagramProtocol):
    """
    Count vowels in a string.

    The client sends requests via UDP and receives one packet per vowel. The
    packets are numbered sequentially.

    The inheritance of DatagramProtocol is not important as it contains empty
    methods.

    Data formats:
    request: REQUEST:id:message
    response: RESPONSE:id:seq:count:message
    """

    def __init__(self):
        # response id -> sequence number -> message
        self.response_cache = {}
        # response id -> Future
        self.response_futures = {}

    def connection_made(self, transport):
        self.transport = transport

    def create_request_id(self, length=4):
        """
        Create a request identifier.
        """
        while True:
            request_id = "".join(random.choice(string.ascii_letters) for i in range(length))
            if request_id not in self.response_cache:
                return request_id

    async def request(self, message):
        """
        Create and send a request.

        Returns the response messages as a list.
        """
        request_id = self.create_request_id()
        self.response_cache[request_id] = {}
        self.response_futures[request_id] = future = asyncio.Future()

        # send request
        request = "REQUEST:{}:{}".format(request_id, message)
        print("Send {!r} to {}".format(request, self.transport.get_extra_info("peername")))
        self.transport.sendto(request.encode())

        # wait for response
        try:
            await future  # waiting for set_result
            responses = list(x[1] for x in sorted(self.response_cache[request_id].items()))
        finally:
            # ignore later responses
            del self.response_cache[request_id]
            del self.response_futures[request_id]
        return responses

    def datagram_received(self, data, addr):
        # data received, parse response
        response = data.decode()
        print("Received {!r} from {}".format(response, addr))
        if response.count(":") < 4:
            print("wrong response format")
            return
        response_type, response_id, response_sequence, response_count, response_message = response.split(":")
        if response_type != "RESPONSE":
            print("wrong response format")
            return

        # ignore responses of canceled requests
        if response_id not in self.response_cache:
            return
        # fill cache
        self.response_cache[response_id][int(response_sequence)] = response_message
        # finish response when all response packets are received
        if len(self.response_cache[response_id]) == int(response_count):
            self.response_futures[response_id].set_result(None)


def main():
    loop = asyncio.get_event_loop()
    print("Starting UDP client")
    connect = loop.create_datagram_endpoint(MultipartUDPClient, remote_addr=("::1", 9999))
    transport, protocol = loop.run_until_complete(connect)

    try:
        response = loop.run_until_complete(protocol.request("Hello, please find my vowels!"))
        for line in response:
            print(line)
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


if __name__ == "__main__":
    main()
