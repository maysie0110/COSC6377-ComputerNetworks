# HW1 - Reverse Proxy

### Mai Trinh


## Reverse Proxy

This is a single reverse proxy system that deal with multiple clients and multiple servers. The clients send JSON messges to reverse proxy identifies a specific privacy policy and the reverse proxy forwards the messages to the appropriate server. When the server receives the message, it computes the SHA1 hash of the message and send it back with the ACK to the reverse proxy and the proxy sends it back to the client.

Reverse proxy employed load balancing system usings threading.

## Running the system
This is a Linux-based system.
To setup the network, run the reverse proxy first using the following command
```
python revproc.py -port <<WELL-KNOWN-PORT>>

Example: python revproc.py -port 123
```

Then run the servers. Run this command in different terminals with different SERVER-ID and SERVER-PORT to create multiple servers

```
python server.py -id <<SERVER-ID>> -pp <<POLICY-ID>> -listen <<SERVER-PORT>> -revproc <<PROXY-PORT>>
Example: python server.py -id 1 -pp PP_1 -listen 100 -revproc 123
```

Finally, run the clients. Run this command in different terminals with variying CLIENT-ID and FILE-NAME to test multiple clients connection.

```
python client.py -id <<CLIENT-ID>> -revproc <<PROXY-PORT>> -pkt <<JSON-FILE-NAME>>

Example: python client.py -id 50 -revproc 123 -pkt 1335.PP_1
```

Note that for this assignment, please put the JSON file to be used in test-payloads folder.
```
Example: \test-payloads\1335.PP_1.json
```

## Limitations and Observations

There are limitations in which the system responds poorly when all servers are busy. 
This system assumes that a server does not disconnect and switch to a different policy and reconnect to reverse proxy.
There is a weird bug. Sometime, the connection between reverse proxy and server shows an error 
```
[Errno 54] Connection reset by peer
```
Not entirely sure what caused the connection to reestablished. However, it does transmit the messages like normal.