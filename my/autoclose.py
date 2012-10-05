#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''Autoclose object.'''

# Copyright 2012 Anthill Beetle

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class AutoClose:
    'Autoclosing object. Calls close() on scope leave.'
    def __init__(self, closable):
        self.__closable = closable
    def __enter__(self):
        return self.__closable
    def __exit__(self, type, value, traceback):
        try:
            self.__closable.close()
        except:
            if not type:
                raise
