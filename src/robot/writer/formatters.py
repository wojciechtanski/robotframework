#  Copyright 2008-2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re

from robot.parsing.settings import Documentation
from robot import utils
from robot.writer.tableformatters import SplittingHtmlFormatter

from .tableformatters import (RowSplittingFormatter, RowSplitter,
    ColumnAligner, SettingTableAligner, NameCell, HeaderCell, Cell)


class _TestDataFileFormatter(object):

    def variable_rows(self, variables):
        for row in self._variable_table_formatter().format_simple_table(variables):
            yield self._format_row(row)

    def setting_rows(self, settings):
        for row in self._setting_table_formatter().format_simple_table(settings):
            yield self._format_row(row)

    def test_rows(self, tests):
        for row in self._test_table_formatter(tests).format_indented_table(tests):
            yield self._format_row(row)

    def keyword_rows(self, keywords):
        for row in self._keyword_table_formatter(keywords).format_indented_table(keywords):
            yield self._format_row(row)

    def empty_row(self):
        return self._format_row([])

    def _format_row(self, row):
        return row


class TsvFormatter(_TestDataFileFormatter):
    _padding = ''

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = RowSplittingFormatter(self._padding, self._cols)

    def _variable_table_formatter(self):
        return self._formatter

    def _setting_table_formatter(self):
        return self._formatter

    def _test_table_formatter(self, tests):
        return self._formatter

    def _keyword_table_formatter(self, keywords):
        return self._formatter

    def header_row(self, table):
        return self._format_row(['*%s*' % cell for cell in table.header])

    def _format_row(self, row):
        return self._pad(row)

    def _pad(self, row):
        return row + [self._padding] * (self._cols - len(row))


class TxtFormatter(_TestDataFileFormatter):
    _padding = ''
    _FIRST_ROW_LENGTH = 18
    _SETTING_NAME_WIDTH = 14

    def __init__(self, cols=8):
        self._cols = cols

    def _variable_table_formatter(self):
        return RowSplittingFormatter(self._padding, self._cols)

    def _setting_table_formatter(self):
        return SettingTableAligner(self._padding, self._cols,
                                   self._SETTING_NAME_WIDTH)

    def _test_table_formatter(self, tests):
        return self._indented_table_formatter(tests)

    def _keyword_table_formatter(self, keywords):
        return self._indented_table_formatter(keywords)

    def header_row(self, table):
        header = ['*** %s ***' % table.header[0]] + table.header[1:]
        if self._should_align_columns(table):
            return ColumnAligner(self._FIRST_ROW_LENGTH, table).align_row(header)
        return header

    def _indented_table_formatter(self, table):
        if self._should_align_columns(table):
            return ColumnAligner(self._FIRST_ROW_LENGTH, table)
        return RowSplittingFormatter(self._padding, self._cols)

    def _should_align_columns(self, table):
        return bool(table.header[1:])

    def _format_row(self, row):
        return self._escape(row)

    def _escape(self, row):
        if len(row) >= 2 and row[0] == '' and row[1] == '':
            row[1] = '\\'
        return [re.sub('\s\s+(?=[^\s])', lambda match: '\\'.join(match.group(0)), item) for item in row]


class PipeFormatter(TxtFormatter):
    _padding = '  '


class HtmlFormatter(_TestDataFileFormatter):

    def __init__(self):
        self._cols = 5
        self._formatter = SplittingHtmlFormatter('', self._cols)

    def empty_row(self):
        return [NameCell('')] + [Cell('') for _ in range(self._cols-1)]

    def _setting_table_formatter(self):
        return self._formatter

    def _variable_table_formatter(self):
        return self._formatter

    def _test_table_formatter(self, tests):
        return self._formatter

    def _keyword_table_formatter(self, keywords):
        return self._formatter

    def header_row(self, table):
        return [HeaderCell(table.header[0], self._cols)]