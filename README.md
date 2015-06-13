# "pipedream" fuzzer
The pipedream proxy is a pure-python single-threaded proxy server, designed to
capture traffic and replay it with modifications, to identify vulnerabilities
in both networked and desktop software.

In it's 'capture' mode, this captures a socket conversation as a .cnv file,
which can then be used in the 'replay' mode to simulate a client, as well as
a 'fuzz' mode to inject random faults. A 'data editor' is also included
which can be used to edit captured conversations before use.

*Note: it is strongly recommended that a fuzz file be edited before trying to
emulate a server*

## basic use (no fuzzing)
The first step of using the fuzzer is to capture a socket conversation. This
is done with the "capture" mode, which sets up a socket proxy, as follows. The
example below captures traffic to the google web server, without 

    pipedream.py -m capture -i localhost:8082 -o www.google.com:80 -f google

Then, the saved format spec file can be used to emulate either the client or
the server, as follows:

    pipedream.py -m replay -o www.google.com:80 -f google-12345.cnv
    pipedream.py -m replayserver -o localhost:8081 -f google-12345.cnv

To introduce mutations, use the -c flag, to specify the percent chance that
a given node will mutate.

## basic use (inline proxy)
This fuzzer can be used as an inline proxy which can do very basic processing
of data going back and forward (via the _back and _forward) functions in the
nominated python file, as follows:

    pipedream.py -m proxy -i localhost:4040 -o www.google.com:80 -f scripts/proxy.py

Note that the sockets are "pretend-asynchronous" - that is, they work on a 
timeout system and block, so you may need to wait for traffic to come through.

## basic use (editor)
This fuzzer also includes a editor, which can modify conversation files. This
can be accessed via:

    pipedream.py -m edit -f google-12345.cnv

Inline help is provided (somewhat).

## example (fuzzing a web browser)
This fuzzer can be easily used to fuzz a web browser. The first step is to
capture traffic to the target web server, by using pipedream in the default
proxy mode:

    pipedream.py -m capture -f graceful2 -i localhost:4040 -o www.reddit.com:80

This will create a socket conversation file, with the extension of .cnv. A
sample is in samples/graceful2-37659.cn_. Open this file in edit mode, as
follows:

    pipedream.py -m edit -f graceful2.cnv

Using the "p" command, inspect the contents of this conversation: note there
are six total requests, corresponding to three HTTP requests, as follows:

    [####] : p
    [ 0 -> len:0x015e ]  [ 47 45 54 20 2f 20 48 54  GET / HT ]
    [ 1 <- len:0x06ee ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 2 -> len:0x0163 ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 3 <- len:0x0550 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 4 <- len:0x1018 ]  [ 95 1c 5c 5b 3b ff ad b5  ..\[;... ]
    [ 5 -> len:0x017a ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 6 <- len:0x0550 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]

The first step is to merge packet 4 into packet 3, such that the HTTP response
is in a single piece. Do this by selecting packet 3 with "s", then using the
swallow command to merge it with packet 4:

    [####] : s 3
    [   3] : swallow 4
    [   3] : s none
    [####] : p
    [ 0 -> len:0x015e ]  [ 47 45 54 20 2f 20 48 54  GET / HT ]
    [ 1 <- len:0x06ee ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 2 -> len:0x0163 ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 3 <- len:0x1568 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [ 4 -> len:0x017a ]  [ 47 45 54 20 2f 63 64 6e  GET /cdn ]
    [ 5 <- len:0x0550 ]  [ 48 54 54 50 2f 31 2e 31  HTTP/1.1 ]
    [total: 6]
    [####] :

Now, we will fuzz the browser by using pipedream to emulate a server. We need
to configure pipedream to respond to an HTTP GET request with the first HTTP
response. Use the "s" command to selec the first response, then use the "bind"
command to link this response with the "GET" verb:

    s 1
    bind .*GET.*
    s none

Now, save the file:

    save graceful2p1.cnv

Now, exit the program, and restart it in replay server mode:

    pipedream.py -m replayserver -i localhost:4040 -c 100 -f graceful2p1.cnv

Using a browser or a TCP socket tool, connect to port 4040 on localhost. If you
use an HTTP browser, you may notice that a successful render does not return what
you expect: this is because reddit's web server does not like connections with a
Host header of "localhost".
