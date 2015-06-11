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

This will create a socket conversation file, with the extension of .cnv A 
previously prepared sample file is in the samples directory. This will 

## WIP WIP