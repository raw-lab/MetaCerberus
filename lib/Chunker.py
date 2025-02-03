# -*- coding: utf-8 -*-
"""Chunker.py: Class for splitting fasta and fastq files into smaller chunks.
Takes into account headers begining with select delimeters (i.e. > or @)
"""

import os
import argparse
import glob
from typing import List
from pathlib import Path


def create_chunks(path, dest, chunksize="1000M", delim=None, lines=None) -> List[Path]:
    chunksize = human2bytes(chunksize)
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    os.makedirs(dest, exist_ok=True)

    i = 0
    fout = open(os.path.join(dest, "%s.%05d%s" % (name, i, ext)), "w")
    with open(path, "r") as inf:
        if delim is not None:
            for l in inf:
                if delim in l:
                    # check filesize, potentially increase i
                    fout.flush()
                    size = os.fstat(fout.fileno()).st_size
                    if size >= chunksize:
                        fout.close()
                        i += 1
                        fout = open(
                            os.path.join(dest, "%s.%05d%s" % (name, i, ext)),
                            "w",
                        )
                        fout.write(l)
                    else:
                        fout.write(l)
                else:
                    fout.write(l)
        else:
            for j, l in enumerate(inf):
                if j % lines == 0:
                    # check filesize, potentially increase i
                    fout.flush()
                    size = os.fstat(fout.fileno()).st_size
                    if size >= chunksize:
                        fout.close()
                        i += 1
                        fout = open(
                            os.path.join(dest, "%s.%05d%s" % (name, i, ext)),
                            "w",
                        )
                        fout.write(l)
                    else:
                        fout.write(l)
                else:
                    fout.write(l)
        fout.close()

    return glob.glob(os.path.join(dest, "*"))


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
        "customary": ("B", "K", "M", "G", "T", "P", "E", "Z", "Y"),
        "customary_ext": (
            "byte",
            "kilo",
            "mega",
            "giga",
            "tera",
            "peta",
            "exa",
            "zetta",
            "iotta",
        ),
        "iec": ("Bi", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"),
        "iec_ext": (
            "byte",
            "kibi",
            "mebi",
            "gibi",
            "tebi",
            "pebi",
            "exbi",
            "zebi",
            "yobi",
        ),
    }

    init = s
    num = ""
    while s and s[0:1].isdigit() or s[0:1] == ".":
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    for name, sset in list(SYMBOLS.items()):
        if letter in sset:
            break
    else:
        if letter == "k":
            # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
            sset = SYMBOLS["customary"]
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]: 1}
    for i, s in enumerate(sset[1:]):
        prefix[s] = 1 << (i + 1) * 10
    return int(num * prefix[letter])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split input file into pieces.")

    # required
    parser.add_argument("infile", help="Path to input file.")
    parser.add_argument("outfolder", help="Path to output folder.")

    # flags
    parser.add_argument(
        "-c", "--chunksize", default="1000M", help="Approximate size of file chunks."
    )

    # required flag
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d", "--delimiter", help="Delimiter for preserving text groups."
    )
    group.add_argument(
        "-l", "--lines", type=int, help="Number of lines to be considered a text group."
    )

    args = parser.parse_args()

    c = create_chunks(
        args.infile,
        args.outfolder,
        chunksize=args.chunksize,
        delim=args.delimiter,
        lines=args.lines,
    )
