# -*- coding: UTF-8 -*-
"""

Regular expressions for winpath:
http://regexlib.com/Search.aspx?k=file+name

^(([a-zA-Z]:|\\)\\)?(((\.)|(\.\.)|([^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?))\\)*[^\\/:\*\?"\|<>\. ](([^\\/:\*\?"\|<>\. ])|([^\\/:\*\?"\|<>]*[^\\/:\*\?"\|<>\. ]))?$

https://github.com/kgryte/regex-filename-windows/blob/master/lib/index.js
REGEX: /^([a-zA-Z]:|[\\\/]{2}[^\\\/]+[\\\/]+[^\\\/]+|)([\\\/]|)([\s\S]*?)((?:\.{1,2}|[^\\\/]+?|)(\.[^.\/\\]*|))(?:[\\\/]*)$/
Splits a Windows filename.
Modified from Node.js [source]{@link https://github.com/nodejs/node/blob/1a3b295d0f46b2189bd853800b1e63ab4d106b66/lib/path.js#L65}.
"""

from __future__ import absolute_import
from behave4cmd0.command_shell_proc import (
    BehaveWinCommandOutputProcessor,
    TracebackLineNormalizer,
    ExceptionWithPathNormalizer,
)
import re
import pytest

# -----------------------------------------------------------------------------
# IMPLEMENTATION
# -----------------------------------------------------------------------------
# winpath_pattern = ur"^($([A-Za-z]:(\[^\]+)*)|((\[^\]+)*)|([^\]+\[^\]+)*)$"
winpath_pattern = (
    "^([A-Za-z]:(\\[\w\.\-]+)+)|((\\[\w\.\-]+)*)|(\s[\w\.\-]+([\w\.\-]+)*)$"
)
winpath_re = re.compile(winpath_pattern, re.UNICODE)


class PathNormalizer(object):
    def normalize(self, output):
        pattern = "^.*$"

    def __call__(self, output):
        pass


# -----------------------------------------------------------------------------
# TEST CANDIDATES:
# -----------------------------------------------------------------------------
line_processor_configerrors = [
    ExceptionWithPathNormalizer(
        "ConfigError: No steps directory in '(?P<path>.*)'",
        "ConfigError: No steps directory in",
    ),
    BehaveWinCommandOutputProcessor.line_processors[1],
]

line_processor_parsererrors = [
    ExceptionWithPathNormalizer(
        'ParserError: Failed to parse "(?P<path>.*)"', "ParserError: Failed to parse"
    ),
    BehaveWinCommandOutputProcessor.line_processors[2],
]

line_processor_ioerrors = [
    ExceptionWithPathNormalizer(
        # ur"No such file or directory: '(?P<path>.*)'",
        # u"No such file or directory:"),  # IOError
        # ur"Error: \\[Errno 2\\] No such file or directory: '(?P<path>.*)'",
        "No such file or directory: '(?P<path>.*)'",
        "[Errno 2] No such file or directory:",
    ),  # IOError
    BehaveWinCommandOutputProcessor.line_processors[3],
]

line_processor_traceback = [
    ExceptionWithPathNormalizer('^\s*File "(?P<path>.*)", line \d+, in ', '  File "'),
    BehaveWinCommandOutputProcessor.line_processors[4],
]

# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
xfail = pytest.mark.xfail()


class TestWinpathRegex(object):
    @pytest.mark.parametrize(
        "winpath",
        [
            "C:\\foo\\bar\\alice.txt",
            "C:\\foo\\bar",
            "C:\\alice.txt",
            "C:\\.verbose",
            ".\\foo\\bar\\alice.txt",
            "..\\foo\\..\\bar\\alice.txt",
            "foo\\bar\\alice.txt",
            "alice.txt",
        ],
    )
    def test_match__with_valid_winpath(self, winpath):
        mo = winpath_re.match(winpath)
        assert mo is not None

    @xfail
    @pytest.mark.parametrize(
        "winpath",
        [
            "2:\\foo\\bar\\alice.txt",
            "C:\\bar\\alice.txt",
        ],
    )
    def test_match__with_invalid_winpath(self, winpath):
        mo = winpath_re.match(winpath)
        assert mo is None


class TestPathNormalizer(object):
    @pytest.mark.parametrize(
        "output, expected",
        [
            (
                "ConfigError: No steps directory in 'C:\\one\\two\\three.txt'",
                "ConfigError: No steps directory in 'C:/one/two/three.txt'",
            ),
        ],
    )
    def test_call__with_pattern1(self, output, expected):
        for line_processor in line_processor_configerrors:
            actual = line_processor(output)
            assert actual == expected

    # ParserError: Failed to parse "(?P<path2>.*)"
    @pytest.mark.parametrize(
        "output, expected",
        [
            (
                'ParserError: Failed to parse "C:\\one\\two\\three.txt"',
                'ParserError: Failed to parse "C:/one/two/three.txt"',
            ),
        ],
    )
    def test_call__with_pattern2(self, output, expected):
        for line_processor in line_processor_parsererrors:
            actual = line_processor(output)
            assert actual == expected

    @pytest.mark.parametrize(
        "output, expected",
        [
            (
                "Error: [Errno 2] No such file or directory: 'C:\\one\\two\\three.txt'",
                "Error: [Errno 2] No such file or directory: 'C:/one/two/three.txt'",
            ),
        ],
    )
    def test_call__with_pattern3(self, output, expected):
        for index, line_processor in enumerate(line_processor_ioerrors):
            actual = line_processor(output)
            assert actual == expected, "line_processor %s" % index

    @pytest.mark.parametrize(
        "output, expected",
        [
            (
                '  File "C:\\one\\two\\three.txt", line 123, in xxx_some_method',
                '  File "C:/one/two/three.txt", line 123, in xxx_some_method',
            ),
        ],
    )
    def test_call__with_pattern4(self, output, expected):
        for index, line_processor in enumerate(line_processor_traceback):
            actual = line_processor(output)
            assert actual == expected, "line_processor %s" % index
