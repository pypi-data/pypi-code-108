# coding=utf8
"""Record SQL Module

Extends Record module to add support for SQL tables
"""

__author__ = "Chris Nasr"
__copyright__ = "OuroborosCoding"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2020-02-12"

# Python imports
import datetime
from enum import IntEnum
from hashlib import md5
import sys
from time import sleep, time

# Pip imports
import arrow
import pymysql

# Framework imports
from . import DictHelper, JSON, Record_Base

# List of available hosts
__mdHosts = {}

# List of available connection
__mdConnections = {}

# defines
MAX_RETRIES = 3

## ESelect
class ESelect(IntEnum):
	ALL			= 1
	CELL		= 2
	COLUMN		= 3
	HASH		= 4
	HASH_ROWS	= 5
	ROW			= 6

# Duplicate key exception
class DuplicateException(Exception):
	"""DuplicateException class

	Used for raising issues with duplicate records
	"""
	pass

class Literal(object):
	"""Literal

	Used as a value that won't be escaped or parsed
	"""

	def __init__(self, text):
		if not isinstance(text, str):
			raise ValueError('first argument to Literal must be a string')
		self._text = text;
	def __str__(self):
		return self._text
	def get(self):
		return self._text

def _clearConnection(host):
	"""Clear Connection

	Handles removing a connection from the module list

	Args:
		host (str): The host to clear

	Returns:
		None
	"""

	# If we have the connection
	if host in __mdConnections:

		# Try to close the connection
		try:
			__mdConnections[host].close()

			# Sleep for a second
			sleep(1)

		# Catch any exception
		except Exception as e:
			print('\n------------------------------------------------------------')
			print('Unknown exception in Record_MySQL.Commands.__clear')
			print('host = ' + str(host))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

		# Delete the connection
		del __mdConnections[host]

def _connection(host, errcnt = 0):
	"""Connection

	Returns a connection to the given host

	Args:
		host (str): The name of the host to connect to
		errcnt (uint): The current error count

	Returns:
		Connection
	"""

	# If we already have the connection, return it
	if host in __mdConnections:
		return __mdConnections[host]

	# If no such host has been added
	if host not in __mdHosts:
		raise ValueError('no such host "%s"' % str(host))

	# Get the config
	dConf = __mdHosts[host]

	# Create a new connection
	try:
		oCon = pymysql.connect(**__mdHosts[host])

		# Turn autocommit on
		oCon.autocommit(True)

		# Change conversions
		conv = oCon.decoders.copy()
		for k in conv:
			if k in [7]: conv[k] = _converterTimestamp
			elif k in [10,11,12]: conv[k] = str
		oCon.decoders = conv

	# Check for errors
	except pymysql.err.OperationalError as e:

		# Increment the error count
		errcnt += 1

		# If we've hit our max errors, raise an exception
		if errcnt == MAX_RETRIES:
			raise ConnectionError(*e.args)

		# Else just sleep for a second and try again
		else:
			sleep(1)
			return _connection(host, errcnt)

	# Store the connection and return it
	__mdConnections[host] = oCon
	return oCon

def _converterTimestamp(ts):
	"""Converter Timestamp

	Converts timestamps received from MySQL into proper integers

	Args:
		ts (str): The timestamp to convert

	Returns:
		uint
	"""

	# If there is no time
	if ts == '0000-00-00 00:00:00':
		return 0

	# Conver the string to a timestamp and return it
	return arrow.get('%s+00:00' % ts).int_timestamp

def _cursor(host, dictCur = False):
	"""Cursor

	Returns a cursor for the given host

	Args:
		host (str): The name of the host
		dictCur (bool): If true, cursor will use dicts

	Return:
		Cursor
	"""

	# Get a connection to the host
	oCon = _connection(host)

	# Try to get a cursor on the connection
	try:
		if dictCur:
			oCursor = oCon.cursor(pymysql.cursors.DictCursor)
		else:
			oCursor = oCon.cursor()

		# Make sure we're on UTF8
		oCursor.execute('SET NAMES %s' % __mdHosts[host]['charset'])

	except :
		# Clear the connection and try again
		_clearConnection(host)
		return _cursor(host, dictCur)

	# Return the cursor
	return oCursor

def _print_sql(type, host, sql):
	"""Print SQL

	Print out a message with host and SQL information. Useful for debugging
	problems

	Arguments:
		type (str): The type of statment
		host (str): The host the statement will be run on
		sql (str): The SQL to print

	Returns
		None
	"""
	print('----------------------------------------\n%s - %s - %s\n\n%s\n' % (
		host,
		type,
		arrow.get().format('YYYY-MM-DD HH:mm:ss'),
		sql
	))

class _wcursor(object):
	"""_with

	Used with the special Python with method to create a connection that will
	always be closed regardless of exceptions
	"""

	def __init__(self, host, dictCur = False):
		self.cursor = _cursor(host, dictCur);

	def __enter__(self):
		return self.cursor

	def __exit__(self, exc_type, exc_value, traceback):
		self.cursor.close()
		if exc_type is not None:
			return False

def addHost(name, info, update=False):
	"""Add Host

	Add a host that can be used by Records

	Arguments:
		name (str): The name that will be used to fetch the host credentials
		info (dict): The necessary credentials to connect to the host

	Returns:
		bool
	"""

	# If the info isn't already stored, or we want to overwrite it
	if name not in __mdHosts or update:

		# Add default charset if it wasn't passed
		if 'charset' not in info:
			info['charset'] = 'utf8'

		# Store the info
		__mdHosts[name] = info

		# Return OK
		return True

	# Nothing to do, not OK
	return False

def dbCreate(name, host = 'primary', charset=None, collate=None):
	"""DB Create

	Creates a DB on the given host

	Arguments:
		name (str): The name of the DB to create
		host (str): The name of the host the DB will be on
		charset (str): Optional default charset
		collate (str): Optional default collate, charset must be set to use

	Returns:
		bool
	"""

	# Generate the statement
	sSQL = 'CREATE DATABASE IF NOT EXISTS `%s%s`' % (Record_Base.dbPrepend(), name)
	if charset:
		sSQL += ' DEFAULT CHARACTER SET %s' % charset
		if collate:
			sSQL += ' COLLATE %s' % collate

	# Create the DB
	Commands.execute(host, sSQL)
	return True

def dbDrop(name, host = 'primary'):
	"""DB Drop

	Drops a DB on the given host

	Arguments:
		name (str): The name of the DB to delete
		host (str): The name of the host the DB is on

	Returns:
		bool
	"""

	# Delete the DB
	Commands.execute(host, "DROP DATABASE IF EXISTS `%s%s`" % (Record_Base.dbPrepend(), name))
	return True

def verbose(set_=None):
	"""Verbose

	Sets/Gets the debug flag

	Arguments:
		set_ (bool|None): Ignore to get the current value

	Returns
		bool|None
	"""
	if set is None:	return Commands._verbose
	else:			Commands._verbose = set_

