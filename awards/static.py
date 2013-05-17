#! /usr/bin/env python2.6
# -*- coding: UTF-8 -*-
'''Contest static data.'''

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


import configuration
import sys
sys.path.append(configuration.library_path)

import my.sql

import MySQLdb


def get_single_or_none(l):
    if not l:
        return None
    elif len(l) == 1:
        return l[0]
    else:
        raise my.sql.UniquenessError


def init(cursor, contest_identifier):
    global start_time
    start_time = my.sql.get_unique_one(cursor,
        'select current_timestamp')

    global user_roles
    user_roles = my.sql.get_indexed_named_tuples(cursor,
        'select * from user_roles')

    global user_actions
    user_actions = my.sql.get_indexed_named_tuples(cursor,
        'select * from user_actions')

    global contest
    contest = my.sql.get_unique_named_tuple(cursor,
        'select * from contests where identifier = %s',
        (contest_identifier,))

    global leagues
    leagues = my.sql.get_indexed_named_tuples(cursor,
        'select * from leagues')

    global contest_stages
    contest_stages = my.sql.get_indexed_named_tuples(cursor,
        'select * from contest_stages order by priority')

    global tenses
    tenses = my.sql.get_indexed_named_tuples(cursor,
        'select * from tenses')

    global nomination_sources
    nomination_sources = my.sql.get_indexed_named_tuples(cursor, '''
        select
            nomination_sources.*,
            (
                select id
                from contest_categories
                where
                    contest = %s and
                    nomination_source = nomination_sources.id and
                    nomination_sources.is_unique
            ) as category
        from
            nomination_sources''',
        (contest.id,))

    global contest_categories
    contest_categories = my.sql.get_indexed_named_tuples(cursor,
        'select * from contest_categories where contest = %s order by priority',
        (contest.id,))

    global ideabox_sections
    ideabox_sections = my.sql.get_indexed_named_tuples(cursor,
        'select * from ideabox_sections order by priority')

    global ideabox_stages
    ideabox_stages = my.sql.get_indexed_named_tuples(cursor,
        'select * from ideabox_stages order by priority')

