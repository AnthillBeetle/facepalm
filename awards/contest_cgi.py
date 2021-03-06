#! /usr/bin/env python2.6
# -*- coding: UTF-8 -*-
'''CGI processor.'''

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

import os
import sys

import configuration

sys.path.append(configuration.library_path)

# Prevent logging directory flood DoS
if 'logdir' in configuration.cgitb_parameters:
    logging_directory = configuration.cgitb_parameters['logdir']
    if logging_directory != None:
        if len(os.listdir(logging_directory)) > 1024:
            del configuration.cgitb_parameters['logdir']
import cgitb; cgitb.enable(**configuration.cgitb_parameters)

from my.autoclose import AutoClose
import my.sql

import Cookie
import MySQLdb

import base64
import cgi
import collections
import datetime
import httplib
import json
import random
import urllib
import urlparse


import static


# Utilities


def escape(string):
    return cgi.escape(string, quote = True)


def multiline_escape(string, spacing = ''):
    return escape(string).replace('\r', '').replace('\n', '\n' + spacing + '  <br>')


def escape_to_single_line(string, spacing = ''):
    return escape(string.replace('\r', '').replace('\n', ' '))


def random_password():
    string = ''
    for i in xrange(0, 6):
        string += chr(random.randint(0, 255))
    return base64.b64encode(string)


def print_masterpiece_for_forum(masterpiece, hide_authors = False):
    section_prefix = static.ideabox_sections[masterpiece.ideabox_section].prefix
    stage_clarification = static.ideabox_stages[masterpiece.ideabox_stage].clarification
    ideabox_note = ''
    if section_prefix:
        ideabox_note += '_'
        ideabox_note += section_prefix
        if stage_clarification:
            ideabox_note += ' (' + stage_clarification + ')'
        ideabox_note += ':_ '
    elif stage_clarification:
        ideabox_note += '_(' + stage_clarification + ')_ '

    print 'bq. ' + ideabox_note + escape_to_single_line(masterpiece.content)

    if masterpiece.authors_explanation:
        print '&lt;br&gt;&lt;br&gt;_Пояснение:_ ' + escape_to_single_line(masterpiece.authors_explanation)

    print

    if 'user_name' in masterpiece._fields and not hide_authors:
        if masterpiece.user_comment:
            print '«' + escape_to_single_line(masterpiece.user_comment) + '»',
        else:
            print 'Б/К',
        print '— *' + escape(masterpiece.user_name) + '*'
        print


def print_masterpiece(spacing, masterpiece):
    section_prefix = static.ideabox_sections[masterpiece.ideabox_section].prefix
    stage_clarification = static.ideabox_stages[masterpiece.ideabox_stage].clarification
    ideabox_note = ''
    if section_prefix:
        ideabox_note += '<i>'
        ideabox_note += section_prefix
        if stage_clarification:
            ideabox_note += ' (' + stage_clarification + ')'
        ideabox_note += ':</i> '
    elif stage_clarification:
        ideabox_note += '<i>(' + stage_clarification + ')</i> '

    print spacing + '<div class="content">' + ideabox_note + multiline_escape(masterpiece.content, spacing) + '</div>'
    if masterpiece.authors_explanation:
        print spacing + '<div class="content">'
        print spacing + '    <i>Пояснение:</i>'
        print spacing + '    ' + multiline_escape(masterpiece.authors_explanation, spacing)
        print spacing + '  </div>'
    print spacing + '<div>'
    if masterpiece.user_comment:
        print spacing + '    <i>' + multiline_escape(masterpiece.user_comment, spacing) + '</i>'
    if 'user_name' in masterpiece._fields:
        print spacing + '    (' + escape(masterpiece.user_name) + ')'
    print spacing + '  </div>'


def get_current_round_id(cursor, contest_stage):
    return my.sql.get_unique_one(cursor, '''
        select round from contest_rounds_and_stages
        where tense = %s and contest = %s and stage = %s''',
        (static.tenses.present.id, static.contest.id, contest_stage.id))


def get_stage_next_time(cursor, contest_stage):
    return my.sql.get_unique_one(cursor, '''
        select begins from contest_rounds_and_stages
        where tense = %s and contest = %s and stage = %s''',
        (static.tenses.future.id, static.contest.id, contest_stage.id))


# Header and footer


def print_cookies():
    cookie = Cookie.SimpleCookie()

    cookie['test'] = 'cookie'
    cookie['user_id'] = user.id if user else ''
    cookie['password'] = user.password if user else ''
    
    max_age_in_days = 31
    expires = datetime.datetime.utcnow() + datetime.timedelta(days = max_age_in_days)

    for cookie_name in ('user_id', 'password'):
        cookie[cookie_name]['max-age'] = max_age_in_days * 86400
        cookie[cookie_name]['expires'] = expires.strftime('%a, %d %b %Y %T GMT')
        cookie[cookie_name]['path'] = '/'

    print cookie.output()


def print_header():
    print 'Content-type: text/html; charset=UTF-8'
    print_cookies()
    if refresh is not None:
        print 'Refresh: ' + str(refresh)
    print ''
    print '<!doctype html>'
    print '<html><head>'
    title = escape(selected_page.title) + ' - ' + escape(static.contest.name)
    if page_subtitle:
        title = escape(page_subtitle) + ' - ' + title
    print '    <title>' + title + '</title>'
    print '    <style type="text/css">'
    print '        a.pagename {text-decoration: none; color: inherit;}'
    print '        a.pagename:hover {text-decoration: underline;}'
    print '        body {font-family: sans-serif; font-size: smaller; max-width: 750px; margin: auto;}'
    print '        div.content /*, textarea.content */ {'
    print '            color: black;'
    print '            background-color: #EEFFCC;'
    print '            border-top: 1px solid #CCDDAA;'
    print '            border-bottom: 1px solid #CCDDAA;'
    print '            border-left: 3px solid #99AA77;'
    print '            border-right: 3px solid #99AA77;'
    print '            padding: 3px;'
    print '            text-align: justify;'
    #print '            font-family: serif;'
    print '          }'
    print '        div.notification {'
    print '            text-align: center;'
    print '            margin: 1ex;'
    print '            padding: 1ex;'
    print '            color: black;'
    print '            background-color: #FEFFE3;'
    print '            border: 1px solid #DCDBB6;'
    print '            border-radius: 5px;'
    print '            -html-border-radius: 5px;'
    print '            -moz-border-radius: 5px;'
    print '            -webkit-border-radius: 5px;'
    print '          }'
    #print '        input.textsize, button.textsize, select.textsize, option.textsize, textarea.textsize {font-size: 100%;}'
    print '        input.seamless, select.seamless {border: none; padding: 0px; background-color: transparent;}'
    print '        input.seamless:hover, select.seamless:hover {border-bottom: 1px solid; margin-bottom: -1px;}'
    #print '        p {text-align: justify;}'
    print '        td.ballot {border: 1px solid gray; padding: 1ex;}'
    print '      </style>'
    print '  </head><body><form method="POST" action="' + script_name + '">'
    print '    <input type="hidden" id="hidden_submit">'
    print '    <input type="hidden" name="page" value="' + selected_page.identifier + '">'
    if anchor:
        print '    <input type="hidden" name="anchor" value="' + anchor + '">'


def print_footer():
    #cgi.print_environ()
    #cgi.print_form(form)
    print '  </form></body></html>'


# User identification


def get_allowed_actions(cursor):
    global allowed_actions, role
    if user:
        role_id = my.sql.get_unique_one(cursor, '''
            select ifnull(contest.role, users.role) role
            from users left join (select * from contests_and_users where contest = %s) contest on users.id = contest.user
            where users.id = %s''', (static.contest.id, user.id))
        role = static.user_roles[role_id]
    else:
        role = static.user_roles.anonymous
    cursor.execute('select action from user_roles_and_actions where role = %s and is_allowed', (role.id,))
    allowed_actions = set([static.user_actions[row[0]] for row in cursor.fetchall()])


def retrieve_user_where(cursor, where, *parameters):
    global user
    user = my.sql.get_unique_named_tuple(cursor,
        'select * from users where ' + where,
        parameters)


def update_user_variable(cursor):
    retrieve_user_where(cursor, 'id = %s', user.id)


def identify_user(cursor):
    global user
    user = None
    if 'user_id' in cookie and 'password' in cookie:
        user_id = cookie['user_id'].value
        password = cookie['password'].value
        if user_id and password:
            retrieve_user_where(cursor, 'id = %s and password = %s', user_id, password)
            if user:
                cursor.execute('''
                    update users
                    set last_logged_in = current_timestamp
                    where id = %s''', (user.id,))
    get_allowed_actions(cursor)


