# Reliable File Transfer with UDP

### How does it work

To run the project on an isolated environment check the instructions at the end of the page.

Server is run with 
```
python3 server.py <result file> <timeout_limit> <window_size>
```

For test cases usually selected 0.005 time limit and 300 as window size.

Client is run with
```
python3 client.py
```

It uses Selective Repeat algorithm for ensuring the reliability. Accepts individual ACK’s for sent packets and slides the window as lowest sequenced numbers in window receives ACK’s.

For client to start listening and server to start sending files both must ensure that connection happened successfully. For this purpose it first makes a three way handshake. Then the server gets to the sending state and the client gets to the listening state. With this approach both get aware of each other’s state.

After the handshake it uses a multithreaded approach for listening to the ACK’s and sending files. One thread is only assigned for listening ACK’s and there are fmy threads assigned for sending packets. Used mutexes and locks, mutexes are assigned when looping window in sending threads and released on new ACK receives and listening timeouts.

There is a ServerFile object which parses files into packets and assign headers to it, it tracks ACK’s and window place for individual files. When a file is completely received it writes the file into objects/ folder.

How is it solving the Head of Line Blocking problem?

It is sending packets of multiple files concurrently. While it is sending a large object it is also sending a small object alongside. So that small objects are not waiting for large objects to finish. Since they are much smaller, usually before it finishes sending a full large file, it sends most of the small objects.

During the three way handshake server sends the metadata about files. So that client know what it will be receiving and constructs file objects.


TCP version

Server is run with 
```
python3 server.py <result file>
```

Client is run with
```
python3 client.py
```

# Test Results and Conclusion

## Packet Loss tests

![Screenshot 2024-01-09 at 15-47-00 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/40d47df9-3a76-44c5-89f6-b1920fff491a)

Here is the visual for packet loss execution times for UDP and TCP implementations. When there is zero delay TCP is much faster but as packets get’s lost my Selective Repeat algorithm starts to perform better. Reason for it is that my algorithm accepts individual ACK’s and starts sending new packets as ACK’s are received. So when packets get delayed it doesn’t wait for whole window to receive ACK instead it slides the window. So losing packets affects the UDP implementation less. TCP uses a mix of GBN and SR algorithms. It uses cumulative ACK’s, it does not send already ACK’d packets and buffers them. This approach is good for not sending unrelated packets but has negative performance when there are packet losses waiting for all window to be received.

### Confidence Intervals (95%)

### UDP:
![Screenshot 2024-01-09 at 15-48-11 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/3bfc3ebe-9ab7-4d78-a353-f27629a8f273)

### TCP:
![Screenshot 2024-01-09 at 15-48-40 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/835ddb4c-eb93-4642-9af1-4c99813fa9d6)

## Packet Corrupt Tests
![Screenshot 2024-01-09 at 15-51-48 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/46274722-86d9-45be-875b-627d14ec4bfb)

My approach relies on Internet checksum. Sending md5 hash of each packet was too costly. After the receive of whole files it calculates the md5 hash of the file and compares it with the checksum. During all of my tests I did not encounter a miss checksum.

As mentioned TCP is working much faster on benchmark since it is data flowing without any interrupt. It accepts cumulative ACK’s which makes it much faster because for my implementation to finish it must receive all individual ACK’s but on TCP it can get cumulative ACK’s and discard earlier ACK’s. This makes it much faster when everything working perfectly.

Similar conclusions were made with packet loss. Since individual ACK’s make window slide better on packet corruptions it does not affect other packets to be sent and my approach keeps sending new packets as lowest number in window get’s ACK’ed. On the other hand TCP uses cumulative ACK’s and waits for window packets to be received until sliding the window.

## Confidence Intervals (95%)

### UDP:
![Screenshot 2024-01-09 at 15-54-18 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/6ee78730-a10d-4fd3-930f-846025de8a3a)

### TCP:
![Screenshot 2024-01-09 at 15-54-49 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/a03a8bb5-e2cd-4acf-9b11-2c6f5592e45b)

## Packet Duplicate Test
![Screenshot 2024-01-09 at 15-55-25 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/34f3e24d-09b5-4b23-9d85-154b99ed0383)

Packet duplicates are simply disregarded on TCP so it works as close as a benchmark case. 

my implementation also disregards packet duplicates and gives very close results to benchmark values. As duplication increases client and server gets to handle more packets. What’s changing here is that it is making each other to send unnecessary ACK’s sometimes. These make it a slightly slower than benchmark values.


