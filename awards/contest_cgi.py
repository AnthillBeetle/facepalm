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


import static


# Utilities


def escape(string):
    return cgi.escape(string, quote = True)


def multiline_escape(string, spacing = ''):
    return escape(string).replace('\r', '').replace('\n', '\n' + spacing + '  <br>')


def random_password():
    string = ''
    for i in xrange(0, 6):
        string += chr(random.randint(0, 255))
    return base64.b64encode(string)


def print_masterpiece_for_forum(masterpiece):
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

    print '@___________________________@'
    print

    print 'bq. ' + ideabox_note + multiline_escape(masterpiece.content.replace('\r', '').replace('\n', ' '))
    print

    if masterpiece.authors_explanation:
        print 'bq. _Пояснение:_ ' + multiline_escape(masterpiece.authors_explanation.replace('\r', '').replace('\n', ' '))
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
        print spacing + '<div class="content"><i>Пояснение:</i> ' + multiline_escape(masterpiece.authors_explanation, spacing) + '</div>'
    print spacing + '<div>'
    if masterpiece.user_comment:
        print spacing + '    <i>' + multiline_escape(masterpiece.user_comment, spacing) + '</i>'
    if 'user_name' in masterpiece._fields:
        print spacing + '    (' + escape(masterpiece.user_name) + ')'
    print spacing + '  </div>'


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
    print '        div.announcement {'
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


# Stage timing


def date2str(date, ):
    return date.strftime('%d.%m.%Y')


def enddate2str(date, __one_second = datetime.timedelta(seconds = 1)):
    date -= __one_second
    return date2str(date)


def print_round_timing(cursor):
    print '    <p style="text-align: center;">'
    current_stages = my.sql.get_indexed_named_tuples(cursor, '''
        select stage id, contest_rounds_and_stages.*
        from contest_rounds_and_stages
        where round = %s''',
        (current_round_id,))
    stages = static.contest_stages
    if stages.publishing.id in current_stages:
        publishing = current_stages[stages.publishing.id]
        if publishing.begins and publishing.ends:
            if selected_page == pages.nomination:
                print '        Номинирование креатива, опубликованного'
            elif selected_page == pages.review:
                print '        Рецензирование креатива, опубликованного'
            elif selected_page == pages.voting:
                print '        Голосование за креатив, опубликованный'
            elif selected_page == pages.results:
                print '        Результаты голосования за креатив, опубликованный'
            print '        с&nbsp;' + date2str(publishing.begins) +' по&nbsp;' + enddate2str(publishing.ends) + '.'
    if stages.voting.id in current_stages:
        voting = current_stages[stages.voting.id]
        if selected_page in (pages.nomination, pages.review):
            verb = 'началось' if voting.begins <= static.start_time else 'начнётся'
            print '        Голосование&nbsp;' + verb + '&nbsp;' + date2str(voting.begins) + '.'
        if selected_page in (pages.voting, pages.results):
            verb = 'окончилось' if voting.ends <= static.start_time else 'окончится'
            print '        Голосование&nbsp;' + verb + '&nbsp;' + enddate2str(voting.ends) + '.'
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
                redirect_parameters['category'] = 'choice'
                return
            errors.append('Неверное имя пользователя или ключ.')

    user = old_user


# Page: nomination