def print_error_page(message, explanation):
    godville_topic_url = 'http://godville.net/forums/show_topic/' + str(static.contest.godville_topic_id)

    print_header()
    print_pagelist()
    print '    <center>'
    print '        <p><font color="red">'
    print ' '*12 + multiline_escape(message, ' '*12)
    print '          </font></p>'
    print '        <p>'
    print ' '*12 + multiline_escape(explanation, ' '*12)
    print '            <br>'
    print '            Если проблема не исчезнет — свяжитесь с администрацией конкурса'
    print '            <a href="' + godville_topic_url + '?page=last">на форуме</a>.'
    print '          </p>'
    print '      </center>'
    print_footer()


def create_user(cursor):
    if 'test' not in cookie:
        print_error_page(
            'Данный сайт работает только с браузерами, принимающими cookie.',
            'Включите приём cookie и повторите операцию.')
        exit()

    local_new_user_count = my.sql.get_unique_one(cursor, '''
        select count(1)
        from users
        where
            remote_address = %s and
            name is null and
            created > (current_timestamp - interval 1 day);''', (remote_address,))
    if local_new_user_count >= 24:
        print_error_page(
            'С вашего адреса за последние сутки уже зарегистрировано слишком много анонимных пользователей.',
            'Попробуйте повторить операцию позже.')
        exit()

    cursor.execute(
        'insert into users(role, remote_address, password) values(%s, %s, %s)',
        (static.user_roles.anonymous.id, remote_address, random_password()))
    retrieve_user_where(cursor, 'id = %s', cursor.connection.insert_id())
    get_allowed_actions(cursor)


def print_login_check_form():
    if not user:
        return
    print '    <p>'
    print '        Имя: <input name="username" value="' + escape(user.name) + '" readonly>'
    print '        Ключ: <input name="password" type="password" value="' + escape(user.password) + '" readonly>'
    print '        <input type="submit" style="text-size: 72pt;" id="login" name="" value="Сохранить"><br>'
    print '        (Нажмите кнопку «Сохранить», чтобы сохранить ключ в настройках браузера.)'
    print '      </p>'


# round_selector


range_type = collections.namedtuple('Range', ('minimum', 'maximum'))

class round_coordinates_type(collections.namedtuple('RoundCoordinates', ('league', 'ordinal'))):
    def to_string_dict(self):
        result = {'ordinal': str(self.ordinal)}
        if self.league != static.leagues.weekly:
            result['league'] = self.league.identifier
        return result


def get_round_coordinates(cursor, round_id):
    league_id, ordinal = my.sql.get_unique_row(cursor,
        'select league, ordinal from contest_rounds where id = %s',
        round_id)
    return round_coordinates_type(static.leagues[league_id], ordinal)


def prepare_selector_view(cursor, stages_range):
    cursor.execute(
        'set @current_contest = %s, @current_stage_priority_minimum = %s, @current_stage_priority_maximum = %s',
        (static.contest.id, stages_range.minimum.priority, stages_range.maximum.priority))


def get_form_round(cursor):
    league = static.leagues.by_identifier(form['league'].value) if 'league' in form else static.leagues.weekly
    cursor.execute('set @current_league = %s', (league.id,))

    if 'ordinal' in form:
        ordinal = int(form['ordinal'].value)
    else:
        ordinal = my.sql.get_unique_one(cursor, 'select max(ordinal) from selector_rounds_parametrized')

    round_id = my.sql.get_unique_one(cursor,
        'select id from selector_rounds_parametrized where ordinal = %s',
        (ordinal,))

    return round_id, round_coordinates_type(league, ordinal)


def do_round_selector(cursor, stages_range):
    global current_round_id

    prepare_selector_view(cursor, stages_range)

    if 'ordinal' in form or 'league' in form:
        current_round_id, current_coordinates = get_form_round(cursor)
    elif current_round_id:
        current_coordinates = get_round_coordinates(cursor, current_round_id)
    else:
        current_round_id, current_coordinates = get_form_round(cursor)  # default values

    voting_round_id = get_current_round_id(cursor, static.contest_stages.voting)
    voting_coordinates = get_round_coordinates(cursor, voting_round_id) if voting_round_id else None

    print '    <p style="text-align: center;">'

    for print_league in (static.leagues.weekly, static.leagues.seasonal, static.leagues.annual):
        cursor.execute('set @current_league = %s', (print_league.id,))
        results_range = range_type(*my.sql.get_unique_row(cursor, 
            'select min(ordinal), max(ordinal) from selector_rounds_parametrized'))
        if results_range == range_type(None, None):
            continue

        if print_league != static.leagues.weekly:
            print '        &nbsp; | &nbsp;'

        central_ordinal = current_coordinates.ordinal if print_league == current_coordinates.league else results_range.maximum
        links_range = range_type(
            max(results_range.minimum, min(central_ordinal - 4, results_range.maximum - 8)),
            min(results_range.maximum, max(central_ordinal + 4, results_range.minimum + 8)))

        def print_ordinal_link(print_ordinal, name = None):
            if not name:
                name = str(print_ordinal)
            print_coordinates = round_coordinates_type(print_league, print_ordinal)
            if print_coordinates == voting_coordinates:
                name = '<i>' + name + '</i>'
            if print_coordinates == current_coordinates:
                print '        <b>' + name + '</b>'
            else:
                print '        ' + selected_page.page_link(name, urllib.urlencode(print_coordinates.to_string_dict()))

        print escape(print_league.selector_prefix) + ':'

        if print_league == current_coordinates.league and current_coordinates.ordinal > results_range.minimum:
            print_ordinal_link(current_coordinates.ordinal - 1, '&nbsp;←&nbsp;')

        if links_range.minimum > results_range.minimum:
            print_ordinal_link(results_range.minimum)

        if links_range.minimum - 1 > results_range.minimum:
            print '        …'

        for link_ordinal in xrange(links_range.minimum, links_range.maximum + 1):
            print_ordinal_link(link_ordinal)

        if links_range.maximum + 1 < results_range.maximum:
            print '        …'

        if links_range.maximum < results_range.maximum:
            print_ordinal_link(results_range.maximum)

        if print_league == current_coordinates.league and current_coordinates.ordinal < results_range.maximum:
            print_ordinal_link(current_coordinates.ordinal + 1, '&nbsp;→&nbsp;')

    print '      </p>'

    return current_coordinates


def print_format_switcher(current_page, current_coordinates):
    format = form['format'].value if 'format' in form else None

    link_dict = current_coordinates.to_string_dict()
    if format == 'forum':
        link_name = 'обычная версия'
    else:
        link_name = 'версия для форума'
        link_dict['format'] = 'forum'

    print '    <p style="text-align: right;">'
    print '        ' + current_page.page_link(link_name, urllib.urlencode(link_dict))
    print '      </p>'


# Stage timing


def date2str(
        the_date,
        append_relative_day = False,
        append_when_weekday = False,
        __relative_day_names = {
#            -2: 'позавчера',
            -1: 'вчера',
            0: 'сегодня',
            1: 'завтра',
#            2: 'послезавтра'
        },
        __weekday_when_names = ['в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу', 'в воскресенье']
    ):
    date_string = the_date.strftime('%d.%m.%Y')
    suffix = None
    if append_relative_day:
        difference_in_days = (the_date.date() - static.start_time.date()).days
        if difference_in_days in __relative_day_names:
            suffix = __relative_day_names[difference_in_days]
    if append_when_weekday and not suffix:
        difference_in_days = (the_date.date() - static.start_time.date()).days
        if abs(difference_in_days) <= 4:
            suffix = __weekday_when_names[the_date.weekday()]
    if suffix:
        date_string += ' (' + suffix + ')'
    return date_string


def date2endstr(
        the_date,
        append_relative_day = False,
        append_when_weekday = False,
        __one_second = datetime.timedelta(seconds = 1)
    ):
    return date2str(the_date - __one_second,
        append_relative_day = append_relative_day,
        append_when_weekday = append_when_weekday)


def datetime2str(
        the_datetime,
        append_relative_day = False,
        append_when_weekday = False
    ):
    return the_datetime.strftime('%H:%M ') + date2str(the_datetime,
        append_relative_day = append_relative_day,
        append_when_weekday = append_when_weekday)


def datetime2endstr(
        the_datetime,
        append_relative_day = False,
        append_when_weekday = False
    ):
    time_string = the_datetime.strftime('%H:%M ')
    if time_string == '00:00 ':
        time_string = '24:00 '
    return time_string + date2endstr(the_datetime,
        append_relative_day = append_relative_day,
        append_when_weekday = append_when_weekday)


