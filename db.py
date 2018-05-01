"""
Defines a DB class that connects to a specified mysql instance and manages the atplanta database.

Example usage:

db = DB(host='localhost')

# Add an entry.
db += db.employee(name = "John")

# Get an entry.
employees_named_john = db.employee(name = "John")
employee_named_john = db.employee(name = "John")[0]

# Delete all entries matching a query.
db -= db.employee(name = "John")

# Same as above.
results = db.employee(name = "John")
db -= results

# Delete particular entry.
db -= db.employee(name = "John")[0]

# Same as above.
employee = db.employee(name = "John")[0]
db -= employee

# Change employee name.
db.employee(name = "John")[0].name = "Jack"

# Set employee name to NULL.
del db.employee(name = "John")[0].name

Making a connection will delete tables not specified in the schema, and insert any missing tables.
Currently, table format is not verified on connection, only that they exist.

Debugging information:

debug statements are categorized, specify the category to debug as follows:
DB(debug = {"tables", "rows"})

The current debug categories are supported:
 tables - Print table related housekeeping.
execute - Print all executed SQL statements.
    all - Display all of the above.

Password hashing is provided by this library, and is implemented as a set hook on
password fields.

Thus, password matching can be verified as follows.

import db
dbi = DB()
john = dbi.user(name = "John")[0]
if dbi.hash_pass(password) == john.password:
    ... do stuff on matching password ...

Setting a password requires no call to hash_pass, and in fact doing so will cause issues:
dbi = DB()
dbi.user(name = "John")[0].password = "Foo bar"
"""

import pymysql.cursors
import hashlib
import base64

def _map(fn, xs):
    for x in xs:
        yield fn(x)

class _SQL():

    def _provide_debug(self, categories):
        self.__debug_categories = categories
        return self

    def _debug(self, category, *message):
        """Print the given debug message for the given category."""

        # Only print this message if we are asking for this debug category.
        if 'all' in self.__debug_categories or category in self.__debug_categories:
            print("DB:", *message)

    def _sql(self, sql, values = None, callback = None):
        """Execute the given SQL statement."""

        # Retrieve table list.
        with self.__connection.cursor() as cursor:

            if values is not None:
                self._debug("execute", "Executing statement:", sql, *values)
                cursor.execute(sql, values)

            else:
                self._debug("execute", "Executing statement:", sql)
                cursor.execute(sql)

            if callback is not None:
                return callback(cursor)

    def _provide_connection(self, sql_connection):
        self.__connection = sql_connection
        return self

    def _provide(self, other):
        self.__connection = other.__connection
        self.__debug_categories = other.__debug_categories
        return self

def _lstr(generator, seperator = ", "):
    first = True
    s = ""
    for val in generator:

        if not first:
            s += seperator

        first = False

        s += val

    return s

class _Numeric():

    def __init__(self, fixed, float):
        self.__fixed = fixed
        self.__float = float

    def __str__(self):
        return "NUMERIC(" + str(self.__fixed) + ", " + str(self.__float) + ")"

    def validate(self, value):
        return True

    def transform(self, value):
        return float(value)

    def format(self, value):
        return str(value)

class _Int():

    def __init__(self):
        pass

    def __str__(self):
        return "INT"

    def validate(self, value):
        return True

    def transform(self, value):
        return int(value)

    def format(self, value):
        return str(value)

class _Varchar():

    def __init__(self, length):
        self.__length = length

    def __str__(self):
        return "VARCHAR(" + str(self.__length) + ")"

    def validate(self, value):
        return isinstance(value, str) and len(value) <= self.__length

    def transform(self, value):
        return value

    def format(self, value):
        return  "'" + value + "'"

class _Char():

    def __init__(self, length):
        self.__length = length

    def __str__(self):
        return "CHAR(" + str(self.__length) + ")"

    def validate(self, value):
        return isinstance(value, str) and len(value) == self.__length

    def transform(self, value):
        return value

    def format(self, value):
        return  "'" + value + "'"

class _Boolean():

    def __str__(self):
        return "BOOLEAN"

    def validate(self, value):
        return isinstance(value, bool)

    def transform(self, value):
        return bool(value)

    def format(self, value):
        if value:
            return 'true'
        return 'false'

class _Date():

    def __str__(self):
        return "DATETIME"

    def validate(self, value):
        return True

    def transform(self, value):
        return str(value)

    def format(self, value):
        return "'" + value + "'"

