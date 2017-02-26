# ----------------------------------------------------------------------
# rainbow, a command line colorizer
# Copyright (C) 2011-2017 Julien Nicoulaud <julien.nicoulaud@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------

import os
import re

from . import LOGGER


class IdentityTransformer:
    def __init__(self):
        pass

    def transform(self, line):
        return line

    def __str__(self):
        return 'identity'


class InsertBeforeRegexTransformer(IdentityTransformer):
    def __init__(self, regex, before):
        IdentityTransformer.__init__(self)
        self.regex = regex
        self.before = before

    def transform(self, line):
        return self.regex.sub(self.before + r'\g<0>', line)

    def __str__(self):
        return 'insert "%s" before "%s"' % (self.before, self.regex)


class InsertAfterRegexTransformer(IdentityTransformer):
    def __init__(self, regex, after):
        IdentityTransformer.__init__(self)
        self.regex = regex
        self.after = after

    def transform(self, line):
        return self.regex.sub(r'\g<0>' + self.after, line)

    def __str__(self):
        return 'insert "%s" after "%s"' % (self.after, self.regex)


class InsertBeforeAndAfterRegexTransformer(IdentityTransformer):
    def __init__(self, regex, before, after):
        IdentityTransformer.__init__(self)
        self.regex = regex
        self.before = before
        self.after = after

    def transform(self, line):
        return self.regex.sub(self.after + r'\g<0>' + self.before, line)

    def __str__(self):
        return 'insert "%s" before and "%s" after "%s"' % (self.before, self.after, self.regex)


class ListTransformer(IdentityTransformer):
    def __init__(self, transformers):
        IdentityTransformer.__init__(self)
        self.transformers = transformers

    def transform(self, line):
        for transformer in self.transformers:
            line = transformer.transform(line)
        return line

    def __str__(self):
        return os.linesep.join(self.transformers)


class TransformerBuilder:
    def __init__(self):
        self.transformers = []

    def add_mapping(self, pattern, filter):
        LOGGER.debug('Binding pattern "%s" with filter "%s".', pattern, filter)
        self.transformers.append(self.make_transformer(re.compile(pattern), filter))

    @staticmethod
    def make_transformer(regex, filter):

        if filter.before and filter.after:
            return InsertBeforeAndAfterRegexTransformer(regex, filter.before, filter.after)

        elif filter.before:
            return InsertBeforeRegexTransformer(regex, filter.before)

        elif filter.after:
            return InsertAfterRegexTransformer(regex, filter.after)

    def build(self):

        if not self.transformers:
            return IdentityTransformer()

        if len(self.transformers) == 1:
            return self.transformers[0]

        return ListTransformer(self.transformers)