def print_nominated_masterpiece(masterpiece, masterpiece_nomination_names):
    print '    <div style="padding: 1ex;">'
    print_masterpiece(' '*8, masterpiece)
    print '        «' + '», «'.join(masterpiece_nomination_names[masterpiece.id]) + '»'
    if 'nomination_date' in masterpiece._fields:
        print masterpiece.nomination_date.strftime('%d.%m.%Y&nbsp;%H:%M')
    print ('        <input type="submit" class="seamless" style="color: red;" name="remove.' + str(masterpiece.id) +
        '" value="X" onclick="return confirm(\x27Действительно удалить номинированный креатив?\x27)">')
    print '      </div style="padding: 1ex;">'


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
    print '        <select name="ideabox_section">'
    for section in static.ideabox_sections:
        print '            <option value="' + escape(section.identifier) + '">' + escape(section.short_name) + '</option>'
    print '          </select>'

    print ('        (<input type="checkbox" name="correction" id="correction" value="yes">'
        + '<label for="correction">коррекция в операционной</label>):<br>')

    print '        <textarea name="content" id="content" style="width: 100%;"></textarea>',

    print '        <label for="authors_explanation">Пояснение автора креатива или коррекции:</label><br>'
    print '        <textarea name="authors_explanation" id="authors_explanation" style="width: 100%;"></textarea>'

    print '        <label for="user_comment">Ваши комментарии:</label><br>'
    print '        <textarea class="content" name="user_comment" id="user_comment" style="width: 100%;"></textarea>'

    print '    <p style="text-align: justify;">'
    for category in static.contest_categories:
        print '        <span title="' + escape(category.description) + '">'
        if category.is_grand_prix:
            print '            <input type="hidden" name="category" value="' + str(category.id) + '">'
            print ('            <span style="white-space: nowrap;">'
                + '<input type="checkbox" id="category.' + str(category.id) + '" checked disabled></span>'
                + '<label for="false_category.' + str(category.id) + '">'
                + escape(category.name) + '</label>')
        else:
            print ('            <span style="white-space: nowrap;">'
                + '<input type="checkbox" name="category" id="category.' + str(category.id) + '"'
                + ' value="' + str(category.id) + '"></span>'
                + '<label for="category.' + str(category.id) + '">'
                + escape(category.name) + '</label>')
        print '          </span>'
    print '      </p>'

    print '      <input type="submit" name="nominate" value="Номинировать!">'

    is_first = True

    masterpieces = my.sql.get_indexed_named_tuples(cursor, '''
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
    masterpiece_nomination_names = collections.defaultdict(list)
    for masterpiece_id, category_name in cursor.fetchall():
        masterpiece_nomination_names[masterpiece_id].append(category_name)

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

    cursor.execute('''
        insert into
            masterpieces(contest, user, ideabox_section, ideabox_stage, content, authors_explanation, user_comment)
        values(%s, %s, %s, %s, %s, %s, %s)''',
        (static.contest.id, user.id, ideabox_section.id, ideabox_stage.id, content, authors_explanation, user_comment))
    masterpiece_id = cursor.connection.insert_id()

    categories = form.getlist('category')
    for category_id in categories:
        cursor.execute('''
            insert into nominations(contest_round, masterpiece, contest_category, user)
                values(%s, %s, %s, %s)''',
                (current_round_id, masterpiece_id, category_id, user.id))


# Page: review


def print_review(cursor):
    if not current_round_id:
        print '    <center><p>'
        print '        Рецензирование окончено. Новый раунд голосования пока не создан.'
        print '      <p></center>'
        return
    if not user:
        errors.append('Недостаточно прав доступа для рецензирования.')
        print_errors()
        return

    print_round_timing(cursor)

    format = form['format'].value if 'format' in form else None

    order = 'asc' if format else 'desc'

    masterpieces = my.sql.get_indexed_named_tuples(cursor, '''
        select
            masterpieces.*,
            nominations.added nomination_date,
            users.name user_name
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

    if format == 'forum':
        print '    <textarea style="width: 100%;" rows="24" readonly>'

        for masterpiece in masterpieces:
            print_masterpiece_for_forum(masterpiece)

        print '</textarea>'

        print '    <p style="text-align: right;">'
        print '        ' + pages.review.page_link('обычная версия')
        print '      </p>'
    else:
        cursor.execute('''
            select nominations.masterpiece, categories.name
            from nominations, contest_categories categories
            where
                nominations.contest_round = %s and
                nominations.contest_category = categories.id
            order by nominations.masterpiece, categories.priority''',
            (current_round_id,))
        masterpiece_nomination_names = collections.defaultdict(list)
        for masterpiece_id, category_name in cursor.fetchall():
            masterpiece_nomination_names[masterpiece_id].append(category_name)

        for masterpiece in masterpieces:
            print_nominated_masterpiece(masterpiece, masterpiece_nomination_names)

        print '    <p style="text-align: right;">'
        print '        ' + pages.review.page_link('версия для форума', 'format=forum')
        print '      </p>'


def process_review(cursor):
    if not (user and static.user_actions.review_nominations in allowed_actions):
        errors.append('Недостаточно прав доступа для рецензирования.')
        return
    if not current_round_id:
        return

    if 'remove' in form_vector_names:
        for masterpiece_id in form_vector_names['remove']:
            remove_nomination(cursor, masterpiece_id, any_user = True)


# Page: voting


def prepare_voting(cursor):
    global available_categories, selected_category, page_subtitle
    available_categories = static.contest_categories.values
    selected_category = available_categories[0]
    if 'category' in form:
        if form['category'].value == 'choice':
            selected_category = None
        else:
            category_id = int(form['category'].value)
            if category_id in static.contest_categories:
                selected_category = static.contest_categories[category_id]
    if selected_category:
        page_subtitle = selected_category.name


def print_voting_closed_message(cursor):
    godville_topic_url = 'http://godville.net/forums/show_topic/' + str(static.contest.godville_topic_id)
    print '    <center><p>'

    print '        Голосование окончено.'
    print '        Итоги последнего голосования можно найти'
    print '        <a href="' + godville_topic_url + '?page=last">на форуме</a>.'

    next_voting_time = my.sql.get_unique_one(cursor, '''
        select begins
        from current_and_future_stages
        where is_future = True and contest = %s and stage = %s''',
        (static.contest.id, static.contest_stages.voting.id))
    if next_voting_time:
        print '        <br>'
        print '        Следующее голосование начнётся ' + date2str(next_voting_time) + '.'

    print '      <p></center>'


def print_voting_category(cursor):
    trailing_dot = '.' if selected_category.description[-1] not in '.?!' else ''
    print '    <p>'
    print '        Категория <b>«' + escape(selected_category.name) + '»</b> —'
    print '        ' + escape(selected_category.description) + trailing_dot
    print '      </p>'
    print '    <p>'
    print '        Выберите в следующем списке креатив, наиболее подходящий под описание категории.'
    print '        Чтобы проголосовать, нажмите кнопку, расположенную справа от креатива.'
    if 'one_off' not in form:
        if len(static.contest_categories) > 1:
            print '        После голосования в одной категории автоматически отображается следующая.'
        print '        При необходимости можно вернуться и изменить свой выбор.'
    print '      </p>'

    print '    <input type="hidden" name="category" value="' + str(selected_category.id) + '">'
    if 'one_off' not in form:
        if selected_category.index - 1 >= 0:
            previous_category = available_categories[selected_category.index - 1]
            print '    <input type="hidden" name="previous_category" value="' + str(previous_category.id) + '">'
        if selected_category.index + 1 < len(available_categories):
            next_category = available_categories[selected_category.index + 1]
            print '    <input type="hidden" name="next_category" value="' + str(next_category.id) + '">'

    print '    <table style="border-collapse: collapse; width: 100%;">'

    masterpieces = my.sql.get_indexed_named_tuples(cursor, '''
        select
            masterpieces.*
        from masterpieces, nominations
        where
            nominations.contest_round = %s and
            nominations.contest_category = %s and
            masterpieces.id = nominations.masterpiece
        order by masterpieces.added, masterpieces.id''',
        (current_round_id, selected_category.id))
    for masterpiece in masterpieces:
        print '        <tr><td class="ballot">'
        print_masterpiece(' '*12, masterpiece)
        print '          </td><td class="ballot">'
        print '            <input type="submit" name="vote.' + str(masterpiece.id) + '" value="»" title="Выбрать!">'
        print '          </td></tr>'

    print '        <tr><td class="ballot">'
    print '            Не голосовать в данной категории.<br>'
    print '            <i>(Выберите этот вариант, если ни один из других не подходит.)</i>'
    print '          </td><td class="ballot">'
    print '            <input type="submit" name="abstain" value="»">'
    print '          </td></tr>'

    print '      </table>'


def print_voting_choice(cursor):
    # Should tolerate no <code>user</code>.

    print '    <p>'
    print '        Ниже показан ваш выбор по категориям.'
    print '      </p>'

    has_votes = False

    masterpieces = my.sql.get_indexed_named_tuples(cursor, '''
        select
            categories.id category_id,
            categories.name category_name,
            masterpieces.*
        from contest_categories categories
            left join (select * from votes where votes.contest_round = %s and votes.user = %s) votes
                on categories.id = votes.contest_category
            left join masterpieces on votes.masterpiece = masterpieces.id
        where categories.contest = %s
        order by categories.priority''',
        (current_round_id, user.id if user else None, static.contest.id))
    for masterpiece in masterpieces:
        print '    <div style="padding: 1ex;">'
        print '        <b>' + escape(masterpiece.category_name) + '</b>'
        print '        ' + pages.voting.page_link(
            '(переголосовать)' if masterpiece.content else '(проголосовать)',
            'category=' + str(masterpiece.category_id) + '&one_off=yes')
        print '        <div style="padding-left: 4ex;">'
        if masterpiece.content:
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

    for category in available_categories:
        if category == selected_category:
            category_line = '<b>' + category.name + '</b>'
        else:
            category_line = pages.voting.page_link(category.name, 'category=' + str(category.id))
        if category.index > 0:
            category_line = '| ' + category_line
        print ' '*8 + category_line

    if selected_category:
        category_line = pages.voting.page_link('выбранное', 'category=choice')
    else:
        category_line = '<b>выбранное</b>'
    print ' '*8 + '| ' + category_line

    print '      </p></center>'

    if selected_category:
        print_voting_category(cursor)
    else:
        print_voting_choice(cursor)


def process_voting(cursor):
    global selected_page

    if static.user_actions.vote not in allowed_actions:
        errors.append('Недостаточно прав доступа для голосования.')
        return
    if not current_round_id:
        return

    if user and 'abstain_all' in form:
        cursor.execute('delete from votes where contest_round = %s and user = %s', (current_round_id, user.id))
        redirect_parameters['category'] = 'choice'
        return

    if 'category' not in form:
        return
    category_id = form['category'].value

    if user and 'abstain' in form:
        cursor.execute(
            'delete from votes where contest_round = %s and contest_category = %s and user = %s',
            (current_round_id, category_id, user.id))

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

    next_category_id = form['next_category'].value if 'next_category' in form else None
    if 'return' in form:
        next_category_id = form['previous_category'].value if 'previous_category' in form else None
    redirect_parameters['category'] = next_category_id if next_category_id else 'choice'


# Page: results


def print_results(cursor):
    global current_round_id

    results_table = 'round_results'

    preview = 'round' in form and form['round'].value == 'running'
    if preview:
        if static.user_actions.preview_results not in allowed_actions:
            errors.append('Недостаточно прав доступа для просмотра предварительных результатов.')
            print_errors()
            return
        current_round_id = my.sql.get_unique_one(cursor,
            'select round from current_rounds where contest = %s and stage = %s',
            (static.contest.id, static.contest_stages.voting.id))
        results_table = 'round_results_view'

        last_url = script_name + '?page=' + selected_page.identifier
        print '    <p style="text-align: center;">'
        print '        <a class="pagename" href="' + last_url + '">последние</a> |'
        print '        <b>предварительные</b>'
        print '      </p>'

        if not current_round_id:
            print '    <center><p>'
            print '        Голосование окончено. Результаты последнего голосования приведены на странице'
            print '        «<a class="pagename" href="' + last_url + '">последние</a>».'
            print '      </p></center>'
            return
    else:
        if static.user_actions.preview_results in allowed_actions:
            preview_url = script_name + '?page=' + selected_page.identifier + '&round=running'
            print '    <p style="text-align: center;">'
            print '        <b>последние</b> |'
            print '        <a class="pagename" href="' + preview_url + '">предварительные</a>'
            print '      </p>'

        if not current_round_id:
            print '    <center><p>'

            print '        Пока нет результатов.'
            next_results_time = my.sql.get_unique_one(cursor, '''
                select begins
                from current_and_future_stages
                where is_future = True and contest = %s and stage = %s''',
                (static.contest.id, static.contest_stages.results.id))
            if next_results_time:
                print '        <br>'
                print '        Результаты будут объявлены ' + date2str(next_results_time) + '.'
            
            print '      </p></center>'
            return

    print_round_timing(cursor)

    print '    <div style="padding: 1ex;">'
    print '        <b>Обозначения</b>'
    print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'
    print '            <table><tr>'
    print '                <td bgcolor="blue"><font color="white">&nbsp;зарегистрированные&nbsp;</font></td>'
    print '                <td bgcolor="lightblue" align="center"><font color="black">&nbsp;анонимы&nbsp;</font></td>'
    print '              </tr></table>'
    print '          </div>'
    print '      </div>'

    for category in static.contest_categories:
        print '    <div style="padding: 1ex;">'
        print '        <b>' + escape(category.name) + '</b>'

        total_score = my.sql.get_unique_one(cursor,
            'select sum(score) from ' + results_table + ' where contest_round = %s and contest_category = %s',
            (current_round_id, category.id))

        if not total_score:
            print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'
            print '            В данной категории ничего не выбрано.'
            print '          </div>'
            print '      </div>'
            continue
 
        total_score = float(total_score)
        masterpieces = my.sql.get_indexed_named_tuples(cursor, '''
            select
                results.registered_score,
                results.score score,
                masterpieces.*,
                users.name user_name
            from
                ''' + results_table + ''' results,
                masterpieces,
                users
            where
                results.contest_round = %s and
                results.contest_category = %s and
                results.masterpiece = masterpieces.id and
                masterpieces.user = users.id
            order by
                results.score desc,
                results.registered_score desc,
                masterpieces.added,
                masterpieces.id
            limit 3''',
            (current_round_id, category.id))
        for masterpiece in masterpieces:
            if not masterpiece.score:
                continue

            registered_percentage = str(int(round(100*masterpiece.registered_score/total_score)))
            anonymous_score = float(masterpiece.score) - masterpiece.registered_score
            anonymous_percentage = str(int(round(100*anonymous_score/total_score)))
            print '        <div style="padding-left: 4ex; padding-top: 1ex; padding-bottom: 1ex;">'

            print '            <table width="100%"><tr>'
            if registered_percentage != '0':
                print '                <td bgcolor="blue" width="' + registered_percentage + '%" align="center"><font color="white">' + str(int(round(masterpiece.registered_score))) + '</font></td>'
            if anonymous_percentage != '0':
                print '                <td bgcolor="lightblue" width="' + anonymous_percentage + '%" align="center"><font color="black">' + str(round(anonymous_score, 1)) + '</font></td>'
            print '                <td></td>'
            print '              </tr></table>'

            print_masterpiece(' '*12, masterpiece)

            print '          </div>'

        print '      </div>'
        

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
            from votes source, votes target
            where
                source.user = %s and
                target.user = %s and
                source.contest_round = target.contest_round and
                source.contest_category = target.contest_category;''',
        (source, target))
    current_voting_round = my.sql.get_unique_one(cursor,
        'select round from current_rounds where contest = %s and stage = %s',
        (static.contest.id, static.contest_stages.voting.id))
    cursor.execute('''
        delete from votes
        where
            votes.user = %s and
            votes.contest_round = %s and
            votes.contest_category in
                (select contest_category from common_votes where contest_round = %s)''',
        (target, current_voting_round, current_voting_round))
    cursor.execute('''
        delete from votes
        where
            votes.user = %s and
            votes.contest_round <> %s''',
        (target, current_voting_round))
    cursor.execute('update votes set user = %s where user = %s', (target, source))
    cursor.execute('update nominations set user = %s where user = %s', (target, source))
    cursor.execute('update masterpieces set user = %s where user = %s', (target, source))
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
    print '        Разрешённые действия: ' + ', '.join(allowed_action_names) + '.'
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
        self._fields = ('id', 'identifier')

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


def init_pages():
    global pages, default_page

    pages = my.sql.Indexed((
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
        current_round_id = my.sql.get_unique_one(cursor,
            'select round from current_rounds where contest = %s and stage = %s',
            (static.contest.id, selected_page.contest_stage.id))


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
    cursor.execute('''
        select stage, round
        from current_and_future_stages
        where not is_future and contest = %s and ends <= %s''',
        (static.contest.id, static.start_time))
    for stage, round in cursor.fetchall():
        cursor.execute('''
            delete from current_and_future_rounds
            where not is_future and contest = %s and stage = %s''',
            (static.contest.id, stage))
        if stage == static.contest_stages.voting.id:
            cursor.execute(
                'delete from round_results where contest_round = %s',
                (round,))
            cursor.execute('''
                insert into round_results
                    select * from round_results_view where contest_round = %s''',
                (round,))

    cursor.execute('''
        select stage, round
        from current_and_future_stages
        where is_future and contest = %s and begins <= %s''',
        (static.contest.id, static.start_time))
    for stage, round in cursor.fetchall():
        cursor.execute('''
            update current_and_future_rounds
            set is_future = False
            where is_future and contest = %s and stage = %s''',
            (static.contest.id, stage))


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
    elif selected_page.identifier == 'voting':
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
        elif static.contest.announcement:
            print '    <div class="announcement">'
            print '        ' + static.contest.announcement
            print '      </div>'

        selected_page.print_function(cursor)

    print_footer()


def main(contest_identifier):
    database = MySQLdb.connect(charset = 'utf8', use_unicode = False, **configuration.database)
    with my.sql.AutoCursor(database) as cursor:
        cursor.execute('set sql_mode = traditional')
        cursor.execute('set time_zone = \x27+4:00\x27')
        static.init(cursor, contest_identifier)
        main_with_cursor(cursor)

