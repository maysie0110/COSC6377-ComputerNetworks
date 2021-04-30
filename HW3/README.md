# HW3 - AWS EC2 Instance

### Mai Trinh

## Reverse Proxy

This is a single reverse proxy system that deal with multiple clients and multiple servers. The clients send JSON messges to reverse proxy identifies a specific privacy policy and the reverse proxy forwards the messages to the appropriate server. When the server receives the message, it computes the SHA1 hash of the message and send it back with the ACK to the reverse proxy and the proxy sends it back to the client.

Reverse proxy employed load balancing system usings threading.

## Deploy code to AWS EC2 Instances
More details in the report