# Commands class
class Commands(object):
	"""Commands class

	Used to directly interface with MySQL
	"""

	# Output SQL for debugging?
	_verbose = False

	@classmethod
	def escape(cls, host, value):
		"""Escape

		Used to escape string values for the DB

		Args:
			host (str): The name of the connection to escape for
			value (str): The value to escape
			rel (str): The relationship of the server, master or slave

		Returns:
			str
		"""

		# Get a connection to the host
		oCon = _connection(host)

		# Get the value
		try:
			sRet = oCon.escape_string(value)

		# Else there's an operational problem so close the connection and
		#	restart
		except pymysql.err.OperationalError as e:

			# Clear the connection and try again
			_clearConnection(host)
			return cls.escape(host, value)

		except Exception as e:
			print('\n------------------------------------------------------------')
			print('Unknown Error in Record_MySQL.Commands.escape')
			print('host = ' + host)
			print('value = ' + str(value))
			print('exception = ' + str(e.__class__.__name__))
			print('args = ' + ', '.join([str(s) for s in e.args]))

			# Rethrow
			raise e

		# Return the escaped string
		return sRet

	@classmethod
	def execute(cls, host, sql, errcnt=0):
		"""Execute

		Used to run SQL that doesn't return any rows

		Args:
			host (str): The name of the connection to execute on
			sql (str|tuple): The SQL (or SQL plus a list) statement to run
			errcnt (uint): DO NOT SET, used internally

		Returns:
			uint
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('EXECUTE', host, sql)

		# Fetch a cursor
		with _wcursor(host) as oCursor:

			try:

				# If the sql arg is a tuple we've been passed a string with a list for the purposes
				#	of replacing parameters
				if isinstance(sql, tuple):
					iRet = oCursor.execute(sql[0], sql[1])
				else:
					iRet = oCursor.execute(sql)

				# Return the changed rows
				return iRet

			# If the SQL is bad
			except (pymysql.err.ProgrammingError, pymysql.err.InternalError) as e:

				# Raise an SQL Exception
				raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

			# Else, a duplicate key error
			except pymysql.err.IntegrityError as e:

				# Raise an SQL Duplicate Exception
				raise DuplicateException(e.args[0], e.args[1])

			# Else there's an operational problem so close the connection and
			#	restart
			except pymysql.err.OperationalError as e:
				print('----------------------------------------')
				print('OPERATIONAL ERROR')
				print(e.args)
				print('')

				# If the error code is one that won't change
				if e.args[0] in [1051, 1054, 1136]:
					raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

				# Increment the error count
				errcnt += 1

				# If we've hit our max errors, raise an exception
				if errcnt == MAX_RETRIES:
					raise ConnectionError(*e.args)

				# Clear the connection and try again
				_clearConnection(host)
				return cls.execute(host, sql, errcnt)

			# Else, catch any Exception
			except Exception as e:
				print('\n------------------------------------------------------------')
				print('Unknown Error in Record_MySQL.Commands.execute')
				print('host = ' + host)
				print('sql = ' + str(sql))
				print('exception = ' + str(e.__class__.__name__))
				print('args = ' + ', '.join([str(s) for s in e.args]))

				# Rethrow
				raise e

	@classmethod
	def insert(cls, host, sql, errcnt=0):
		"""Insert

		Handles INSERT statements and returns the new ID. To insert records
		without auto_increment it's best to just stick to CSQL.execute()

		Args:
			host (str): The name of the connection to into on
			sql (str): The SQL statement to run
			errcnt (uint): DO NOT SET, used internally

		Returns:
			mixed
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('INSERT', host, sql)

		# Fetch a cursor
		with _wcursor(host) as oCursor:

			try:

				# If the sql arg is a tuple we've been passed a string with a list for the purposes
				#	of replacing parameters
				if isinstance(sql, tuple):
					oCursor.execute(sql[0], sql[1])
				else:
					oCursor.execute(sql)

				# Get the ID
				mInsertID = oCursor.lastrowid

				# Return the last inserted ID
				return mInsertID

			# If the SQL is bad
			except pymysql.err.ProgrammingError as e:

				# Raise an SQL Exception
				raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

			# Else, a duplicate key error
			except pymysql.err.IntegrityError as e:

				# Raise an SQL Duplicate Exception
				raise DuplicateException(e.args[0], e.args[1])

			# Else there's an operational problem so close the connection and
			#	restart
			except pymysql.err.OperationalError as e:

				# If the error code is one that won't change
				if e.args[0] in [1054]:
					raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

				# Increment the error count
				errcnt += 1

				# If we've hit our max errors, raise an exception
				if errcnt == MAX_RETRIES:
					raise ConnectionError(*e.args)

				# Clear the connection and try again
				_clearConnection(host)
				return cls.insert(host, sql, errcnt)

			# Else, catch any Exception
			except Exception as e:
				print('\n------------------------------------------------------------')
				print('Unknown Error in Record_MySQL.Commands.insert')
				print('host = ' + host)
				print('sql = ' + str(sql))
				print('exception = ' + str(e.__class__.__name__))
				print('args = ' + ', '.join([str(s) for s in e.args]))

				# Rethrow
				raise e

	@classmethod
	def select(cls, host, sql, seltype=ESelect.ALL, field=None, errcnt=0):
		"""Select

		Handles SELECT queries and returns the data

		Args:
			host (str): The name of the host to select from
			sql (str): The SQL statement to run
			seltype (ESelect): The format to return the data in
			field (str): Only used by HASH_ROWS since MySQLdb has no ordereddict
				for associative rows
			errcnt (uint): DO NOT SET, used internally

		Returns:
			mixed
		"""

		# Print debug if requested
		if cls._verbose: _print_sql('SELECT', host, sql)

		# Get a cursor
		bDictCursor = seltype in (ESelect.ALL, ESelect.HASH_ROWS, ESelect.ROW)

		# Fetch a cursor
		with _wcursor(host, bDictCursor) as oCursor:

			try:

				# If the sql arg is a tuple we've been passed a string with a list for the purposes
				#	of replacing parameters
				if isinstance(sql, tuple):
					oCursor.execute(sql[0], sql[1])
				else:
					oCursor.execute(sql)

				# If we want all rows
				if seltype == ESelect.ALL:
					mData = list(oCursor.fetchall())

				# If we want the first cell 0,0
				elif seltype == ESelect.CELL:
					mData = oCursor.fetchone()
					if mData != None:
						mData = mData[0]

				# If we want a list of one field
				elif seltype == ESelect.COLUMN:
					mData = []
					mTemp = oCursor.fetchall()
					for i in mTemp:
						mData.append(i[0])

				# If we want a hash of the first field and the second
				elif seltype == ESelect.HASH:
					mData = {}
					mTemp = oCursor.fetchall()
					for n,v in mTemp:
						mData[n] = v

				# If we want a hash of the first field and the entire row
				elif seltype == ESelect.HASH_ROWS:
					# If the field arg wasn't set
					if field == None:
						raise ValueError('Must specificy a field for the dictionary key when using HASH_ROWS')

					mData = {}
					mTemp = oCursor.fetchall()

					for o in mTemp:
						# Store the entire row under the key
						mData[o[field]] = o

				# If we want just the first row
				elif seltype == ESelect.ROW:
					mData = oCursor.fetchone()

				# Return the results
				return mData

			# If the SQL is bad
			except pymysql.err.ProgrammingError as e:

				# Raise an SQL Exception
				raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

			# Else, a duplicate key error
			except pymysql.err.IntegrityError as e:

				# Raise an SQL Duplicate Exception
				raise SqlDuplicateException(e.args[0], e.args[1])

			# Else there's an operational problem so close the connection and
			#	restart
			except pymysql.err.OperationalError as e:

				# If the error code is one that won't change
				if e.args[0] in [1054]:
					raise ValueError(e.args[0], 'SQL error (' + str(e.args[0]) + '): ' + str(e.args[1]) + '\n' + str(sql))

				# Increment the error count
				errcnt += 1

				# If we've hit our max errors, raise an exception
				if errcnt == MAX_RETRIES:
					raise ConnectionError(*e.args)

				# Clear the connection and try again
				_clearConnection(host)
				return cls.select(host, sql, seltype, field, errcnt)

			# Else, catch any Exception
			except Exception as e:
				print('\n------------------------------------------------------------')
				print('Unknown Error in Record_MySQL.Commands.select')
				print('host = ' + host)
				print('sql = ' + str(sql))
				print('exception = ' + str(e.__class__.__name__))
				print('args = ' + ', '.join([str(s) for s in e.args]))

				# Rethrow
				raise e