class _Enum():

    def __init__(self, *values):
        self.__values = values

    def __str__(self):

        return 'ENUM(' + _lstr('"' + v + '"' for v in self.__values) + ')'

    def validate(self, value):
        return value in self.__values

    def transform(self, value):
        return str(value)

    def format(self, value):
        return "'" + value + "'"

def hash_pass(password):
   s = hashlib.sha256()
   s.update(password.encode('utf-8'))
   return str(base64.b64encode(s.digest()))[2:-1]

def _remove_visits(db, entry, value):
    try:
        db -= db.visits(property_id = entry.id)
    except:
        pass
    return value

_TABLE_DESCRIPTIONS = {
    'user': {
        'email': {'type': _Varchar(100),
                  'traits': {'unique', 'primary'}},

        'username': {'type': _Varchar(100),
                     'traits': {'unique'}},

        'password': {'type': _Char(44),
                     'hook': {'set': lambda db, e, v: hash_pass(v)}},

        'type': {'type': _Enum('admin', 'owner', 'visitor')}
    },

    'property': {
        'id': {'type': _Int(),
               'traits': {'unique', 'primary', 'auto_increment'},
               'hook': {'set': _remove_visits}},

        'name': {'type': _Varchar(100),
                 'traits': {'unique'},
                 'hook': {'set': _remove_visits}},

        'address': {'type': _Varchar(100),
                    'hook': {'set': _remove_visits}},

        'city': {'type': _Varchar(100),
                 'hook': {'set': _remove_visits}},

        'zip': {'type': _Varchar(5),
                'hook': {'set': _remove_visits}},

        'size': {'type': _Numeric(8, 5),
                 'hook': {'set': _remove_visits}},

        'is_commercial': {'type': _Boolean(),
                          'hook': {'set': _remove_visits}},

        'is_public': {'type': _Boolean(),
                      'hook': {'set': _remove_visits}},

        'owned_by': {'type': _Varchar(100),
                     'hook': {'set': _remove_visits},
                    'foreign': {'references': 'user(email)',
                                'delete': 'cascade',
                                'update': 'cascade'}},

        'approved_by': {'type': _Varchar(100),
                       'traits': {'nullable'},
                        'hook': {'set': _remove_visits},
                       'foreign': {'references': 'user(email)',
                                   'delete': 'set null',
                                   'update': 'cascade'}},

        'type': {'type': _Enum('farm', 'orchard', 'garden'),
                 'hook': {'set': _remove_visits}},
    },

    'item': {
        'name': {'type': _Varchar(100),
                 'traits': {'unique', 'primary'}},

        'approved_by': {'type': _Varchar(100),
                       'traits': {'nullable'},
                       'foreign': {'references': 'user(email)',
                                   'delete': 'set null',
                                   'update': 'cascade'}},

        'category': {'type': _Enum('animal', 'fruit', 'nut', 'flower', 'vegetable')}
    },

    'has': {
        'property_id': {'type': _Int(),
                        'traits': {'primary'},
                        'foreign': {'references': 'property(id)',
                                    'delete': 'cascade',
                                    'update': 'cascade'}},

        'item_name': {'type': _Varchar(100),
                      'traits': {'primary'},
                      'foreign': {'references': 'item(name)',
                                  'delete': 'cascade',
                                  'update': 'cascade'}},

    },

    'visits': {

        'date': {'type': _Varchar(100)},
        'rating': {'type': _Numeric(5, 0)},

        'property_id': {'type': _Int(),
                        'traits': {'primary'},
                        'foreign': {'references': 'property(id)',
                                    'delete': 'cascade',
                                    'update': 'cascade'}},

        'user_email': {'type': _Varchar(100),
                       'traits': {'primary'},
                       'foreign': {'references': 'user(email)',
                                   'delete': 'cascade',
                                   'update': 'cascade'}},

    }
}

# We create this manually as this encodes creation order of tables.
_TABLE_NAMES = [
    'user',
    'property',
    'item',
    'has',
    'visits'
]

def _transform_hook(table, name, db, hook, entry = None, value = None, validate = True, pass_value = False):
    """
    Given an item description, transform a mutation command using any hooks,
    and then validate the result using the type validators.
    """

    row = _TABLE_DESCRIPTIONS[table][name]
    v = None

    if 'hook' in row and hook in row['hook']:
        if pass_value:
            v = row['hook'][hook](db, entry, value)

        else:
            v = row['hook'][hook](db, entry)

        #if validate:
            #if not row['type'].validate(v):
                #raise Exception("Failed to validate input data for form: " + table + '.' + name)

        return v

    return value

