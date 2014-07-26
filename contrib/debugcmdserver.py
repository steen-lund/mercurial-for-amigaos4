#!/usr/bin/env python
#
# Dumps output generated by Mercurial's command server in a formatted style to a
# given file or stderr if '-' is specified. Output is also written in its raw
# format to stdout.
#
# $ ./hg serve --cmds pipe | ./contrib/debugcmdserver.py -
# o, 52   -> 'capabilities: getencoding runcommand\nencoding: UTF-8'

import sys, struct

if len(sys.argv) != 2:
    print 'usage: debugcmdserver.py FILE'
    sys.exit(1)

outputfmt = '>cI'
outputfmtsize = struct.calcsize(outputfmt)

if sys.argv[1] == '-':
    log = sys.stderr
else:
    log = open(sys.argv[1], 'a')

def read(size):
    data = sys.stdin.read(size)
    if not data:
        raise EOFError
    sys.stdout.write(data)
    sys.stdout.flush()
    return data

try:
    while True:
        header = read(outputfmtsize)
        channel, length = struct.unpack(outputfmt, header)
        log.write('%s, %-4d' % (channel, length))
        if channel in 'IL':
            log.write(' -> waiting for input\n')
        else:
            data = read(length)
            log.write(' -> %r\n' % data)
        log.flush()
except EOFError:
    pass
finally:
    if log != sys.stderr:
        log.close()
