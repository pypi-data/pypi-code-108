#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# postgresql utility methods
# IMIO <support@imio.be>
#

import psycopg2
from system import error, trace

# ------------------------------------------------------------------------------


# dsn="host=localhost port=5432 dbname= user= password="
def openConnection(dsn):
    """ open a postgres connection """
    conn = None
    try:
        conn = psycopg2.connect(dsn)
    except Exception as message:
        msg = "Cannot connect to database with dsn '%s': %s" % (dsn, message)
        error(msg)
        raise Exception(msg)
    return conn

# ------------------------------------------------------------------------------


def insertInTable(dsn, table, columns, vals, TRACE=False):
    """ insert values in a table """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = "insert into %s(%s) values(%s)" % (table, columns, vals)
    trace(TRACE, "Insertion: %s" % req)
    try:
        cursor.execute(req)
        cursor.close()
    except Exception as message:
        conn.rollback()
        error("Cannot insert in database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------


def updateTable(dsn, table, updates, condition='', TRACE=False):
    """ update columns in a table """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = "update %s set %s" % (table, updates)
    if condition:
        req += ' where %s' % condition
    trace(TRACE, "Update: %s" % req)
    try:
        cursor.execute(req)
        cursor.close()
    except Exception as message:
        conn.rollback()
        error("Cannot update in database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------


def selectWithSQLRequest(dsn, sql, TRACE=False):
    """ select multiple lines in a table with a complete sql """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = sql
    trace(TRACE, "Selection: %s" % req)
    try:
        cursor.execute(req)
        data = cursor.fetchall()
        cursor.close()
    except Exception as message:
        error("Cannot select from database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return None
    conn.close()
    return data

# ------------------------------------------------------------------------------


def selectAllInTable(dsn, table, selection, condition='', TRACE=False):
    """ select multiple lines in a table """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = "select %s from %s" % (selection, table)
    if condition:
        req += ' where %s' % condition
    trace(TRACE, "Selection: %s" % req)
    try:
        cursor.execute(req)
        data = cursor.fetchall()
        cursor.close()
    except Exception as message:
        error("Cannot select from database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return None
    conn.close()
    return data

# ------------------------------------------------------------------------------


def selectOneInTable(dsn, table, selection, condition='', TRACE=False):
    """ select a single line in a table """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = "select %s from %s" % (selection, table)
    if condition:
        req += ' where %s' % condition
    trace(TRACE, "Selection: %s" % req)
    try:
        cursor.execute(req)
        data = cursor.fetchone()
        cursor.close()
    except Exception as message:
        error("Cannot select from database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return None
    conn.close()
    return data

# ------------------------------------------------------------------------------


def deleteTable(dsn, table, condition='', TRACE=False):
    """ delete a table """
    conn = openConnection(dsn)
    cursor = conn.cursor()
    req = "delete from %s" % table
    if condition:
        req += ' where %s' % condition
    trace(TRACE, "Deletion : %s" % req)
    try:
        cursor.execute(req)
        cursor.close()
    except Exception as message:
        conn.rollback()
        error("Cannot delete from database : %s" % message)
        error("Request was : '%s'" % req)
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

# ------------------------------------------------------------------------------