def _transform_field(table, name, value):
    if value is not None:
        return _TABLE_DESCRIPTIONS[table][name]['type'].transform(value)
    return None

def _insert_clause(table, fields):

    def conv(k, v):
        if v is None:
            return "NULL"
        return _TABLE_DESCRIPTIONS[table][k]['type'].format(v)

    f = []
    for k, v in fields.items():
        f.append((k, v))

    f = sorted(f, key = lambda v: v[0])

    return _lstr(
         (conv(k, v)
          for k, v
          in f),
    )

def _where_clause(table, fields):

    def gen(k, v):
        if v is None:
            return k + " IS NULL"
        return k + '=' + str(v)

    def conv(k, v):
        if v is None:
            return None
        return _TABLE_DESCRIPTIONS[table][k]['type'].format(v)

    return _lstr(
        (gen(k, v)
         for k, v in
         {k: conv(k, v)
          for k, v
          in fields.items()}.items()),
        seperator = " AND "
    )

class _Result(_SQL):
    def __init__(self, db, name, value):
        self.__name = name
        self.__db = db
        self.__value = value

    def __delattr__(self, name):

        if name not in _TABLE_DESCRIPTIONS[self.__name]:
            pass

        _transform_hook(self.__name, name, self.__db, 'set_null', self)

        query = (
            'UPDATE '
            + self.__name
            + ' SET '
            + name
            + ' = NULL WHERE '
            + _lstr(
                (key + " = '" + value + "'"
                 for key, value
                 in self.__value.items()),
                seperator = " AND "
            )
        )

        self._sql(query)

    def __setattr__(self, name, value):
        if name[0] == '_':
            super().__setattr__(name, value)
            return

        v = _transform_hook(
            self.__name,
            name,
            self.__db,
            'set', self, value,
            pass_value = True
        )

        query = (
            'UPDATE '
            + self.__name
            + ' SET '
            + name
            + ' = '
            + _insert_clause(self.__name, {name: value})
            + ' WHERE '
            + _where_clause(self.__name, self.__value)
        )

        self._sql(query)

        self.__value[name] = value

    def __getattr__(self, name):
        if name not in _TABLE_DESCRIPTIONS[self.__name]:
            pass

        query = (
            'SELECT '
            + name
            + ' FROM '
            + self.__name
            + ' WHERE '
            + _where_clause(self.__name, self.__value)
        )

        value = self._sql(query, callback = lambda c: c.fetchall())[0][name]

        return _transform_field(
            self.__name,
            name,
            _transform_hook(
                self.__name,
                name,
                self.__db,
                'get',
                self,
                value,
                pass_value = True
            )
        )

class _Query(_SQL):
    def __init__(self, db, name, key):

        self.__db = db
        self.__name = name
        self.__key = key
        self.__rows = None

    def _append(self):

        key = {k: _transform_hook(self.__name, k, self.__db, 'set', self, v, pass_value = True)
               for k, v
               in self.__key.items()}

        query = (
            "INSERT INTO "
            + self.__name
            + " ("
            + _lstr(sorted(key for key in self.__key.keys()))
            + " ) VALUES ("
            + _insert_clause(self.__name, key)
            + ")"
        )

        self._sql(query)

    def __resolve(self):
        if self.__rows is not None:
            return

        results = []

        key = {k: _transform_hook(self.__name, k, self.__db, 'get', self, v, pass_value = True)
               for k, v
               in self.__key.items()}

        if len(key) == 0:
            query = (
                'SELECT * FROM '
                + self.__name
            )
        else:
            query = (
                'SELECT * FROM '
                + self.__name
                + ' WHERE '
                + _where_clause(self.__name, key)
            )

        self.__rows = self._sql(query, callback = lambda c: c.fetchall())
        print("Rows before transformation:", self.__rows)

        self.__rows = [{k: _transform_field(self.__name, k, v)
                       for k, v
                       in r.items()}
                       for r in self.__rows]

        print("Rows after transformation:", self.__rows)

    def __getitem__(self, index):
        self.__resolve()

        return _Result(
            self.__db,
            self.__name,
            self.__rows[index]
        )._provide(self)

    def __len__(self):
        self.__resolve()

        return len(self.__rows)

    def _delete(self):

        if len(self.__key) == 0:
            self._sql('DELETE FROM ' + self.__name)
            return

        key = self.__key

        def conv(v):
            if v is None:
                return 'IS NULL'
            else:
                return "= '" + str(v) + "'"

        query = (
            'DELETE FROM '
            + self.__name
            + ' WHERE '
            + _lstr(
                (str(key) + ' '
                 + conv(value)
                 for key, value in key.items()),
                seperator = " AND "
            )
        )

        self.__rows = self._sql(query, callback = lambda c: c.fetchall())