def print_round_timing(cursor):
    print '    <p style="text-align: center;">'
    current_stages = my.sql.get_indexed_named_tuples(cursor, '''
        select stage id, contest_rounds_and_stages.*
        from contest_rounds_and_stages
        where round = %s''',
        (current_round_id,))
    stages = static.contest_stages
    if stages.nomination.id in current_stages:
        nomination = current_stages[stages.nomination.id]
        page_descriptions = {
            pages.nomination.id: 'Номинирование креатива за период',
            pages.review.id: 'Рецензирование креатива, номинированного',
            pages.overview.id: 'Просмотр креатива, номинированного',
            pages.voting.id: 'Голосование за креатив, номинированный',
            pages.results.id: 'Результаты голосования за креатив, номинированный',
        }
        print '        ' + page_descriptions[selected_page.id]
        print '        с&nbsp;' + date2str(nomination.begins) +' по&nbsp;' + date2endstr(nomination.ends) + '.<br>'
    else:
        round_description_prefices = {
            pages.review.id: 'Рецензирование перед голосованием',
            pages.overview.id: 'Просмотр перед голосованием',
            pages.voting.id: 'Голосование',
            pages.results.id: 'Результаты голосования',
        }
        round_description = my.sql.get_unique_one(cursor,
            'select description from contest_rounds where id = %s',
            (current_round_id,))
        if round_description and selected_page.id in round_description_prefices:
            print '        ' + round_description_prefices[selected_page.id] + ' за ' + escape(round_description) + '.<br>'
    if stages.voting.id in current_stages:
        voting = current_stages[stages.voting.id]
        if selected_page in (pages.nomination, pages.review, pages.overview):
            verb = 'началось' if voting.begins <= static.start_time else 'начнётся'
            print '        Голосование&nbsp;' + verb + ' в&nbsp;' + datetime2str(voting.begins, append_relative_day = True, append_when_weekday = True) + '.'
        if selected_page in (pages.voting, pages.results):
            verb = 'окончилось' if voting.ends <= static.start_time else 'окончится'
            print '        Голосование&nbsp;' + verb + ' в&nbsp;' + datetime2endstr(voting.ends, append_relative_day = True, append_when_weekday = True) + '.'
    print '      </p>'


# Page: entrance


def print_entrance(cursor):
    print '    <p style="text-align: center;">'
    print '        Имя: <input name="username">'
    print '        Ключ: <input name="password" type="password">'
    print '        <input type="submit" id="login" name="" value="Войти!"><br>'
    print '      </p>'
    print '    <p style="text-align: center;">'
    print '        Если у вас нет ключа, получите его на странице «' + pages.registration.page_link() + '».'
    print '      </p>'


def process_entrance(cursor):
    global user
    global selected_page

    old_user = user

    if 'username' in form and 'password' in form:
        username = form['username'].value.strip()
        password = form['password'].value.strip()
        if username or password:
            retrieve_user_where(cursor, 'name = %s and password = %s', username, password)
            if user:
                get_allowed_actions(cursor)
                if old_user and not old_user.name:
                    merge_user_into(cursor, old_user.id, user.id)
                selected_page = pages.voting
                redirect_parameters['category_index'] = 'review'
                return
            errors.append('Неверное имя пользователя или ключ.')

    user = old_user


# Page: nomination


def print_nominated_masterpiece(masterpiece, masterpiece_nomination_names, overview = False):
    print '    <div style="padding: 1ex;">'
    print_masterpiece(' '*8, masterpiece)
    print '        <div>'
    print '            «' + '», «'.join(masterpiece_nomination_names[masterpiece.id]) + '»'
    if 'nomination_date' in masterpiece._fields:
        print '            ' + masterpiece.nomination_date.strftime('%d.%m.%Y&nbsp;%H:%M')
    if not overview:
        print ('            <input type="submit" class="seamless" style="color: red;" name="remove.' + str(masterpiece.id) +
            '" value="X" onclick="return confirm(\x27Действительно удалить номинированный креатив?\x27)">')
    print '          </div>'
    print '      </div>'


def fetch_masterpiece_category_names(cursor):
    masterpiece_category_names = collections.defaultdict(list)
    for masterpiece_id, category_name in cursor.fetchall():
        masterpiece_category_names[masterpiece_id].append(category_name)
    return masterpiece_category_names


def print_nomination(cursor):
    if not current_round_id:
        print '    <center><p>'
        print '        Номинирование окончено. Новый раунд голосования пока не создан.'
        print '      <p></center>'
        return
    if not user:
        errors.append('Недостаточно прав доступа для номинирования.')
        print_errors()
        return

    print_round_timing(cursor)

    #print '        <label for="content">Креатив:</label><br>'
    print '    <select name="ideabox_section">'
    for section in static.ideabox_sections:
        print '        <option value="' + escape(section.identifier) + '">' + escape(section.short_name) + '</option>'
    print '      </select>'

    print ('    (<input type="checkbox" name="correction" id="correction" value="yes">'
        + '<label for="correction">коррекция в операционной</label>):<br>')

    print '    <textarea name="content" id="content" style="width: 100%;"></textarea>',

    print '    <label for="authors_explanation">Пояснение автора креатива или коррекции:</label><br>'
    print '    <textarea name="authors_explanation" id="authors_explanation" style="width: 100%;"></textarea>'

    print '    <label for="user_comment">Ваши комментарии:</label><br>'
    print '    <textarea class="content" name="user_comment" id="user_comment" style="width: 100%;"></textarea>'

    manual_nomination_categories = [category for category in static.contest_categories
        if category.nomination_source in (
            static.nomination_sources.manual.id,
            static.nomination_sources.preselected.id)]
    if manual_nomination_categories:
        print '    <p style="text-align: justify;">'
        for category in manual_nomination_categories:
            print '        <span title="' + escape(category.description) + '">'
            print ('            <span style="white-space: nowrap;">'
                + '<input type="checkbox" name="category" id="category.' + str(category.id) + '"'
                + (' checked' if category.nomination_source == static.nomination_sources.preselected.id else '')
                + ' value="' + str(category.id) + '"></span>'
                + '<label for="category.' + str(category.id) + '">'
                + escape(category.name) + '</label>')
            print '          </span>'
        print '      </p>'

    print '    <input type="submit" name="nominate" value="Номинировать!">'

    is_first = True

    masterpieces = my.sql.get_named_tuples(cursor, '''
        select
            masterpieces.*,
            nominations.added nomination_date
        from
            masterpieces inner join (
                    select masterpiece, max(added) added
                    from nominations
                    where contest_round = %s and user = %s
                    group by masterpiece
                ) nominations on masterpieces.id = nominations.masterpiece
        order by
            masterpieces.added desc,
            masterpieces.id desc''',
        (current_round_id, user.id))

    cursor.execute('''
        select nominations.masterpiece, categories.name
        from nominations, contest_categories categories
        where
            nominations.contest_round = %s and
            nominations.user = %s and
            nominations.contest_category = categories.id
        order by nominations.masterpiece, categories.priority''',
        (current_round_id, user.id))
    masterpiece_nomination_names = fetch_masterpiece_category_names(cursor)

    for masterpiece in masterpieces:
        if is_first:
            is_first = False
            print '    <hr style="margin-top: 2ex;">'
            print '    <p>'
            print '        Ниже показан номинированный вами креатив.'
            print '      </p>'
        print_nominated_masterpiece(masterpiece, masterpiece_nomination_names)

    #if not is_first:
    #    print '    <div style="padding: 1ex;">Вы пока ничего не номинировали в этом раунде.</div>'


def remove_nomination(cursor, masterpiece_id, any_user = False):
    vote_count = my.sql.get_unique_one(cursor,
        'select count(1) from votes where contest_round = %s and masterpiece = %s',
        (current_round_id, masterpiece_id))
    if vote_count:
        errors.append('Невозможно удалить креатив, так как за него уже проголосовали.')
        return

    cursor.execute(
        'delete from nominations where contest_round = %s and masterpiece = %s and (%s or user = %s)',
        (current_round_id, masterpiece_id, any_user, user.id))

    nomination_count = my.sql.get_unique_one(cursor,
        'select count(1) from nominations where masterpiece = %s',
        (masterpiece_id,))
    if not nomination_count:
        cursor.execute(
            'delete from masterpieces where id = %s and (%s or user = %s)',
            (masterpiece_id, any_user, user.id))