class Record(Record_Base.Record):
	"""Record

	Extends the base Record class
	"""

	__nodeToSQL = {
		'any': False,
		'base64': False,
		'bool': 'tinyint(1) unsigned',
		'date': 'date',
		'datetime': 'datetime',
		'decimal': 'decimal',
		'float': 'double',
		'int': 'integer',
		'ip': 'char(15)',
		'json': 'text',
		'md5': 'char(32)',
		'price': 'decimal(8,2)',
		'string': False,
		'time': 'time',
		'timestamp': 'timestamp',
		'uint': 'integer unsigned',
		'uuid': 'char(36)',
		'uuid4': 'char(36)'
	}
	"""Node To SQL

	Used as default values for FormatOC Node types to SQL data types
	"""

	@classmethod
	def _nodeToType(cls, node, host):
		"""Node To Type

		Converts the Node type to a valid MySQL field type

		Arguments:
			node (FormatOC.Node): The node we need an SQL type for
			host (str): The host in case we need to escape anything

		Raises:
			ValueError

		Returns:
			str
		"""

		# Get the node's type
		sType = node.type()

		# Can't use any in MySQL
		if sType == 'any':
			raise ValueError('"any" nodes can not be used in Record_MySQL')

		# If the type is a string
		elif sType in ['base64', 'string']:

			# If we have options
			lOptions = node.options()
			if not lOptions is None:

				# Create an enum
				return 'enum(%s)' % (','.join([
					cls.escape(host, sType, s)
					for s in lOptions
				]))

			# Else, need maximum
			else:

				# Get min/max values
				dMinMax = node.minmax()

				# If we have don't have a maximum
				if dMinMax['maximum'] is None:
					raise ValueError('"string" nodes must have a __maximum__ value if __sql__.type is not set in Record_MySQL')

				# If the minimum matches the maximum
				if dMinMax['minimum'] == dMinMax['maximum']:

					# It's a char as all characters must be filled
					return 'char(%d)' % dMinMax['maximum']

				else:

					# long text
					if dMinMax['maximum'] == 4294967296:
						return 'longtext'
					elif dMinMax['maximum'] == 16777216:
						return 'mediumtext'
					elif dMinMax['maximum'] == 65536:
						return 'text'
					else:
						return 'varchar(%d)' % dMinMax['maximum']

		# Else, get the default
		elif sType in cls.__nodeToSQL:
			return cls.__nodeToSQL[sType]

		# Else
		else:
			raise ValueError('"%s" is not a known type to Record_MySQL')

	@classmethod
	def addChanges(cls, _id, changes, custom={}):
		"""Add Changes

		Adds a record to the tables associated _changes table. Useful for
		Record types that can't handle multiple levels and have children
		tables that shouldn't be updated for every change in a single record

		Arguments:
			_id (mixed): The ID of the record the change is associated with
			changes (dict): The dictionary of changes to add
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the table doesn't want changes
		if not dStruct['changes']:
			raise Exception('%s doesn\'t allow for changes' % dStruct['tree']._name)

		# If changes isn't a dict
		if not isinstance(changes, dict):
			raise ValueError('changes', 'must be a dict')

		# If Changes requires fields
		if isinstance(dStruct['changes'], list):

			# If any of the fields are missing
			for k in dStruct['changes']:
				if k not in changes:
					raise Exception('"%s" missing from changes' % k)

		# Generate the INSERT statement
		sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
				'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
					dStruct['db'],
					dStruct['table'],
					dStruct['primary'],
					cls.escape(
						dStruct['host'],
						dStruct['tree'][dStruct['primary']].type(),
						_id
					),
					JSON.encode(changes)
				)

		# Create the changes record
		iRet = Commands.execute(dStruct['host'], sSQL)

		# Return based on the rows changed
		return iRet and True or False

	@classmethod
	def append(cls, _id, array, item, custom={}):
		"""Append

		Adds an item to a given array/list for a specific record

		Arguments:
			_id (mixed): The ID of the record to append to
			array (str): The name of the field with the array
			item (mixed): The value to append to the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise Exception('append method not available in Record_MySQL')

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		raise NotImplementedError('Must implement the "config" method')

	@classmethod
	def contains(cls, _id, array, item, custom={}):
		"""Contains

		Checks if a specific item exist inside a given array/list

		Arguments:
			_id (mixed): The ID of the record to check
			array (str): The name of the field with the array
			item (mixed): The value to check for in the array
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise Exception('contains method not available in Record_MySQL')

	@classmethod
	def count(cls, _id=None, filter=None, custom={}):
		"""Count

		Returns the number of records associated with index or filter

		Arguments:
			_id (mixed): The ID(s) to check
			filter (dict): Additional filter
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Init possible WHERE values
		lWhere = []

		# If there's no primary key, we want all records
		if _id is None:
			pass

		# If we are using the primary key
		else:

			# Append the ID check
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.processValue(dStruct, dStruct['primary'], _id)
			))

		# If we want to filter the data further
		if filter:

			# Go through each value
			for n,v in filter.items():

				# Generate theSQL and append it to the list
				lWhere.append('`%s` %s' % (
					n,
					cls.processValue(dStruct, n, v)
				))

		# Build the statement
		sSQL = 'SELECT COUNT(*) FROM `%s`.`%s` ' \
				'%s ' % (
					dStruct['db'],
					dStruct['table'],
					lWhere and 'WHERE %s' % ' AND '.join(lWhere) or ''
				)

		# Run the request and return the count
		return Commands.select(dStruct['host'], sSQL, ESelect.CELL)

	def create(self, conflict='error', changes=None):
		"""Create

		Adds the record to the DB and returns the primary key

		Arguments:
			conflict (str|list): Must be one of 'error', 'ignore', 'replace',
				or a list of fields to update
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			mixed|None
		"""

		# Make sure conflict arg is valid
		if not isinstance(conflict, (tuple,list)) and \
			conflict not in ('error', 'ignore', 'replace'):
			raise ValueError('conflict', conflict)

		# If the record requires revisions, make the first one
		if self._dStruct['revisions']:
			self._revision(True)

		# Create the string of all fields and values but the primary if it's
		#	auto incremented
		lTemp = [[], []]
		for f in self._dStruct['tree'].keys():

			# If it's the primary key with auto_primary on
			if f == self._dStruct['primary'] and self._dStruct['auto_primary']:

				# If it's a string, add the field and set the value to the
				#	SQL variable
				if isinstance(self._dStruct['auto_primary'], str):

					# Add the field and set the value to the SQL variable
					lTemp[0].append('`%s`' % f)
					lTemp[1].append('@_AUTO_PRIMARY')

			elif f in self._dRecord:
				lTemp[0].append('`%s`' % f)
				if self._dRecord[f] != None:
					lTemp[1].append(self.escape(
						self._dStruct['host'],
						self._dStruct['tree'][f].type(),
						self._dRecord[f]
					))
				else:
					lTemp[1].append('NULL')

		# If we have replace for conflicts
		if conflict == 'replace':
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"%s = VALUES(%s)" % (s, s)
				for s in lTemp[0]
			])

		elif isinstance(conflict, (tuple,list)):
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"%s = VALUES(%s)" % (s, s)
				for s in conflict
			])

		# Else, no update
		else:
			sUpdate = ''

		# Join the fields and values
		sFields	= ','.join(lTemp[0])
		sValues	= ','.join(lTemp[1])

		# Cleanup
		del lTemp

		# Generate the INSERT statement
		sSQL = 'INSERT %sINTO `%s`.`%s` (%s)\n' \
				' VALUES (%s)\n' \
				'%s' % (
					(conflict == 'ignore' and 'IGNORE ' or ''),
					self._dStruct['db'],
					self._dStruct['table'],
					sFields,
					sValues,
					sUpdate
				)

		# If the primary key is auto generated
		if self._dStruct['auto_primary']:

			# If it's a string
			if isinstance(self._dStruct['auto_primary'], str):

				# Set the SQL variable to the requested value
				Commands.execute(self._dStruct['host'], 'SET @_AUTO_PRIMARY = %s' % self._dStruct['auto_primary'])

				# Execute the regular SQL
				Commands.execute(self._dStruct['host'], sSQL)

				# Fetch the SQL variable
				self._dRecord[self._dStruct['primary']] = Commands.select(
					self._dStruct['host'],
					'SELECT @_AUTO_PRIMARY',
					ESelect.CELL
				)

			# Else, assume auto_increment
			else:
				self._dRecord[self._dStruct['primary']] = Commands.insert(
					self._dStruct['host'],
					sSQL
				)

			# Get the return from the primary key
			mRet = self._dRecord[self._dStruct['primary']]

		# Else, the primary key was passed, we don't need to fetch it
		else:
			if not Commands.execute(self._dStruct['host'], sSQL):
				mRet = None
			else:
				mRet = True

		# Clear changed fields
		self._dChanged = {}

		# If changes are required
		if self._dStruct['changes']:

			# Create the changes record
			dChanges = {
				"old": None,
				"new": "inserted"
			}

			# If Changes requires fields
			if isinstance(self._dStruct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in self._dStruct['changes']:
					dChanges[k] = changes[k]

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						self._dStruct['db'],
						self._dStruct['table'],
						self._dStruct['primary'],
						self.escape(
							self._dStruct['host'],
							self._dStruct['tree'][self._dStruct['primary']].type(),
							self._dRecord[self._dStruct['primary']]
						),
						JSON.encode(dChanges)
					)

			# Create the changes record
			Commands.execute(self._dStruct['host'], sSQL)

		# Return
		return mRet

	@classmethod
	def createMany(cls, records, conflict='error', custom={}):
		"""Create Many

		Inserts multiple records at once, returning all their primary keys
		if auto_primary is true, else just returning the number of records
		inserted (or replaced if replace is set to True)

		Arguments:
			records (Record_MySQL.Record[]): A list of Record instances to insert
			conflict (str): Must be one of 'error', 'ignore', 'replace'
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Make sure conflict arg is valid
		if conflict not in ('error', 'ignore', 'replace'):
			raise ValueError('conflict', conflict)

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError('Tables with \'changes\' flag can\'t be inserted using createMany')

		# Create the list of fields
		lFields = []
		for f in dStruct['tree'].keys():

			# If it's not the primary key, or it is but it's not auto incrmented
			if f != dStruct['primary'] or \
				dStruct['auto_primary'] is not True:
				lFields.append(f)

		# If we have revisions, add the field
		if dStruct['revisions']:
			lFields.append(dStruct['rev_field'])

		# Initialise a list of records
		lRecords = []

		# Loop through the records
		for o in records:

			# If the record requires revisions
			if dStruct['revisions']:
				o._revision(True)

			# Loop through the fields
			lValues = []
			for f in lFields:

				# If it's the primary, and auto_primary is a string
				if f == dStruct['primary'] and \
					dStruct['auto_primary'] is not False:

					# If we generate the key ourselves, add it
					if isinstance(dStruct['auto_primary'], str):
						lValues.append('%s' % dStruct['auto_primary'])

				else:

					if f in o and o[f] != None:
						lValues.append(cls.escape(
							dStruct['host'],
							dStruct['tree'][f].type(),
							o[f]
						))
					else:
						lValues.append('NULL')

			# Add the record
			lRecords.append("%s" % ','.join(lValues))

		# If we want to replace duplicate keys
		if conflict == 'replace':
			sUpdate = 'ON DUPLICATE KEY UPDATE %s' % ',\n'.join([
				"`%s` = VALUES(`%s`)" % (lFields[i], lFields[i])
				for i in range(len(lFields))
			])

		# Else, no update
		else:
			sUpdate = ''

		# Generate the INSERT statements
		sSQL = 'INSERT %sINTO `%s`.`%s` (`%s`) ' \
				'VALUES (%s) ' \
				'%s' % (
			(conflict == 'ignore' and 'IGNORE ' or ''),
			dStruct['db'],
			dStruct['table'],
			'`,`'.join(lFields),
			'),('.join(lRecords),
			sUpdate
		)

		# Run the statment
		iRes = Commands.execute(dStruct['host'], sSQL)

		# Return based on the result
		return iRes and True or False

	def delete(self, changes=None):
		"""Delete

		Deletes the record represented by the instance

		Arguments:
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""

		# If the record lacks a primary key (never been created/inserted)
		if self._dStruct['primary'] not in self._dRecord:
			raise KeyError(self._dStruct['primary'])

		# Generate the DELETE statement
		sSQL = 'DELETE FROM `%s`.`%s` WHERE `%s` %s' % (
			self._dStruct['db'],
			self._dStruct['table'],
			self._dStruct['primary'],
			self.processValue(
				self._dStruct,
				self._dStruct['primary'],
				self._dRecord[self._dStruct['primary']]
			)
		)

		# Delete the record
		iRet = Commands.execute(self._dStruct['host'], sSQL)

		# If no record was deleted
		if iRet != 1:
			return False

		# If changes are required
		if self._dStruct['changes']:

			# Create the changes record
			dChanges = {
				"old": self._dRecord,
				"new": None
			}

			# If Changes requires fields
			if isinstance(self._dStruct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in self._dStruct['changes']:
					dChanges[k] = changes[k]

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						self._dStruct['db'],
						self._dStruct['table'],
						self._dStruct['primary'],
						self.escape(
							self._dStruct['host'],
							self._dStruct['tree'][self._dStruct['primary']].type(),
							self._dRecord[self._dStruct['primary']]
						),
						JSON.encode(dChanges)
					)

			# Insert the changes
			Commands.execute(self._dStruct['host'], sSQL)

		# Remove the primary key value so we can't delete again or save
		del self._dRecord[self._dStruct['primary']]

		# Return OK
		return True

	@classmethod
	def deleteGet(cls, _id=None, index=None, custom={}):
		"""Delete Get

		Deletes one or many records by primary key or index and returns how many
		were found/deleted

		Arguments:
			_id (mixed|mixed[]): The primary key(s) to delete or None for all
				records
			index (str): Used as the index instead of the primary key
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Return:
			int
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If changes are required
		if dStruct['changes']:
			raise RuntimeError('Tables with \'changes\' flag can\'t be deleted using deleteGet')

		# If there's no index and at least one ID passed
		if not index and _id:
			if not dStruct['primary']:
				raise DocumentException('Can not delete by primary key if none exists')
			index = dStruct['primary']

		# Build the statement
		sSQL = 'DELETE FROM `%s`.`%s`' % (dStruct['db'], dStruct['table'])

		# If we have ID(s)
		if _id is not None:
			sSQL += ' WHERE `%s` %s' % (index, cls.processValue(dStruct, index, _id))

		# Delete the records
		return Commands.execute(dStruct['host'], sSQL)

	# escape method
	@classmethod
	def escape(cls, host, type_, value):
		"""Escape

		Takes a value and turns it into an acceptable string for SQL

		Args:
			host (str): The name of the host if we need to call the server
			type_ (str): The type of data to escape
			value (mixed): The value to escape

		Returns:
			str
		"""

		# If it's a literal
		if isinstance(value, Literal):
			return value.get()

		elif value is None:
			return 'NULL'

		else:

			# If we're escaping a bool
			if type_ == 'bool':

				# If it's already a bool or a valid int representation
				if isinstance(value, bool) or (isinstance(value, (int,long)) and value in [0,1]):
					return (value and '1' or '0')

				# Else if it's a string
				elif isinstance(value, str):

					# If it's t, T, 1, f, F, or 0
					return (value in ('true', 'True', 'TRUE', 't', 'T', '1') and '1' or '0')

			# Else if it's a date, md5, or UUID, return as is
			elif type_ in ('base64', 'date', 'datetime', 'md5', 'time', 'uuid', 'uuid4'):
				return "'%s'" % value

			# Else if the value is a decimal value
			elif type_ in ('decimal', 'float', 'price'):
				return str(float(value))

			# Else if the value is an integer value
			elif type_ in ('int', 'uint'):
				return str(int(value))

			# Else if it's a timestamp
			elif type_ == 'timestamp' and (isinstance(value, int) or re.match('^\d+$', value)):
				return 'FROM_UNIXTIME(%s)' % str(value)

			# Else it's a standard escape
			else:
				return "'%s'" % Commands.escape(host, value)

	@classmethod
	def exists(cls, _id, index=None, custom={}):
		"""Exists

		Returns true if the specified primary key or unique index value exists

		Arguments:
			_id (mixed): The primary key to check
			index (str): Used as the index instead of the primary key
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If an index was passed
		if index is not None:

			# Use filter to check for the record
			if not cls.filter({index: _id}, raw=[dStruct['primary']], limit=1, custom=custom):
				return False

		# Else, assume an ID
		else:

			# Use the get method to check for the record
			if not cls.get(_id, raw=[dStruct['primary']], custom=custom):
				return False

		# If anything was returned, the key exists
		return True

	def fieldSet(self, field, val):
		"""Field Set

		Overwrites Record_Base.Record.fieldSet to allow for setting Literals,
		values that are not verified and then sent to the server as is

		Arguments:
			field (str): The name of the field to set
			val (mixed): The value to set the field to

		Returns:
			self for chaining

		Raises:
			KeyError: field doesn't exist in the structure of the record
			ValueError: value is not valid for the field
		"""

		# If the value is actually a literal, accept it as is
		if isinstance(val, Literal):
			self._dRecord[field] = val

		# Else, allow the parent to validate the value
		else:
			super().fieldSet(field, val)

	# filter static method
	@classmethod
	def filter(cls, fields, raw=None, distinct=False, orderby=None, limit=None, custom={}):
		"""Filter

		Finds records based on the specific fields and values passed

		Arguments:
			fields (dict): A dictionary of field names to the values they
				should match
			raw (bool|list): Return raw data (dict) for all or a set list of
				fields
			distinct (bool): Only return distinct data
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record[]|dict[]
		"""

		# By default we will return multiple records
		bMulti = True

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the SELECT fields
		if raw is None or raw is True:
			sFields = '`%s`' % '`,`'.join(dStruct['tree'].keys())
		else:
			sFields = '`%s`' % '`,`'.join(raw)

		# Go through each value
		lWhere = [];
		for n,v in fields.items():

			# Generate theSQL and append it to the list
			lWhere.append(
				'`%s` %s' % (n, cls.processValue(dStruct, n, v))
			)

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# If the limit isn't set
		if limit is None:
			sLimit = ''

		# Else, generate it
		else:

			# If we got an int
			if isinstance(limit, int):
				sLimit = 'LIMIT %d' % limit
				if limit == 1:
					bMulti = False

			# If we got a tuple/list
			elif isinstance(limit, (list,tuple)):
				sLimit = 'LIMIT %d, %d' % (limit[0], limit[1])
				if limit[1] == 1:
					bMulti = False

			# Else, invalid limit format
			else:
				raise Exception('Invalid limit passed to filter')

		# Build the statement
		sSQL = 'SELECT %s%s FROM `%s`.`%s` ' \
				'WHERE %s ' \
				'%s %s' % (
					distinct and 'DISTINCT ' or '',
					sFields,
					dStruct['db'],
					dStruct['table'],
					' AND '.join(lWhere),
					sOrderBy,
					sLimit
				)

		# If we only want multiple records
		if bMulti:

			# Get all the records
			lRecords = Commands.select(dStruct['host'], sSQL, ESelect.ALL)

			# If there's no data, return an empty list
			if not lRecords:
				return []

			# If Raw requested, return as is
			if raw:
				return lRecords

			# Else create instances for each
			else:
				return [cls(d, custom) for d in lRecords]

		# Else, we want one record
		else:

			# Get one row
			dRecord = Commands.select(dStruct['host'], sSQL, ESelect.ROW)

			# If there's no data, return None
			if not dRecord:
				return None

			# If Raw requested, return as is
			if raw:
				return dRecord

			# Else create an instances
			else:
				return cls(dRecord, custom)

	@classmethod
	def generateConfig(cls, tree, special='mysql', db=None):
		"""Generate Config

		Generates record specific config based on the Format-OC tree passed

		Arguments:
			tree (FormatOC.Tree): the tree associated with the record type
			special (str): The special section used to identify the child info

		Returns:
			dict
		"""

		# Call the parent
		return super().generateConfig(tree, special, db);

	@classmethod
	def get(cls, _id=None, index=None, filter=None, match=None, raw=None, distinct=False, orderby=None, limit=None, custom={}):
		"""Get

		Returns records by primary key or index, can also be given an extra filter

		Arguments:
			_id (str|str[]): The primary key(s) to fetch from the table
			index (str): N/A in MySQL
			filter (dict): Additional filter
			match (tuple): N/A in MySQL
			raw (bool|list): Return raw data (dict) for all or a set list of
				fields
			distinct (bool): Only return distinct data
			orderby (str|str[]): A field or fields to order the results by
			limit (int|tuple): The limit and possible starting point
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			Record|Record[]|dict|dict[]
		"""

		# Don't allow index or match in MySQL
		if index is not None:
			raise Exception('index not a valid argument in Record_MySQL.get')
		if match is not None:
			raise Exception('match not a valid argument in Record_MySQL.get')

		# By default we will return multiple records
		bMulti = True

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the SELECT fields
		if raw is None or raw is True:
			sFields = '`%s`' % '`,`'.join(dStruct['tree'].keys())
		else:
			sFields = '`%s`' % '`,`'.join(raw)

		# Init the where fields
		lWhere = [];

		# If there's an id
		if _id is not None:

			# Add the primary
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.processValue(dStruct, dStruct['primary'], _id)
			))

			# Check if the _id is a single value
			if not isinstance(_id, (dict,list,tuple)) or \
				isinstance(_id, str):
				bMulti = False

		# If there's an additional filter
		if filter:

			# Go through each value
			for n,v in filter.items():

				# Generate theSQL and append it to the list
				lWhere.append(
					'`%s` %s' % (n, cls.processValue(dStruct, n, v))
				)

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# If the limit isn't set
		if limit is None:
			sLimit = ''

		# Else, generate it
		else:

			# If we got an int
			if isinstance(limit, int):
				sLimit = 'LIMIT %d' % limit
				if limit == 1:
					bMulti = False

			# If we got a tuple/list
			elif isinstance(limit, (list,tuple)):
				sLimit = 'LIMIT %d, %d' % (limit[0], limit[1])
				if limit[1] == 1:
					bMulti = False

		# Build the statement
		sSQL = 'SELECT %s%s FROM `%s`.`%s` ' \
				'%s ' \
				'%s %s' % (
					distinct and 'DISTINCT ' or '',
					sFields,
					dStruct['db'],
					dStruct['table'],
					lWhere and 'WHERE %s' % ' AND '.join(lWhere) or '',
					sOrderBy,
					sLimit
				)

		# If we only want multiple records
		if bMulti:

			# Get all the records
			lRecords = Commands.select(dStruct['host'], sSQL, ESelect.ALL)

			# If there's no data, return an empty list
			if not lRecords:
				return []

			# If Raw requested, return as is
			if raw:
				return lRecords

			# Else create instances for each
			else:
				return [cls(d, custom) for d in lRecords]

		# Else, we want one record
		else:

			# Get one row
			dRecord = Commands.select(dStruct['host'], sSQL, ESelect.ROW)

			# If there's no data, return None
			if not dRecord:
				return None

			# If Raw requested, return as is
			if raw:
				return dRecord

			# Else create an instances
			else:
				return cls(dRecord, custom)

	@classmethod
	def getChanges(cls, _id, orderby=None, custom={}):
		"""Get Changes

		Returns the changes record associated with the primary record and table.
		Used by Record types that have the 'changes' flag set

		Arguments:
			_id (mixed): The of the primary record to fetch changes for
			orderby (str|str[]): A field or fields to order the results by
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			dict
		"""

		# By default we will return multiple records
		bMulti = True

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the order isn't set
		if orderby is None:
			sOrderBy = ''

		# Else, generate it
		else:

			# If the field is a list of fields
			if isinstance(orderby, (list, tuple)):

				# Go through each field
				lOrderBy = []
				for i in orderby:
					if isinstance(i, (list,tuple)):
						lOrderBy.append('`%s` %s' % (i[0], i[1]))
					else:
						lOrderBy.append('`%s`' % i)
				sOrderBy = 'ORDER BY %s' % ','.join(lOrderBy)

			# Else there's only one field
			else:
				sOrderBy = 'ORDER BY `%s`' % orderby

		# Generate the SELECT statement
		sSQL = 'SELECT `%s`, `created`, `items` ' \
				'FROM `%s`.`%s_changes` ' \
				'WHERE `%s` %s ' \
				'%s' % (
			dStruct['primary'],
			dStruct['db'],
			dStruct['table'],
			dStruct['primary'],
			cls.processValue(dStruct, dStruct['primary'], _id),
			sOrderBy
		)

		# Fetch all records
		lRecords = Commands.select(dStruct['host'], sSQL, ESelect.ALL)

		# Go through each record and turn the items from JSON to dicts
		for i in range(len(lRecords)):
			lRecords[i]['items'] = JSON.decode(lRecords[i]['items'])

		# Return the records
		return lRecords

	# processValue static method
	@classmethod
	def processValue(cls, struct, field, value):
		"""Process Value

		Takes a field and a value or values and returns the proper SQL
		to look up the values for the field

		Args:
			struct (dict): The structure associated with the record
			field (str): The name of the field
			value (mixed): The value as a single item, list, or dictionary

		Returns:
			str
		"""

		# Get the field type
		sType = struct['tree'][field].type()

		# If the value is a list
		if isinstance(value, (list,tuple)):

			# Build the list of values
			lValues = []
			for i in value:
				# If it's None
				if i is None: lValues.append('NULL')
				else: lValues.append(cls.escape(struct['host'], sType, i))
			sRet = 'IN (%s)' % ','.join(lValues)

		# Else if the value is a dictionary
		elif isinstance(value, dict):

			# If it has a start and end
			if 'between' in value:
				sRet = 'BETWEEN %s AND %s' % (
							cls.escape(struct['host'], sType, value['between'][0]),
							cls.escape(struct['host'], sType, value['between'][1])
						)

			# Else if we have a less than
			elif 'lt' in value:
				sRet = '< ' + cls.escape(struct['host'], sType, value['lt'])

			# Else if we have a greater than
			elif 'gt' in value:
				sRet = '> ' + cls.escape(struct['host'], sType, value['gt'])

			# Else if we have a less than equal
			elif 'lte' in value:
				sRet = '<= ' + cls.escape(struct['host'], sType, value['lte'])

			# Else if we have a greater than equal
			elif 'gte' in value:
				sRet = '>= ' + cls.escape(struct['host'], sType, value['gte'])

			# Else if we have a not equal
			elif 'neq' in value:

				# If the value is a list
				if isinstance(value['neq'], (list,tuple)):

					# Build the list of values
					lValues = []
					for i in value['neq']:
						# If it's None
						if i is None: lValues.append('NULL')
						else: lValues.append(cls.escape(struct['host'], sType, i))
					sRet = 'NOT IN (%s)' % ','.join(lValues)

				# Else, it must be a single value
				else:
					if value['neq'] is None: sRet = 'IS NOT NULL'
					else: sRet = '!= ' + cls.escape(struct['host'], sType, value['neq'])

			elif 'like' in value:
				sRet = 'LIKE ' + cls.escape(struct['host'], sType, value['like'])

			# No valid key in dictionary
			else:
				raise ValueError('key must be one of "between", "lt", "gt", "lte", "gte", or "neq"')

		# Else, it must be a single value
		else:

			# If it's None
			if value is None: sRet = 'IS NULL'
			else: sRet = '= ' + cls.escape(struct['host'], sType, value)

		# Return the processed value
		return sRet

	@classmethod
	def remove(cls, _id, array, index, custom={}):
		"""Remove

		Removes an item from a given array/list for a specific record

		Arguments:
			_id (mixed): The ID of the record to remove from
			array (str): The name of the field with the array
			index (uint): The index of the array to remove
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""
		raise Exception('remove method not available in Record_MySQL')

	def save(self, replace=False, changes=None):
		"""Save

		Updates the record in the DB and returns true if anything has changed,
		or a new revision number of the record is revisionable

		Arguments:
			replace (bool): If true, replace all fields instead of updating
			changes (dict): Data needed to store a change record, is
				dependant on the 'changes' config value

		Returns:
			bool
		"""

		# If no fields have been changed, nothing to do
		if not self._dChanged:
			return False

		# If there is no primary key in the record
		if self._dStruct['primary'] not in self._dRecord:
			raise KeyError(self._dStruct['primary'])

		# If revisions are required
		if self._dStruct['revisions']:

			# Store the old revision
			sRevCurr = self._dRecord[self._dStruct['rev_field']]

			# If updating the revision fails
			if not self._revision():
				return False

			# Use the primary key to fetch the record and return the rev
			sSQL = 'SELECT `%s` FROM `%s`.`%s` WHERE `%s` = %s' % (
				self._dStruct['rev_field'],
				self._dStruct['db'],
				self._dStruct['table'],
				self._dStruct['primary'],
				self.escape(
					self._dStruct['host'],
					self._dStruct['tree'][self._dStruct['primary']].type(),
					self._dRecord[self._dStruct['primary']]
				)
			)

			# Select the cell
			sRev = Commands.select(self._dStruct['host'], sSQL, ESelect.CELL)

			# If there's no such record
			if not sRev:
				return False

			# If it is found, but the revisions don't match up
			if sRev != sRevCurr:
				raise Record_Base.RevisionException(
					self._dRecord[self._dStruct['primary']]
				)

		# If a replace was requested, or all fields have been changed
		if replace or (isinstance(self._dChanged, bool) and self._dChanged):
			lKeys = self._dStruct['tree'].keys()
			lKeys.remove(self._dStruct['primary'])
			dValues = {
				k:(k in self._dRecord and self._dRecord[k] or None)
				for k in lKeys
			}

		# Else we are updating
		else:
			dValues = {k:self._dRecord[k] for k in self._dChanged}

		# Go through each value and create the pairs
		lValues = []
		for f in dValues.keys():
			if f != self._dStruct['primary'] or not self._dStruct['auto_primary']:
				if dValues[f] != None:
					lValues.append('`%s` = %s' % (
						f, self.escape(
							self._dStruct['host'],
							self._dStruct['tree'][f].type(),
							dValues[f]
						)
					))
				else:
					lValues.append('`%s` = NULL' % f)

		# Generate SQL
		sSQL = 'UPDATE `%s`.`%s` SET %s ' \
				'WHERE `%s` = %s' % (
					self._dStruct['db'],
					self._dStruct['table'],
					', '.join(lValues),
					self._dStruct['primary'],
					self.escape(
						self._dStruct['host'],
						self._dStruct['tree'][self._dStruct['primary']].type(),
						self._dRecord[self._dStruct['primary']]
					)
				)

		# Update the record
		iRes = Commands.execute(self._dStruct['host'], sSQL)

		# If the record wasn't updated for some reason
		if iRes != 1:
			return False

		# If changes are required
		if self._dStruct['changes'] and changes != False:

			# Create the changes record
			dChanges = self.generateChanges(
				self._dOldRecord,
				self._dRecord
			)

			# If Changes requires fields
			if isinstance(self._dStruct['changes'], list):

				# If they weren't passed
				if not isinstance(changes, dict):
					raise ValueError('changes')

				# Else, add the extra fields
				for k in self._dStruct['changes']:
					dChanges[k] = changes[k]

			# Generate the INSERT statement
			sSQL = 'INSERT INTO `%s`.`%s_changes` (`%s`, `created`, `items`) ' \
					'VALUES(%s, CURRENT_TIMESTAMP, \'%s\')' % (
						self._dStruct['db'],
						self._dStruct['table'],
						self._dStruct['primary'],
						self.escape(
							self._dStruct['host'],
							self._dStruct['tree'][self._dStruct['primary']].type(),
							self._dRecord[self._dStruct['primary']]
						),
						JSON.encode(dChanges)
					)

			# Create the changes record
			Commands.execute(self._dStruct['host'], sSQL)

			# Reset the old record
			self._dOldRecord = None

		# Clear the changed fields flags
		self._dChanged = {}

		# Return OK
		return True

	@classmethod
	def tableCreate(cls, custom={}):
		"""Table Create

		Creates the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the 'create' value is missing
		if 'create' not in dStruct:
			raise ValueError('Record_MySQL.tableCreate requires \'create\' in config. i.e. ["_id", "field1", "field2", "etc"]')

		# If the primary key is added, remove it
		if dStruct['primary'] in dStruct['create']:
			dStruct['create'].remove(dStruct['primary'])

		# Get all child node keys
		lNodeKeys = dStruct['tree'].keys()
		lMissing = [s for s in lNodeKeys if s not in dStruct['create'] and s != dStruct['primary']]

		# If any are missing
		if lMissing:
			raise ValueError('Record_MySQL.tableCreate missing fields `%s` for `%s`.`%s`' % (
				'`, `'.join(lMissing),
				dStruct['db'],
				dStruct['table']
			))

		# Generate the list of fields
		lFields = []
		for f in dStruct['create']:

			# Get the sql special data
			dSQL = dStruct['tree'][f].special('sql', default={})

			# If it's a string
			if isinstance(dSQL, str):
				dSQL = {"type": dSQL}

			# Add the line
			lFields.append('`%s` %s %s' % (
				f,
				('type' in dSQL and dSQL['type'] or cls._nodeToType(dStruct['tree'][f], dStruct['host'])),
				('opts' in dSQL and dSQL['opts'] or (dStruct['tree'][f].optional() and 'null' or 'not null'))
			))

		# If we have a primary key
		if dStruct['primary']:

			# Push the primary key to the front
			#	Get the sql special data
			dSQL = dStruct['tree'][dStruct['primary']].special('sql', default={})

			# If it's a string
			if isinstance(dSQL, str):
				dSQL = {"type": dSQL}

			# Primary key type
			sIDType = 'type' in dSQL and dSQL['type'] or cls._nodeToType(dStruct['tree'][dStruct['primary']], dStruct['host'])
			sIDOpts = 'opts' in dSQL and dSQL['opts'] or 'not null'

			# Add the line
			lFields.insert(0, '`%s` %s %s%s' % (
				dStruct['primary'],
				sIDType,
				(dStruct['auto_primary'] is True and 'auto_increment ' or ''),
				sIDOpts
			))

			# Init the list of indexes
			lIndexes = ['primary key (`%s`)' % dStruct['primary']]

		else:
			lIndexes = []

		# If there are indexes
		if dStruct['indexes']:

			# Make sure it's a dict
			if not isinstance(dStruct['indexes'], dict):
				raise ValueError('Record_MySQL.tableCreate requires \'indexes\' to be a dict')

			# Loop through the indexes to get the name and fields
			for sName,mFields in dStruct['indexes'].items():

				# If the fields are another dict
				if isinstance(mFields, dict):
					sType = next(iter(mFields))
					sFields = '`%s`' %  (isinstance(mFields[sType], (list,tuple)) and \
										'`,`'.join(mFields[sType]) or \
										(mFields[sType] and mFields[sType] or sName))

				# Else if it's a list
				elif isinstance(mFields, (list,tuple)):
					sType = 'index'
					sFields = '`%s`' %  '`,`'.join(mFields)

				# Else, must be a string or None
				else:
					sType = 'index'
					sFields = '`%s`' % (mFields and mFields or sName)

				# Append the index
				lIndexes.append('%s `%s` (%s)' % (
					sType, sName, sFields
				))

			# Combine the indexes
			sIndexes = ', '.join(lIndexes)

		# Generate the CREATE statement
		sSQL = 'CREATE TABLE IF NOT EXISTS `%s`.`%s` (%s, %s) '\
				'ENGINE=%s CHARSET=%s COLLATE=%s' % (
					dStruct['db'],
					dStruct['table'],
					', '.join(lFields),
					', '.join(lIndexes),
					'engine' in dStruct and dStruct['engine'] or 'InnoDB',
					'charset' in dStruct and dStruct['charset'] or 'utf8',
					'collate' in dStruct and dStruct['collate'] or 'utf8_bin'
				)

		# Create the table
		Commands.execute(dStruct['host'], sSQL)

		# If changes are required
		if dStruct['primary'] and dStruct['changes']:

			# Generate the CREATE statement
			sSQL = 'CREATE TABLE IF NOT EXISTS `%s`.`%s_changes` (' \
					'`%s` %s not null %s, ' \
					'`created` datetime not null DEFAULT CURRENT_TIMESTAMP, ' \
					'`items` text not null, ' \
					'index `%s` (`%s`)) ' \
					'ENGINE=%s CHARSET=%s COLLATE=%s' % (
				dStruct['db'],
				dStruct['table'],
				dStruct['primary'],
				sIDType,
				sIDOpts,
				dStruct['primary'], dStruct['primary'],
				'engine' in dStruct and dStruct['engine'] or 'InnoDB',
				'charset' in dStruct and dStruct['charset'] or 'utf8',
				'collate' in dStruct and dStruct['collate'] or 'utf8_bin'
			)

			# Create the table
			Commands.execute(dStruct['host'], sSQL)

		# Return OK
		return True

	@classmethod
	def tableDrop(cls, custom={}):
		"""Table Drop

		Deletes the record's table/collection/etc in the DB

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			bool
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Generate the DROP statement
		sSQL = 'drop table `%s`.`%s`' % (
					dStruct['db'],
					dStruct['table'],
				)

		# Delete the table
		Commands.execute(dStruct['host'], sSQL)

		# If changes are required
		if dStruct['changes']:

			# Generate the DROP statement
			sSQL = 'drop table `%s`.`%s_changes`' % (
						dStruct['db'],
						dStruct['table'],
					)

			# Delete the table
			Commands.execute(dStruct['host'], sSQL)

		# Return OK
		return True

	@classmethod
	def updateField(cls, field, value, _id=None, index=None, filter=None, custom={}):
		"""Updated Field

		Updates a specific field to the value for an ID, many IDs, or the entire
		table

		Arguments:
			field (str): The name of the field to update
			value (mixed): The value to set the field to
			_id (mixed): Optional ID(s) to filter by
			index (str): Optional name of the index to use instead of primary
			filter (dict): Optional filter list to decide what records get updated
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			uint -- Number of records altered
		"""

		# Don't allow index
		if index is not None:
			raise Exception('index not a valid argument in Record_MySQL.updateField')

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# If the field doesn't exist
		if field not in dStruct['tree']:
			raise ValueError('%s not a valid field' % field)

		# Init the where fields
		lWhere = [];

		# Add the primary if passed
		if _id is not None:
			lWhere.append('`%s` %s' % (
				dStruct['primary'],
				cls.processValue(dStruct, dStruct['primary'], _id)
			))

		# If there's an additional filter
		if filter:

			# Go through each value
			for n,v in filter.items():

				# Generate theSQL and append it to the list
				lWhere.append(
					'`%s` %s' % (n, cls.processValue(dStruct, n, v))
				)

		# Generate the SQL to update the field
		sSQL = 'UPDATE `%s`.`%s` ' \
				'SET `%s` %s ' \
				'%s' % (
			dStruct['db'], dStruct['table'],
			field, cls.processValue(dStruct, field, value),
			lWhere and ('WHERE %s' % ' AND '.join(lWhere)) or ''
		)

		# Update all the records and return the number of rows changed
		return Commands.execute(dStruct['host'], sSQL)

	@classmethod
	def uuid(cls, custom={}):
		"""UUID

		Returns a universal unique ID

		Arguments:
			custom (dict): Custom Host and DB info
				'host' the name of the host to get/set data on
				'append' optional postfix for dynamic DBs

		Returns:
			str
		"""

		# Fetch the record structure
		dStruct = cls.struct(custom)

		# Get the UUID
		return Commands.select(dStruct['host'], 'select uuid()', ESelect.CELL)

# Register the module with the Base
Record_Base.registerType('mysql', sys.modules[__name__])
