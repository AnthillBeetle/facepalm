#! /usr/bin/env python2.6
# -*- coding: UTF-8 -*-
'My SQL functions.'

import collections

class AutoCursor:
    'Produces database cursor from connection and closes both on exit.'
    def __init__(self, connection):
        self.__connection = connection
        self.__cursor = connection.cursor()
    def __enter__(self):
        return self.__cursor
    def __exit__(self, exception, value, traceback):
        try:
            if exception:
                self.__connection.rollback()
            else:
                self.__connection.commit()
            self.__cursor.close()
            self.__connection.close()
        except:
            if not exception:
                raise

def insert(cursor, table, values):
    '''Insert values into table.
    
    values must be a column:value dictionary.'''
    if not isinstance(values, dict):
        raise ValueError('values is not a dict.')
    if not values:
        raise ValueError('values is empty')
    names = values.keys()
    sql = (
        'INSERT INTO ' + table + '(' + ', '.join(names) + ') ' +
        'VALUES (:' + ', :'.join(names) + ')')
    return cursor.execute(sql, values)

class CheckError(Exception):
    'Database check error.'
    pass

class QueryError(CheckError):
    'Query error.'
    pass

class UniquenessError(CheckError):
    'Database uniqueness check error.'
    pass

def fetch_unique_row(cursor):
    'Returns unique row.'
    row = cursor.fetchone()
    if not row:
        return row
    if cursor.fetchone():
        raise UniquenessError
    return row

def get_unique_row(cursor, query, *parameters):
    'Returns unique row.'
    cursor.execute(query, *parameters)
    return fetch_unique_row(cursor)

def fetch_unique_one(cursor):
    'Returns unique scalar.'
    row = cursor.fetchone()
    if not row:
        return row
    if cursor.fetchone():
        raise UniquenessError
    if len(row) != 1:
        raise QueryError
    return row[0]

def get_unique_one(cursor, query, *parameters):
    'Returns unique scalar.'
    cursor.execute(query, *parameters)
    return fetch_unique_one(cursor)

def _ifetch(cursor):
    'Iterates <code>cursor</code> rows.'
    while True:
        row = cursor.fetchone()
        if not row:
            break
        yield row

def _ifetch_one(cursor):
    'Iterates <code>cursor</code> values.'
    while True:
        row = cursor.fetchone()
        if not row:
            break
        if len(row) != 1:
            raise QueryError
        yield row[0]

def check_uniqueness(cursor, field):
    '''Makes sure values in field do not repeat.
    
    field must have database.column structure.
    Throws UniquenessError.'''
    view, column = field.rsplit('.', 1)
    column_count = column + '_count'
    cursor.execute(
        'SELECT ' + column + ', count(1) AS ' + column_count +
        ' FROM ' + view +
        ' GROUP BY ' + column +
        ' HAVING ' + column_count + ' > 1')
    if cursor.fetchone():
        raise UniquenessError, field
    return

class ReferenceError(CheckError):
    'Database reference check error.'
    pass

def check_reference(cursor, referrer, referred):
    '''Makes sure there's a value in referred for each value in referrer.
    
    Both referrer and referred must have database.column structure.
    Uniqueness is not checked, use check_uniqueness for this.
    Throws ReferenceError.'''
    referrer_table, _ = referrer.rsplit('.', 1)
    referred_table, _ = referred.rsplit('.', 1)
    cursor.execute(
        'SELECT 1' +
        ' FROM ' + referrer_table + ' LEFT JOIN ' + referred_table +
        ' ON ' + referrer + ' = ' + referred +
        ' WHERE ' + referred + ' IS NULL')
    if cursor.fetchone():
        raise ReferenceError, (referrer, referred)
    return


def define_named_tuple(cursor, preceding_fields = (), following_fields = ()):
    'Returns <code>namedtuple</code> corresponding to current <code>cursor</code> request.'
    fields = preceding_fields + zip(*cursor.description)[0] + following_fields
    return collections.namedtuple('__'.join(fields), fields)

def get_unique_named_tuple(cursor, query, *parameters):
    'Returns unique row as <code>namedtuple</code>.'
    cursor.execute(query, *parameters)
    type = define_named_tuple(cursor)
    row = fetch_unique_row(cursor)
    value = type(*row) if row else None
    return value

class Indexed(object):
    def __init__(self, values):
        values = tuple(values)
        by_id = {}
        by_identifier = {}
        self.__values = values
        self.__by_id = by_id
        self.__by_identifier = by_identifier
        for value in values:
            if 'id' in value._fields:
                by_id[value.id] = value
            if 'identifier' in value._fields:
                by_identifier[value.identifier] = value
                self.__setattr__(value.identifier, value)
    # list-like methods
    def __len__(self):
        return self.__values.__len__()
    def __iter__(self):
        return self.__values.__iter__()
    def __reversed__(self):
        return self.__values.__reversed__()
    @property
    def values(self):
        return self.__values
    # dict-like methods for id
    def __getitem__(self, key):
        return self.__by_id.__getitem__(key)
    def __contains__(self, item):
        return self.__by_id.__contains__(item)
    # dict-like methods for identifier
    def by_identifier(self, identifier):
        return self.__by_identifier[identifier]

def get_indexed_named_tuples(cursor, query, *parameters):
    '''Returns <code>query</code> result as <code>Indexed</code> <code>namedtuple</code> objects.
    
    Utilizes 'id' and 'identifier' columns.'''
    cursor.execute(query, *parameters)
    value_type = define_named_tuple(cursor, ('index', ))
    values = []
    for row in cursor.fetchall():
        value = value_type(len(values), *row)
        values.append(value)
    return Indexed(values)
