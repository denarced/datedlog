#!/usr/bin/env python3

import os
import re
import sys


class LogFile():
    TIME_RE = r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d.\d{4}).*'

    def __init__(self, fp):
        self.fp = fp
        self.buf = []
        self.nextTime = None
        self.more = True

    def hasMore(self):
        return self.more

    def read(self):
        # Read until timestamp line is found or EOF
        # Return all lines except for the timestamp line
        # Put the timestamp line into buf
        # If the EOF is met, mark more = False
        while True:
            # Read next line
            line = self.fp.readline()
            # If empty, EOF has been met. more = False, copy buf, clear it
            if line == '':
                self.more = False
                returned = list(self.buf)
                self.buf = []
                return returned
            timestamp = self.deriveTimestamp(line)
            if timestamp:
                returned = list(self.buf)
                self.buf = [line]
                self.nextTime = timestamp
                return returned
            self.buf.append(line)

    def deriveTimestamp(self, line):
        match = re.match(LogFile.TIME_RE, line)
        if match:
            return match.group(1)

    def close(self):
        self.fp.close()

def logFilesWithMinimumTimestamps(logFiles):
    minimum = None
    for each in logFiles:
        if minimum is None:
            minimum = each
        elif minimum.nextTime > each.nextTime:
                minimum = each
    return minimum


def appendDates(lines):
    match = re.match(LogFile.TIME_RE, lines[0])
    assert match, "Oops, the first line should always contain the timestamp"
    outf = open(match.group(1)[0:10] + '.log', 'a')
    for each in lines:
        outf.write(each)


def main(logFiles):
    while logFiles:
        minimum = logFilesWithMinimumTimestamps(logFiles)
        lines = minimum.read()
        appendDates(lines)
        if not minimum.hasMore():
            logFiles.remove(minimum)

if __name__ == '__main__':
    # Create a list of LogFile objects and initialize each of them in such a way
    # that the first line with a timestamp is read. If any file begins with
    # timestampless lines, they are ignored.
    logFiles = []
    for each in sys.argv[1:]:
        if os.path.exists(each):
            logFile = LogFile(open(each))
            # read until the first timestamp
            # ignore the read lines before the first timestamp
            logFile.read()
            if logFile.hasMore():
                logFiles.append(logFile)
        else:
            print('Doesn\'t exist and therefore skipping:', each)

    # the list might be empty because there were no args or because the files
    # didn't exist or had no timestamps
    if logFiles:
        main(logFiles)
        for each in logFiles:
            each.close()
