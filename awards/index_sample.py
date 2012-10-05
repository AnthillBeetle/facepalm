#! /usr/bin/env python2.6
# -*- coding: UTF-8 -*-
'''Web-server index file.'''

# Copyright 2012 Anthill Beetle

# This file is part of Facepalm web-engine.

# Facepalm web-engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Facepalm web-engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Facepalm web-engine. If not, see <http://www.gnu.org/licenses/>.


import sys
sys.path.append('/home/user/creogodville/awards')

import awards.contest_cgi

awards.contest_cgi.main('facepalm')