class _Table(_SQL):

    def __init__(self, db, name):
        """Create a new table wrapper."""

        self.__db = db
        self.__name = name

    def __call__(self, **key):

        return _Query(
            self.__db,
            self.__name,
            key
        )._provide(self)

class DB(_SQL):
    """
    A database manager.
    """

    def __init_tables(self):
        """Make sure table layout is legal."""

        tables = self._sql(
            "SHOW TABLES",
            callback = lambda c: [t['Tables_in_atplanta'] for t in c.fetchall()]
        )

        # Print tables we found.
        for table in tables:
            self._debug("table", "Discovered table:", table)

        # Remove every extra table.
        for table in tables:
            if table not in _TABLE_NAMES:
                self._sql("DROP TABLE " + table)
                self._debug("table", "Removed extraneous table:", table)

        # Create missing tables.
        for needed_table in _TABLE_NAMES:
            if needed_table not in tables:

                # Table creation header.
                statement = "CREATE TABLE " + needed_table + " ("

                # Primary key tracker.
                primaries = []

                # Add fields to table creation.
                first = True
                auto_increment = False
                for field, properties in _TABLE_DESCRIPTIONS[needed_table].items():

                    if not first:
                        statement += ", "

                    first = False

                    # Add field name
                    statement += field + " "

                    # Add field type.
                    statement += str(properties['type'])

                    # Check if nullable.
                    if "traits" in properties and ("nullable" not in properties["traits"]):
                        statement += " NOT NULL"

                    # Check if unique.
                    if "traits" in properties and ("unique" in properties["traits"]):
                        statement += " UNIQUE"

                    # Check if primary key.
                    if "traits" in properties and ("primary" in properties["traits"]):
                        primaries.append(field)

                    if "traits" in properties and ("auto_increment" in properties["traits"]):
                        statement += " AUTO_INCREMENT"
                        auto_increment = True

                    # Check if foreign key.
                    if "foreign" in properties:
                        fprops = properties['foreign']

                        statement += ", FOREIGN KEY (" + field + ") REFERENCES " + fprops["references"]
                        if 'update' in fprops:
                            statement += " ON UPDATE " + fprops["update"].upper()
                        if 'delete' in fprops:
                            statement += " ON DELETE " + fprops["delete"].upper()

                # Add primary keys to statement.
                if len(primaries) != 0:
                    if not first:
                        statement += ","
                    statement += ' PRIMARY KEY(' + _lstr(primaries) + ')'

                statement += ") ENGINE = InnoDB"
                self._sql(statement)
                if auto_increment:
                    self._sql("ALTER TABLE " + needed_table + " AUTO_INCREMENT=00000")
                self._debug("table", "Created missing table:", needed_table)

    def __init__(self,
                 host = 'localhost',
                 user = 'root',
                 password = 'password',
                 database = 'atplanta',
                 debug = set()):

        """Connect to the Atplanta database, and initliaze a DB class around it."""

        # Set debug flag.
        self._provide_debug(debug)

        # Our local DB connection.
        self._provide_connection(
            pymysql.connect(
                host = host,
                user = user,
                password = password,
                db = database,
                charset = 'utf8mb4',
                cursorclass = pymysql.cursors.DictCursor,
                autocommit = True
            )
        )

        # Ensure table layout is legal.
        self.__init_tables()

    def __iadd__(self, entry):

        if not isinstance(entry, _Query):
            raise Exception("Can only insert query into the database.")

        entry._append()

        return self

    def __isub__(self, entry):
        if isinstance(entry, _Query) or isinstance(entry, _Row):
            entry._delete()
            return self

        raise Exception("Tried to delete from database with invalid type.")

    def __getattr__(self, name):
        """Returns the named table."""

        # Don't hijack access to attributes that are not part of the schema.
        if name.lower() not in _TABLE_NAMES:
            pass

        return _Table(
            self,
            name
        )._provide(self)
