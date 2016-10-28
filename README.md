# Multi-part responses with asyncio

This example contains a UDP client that can await responses of requests by using `asyncio` if the responses come in multiple packets. The response packets need to contain a sequence number and a total number of packets.

Additionally, the client sends a request identifier that is sent back in the responses to assign the responses to the requests if multiple requests are executed at the same time.

The client waits for all response packets and sorts the response.

In this example, the server searches for the vowel contained in the message and sends back a packet per character that is a vowel. To simulate network troubles, the server shuffles the packets before sending.

## Basic usage

```python
# initialization
text = "Hello, please find my vowels!"
loop = asyncio.get_event_loop()
connect = loop.create_datagram_endpoint(MultipartUDPClient, remote_addr=("::1", 9999))
transport, protocol = loop.run_until_complete(connect)

# inside of a coroutine
async def do_something():
    vowel_positions = await protocol.request(text)
    for line in response:
        print(line)

# outside of a coroutine
vowel_positions = loop.run_until_complete(protocol.request(text))
for line in response:
    print(line)

# outside of a coroutine using a callback function
def callback(future):
    for line in future.result():
        print(line)
    asyncio.get_event_loop().stop()
future = asyncio.ensure_future(protocol.request(text))
loop.run_forever()
```

### Output
```
vowel e at position 1
vowel o at position 4
vowel e at position 9
vowel a at position 10
vowel e at position 12
vowel i at position 15
vowel o at position 23
vowel e at position 25
```

## Message format
request: `REQUEST:id:message`

response: `RESPONSE:id:seq:count:message`

* `id` is the request id that is sent back in responses
* `seq` is the sequence number of the response packet (from 0 to `count`-1)
* `count` is the total number of response packets
* `message` is the message to count the vowels

## Requirements

* Python ≥ 3.5 (uses `async`/`await`)