def process_nomination(cursor):
    if not (user and static.user_actions.nominate in allowed_actions):
        errors.append('Недостаточно прав доступа для номинирования.')
        return
    if not current_round_id:
        return

    if 'remove' in form_vector_names:
        for masterpiece_id in form_vector_names['remove']:
            remove_nomination(cursor, masterpiece_id)

    if 'nominate' not in form:
        return

    ideabox_section = static.ideabox_sections.by_identifier(form['ideabox_section'].value)
    ideabox_stage = static.ideabox_stages.correction if 'correction' in form else static.ideabox_stages.voting
    content = form['content'].value.strip()
    authors_explanation = form['authors_explanation'].value.strip()
    user_comment = form['user_comment'].value.strip()

    content = content.replace('…', '...')
    authors_explanation = authors_explanation.replace('…', '...')
    explanation_prefix = 'Пояснение:'
    if authors_explanation.startswith(explanation_prefix):
        authors_explanation = authors_explanation[len(explanation_prefix):].lstrip()

    if not content:
        errors.append('Не указан креатив.')
        return
    if max(map(len, (content, authors_explanation, user_comment))) >= 1024:
        errors.append('Много букафф. Ниасилил!')
        return

    repeat_count = my.sql.get_unique_one(cursor, '''
        select count(1)
        from masterpieces
        where contest = %s and content = %s and authors_explanation = %s''',
        (static.contest.id, content, authors_explanation))
    if repeat_count > 0:
        errors.append('Этот креатив уже номинирован.')
        return

    category_ids = form.getlist('category')
    if not category_ids and static.nomination_sources.other.category:
        category_ids.append(static.nomination_sources.other.category)
    for category_id in (static.nomination_sources.singleton.category, static.nomination_sources.best.category):
        if category_id:
            category_ids.append(category_id)
    if not category_ids:
        errors.append('Не выбрана ни одна категория.')
        return

    cursor.execute('''
        insert into
            masterpieces(contest, user, ideabox_section, ideabox_stage, content, authors_explanation, user_comment)
        values(%s, %s, %s, %s, %s, %s, %s)''',
        (static.contest.id, user.id, ideabox_section.id, ideabox_stage.id, content, authors_explanation, user_comment))
    masterpiece_id = cursor.connection.insert_id()

    for category_id in category_ids:
        cursor.execute('''
            insert into nominations(contest_round, masterpiece, contest_category, user)
                values(%s, %s, %s, %s)''',
                (current_round_id, masterpiece_id, category_id, user.id))


# Page: review


def print_review(cursor, overview = False):
    current_page = pages.overview if overview else pages.review

    current_coordinates = do_round_selector(cursor, range_type(static.contest_stages.nomination, static.contest_stages.voting))
    if not current_round_id:
        errors.append('Данный раунд голосования недоступен.')
        print_errors()
        return

    for key, value in current_coordinates.to_string_dict().iteritems():
        print '    <input type="hidden" name="' + escape(key) + '" value="' + escape(value) + '">'

    if not current_round_id:
        print '    <center><p>'
        if overview:
            print '        Просмотр окончен.'
        else:
            print '        Рецензирование окончено.'
        print '        Новый раунд голосования пока не создан.'
        print '      <p></center>'
        return
    if not user:
        if overview:
            errors.append('Недостаточно прав доступа для просмотра.')
        else:
            errors.append('Недостаточно прав доступа для рецензирования.')
        print_errors()
        return

    print_round_timing(cursor)

    format = form['format'].value if 'format' in form else None

    order = 'asc' if format == 'forum' else 'desc'

    masterpieces = my.sql.get_named_tuples(cursor, '''
        select
            masterpieces.*,
            nominations.added nomination_date''' + ('' if overview else ''',
            users.name user_name''') + '''
        from
            masterpieces inner join (
                    select masterpiece, max(added) added
                    from nominations
                    where contest_round = %s
                    group by masterpiece
                ) nominations on masterpieces.id = nominations.masterpiece
            left join users on masterpieces.user = users.id
        order by
            masterpieces.added ''' + order + ''',
            masterpieces.id ''' + order,
        (current_round_id,))

    if not masterpieces:
        print '    <div style="text-align: center;">Пока ничего не номинировано.</div>'
        return

    cursor.execute('''
        select nominations.masterpiece, categories.name
        from nominations, contest_categories categories
        where
            nominations.contest_round = %s and
            nominations.contest_category = categories.id
        order by nominations.masterpiece, categories.priority''',
        (current_round_id,))
    masterpiece_nomination_names = fetch_masterpiece_category_names(cursor)

    if format == 'forum':
        print '    <textarea style="width: 100%;" rows="24">'

        print 'ВНИМАНИЕ, ВНИМАНИЕ, ИДЕТ "ГОЛОСОВАНИЕ":' + pages.voting.absolute_url() + ':'
        print

        for category in static.contest_categories:
            if category.nomination_source in (
                    static.nomination_sources.disabled.id,
                    static.nomination_sources.best.id):
                continue

            has_printed_category_name = False
            for masterpiece in masterpieces:
                if category.name in masterpiece_nomination_names[masterpiece.id]:
                    if not has_printed_category_name:
                        has_printed_category_name = True
                        print '_*' + escape(category.name) + '*_'
                        print
                    print_masterpiece_for_forum(masterpiece, hide_authors = True)
                    category_has_masterpieces = True

        print '"Голосуйте":' + pages.voting.absolute_url() + ',',
        print 'и не забывайте "номинировать":' + pages.nomination.absolute_url() + ' креатив на следующий раунд!'

        print '</textarea>'
    else:
        for masterpiece in masterpieces:
            print_nominated_masterpiece(masterpiece, masterpiece_nomination_names, overview)

    print_format_switcher(current_page, current_coordinates)


def process_review(cursor):
    global current_round_id

    if not (user and static.user_actions.review_nominations in allowed_actions):
        errors.append('Недостаточно прав доступа для рецензирования.')
        return

    prepare_selector_view(cursor, range_type(static.contest_stages.nomination, static.contest_stages.voting))
    current_round_id, current_coordinates = get_form_round(cursor)
    if not current_round_id:
        errors.append('Элемент недоступен.')
        return

    redirect_parameters.update(current_coordinates.to_string_dict())

    if 'remove' in form_vector_names:
        for masterpiece_id in form_vector_names['remove']:
            remove_nomination(cursor, masterpiece_id, any_user = True)


# Page: overview


def print_overview(cursor):
    print_review(cursor, overview = True)


def process_overview(cursor):
    pass


# Page: voting


def list_available_categories(cursor):
    global available_categories 
    cursor.execute(
        'select distinct nominations.contest_category from nominations where nominations.contest_round = %s',
        (current_round_id,))
    category_ids = set(sum(cursor.fetchall(), ()))
    hidden_source_ids = (static.nomination_sources.disabled.id, static.nomination_sources.other.id)
    available_categories = list(category
        for category
        in static.contest_categories.values
        if category.id in category_ids and category.nomination_source not in hidden_source_ids)


def prepare_voting(cursor):
    global one_off, category_index, page_subtitle

    one_off = 'one_off' in form and form['one_off'].value == 'yes'

    list_available_categories(cursor)
    
    category_index = 0 if available_categories else None
    if 'category_index' in form:
        if form['category_index'].value == 'review':
            category_index = None
        else:
            category_index_candidate = int(form['category_index'].value)
            if category_index_candidate >= 0 and category_index_candidate < len(available_categories):
                category_index = category_index_candidate
    if category_index is not None:
        page_subtitle = available_categories[category_index].name


def print_voting_closed_message(cursor):
    godville_topic_url = 'http://godville.net/forums/show_topic/' + str(static.contest.godville_topic_id)
    print '    <center><p>'

    if get_current_round_id(cursor, static.contest_stages.results):
        print '        Голосование окончено, результаты приведены на странице «' + pages.results.page_link('результаты') + '».<br>'
    else:
        print '        Нет доступных голосований.'

    if static.user_actions.nominate in allowed_actions and get_current_round_id(cursor, static.contest_stages.nomination):
        print '        Пока можно ' + pages.nomination.page_link('номинировать') + ' креатив на следующий раунд.<br>'

    next_voting_time = get_stage_next_time(cursor, static.contest_stages.voting)
    if next_voting_time:
        next_voting_time_string = datetime2str(next_voting_time, append_relative_day = True, append_when_weekday = True)
        print '        Следующее голосование начнётся в&nbsp;' + next_voting_time_string + '.'

    print '      <p></center>'


