#! /usr/bin/env python2.6
# -*- coding: UTF-8 -*-
'''Конкурс «Золотая Фейспалмовая ветвь» и другие.'''

import configuration
import sys
sys.path.append(configuration.library_path)

import my.sql

import MySQLdb


def init(cursor, contest_identifier):
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

    global contest_stages
    contest_stages = my.sql.get_indexed_named_tuples(cursor,
        'select * from contest_stages order by priority')

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

