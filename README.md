# Online Chat Assignment

This project revolves around implmenting an online chat using the knowledge we aquired during the Networking Course in Ariel-University.

## Diagrams

![Messages](https://i.imgur.com/oHGT8sS.jpg)
![Download process](https://i.imgur.com/dsZ4dhl.jpg)

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

## Features

- Sending messages to all existing members on the server or to one or more specific members.
- Downloading existing files from the server.



## Deployment

To deploy this project run

```bash
  npm run deploy
```


## Usage/Examples

here we add videos


## Authors

- [@lior2k](https://www.github.com/lior2k)
- [@chai9l](https://www.github.com/chai9l)

## Appendix

Any additional information goes here