## Confidence Intervals (95%):

### UDP:
![Screenshot 2024-01-09 at 15-56-42 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/08ce2a6a-1339-4177-baab-a2ff479d7d27)

### TCP:
![Screenshot 2024-01-09 at 15-57-04 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/455e05e0-d368-4835-956e-7ecc3f006781)


## Benchmark Test:
![Screenshot 2024-01-09 at 15-57-40 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/a73ed067-bd36-49d8-9ea8-34dd96947aed)

TCP is much faster on perfect conditions as mentioned earlier. It is accepting cumulative ACK’s and since packets dont get lost or corrupted it is working without any disruption and one ACK signal for whole window is sufficient. On the other hand UDP needs to process every individual ACK, although it continues to send packets.

## Delay Test:
![Screenshot 2024-01-09 at 15-58-53 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/c35d2157-fa77-44d3-a5b2-ccf29a4dcebd)

On delayed packets case TCP gets delayed as expected but this time my implementation does not get to pass it in performance it also gets delayed. I compared it with the loss case to understand the reason for the change in this graph. For example when a packet is lost my implementation timeout works and it sends the packet again it keeps doing it whenever the timeout runs until it receives an ACK for it. When there is 10% packet loss even if a packet is lost if the timeout is small it sends back the packet in a short time and it is very much likely that it will receive an ACK the second or third time. So the delay would be only a maximum of 2-3 times the timeout I set in my server for a packet. 

On the other hand when there is only delay my server will not receive an ACK in the given time, and it will send the packet again but the problem is that, the next packet will also be delayed. As the delay increases my implementation will work slowly.
So having a short timeout is not a good effect in here.Since I did not implement a dynamic timeout and window size deciding algorithm I run these tests under the same conditions. 

## Confidence Intevals (%95):

### UDP:
![Screenshot 2024-01-09 at 16-01-21 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/0790866e-8383-4e40-8792-44cd87602eea)

### TCP:
![Screenshot 2024-01-09 at 16-01-43 Adsız doküman](https://github.com/onuruci/file-transfer/assets/63292060/7986c683-6009-43e3-b05b-11a4234c1b88)




# How to run
This assignment is initially cloned from https://github.com/cengwins/ceng435.

Install docker and VSCode on your sytstem

Go to your favorite development folder on your local machine and run

```
   git clone https://github.com/cengwins/ceng435.git
```

Open this folder (ceng435) in VSCode

Open a terminal in VSCode, under the ceng435 directory where the Dockerfile resides run

```
   docker build -t ceng435 .
```

After the image is built

You can run the following to get the server machine
```
   docker run -t -i --rm --privileged --cap-add=NET_ADMIN --name ceng435server -v ./code:/app:rw ceng435:latest bash
```

and the following for the client machine

```
   docker run -t -i --rm --privileged --cap-add=NET_ADMIN --name ceng435client -v ./code:/app:rw ceng435:latest bash
```

and you will be in your Ubuntu 22.04 Docker instance (python installed). Note that if you develop code in these Docker instances, if you stop the machine your code will be lost. That is why I recommend you to use Github to store your code and clone in the machine, and push your code to Github before shutting the Docker instances down. The other option is to work in the /app folder in your Docker instance is mounted to the "code" directory of your own machine.

**IMPORTANT** Note that the "code" folder on your local machine is mounted to the "/app" folder in the Docker instance  (read/write mode). You can use these folders (they are the same in fact) to develop your code. Other than the /app folder, this tool does not guarantee any persistent storage: if you exit the Docker instance, all data will be lost.

After running the Ubuntu Docker, you can type "ip addr" to see your network configuration. Work on eth0.

Docker extension of vscode will be of great benefit to you.

In the server terminal, move to the **"objects" folder** and run

```
   ./generateobjects
```

to generate 10 small (10K) and 10 large (10M) objects together with their md5 checksums.

Some tc commands that may be of help to you can be found at https://man7.org/linux/man-pages/man8/tc-netem.8.html and https://www.cs.unm.edu/~crandall/netsfall13/TCtutorial.pdf

You will analyze the impact of delay, packet loss percentage, corrupt packet percentage, duplicate percentage, reorder percentage on the total time to download all 20 objects. You will plot figures for each parameter (delay, loss, ...) where the x-axis of the figure will have various values for these parameters and the y-axis will be the total time to download 20 objects. There will be two curves in each figure, one for TCP and the other curve for your UDP-based RDT implementation together with interleaving technique.



