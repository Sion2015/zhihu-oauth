# coding=utf-8

from __future__ import unicode_literals

import os

try:
    # Py3
    # noinspection PyCompatibility
    from html.parser import HTMLParser
except ImportError:
    # Py2
    # noinspection PyCompatibility,PyUnresolvedReferences
    from HTMLParser import HTMLParser

__all__ = ["INVALID_CHARS", "remove_invalid_char", 'add_serial_number',
           'SimpleHtmlFormatter']

INVALID_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']


def remove_invalid_char(dirty):
    clean = []
    for c in dirty:
        if c not in INVALID_CHARS:
            clean.append(c)
    return ''.join(clean)


def add_serial_number(file_path, postfix):
    full_path = file_path + '.' + postfix
    if not os.path.isfile(full_path):
        return full_path
    serial = 1
    while os.path.isfile(full_path):
        # noinspection PyUnboundLocalVariable
        try:
            # noinspection PyCompatibility
            serial_str = unicode(str(serial))
        except NameError:
            serial_str = str(serial)
        full_path = file_path + ' - ' + serial_str + '.' + postfix
        serial += 1
    return full_path


BASE_HTML_HEADER = """<meta name="referrer" content="no-referrer" />
<meta name="charset" content="utf-8" />
"""


# TODO: 测试 SimpleHtmlFormatter 对各种文章的兼容性


class SimpleHtmlFormatter(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._level = 0
        self._last = ''
        self._in_code = False
        self._prettified = [BASE_HTML_HEADER]

    def handle_starttag(self, tag, attrs):
        if not self._in_code:
            self._prettified.extend(['\t'] * self._level)
        self._prettified.append('<' + tag)
        for name, value in attrs:
            self._prettified.append(' ' + name + '="' + value + '"')
        self._prettified.append('>')
        if not self._in_code:
            self._prettified.append('\n')
        if tag != 'br' and tag != 'img':
            self._level += 1
        if tag == 'code':
            self._in_code = True
        self._last = tag

    def handle_endtag(self, tag):
        if tag != 'br' and tag != 'img':
            self._level -= 1
        if not self._in_code:
            self._prettified.extend(['\t'] * self._level)
        self._prettified.append('</' + tag + '>')
        if not self._in_code:
            self._prettified.append('\n')
        self._last = tag
        if tag == 'code':
            self._in_code = False

    def handle_startendtag(self, tag, attrs):
        if not self._in_code:
            self._prettified.extend(['\t'] * self._level)
        self._prettified.append('<' + tag)
        for name, value in attrs:
            self._prettified.append(' ' + name + '="' + value + '"')
        self._prettified.append('/>')
        self._last = tag

    def handle_data(self, data):
        if not self._in_code:
            self._prettified.extend(['\t'] * self._level)
            if self._last == 'img':
                self._prettified.append('<br>\n')
                self._prettified.extend(['\t'] * self._level)
        self._prettified.append(data)
        if not self._in_code:
            self._prettified.append('\n')

    def handle_charref(self, name):
        self._prettified.append('&#' + name)

    def handle_entityref(self, name):
        self._prettified.append('&' + name + ';')

    def error(self, message):
        self._prettified = ['error when parser the html file.']

    def prettify(self):
        return ''.join(self._prettified)