def print_voting_category(cursor):
    selected_category = available_categories[category_index]
    trailing_dot = '.' if selected_category.description[-1] not in '.?!' else ''
    print '    <p>'
    print '        Категория <b>«' + escape(selected_category.name) + '»</b> —'
    print '        ' + escape(selected_category.description) + trailing_dot
    print '      </p>'
    print '    <p>'
    print '        Выберите в следующем списке креатив, наиболее подходящий под описание категории.'
    print '        Чтобы проголосовать, нажмите кнопку, расположенную справа от креатива.'
    if not one_off:
        if len(available_categories) > 1:
            print '        После голосования в одной категории автоматически отображается следующая.'
        print '        При необходимости можно вернуться и изменить свой выбор.'
    print '      </p>'

    print '    <input type="hidden" name="category_index" value="' + str(category_index) + '">'
    print '    <input type="hidden" name="category_id" value="' + str(selected_category.id) + '">'
    if one_off:
        print '    <input type="hidden" name="one_off" value="yes">'

    print '    <table style="border-collapse: collapse; width: 100%;">'

    show_voted_only = (
        user and
        selected_category.nomination_source == static.nomination_sources.best.id and
        not ('show' in form and form['show'].value == 'all'))

    if show_voted_only:
        cursor.execute('''
            select votes.masterpiece, categories.name
            from votes, contest_categories categories
            where
                votes.contest_round = %s and
                votes.user = %s and
                votes.contest_category = categories.id and
                votes.contest_category <> %s
            order by votes.masterpiece, categories.priority''',
            (current_round_id, user.id, selected_category.id))
        masterpiece_vote_names = fetch_masterpiece_category_names(cursor)
        if not masterpiece_vote_names:
            show_voted_only = False

    category_id = selected_category.id
    skipped_masterpieces = 0
    for loop_index in (1, 2):
        masterpieces = my.sql.get_named_tuples(cursor, '''
            select masterpieces.*
            from masterpieces, nominations
            where
                nominations.contest_round = %s and
                nominations.contest_category = %s and
                masterpieces.id = nominations.masterpiece
            order by masterpieces.added, masterpieces.id''',
            (current_round_id, category_id))
        for masterpiece in masterpieces:
            if show_voted_only:
                vote_names = masterpiece_vote_names[masterpiece.id]
                if not vote_names:
                    skipped_masterpieces += 1
                    continue
            print '        <tr><td class="ballot">'
            print_masterpiece(' '*12, masterpiece)
            if show_voted_only:
                print '            «' + '», «'.join(vote_names) + '»'
            elif loop_index == 2:
                print '            Не номинировано ни в одной другой категории.'
                skipped_masterpieces -= 1
            print '          </td><td class="ballot">'
            print '            <input type="submit" name="vote.' + str(masterpiece.id) + '" value="»" title="Выбрать!">'
            print '          </td></tr>'

        if not show_voted_only or not static.nomination_sources.other.category:
            break
        category_id = static.nomination_sources.other.category
        show_voted_only = False

    if skipped_masterpieces:
        print '        <tr><td class="ballot" colspan = "2"><center>'
        last_digit = skipped_masterpieces % 10
        verb, unit = (
            ('Скрыто', 'единиц') if last_digit in (0, 5, 6, 7, 8, 9) or skipped_masterpieces % 100 in (11, 12, 13, 14) else
            ('Скрыты', 'единицы') if last_digit in (2, 3, 4) else
            ('Скрыта', 'единица') #if last_digit = 1
        )
        print '            ' + verb + ' ' + str(skipped_masterpieces) + ' ' + unit + ' креатива,'
        print '            за ' + ('которые' if skipped_masterpieces > 1 else 'которую') + ' вы не проголосовали в других категориях.'
        print '            ' + pages.voting.page_link('(показать всё)',
            'category_index=' + str(category_index) +
            '&show=all' +
            ('&one_off=yes' if one_off else ''))
        print '          </center></td></tr>'

    print '        <tr><td class="ballot">'
    print '            Не голосовать в данной категории.<br>'
    print '            <i>(Выберите этот вариант, если ни один из других не подходит.)</i>'
    print '          </td><td class="ballot">'
    print '            <input type="submit" name="abstain" value="»">'
    print '          </td></tr>'

    print '      </table>'


def print_voting_review(cursor):
    # Should tolerate no <code>user</code>.

    print '    <p>'
    print '        Ниже показан ваш выбор по категориям.'
    print '      </p>'
    print '    <input type="hidden" name="category_index" value="review">'

    has_votes = False

    masterpieces = my.sql.get_named_tuples(cursor, '''
        select
            votes.contest_category,
            masterpieces.*
        from
            votes,
            masterpieces
        where
            votes.contest_round = %s and
            votes.user = %s and
            votes.masterpiece = masterpieces.id''',
        (current_round_id, user.id if user else None))
    masterpieces_by_category_id = {}
    for masterpiece in masterpieces:
        masterpieces_by_category_id[masterpiece.contest_category] = masterpiece

    for index, category in enumerate(available_categories):
        masterpiece = masterpieces_by_category_id[category.id] if category.id in masterpieces_by_category_id else None
        print '    <div style="padding: 1ex;">'
        print '        <b>' + escape(category.name) + '</b>'
        print '        ' + pages.voting.page_link(
            '(переголосовать)' if masterpiece else '(проголосовать)',
            'category_index=' + str(index) + '&one_off=yes')
        print '        <div style="padding-left: 4ex;">'
        if masterpiece:
            print_masterpiece(' '*12, masterpiece)
            has_votes = True
        else:
            print '            <i>Ничего не выбрано.</i>'
        print '          </div>'
        print '      </div>'

    if has_votes:
        print '    <div style="text-align: right">'
        print '        <input type="submit" class="seamless" name="abstain_all" value="(Очистить всё)" onclick="return confirm(\x27Удалить выбор во всех категориях?\x27)">'
        print '    </div>'


def print_voting(cursor):
    if not current_round_id:
        print_voting_closed_message(cursor)
        return

    print_round_timing(cursor)

    print '    <center><p>'

    if not available_categories:
        print '        Выбирать пока не из чего — ничего не номинировано.'
        print '      </p></center>'
        return

    for index, category in enumerate(available_categories):
        if index == category_index:
            category_line = '<b>' + category.name + '</b>'
        else:
            category_line = pages.voting.page_link(category.name, 'category_index=' + str(index))
        if index > 0:
            category_line = '| ' + category_line
        print ' '*8 + category_line

    if category_index is not None:
        category_line = pages.voting.page_link('выбранное', 'category_index=review')
    else:
        category_line = '<b>выбранное</b>'
    print ' '*8 + '| ' + category_line

    print '      </p></center>'

    if category_index is not None:
        print_voting_category(cursor)
    else:
        print_voting_review(cursor)


def process_voting(cursor):
    global category_index

    if static.user_actions.vote not in allowed_actions:
        errors.append('Недостаточно прав доступа для голосования.')
        return
    if not current_round_id:
        return

    prepare_voting(cursor)
    if category_index is None:
        if user and 'abstain_all' in form:
            cursor.execute('delete from votes where contest_round = %s and user = %s', (current_round_id, user.id))
            redirect_parameters['category_index'] = 'review'
        return
    category_id = form['category_id'].value
    has_voted = False

    if user and 'abstain' in form:
        cursor.execute(
            'delete from votes where contest_round = %s and contest_category = %s and user = %s',
            (current_round_id, category_id, user.id))
        has_voted = True

    if 'vote' in form_vector_names:
        if not user:
            create_user(cursor)
        for masterpiece_id in form_vector_names['vote']:
            cursor.execute(
                'delete from votes where contest_round = %s and contest_category = %s and user = %s',
                (current_round_id, category_id, user.id))
            cursor.execute(
                'insert into votes(contest_round, contest_category, user, masterpiece) values(%s, %s, %s, %s)',
                (current_round_id, category_id, user.id, masterpiece_id))
        has_voted = True

    if has_voted:
        category_index += 1
        if one_off or category_index >= len(available_categories):
            category_index = None
    redirect_parameters['category_index'] = str(category_index) if category_index is not None else 'review'


# Page: results


