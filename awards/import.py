#! /usr/bin/env python
# -*- coding: UTF-8 -*-
'''Data import.'''

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


from __future__ import with_statement

import configuration
import sys
sys.path.append(configuration.library_path)

import my.sql

import MySQLdb

import base64
import datetime
import os
import random


import static


def random_password():
    string = ''
    for i in xrange(0, 6):
        string += chr(random.randint(0, 255))
    return base64.b64encode(string)


def parse_datetime(datetime_string):
    date_string, space, time_string = datetime_string.partition(' ')
    if not space:
        raise ValueError('No space in <code>datetime_string</code>.')
    month, day, year = date_string.split('/')
    hour, minute, second = time_string.split(':')
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


def main_with_cursor(cursor):
    round_id = my.sql.get_unique_one(cursor, '''
        select round from current_rounds where contest = %s and stage =
            (select id from contest_stages where identifier = 'review')''', (static.contest.id,))

    index = 0
    for line in open('google_docs_masterpieces.csv', 'r'):
        fields = line.rstrip('\n').split('#')
        fields = map(str.strip, fields, ' ')

        if len(fields) == 1:
            continue

        published, username, ideabox_stage, ideabox_section, content, authors_explanation, user_comment = fields
        if published == 'Timestamp':
            continue
        published = parse_datetime(published)

        print published, '#', username, '#', ideabox_stage, '#', ideabox_section, '#', content, '#', authors_explanation, '#', user_comment
        
        user_id = my.sql.get_unique_one(cursor, 'select id from users where name = %s', (username,))
        if not user_id:
            password = random_password()
            cursor.execute('''
                insert into users(
                    role,
                    registered,
                    remote_address,
                    name,
                    password)
                values(
                    (select id from user_roles where identifier = 'registered'),
                    current_timestamp,
                    '',
                    %s,
                    %s)''',
                (username, password))
            user_id = cursor.connection.insert_id()

        questionable_foreword = 'Обсуждаемое:'
        if content.startswith(questionable_foreword):
            content = content[len(questionable_foreword):].lstrip()

        explanation_foreword = 'Пояснение:'
        if authors_explanation.startswith(explanation_foreword):
            authors_explanation = authors_explanation[len(explanation_foreword):].lstrip()

        ideabox_subsection, _, content_remainder = content.partition(':')
        section_id = None
        if content_remainder:
            section_id = my.sql.get_unique_one(cursor,
                'select id from ideabox_sections where godville_section_name = %s and godville_subsection_name = %s',
                (ideabox_section, ideabox_subsection))
            if section_id:
                content = content_remainder.lstrip()
        if not section_id:
            section_id = my.sql.get_unique_one(cursor,
                'select id from ideabox_sections where godville_section_name = %s',
                (ideabox_section,))

        index += 1
        cursor.execute('''
            insert into masterpieces(
                google_docs_index,
                contest,
                user,
                published,
                ideabox_section,
                ideabox_stage,
                content,
                authors_explanation,
                user_comment)
            values(
                %s,
                %s,
                %s,
                %s,
                %s,
                (select id from ideabox_stages where google_docs_name = %s),
                %s,
                %s,
                %s)''',
            (
                index,
                static.contest.id,
                user_id,
                published,
                section_id,
                ideabox_stage,
                content,
                authors_explanation,
                user_comment)
            )
        masterpiece_id = cursor.connection.insert_id()

        cursor.execute('''
            insert into nominations(contest_round, masterpiece, contest_category, user)
                select %s, %s, id, %s from contest_categories where contest = %s and name <> %s''',
                (round_id, masterpiece_id, user_id, static.contest.id, 'Мисс Монстр' if ideabox_section != 'Монстры' else ''))


def main():
    if len(sys.argv) <= 1:
        print 'Usage: import <contest_identifier>'
        return
    contest_identifier = sys.argv[1]

    database = MySQLdb.connect(charset = 'utf8', use_unicode = False, **configuration.database)
    with my.sql.AutoCursor(database) as cursor:
        cursor.execute('set sql_mode = traditional')
        cursor.execute('set time_zone = \x27+4:00\x27')
        static.init(cursor, contest_identifier)
        main_with_cursor(cursor)


main()

