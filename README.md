# Online Chat Assignment

This project revolves around implementing an online chat including reliable file transfer over udp using the knowledge we aquired during the Networking Course in Ariel-University.

## Introduction
First and foremost we implemented our online chat room is a server-multiple client application. The chat room allows sending and receiving messages over TCP connections. Each user may send messages to the entire chat room or private messages to other specific users. Furthermore, we were tasked with implementing reliable file transfer over UDP.
Reliable Data Transfer (RDT) over UDP (User Datagram Protocol), in our case data being files. The reliability is achieved using Sequence Numbering Protocol. Unlike TCP, UDP is an unreliable data transfer protocol in the transport layer. Our goal is transferring files fast and reliably over UDP connections.


#### Selective Repeat Protocol - SRP

By requesting a certain file the server transmits the relevant data for the download proccess, within that data the client finds the file size, he then knows to expect filesize/2048 amount of **different** packets heading his way. Each packet has that Sequence Number header, that way the client reveals which packets he gets and which packets are still missing. Using SRP protocol the client and server are communicating back and forth accordingly until the client receives every packet sequence starting with 01 up to the amount of total packets.

![segments drawio](https://user-images.githubusercontent.com/92747945/156886555-f774e33b-b04b-4066-beed-aaa5ab3c54e7.png)

## Reliable UDP

* We begin with the client sending the server the 
    file-request command.
* The server then sends the relevant data for the transfer process (aka File size, Available port, etc)
* Based on the data received from the server, the client then knows how many segments of data to look forward to.
* The server breaks the File's data into data segments.
    each segment consists of 2 bytes that represents the segment's sequence number (e.g 00,01,02,...,99) and another 2046 bytes of the file's data.
* According to the number of required segments, the client then sends which missing packets are needed to completely download the file.
* To which the server responds by sending back all of the missing segments that were sent by the client's request.
* This method prevents packet lose because the back and forth between the client and the server continues until the client recevied every segment.
* The two above stages works in a loop up until the client received all the data needed, when that happens the client sends 'check' message to the server to finish the download process.

#### Latency
The issue we had with latency was: missing packets messages were chained together as the client sent more requests then the server recevied, this caused the server to receive multiple packets requests at once which caused KeyErrors and wrong packet numbers. 

## Diagrams

### Messages Diagram:
![Messages](https://i.imgur.com/uHethui.jpeg)
### Download Diagram:
![Download process](https://i.imgur.com/dsZ4dhl.jpg)

## Features

- Sending messages to all existing members on the server or to one or more specific members.
- Downloading existing files from the server.


## Deployment
- Download the Code
- To run on Windows:
```sh
To run on localhost ignore the ip related instructions and enter 127.0.0.1 / 127.0.1.1 when requested to enter ip.
```
- Run Server.py.

![image](https://user-images.githubusercontent.com/92747945/156879417-456b1bc4-f2f2-4f3f-ab75-0cdd599032c9.png)

- Open cmd (on the server's computer), type ipconfig and look for your IPv4 address under Wireless Lan Adapter.

![image](https://user-images.githubusercontent.com/92747945/156879628-2d9a03c5-b1b8-448c-b815-5d658c283c21.png)

- Run Client.py (from any computer on the wifi network).

![image](https://user-images.githubusercontent.com/92747945/156879546-0d24a523-cb9e-44ed-95cd-b7f49e10a452.png)

- Enter the server's IPv4 address.

![image](https://user-images.githubusercontent.com/92747945/156879694-0d9ad4fc-30c9-4ccb-a10f-e0076ffb48f1.png)

- Enter your username.

![image](https://user-images.githubusercontent.com/92747945/156879703-ae48bfd2-d8d4-4d23-8a4f-07ae03ab3b33.png)

```sh
Make sure to run the server before the client.
Make sure to cd to src folder before running Server/Client.
On Linux the proccess is the same except the ipconfig command which is different, if you dont know the linux version of ipconfig, google it. :)
```

## Usage/Examples

Commands example:

![commandexamples](https://user-images.githubusercontent.com/92747945/156895426-37d2d076-ced8-4dba-88ef-ca2260dd416c.png)

https://user-images.githubusercontent.com/92747945/156892358-0d783984-f260-4715-a8a4-b65552770cd8.mp4

## Authors

- [@lior2k](https://www.github.com/lior2k)
- [@chai9l](https://www.github.com/chai9l)