def print_results(cursor):
    global current_round_id

    current_coordinates = do_round_selector(cursor, range_type(static.contest_stages.voting, static.contest_stages.results))
    if not current_round_id:
        errors.append('Данный раунд голосования недоступен.')
        print_errors()
        return

    print_round_timing(cursor)

    format = form['format'].value if 'format' in form else None

    preview_round_id = get_current_round_id(cursor, static.contest_stages.voting)

    if current_round_id == preview_round_id and static.user_actions.preview_results not in allowed_actions:
        print '    <center><p>'
        print '        Пока нет результатов.'
        print '      </p></center>'
        return

    if format == 'forum':
        print '    <textarea style="width: 100%;" rows="24">'
        print 'ОБЪЯВЛЯЕМ "РЕЗУЛЬТАТЫ":' + pages.results.absolute_url() + ' ГОЛОСОВАНИЯ:'
        print
    else:
        print '    <div style="padding: 1ex;">'
        print '        <b>Обозначения</b>'
        print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'
        print '            <table><tr>'
        print '                <td bgcolor="blue"><font color="white">&nbsp;зарегистрированные&nbsp;</font></td>'
        print '                <td bgcolor="lightblue" align="center"><font color="black">&nbsp;анонимы&nbsp;</font></td>'
        print '              </tr>'
        print '            <tr>'
        print '                <td colspan="2"><b>' + static.contest.prix_character_html + '</b> победитель в категории</td>'
        print '              </tr></table>'
        print '          </div>'
        print '      </div>'

    cursor.execute('''
        create temporary table current_round_results(
            contest_category int not null,
            masterpiece int not null,
            registered_score int not null,
            score float not null,
            primary key(contest_category, masterpiece))''')
    if current_round_id == preview_round_id:
        cursor.execute('''
            create temporary table current_votes_user(
                contest_category int not null,
                user int not null,
                masterpiece int not null,
                remote_address varchar(255) not null,
                name varchar(255) default null,
                primary key(contest_category, user, masterpiece),
                unique key(contest_category, name(128), remote_address(128)))''')
        cursor.execute('''
            create temporary table current_vote_multiples(
                contest_category int not null,
                remote_address varchar(255) not null,
                multiple_count int not null,
                primary key(contest_category, remote_address(128)))''')
        cursor.execute('''
            insert into
                current_votes_user
            select
                votes.contest_category,
                votes.user,
                votes.masterpiece,
                users.remote_address,
                users.name
            from
                votes inner join users on votes.user = users.id
            where
                votes.contest_round = %s''',
            (current_round_id,))
        cursor.execute('''
            insert into
                current_vote_multiples
            select
                contest_category,
                remote_address,
                count(1) as multiple_count
            from
                current_votes_user
            where
                name is null
            group by
                contest_category,
                remote_address''')
        cursor.execute('''
            insert into
                current_round_results
            select
                votes.contest_category,
                votes.masterpiece,
                count(votes.name)*2 registered_score,
                sum(if(votes.name is null, 1.0/vote_multiples.multiple_count, 2)) score
            from
                current_votes_user votes left join current_vote_multiples vote_multiples on
                    votes.contest_category = vote_multiples.contest_category and
                    votes.remote_address = vote_multiples.remote_address
            group by
                contest_category,
                masterpiece''')
    else:
        cursor.execute('''
            insert into
                current_round_results
            select
                contest_category,
                masterpiece,
                registered_score,
                score
            from
                round_results
            where
                contest_round = %s''',
            (current_round_id,))

    list_available_categories(cursor)
    for category in available_categories:
        if format == 'forum':
            print '—'
            print
            print '_*' + escape(category.name) + '*_'
            print
        else:
            print '    <div style="padding: 1ex;">'
            print '        <b>' + escape(category.name) + '</b>'

        total_score = my.sql.get_unique_one(cursor,
            'select sum(score) from current_round_results where contest_category = %s',
            (category.id,))

        if not total_score:
            if format == 'forum':
                print '_В данной категории ничего не выбрано._'
                print
            else:
                print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'
                print '            В данной категории ничего не выбрано.'
                print '          </div>'
                print '      </div>'
            continue
 
        total_score = float(total_score)
        masterpieces = my.sql.get_named_tuples(cursor, '''
            select
                results.registered_score,
                results.score,
                masterpieces.*,
                users.name as user_name,
                winners.masterpiece is not null as is_winner
            from
                current_round_results results
                inner join masterpieces on results.masterpiece = masterpieces.id
                inner join users on masterpieces.user = users.id
                left join (select * from round_winners where contest_round = %s and contest_category = %s) winners
                    on results.masterpiece = winners.masterpiece
            where
                results.contest_category = %s
            order by
                results.score desc,
                results.registered_score desc,
                masterpieces.added,
                masterpieces.id
            limit 3''',
            (current_round_id, category.id, category.id))

        if current_round_id == preview_round_id:
            winning_score = masterpieces[0].score
            if len(masterpieces) >= 3 and masterpieces[2].score == winning_score:
                winning_score = total_score

        has_winners = False
        for masterpiece in masterpieces:
            if not masterpiece.score:
                continue

            is_winner = (masterpiece.score == winning_score) if current_round_id == preview_round_id else masterpiece.is_winner
            has_winners |= is_winner

            if format == 'forum':
                if is_winner:
                    print_masterpiece_for_forum(masterpiece)
            else:
                registered_percentage = str(int(round(100*masterpiece.registered_score/total_score)))
                anonymous_score = float(masterpiece.score) - masterpiece.registered_score
                anonymous_percentage = str(int(round(100*anonymous_score/total_score)))
                print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'

                print '            <table width="100%"><tr>'
                if registered_percentage != '0':
                    print '                <td bgcolor="blue" width="' + registered_percentage + '%" align="center"><font color="white">' + str(int(round(masterpiece.registered_score))) + '</font></td>'
                if anonymous_percentage != '0':
                    print '                <td bgcolor="lightblue" width="' + anonymous_percentage + '%" align="center"><font color="black">' + str(round(anonymous_score, 1)) + '</font></td>'
                if is_winner:
                    print '                <td><b>' + static.contest.prix_character_html + '</b></td>'
                print '                <td></td>'
                print '              </tr></table>'

                print_masterpiece(' '*12, masterpiece)

                print '          </div>'

        if format == 'forum':
            if not has_winners:
                print '_Победителя выявить не удалось._'
                print
        else:
            print '      </div>'

    if format == 'forum':
        print '—'
        print
        print 'Спасибо всем участникам, и не забывайте "номинировать":' + pages.nomination.absolute_url() + ' креатив на следующий раунд!'

        print '</textarea>'

    print_format_switcher(pages.results, current_coordinates)


def process_results(cursor):
    pass


# Page: registration


def merge_user_into(cursor, source, target):
    if source == target:
        return

    cursor.execute('''
        create temporary table common_votes(
            contest_round int not null,
            contest_category int not null,
            primary key(contest_round, contest_category))''')
    cursor.execute('''
        insert into common_votes(contest_round, contest_category)
            select
                source.contest_round,
                source.contest_category
            from
                votes source,
                votes target
            where
                source.user = %s and
                target.user = %s and
                source.contest_round = target.contest_round and
                source.contest_category = target.contest_category;''',
        (source, target))
    current_voting_round_id = get_current_round_id(cursor, static.contest_stages.voting)
    if current_voting_round_id:
        cursor.execute('''
            delete from votes
            where
                votes.user = %s and
                votes.contest_round = %s and
                votes.contest_category in
                    (select contest_category from common_votes where contest_round = %s)''',
            (target, current_voting_round_id, current_voting_round_id))
        cursor.execute('''
            delete from votes
            where
                votes.user = %s and
                votes.contest_round <> %s''',
            (target, current_voting_round_id))
    else:
        cursor.execute('delete from votes where votes.user = %s', (target,))
    cursor.execute('update votes set user = %s where user = %s', (target, source))

    cursor.execute('update nominations set user = %s where user = %s', (target, source))
    cursor.execute('update masterpieces set user = %s where user = %s', (target, source))

    cursor.execute('''
        create temporary table common_dismissed_notifications(id int not null primary key)''')
    cursor.execute('''
        insert into common_dismissed_notifications(id)
            select
                source.notification as id
            from
                notifications_dismissed_by_users source,
                notifications_dismissed_by_users target
            where
                source.user = %s and
                target.user = %s and
                source.notification = target.notification;''',
        (source, target))
    cursor.execute('''
        delete from notifications_dismissed_by_users
        where
            user = %s and
            notification in
                (select id from common_dismissed_notifications)''',
        (target,))
    cursor.execute('update notifications_dismissed_by_users set user = %s where user = %s', (target, source))

    cursor.execute('delete from user_registrations where user = %s', (source))
    cursor.execute('delete from users where id = %s', (source,))


def get_user_registration(cursor):
    global registration
    registration = my.sql.get_unique_named_tuple(cursor, '''
        select *, (current_timestamp - last_checked) time_passed
        from user_registrations
        where user = %s''', (user.id,))


def check_registration(cursor):
    global refresh
    global registration, retry_registration
    global user

    registration = None
    retry_registration = False

    if not user or user.name:
        return
    if static.user_actions.register not in allowed_actions:
        errors.append('Недостаточно прав доступа для регистрации.')
        return

    get_user_registration(cursor)
    if not registration:
        return
    if registration.time_passed and registration.time_passed <= 25:
        refresh = 30
        return

    cursor.execute(
        'update user_registrations set last_checked = current_timestamp where user = %s', (user.id,))
    try:
        http_connection = httplib.HTTPConnection('godville.net')
        with AutoClose(http_connection):
            http_connection.request('GET', '/gods/api/' + urllib.quote(registration.godname) + '.json')
            response = http_connection.getresponse()
            response_headers = response.getheaders()
            response_text = response.read()
    except IOError:
        retry_registration = True
        errors.append('Не удалось подключиться к серверу Годвилля. Попробуйте повторить позже.')
        return

    if response.status == 404:
        retry_registration = True
        cursor.execute('delete from user_registrations where user = %s', (user.id,))
        errors.append('Неверное имя бога, исправьте и попробуйте ещё раз.')
        return

    if response.status == 502:
        errors.append('Сервера Годвилля сказал «Oops...» Возможно, оно починится само.')
        refresh = 60
        return

    response_parameters = (
        response.status,
        response.msg.gettype(),
        response.msg.getencoding(),
        response.msg.getparam('charset').lower()
    )
    if response_parameters != (200, 'application/json', '7bit', 'utf-8'):
        print_header()
        print '    <p><font color="red">'
        print '        Сервер Годвилля ответил: ' + str(response.status) + ' ' + escape(response.reason) + '<br>'
        print '      </font></p>'
        print '    <p>'
        print escape(response_headers)
        print '      </p>'
        print '    <p>'
        print escape(response_text)
        print '      </p>'
        print_footer()
        exit()

    response_json = json.loads(response_text)

    true_godname = response_json['godname'].encode('utf8')
    if registration.godname != true_godname:
        cursor.execute(
            'update user_registrations set godname = %s where user = %s', (true_godname, user.id))
        get_user_registration(cursor)

    hero_level = response_json['level']
    if hero_level < 20:
        retry_registration = True
        cursor.execute('delete from user_registrations where user = %s', (user.id,))
        errors.append('Слишком низкий уровень героя, для регистрации нужен по крайней мере 20-й уровень.')
        return

    motto = response_json['motto']
    if registration.secret not in motto:
        if 'health' not in response_json:
            errors.append('В <a href="http://godville.net/user/profile" target="_blank">профиле</a> ' +
                'отключена опция «Оперативные данные в API». Включите её на время регистрации.')
        if 'expired' in response_json and response_json['expired'] == 'true':
            errors.append('Герой неактивен. ' +
                'Откройте <a href="http://godville.net/superhero" target="_blank">страницу героя</a>.')
        refresh = 30
        return

    god_user = my.sql.get_unique_named_tuple(cursor,
        'select * from users where name = %s',
        (registration.godname,))
    if god_user:
        merge_user_into(cursor, user.id, god_user.id)
        user = god_user
    else:
        cursor.execute('delete from user_registrations where user = %s', (user.id,))
        cursor.execute('''
            update users
            set
                role = %s,
                registered = current_timestamp,
                name = %s
            where id = %s''',
            (static.user_roles.registered.id, registration.godname, user.id))
        update_user_variable(cursor)
    get_allowed_actions(cursor)
    refresh = 0
    return


