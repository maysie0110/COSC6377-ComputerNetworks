# HW2 - Analysis and Writing

### Mai Trinh

For detail report, please check COSC_6377_HW2.pdf

## Running the system
This is a Linux-based system.
To setup the network, run the server first using the following command
```
python server.py
```

Then run the clients. To run Python script, use the following command

```
python client-default.py
python client.py
```

To run Java script, use the following command. Note this should be run from the root directory, not from the HW2 directory.

```
java HW2.client
java HW2.clientDefault
```

The results of headers is logged in log.txt file.

## Limitations

This application is running in local network on port 8001 (i.e. http://127.0.0.1:8001).