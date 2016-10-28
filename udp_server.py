#!/usr/bin/env python3

import asyncio
import random
import time


class MultipartUDPServer(asyncio.DatagramProtocol):
    """
    Count vowels in a string.

    The server receives requests via UDP and responds one packet per vowel.
    The packets are numbered sequentially.

    The inheritance of DatagramProtocol is not important as it contains empty
    methods.

    Data formats:
    request: REQUEST:id:message
    response: RESPONSE:id:seq:count:message
    """

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # data received, parse request
        request = data.decode()
        print("Received {!r} from {}".format(request, addr))
        if request.count(":") < 2:
            print("wrong request format")
            return
        request_type, request_id, request_message = request.split(":", 2)
        if request_type != "REQUEST":
            print("wrong request format")
            return

        # find vowel positions
        response_messages = []
        for pos, char in enumerate(request_message):
            if char.lower() in "aeiou":
                response_messages.append("vowel {} at position {}".format(char, pos) + "\n" * request.endswith("\n"))
        response_type, response_id = "RESPONSE", request_id
        response_count = len(response_messages)

        # simulate packets not in sequence
        response_messages = list(enumerate(response_messages))
        random.shuffle(response_messages)

        # send response
        for response_sequence, response_message in response_messages:
            time.sleep(.1)  # slow down
            response = ":".join(map(str, (response_type, response_id, response_sequence, response_count, response_message)))
            print("Send {!r} to {}".format(response, addr))
            self.transport.sendto(response.encode(), addr)


def main():
    loop = asyncio.get_event_loop()

    print("Starting UDP server")
    listen = loop.create_datagram_endpoint(MultipartUDPServer, local_addr=("::1", 9999))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


if __name__ == "__main__":
    main()