def print_registration(cursor):
    if user and user.name:
        print '    <p><b>'
        print '        Поздравляем с регистрацией!'
        print '      </b><p>'
        print '    <p>'
        print '        Теперь вы можете вернуть свой прежний девиз. Ваш ключ: ' + escape(user.password)
        print '      </p>'
        print '    <p>'
        print '        Ключ нужен для входа с других устройств, а также после удаления cookie.<br>'
        print '        Его всегда можно посмотреть и изменить на странице'
        print '        «' + pages.profile.page_link() + '» этого сайта.<br>'
        print '        Его можно восстановить, пройдя регистрацию заново.<br>'
        print '      </p>'
        print_login_check_form()
        return

    godname = registration.godname if registration else ''
    if not registration or retry_registration:
        print '    <p>'
        print '        Регистрация удваивает вес вашего голоса и позволяет заходить на сайт с нескольких устройств.'
        print '        Кроме того, если вы не зарегистрированы на сайте,'
        print '        при повторном голосовании с того же адреса в&nbsp;интернет вес вашего голоса может быть уменьшен.'
        print '      </p>'
        print '    <p>'
        print '        Регистрация на данном сайте производится по имени бога в Годвилле.'
        print '        Зарегистрироваться может любой бог, герой которого достиг хотя бы 20-го уровня.'
        print '        Просто введите своё точное имя бога, нажмите «Далее» и следуйте инструкциям.'
        print '      </p>'
        print '    <p>'
        print '        Имя бога: <input name="godname" value="' + escape(godname) + '">'
        print '        <input type="submit" name="" value="Далее &#62;">'
        print '      </p>'
    else:
        print '    <p>'
        print '        Имя бога: ' + escape(godname)
        print '        <input type="submit" class="seamless" style="color: red;" name="clear_godname" value="X" title="Удалить!">'
        print '      </p>'
        print '    <p>'
        print '        Временно <b>добавьте в начало девиза своего героя число ' + escape(registration.secret) + '</b>.<br>'
        print '        Вернитесь на эту страницу и <b>подождите пару минут</b>.<br>'
        print '        Если ничего не будет происходить — обновите страницу.'
        print '      </p>'


def process_registration(cursor):
    if user and user.name:
        return
    if static.user_actions.register not in allowed_actions:
        errors.append('Недостаточно прав доступа для регистрации.')
        return

    godname = form['godname'].value.strip() if 'godname' in form else ''

    if user and (godname or 'clear_godname' in form):
        cursor.execute('delete from user_registrations where user = %s', (user.id,))

    if godname:
        if not user:
            create_user(cursor)
        secret = str(random.randint(1E5, 1E6-1))
        cursor.execute(
            'insert into user_registrations(user, godname, secret) values(%s, %s, %s)',
            (user.id, godname, secret))
        get_user_registration(cursor)


# Page: profile


def print_profile(cursor):
    if not user:
        errors.append('Профиль не создан.')
        print_errors()
        return
    print_login_check_form()
    print '    <p>'
    print '        Ключ: ' + escape(user.password)
    print '        <input type="submit" class="seamless" name="recreate_password" value="(сменить)">'
    print '      </p>'
    print '    <p>'
    print '        Роль: ' + escape(role.name) + '.'
    print '    <p>'
    allowed_action_names = [action.description for action in allowed_actions]
    allowed_action_names.sort()
    print '      </p>'
    print '        Разрешённые действия: ' + escape(', '.join(allowed_action_names)) + '.'
    print '      </p>'
    print '    <p>'
    print '        <input type="submit" name="logout" value="Выйти">'
    print '      </p>'



def process_profile(cursor):
    global user
    global selected_page

    if user and 'recreate_password' in form:
        if static.user_actions.edit_profile not in allowed_actions:
            errors.append('Недостаточно прав доступа для изменения профиля.')
            return

        cursor.execute('update users set password = %s where id = %s', (random_password(), user.id))
        update_user_variable(cursor)

    if 'logout' in form:
        user = None
        get_allowed_actions(cursor)
        selected_page = pages.entrance


# Page


class Page:
    def __init__(
        self,
        identifier,
        name,
        title,
        contest_stage,
        primary_action,
        print_function,
        process_function
    ):
        self.id = identifier
        self.identifier = identifier

        self.name = name
        self.title = title

        self.contest_stage = contest_stage
        self.primary_action = primary_action

        self.print_function = print_function
        self.process_function = process_function

        self.is_available = True
        self.is_shown = True

    def __eq__(self, other):
        return isinstance(other, Page) and other.identifier == self.identifier
    def __ne__(self, other):
        return not (self == other)
    def disable(self):
        self.is_available = False
        self.is_shown = False
    def hide(self):
        self.is_shown = False
    def page_link(self, name = None, query_parameters = ''):
        if name == None:
            name = self.name
        return '<a class="pagename" href="' + (self.location + query_parameters).rstrip('&?') + '">' + name + '</a>'
    def absolute_url(self, query_parameters = ''):
        if 'SCRIPT_URI' in os.environ:
            url = os.environ['SCRIPT_URI']
        else:
            url = os.environ['REQUEST_SCHEME'] + '://' + os.environ['HTTP_HOST']
        return urlparse.urljoin(url, (self.location + query_parameters).rstrip('&?'))


def init_pages():
    global pages, default_page

    pages = my.sql.Indexed(('id', 'identifier'), (
        Page(
            identifier = 'entrance',
            name = 'вход',
            title = 'Вход',
            contest_stage = None,
            primary_action = static.user_actions.access,
            print_function = print_entrance,
            process_function = process_entrance),
        Page(
            identifier = 'nomination',
            name = 'номинирование',
            title = 'Номинирование',
            contest_stage = static.contest_stages.nomination,
            primary_action = static.user_actions.nominate,
            print_function = print_nomination,
            process_function = process_nomination),
        Page(
            identifier = 'review',
            name = 'рецензирование',
            title = 'Рецензирование',
            contest_stage = static.contest_stages.review,
            primary_action = static.user_actions.review_nominations,
            print_function = print_review,
            process_function = process_review),
        Page(
            identifier = 'overview',
            name = 'просмотр',
            title = 'Просмотр',
            contest_stage = static.contest_stages.review,
            primary_action = static.user_actions.overview_nominations,
            print_function = print_overview,
            process_function = process_overview),
        Page(
            identifier = 'voting',
            name = 'голосование',
            title = 'Голосование',
            contest_stage = static.contest_stages.voting,
            primary_action = static.user_actions.vote,
            print_function = print_voting,
            process_function = process_voting),
        Page(
            identifier = 'results',
            name = 'результаты',
            title = 'Результаты',
            contest_stage = static.contest_stages.results,
            primary_action = static.user_actions.access,
            print_function = print_results,
            process_function = process_results),
        Page(
            identifier = 'profile',
            name = 'профиль',
            title = 'Профиль',
            contest_stage = None,
            primary_action = static.user_actions.edit_profile,
            print_function = print_profile,
            process_function = process_profile),
        Page(
            identifier = 'registration',
            name = 'регистрация',
            title = 'Регистрация',
            contest_stage = None,
            primary_action = static.user_actions.access,
            print_function = print_registration,
            process_function = process_registration)
    ))

    default_page = pages.voting

    for page in pages:
        location = script_name + '?'
        if page != default_page:
            location += 'page=' + page.identifier + '&'
        page.location = location

        if page.primary_action and page.primary_action not in allowed_actions:
            page.disable()

    if pages.review.is_available:
        pages.overview.hide()

    if user and user.name:
        pages.entrance.hide()
        pages.registration.hide()


