# -*- coding: utf-8 -*-
"""Chunker.py: Class for splitting fasta and fastq files into smaller chunks.
Takes into account headers begining with select delimeters (i.e. > or @)
"""

import os
import argparse
import glob


class Chunker:

    def __init__(self, path, dest, chunksize='1000M', delim=None, lines=None):
        self.path = path
        self.dest = dest
        self.chunksize = human2bytes(chunksize)
        self.delim = delim
        self.lines = lines

        self.fn = os.path.basename(self.path)
        self.name, self.ext = os.path.splitext(self.fn)

        #if os.path.exists(dest):
        #    if os.listdir(dest):
        #        raise IOError("Destination folder not empty.")

        os.makedirs(dest, exist_ok=True)

        self.stream()
        self.files = glob.glob(os.path.join(dest, '*'))

    def stream(self):
        if self.delim is not None:
            self.stream_delim()
        else:
            self.stream_lines()

    def stream_delim(self):
        i = 0
        fout = open(os.path.join(self.dest, '%s.%05d%s' % (self.name, i, self.ext)), 'w')
        with open(self.path, 'r') as inf:
            for l in inf:
                if self.delim in l:
                    # check filesize, potentially increase i
                    fout.flush()
                    size = os.fstat(fout.fileno()).st_size
                    if size >= self.chunksize:
                        fout.close()
                        i += 1
                        fout = open(os.path.join(self.dest, '%s.%05d%s' % (self.name, i, self.ext)), 'w')
                        fout.write(l)
                    else:
                        fout.write(l)
                else:
                    fout.write(l)
            fout.close()

    def stream_lines(self):
        i = 0
        fout = open(os.path.join(self.dest, '%s.%05d%s' % (self.name, i, self.ext)), 'w')
        with open(self.path, 'r') as inf:
            for j, l in enumerate(inf):
                if j % self.lines == 0:
                    # check filesize, potentially increase i
                    fout.flush()
                    size = os.fstat(fout.fileno()).st_size
                    if size >= self.chunksize:
                        fout.close()
                        i += 1
                        fout = open(os.path.join(self.dest, '%s.%05d%s' % (self.name, i, self.ext)), 'w')
                        fout.write(l)
                    else:
                        fout.write(l)
                else:
                    fout.write(l)
            fout.close()


def human2bytes(s):
    """
    Attempts to guess the string format based on default symbols
    set and return the corresponding bytes as an integer.
    When unable to recognize the format ValueError is raised.

      >>> human2bytes('0 B')
      0
      >>> human2bytes('1 K')
      1024
      >>> human2bytes('1 M')
      1048576
      >>> human2bytes('1 Gi')
      1073741824
      >>> human2bytes('1 tera')
      1099511627776

      >>> human2bytes('0.5kilo')
      512
      >>> human2bytes('0.1  byte')
      0
      >>> human2bytes('1 k')  # k is an alias for K
      1024
      >>> human2bytes('12 foo')
      Traceback (most recent call last):
          ...
      ValueError: can't interpret '12 foo'
    """
    SYMBOLS = {
        'customary': ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
        'customary_ext': ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                          'zetta', 'iotta'),
        'iec': ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
        'iec_ext': ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                    'zebi', 'yobi'),
    }

    init = s
    num = ""
    while s and s[0:1].isdigit() or s[0:1] == '.':
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    for name, sset in list(SYMBOLS.items()):
        if letter in sset:
            break
    else:
        if letter == 'k':
            # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
            sset = SYMBOLS['customary']
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]: 1}
    for i, s in enumerate(sset[1:]):
        prefix[s] = 1 << (i + 1) * 10
    return int(num * prefix[letter])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split input file into pieces.')

    # required
    parser.add_argument('infile', help='Path to input file.')
    parser.add_argument('outfolder', help='Path to output folder.')

    # flags
    parser.add_argument('-c', '--chunksize', default='1000M', help='Approximate size of file chunks.')

    # required flag
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--delimiter', help='Delimiter for preserving text groups.')
    group.add_argument('-l', '--lines', type=int, help='Number of lines to be considered a text group.')

    args = parser.parse_args()

    c = Chunker(args.infile, args.outfolder, chunksize=args.chunksize, delim=args.delimiter, lines=args.lines)
