# COSC6377-ComputerNetworks

# Reverse Proxy


# Running the system
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