def select_page(cursor):
    global selected_page
    selected_page = default_page
    if 'page' in form and form['page'].value in pages:
        selected_page = pages[form['page'].value]

    global current_round_id
    if selected_page.contest_stage:
        current_round_id = get_current_round_id(cursor, selected_page.contest_stage)


# notifications


def print_notifications(cursor):
    if not user:
        return

    cursor.execute('''
        select notification, html
        from notifications_and_contests
        where
            contest = %s and
            notification not in
                (select notification from notifications_dismissed_by_users where user = %s)
        order by notification''', (static.contest.id, user.id))

    for notification_id, notification_html in cursor.fetchall():
        print '    <div class="notification">'
        print '        ' + notification_html
        print ('        <input type="submit" class="seamless" style="color: red;"' +
            ' name="dismiss_notification.' + str(notification_id) + '" value="X">')
        print '      </div>'


def process_notifications(cursor):
    if not user:
        return

    if 'dismiss_notification' in form_vector_names:
        for notification_id in form_vector_names['dismiss_notification']:
            cursor.execute(
                'delete from notifications_dismissed_by_users where notification = %s and user = %s',
                (notification_id, user.id));
            cursor.execute(
                'insert into notifications_dismissed_by_users(notification, user) values(%s, %s)',
                (notification_id, user.id));


# main


def print_pagelist():
    print '    <p style="text-align: center;">'
    if user and user.name:
        print '        <i>Ave,', escape(user.name) + '!</i>'
    else:
        print '        <i>Приветствуем, Аноним!</i>'
    for page in pages:
        if page.is_shown:
            if page == selected_page:
                print '        | <b>' + page.name + '</b>'
            else:
                print '        | ' + page.page_link()
    if static.contest.pagelist_suffix:
        print '        ' + static.contest.pagelist_suffix
    print '      </p>'


def print_errors():
    global errors
    print '    <font color="red"><center>'
    for error in errors:
        print '        <p>' + error + '</p>'
    print '      </center></font>'
    errors = []


def maint(cursor):
    for iteration_index in range(0, 4):
        cursor.execute('''
            select stage, round
            from contest_rounds_and_stages
            where tense = %s and contest = %s and ends <= %s''',
            (static.tenses.present.id, static.contest.id, static.start_time))
        for stage, round in cursor.fetchall():
            cursor.execute('''
                update contest_rounds_and_stages
                set tense = null
                where tense = %s and contest = %s and stage = %s''',
                (static.tenses.present.id, static.contest.id, stage))

            if stage == static.contest_stages.voting.id:
                cursor.execute(
                    'delete from round_results where contest_round = %s',
                    (round,))
                cursor.execute(
                    'set @current_contest_round = %s, @current_contest_category = null',
                    (round,))
                cursor.execute('''
                    insert into round_results
                        select @current_contest_round as contest_round, results.*
                            from round_results_view_parametrized results''')
                cursor.execute(
                    'delete from round_winners where contest_round = %s',
                    (round,))
                cursor.execute('''
                    insert into round_winners
                        select * from round_winners_view where contest_round = %s''',
                    (round,))

        stages_has_ended = False

        cursor.execute('''
            select stage, round, begins, ends <= %s as has_already_ended
            from contest_rounds_and_stages
            where tense = %s and contest = %s and begins <= %s''',
            (static.start_time, static.tenses.future.id, static.contest.id, static.start_time))
        for stage, round, begins, has_already_ended in cursor.fetchall():
            cursor.execute('''
                update contest_rounds_and_stages
                set tense = %s
                where tense = %s and contest = %s and stage = %s''',
                (static.tenses.present.id, static.tenses.future.id, static.contest.id, stage))

            stages_has_ended = stages_has_ended or has_already_ended

            league_id, reached_stage, following_round = my.sql.get_unique_row(cursor, '''
                select rounds.league, rounds.reached_stage, following.id
                from contest_rounds rounds left join contest_rounds following on
                    rounds.contest = following.contest and
                    rounds.league = following.league and
                    rounds.ordinal + 1 = following.ordinal
                where rounds.id = %s''',
                (round,))

            if not reached_stage or static.contest_stages[reached_stage].priority < static.contest_stages[stage].priority:
                cursor.execute('update contest_rounds set reached_stage = %s where id = %s', (stage, round))

            if not following_round:
                cursor.execute('''
                    insert into contest_rounds(
                        contest,
                        league,
                        ordinal,
                        upper
                    )
                    select
                        contest,
                        league,
                        ordinal + 1 as ordinal,
                        upper
                    from contest_rounds
                    where id = %s''',
                (round,))
                following_round = cursor.connection.insert_id()

                if league_id == static.leagues.weekly.id:
                    cursor.execute('''
                        insert into contest_rounds_and_stages(contest, round, stage, begins, ends)
                        select contest, %s as round, stage, (begins + interval 7 day), (ends + interval 7 day)
                        from contest_rounds_and_stages
                        where round = %s''',
                    (following_round, round))

            next_round = my.sql.get_unique_one(cursor, '''
                select round
                from contest_rounds_and_stages
                where contest = %s and stage = %s and begins = (
                    select min(begins)
                    from contest_rounds_and_stages
                    where contest = %s and stage = %s and begins > %s)''',
                (static.contest.id, stage, static.contest.id, stage, begins))
            if next_round:
                cursor.execute('''
                    update contest_rounds_and_stages
                    set tense = %s
                    where round = %s and stage = %s''',
                    (static.tenses.future.id, next_round, stage))

        if not stages_has_ended:
            break


def main_with_cursor(cursor):
    maint(cursor)

    global form, form_vector_names, cookie
    form = cgi.FieldStorage(keep_blank_values = True)
    form_vector_names = collections.defaultdict(list)
    for name in form:
        name, separator, parameter = name.partition('.')
        if separator:
            form_vector_names[name].append(parameter)
    cookie = Cookie.SimpleCookie(os.environ['HTTP_COOKIE']) if 'HTTP_COOKIE' in os.environ else Cookie.SimpleCookie()

    global refresh, errors, redirect_parameters, anchor, page_subtitle
    refresh = None
    errors = list(form['errors'].value.split('\n')) if 'errors' in form else []
    redirect_parameters = {}
    anchor = None
    page_subtitle = None

    global remote_address, host_name, script_name
    remote_address = os.environ['REMOTE_ADDR']
    # host_name = os.environ['HTTP_HOST']
    script_name = os.environ['SCRIPT_NAME']

    default_script_name = '/index.py'
    if script_name.endswith(default_script_name):
        script_name = script_name[:1-len(default_script_name)]

    identify_user(cursor)

    init_pages()
    select_page(cursor)

    if os.environ['REQUEST_METHOD'] == 'POST':
        process_notifications(cursor)

        selected_page.process_function(cursor)

        print 'Status: 303 See Other'
        location = selected_page.location
        if errors:
            location += 'errors=' + urllib.quote_plus('\n'.join(errors)) + '&'
        for parameter_name in redirect_parameters:
            location += urllib.quote_plus(parameter_name) + '='
            location += urllib.quote_plus(redirect_parameters[parameter_name]) + '&'
        location = location.rstrip('&?')
        if anchor:
            location += '#' + anchor
        print 'Location:', location
        print_cookies()
        print
        return

    if selected_page.identifier == 'registration':
        check_registration(cursor)
    elif selected_page.identifier == 'voting' and current_round_id:
        prepare_voting(cursor)

    print_header()

    if not selected_page.is_available:
        if static.user_actions.access in allowed_actions:
            errors.append('Недостаточно прав доступа для просмотра данной страницы.')

            print_pagelist()

            print_errors()

            if not (user and user.name):
                print '    <center><p>Возможно, вам нужно ' + pages.registration.page_link('зарегистрироваться') + '.</p></center>'
        else:
            errors.append('Доступ с вашей учётной записи заблокирован.')
            print_errors()
    else:
        print_pagelist()

        if errors:
            print_errors()

        print_notifications(cursor)

        selected_page.print_function(cursor)

    print_footer()


def print_maintenance_page(maintenance_message_html):
    print 'Content-type: text/html; charset=UTF-8'
    print ''
    print '<!doctype html>'
    print '<html><head>'
    print '    <title>Сайт временно недоступен</title>'
    print '  </head><body>'
    print '    <H1>Сайт временно недоступен</H1>'
    print '    ' + maintenance_message_html
    print '  </body></html>'


def main(contest_identifier):
    database = MySQLdb.connect(charset = 'utf8mb4', use_unicode = False, **configuration.database)
    with my.sql.AutoCursor(database) as cursor:
        cursor.execute('set sql_mode = traditional')
        cursor.execute('set time_zone = \x27+3:00\x27')

        maintenance_message_html = my.sql.get_unique_one(cursor, 'select maintenance_message_html from engine')
        if maintenance_message_html:
            print_maintenance_page(maintenance_message_html)
        else:
            static.init(cursor, contest_identifier)
            main_with_cursor(cursor)

