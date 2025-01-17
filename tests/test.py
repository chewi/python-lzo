#! /usr/bin/env python
##
## vi:ts=4:et
##
##---------------------------------------------------------------------------##
##
## This file is part of the LZO real-time data compression library.
##
## Copyright (C) 1998-2002 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## The LZO library is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of
## the License, or (at your option) any later version.
##
## The LZO library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with the LZO library; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/opensource/lzo/
##
##---------------------------------------------------------------------------##

from __future__ import print_function
import inspect
import sys, string

# update sys.path when running in the build directory
from tests.util import get_sys_path
sys.path = get_sys_path()

import lzo


# ***********************************************************************
#  a very simple test driver...
# ***********************************************************************

def print_modinfo():
    #print sys.modules
    mod = sys.modules['lzo']
    #print mod
    d = mod.__dict__
    for k in d.keys():
        print(k, d[k])


def gen(src, level=1):
    a0 = lzo.adler32(src)
    c  = lzo.compress(src, level)
    u1 = lzo.decompress(c)
    a1 = lzo.adler32(u1)
    o  = lzo.optimize(c)
    u2 = lzo.decompress(o)
    a2 = lzo.adler32(u2)
    if src != u1:
        raise lzo.error("internal error 1: %r %r", src, u1)
    if src != u2:
        raise lzo.error("internal error 1: %r %r",  src, u2)
    if a0 != a1 or a0 != a2:
        raise lzo.error("internal error 2")
    print("compressed %6d -> %6d" % (len(src), len(c)))

def gen_all(src):
    all_algos = {"LZO1", "LZO1A", "LZO1B", "LZO1C", "LZO1F", "LZO1X", "LZO1Y", "LZO1Z", "LZO2A"}
    if not src:
        # LZO1 and LZO1A header exception for empty input
        all_algos.remove("LZO1")
        all_algos.remove("LZO1A")
    for algo in all_algos:
        a0 = lzo.adler32(src)
        c  = lzo.compress(src, algorithm=algo)
        u1 = lzo.decompress(c, algorithm=algo)
        a1 = lzo.adler32(u1)
        if src != u1:
            raise lzo.error("internal error 1: %r %r", src, u1)
        if a0 != a1:
            raise lzo.error("internal error 2")
        print(f"compressed using {algo} {len(src): 6} -> {len(c): 6}")


def gen_raw(src, level=1):
    a0 = lzo.adler32(src)
    c  = lzo.compress(src, level, False)
    u1 = lzo.decompress(c, False, len(src))
    a1 = lzo.adler32(u1)
    o  = lzo.optimize(c, False, len(src))
    u2 = lzo.decompress(o, False, len(src))
    a2 = lzo.adler32(u2)
    # make sure it still works when you overstate the output buffer length
    u3 = lzo.decompress(c, False, len(src) + 100)
    if src != u1 or src != u2 or src != u3:
        raise lzo.error("internal error 1")
    if a0 != a1 or a0 != a2:
        raise lzo.error("internal error 2")
    print("compressed %6d -> %6d" % (len(src), len(c)))

def test_version():
    import pkg_resources
    pkg_version = pkg_resources.require("python-lzo")[0].version
    mod_version = lzo.__version__.decode('utf-8')
    assert pkg_version == mod_version, \
        "%r != %r" %(pkg_version, mod_version)

def test_lzo():
    yield gen, b"aaaaaaaaaaaaaaaaaaaaaaaa"
    yield gen, b"abcabcabcabcabcabcabcabc"
    yield gen, b"abcabcabcabcabcabcabcabc", 9

def test_lzo_all():
    yield gen_all, b"aaaaaaaaaaaaaaaaaaaaaaaa"
    yield gen_all, b"abcabcabcabcabcabcabcabc"
    yield gen_all, b"abcabcabcabcabcabcabcabc"

def test_lzo_raw():
    yield gen_raw, b"aaaaaaaaaaaaaaaaaaaaaaaa"
    yield gen_raw, b"abcabcabcabcabcabcabcabc"
    yield gen_raw, b"abcabcabcabcabcabcabcabc", 9


def test_lzo_empty():
    yield gen, b""
    yield gen_raw, b""

def test_lzo_empty_all():
    yield gen_all, b""

def test_lzo_big():
    gen(b" " * 131072)
    gen_all(b" " * 131072)

def test_lzo_raw_big():
    gen_raw(b" " * 131072)


if sys.maxsize > 1<<32:
    # This test raises OverflowError on 32-bit Pythons. Compressing
    # this much data requires a 64-bit system.
    def test_lzo_compress_extremely_big():
        b = lzo.compress(bytes(bytearray((1024**3)*2)))

if __name__ == "__main__":
    all_tests = (test_lzo, test_lzo_raw, test_lzo_empty, test_lzo_big, test_lzo_raw_big, test_lzo_all, test_lzo_empty_all)
    for test_func in all_tests:
        if inspect.isgeneratorfunction(test_func) is True:
            for test_case in test_func():
                test = test_case[0]
                args = test_case[1:]
                test(*args)
        else:
            test_func()
