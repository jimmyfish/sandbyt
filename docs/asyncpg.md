### Install asyncpg with GSSAPI/SSPI support

Source: https://magicstack.github.io/asyncpg/current/installation

Installs asyncpg with optional support for GSSAPI/SSPI authentication. This command installs SSPI on Windows and GSSAPI on other platforms. On Linux, ensure libkrb5-dev or krb5-devel is installed.

```bash
$ pip install 'asyncpg[gssauth]'
```

--------------------------------

### Install asyncpg from source with debug build

Source: https://magicstack.github.io/asyncpg/current/installation

Creates a debug build of asyncpg from a source checkout, including additional runtime checks. This is achieved by setting the ASYNCPG_DEBUG environment variable before installation.

```bash
$ env ASYNCPG_DEBUG=1 pip install -e .
```

--------------------------------

### Install asyncpg with pip

Source: https://magicstack.github.io/asyncpg/current/installation

Standard installation of the asyncpg library using pip. This is the recommended method for most users and requires no external dependencies unless GSSAPI/SSPI authentication is needed.

```bash
$ pip install asyncpg
```

--------------------------------

### Install asyncpg from source with pip

Source: https://magicstack.github.io/asyncpg/current/installation

Installs asyncpg from a local source checkout using pip's editable install option. Requires a C compiler, CPython header files, and the repository to be cloned with --recurse-submodules.

```bash
$ pip install -e .
```

--------------------------------

### Run asyncpg tests

Source: https://magicstack.github.io/asyncpg/current/installation

Executes the test suite for asyncpg. This command requires PostgreSQL to be installed on the system.

```bash
$ python setup.py test
```

--------------------------------

### Basic asyncpg Connection and Fetch Example

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates establishing a basic connection to a PostgreSQL database using asyncpg and fetching all rows from the 'pg_type' table. This example requires an event loop to run and prints the fetched records.

```python
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    types = await con.fetch('SELECT * FROM pg_type')
    print(types)

asyncio.run(run())
```

--------------------------------

### Programmatic SSL Context Configuration (verify-full)

Source: https://magicstack.github.io/asyncpg/current/api/index

Configures an SSL context for a direct SSL connection, equivalent to sslmode=verify-full with certificate verification. It loads a CA bundle for server certificate verification and client certificate/key for authentication. This example demonstrates how to use ssl.create_default_context and sslctx.load_cert_chain for detailed SSL setup.

```python
import asyncpg
import asyncio
import ssl

async def main():
    # Load CA bundle for server certificate verification,
    # equivalent to sslrootcert= in DSN.
    sslctx = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile="path/to/ca_bundle.pem")
    # If True, equivalent to sslmode=verify-full, if False:
    # sslmode=verify-ca.
    sslctx.check_hostname = True
    # Load client certificate and private key for client
    # authentication, equivalent to sslcert= and sslkey= in
    # DSN.
    sslctx.load_cert_chain(
        "path/to/client.cert",
        keyfile="path/to/client.key",
    )
    con = await asyncpg.connect(user='postgres', ssl=sslctx)
    await con.close()

asyncio.run(main())
```

--------------------------------

### Get Execution Plan of a Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Demonstrates how to retrieve the execution plan for a prepared statement using the `explain` method. The `analyze` option can be used to get runtime statistics.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        stmt = await conn.prepare('SELECT 1')
        plan = await stmt.explain()
        print(plan)

        # To get runtime statistics, use analyze=True
        # Be cautious: EXPLAIN ANALYZE executes the statement.
        # Wrap in a transaction to avoid side effects if necessary.
        # async with conn.transaction():
        #     plan_analyze = await stmt.explain(analyze=True)
        #     print(plan_analyze)
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Prepared Statement Usage Example

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to prepare a SQL statement and execute it multiple times using asyncpg. Prepared statements improve performance by allowing the database to parse, analyze, and compile the query once.

```APIDOC
## Prepared Statement Usage Example

### Description
This example shows the basic usage of prepared statements in asyncpg. A statement is prepared using `conn.prepare()`, and then executed multiple times with different parameters using methods like `fetchval()`.

### Method
`Connection.prepare()` followed by statement execution methods (e.g., `PreparedStatement.fetchval()`)

### Endpoint
N/A (This is a client-side API usage example)

### Parameters
N/A

### Request Example
```python
import asyncpg, asyncio

async def run():
    conn = await asyncpg.connect()
    stmt = await conn.prepare('''SELECT 2 ^ $1''')
    print(await stmt.fetchval(10))
    print(await stmt.fetchval(20))

asyncio.run(run())
```

### Response
#### Success Response (200)
Output from executing the prepared statement.

#### Response Example
```
1024.0
1048576.0
```
```

--------------------------------

### Prepare SQL Statement and Get Parameter Types (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Shows how to prepare a SQL statement with parameters and inspect the types of these parameters. This helps in understanding the expected input for the prepared statement.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        stmt = await conn.prepare('SELECT ($1::int, $2::text)')
        print(stmt.get_parameters())
        # Expected output (example):
        #   (Type(oid=23, name='int4', kind='scalar', schema='pg_catalog'),
        #    Type(oid=25, name='text', kind='scalar', schema='pg_catalog'))
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Create asyncpg Connection Pool with examples

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Demonstrates how to create a connection pool using `asyncpg.create_pool`. It shows usage with `async with` for automatic resource management, and direct `await` calls for manual control. It also details the parameters for configuring pool size, timeouts, and connection lifecycle.

```python
import asyncpg

async def example():
    # Usage with async with block
    async with asyncpg.create_pool(user='postgres', command_timeout=60) as pool:
        await pool.fetch('SELECT 1')

    # Usage with direct await (not recommended)
    pool = await asyncpg.create_pool(user='postgres', command_timeout=60)
    con = await pool.acquire()
    try:
        await con.fetch('SELECT 1')
    finally:
        await pool.release(con)
```

--------------------------------

### Connect to PostgreSQL and Fetch Data (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This example demonstrates how to establish a connection to a PostgreSQL database using asyncpg, fetch all records from the 'pg_type' table, and print the results. It requires the 'asyncpg' and 'asyncio' libraries.

```python
>>> import asyncpg
>>> import asyncio
>>> async def run():
...     con = await asyncpg.connect(user='postgres')
...     types = await con.fetch('SELECT * FROM pg_type')
...     print(types)
... 
>>> asyncio.run(run())
[<Record typname='bool' typnamespace=11 ...
```

--------------------------------

### Prepare SQL Statement and Get Query Text (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Demonstrates how to prepare a SQL statement using asyncpg and retrieve the original query string. This is useful for verifying the statement or logging.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        stmt = await conn.prepare('SELECT $1::int')
        assert stmt.get_query() == "SELECT $1::int"
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Pool Connection Acquisition

Source: https://magicstack.github.io/asyncpg/current/api/index

Methods for acquiring and releasing database connections from the pool. Includes examples for both context management and manual handling.

```APIDOC
## GET /acquire

### Description
Acquires a database connection from the pool. The connection can be used within an `async with` block or manually acquired and released.

### Method
GET

### Endpoint
/acquire

### Parameters
#### Query Parameters
- **timeout** (float) - Optional - A timeout for acquiring a Connection.

### Request Example
```python
# Using async with
async with pool.acquire() as con:
    await con.execute('...')

# Manual acquisition and release
con = await pool.acquire()
try:
    await con.execute('...')
finally:
    await pool.release(con)
```

### Response
#### Success Response (200)
- **con** (Connection) - An instance of `Connection`.

#### Response Example
```json
{
  "connection_id": "some_connection_identifier"
}
```
```

--------------------------------

### Get Server Version Information

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates retrieving the version of the connected PostgreSQL server using the `get_server_version` method. The returned value is a named tuple providing detailed version information.

```python
con.get_server_version()
# Example output: sys.version_info(major=14, minor=5, micro=0, releaselevel='final', serial=0)
```

--------------------------------

### Prepare SQL Statement and Get Status Message (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Illustrates preparing a SQL statement and retrieving the status message after execution. This is particularly useful for DDL commands like CREATE TABLE.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        stmt = await conn.prepare('CREATE TABLE mytab (a int)')
        await stmt.fetch()
        assert stmt.get_statusmsg() == "CREATE TABLE"
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Record Object Methods (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Provides examples of using various methods available on asyncpg `Record` objects. These include checking the number of fields (`len`), accessing fields by name or index (`r[field]`), checking for field existence (`name in r`), iterating over values (`iter(r)`), getting a field with a default value (`get()`), and retrieving iterators for values (`values()`), keys (`keys()`), and items (`items()`).

```python
# Assuming 'r' is a Record object
len(r)
r[field]
name in r
iter(r)
r.get(name[, default])
r.values()
r.keys()
r.items()
```

--------------------------------

### Get Connection Settings - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Returns an object containing the configuration settings for the current connection to the PostgreSQL server.

```python
settings = self.get_settings()
print(f"Client encoding: {settings.client_encoding}")
```

--------------------------------

### Transaction Start Method

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

Handles the initiation of a database transaction or savepoint. It checks the current transaction state, determines whether to issue a BEGIN statement or a SAVEPOINT command, and applies specified isolation levels, read-only, and deferrable options. It also manages nested transaction logic.

```python
    @connresource.guarded
    async def start(self):
        """Enter the transaction or savepoint block."""
        self.__check_state_base('start')
        if self._state is TransactionState.STARTED:
            raise apg_errors.InterfaceError(
                'cannot start; the transaction is already started')

        con = self._connection

        if con._top_xact is None:
            if con._protocol.is_in_transaction():
                raise apg_errors.InterfaceError(
                    'cannot use Connection.transaction() in '
                    'a manually started transaction')
            con._top_xact = self
        else:
            if self._isolation:
                top_xact_isolation = con._top_xact._isolation
                if top_xact_isolation is None:
                    top_xact_isolation = ISOLATION_LEVELS_BY_VALUE[
                        await self._connection.fetchval(
                            'SHOW transaction_isolation;')]
                if self._isolation != top_xact_isolation:
                    raise apg_errors.InterfaceError(
                        'nested transaction has a different isolation level: '
                        'current {!r} != outer {!r}'.format(
                            self._isolation, top_xact_isolation))
            self._nested = True

        if self._nested:
            self._id = con._get_unique_id('savepoint')
            query = 'SAVEPOINT {};'.format(self._id)
        else:
            query = 'BEGIN'
            if self._isolation == 'read_committed':
                query += ' ISOLATION LEVEL READ COMMITTED'
            elif self._isolation == 'read_uncommitted':
                query += ' ISOLATION LEVEL READ UNCOMMITTED'
            elif self._isolation == 'repeatable_read':
                query += ' ISOLATION LEVEL REPEATABLE READ'
            elif self._isolation == 'serializable':
                query += ' ISOLATION LEVEL SERIALIZABLE'
            if self._readonly:
                query += ' READ ONLY'
            if self._deferrable:
                query += ' DEFERRABLE'
            query += ';'

        try:
            await self._connection.execute(query)
        except BaseException:
```

--------------------------------

### Prepare SQL Statement and Get Attribute Descriptions (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Demonstrates retrieving descriptions of relation attributes (columns) for a prepared SQL statement. This is useful for understanding the structure of the result set.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        st = await conn.prepare('''
            SELECT typname, typnamespace FROM pg_type
        ''')
        print(st.get_attributes())
        # Expected output (example):
        #   (Attribute(
        #       name='typname',
        #       type=Type(oid=19, name='name', kind='scalar',
        #                 schema='pg_catalog')),
        #    Attribute(
        #       name='typnamespace',
        #       type=Type(oid=26, name='oid', kind='scalar',
        #                 schema='pg_catalog')))
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Initialize asyncpg Pool with Parameters

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Initializes an asyncpg Pool instance using provided connection details, size limits, and optional connection lifecycle management callbacks. This method accepts a Data Source Name (DSN), connection class, record class, pool size constraints, query limits, and event loop. It also supports custom connect, setup, init, and reset functions, along with maximum inactive connection lifetime and additional connection keyword arguments.

```python
return Pool(
        dsn,
        connection_class=connection_class,
        record_class=record_class,
        min_size=min_size,
        max_size=max_size,
        max_queries=max_queries,
        loop=loop,
        connect=connect,
        setup=setup,
        init=init,
        reset=reset,
        max_inactive_connection_lifetime=max_inactive_connection_lifetime,
        **connect_kwargs,
    )
```

--------------------------------

### Get Attributes of a Prepared Statement in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Shows how to retrieve the attributes (columns) of a prepared statement in asyncpg. This is useful for understanding the structure of the data returned by a query. The example fetches type names and namespaces from the pg_type system catalog.

```python
st = await self.con.prepare('''
    SELECT typname, typnamespace FROM pg_type
''')
print(st.get_attributes())
```

--------------------------------

### EXECUTE SQL Commands

Source: https://magicstack.github.io/asyncpg/current/api/index

Execute SQL commands and get the status of the last command. Supports parameterized queries.

```APIDOC
## async.execute

### Description
Execute an SQL command. This method can be used for any SQL command, including DDL statements like CREATE TABLE and DML statements like INSERT, UPDATE, DELETE.

### Method
`async def execute(command: str, *args, timeout: float = None) -> str`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **command** (str) - The SQL command to execute.
- **args** - Query arguments (positional arguments for placeholders like $1, $2).
- **timeout** (float) - Optional timeout value in seconds.

### Request Example
```python
# Example 1: Simple INSERT
await con.execute('''
    INSERT INTO mytab (a) VALUES (100), (200), (300);
''')
# Returns: INSERT 0 3

# Example 2: Parameterized INSERT
await con.execute('''
    INSERT INTO mytab (a) VALUES ($1), ($2)
''', 10, 20)
# Returns: INSERT 0 2
```

### Response
#### Success Response (str)
- Status of the last SQL command (e.g., 'INSERT 0 3').

### Changes
- Changed in version 0.5.4: Made it possible to pass query arguments.
```

--------------------------------

### Get Parameters of a Prepared Statement in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Illustrates how to get the parameter types of a prepared statement using asyncpg. This method returns a tuple describing the OIDs and names of the parameters expected by the statement, which is helpful for validation and understanding query input requirements.

```python
stmt = await connection.prepare('SELECT ($1::int, $2::text)')
print(stmt.get_parameters())
```

--------------------------------

### Transaction Class Initialization and Context Management

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

Initializes a Transaction object, validating isolation levels and setting initial state. Implements __aenter__ and __aexit__ for asynchronous context management, ensuring transactions are properly started and either committed or rolled back upon exiting the context.

```python
class Transaction(connresource.ConnectionResource):
    """Represents a transaction or savepoint block.

    Transactions are created by calling the
    :meth:`Connection.transaction() <connection.Connection.transaction>`
    function.
    """

    __slots__ = ('_connection', '_isolation', '_readonly', '_deferrable',
                 '_state', '_nested', '_id', '_managed')

    def __init__(self, connection, isolation, readonly, deferrable):
        super().__init__(connection)

        if isolation and isolation not in ISOLATION_LEVELS:
            raise ValueError(
                'isolation is expected to be either of {}, '
                'got {!r}'.format(ISOLATION_LEVELS, isolation))

        self._isolation = isolation
        self._readonly = readonly
        self._deferrable = deferrable
        self._state = TransactionState.NEW
        self._nested = False
        self._id = None
        self._managed = False

    async def __aenter__(self):
        if self._managed:
            raise apg_errors.InterfaceError(
                'cannot enter context: already in an `async with` block')
        self._managed = True
        await self.start()

    async def __aexit__(self, extype, ex, tb):
        try:
            self._check_conn_validity('__aexit__')
        except apg_errors.InterfaceError:
            if extype is GeneratorExit:
                return
            else:
                raise

        try:
            if extype is not None:
                await self.__rollback()
            else:
                await self.__commit()
        finally:
            self._managed = False
```

--------------------------------

### Setup Asyncpg Connection Inactivity Timer

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Configures a timer to monitor connection inactivity. If a connection remains idle for longer than the `_max_inactive_time`, a callback (`_deactivate_inactive_connection`) is triggered to clean it up.

```python
    def _setup_inactive_callback(self):
        if self._inactive_callback is not None:
            raise exceptions.InternalClientError(
                'pool connection inactivity timer already exists')

        if self._max_inactive_time:
            self._inactive_callback = self._pool._loop.call_later(
                self._max_inactive_time, self._deactivate_inactive_connection)
```

--------------------------------

### Get Server Version - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Fetches and returns the version of the connected PostgreSQL server. The result is a named tuple containing major, minor, micro versions, release level, and serial number.

```python
version = self.get_server_version()
print(f"PostgreSQL version: {version.major}.{version.minor}.{version.micro}")
```

--------------------------------

### Get a New Connection from Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This asynchronous Python method handles the creation and initialization of a new database connection for the asyncpg pool. It validates the connection class, applies an optional initialization function (`_init`), and raises exceptions for connection or initialization errors.

```python
    async def _get_new_connection(self):
        con = await self._connect(
            *self._connect_args,
            loop=self._loop,
            connection_class=self._connection_class,
            record_class=self._record_class,
            **self._connect_kwargs,
        )
        if not isinstance(con, self._connection_class):
            good = self._connection_class
            good_n = f'{good.__module__}.{good.__name__}'
            bad = type(con)
            if bad.__module__ == "builtins":
                bad_n = bad.__name__
            else:
                bad_n = f'{bad.__module__}.{bad.__name__}'
            raise exceptions.InterfaceError(
                "expected pool connect callback to return an instance of "
                f"'{good_n}', got " f"'{bad_n}'"
            )

        if self._init is not None:
            try:
                await self._init(con)
            except (Exception, asyncio.CancelledError) as ex:
                # If a user-defined `init` function fails, we don't
                # know if the connection is safe for re-use, hence
                # we close it.  A new connection will be created
                # when `acquire` is called again.
                try:
                    # Use `close()` to close the connection gracefully.
                    # An exception in `init` isn't necessarily caused
                    # by an IO or a protocol error.  close() will
                    # do the necessary cleanup via _release_on_close().
                    await con.close()
                finally:
                    raise ex

        return con
```

--------------------------------

### _StatementCache Get and Has Methods (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Retrieves a statement from the cache if it exists and optionally promotes it to the most recently used position. The `has` method checks for existence without promoting the entry.

```python
    def get(self, query, *, promote=True):
        if not self._max_size:
            # The cache is disabled.
            return

        entry = self._entries.get(query)  # type: _StatementCacheEntry
        if entry is None:
            return

        if entry._statement.closed:
            # Happens in unittests when we call `stmt._state.mark_closed()`
            # manually or when a prepared statement closes itself on type
            # cache error.
            self._entries.pop(query)
            self._clear_entry_callback(entry)
            return

        if promote:
            # `promote` is `False` when `get()` is called by `has()`.
            self._entries.move_to_end(query, last=True)

        return entry._statement

    def has(self, query):
        return self.get(query, promote=False) is not None
```

--------------------------------

### Get Idle Connection Size of asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Returns the current number of idle connections available in the asyncpg pool.

```python
pool.get_idle_size()
```

--------------------------------

### Get Minimum Connections in Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method returns the configured minimum number of connections that the asyncpg pool aims to maintain. It accesses the `_minsize` attribute.

```python
    def get_min_size(self):
        """Return the minimum number of connections in this pool.

        .. versionadded:: 0.25.0
        """
        return self._minsize
```

--------------------------------

### Get Prepared Statement Query Text (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieves the SQL query string associated with a prepared statement. This is useful for debugging or logging. It requires an active connection and a prepared statement object.

```python
stmt = await connection.prepare('SELECT $1::int')
assert stmt.get_query() == "SELECT $1::int"
```

--------------------------------

### Get Server Process ID - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Retrieves the Process ID (PID) of the PostgreSQL server process that the current connection is utilizing.

```python
pid = self.get_server_pid()
```

--------------------------------

### Configure asyncpg for Hstore Type Decoding

Source: https://magicstack.github.io/asyncpg/current/usage

This example demonstrates how to register a codec for the hstore extension type, allowing asyncpg to decode hstore values directly into Python dictionaries. It uses Connection.set_builtin_type_codec() to register the 'pg_contrib.hstore' codec.

```python
import asyncpg
import asyncio

async def run():
    conn = await asyncpg.connect()
    # Assuming the hstore extension exists in the public schema.
    await conn.set_builtin_type_codec(
        'hstore', codec_name='pg_contrib.hstore')
    result = await conn.fetchval("SELECT 'a=>1,b=>2,c=>NULL'::hstore")
    assert result == {'a': '1', 'b': '2', 'c': None}

asyncio.run(run())
```

--------------------------------

### Manual Transaction Management (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Manages a database transaction manually by starting, committing, or rolling back. This provides explicit control over transaction boundaries and error handling. Requires an active connection and transaction object.

```python
tr = connection.transaction()
await tr.start()
try:
    ...
except:
    await tr.rollback()
    raise
else:
    await tr.commit()
```

--------------------------------

### Get Maximum Connections Allowed in Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method returns the maximum number of connections that the asyncpg pool is configured to allow. It accesses the `_maxsize` attribute.

```python
    def get_max_size(self):
        """Return the maximum allowed number of connections in this pool.

        .. versionadded:: 0.25.0
        """
        return self._maxsize
```

--------------------------------

### Create and Use Asyncpg Connection Pool in Python Web Service

Source: https://magicstack.github.io/asyncpg/current/usage

This Python code demonstrates creating a connection pool with asyncpg and integrating it into an aiohttp web application. It handles incoming requests, acquires a connection, starts a transaction, executes a query, and returns the result. Dependencies include asyncio, asyncpg, and aiohttp. The input is a request with an optional 'power' parameter, and the output is a web response containing the computed power of two.

```python
import asyncio
import asyncpg
from aiohttp import web


async def handle(request):
    """Handle incoming requests."""
    pool = request.app['pool']
    power = int(request.match_info.get('power', 10))

    # Take a connection from the pool.
    async with pool.acquire() as connection:
        # Open a transaction.
        async with connection.transaction():
            # Run the query passing the request argument.
            result = await connection.fetchval('select 2 ^ $1', power)
            return web.Response(
                text="2 ^ {} is {}".format(power, result))


async def init_db(app):
    """Initialize a connection pool."""
     app['pool'] = await asyncpg.create_pool(database='postgres',
                                             user='postgres')
     yield
     await app['pool'].close()


def init_app():
    """Initialize the application server."""
    app = web.Application()
    # Create a database context
    app.cleanup_ctx.append(init_db)
    # Configure service routes
    app.router.add_route('GET', '/{power:\d+}', handle)
    app.router.add_route('GET', '/', handle)
    return app


app = init_app()
web.run_app(app)

```

--------------------------------

### Handle Query Results as Records (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to interact with `Record` objects returned by asyncpg's `fetch*` methods. `Record` objects allow accessing row data by numeric index or field name, similar to tuples and dictionaries. This example shows fetching role information from `pg_roles`.

```python
import asyncpg
import asyncio

loop = asyncio.get_event_loop()
conn = loop.run_until_complete(asyncpg.connect())
r = loop.run_until_complete(conn.fetchrow('''
    SELECT oid, rolname, rolsuper FROM pg_roles WHERE rolname = user
'''))

print(r)
print(r['oid'])
print(r[0])
print(dict(r))
print(tuple(r))
```

--------------------------------

### Get Executed Command Status Message (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieves the status message of the last executed command by a prepared statement. Useful for confirming command success, like CREATE TABLE or INSERT. Requires an executed statement.

```python
stmt = await connection.prepare('CREATE TABLE mytab (a int)')
await stmt.fetch()
assert stmt.get_statusmsg() == "CREATE TABLE"
```

--------------------------------

### Connection Methods

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This section details methods related to connection and query execution, including creating cursors, preparing statements, fetching data, and managing transactions.

```APIDOC
## POST /connection/cursor

### Description
Creates a cursor factory for executing queries.

### Method
POST

### Endpoint
/connection/cursor

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments for the query.
- **prefetch** (int) - Optional - Number of rows to prefetch.
- **timeout** (float) - Optional - Timeout in seconds.
- **record_class** (type) - Optional - Class to use for returned records.

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **cursor_factory** (:class:`~cursor.CursorFactory`) - A CursorFactory object.

#### Response Example
```json
{
  "cursor_factory": "<cursor.CursorFactory object>"
}
```

## POST /connection/prepare

### Description
Creates a prepared statement for a given SQL query.

### Method
POST

### Endpoint
/connection/prepare

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to prepare.
- **name** (str) - Optional - Name for the prepared statement.
- **timeout** (float) - Optional - Timeout in seconds.
- **record_class** (type) - Optional - Class to use for records returned by the prepared statement.

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **prepared_statement** (:class:`~prepared_stmt.PreparedStatement`) - A PreparedStatement instance.

#### Response Example
```json
{
  "prepared_statement": "<prepared_stmt.PreparedStatement object>"
}
```

## POST /connection/fetch

### Description
Executes a query and returns the results as a list of records.

### Method
POST

### Endpoint
/connection/fetch

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments for the query.
- **timeout** (float) - Optional - Timeout in seconds.
- **record_class** (type) - Optional - Class to use for returned records.

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **records** (list) - A list of :class:`~asyncpg.Record` instances.

#### Response Example
```json
[
  { "column1": "value1", "column2": "value2" },
  { "column1": "value3", "column2": "value4" }
]
```

## POST /connection/fetchval

### Description
Executes a query and returns a single value from the first row.

### Method
POST

### Endpoint
/connection/fetchval

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments for the query.
- **column** (int) - Optional - The index of the column to return (defaults to 0).
- **timeout** (float) - Optional - Timeout in seconds.

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **value** - The value from the specified column of the first record, or None if no records were returned.

#### Response Example
```json
"example_value"
```

## POST /connection/fetchrow

### Description
Executes a query and returns the first row.

### Method
POST

### Endpoint
/connection/fetchrow

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments for the query.
- **timeout** (float) - Optional - Timeout in seconds.
- **record_class** (type) - Optional - Class to use for the returned record.

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **record** (:class:`~asyncpg.Record`) - The first record returned by the query, or None if no records were returned.

#### Response Example
```json
{
  "column1": "value1",
  "column2": "value2"
}
```
```

--------------------------------

### Get Current Number of Connections in Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method calculates and returns the total number of currently connected connections in the asyncpg pool. It iterates through connection holders and checks if each is connected.

```python
    def get_size(self):
        """Return the current number of connections in this pool.

        .. versionadded:: 0.25.0
        """
        return sum(h.is_connected() for h in self._holders)
```

--------------------------------

### Get Number of Idle Connections in Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method calculates and returns the number of currently idle connections within the asyncpg pool. It sums up connection holders that are both connected and idle.

```python
    def get_idle_size(self):
        """Return the current number of idle connections in this pool.

        .. versionadded:: 0.25.0
        """
        return sum(h.is_connected() and h.is_idle() for h in self._holders)
```

--------------------------------

### asyncpg.connect Parameters

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This section details the various parameters available when establishing a connection using asyncpg.connect. It covers connection attributes, authentication methods, and advanced configuration options.

```APIDOC
## asyncpg.connect Parameters

### Description
This endpoint outlines the parameters for establishing a connection with asyncpg. It covers connection string components, authentication credentials, SSL configuration, and session attribute targeting.

### Method
`asyncpg.connect()`

### Endpoint
N/A (Function call)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

- **dsn** (str): The connection string URI. Supports multiple hosts and SSL options like ``sslcert``, ``sslkey``, ``sslrootcert``, ``sslcrl``, ``sslpassword``, ``ssl_min_protocol_version``, and ``ssl_max_protocol_version``. Defaults are consistent with libpq for certificate and key files under ``~/.postgresql/``.
- **host** (str or list[str]): Hostname or list of hostnames for the PostgreSQL server. Support for multiple hosts was added in v0.18.0.
- **port** (int or list[int]): Port number or list of port numbers for the PostgreSQL server.
- **user** (str): Username for authentication.
- **password** (str or callable or async function): Password for authentication. Accepts callable or async function since v0.21.0.
- **database** (str): The name of the database to connect to.
- **server_settings** (dict): A dictionary for setting server configuration parameters. Introduced in v0.11.0 to replace arbitrary keyword arguments.
- **connection_class** (class): A custom connection class, must be a subclass of `asyncpg.Connection`. Added in v0.11.0.
- **record_class** (class): A custom record class, defaults to `asyncpg.Record`. Validated using `_check_record_class`.
- **loop** (asyncio.AbstractEventLoop): The event loop to use. Defaults to the current event loop.
- **timeout** (float): Connection timeout in seconds.
- **command_timeout** (float): Timeout for commands in seconds.
- **statement_cache_size** (int): Maximum number of statements to cache.
- **max_cached_statement_lifetime** (float): Maximum lifetime of cached statements in seconds.
- **max_cacheable_statement_size** (int): Maximum size of statements to cache.
- **ssl** (str or SSLContext or bool): SSL mode. Defaults to `'prefer'` since v0.22.0. Supported modes include:
    - ``"true"`` / ``"1"``: Enable SSL
    - ``"false"`` / ``"0"``: Disable SSL
    - ``"allow"``: Allow SSL, but don't require it
    - ``"prefer"``: Prefer SSL, but allow non-SSL connections
    - ``"require"``: Require SSL
    - ``"verify-ca"``: Require SSL and verify that the server certificate is signed by a trusted Certificate Authority
    - ``"verify-full"``: Require SSL, verify CA, and verify that the server hostname matches the certificate
- **direct_tls** (bool): Enable direct TLS connection. Added in v0.26.0.
- **target_session_attrs** (str): Target session attributes. Options include:
    - ``"read-write"``: Host must allow writes.
    - ``"read-only"``: Host must NOT allow writes.
    - ``"prefer-standby"``: Try to find a standby host first, otherwise return any.
    If not specified, defaults to the value from *dsn*, ``PGTARGETSESSIONATTRS`` environment variable, or ``"any"``.
- **krbsrvname** (str): Kerberos service name for GSSAPI authentication. Defaults to 'postgres'. Added in v0.30.0.
- **gsslib** (str): GSS library for GSSAPI/SSPI authentication. Can be 'gssapi' or 'sspi'. Defaults to 'sspi' on Windows and 'gssapi' otherwise. Added in v0.30.0.
- **passfile** (str): Path to the password file. Added in v0.16.0.

### Request Example
```python
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(
        user='postgres',
        password='password',
        database='database',
        host='localhost',
        port=5432,
        server_settings={'search_path': 'myschema'},
        ssl='prefer',
        target_session_attrs='read-write'
    )
    print(con)

asyncio.run(run())
```

### Response
#### Success Response (200)
- **Connection** (asyncpg.connection.Connection): An instance of the connection object.

#### Response Example
```
<Connection client_encoding='UTF8' status='READY'>
```
```

--------------------------------

### Close Asyncpg Connection Gracefully

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Demonstrates the graceful closing of an asyncpg connection using the `close()` method. This method ensures proper cleanup, even if exceptions occur during setup. It's crucial for releasing resources and maintaining pool integrity.

```python
                try:
                    # Use `close()` to close the connection gracefully.
                    # An exception in `setup` isn't necessarily caused
                    # by an IO or a protocol error.  close() will
                    # do the necessary cleanup via _release_on_close().
                    await self._con.close()
                finally:
                    raise ex
```

--------------------------------

### Configure asyncpg to Decode Numeric Columns as Floats

Source: https://magicstack.github.io/asyncpg/current/usage

This example shows how to instruct asyncpg to decode numeric database columns as Python floats instead of the default Decimal instances. This is achieved by setting a type codec for the 'numeric' type.

```python
import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect()

    try:
        await conn.set_type_codec(
            'numeric', encoder=str, decoder=float,
            schema='pg_catalog', format='text'
        )

        res = await conn.fetchval("SELECT $1::numeric", 11.123)
        print(res, type(res))

    finally:
        await conn.close()

asyncio.run(main())
```

--------------------------------

### Use asyncpg Connection for Database Transactions

Source: https://magicstack.github.io/asyncpg/current/usage

This example illustrates how to manage database transactions in asyncpg using the `Connection.transaction()` method within an `async with` statement. Changes within the block are committed upon successful exit, otherwise rolled back.

```python
async with connection.transaction():
    await connection.execute("INSERT INTO mytable VALUES(1, 2, 3)")
```

--------------------------------

### Execute Query with Options (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a single query with support for arguments, timeouts, and custom return types. It handles query logging and integrates with statement caching for performance.

```python
async def _execute(
        self,
        query,
        args,
        timeout,
        *, # Use named arguments
        limit=None,
        return_status=False,
        ignore_custom_codec=False,
        record_class=None
    ):
        executor = lambda stmt, timeout: self._protocol.bind_execute(
            state=stmt,
            args=args,
            portal_name='',
            limit=limit,
            return_extra=return_status,
            timeout=timeout,
        )
        timeout = self._protocol._get_timeout(timeout)
        if self._query_loggers:
            with self._time_and_log(query, args, timeout):
                result, stmt = await self._do_execute(
                    query,
                    executor,
                    timeout,
                    record_class=record_class,
                    ignore_custom_codec=ignore_custom_codec,
                )
        else:
            result, stmt = await self._do_execute(
                query,
                executor,
                timeout,
                record_class=record_class,
                ignore_custom_codec=ignore_custom_codec,
            )
        return result, stmt
```

--------------------------------

### Execute SQL Commands with asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates executing SQL commands, including multi-statement commands and parameterized inserts, using the `execute` method in asyncpg. It shows how to create tables, insert data, and use placeholders for dynamic values.

```python
await con.execute('''
    CREATE TABLE mytab (a int);
    INSERT INTO mytab (a) VALUES (100), (200), (300);
''')
INSERT 0 3

await con.execute('''
    INSERT INTO mytab (a) VALUES ($1), ($2)
''', 10, 20)
INSERT 0 2
```

--------------------------------

### Configure asyncpg for PostGIS Geometry Type

Source: https://magicstack.github.io/asyncpg/current/usage

This example demonstrates how to configure asyncpg to automatically encode and decode the PostGIS 'geometry' type. It relies on the geo interface specification and Shapely for WKB format handling, enabling seamless conversion between Python objects and database geometries.

```python
import asyncio
import asyncpg

import shapely.geometry
import shapely.wkb
from shapely.geometry.base import BaseGeometry


async def main():
    conn = await asyncpg.connect()

    try:
        def encode_geometry(geometry):
            if not hasattr(geometry, '__geo_interface__'):
                raise TypeError('{g} does not conform to ' 
                                'the geo interface'.format(g=geometry))
            shape = shapely.geometry.shape(geometry)
            return shapely.wkb.dumps(shape)

        def decode_geometry(wkb):
            return shapely.wkb.loads(wkb)

        await conn.set_type_codec(
            'geometry',  # also works for 'geography'
            encoder=encode_geometry,
            decoder=decode_geometry,
            format='binary',
        )

        data = shapely.geometry.Point(-73.985661, 40.748447)
        res = await conn.fetchrow(
            '''SELECT 'Empire State Building' AS name,
                      $1::geometry            AS coordinates
            ''',
            data)

        print(res)

    finally:
        await conn.close()

asyncio.run(main())
```

--------------------------------

### Transaction State Enum Definition

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

Defines the possible states for a database transaction, including NEW, STARTED, COMMITTED, ROLLEDBACK, and FAILED. This enum helps in managing and tracking the lifecycle of a transaction within the asyncpg library.

```python
import enum

from . import connresource
from . import exceptions as apg_errors


class TransactionState(enum.Enum):
    NEW = 0
    STARTED = 1
    COMMITTED = 2
    ROLLEDBACK = 3
    FAILED = 4
```

--------------------------------

### PreparedStatement Methods

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Provides details on various methods available for a prepared statement object in asyncpg.

```APIDOC
## PreparedStatement Class

A representation of a prepared statement.

### Methods

*   **`get_name()`**
    *   **Description**: Returns the name of this prepared statement.
    *   **Version Added**: 0.25.0

*   **`get_query()`**
    *   **Description**: Returns the text of the query for this prepared statement.
    *   **Example**:
        ```python
        stmt = await connection.prepare('SELECT $1::int')
        assert stmt.get_query() == "SELECT $1::int"
        ```

*   **`get_statusmsg()`**
    *   **Description**: Returns the status of the executed command.
    *   **Example**:
        ```python
        stmt = await connection.prepare('CREATE TABLE mytab (a int)')
        await stmt.fetch()
        assert stmt.get_statusmsg() == "CREATE TABLE"
        ```

*   **`get_parameters()`**
    *   **Description**: Returns a description of statement parameters types.
    *   **Returns**: A tuple of :class:`asyncpg.types.Type`.
    *   **Example**:
        ```python
        stmt = await connection.prepare('SELECT ($1::int, $2::text)')
        print(stmt.get_parameters())
        # Will print:
        #   (Type(oid=23, name='int4', kind='scalar', schema='pg_catalog'),
        #    Type(oid=25, name='text', kind='scalar', schema='pg_catalog'))
        ```

*   **`get_attributes()`**
    *   **Description**: Returns a description of relation attributes (columns).
    *   **Returns**: A tuple of :class:`asyncpg.types.Attribute`.
    *   **Example**:
        ```python
        st = await self.con.prepare('''
            SELECT typname, typnamespace FROM pg_type
        ''')
        print(st.get_attributes())
        # Will print:
        #   (Attribute(
        #       name='typname',
        #       type=Type(oid=19, name='name', kind='scalar',
        #                 schema='pg_catalog')),
        #    Attribute(
        #       name='typnamespace',
        #       type=Type(oid=26, name='oid', kind='scalar',
        #                 schema='pg_catalog')))
        ```

*   **`cursor(*args, prefetch=None, timeout=None)`**
    *   **Description**: Returns a *cursor factory* for the prepared statement.
    *   **Parameters**:
        *   `*args`: Query arguments.
        *   `prefetch` (int, optional): The number of rows the *cursor iterator* will prefetch (defaults to ``50``).
        *   `timeout` (float, optional): Optional timeout in seconds.
    *   **Returns**: A :class:`~cursor.CursorFactory` object.

*   **`explain(*args, analyze=False)`**
    *   **Description**: Returns the execution plan of the statement.
    *   **Parameters**:
        *   `*args`: Query arguments.
        *   `analyze` (bool, optional): If ``True``, the statement will be executed and the run time statitics added to the return value.
    *   **Returns**: An object representing the execution plan. This value is actually a deserialized JSON output of the SQL ``EXPLAIN`` command.
    *   **Note**: When `analyze=True`, the statement is actually executed. Side effects will occur. Use within a `BEGIN`/`ROLLBACK` block if side effects are not desired.
```

--------------------------------

### POST /connect

Source: https://magicstack.github.io/asyncpg/current/api/index

Establishes an asynchronous connection to a PostgreSQL database. This endpoint details the various parameters available for configuring the connection, including authentication, SSL, server settings, and session attributes.

```APIDOC
## POST /connect

### Description
Establishes an asynchronous connection to a PostgreSQL database. This endpoint details the various parameters available for configuring the connection, including authentication, SSL, server settings, and session attributes.

### Method
POST

### Endpoint
/connect

### Parameters
#### Query Parameters
- **user** (str) - Optional - The username for connecting to the database.
- **password** (str | callable | async function) - Optional - The password for connecting to the database. Can be a callable or an async function.
- **database** (str) - Optional - The name of the database to connect to.
- **host** (str | list[str]) - Optional - The hostname or a list of hostnames for the database server.
- **port** (int | list[int]) - Optional - The port number or a list of port numbers for the database server.
- **ssl** (bool | ssl.SSLContext | str) - Optional - Controls SSL connection behavior. Can be `True` (default context), an `ssl.SSLContext` instance, or one of the following strings: `'disable'`, `'prefer'`, `'allow'`, `'require'`, `'verify-ca'`, `'verify-full'`. Defaults to `'prefer'`. Ignored for Unix domain sockets.
- **direct_tls** (bool) - Optional - If `True`, performs a direct SSL connection, skipping PostgreSQL STARTTLS mode. Must be used with the `ssl` parameter.
- **server_settings** (dict) - Optional - A dictionary of server runtime parameters.
- **connection_class** (type) - Optional - The class for the returned connection object. Must be a subclass of `asyncpg.Connection`.
- **record_class** (type) - Optional - The class to use for records returned by queries. Must be a subclass of `asyncpg.Record`.
- **target_session_attrs** (str) - Optional - Checks that the host has the correct attribute. Can be: `'any'`, `'primary'`, `'standby'`, `'read-write'`, `'read-only'`, `'prefer-standby'`.
- **krbsrvname** (str) - Optional - Kerberos service name for GSSAPI authentication. Defaults to 'postgres'.
- **gsslib** (str) - Optional - GSS library for GSSAPI/SSPI authentication. Can be 'gssapi' or 'sspi'. Defaults to 'sspi' on Windows and 'gssapi' otherwise.
- **passfile** (str) - Optional - Path to the password file.

### Request Example
```json
{
  "user": "postgres",
  "password": "secretpassword",
  "database": "mydatabase",
  "host": "localhost",
  "port": 5432,
  "ssl": "verify-full"
}
```

### Response
#### Success Response (200)
- **connection** (object) - An instance of `asyncpg.Connection`.

#### Response Example
```json
{
  "connection": "<asyncpg.Connection object at 0x...>"
}
```
```

--------------------------------

### Query Execution API

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for executing raw SQL queries and commands against the database.

```APIDOC
## Query Execution Methods

### Description
These methods allow for the execution of SQL queries and commands, with support for passing arguments and handling timeouts.

### Methods

#### `execute(query: str, *args, timeout: float=None)`

##### Description
Executes an SQL command or multiple commands. Can accept positional arguments for prepared statements.

##### Parameters
- **query** (str) - The SQL query or command string to execute.
- **args** - Positional arguments for the query. Can be empty for non-parameterized queries.
- **timeout** (float) - Optional - Timeout value in seconds for the query execution.

##### Returns
- `str` - The status message of the last executed SQL command.

##### Request Example (Parameterized Query)
```py
await con.execute('INSERT INTO mytab (a) VALUES ($1), ($2)', 10, 20)
```

##### Response Example (Success)
```
INSERT 0 2
```

#### `executemany(command: str, args, *, timeout: float=None)`

##### Description
Executes a given SQL command for each sequence of arguments provided in `args`. This operation is atomic.

##### Parameters
- **command** (str) - The SQL command to execute repeatedly.
- **args** - An iterable where each element is a sequence of arguments for the `command`.
- **timeout** (float) - Optional - Timeout value in seconds for the entire operation.

##### Returns
- `None`

##### Example
```py
await con.executemany('INSERT INTO mytab (a) VALUES ($1, $2, $3)', [(1, 2, 3), (4, 5, 6)])
```

### Version Changes
- `execute()`: Query arguments support added in v0.5.4.
- `executemany()`: Added in v0.7.0. Became keyword-only `timeout` in v0.11.0. Became atomic in v0.22.0.
```

--------------------------------

### Get Pool Size Information (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieve the current number of idle connections, the maximum allowed connections, the minimum required connections, and the total current connections within the asyncpg connection pool. These functions provide insights into the pool's utilization and capacity. Added in version 0.25.0.

```python
asyncpg.Pool.get_idle_size()
asyncpg.Pool.get_max_size()
asyncpg.Pool.get_min_size()
asyncpg.Pool.get_size()
```

--------------------------------

### Transaction State Checking in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

These methods check the current state of a transaction before allowing operations like commit or rollback. They prevent operations on transactions that are already committed, rolled back, failed, or not yet started, raising InterfaceError for invalid states.

```python
def __check_state_base(self, opname):
    if self._state is TransactionState.COMMITTED:
        raise apg_errors.InterfaceError(
            'cannot {}; the transaction is already committed'.format(
                opname))
    if self._state is TransactionState.ROLLEDBACK:
        raise apg_errors.InterfaceError(
            'cannot {}; the transaction is already rolled back'.format(
                opname))
    if self._state is TransactionState.FAILED:
        raise apg_errors.InterfaceError(
            'cannot {}; the transaction is in error state'.format(
                opname))

def __check_state(self, opname):
    if self._state is not TransactionState.STARTED:
        if self._state is TransactionState.NEW:
            raise apg_errors.InterfaceError(
                'cannot {}; the transaction is not yet started'.format(
                    opname))
        self.__check_state_base(opname)
```

--------------------------------

### Get Reset Query for Connection Release in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Retrieves the SQL query used to reset a connection's state before it's released back to the pool. This query may include commands like releasing advisory locks, closing cursors, unlistening from channels, and resetting all SQL parameters, depending on server capabilities. The query is cached after the first call.

```python
    def get_reset_query(self):
        """Return the query sent to server on connection release.

        The query returned by this method is used by :meth:`Connection.reset`,
        which is, in turn, used by :class:`~asyncpg.pool.Pool` before making
        the connection available to another acquirer.

        .. versionadded:: 0.30.0
        """
        if self._reset_query is not None:
            return self._reset_query

        caps = self._server_caps

        _reset_query = []
        if caps.advisory_locks:
            _reset_query.append('SELECT pg_advisory_unlock_all();')
        if caps.sql_close_all:
            _reset_query.append('CLOSE ALL;')
        if caps.notifications and caps.plpgsql:
            _reset_query.append('UNLISTEN *;')
        if caps.sql_reset:
            _reset_query.append('RESET ALL;')

        _reset_query = '\n'.join(_reset_query)
        self._reset_query = _reset_query

        return _reset_query
```

--------------------------------

### Connection Parameters

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This section details the various parameters available when establishing a connection using asyncpg, influencing aspects like statement caching, timeouts, SSL, and server configuration.

```APIDOC
## Connection Parameters

This endpoint documentation outlines the parameters for establishing a connection in asyncpg.

### Method
N/A (Configuration parameters for `asyncpg.connect`)

### Parameters

#### Connection Parameters

- **statement_cache_size** (int) - Optional - The size of the prepared statement LRU cache. Pass `0` to disable the cache.
- **max_cached_statement_lifetime** (int) - Optional - The maximum time in seconds a prepared statement will stay in the cache. Pass `0` to allow statements to be cached indefinitely.
- **max_cacheable_statement_size** (int) - Optional - The maximum size of a statement that can be cached (15KiB by default). Pass `0` to allow all statements to be cached regardless of their size.
- **command_timeout** (float) - Optional - The default timeout for operations on this connection (the default is `None`: no timeout).
- **ssl** (bool or ssl.SSLContext or str) - Optional - Configures SSL connections. Can be `True` (uses default context), an `ssl.SSLContext` instance, or one of the following strings: `'disable'`, `'prefer'`, `'allow'`, `'require'`, `'verify-ca'`, `'verify-full'`. Defaults to `'prefer'`.
- **direct_tls** (bool) - Optional - If `True`, skips STARTTLS and performs a direct SSL connection. Must be used with the `ssl` parameter.
- **server_settings** (dict) - Optional - A dictionary of server runtime parameters. Refer to PostgreSQL documentation for supported options.
- **connection_class** (type) - Optional - The class to use for the connection object. Must be a subclass of `asyncpg.connection.Connection`.
- **record_class** (type) - Optional - The class to use for records returned by queries. Must be a subclass of `asyncpg.Record`.
- **target_session_attrs** (SessionAttribute) - Optional - Checks that the host has the correct attribute. Can be: `"any"`, `"primary"`, `"standby"`.

### Request Example
```python
import asyncpg
import asyncio
import ssl

async def main():
    # Example with SSL verification
    sslctx = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile="path/to/ca_bundle.pem"
    )
    sslctx.check_hostname = True
    sslctx.load_cert_chain(
        "path/to/client.cert",
        keyfile="path/to/client.key"
    )
    
    con = await asyncpg.connect(
        user='postgres',
        password='password',
        database='database',
        host='localhost',
        port=5432,
        statement_cache_size=100,
        max_cached_statement_lifetime=300,
        max_cacheable_statement_size=0,
        command_timeout=10.0,
        ssl=sslctx,
        direct_tls=False,
        server_settings={"application_name": "my_app"},
        connection_class=asyncpg.connection.Connection,
        record_class=asyncpg.Record,
        target_session_attrs="primary"
    )
    # ... use connection ...
    await con.close()

asyncio.run(main())
```

### Response
N/A (This describes connection parameters, not a direct API response.)

#### Success Response (200)
N/A

#### Response Example
N/A
```

--------------------------------

### Custom Complex Type Conversion with asyncpg in Python

Source: https://magicstack.github.io/asyncpg/current/usage

Shows how to set up custom type conversion for Python's `complex` numbers to a custom PostgreSQL composite type named `mycomplex`. This example involves creating the composite type in the database and then defining encoders and decoders for it using `set_type_codec`. Dependencies include 'asyncpg' and 'asyncio'.

```python
import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect()

    try:
        await conn.execute(
            '\
            CREATE TYPE mycomplex AS (
                r float,
                i float
            );
            '
        )
        await conn.set_type_codec(
            'complex',
            encoder=lambda x: (x.real, x.imag),
            decoder=lambda t: complex(t[0], t[1]),
            format='tuple',
        )

        res = await conn.fetchval('SELECT $1::mycomplex', (1+2j))

    finally:
        await conn.close()

asyncio.run(main())

```

--------------------------------

### Prepared Statements

Source: https://magicstack.github.io/asyncpg/current/api/index

Create and manage prepared statements for efficient query execution.

```APIDOC
## POST /connection/prepare

### Description
Creates a prepared statement for a given SQL query. This allows for more efficient execution of repeated queries.

### Method
POST

### Endpoint
`/connection/prepare`

### Parameters
#### Query Parameters
- **query** (string) - Required - The SQL query string to prepare.
- **name** (string) - Optional - A name for the prepared statement. If not provided, a name is auto-generated.
- **timeout** (float) - Optional - Timeout value in seconds for preparing the statement.
- **record_class** (type) - Optional - The class to use for records returned by the prepared statement. Must be a subclass of `Record`.

### Request Example
```json
{
  "query": "SELECT * FROM users WHERE id = $1",
  "name": "get_user_by_id",
  "timeout": 5.0
}
```

### Response
#### Success Response (200)
- **PreparedStatement** (object) - An object representing the prepared statement.

#### Response Example
```json
{
  "name": "get_user_by_id",
  "query": "SELECT * FROM users WHERE id = $1"
}
```
```

--------------------------------

### Create and Use asyncpg Connection Pool (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates creating an asyncpg connection pool and using it with an 'async with' block to perform a simple fetch operation. This is a common and recommended way to manage connections.

```python
async with asyncpg.create_pool(user='postgres',
                               command_timeout=60) as pool:
    await pool.fetch('SELECT 1')
```

--------------------------------

### Pre-connecting Asyncpg Pool Connections

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python code demonstrates how to pre-connect a specified number of connections in an asyncpg pool. It prioritizes connecting the first holder and then connects additional holders up to the minimum size to ensure early visibility of connection issues and readiness.

```python
            # Connect the first connection holder in the queue so that
            # any connection issues are visible early.
            first_ch = self._holders[-1]  # type: PoolConnectionHolder
            await first_ch.connect()

            if self._minsize > 1:
                connect_tasks = []
                for i, ch in enumerate(reversed(self._holders[:-1])):
                    # `minsize - 1` because we already have first_ch
                    if i >= self._minsize - 1:
                        break
                    connect_tasks.append(ch.connect())

                await asyncio.gather(*connect_tasks)
```

--------------------------------

### Establish Asyncpg Connection with Parameters (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This Python code snippet illustrates the internal logic for establishing an asyncpg connection, including parameter validation and calling a utility function for the actual connection process. It handles connection class type checking, record class validation, and utilizes asyncio for asynchronous operations. Dependencies include 'asyncio', 'compat', and 'connect_utils'.

```python
if not issubclass(connection_class, Connection):
        raise exceptions.InterfaceError(
            'connection_class is expected to be a subclass of ' \
            'asyncpg.Connection, got {!r}'.format(connection_class))

    if record_class is not protocol.Record:
        _check_record_class(record_class)

    if loop is None:
        loop = asyncio.get_event_loop()

    async with compat.timeout(timeout):
        return await connect_utils._connect(
            loop=loop,
            connection_class=connection_class,
            record_class=record_class,
            dsn=dsn,
            host=host,
            port=port,
            user=user,
            password=password,
            passfile=passfile,
            ssl=ssl,
            direct_tls=direct_tls,
            database=database,
            server_settings=server_settings,
            command_timeout=command_timeout,
            statement_cache_size=statement_cache_size,
            max_cached_statement_lifetime=max_cached_statement_lifetime,
            max_cacheable_statement_size=max_cacheable_statement_size,
            target_session_attrs=target_session_attrs,
            krbsrvname=krbsrvname,
            gsslib=gsslib,
        )
```

--------------------------------

### Pool Initialization

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This section details the parameters available when initializing an asyncpg Pool object.

```APIDOC
## asyncpg.pool.Pool()

### Description
Initializes a new asyncpg Pool object.

### Method
CONSTRUCTOR

### Endpoint
N/A

### Parameters
#### Path Parameters
N/A

#### Query Parameters
N/A

#### Request Body
N/A

### Request Example
```python
# This is a constructor, not a request example
```

### Response
#### Success Response (200)
N/A

#### Response Example
```python
# This is a constructor, not a response example
```

### Parameters
- **dsn** (str) - Description of the database connection string.
- **connection_class** (type) - Optional. The connection class to use.
- **record_class** (type) - Optional. The record class to use. Added in 0.22.0.
- **min_size** (int) - Optional. The minimum number of connections in the pool.
- **max_size** (int) - Optional. The maximum number of connections in the pool.
- **max_queries** (int) - Optional. The maximum number of queries per connection.
- **loop** (asyncio.BaseEventLoop) - Optional. The asyncio event loop instance. If ``None``, the default event loop will be used.
- **connect** (callable) - Optional. A callable used to establish a new connection. Added in 0.30.0.
- **setup** (callable) - Optional. A callable to run after a connection is established.
- **init** (callable) - Optional. A callable to run when a connection is initialized.
- **reset** (callable) - Optional. A callable to run when a connection is reset. Added in 0.30.0.
- **max_inactive_connection_lifetime** (float) - Optional. The maximum lifetime of an inactive connection.
- ****connect_kwargs** (dict) - Additional keyword arguments for the connection.

### Version Changes
- **0.10.0**: An :exc:`~asyncpg.exceptions.InterfaceError` will be raised on any attempted operation on a released connection.
- **0.13.0**: An :exc:`~asyncpg.exceptions.InterfaceError` will be raised on any attempted operation on a prepared statement or a cursor created on a connection that has been released to the pool.
- **0.13.0**: An :exc:`~asyncpg.exceptions.InterfaceWarning` will be produced if there are any active listeners present on the connection at the moment of its release to the pool.
- **0.22.0**: Added the *record_class* parameter.
- **0.30.0**: Added the *connect* and *reset* parameters.
```

--------------------------------

### Connection API

Source: https://magicstack.github.io/asyncpg/current/api/index

Establishes a connection to a PostgreSQL server. Connection parameters can be provided via a DSN string, keyword arguments, or environment variables. The function returns a new Connection object.

```APIDOC
## asyncpg.connect()

### Description
A coroutine to establish a connection to a PostgreSQL server.
The connection parameters may be specified either as a connection URI in _dsn_, or as specific keyword arguments, or both. If both _dsn_ and keyword arguments are specified, the latter override the corresponding values parsed from the connection URI. The default values for the majority of arguments can be specified using environment variables.

Returns a new `Connection` object.

### Method
Asynchronous Function Call

### Endpoint
N/A (Function Call)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

*   **dsn** (str) - Connection arguments specified using as a single string in the libpq connection URI format: `postgres://user:password@host:port/database?option=value`.
*   **host** (str or list[str]) - Database host address or a sequence of addresses.
*   **port** (int or list[int]) - Port number to connect to at the server host.
*   **user** (str) - The name of the database role used for authentication.
*   **database** (str) - The name of the database to connect to.
*   **password** (str or callable) - Password to be used for authentication.
*   **passfile** (str) - The name of the file used to store passwords.
*   **loop** (asyncio.AbstractEventLoop) - An asyncio event loop instance.
*   **timeout** (float) - Connection timeout in seconds.
*   **statement_cache_size** (int) - The size of prepared statement LRU cache.
*   **max_cached_statement_lifetime** (int) - The maximum time in seconds a prepared statement will stay in the cache.
*   **max_cacheable_statement_size** (int) - The maximum size of a statement that can be cached.
*   **command_timeout** (float) - The default timeout for operations on this connection.
*   **ssl** - SSL connection options.
*   **direct_tls** (bool) - Whether to use direct TLS connection.
*   **connection_class** (type) - The class to use for creating a connection.
*   **record_class** (type) - The class to use for representing records.
*   **server_settings** (dict) - Dictionary of server settings to apply.
*   **target_session_attrs** (str) - Target session attributes for connection.
*   **krbsrvname** (str) - Kerberos service name.
*   **gsslib** (str) - GSSAPI library to use.

### Request Example
```python
import asyncpg

async def connect_to_db():
    conn = await asyncpg.connect(user='postgres', password='password', 
                                 database='database', host='127.0.0.1')
    # Use the connection...
    await conn.close()
```

### Response
#### Success Response (200)
An `asyncpg.connection.Connection` object representing the established connection.

#### Response Example
```python
<asyncpg.connection.Connection object at 0x...>
```
```

--------------------------------

### BaseCursor Initialization and State Management (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Initializes the BaseCursor with connection and query details, managing the state and arguments. It includes logic to attach the state upon initialization.

```Python
class BaseCursor(connresource.ConnectionResource):

    __slots__ = (
        '_state',
        '_args',
        '_portal_name',
        '_exhausted',
        '_query',
        '_record_class',
    )

    def __init__(self, connection, query, state, args, record_class):
        super().__init__(connection)
        self._args = args
        self._state = state
        if state is not None:
            state.attach()
        self._portal_name = None
        self._exhausted = False
        self._query = query
        self._record_class = record_class
```

--------------------------------

### PreparedStatement Class Methods

Source: https://magicstack.github.io/asyncpg/current/api/index

Details the methods available on the `PreparedStatement` object returned by `Connection.prepare()`, allowing for various ways to execute the prepared query and retrieve results.

```APIDOC
## PreparedStatement Class Methods

### Description
The `PreparedStatement` object represents a compiled SQL query ready for execution. It provides methods to fetch results in different formats, execute statements with multiple argument sets, and inspect the statement's properties.

### Methods

#### `cursor(*args, prefetch=None, timeout=None)`

##### Description
Returns a cursor factory for the prepared statement.

##### Parameters
*   **args** (any) - Query arguments.
*   **prefetch** (int) - The number of rows the cursor iterator will prefetch (defaults to 50).
*   **timeout** (float) - Optional timeout in seconds.

##### Returns
A `CursorFactory` object.

#### `executemany(args, *, timeout=None)`

##### Description
Execute the statement for each sequence of arguments in `args`.

##### Parameters
*   **args** (iterable) - An iterable containing sequences of arguments.
*   **timeout** (float) - Optional timeout value in seconds.

##### Returns
None. This method discards the results of the operations.
Added in version 0.22.0.

#### `explain(*args, analyze=False)`

##### Description
Return the execution plan of the statement.

##### Parameters
*   **args** (any) - Query arguments.
*   **analyze** (bool) - If `True`, the statement will be executed and the run time statistics added to the return value.

##### Returns
An object representing the execution plan. This value is actually a deserialized JSON output of the SQL `EXPLAIN` command.

#### `fetch(*args, timeout=None)`

##### Description
Execute the statement and return a list of `Record` objects.

##### Parameters
*   **args** (any) - Query arguments.
*   **timeout** (float) - Optional timeout value in seconds.

##### Returns
A list of `Record` instances.

#### `fetchmany(args, *, timeout=None)`

##### Description
Execute the statement and return a list of `Record` objects. This is equivalent to calling `fetch` with the same arguments.

##### Parameters
*   **args** (any) - Query arguments.
*   **timeout** (float) - Optional timeout value in seconds.

##### Returns
A list of `Record` instances.
Added in version 0.30.0.

#### `fetchrow(*args, timeout=None)`

##### Description
Execute the statement and return the first row.

##### Parameters
*   **args** (any) - Query arguments.
*   **timeout** (float) - Optional timeout value in seconds.

##### Returns
The first row as a `Record` instance.

#### `fetchval(*args, column=0, timeout=None)`

##### Description
Execute the statement and return a value from the first row.

##### Parameters
*   **args** (any) - Query arguments.
*   **column** (int) - Numeric index within the record of the value to return (defaults to 0).
*   **timeout** (float) - Optional timeout in seconds. If not specified, defaults to the value of `command_timeout` argument to the `Connection` instance constructor.

##### Returns
The value of the specified column of the first record.

#### `get_attributes()`

##### Description
Return a description of relation attributes (columns).

##### Returns
A tuple of `asyncpg.types.Attribute`.

##### Example
```python
st = await self.con.prepare('''
    SELECT typname, typnamespace FROM pg_type
''')
print(st.get_attributes())
```

#### `get_name() → str`

##### Description
Return the name of this prepared statement.
Added in version 0.25.0.

##### Returns
string

#### `get_parameters()`

##### Description
Return a description of statement parameters types.

##### Returns
A tuple of `asyncpg.types.Type`.

##### Example
```python
stmt = await connection.prepare('SELECT ($1::int, $2::text)')
print(stmt.get_parameters())
```
```

--------------------------------

### Create Cursor Factory from Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Explains how to obtain a cursor factory from a prepared statement. The cursor factory can then be used to fetch data in batches.

```python
import asyncpg

async def example():
    conn = await asyncpg.connect(user='user', password='password', database='database', host='host')
    try:
        stmt = await conn.prepare('SELECT $1::text')
        cursor_factory = stmt.cursor('some text', prefetch=10)
        # Now use cursor_factory to fetch data
        # async for row in cursor_factory:
        #     print(row)
    finally:
        await conn.close()

asyncpg.run(example())
```

--------------------------------

### Async Context Management for Asyncpg Pool (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Implements asynchronous context management protocols (`__await__`, `__aenter__`, `__aexit__`) for the asyncpg Pool. This allows the pool to be used with `async with` statements for proper initialization and closing.

```python
def __await__(self):
        return self._async__init__().__await__()

    async def __aenter__(self):
        await self._async__init__()
        return self

    async def __aexit__(self, *exc):
        await self.close()
```

--------------------------------

### Asyncpg Connection Initialization

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Initializes a new Connection object, setting up internal attributes for managing the database session. This includes protocol, transport, statement caching, server version detection, and transaction management.

```python
class Connection(metaclass=ConnectionMeta):
    """A representation of a database session.

    Connections are created by calling :func:`~asyncpg.connection.connect`.
    """

    __slots__ = ('_protocol', '_transport', '_loop',
                 '_top_xact', '_aborted',
                 '_pool_release_ctr', '_stmt_cache', '_stmts_to_close',
                 '_stmt_cache_enabled',
                 '_listeners', '_server_version', '_server_caps',
                 '_intro_query', '_reset_query', '_proxy',
                 '_stmt_exclusive_section', '_config', '_params', '_addr',
                 '_log_listeners', '_termination_listeners', '_cancellations',
                 '_source_traceback', '_query_loggers', '__weakref__')

    def __init__(self, protocol, transport, loop,
                 addr,
                 config: connect_utils._ClientConfiguration,
                 params: connect_utils._ConnectionParameters):
        self._protocol = protocol
        self._transport = transport
        self._loop = loop
        self._top_xact = None
        self._aborted = False
        # Incremented every time the connection is released back to a pool.
        # Used to catch invalid references to connection-related resources
        # post-release (e.g. explicit prepared statements).
        self._pool_release_ctr = 0

        self._addr = addr
        self._config = config
        self._params = params

        self._stmt_cache = _StatementCache(
            loop=loop,
            max_size=config.statement_cache_size,
            on_remove=functools.partial(
                _weak_maybe_gc_stmt, weakref.ref(self)),
            max_lifetime=config.max_cached_statement_lifetime)

        self._stmts_to_close = set()
        self._stmt_cache_enabled = config.statement_cache_size > 0

        self._listeners = {}
        self._log_listeners = set()
        self._cancellations = set()
        self._termination_listeners = set()
        self._query_loggers = set()

        settings = self._protocol.get_settings()
        ver_string = settings.server_version
        self._server_version = \
            serverversion.split_server_version_string(ver_string)

        self._server_caps = _detect_server_capabilities(
            self._server_version, settings)

        if self._server_version < (14, 0):
            self._intro_query = introspection.INTRO_LOOKUP_TYPES_13
        else:
            self._intro_query = introspection.INTRO_LOOKUP_TYPES

        self._reset_query = None
        self._proxy = None

        # Used to serialize operations that might involve anonymous
        # statements.  Specifically, we want to make the following
        # operation atomic:
        #    ("prepare an anonymous statement", "use the statement")
        #
        # Used for `con.fetchval()`, `con.fetch()`, `con.fetchrow()`,
        # `con.execute()`, and `con.executemany()`.
        self._stmt_exclusive_section = _Atomic()

        if loop.get_debug():
            self._source_traceback = _extract_stack()
        else:
            self._source_traceback = None

    def __del__(self):
        if not self.is_closed() and self._protocol is not None:
            if self._source_traceback:
                msg = "unclosed connection {!r}; created at:\n {}".format(
                    self, self._source_traceback)
            else:
                msg = (
                    "unclosed connection {!r}; run in asyncio debug "
                    "mode to show the traceback of connection "
                    "origin".format(self)
                )

            warnings.warn(msg, ResourceWarning)
            if not self._loop.is_closed():
                self.terminate()
```

--------------------------------

### Connection Information

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for retrieving information about the connected PostgreSQL server and connection settings.

```APIDOC
## Connection Information

### Description
Provides methods to retrieve essential details about the PostgreSQL server and the current connection.

### Methods

#### `def get_server_pid(self)`

##### Description
Returns the Process ID (PID) of the PostgreSQL server process to which the connection is established.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters
None

##### Request Example
None

##### Response

###### Success Response (integer)
- **PID** (integer) - The PID of the server process.

###### Response Example
```
12345
```

#### `def get_server_version(self)`

##### Description
Returns the version of the connected PostgreSQL server as a named tuple.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters
None

##### Request Example
None

##### Response

###### Success Response (named tuple)
- **version** (named tuple) - A named tuple containing `major`, `minor`, `micro`, `releaselevel`, and `serial` components of the server version.

###### Response Example
```json
{
  "major": 9,
  "minor": 6,
  "micro": 1,
  "releaselevel": "final",
  "serial": 0
}
```

#### `def get_settings(self)`

##### Description
Returns the connection settings as a `asyncpg.ConnectionSettings` object.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters
None

##### Request Example
None

##### Response

###### Success Response (:class:`~asyncpg.ConnectionSettings`)
- **settings** (:class:`~asyncpg.ConnectionSettings`) - An object containing the connection settings.

###### Response Example
```json
{
  "settings": "<asyncpg.ConnectionSettings object>"
}
```
```

--------------------------------

### FETCH Query Results

Source: https://magicstack.github.io/asyncpg/current/api/index

Run a query and retrieve all results as a list of Record objects.

```APIDOC
## async.fetch

### Description
Run a query and return the results as a list of `Record` instances. You can optionally specify a `record_class` to customize the returned record objects.

### Method
`async def fetch(query: str, *args, timeout: float = None, record_class = None) -> list`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **query** (str) - The SQL query text.
- **args** - Query arguments for placeholders in the query.
- **timeout** (float) - Optional timeout value in seconds.
- **record_class** (type) - Optional. A subclass of `Record` to use for returned records. Defaults to the connection's `record_class`.

### Request Example
```python
# Fetch all rows from mytab
records = await con.fetch('SELECT * FROM mytab')
for rec in records:
    print(rec['a']) # or rec.a
```

### Response
#### Success Response (list[Record])
- A list of `Record` instances. The actual type of list elements will be `record_class` if specified.

### Changes
- Changed in version 0.22.0: Added the `record_class` parameter.
```

--------------------------------

### Prepare and Execute a PostgreSQL Query with asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to prepare a PostgreSQL query using asyncpg and then execute it multiple times with different parameters. Prepared statements allow the database to parse, analyze, and compile a query once, reusing the execution plan for subsequent calls, thus improving performance for frequently executed queries.

```python
import asyncpg
import asyncio

async def run():
    conn = await asyncpg.connect()
    stmt = await conn.prepare('''SELECT 2 ^ $1''')
    print(await stmt.fetchval(10))
    print(await stmt.fetchval(20))

asyncio.run(run())
```

--------------------------------

### Create and Initialize Connection Pool Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This code defines the `Pool` class in asyncpg, which manages a pool of database connections. It handles connection acquisition, release, and initialization. The class also includes parameters for minimum and maximum pool size, connection limits, and connection lifetime.

```python
class Pool:
    """A connection pool.

    Connection pool can be used to manage a set of connections to the database.
    Connections are first acquired from the pool, then used, and then released
    back to the pool.  Once a connection is released, it's reset to close all
    open cursors and other resources *except* prepared statements.

    Pools are created by calling :func:`~asyncpg.pool.create_pool`.
    """

    __slots__ = (
        '_queue', '_loop', '_minsize', '_maxsize',
        '_init', '_connect', '_reset', '_connect_args', '_connect_kwargs',
        '_holders', '_initialized', '_initializing', '_closing',
        '_closed', '_connection_class', '_record_class', '_generation',
        '_setup', '_max_queries', '_max_inactive_connection_lifetime'
    )

    def __init__(self, *connect_args,
                 min_size,
                 max_size,
                 max_queries,
                 max_inactive_connection_lifetime,
                 connect=None,
                 setup=None,
                 init=None,
                 reset=None,
                 loop,
                 connection_class,
                 record_class,
                 **connect_kwargs):

        if len(connect_args) > 1:
            warnings.warn(
                "Passing multiple positional arguments to asyncpg.Pool "
                "constructor is deprecated and will be removed in "
                "asyncpg 0.17.0.  The non-deprecated form is "
                "asyncpg.Pool(<dsn>, **kwargs)",
                DeprecationWarning, stacklevel=2)

        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

        if max_size <= 0:
            raise ValueError('max_size is expected to be greater than zero')

        if min_size < 0:
            raise ValueError(
                'min_size is expected to be greater or equal to zero')

        if min_size > max_size:
            raise ValueError('min_size is greater than max_size')

        if max_queries <= 0:
            raise ValueError('max_queries is expected to be greater than zero')

        if max_inactive_connection_lifetime < 0:
            raise ValueError(
                'max_inactive_connection_lifetime is expected to be greater '
                'or equal to zero')

        if not issubclass(connection_class, connection.Connection):
            raise TypeError(
                'connection_class is expected to be a subclass of '
                'asyncpg.Connection, got {!r}'.format(connection_class))

        if not issubclass(record_class, protocol.Record):
            raise TypeError(
                'record_class is expected to be a subclass of '
                'asyncpg.Record, got {!r}'.format(record_class))

        self._minsize = min_size
        self._maxsize = max_size

        self._holders = []
        self._initialized = False
        self._initializing = False
        self._queue = None

        self._connection_class = connection_class
        self._record_class = record_class

        self._closing = False
        self._closed = False
        self._generation = 0

        self._connect = connect if connect is not None else connection.connect
        self._connect_args = connect_args
        self._connect_kwargs = connect_kwargs

        self._setup = setup
        self._init = init
        self._reset = reset

        self._max_queries = max_queries
        self._max_inactive_connection_lifetime = \
            max_inactive_connection_lifetime

    async def _async__init__(self):
        if self._initialized:
            return self
        if self._initializing:
            raise exceptions.InterfaceError(
                'pool is being initialized in another task')
        if self._closed:
            raise exceptions.InterfaceError('pool is closed')
        self._initializing = True
        try:
            await self._initialize()
            return self
        finally:
            self._initializing = False
            self._initialized = True

    async def _initialize(self):
        self._queue = asyncio.LifoQueue(maxsize=self._maxsize)
        for _ in range(self._maxsize):
            ch = PoolConnectionHolder(
                self,
                max_queries=self._max_queries,
                max_inactive_time=self._max_inactive_connection_lifetime,
                setup=self._setup)

            self._holders.append(ch)
            self._queue.put_nowait(ch)

        if self._minsize:
            pass
```

--------------------------------

### fetchmany Method

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a query for each sequence of arguments and returns the results as a list of Record instances. Supports custom Record classes.

```APIDOC
## fetchmany

### Description
Runs a query for each sequence of arguments in *args* and returns the results as a list of :class:`Record`. Allows specifying a custom Record class.

### Method
POST (Implicit, used internally)

### Endpoint
N/A (Internal method representation)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
>>> rows = await con.fetchmany('''
...         INSERT INTO mytab (a, b) VALUES ($1, $2) RETURNING a;
...     ''', [('x', 1), ('y', 2), ('z', 3)])
```

### Response
#### Success Response (200)
- **list** (list of asyncpg.Record or custom record_class) - A list of Record instances.

#### Response Example
```json
{
  "example": "[<Record row=('x',)>, <Record row=('y',)>, <Record row=('z',)>]"
}
```
```

--------------------------------

### Helper Methods for Asyncpg Pool Initialization and State Checks (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Provides internal helper methods for managing the pool's state. `_check_init` ensures the pool is initialized and not closed before an operation. `_drop_statement_cache` and `_drop_type_cache` clear caches on all active connections.

```python
def _check_init(self):
        if not self._initialized:
            if self._initializing:
                raise exceptions.InterfaceError(
                    'pool is being initialized, but not yet ready: '
                    'likely there is a race between creating a pool and '
                    'using it')
            raise exceptions.InterfaceError('pool is not initialized')
        if self._closed:
            raise exceptions.InterfaceError('pool is closed')

def _drop_statement_cache(self):
        # Drop statement cache for all connections in the pool.
        for ch in self._holders:
            if ch._con is not None:
                ch._con._drop_local_statement_cache()

def _drop_type_cache(self):
        # Drop type codec cache for all connections in the pool.
        for ch in self._holders:
            if ch._con is not None:
                ch._con._drop_local_type_cache()
```

--------------------------------

### Format COPY Options in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Formats options for COPY commands, including format, delimiter, null values, and quoting. Handles various option types and applies appropriate quoting.

```python
def _format_copy_opts(self, *, format=None, oids=None, freeze=None,
                          delimiter=None, null=None, header=None, quote=None,
                          escape=None, force_quote=None, force_not_null=None,
                          force_null=None, encoding=None):
        kwargs = dict(locals())
        kwargs.pop('self')
        opts = []

        if force_quote is not None and isinstance(force_quote, bool):
            kwargs.pop('force_quote')
            if force_quote:
                opts.append('FORCE_QUOTE *')

        for k, v in kwargs.items():
            if v is not None:
                if k in ('force_not_null', 'force_null', 'force_quote'):
                    v = '(' + ', '.join(utils._quote_ident(c) for c in v) + ')'
                elif k in ('oids', 'freeze', 'header'):
                    v = str(v)
                else:
                    v = utils._quote_literal(v)

                opts.append('{} {}'.format(k.upper(), v))

        if opts:
            return '(' + ', '.join(opts) + ')'
        else:
            return ''

```

--------------------------------

### FETCH MANY Query Results

Source: https://magicstack.github.io/asyncpg/current/api/index

Run a query for each sequence of arguments and return all results as a list of Record objects.

```APIDOC
## async.fetchmany

### Description
Run a query for each sequence of arguments in `args` and return the combined results as a list of `Record` instances. Supports custom `record_class`.

### Method
`async def fetchmany(query: str, args: list, timeout: float = None, record_class = None) -> list`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **query** (str) - The SQL query to execute.
- **args** (list) - An iterable containing sequences of arguments for each execution of the query.
- **timeout** (float) - Optional timeout value in seconds.
- **record_class** (type) - Optional. A subclass of `Record` to use for returned records. Defaults to the connection's `record_class`.

### Request Example
```python
rows = await con.fetchmany('''
    INSERT INTO mytab (a, b) VALUES ($1, $2) RETURNING a;
''', [('x', 1), ('y', 2), ('z', 3)])
# rows will be a list of Record objects
```

### Response
#### Success Response (list[Record])
- A list of `Record` instances. The actual type of list elements will be `record_class` if specified.

### Changes
- Added in version 0.30.0.
```

--------------------------------

### Connection Settings and Status

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieve connection settings and check the connection status.

```APIDOC
## GET /connection/settings

### Description
Retrieves the current connection settings.

### Method
GET

### Endpoint
`/connection/settings`

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **ConnectionSettings** (object) - An object containing connection configuration details.

#### Response Example
```json
{
  "user": "postgres",
  "database": "mydatabase",
  "host": "localhost",
  "port": 5432
}
```

## GET /connection/status

### Description
Checks if the connection to the database is closed.

### Method
GET

### Endpoint
`/connection/status`

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **is_closed** (boolean) - True if the connection is closed, False otherwise.

#### Response Example
```json
{
  "is_closed": false
}
```

## GET /connection/transaction/status

### Description
Checks if the connection is currently within a transaction.

### Method
GET

### Endpoint
`/connection/transaction/status`

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **is_in_transaction** (boolean) - True if inside a transaction, False otherwise.

#### Response Example
```json
{
  "is_in_transaction": true
}
```
```

--------------------------------

### Programmatic SSL Context Configuration (require)

Source: https://magicstack.github.io/asyncpg/current/api/index

Sets up an SSL context for a direct SSL connection using sslmode=require, disabling server certificate and host verification. This is useful when server verification is not strictly needed. It uses ssl.create_default_context with hostname checking and verification explicitly turned off.

```python
import asyncpg
import asyncio
import ssl

async def main():
    sslctx = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH)
    sslctx.check_hostname = False
    sslctx.verify_mode = ssl.CERT_NONE
    con = await asyncpg.connect(user='postgres', ssl=sslctx)
    await con.close()

asyncio.run(main())
```

--------------------------------

### Pool Configuration

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Methods for configuring and updating connection parameters for the pool.

```APIDOC
## Pool Configuration

### set_connect_args(dsn=None, **connect_kwargs)

Set the new connection arguments for this pool. The new connection arguments will be used for all subsequent new connection attempts. Existing connections will remain until they expire. Use :meth:`Pool.expire_connections() <asyncpg.pool.Pool.expire_connections>` to expedite the connection expiry.

**Parameters**

*   **dsn** (str) - Connection arguments specified using as a single string in the following format: ``postgres://user:pass@host:port/database?option=value``.
*   **\*\*connect_kwargs** - Keyword arguments for the :func:`~asyncpg.connection.connect` function.

**Version Added:** 0.16.0
```

--------------------------------

### Connection

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Represents a database session. Connections are created by calling :func:`~asyncpg.connection.connect`.

```APIDOC
## Class Connection

### Description
A representation of a database session. Connections are created by calling :func:`~asyncpg.connection.connect`.

### Initialization

`__init__(self, protocol, transport, loop, addr, config: connect_utils._ClientConfiguration, params: connect_utils._ConnectionParameters)`

Initializes a new Connection instance.

### Methods

#### `add_listener(self, channel, callback)`

Adds a listener for Postgres notifications.

- **channel** (str) - Required - The channel to listen on.
- **callback** (callable) - Required - A callable or coroutine function that will receive notifications. It accepts `connection`, `pid`, `channel`, and `payload` as arguments.

### Request Example

```python
async def my_listener(connection, pid, channel, payload):
    print(f"Received notification on channel '{channel}' from PID {pid} with payload: {payload}")

await connection.add_listener('my_channel', my_listener)
```

### Response

This method does not return a value upon successful registration.
```

--------------------------------

### Execute Many with Options (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a query multiple times with different argument sets, optimized for bulk operations. It supports returning rows and integrates with statement caching.

```python
async def _executemany(
        self,
        query,
        args,
        timeout,
        return_rows=False,
        record_class=None,
    ):
        executor = lambda stmt, timeout: self._protocol.bind_execute_many(
            state=stmt,
            args=args,
            portal_name='',
            timeout=timeout,
            return_rows=return_rows,
        )
        timeout = self._protocol._get_timeout(timeout)
        with self._stmt_exclusive_section:
            with self._time_and_log(query, args, timeout):
                result, _ = await self._do_execute(
                    query, executor, timeout, record_class=record_class
                )
        return result
```

--------------------------------

### Listeners

Source: https://magicstack.github.io/asyncpg/current/api/index

Manage callbacks for database notifications and connection events.

```APIDOC
## POST /connection/listener/add

### Description
Adds a callback to listen for notifications on a specific channel.

### Method
POST

### Endpoint
`/connection/listener/add`

### Parameters
#### Request Body
- **channel** (string) - Required - The channel to listen on.
- **callback** (callable) - Required - The callback function to be executed when a notification is received.

### Request Example
```json
{
  "channel": "my_channel",
  "callback": "notification_handler"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Listener added successfully."
}
```

## DELETE /connection/listener/remove

### Description
Removes a previously added listener callback for a specific channel.

### Method
DELETE

### Endpoint
`/connection/listener/remove`

### Parameters
#### Request Body
- **channel** (string) - Required - The channel the listener was registered on.
- **callback** (callable) - Required - The callback function to remove.

### Request Example
```json
{
  "channel": "my_channel",
  "callback": "notification_handler"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Listener removed successfully."
}
```

## POST /connection/termination_listener/add

### Description
Adds a callback to be executed when the connection is terminated.

### Method
POST

### Endpoint
`/connection/termination_listener/add`

### Parameters
#### Request Body
- **callback** (callable) - Required - The callback function to execute on connection termination.

### Request Example
```json
{
  "callback": "connection_closed_handler"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Termination listener added successfully."
}
```

## DELETE /connection/termination_listener/remove

### Description
Removes a previously added termination listener callback.

### Method
DELETE

### Endpoint
`/connection/termination_listener/remove`

### Parameters
#### Request Body
- **callback** (callable) - Required - The termination listener callback function to remove.

### Request Example
```json
{
  "callback": "connection_closed_handler"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Termination listener removed successfully."
}
```
```

--------------------------------

### BitString Creation and Conversion (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to create a BitString from an integer and convert it back to an integer. Supports specifying bit order and signed representation, similar to Python's int.to_bytes and int.from_bytes.

```python
from asyncpg.types import BitString

# Create a BitString from an integer
bit_string = BitString.from_int(10, length=8, bitorder='big', signed=False)
print(f"BitString created: {bit_string}")

# Convert BitString back to an integer
integer_value = bit_string.to_int(bitorder='big', signed=False)
print(f"Integer value: {integer_value}")

# Example with signed integer and different bit order
negative_bit_string = BitString.from_int(-5, length=8, bitorder='little', signed=True)
print(f"Negative BitString: {negative_bit_string}")
negative_int_value = negative_bit_string.to_int(bitorder='little', signed=True)
print(f"Negative integer value: {negative_int_value}")
```

--------------------------------

### BaseCursor Bind and Execute (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Binds arguments to a prepared statement and executes it. This method manages portal creation and checks for existing open portals, returning execution results.

```Python
    async def _bind_exec(self, n, timeout):
        self._check_ready()

        if self._portal_name:
            raise exceptions.InterfaceError(
                'cursor already has an open portal')

        con = self._connection
        protocol = con._protocol

        self._portal_name = con._get_unique_id('portal')
        buffer, _, self._exhausted = await protocol.bind_execute(
            self._state, self._args, self._portal_name, n, True, timeout)
        return buffer
```

--------------------------------

### Create and Manage asyncpg Pool Manually (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Shows how to create a connection pool using 'await' directly and then manually acquire and release connections. This method is not recommended due to potential resource leaks if not handled carefully with try/finally blocks.

```python
pool = await asyncpg.create_pool(user='postgres', command_timeout=60)
con = await pool.acquire()
try:
    await con.fetch('SELECT 1')
finally:
    await pool.release(con)
```

--------------------------------

### Configure SSL Context for asyncpg (verify-full)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This Python code snippet demonstrates how to configure an SSL context for asyncpg to enforce 'verify-full' mode. It loads a CA bundle for server verification, enables hostname checking, and loads client certificates and keys for authentication. This is equivalent to using specific DSN parameters like sslmode=verify-full, sslcert, sslkey, and sslrootcert.

```pycon
>>> import asyncpg
>>> import asyncio
>>> import ssl
>>> async def main():
...     # Load CA bundle for server certificate verification,
...     # equivalent to sslrootcert= in DSN.
...     sslctx = ssl.create_default_context(
...         ssl.Purpose.SERVER_AUTH,
...         cafile="path/to/ca_bundle.pem")
...     # If True, equivalent to sslmode=verify-full, if False:
...     # sslmode=verify-ca.
...     sslctx.check_hostname = True
...     # Load client certificate and private key for client
...     # authentication, equivalent to sslcert= and sslkey= in
...     # DSN.
...     sslctx.load_cert_chain(
...         "path/to/client.cert",
...         keyfile="path/to/client.key",
...     )
...     con = await asyncpg.connect(user='postgres', ssl=sslctx)
...     await con.close()
>>> asyncio.run(main())
```

--------------------------------

### Transaction Management

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Provides a context manager for creating and managing PostgreSQL transactions.

```APIDOC
## Transaction Management

### Description
Creates and manages PostgreSQL transactions using a context manager. Transaction parameters like isolation level, read-only status, and deferrability can be specified.

### Method

#### `def transaction(self, *, isolation=None, readonly=False, deferrable=False)`

##### Description
Creates a `asyncpg.Transaction` object that can be used as an asynchronous context manager to demarcate transaction boundaries.

##### Method
`def` (returns a transaction object)

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
```python
async with connection.transaction(isolation='serializable'):
    # Perform transactional operations here
    await connection.execute('UPDATE ...')
```

##### Response

###### Success Response (:class:`~asyncpg.Transaction`)
- **transaction** (:class:`~asyncpg.Transaction`) - A transaction object.

###### Response Example
```json
{
  "transaction": "<asyncpg.Transaction object>"
}
```
```

--------------------------------

### Query Execution

Source: https://magicstack.github.io/asyncpg/current/api/index

Methods for executing SQL queries, including single commands, multiple commands, and fetching results.

```APIDOC
## POST /execute

### Description
Executes an SQL command or a series of commands using one of the pool's connections. This method behaves identically to `Connection.execute()`.

### Method
POST

### Endpoint
/execute

### Parameters
#### Request Body
- **query** (str) - Required - The SQL command(s) to execute.
- **args** (list) - Optional - Arguments to be substituted into the query.
- **timeout** (float) - Optional - A timeout for the execution.

### Request Example
```json
{
  "query": "INSERT INTO users (name) VALUES ($1)",
  "args": ["Alice"],
  "timeout": 5.0
}
```

### Response
#### Success Response (200)
- **result** (str) - The result of the SQL command execution.

## POST /executemany

### Description
Executes an SQL command for each sequence of arguments provided in a list. This method behaves identically to `Connection.executemany()`.

### Method
POST

### Endpoint
/executemany

### Parameters
#### Request Body
- **command** (str) - Required - The SQL command to execute for each set of arguments.
- **args** (list) - Required - A list of argument sequences to be used with the command.
- **timeout** (float) - Optional - A timeout for the execution.

### Request Example
```json
{
  "command": "INSERT INTO products (name, price) VALUES ($1, $2)",
  "args": [["Laptop", 1200.00], ["Mouse", 25.00]],
  "timeout": 10.0
}
```

### Response
#### Success Response (200)
Indicates successful execution of the command for all argument sequences.

## GET /fetch

### Description
Executes a query and returns the results as a list of records. This method behaves identically to `Connection.fetch()`.

### Method
GET

### Endpoint
/fetch

### Parameters
#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments to be substituted into the query.
- **timeout** (float) - Optional - A timeout for the query execution.
- **record_class** (str) - Optional - The class to use for representing records.

### Request Example
```
GET /fetch?query=SELECT+*+FROM+users&args=["Alice"]&timeout=5.0
```

### Response
#### Success Response (200)
- **records** (list) - A list of records returned by the query.

#### Response Example
```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```

## GET /fetchmany

### Description
Executes a query for each sequence of arguments and returns the results as a list of records. This method behaves identically to `Connection.fetchmany()`.

### Method
GET

### Endpoint
/fetchmany

### Parameters
#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Required - A list of argument sequences for the query.
- **timeout** (float) - Optional - A timeout for the query execution.
- **record_class** (str) - Optional - The class to use for representing records.

### Request Example
```
GET /fetchmany?query=SELECT+name+FROM+users+WHERE+id+%3D+%241&args=[[1], [2]]&timeout=10.0
```

### Response
#### Success Response (200)
- **records** (list) - A list of records returned by the queries.

## GET /fetchrow

### Description
Executes a query and returns the first row of the result. This method behaves identically to `Connection.fetchrow()`.

### Method
GET

### Endpoint
/fetchrow

### Parameters
#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments to be substituted into the query.
- **timeout** (float) - Optional - A timeout for the query execution.
- **record_class** (str) - Optional - The class to use for representing records.

### Request Example
```
GET /fetchrow?query=SELECT+name+FROM+users+WHERE+id+%3D+1
```

### Response
#### Success Response (200)
- **record** (object) - The first record returned by the query, or null if no rows are found.

#### Response Example
```json
{
  "name": "Alice"
}
```

## GET /fetchval

### Description
Executes a query and returns a single value from the first row and first column of the result. This method behaves identically to `Connection.fetchval()`.

### Method
GET

### Endpoint
/fetchval

### Parameters
#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** (list) - Optional - Arguments to be substituted into the query.
- **column** (integer) - Optional - The index of the column to retrieve (defaults to 0).
- **timeout** (float) - Optional - A timeout for the query execution.

### Request Example
```
GET /fetchval?query=SELECT+COUNT(*) FROM users
```

### Response
#### Success Response (200)
- **value** (any) - The value from the specified column of the first row.

#### Response Example
```json
{
  "value": 100
}
```
```

--------------------------------

### Query Logging

Source: https://magicstack.github.io/asyncpg/current/api/index

Manage callbacks for logging executed queries.

```APIDOC
## POST /connection/query_logger/add

### Description
Adds a callback function to be executed for each query logged by the connection. The callback receives a `LoggedQuery` object.

### Method
POST

### Endpoint
`/connection/query_logger/add`

### Parameters
#### Request Body
- **callback** (callable) - Required - The callable or coroutine function to be called with query log data.

### Request Example
```json
{
  "callback": "my_query_logger_function"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Query logger added successfully."
}
```

## DELETE /connection/query_logger/remove

### Description
Removes a previously added query logger callback.

### Method
DELETE

### Endpoint
`/connection/query_logger/remove`

### Parameters
#### Request Body
- **callback** (callable) - Required - The query logger callback function to remove.

### Request Example
```json
{
  "callback": "my_query_logger_function"
}
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Query logger removed successfully."
}
```
```

--------------------------------

### _StatementCache Initialization and Configuration (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Initializes the _StatementCache with parameters for the event loop, maximum cache size, a callback for removed statements, and maximum statement lifetime. It uses an OrderedDict for LRU cache implementation.

```python
class _StatementCache:

    __slots__ = ('_loop', '_entries', '_max_size', '_on_remove',
                 '_max_lifetime')

    def __init__(self, *, loop, max_size, on_remove, max_lifetime):
        self._loop = loop
        self._max_size = max_size
        self._on_remove = on_remove
        self._max_lifetime = max_lifetime

        # We use an OrderedDict for LRU implementation.  Operations:
        #
        # * We use a simple `__setitem__` to push a new entry:
        #       `entries[key] = new_entry`
        #   That will push `new_entry` to the *end* of the entries dict.
        #
        # * When we have a cache hit, we call
        #       `entries.move_to_end(key, last=True)`
        #   to move the entry to the *end* of the entries dict.
        #
        # * When we need to remove entries to maintain `max_size`, we call
        #       `entries.popitem(last=False)`
        #   to remove an entry from the *beginning* of the entries dict.
        #
        # So new entries and hits are always promoted to the end of the
        # entries dict, whereas the unused one will group in the
        # beginning of it.
        self._entries = collections.OrderedDict()
```

--------------------------------

### CURSOR API

Source: https://magicstack.github.io/asyncpg/current/api/index

Creates a cursor factory for executing SQL queries. Allows for prefetching and specifying record classes.

```APIDOC
## POST /cursor

### Description
Returns a cursor factory for a given SQL query. This allows for efficient iteration over query results, especially for large datasets. You can configure prefetching and the class used for returned records.

### Method
POST

### Endpoint
/cursor

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL query to execute.
- **args** - Optional - Query arguments to be bound to the query.
- **prefetch** (int) - Optional - The number of rows the cursor iterator will prefetch. Defaults to 50.
- **timeout** (float) - Optional - Timeout value in seconds.
- **record_class** (type) - Optional - The class to use for records returned by this cursor. Must be a subclass of `Record`. If not specified, a per-connection `record_class` is used.

### Request Example
```json
{
  "query": "SELECT * FROM users WHERE id = $1",
  "args": [123],
  "prefetch": 100,
  "record_class": "UserRecord"
}
```

### Response
#### Success Response (200)
- **cursor_factory** (object) - A `CursorFactory` object.

#### Response Example
```json
{
  "cursor_factory": { ... }
}
```
```

--------------------------------

### fetch

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a query and returns a list of Record objects. It handles query binding and execution, returning all rows fetched.

```APIDOC
## GET /fetch

### Description
Executes the statement and returns a list of :class:`Record` objects.

### Method
GET

### Endpoint
/fetch

### Parameters
#### Query Parameters
- **query** (str) - Required - Query text
- **args** (tuple) - Required - Query arguments
- **timeout** (float) - Optional - Optional timeout value in seconds.

### Response
#### Success Response (200)
- **data** (list[Record]) - A list of :class:`Record` instances.

#### Response Example
```json
[
  {
    "column1": "value1",
    "column2": 123
  },
  {
    "column1": "value2",
    "column2": 456
  }
]
```
```

--------------------------------

### CursorFactory Initialization and Iteration (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Initializes a CursorFactory with connection details and query parameters. The __aiter__ method returns a CursorIterator for efficient result traversal, supporting prefetching.

```Python
class CursorFactory(connresource.ConnectionResource):
    """A cursor interface for the results of a query.

    A cursor interface can be used to initiate efficient traversal of the
    results of a large query.
    """

    __slots__ = (
        '_state',
        '_args',
        '_prefetch',
        '_query',
        '_timeout',
        '_record_class',
    )

    def __init__(
        self,
        connection,
        query,
        state,
        args,
        prefetch,
        timeout,
        record_class
    ):
        super().__init__(connection)
        self._args = args
        self._prefetch = prefetch
        self._query = query
        self._timeout = timeout
        self._state = state
        self._record_class = record_class
        if state is not None:
            state.attach()

    @connresource.guarded
    def __aiter__(self):
        prefetch = 50 if self._prefetch is None else self._prefetch
        return CursorIterator(
            self._connection,
            self._query,
            self._state,
            self._args,
            self._record_class,
            prefetch,
            self._timeout,
        )
```

--------------------------------

### asyncpg.connect()

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

A coroutine to establish a connection to a PostgreSQL server. Connection parameters can be specified via a DSN string or keyword arguments.

```APIDOC
## POST /connect

### Description
Establishes a connection to a PostgreSQL server. This function supports connection parameters specified via a DSN string or individual keyword arguments, with keyword arguments overriding DSN values. Default connection parameters can be set using environment variables.

### Method
POST

### Endpoint
/connect

### Parameters
#### Query Parameters
- **dsn** (string) - Optional - Connection arguments specified using as a single string in the libpq connection URI format.
- **host** (string | list[string]) - Optional - Database host address or a sequence of addresses. Defaults to DSN, PGHOST env var, common socket directories, or localhost.
- **port** (integer | list[integer]) - Optional - Port number to connect to. Defaults to DSN, PGPORT env var, or 5432.
- **user** (string) - Optional - The name of the database role for authentication. Defaults to DSN, PGUSER env var, or OS user name.
- **database** (string) - Optional - The name of the database to connect to. Defaults to DSN, PGDATABASE env var, or computed user name.
- **password** (string | callable) - Optional - Password for authentication. Defaults to DSN or PGPASSWORD env var. Can be a string or a callable returning a string.
- **passfile** (string) - Optional - Path to the password file (defaults to ~/.pgpass).
- **loop** (asyncio.BaseEventLoop) - Optional - An asyncio event loop instance. Defaults to the default event loop.
- **timeout** (float) - Optional - Connection timeout in seconds (default: 60).
- **statement_cache_size** (integer) - Optional - Size of the statement cache (default: 100).
- **max_cached_statement_lifetime** (integer) - Optional - Maximum lifetime for cached statements in seconds (default: 300).
- **max_cacheable_statement_size** (integer) - Optional - Maximum size of cacheable statements in bytes (default: 15360).
- **command_timeout** (integer) - Optional - Command timeout in seconds (default: None).
- **ssl** (bool | ssl.SSLContext) - Optional - SSL configuration. Can be True, False, or an ssl.SSLContext object.
- **direct_tls** (bool) - Optional - Whether to use direct TLS connection (default: None).
- **connection_class** (type) - Optional - Custom connection class (default: asyncpg.connection.Connection).
- **record_class** (type) - Optional - Custom record class (default: protocol.Record).
- **server_settings** (dict) - Optional - Dictionary of server settings to apply.
- **target_session_attrs** (string) - Optional - Target session attributes (e.g., 'read-write').
- **krbsrvname** (string) - Optional - Kerberos service name.
- **gsslib** (string) - Optional - GSSAPI library path.

### Request Example
```json
{
  "dsn": "postgres://user:password@host:port/database",
  "timeout": 30,
  "command_timeout": 15
}
```

### Response
#### Success Response (200)
- **connection** (asyncpg.connection.Connection) - A new Connection object representing the established connection.

#### Response Example
```json
{
  "connection": "<asyncpg.connection.Connection object at 0x...>"
}
```
```

--------------------------------

### Acquire Database Connection from Pool (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to acquire a database connection from an asyncpg pool. Connections can be used directly or within an 'async with' block for automatic release. A timeout can be specified for acquiring the connection.

```python
async with pool.acquire() as con:
    await con.execute(...) 
```

```python
con = await pool.acquire()
try:
    await con.execute(...)
finally:
    await pool.release(con)
```

--------------------------------

### Prepare Statement Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Prepares a SQL query as a statement for efficient repeated execution. Supports optional naming, timeouts, and custom record classes for results. If a record_class is not provided, a per-connection default is used.

```python
async def prepare(
        self,
        query,
        *,
        name=None,
        timeout=None,
        record_class=None,
    ):
        """Create a *prepared statement* for the specified query.

        :param str query:
            Text of the query to create a prepared statement for.
        :param str name:
            Optional name of the returned prepared statement.  If not
            specified, the name is auto-generated.
        :param float timeout:
            Optional timeout value in seconds.
        :param type record_class:
            If specified, the class to use for records returned by the
            prepared statement.  Must be a subclass of
            :class:`~asyncpg.Record`.  If not specified, a per-connection
            *record_class* is used.

        :return:
            A :class:`~prepared_stmt.PreparedStatement` instance.

        .. versionchanged:: 0.22.0
            Added the *record_class* parameter.

        .. versionchanged:: 0.25.0
            Added the *name* parameter.
        """
        return await self._prepare(
            query,
            name=name,
            timeout=timeout,
            use_cache=False,
            record_class=record_class,
        )
```

--------------------------------

### Create Prepared Statements with asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Prepares a SQL query as a statement for efficient execution. Supports optional naming, timeouts, and custom record classes for results. Added in version 0.22.0 for record_class and 0.25.0 for name.

```python
await con._async_prepare(
    query: str,
    name: str | None = None,
    timeout: float | None = None,
    record_class: type | None = None
)
```

--------------------------------

### Establish PostgreSQL Connection with asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

A coroutine to establish a connection to a PostgreSQL server. Parameters can be specified via a DSN string or keyword arguments. Defaults can be set using environment variables. Returns a Connection object.

```python
async def connect(
    dsn=None,
    *, 
    host=None,
    port=None,
    user=None,
    database=None,
    password=None,
    passfile=None,
    loop=None,
    timeout=60,
    statement_cache_size=100,
    max_cached_statement_lifetime=300,
    max_cacheable_statement_size=1024 * 15,
    command_timeout=None,
    ssl=None,
    direct_tls=None,
    connection_class=Connection,
    record_class=protocol.Record,
    server_settings=None,
    target_session_attrs=None,
    krbsrvname=None,
    gsslib=None):
    r"""A coroutine to establish a connection to a PostgreSQL server.

    The connection parameters may be specified either as a connection
    URI in *dsn*, or as specific keyword arguments, or both.
    If both *dsn* and keyword arguments are specified, the latter
    override the corresponding values parsed from the connection URI.
    The default values for the majority of arguments can be specified
    using `environment variables <postgres envvars_>`_.

    Returns a new :class:`~asyncpg.connection.Connection` object.

    :param dsn:
        Connection arguments specified using as a single string in the
        `libpq connection URI format`_:
        ``postgres://user:password@host:port/database?option=value``.
        The following options are recognized by asyncpg: ``host``,
        ``port``, ``user``, ``database`` (or ``dbname``), ``password``,
        ``passfile``, ``sslmode``, ``sslcert``, ``sslkey``, ``sslrootcert``,
        and ``sslcrl``.  Unlike libpq, asyncpg will treat unrecognized
        options as `server settings`_ to be used for the connection.

        .. note::

           The URI must be *valid*, which means that all components must
           be properly quoted with :py:func:`urllib.parse.quote_plus`, and
           any literal IPv6 addresses must be enclosed in square brackets.
           For example:

           .. code-block:: text

              postgres://dbuser@[fe80::1ff:fe23:4567:890a%25eth0]/dbname

    :param host:
        Database host address as one of the following:

        - an IP address or a domain name;
        - an absolute path to the directory containing the database
          server Unix-domain socket (not supported on Windows);
        - a sequence of any of the above, in which case the addresses
          will be tried in order, and the first successful connection
          will be returned.

        If not specified, asyncpg will try the following, in order:

        - host address(es) parsed from the *dsn* argument,
        - the value of the ``PGHOST`` environment variable,
        - on Unix, common directories used for PostgreSQL Unix-domain
          sockets: ``"/run/postgresql"``, ``"/var/run/postgresl"``,
          ``"/var/pgsql_socket"``, ``"/private/tmp"``, and ``"/tmp"``,
        - ``"localhost"``.

    :param port:
        Port number to connect to at the server host
        (or Unix-domain socket file extension).  If multiple host
        addresses were specified, this parameter may specify a
        sequence of port numbers of the same length as the host sequence,
        or it may specify a single port number to be used for all host
        addresses.

        If not specified, the value parsed from the *dsn* argument is used,
        or the value of the ``PGPORT`` environment variable, or ``5432`` if
        neither is specified.

    :param user:
        The name of the database role used for authentication.

        If not specified, the value parsed from the *dsn* argument is used,
        or the value of the ``PGUSER`` environment variable, or the
        operating system name of the user running the application.

    :param database:
        The name of the database to connect to.

        If not specified, the value parsed from the *dsn* argument is used,
        or the value of the ``PGDATABASE`` environment variable, or the
        computed value of the *user* argument.

    :param password:
        Password to be used for authentication, if the server requires
        one.  If not specified, the value parsed from the *dsn* argument
        is used, or the value of the ``PGPASSWORD`` environment variable.
        Note that the use of the environment variable is discouraged as
        other users and applications may be able to read it without needing
        specific privileges.  It is recommended to use *passfile* instead.

        Password may be either a string, or a callable that returns a string.
        If a callable is provided, it will be called each time a new connection
        is established.

    :param passfile:
        The name of the file used to store passwords
        (defaults to ``~/.pgpass``, or ``%APPDATA%\postgresql\pgpass.conf``
        on Windows).

    :param loop:
        An asyncio event loop instance.  If ``None``, the default
        event loop will be used.

    :param float timeout:
        Connection timeout in seconds.
    """
    pass
```

--------------------------------

### Python: PoolConnectionProxy - Initialize and Proxy Attributes

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

PoolConnectionProxy acts as a proxy for a connection object managed by the pool. Its initializer takes a holder and the actual connection, setting up the proxy relationship. It also overrides __getattr__ to delegate attribute lookups to the underlying connection, ensuring seamless access to connection methods and properties.

```python
class PoolConnectionProxy(connection._ConnectionProxy,
                          metaclass=PoolConnectionProxyMeta,
                          wrap=True):

    __slots__ = ('_con', '_holder')

    def __init__(self, holder: 'PoolConnectionHolder',
                 con: connection.Connection):
        self._con = con
        self._holder = holder
        con._set_proxy(self)

    def __getattr__(self, attr):
        # Proxy all unresolved attributes to the wrapped Connection object.
        return getattr(self._con, attr)

    def _detach(self) -> connection.Connection:
        if self._con is None:
            return

        con, self._con = self._con, None
        con._set_proxy(None)
        return con

    def __repr__(self):
        if self._con is None:
            return '<{classname} [released] {id:#x}>'.format(
                classname=self.__class__.__name__, id=id(self))
        else:
            return '<{classname} {con!r} {id:#x}>'.format(
                classname=self.__class__.__name__, con=self._con, id=id(self))
```

--------------------------------

### Fetch Query Results as a List of Records

Source: https://magicstack.github.io/asyncpg/current/api/index

Shows how to execute a query and retrieve all results as a list of `Record` objects using the `fetch` method. It supports passing query arguments and an optional `record_class` for custom record types.

```python
await con.fetch("SELECT * FROM mytab WHERE a > $1", 150)
```

--------------------------------

### Create Pool and Acquire Connection for Multiple Operations (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Illustrates creating a connection pool and then acquiring a single connection within an 'async with' block to perform multiple database operations, such as creating a table and fetching data. This pattern is useful for sequential operations on a dedicated connection.

```python
async with asyncpg.create_pool(user='postgres',
                               command_timeout=60) as pool:
    async with pool.acquire() as con:
        await con.execute('''
           CREATE TABLE names (
              id serial PRIMARY KEY,
              name VARCHAR (255) NOT NULL)
        ''')
        await con.fetch('SELECT 1')
```

--------------------------------

### LISTEN/UNLISTEN Channel Management

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for managing channel listeners, allowing clients to subscribe to and unsubscribe from PostgreSQL NOTIFY events.

```APIDOC
## LISTEN/UNLISTEN Channel Management

### Description
Manages listeners for PostgreSQL channels, enabling asynchronous notification handling. Callbacks can be regular functions or coroutine functions.

### Methods

#### `async def add_listener(self, channel, callback)`

##### Description
Adds a callback to listen for messages on a specified channel.

##### Method
`async def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None

#### `async def remove_listener(self, channel, callback)`

##### Description
Removes a previously added callback for a specified channel.

##### Method
`async def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None
```

--------------------------------

### create_pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Creates a connection pool for managing database connections. It can be used with `async with` for automatic management or directly with `await` for manual control.

```APIDOC
## POST /create_pool

### Description
Creates a connection pool to manage a set of connections to the database. Connections are acquired from the pool, used, and then released back. Prepared statements and cursors remain valid after release, but listeners are removed.

### Method
POST

### Endpoint
/create_pool

### Parameters
#### Query Parameters
- **dsn** (str) - Optional - Connection arguments in the format: `postgres://user:pass@host:port/database?option=value`.
- **min_size** (int) - Optional - The number of connections the pool will be initialized with. Defaults to 10.
- **max_size** (int) - Optional - The maximum number of connections in the pool. Defaults to 10.
- **max_queries** (int) - Optional - The number of queries after which a connection is closed and replaced. Defaults to 50000.
- **max_inactive_connection_lifetime** (float) - Optional - The number of seconds after which inactive connections will be closed. Defaults to 300.0. Set to 0 to disable.
- **connection_class** (Connection) - Optional - The class to use for connections. Must be a subclass of `asyncpg.connection.Connection`.
- **record_class** (type) - Optional - The class to use for records returned by queries. Must be a subclass of `asyncpg.Record`.

#### Request Body
Parameters for `connect()` function.

### Request Example
```python
import asyncpg

async def main():
    async with asyncpg.create_pool(user='postgres', command_timeout=60) as pool:
        await pool.fetch('SELECT 1')

async with asyncpg.create_pool(user='postgres',
                               command_timeout=60) as pool:
    async with pool.acquire() as con:
        await con.execute('''
           CREATE TABLE names (
              id serial PRIMARY KEY,
              name VARCHAR (255) NOT NULL)
        ''')
        await con.fetch('SELECT 1')

# Manual control (not recommended)
pool = await asyncpg.create_pool(user='postgres', command_timeout=60)
con = await pool.acquire()
try:
    await con.fetch('SELECT 1')
finally:
    await pool.release(con)
```

### Response
#### Success Response (200)
- **pool** (Pool) - An instance of the `Pool` class.

#### Response Example
```json
{
  "pool_instance": "<asyncpg.pool.Pool object at 0x...>"
}
```

### Errors
- **InterfaceError**: Raised on any attempted operation on a released connection (0.10.0+).
- **InterfaceError**: Raised on attempted operation on a prepared statement or cursor from a released connection (0.13.0+).
- **InterfaceWarning**: Produced if active listeners are present on a connection when released to the pool (0.13.0+).
```

--------------------------------

### Query Execution

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Methods for executing SQL queries through the connection pool.

```APIDOC
## Query Execution

### execute(query: str, *args, timeout: float=None) -> str

Execute an SQL command (or commands). Pool performs this operation using one of its connections. Other than that, it behaves identically to :meth:`Connection.execute() <asyncpg.connection.Connection.execute>`.

**Parameters**

*   **query** (str) - The SQL query to execute.
*   **\*args** - Positional arguments to pass to the query.
*   **timeout** (float, optional) - The timeout in seconds for the operation.

**Returns**

*   (str) - The command status.

**Version Added:** 0.10.0

### executemany(command: str, args, *, timeout: float=None)

Execute an SQL command with multiple sets of arguments. This method behaves identically to :meth:`Connection.executemany() <asyncpg.connection.Connection.executemany>` when used with a pool.

**Parameters**

*   **command** (str) - The SQL command to execute.
*   **args** - An iterable of argument tuples or lists for the command.
*   **timeout** (float, optional) - The timeout in seconds for the operation.
```

--------------------------------

### Execute SQL Commands with asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes an SQL command or multiple commands. Can accept query arguments for parameterized queries. Returns the status of the last SQL command. Supports optional timeouts.

```python
await con.execute('''
    CREATE TABLE mytab (a int);
    INSERT INTO mytab (a) VALUES (100), (200), (300);
''')

await con.execute('''
    INSERT INTO mytab (a) VALUES ($1), ($2)
''', 10, 20)
```

--------------------------------

### Fetch Multiple Rows as Records (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a query for each sequence of arguments in 'args' and returns the results as a list of asyncpg.Record instances. An optional 'record_class' can be provided to specify the type of the returned records. Handles query execution and result aggregation.

```python
await con.fetchmany(
            '''
            INSERT INTO mytab (a, b) VALUES ($1, $2) RETURNING a;
        ''',
            [('x', 1), ('y', 2), ('z', 3)]
        )
```

--------------------------------

### Execute Queries with asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes SQL queries asynchronously using asyncpg. This method handles query execution, argument binding, and optional return status, allowing for flexible data manipulation and retrieval. It is designed to be robust and efficient, utilizing internal statement caches.

```python
async def _execute(
    self,
    query,
    args,
    limit,
    timeout,
    *,
    return_status=False,
    ignore_custom_codec=False,
    record_class=None
):
    with self._stmt_exclusive_section:
        result, _ = await self.__execute(
            query,
            args,
            limit,
            timeout,
            return_status=return_status,
            record_class=record_class,
            ignore_custom_codec=ignore_custom_codec,
        )
    return result
```

--------------------------------

### FETCH ONE Value

Source: https://magicstack.github.io/asyncpg/current/api/index

Run a query and return a specific value from the first row.

```APIDOC
## async.fetchval

### Description
Run a query and return a single value from the first row of the result set. By default, it returns the value from the first column (index 0).

### Method
`async def fetchval(query: str, *args, column: int = 0, timeout: float = None)`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **query** (str) - The SQL query text.
- **args** - Query arguments for placeholders in the query.
- **column** (int) - The zero-based index of the column whose value to return. Defaults to 0.
- **timeout** (float) - Optional timeout value in seconds. Defaults to `command_timeout`.

### Request Example
```python
# Get the count of records
count = await con.fetchval('SELECT COUNT(*) FROM mytab')
# Get a specific value from the first row
first_value = await con.fetchval('SELECT a FROM mytab ORDER BY a LIMIT 1', column=0)
```

### Response
#### Success Response (Any | None)
- The value of the specified column from the first record, or `None` if no records were returned.
```

--------------------------------

### Asyncpg Connection Proxy Base Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

A base class designed to facilitate `isinstance(Connection)` checks. It does not define any specific methods or attributes, serving purely as a type marker within the asyncpg library.

```python
class _ConnectionProxy:
    # Base class to enable `isinstance(Connection)` check.
    __slots__ = ()

```

--------------------------------

### fetch Method

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Fetches the first row of a query result as a Record instance or None if no records are returned. Allows specifying a custom Record class.

```APIDOC
## fetch

### Description
Fetches the first row of a query result as a :class:`~asyncpg.Record` instance, or None if no records were returned by the query. If specified, *record_class* is used as the type for the result value.

### Method
POST (Implicit, used internally)

### Endpoint
N/A (Internal method representation)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
None

### Response
#### Success Response (200)
- **Record** (asyncpg.Record or custom record_class) - The first row of the query result, or None.

#### Response Example
```json
{
  "example": "<Record row=('value1', 'value2')>"
}
```
```

--------------------------------

### Fetch Records Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a SQL query and returns all results as a list of records. Allows specifying query arguments, a timeout, and a custom record class for the returned objects. Defaults to asyncpg.Record if no record_class is provided.

```python
async def fetch(
        self,
        query,
        *args,
        timeout=None,
        record_class=None
    ) -> list:
        """Run a query and return the results as a list of :class:`Record`.

        :param str query:
            Query text.
        :param args:
            Query arguments.
        :param float timeout:
            Optional timeout value in seconds.
        :param type record_class:
            If specified, the class to use for records returned by this method.
            Must be a subclass of :class:`~asyncpg.Record`.  If not specified,
            a per-connection *record_class* is used.

        :return list:
            A list of :class:`~asyncpg.Record` instances.  If specified, the
            actual type of list elements would be *record_class*.

        .. versionchanged:: 0.22.0
            Added the *record_class* parameter.
        """
        self._check_open()
        return await self._execute(
            query,
            args,
            0,
            timeout,
            record_class=record_class,
        )
```

--------------------------------

### Copy Data Out to File or Writer (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Handles copying data from a database query result to a specified output. The output can be a file path, a file-like object, or a callable that returns an awaitable. It manages opening and closing files if a path is provided.

```Python
async def _copy_out(self, copy_stmt, output, timeout):
        path = None

        writer = None
        opened_by_us = False
        run_in_executor = self._loop.run_in_executor

        if path is not None:
            # a path
            f = await run_in_executor(None, open, path, 'wb')
            opened_by_us = True
        elif hasattr(output, 'write'):
            # file-like
            f = output
        elif callable(output):
            # assuming calling output returns an awaitable.
            writer = output
        else:
            raise TypeError(
                'output is expected to be a file-like object, '
                'a path-like object or a coroutine function, '
                'not {}'.format(type(output).__name__)
            )

        if writer is None:
            async def _writer(data):
                await run_in_executor(None, f.write, data)
            writer = _writer

        try:
            return await self._protocol.copy_out(copy_stmt, writer, timeout)
        finally:
            if opened_by_us:
                f.close()
```

--------------------------------

### copy_from_query Method

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies the results of a query to a file or file-like object, supporting various COPY statement options.

```APIDOC
## copy_from_query

### Description
Copies the results of a query to a file or file-like object. This method supports various options for the PostgreSQL `COPY` statement.

### Method
POST (Implicit, used internally)

### Endpoint
N/A (Internal method representation)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
# Example for copy_from_query is not provided in the source text.
# Assuming a similar structure to copy_from_table.
```

### Response
#### Success Response (200)
- **str** - The status string of the COPY command (e.g., 'COPY 100').

#### Response Example
```json
{
  "example": "COPY 100"
}
```
```

--------------------------------

### Basic asyncpg Database Operations in Python

Source: https://magicstack.github.io/asyncpg/current/usage

Demonstrates the fundamental usage of asyncpg to connect to a PostgreSQL database, create a table, insert data, fetch a record, and close the connection. It uses standard Python asyncio and the asyncpg library. Dependencies include 'asyncpg', 'datetime', and 'asyncio'.

```python
import asyncio
import asyncpg
import datetime

async def main():
    # Establish a connection to an existing database named "test"
    # as a "postgres" user.
    conn = await asyncpg.connect('postgresql://postgres@localhost/test')
    # Execute a statement to create a new table.
    await conn.execute('\
        CREATE TABLE users(
            id serial PRIMARY KEY,
            name text,
            dob date
        )
    ')

    # Insert a record into the created table.
    await conn.execute('\
        INSERT INTO users(name, dob) VALUES($1, $2)
    ', 'Bob', datetime.date(1984, 3, 1))

    # Select a row from the table.
    row = await conn.fetchrow(
        'SELECT * FROM users WHERE name = $1', 'Bob')
    # *row* now contains
    # asyncpg.Record(id=1, name='Bob', dob=datetime.date(1984, 3, 1))

    # Close the connection.
    await conn.close()

asyncio.run(main())

```

--------------------------------

### PoolAcquireContext Context Manager (`async with pool.acquire()`)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Manages the acquisition and release of a single connection from the pool using an `async with` statement. It ensures that a connection is acquired before entering the block and automatically released upon exiting.

```APIDOC
## ASYNC WITH POOL.ACQUIRE

### Description
Use a connection acquired from the pool as an asynchronous context manager. This ensures the connection is automatically released back to the pool after use, even if errors occur.

### Method
ASYNC WITH

### Endpoint
N/A

### Parameters
#### Path Parameters
None

#### Query Parameters
* **timeout** (float | None) - Optional - The maximum time in seconds to wait for a connection to become available.

#### Request Body
None

### Request Example
```python
async def query_data(pool):
    async with pool.acquire(timeout=10) as connection:
        # Use the connection here
        result = await connection.fetch('SELECT * FROM my_table')
        return result
    # Connection is automatically released here
```

### Response
#### Success Response
* **connection** (Connection) - The acquired connection object.

#### Response Example
N/A
```

--------------------------------

### ServerVersion Tuple Structure (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Illustrates the structure of the ServerVersion tuple used by asyncpg to represent PostgreSQL server versions. It breaks down the version into major, minor, micro, release level, and serial components.

```python
from asyncpg.types import ServerVersion

# Example of creating a ServerVersion tuple
server_version = ServerVersion(major=14, minor=2, micro=5, releaselevel='stable', serial=1)

# Accessing version components
print(f"Major version: {server_version.major}")
print(f"Minor version: {server_version.minor}")
print(f"Micro version: {server_version.micro}")
print(f"Release level: {server_version.releaselevel}")
print(f"Serial: {server_version.serial}")

# Using aliases
print(f"Alias for major: {server_version[0]}")
print(f"Alias for minor: {server_version[1]}")
```

--------------------------------

### Fetch Query Results as List (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Runs a query and returns the results as a list of Record objects. This operation is performed using a connection from the pool and mirrors the functionality of Connection.fetch(). It accepts a query, arguments, and optional timeout and record class.

```python
async def fetch(self,
            query,
            *args,
            timeout=None,
            record_class=None
    ) -> list:
        """Run a query and return the results as a list of :class:`Record`.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.fetch() <asyncpg.connection.Connection.fetch>`.

        .. versionadded:: 0.10.0
        """
        async with self.acquire() as con:
            return await con.fetch(
                query,
                *args,
                timeout=timeout,
                record_class=record_class
            )
```

--------------------------------

### Manage Query Logging with Context Manager

Source: https://magicstack.github.io/asyncpg/current/api/index

A context manager to add and remove callbacks for logging executed queries. The callback receives a LoggedQuery object containing details about the query execution.

```python
class QuerySaver:
    def __init__(self):
        self.queries = []
    def __call__(self, record):
        self.queries.append(record.query)

with con.query_logger(QuerySaver()):
    await con.execute("SELECT 1")
print(log.queries)
```

--------------------------------

### Execute SQL Command with Arguments (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Executes an SQL command for each sequence of arguments provided. This method utilizes a connection from the pool and behaves identically to Connection.executemany(). It returns the results of the command execution.

```python
async def executemany(self,
            command,
            args,
            timeout=None) -> None:
        """Execute an SQL *command* for each sequence of arguments in *args*.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.executemany() <asyncpg.connection.Connection.executemany>`.

        .. versionadded:: 0.10.0
        """
        async with self.acquire() as con:
            return await con.executemany(command, args, timeout=timeout)
```

--------------------------------

### Query Loggers

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for adding and removing loggers that are invoked whenever queries are executed.

```APIDOC
## Query Loggers

### Description
Manages loggers that are called when queries are executed. Loggers receive a `LoggedQuery` object containing details about the query execution.

### Methods

#### `def add_query_logger(self, callback)`

##### Description
Adds a logger to be called when queries are executed.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None

#### `def remove_query_logger(self, callback)`

##### Description
Removes a previously added query logger.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None
```

--------------------------------

### Pool Context Manager (`async with`)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Provides a convenient way to manage the pool's lifecycle within an `async with` block. When entering the block, the pool is initialized. When exiting, the pool is automatically closed.

```APIDOC
## ASYNC WITH POOL

### Description
Use the pool as an asynchronous context manager to automatically handle initialization and closing.

### Method
ASYNC WITH

### Endpoint
N/A

### Parameters
None

### Request Example
```python
import asyncpg

async def main():
    pool = await asyncpg.create_pool(user='user', password='password', database='database')
    async with pool:
        # Use the pool here. It will be automatically closed upon exiting the block.
        async with pool.acquire() as connection:
            await connection.execute('SELECT 1')

    # Pool is closed here
```

### Response
#### Success Response
* **None** - The context manager handles setup and teardown.

#### Response Example
N/A
```

--------------------------------

### EXECUTE API

Source: https://magicstack.github.io/asyncpg/current/api/index

Executes a single or multiple SQL commands. This is a general-purpose method for running SQL statements.

```APIDOC
## POST /execute

### Description
Executes an SQL command or multiple SQL commands. This method is suitable for any SQL statement, including DDL, DML, and utility commands. It can process multiple commands in a single call if no arguments are provided.

### Method
POST

### Endpoint
/execute

### Parameters
#### Path Parameters
None

#### Query Parameters
- **query** (str) - Required - The SQL command(s) to execute.
- **args** - Optional - Query arguments to be bound to the query.
- **timeout** (float) - Optional - Timeout value in seconds.

### Request Example
```json
{
  "query": "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(50));",
  "timeout": 5.0
}
```

### Response
#### Success Response (200)
- **status** (str) - The status string returned by the execution of the SQL command(s).

#### Response Example
```json
{
  "status": "CREATE TABLE"
}
```
```

--------------------------------

### Copy Records to Table using Pool (Binary COPY)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Copies a list of records to a specified table using binary COPY via a pool connection. This method is efficient for bulk insertion of structured data. It mirrors the functionality of Connection.copy_records_to_table().

```python
async def copy_records_to_table(
        self,
        table_name,
        *,
        records,
        columns=None,
        schema_name=None,
        timeout=None,
        where=None
    ):
        """Copy a list of records to the specified table using binary COPY.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.copy_records_to_table()
        <asyncpg.connection.Connection.copy_records_to_table>`.

        .. versionadded:: 0.24.0
        """
        async with self.acquire() as con:
            return await con.copy_records_to_table(
                table_name,
                records=records,
                columns=columns,
                schema_name=schema_name,
                timeout=timeout,
                where=where
            )
```

--------------------------------

### POST /create_pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Creates a connection pool for managing PostgreSQL connections asynchronously. It can be used with async with statements or directly with await.

```APIDOC
## POST /create_pool

### Description
Creates a connection pool for managing PostgreSQL connections asynchronously. It can be used with async with statements or directly with await.

### Method
POST

### Endpoint
/create_pool

### Parameters
#### Query Parameters
- **dsn** (str) - Optional - Connection arguments specified using as a single string in the following format: `postgres://user:pass@host:port/database?option=value`.

#### Request Body
- **min_size** (int) - Optional - Number of connections the pool will be initialized with. Defaults to 10.
- **max_size** (int) - Optional - Max number of connections in the pool. Defaults to 10.
- **max_queries** (int) - Optional - Number of queries after a connection is closed and replaced with a new connection. Defaults to 50000.
- **max_inactive_connection_lifetime** (float) - Optional - Number of seconds after which inactive connections in the pool will be closed. Pass `0` to disable this mechanism. Defaults to 300.0.
- **connect_kwargs** (dict) - Optional - Keyword arguments for the :func:`~asyncpg.connection.connect` function.
- **connection_class** (Connection) - Optional - The class to use for connections. Must be a subclass of :class:`~asyncpg.connection.Connection`. Defaults to `asyncpg.connection.Connection`.
- **record_class** (type) - Optional - If specified, the class to use for records returned by queries on the connections in this pool. Must be a subclass of :class:`~asyncpg.Record`.
- **connect** (coroutine) - Optional - A coroutine that is called instead of :func:`~asyncpg.connection.connect` whenever the pool needs to make a new connection. Must return an instance of type specified by *connection_class* or :class:`~asyncpg.connection.Connection` if *connection_class* was not specified.
- **setup** (coroutine) - Optional - A coroutine to prepare a connection right before it is returned from :meth:`Pool.acquire()`. An example use case would be to automatically set up notifications listeners for all connections of a pool.
- **init** (coroutine) - Optional - A coroutine to initialize a connection when it is created. An example use case would be to setup type codecs with :meth:`Connection.set_builtin_type_codec()` or :meth:`Connection.set_type_codec()`.
- **reset** (coroutine) - Optional - A coroutine to reset a connection before it is returned to the pool by :meth:`Pool.release()`. The function is supposed to reset any changes made to the database session so that the next acquirer gets the connection in a well-defined state.

### Request Example
```json
{
  "min_size": 5,
  "max_size": 20,
  "max_inactive_connection_lifetime": 600.0
}
```

### Response
#### Success Response (200)
- **pool** (Pool) - A connection pool object.

#### Response Example
```json
{
  "pool": "<asyncpg.pool.Pool object>"
}
```
```

--------------------------------

### copy_from_table Method

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies table contents to a file or file-like object, supporting various COPY statement options.

```APIDOC
## copy_from_table

### Description
Copies table contents to a file or file-like object. This method supports various options for the PostgreSQL `COPY` statement.

### Method
POST (Implicit, used internally)

### Endpoint
N/A (Internal method representation)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
>>> import asyncpg
>>> import asyncio
>>> async def run():
...     con = await asyncpg.connect(user='postgres')
...     result = await con.copy_from_table(
...         'mytable', columns=('foo', 'bar'),
...         output='file.csv', format='csv')
...     print(result)
... 
>>> asyncio.run(run())
```

### Response
#### Success Response (200)
- **str** - The status string of the COPY command (e.g., 'COPY 100').

#### Response Example
```json
{
  "example": "COPY 100"
}
```
```

--------------------------------

### Fetch First Row from Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared statement and returns the first row as a Record instance. Returns None if no data is found.

```Python
    @connresource.guarded
    async def fetchrow(self, *args, timeout=None):
        """Execute the statement and return the first row.

        :param str query: Query text
        :param args: Query arguments
        :param float timeout: Optional timeout value in seconds.

        :return: The first row as a :class:`Record` instance.
        """
        data = await self.__bind_execute(args, 1, timeout)
        if not data:
            return None
        return data[0]
```

--------------------------------

### Connection Metadata

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieve metadata about the PostgreSQL server connection.

```APIDOC
## Connection Metadata Methods

### Description
These methods provide information about the current PostgreSQL server connection.

### Methods
1.  **`get_reset_query()`**
    *   **Description**: Returns the SQL query that is sent to the server when a connection is released (used by `Connection.reset()` and `Pool`).
    *   **Added in version**: 0.30.0.

2.  **`get_server_pid()`**
    *   **Description**: Returns the Process ID (PID) of the PostgreSQL server process to which the connection is bound.

3.  **`get_server_version()`**
    *   **Description**: Returns the version of the connected PostgreSQL server as a named tuple, similar to `sys.version_info`.
    *   **Example**: `con.get_server_version()` might return `sys.version_info(major=14, minor=5, micro=0, releaselevel='final', serial=0)`.
```

--------------------------------

### Copy Data to Table (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies data from a source (file path, file-like object, or async iterable) to a specified table using asyncpg. Requires 'asyncpg' and 'asyncio'. Supports various COPY options like columns, schema, timeout, format, delimiter, and a 'where' clause (PostgreSQL 12+). Returns the COPY command status.

```python
import asyncpg
import asyncio
async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_to_table(
        'mytable', source='datafile.tbl')
    print(result)

asyncio.run(run())
```

--------------------------------

### Copy Records to Table (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies a list of records (as tuples or an asynchronous iterable) to a specified table using binary COPY with asyncpg. Requires 'asyncpg' and 'asyncio'. Supports optional column specification, schema, timeout, and a 'where' clause (PostgreSQL 12+). Returns the COPY command status.

```python
import asyncpg
import asyncio
async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_records_to_table(
        'mytable', records=[
            (1, 'foo', 'bar'),
            (2, 'ham', 'spam')])
    print(result)

asyncio.run(run())
```

```python
import asyncpg
import asyncio
async def run():
    con = await asyncpg.connect(user='postgres')
    async def record_gen(size):
        for i in range(size):
            yield (i,)
    result = await con.copy_records_to_table(
        'mytable', records=record_gen(100))
    print(result)

asyncio.run(run())
```

--------------------------------

### Execute SQL Command via Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This asynchronous Python method executes an SQL command using a connection from the asyncpg pool. It wraps the `Connection.execute()` method, handling connection acquisition and releasing. It supports query parameters and an optional timeout.

```python
    async def execute(self, query: str, *args, timeout: float=None) -> str:
        """Execute an SQL command (or commands).

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.execute() <asyncpg.connection.Connection.execute>`.

        .. versionadded:: 0.10.0
        """
        async with self.acquire() as con:
            return await con.execute(query, *args, timeout=timeout)
```

--------------------------------

### Copy Query Results to File (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies the results of a given SQL query to a file or file-like object. It accepts the query string and its arguments, along with options for the COPY statement such as format, delimiter, and encoding. This method facilitates exporting query data efficiently.

```python
await con.copy_from_query(
            query,
            *args,
            output=output_file,
            format='csv',
            delimiter=',',
            header=True
        )
```

--------------------------------

### Copy Data From Query to File (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Executes a query and copies its results to a specified output, such as a file. Supports various COPY statement options and can handle different output formats like CSV. Requires asyncpg and asyncio libraries.

```python
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_from_query(
        'SELECT foo, bar FROM mytable WHERE foo > $1', 10,
        output='file.csv', format='csv')
    print(result)

asyncio.run(run())
```

--------------------------------

### fetchmany

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a query and returns a list of Record objects, potentially a subset of all results. Designed for fetching results in chunks.

```APIDOC
## GET /fetchmany

### Description
Executes the statement and returns a list of :class:`Record` objects.

### Method
GET

### Endpoint
/fetchmany

### Parameters
#### Query Parameters
- **args** (list) - Required - Query arguments.
- **timeout** (float) - Optional - Optional timeout value in seconds.

### Response
#### Success Response (200)
- **data** (list[Record]) - A list of :class:`Record` instances.

#### Response Example
```json
[
  {
    "column1": "value1",
    "column2": 123
  },
  {
    "column1": "value2",
    "column2": 456
  }
]
```
```

--------------------------------

### Fetch Query Results with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Runs a query and returns results as a list of 'Record' objects using a connection from the asyncpg pool. This method is equivalent to Connection.fetch(). Supports query arguments, timeout, and custom record classes.

```python
await pool.fetch(query, *args, timeout=timeout, record_class=record_class)
```

--------------------------------

### copy_from_query

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies the results of a query to a specified output. The output can be a file path, a file-like object, or a coroutine function that accepts bytes.

```APIDOC
## POST /copy_from_query

### Description
Copies the results of a query to a specified output. The output can be a file path, a file-like object, or a coroutine function that accepts bytes. This method is useful for exporting query results directly to storage or processing them as they are generated.

### Method
POST

### Endpoint
/copy_from_query

### Parameters
#### Path Parameters
None

#### Query Parameters
* **query** (str) - Required - The SQL query whose results will be copied.
* **args** (list) - Optional - Query arguments to be used with the query.
* **output** (path-like object, file-like object, coroutine function) - Required - Specifies where the copied data should go. This can be a file path, an open file object, or a coroutine function that accepts bytes.
* **timeout** (float) - Optional - A timeout value in seconds for the operation.
* **format** (str) - Optional - The format of the output (e.g., 'csv', 'binary').
* **oids** (bool) - Optional - Include OIDs in the output.
* **delimiter** (str) - Optional - The delimiter to use for CSV format.
* **null** (str) - Optional - The string to represent NULL values.
* **header** (bool) - Optional - Include a header row in CSV output.
* **quote** (str) - Optional - The character used for quoting in CSV format.
* **escape** (str) - Optional - The character used for escaping in CSV format.
* **force_quote** (list) - Optional - A list of column names to force quoting.
* **encoding** (str) - Optional - The encoding of the output data.

#### Request Body
(Not applicable for this method, parameters are passed directly)

### Request Example
```py
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_from_query(
        'SELECT foo, bar FROM mytable WHERE foo > $1',
        10,
        output='file.csv',
        format='csv'
    )
    print(result)

asyncio.run(run())
```

### Response
#### Success Response (200)
* **status** (str) - The status string of the COPY command (e.g., 'COPY 10').

#### Response Example
```json
{
  "status": "COPY 10"
}
```
```

--------------------------------

### Copy Table Data to File (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies data from a specified table to a file or file-like object. Supports specifying columns, schema, and various COPY statement options like format, delimiter, and null values. Returns the status string of the COPY command.

```python
await con.copy_from_table(
            'mytable', columns=('foo', 'bar'),
            output='file.csv', format='csv'
        )
```

--------------------------------

### Connection State and Closing

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for checking the status of a connection and for closing or terminating it.

```APIDOC
## GET /connection/is_closed

### Description
Checks if the connection has been closed. Returns `True` if the connection is closed, `False` otherwise.

### Method
GET

### Endpoint
/connection/is_closed

### Response
#### Success Response (200)
- **is_closed** (boolean) - `True` if the connection is closed, `False` otherwise.

#### Response Example
```json
{
  "is_closed": false
}
```

## POST /connection/close

### Description
Closes the connection gracefully. Waits for any pending data to be sent and received before closing. An optional timeout can be specified.

### Method
POST

### Endpoint
/connection/close

### Parameters
#### Query Parameters
- **timeout** (float) - Optional - Timeout value in seconds.

### Request Example
```json
{
  "timeout": 5.0
}
```

### Response
#### Success Response (200)
- **message** (string) - Indicates the connection has been closed successfully.

#### Response Example
```json
{
  "message": "Connection closed gracefully."
}
```

## POST /connection/terminate

### Description
Terminates the connection immediately without waiting for pending data. This is a forceful closure.

### Method
POST

### Endpoint
/connection/terminate

### Response
#### Success Response (200)
- **message** (string) - Indicates the connection has been terminated.

#### Response Example
```json
{
  "message": "Connection terminated."
}
```
```

--------------------------------

### Asyncpg Server Capabilities Structure

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Defines a named tuple for representing PostgreSQL server capabilities. It includes boolean flags for features like advisory locks, notifications, PL/pgSQL support, SQL reset, closing all connections, JIT compilation, and copying from where.

```python
ServerCapabilities = collections.namedtuple(
    'ServerCapabilities',
    ['advisory_locks', 'notifications', 'plpgsql', 'sql_reset',
     'sql_close_all', 'sql_copy_from_where', 'jit'])
ServerCapabilities.__doc__ = 'PostgreSQL server capabilities.'

```

--------------------------------

### Copy Data In from File or Reader (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Handles copying data from a source into the database. The source can be a file path, a file-like object, an asynchronous iterable, or raw data. It supports reading data in chunks and managing file operations.

```Python
async def _copy_in(self, copy_stmt, source, timeout):
        try:
            path = os.fspath(source)
        except TypeError:
            # source is not a path-like object
            path = None

        f = None
        reader = None
        data = None
        opened_by_us = False
        run_in_executor = self._loop.run_in_executor

        if path is not None:
            # a path
            f = await run_in_executor(None, open, path, 'rb')
            opened_by_us = True
        elif hasattr(source, 'read'):
            # file-like
            f = source
        elif isinstance(source, collections.abc.AsyncIterable):
            # assuming calling output returns an awaitable.
            # copy_in() is designed to handle very large amounts of data, and
            # the source async iterable is allowed to return an arbitrary
            # amount of data on every iteration.
            reader = source
        else:
            # assuming source is an instance supporting the buffer protocol.
            data = source

        if f is not None:
            # Copying from a file-like object.
            class _Reader:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    data = await run_in_executor(None, f.read, 524288)
                    if len(data) == 0:
                        raise StopAsyncIteration
                    else:
                        return data

            reader = _Reader()

        try:
            return await self._protocol.copy_in(
                copy_stmt, reader, data, None, None, timeout)
        finally:
            if opened_by_us:
                await run_in_executor(None, f.close)
```

--------------------------------

### Execute SQL Commands for Multiple Argument Sets

Source: https://magicstack.github.io/asyncpg/current/api/index

Illustrates the `executemany` method for executing an SQL command for each sequence of arguments provided. This is useful for bulk inserts or updates where the same command structure is applied to different data sets. Note that this operation is atomic.

```python
await con.executemany('''
    INSERT INTO mytab (a) VALUES ($1, $2, $3);
''', [(1, 2, 3), (4, 5, 6)])
```

--------------------------------

### Copy Table Data to Output (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Copies table contents to a file or file-like object. This operation is handled by a pool connection and mirrors Connection.copy_from_table(). It requires the table name and output destination, with numerous optional parameters for customization.

```python
async def copy_from_table(
            self,
            table_name,
            *,
            output,
            columns=None,
            schema_name=None,
            timeout=None,
            format=None,
            oids=None,
            delimiter=None,
            null=None,
            header=None,
            quote=None,
            escape=None,
            force_quote=None,
            encoding=None
    ):
        """Copy table contents to a file or file-like object.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.copy_from_table() <asyncpg.connection.Connection.copy_from_table>`.

        .. versionadded:: 0.24.0
        """
        async with self.acquire() as con:
            return await con.copy_from_table(
                table_name,
                output=output,
                columns=columns,
                schema_name=schema_name,
                timeout=timeout,
                format=format,
                oids=oids,
                delimiter=delimiter,
                null=null,
                header=header,
                quote=quote,
                escape=escape,
                force_quote=force_quote,
                encoding=encoding
            )
```

--------------------------------

### Access Connection Settings (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates how to retrieve specific settings from an asyncpg connection object. The `get_settings()` method returns a `ConnectionSettings` object, which allows accessing settings like `client_encoding` as attributes. An `AttributeError` is raised if a setting is not defined.

```python
# Assuming 'connection' is an asyncpg Connection object
connection.get_settings().client_encoding
```

--------------------------------

### Copy Data to Table using Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Copies data from a source to a specified table using a connection from the pool. Supports various options for data formatting, delimiters, and column mapping. It behaves identically to Connection.copy_to_table().

```python
async def copy_to_table(
        self,
        table_name,
        *,
        source,
        columns=None,
        schema_name=None,
        timeout=None,
        format=None,
        oids=None,
        freeze=None,
        delimiter=None,
        null=None,
        header=None,
        quote=None,
        escape=None,
        force_quote=None,
        force_not_null=None,
        force_null=None,
        encoding=None,
        where=None
    ):
        """Copy data to the specified table.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.copy_to_table()
        <asyncpg.connection.Connection.copy_to_table>`.

        .. versionadded:: 0.24.0
        """
        async with self.acquire() as con:
            return await con.copy_to_table(
                table_name,
                source=source,
                columns=columns,
                schema_name=schema_name,
                timeout=timeout,
                format=format,
                oids=oids,
                freeze=freeze,
                delimiter=delimiter,
                null=null,
                header=header,
                quote=quote,
                escape=escape,
                force_quote=force_quote,
                force_not_null=force_not_null,
                force_null=force_null,
                encoding=encoding,
                where=where
            )
```

--------------------------------

### Bind Execution Logic (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Internal method to bind arguments to a prepared statement and execute it. It captures the data, status, and any pending state.

```Python
    async def __bind_execute(self, args, limit, timeout):
        data, status, _ = await self.__do_execute(
            lambda protocol: protocol.bind_execute(
                self._state, args, '', limit, True, timeout))
        self._last_status = status
        return data
```

--------------------------------

### Copy Query Results to Output (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Copies the results of a query to a file or file-like object. This method uses a pool connection and is analogous to Connection.copy_from_query(). It requires the query and output destination, along with various optional parameters for control.

```python
async def copy_from_query(
            self,
            query,
            *args,
            output,
            timeout=None,
            format=None,
            oids=None,
            delimiter=None,
            null=None,
            header=None,
            quote=None,
            escape=None,
            force_quote=None,
            encoding=None
    ):
        """Copy the results of a query to a file or file-like object.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.copy_from_query() <asyncpg.connection.Connection.copy_from_query>`.

        .. versionadded:: 0.24.0
        """
        async with self.acquire() as con:
            return await con.copy_from_query(
                query,
                *args,
                output=output,
                
```

--------------------------------

### POST /copy_records_to_table

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies a list of records to a specified table using the binary COPY command. Supports asynchronous iterables for records and an optional WHERE clause for filtering (requires PostgreSQL 12+).

```APIDOC
## POST /copy_records_to_table

### Description
Copies a list of records to the specified table using binary COPY. Asynchronous iterables are supported for records. An optional WHERE clause can be provided for filtering, which requires PostgreSQL version 12 or later.

### Method
POST

### Endpoint
This method is part of the asyncpg connection object, not a direct HTTP endpoint.

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **table_name** (str) - Required - The name of the table to copy data to.
- **records** (iterable) - Required - An iterable (or asynchronous iterable) returning row tuples to copy into the table.
- **columns** (list[str]) - Optional - A list of column names to copy.
- **schema_name** (str) - Optional - An optional schema name to qualify the table.
- **where** (str) - Optional - An optional SQL expression used to filter rows when copying. Requires PostgreSQL 12+.
- **timeout** (float) - Optional - Optional timeout value in seconds.

### Request Example
```python
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_records_to_table(
        'mytable', records=[
            (1, 'foo', 'bar'),
            (2, 'ham', 'spam')
        ])
    print(result)

asyncio.run(run())
```

### Response
#### Success Response (200)
- **status_string** (str) - The status string of the COPY command (e.g., 'COPY 2').

#### Response Example
```json
{
  "status_string": "COPY 2"
}
```
```

--------------------------------

### Log Queries with asyncpg Context Manager

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Provides a context manager to add and remove query logging callbacks. Any SQL query executed within this context will be passed to the provided callback function, which can be a regular function or a coroutine. This is useful for monitoring query performance and debugging.

```python
@contextlib.contextmanager
def query_logger(self, callback):
    """Context manager that adds `callback` to the list of query loggers,
    and removes it upon exit.

    :param callable callback:
        A callable or a coroutine function receiving one argument:
        **record**, a LoggedQuery containing `query`, `args`, `timeout`,
        `elapsed`, `exception`, `conn_addr`, and `conn_params`.

    Example:

    .. code-block:: pycon

        >>> class QuerySaver:
                def __init__(self):
                    self.queries = []
                def __call__(self, record):
                    self.queries.append(record.query)
        >>> with con.query_logger(QuerySaver()):
        >>>     await con.execute("SELECT 1")
        >>> print(log.queries)
        ['SELECT 1']

    .. versionadded:: 0.29.0
    """
    self.add_query_logger(callback)
    yield
    self.remove_query_logger(callback)
```

--------------------------------

### Execute Prepared Statement and Fetch Value (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared SQL statement and returns a single value from the first row. Handles potential transaction rollbacks and JSON decoding.

```Python
            tr = self._connection.transaction()
            await tr.start()
            try:
                data = await self._connection.fetchval(query, *args)
            finally:
                await tr.rollback()
        else:
            data = await self._connection.fetchval(query, *args)

        return json.loads(data)
```

--------------------------------

### FETCH ONE Row

Source: https://magicstack.github.io/asyncpg/current/api/index

Run a query and return only the first row of the result set.

```APIDOC
## async.fetchrow

### Description
Run a query and return the first row of the result set as a `Record` instance. Returns `None` if no records are found. Supports custom `record_class`.

### Method
`async def fetchrow(query: str, *args, timeout: float = None, record_class = None)`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **query** (str) - The SQL query text.
- **args** - Query arguments for placeholders in the query.
- **timeout** (float) - Optional timeout value in seconds.
- **record_class** (type) - Optional. A subclass of `Record` to use for the returned record. Defaults to the connection's `record_class`.

### Request Example
```python
# Fetch the first user
user = await con.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
if user:
    print(user['name']) # or user.name
```

### Response
#### Success Response (Record | None)
- The first row as a `Record` instance, or `None` if no records were returned.

### Changes
- Changed in version 0.22.0: Added the `record_class` parameter.
```

--------------------------------

### Fetch Multiple Query Results with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Runs a query for each sequence of arguments in a list and returns all results as a list of 'Record' objects using a connection from the asyncpg pool. This method is equivalent to Connection.fetchmany().

```python
await pool.fetchmany(query, args, timeout=timeout, record_class=record_class)
```

--------------------------------

### Pool State Information

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Methods to retrieve the current state and configuration of the connection pool.

```APIDOC
## Pool State Information

### is_closing()

Return ``True`` if the pool is closing or is closed.

**Version Added:** 0.28.0

### get_size()

Return the current number of connections in this pool.

**Version Added:** 0.25.0

### get_min_size()

Return the minimum number of connections in this pool.

**Version Added:** 0.25.0

### get_max_size()

Return the maximum allowed number of connections in this pool.

**Version Added:** 0.25.0

### get_idle_size()

Return the current number of idle connections in this pool.

**Version Added:** 0.25.0
```

--------------------------------

### EXECUTE MANY SQL Commands

Source: https://magicstack.github.io/asyncpg/current/api/index

Execute an SQL command for each sequence of arguments in a list. This operation is atomic.

```APIDOC
## async.executemany

### Description
Execute an SQL command for each sequence of arguments in `args`. This method was made atomic in version 0.22.0, meaning all executions succeed or none do.

### Method
`async def executemany(command: str, args: list, timeout: float = None)`

### Endpoint
N/A (Method within a connection object)

### Parameters
#### Arguments
- **command** (str) - The SQL command to execute.
- **args** (list) - An iterable containing sequences of arguments for each execution of the command.
- **timeout** (float) - Optional timeout value in seconds. Keyword-only since 0.11.0.

### Request Example
```python
await con.executemany('''
    INSERT INTO mytab (a) VALUES ($1, $2, $3);
''', [(1, 2, 3), (4, 5, 6)])
```

### Response
#### Success Response (None)
- This method discards the results of the operations.

### Changes
- Added in version 0.7.0.
- Changed in version 0.11.0: `timeout` became a keyword-only parameter.
- Changed in version 0.22.0: `executemany()` is now an atomic operation.
```

--------------------------------

### Connect Function Signature (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Defines the signature for the connect function in asyncpg, which establishes a connection to a PostgreSQL database using various connection parameters.

```python
async def connect(dsn=None, *,
                  host=None, port=None,
                  user=None, password=None, passfile=None,
                  database=None,
```

--------------------------------

### Fetch Records from Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared statement and returns a list of Record objects. This method is guarded by 'connresource.guarded' for connection resource management.

```Python
    @connresource.guarded
    async def fetch(self, *args, timeout=None):
        """Execute the statement and return a list of :class:`Record` objects.

        :param str query: Query text
        :param args: Query arguments
        :param float timeout: Optional timeout value in seconds.

        :return: A list of :class:`Record` instances.
        """
        data = await self.__bind_execute(args, 0, timeout)
        return data
```

--------------------------------

### Log Message Listeners

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for managing listeners that are invoked when asynchronous NoticeResponse messages are received from the connection.

```APIDOC
## Log Message Listeners

### Description
Manages listeners for PostgreSQL log messages. Callbacks are invoked for WARNING, NOTICE, DEBUG, INFO, or LOG messages.

### Methods

#### `def add_log_listener(self, callback)`

##### Description
Adds a listener for asynchronous Postgres log messages.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None

#### `def remove_log_listener(self, callback)`

##### Description
Removes a previously added log message listener.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None
```

--------------------------------

### Execute Prepared Statement Multiple Times (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared statement for each sequence of arguments provided. This method discards the results and is suitable for bulk operations.

```Python
    @connresource.guarded
    async def executemany(self, args, *, timeout: float=None):
        """Execute the statement for each sequence of arguments in *args*.

        :param args: An iterable containing sequences of arguments.
        :param float timeout: Optional timeout value in seconds.
        :return None: This method discards the results of the operations.

        .. versionadded:: 0.22.0
        """
        return await self.__do_execute(
            lambda protocol: protocol.bind_execute_many(
                self._state,
                args,
                portal_name='',
                timeout=timeout,
                return_rows=False,
            ))

```

--------------------------------

### Fetch Multiple Rows with Arguments (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Executes a query for each sequence of arguments and returns the results as a list of Record objects. This method uses a pool connection and is equivalent to Connection.fetchmany(). It requires a query and arguments, and supports optional timeout and record class.

```python
async def fetchmany(self, query, args, *, timeout=None, record_class=None):
        """Run a query for each sequence of arguments in *args* and return the results as a list of :class:`Record`.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.fetchmany() <asyncpg.connection.Connection.fetchmany>`.

        .. versionadded:: 0.30.0
        """
        async with self.acquire() as con:
            return await con.fetchmany(
                query, args, timeout=timeout, record_class=record_class
            )
```

--------------------------------

### Configure SSL Context for asyncpg (require mode)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This Python code snippet shows how to configure an SSL context for asyncpg to use 'require' mode without server certificate or host verification. It creates a default SSL context, disables hostname checking, and sets the verify mode to CERT_NONE. This configuration is equivalent to using sslmode=require in the DSN.

```pycon
>>> import asyncpg
>>> import asyncio
>>> import ssl
>>> async def main():
...     sslctx = ssl.create_default_context(
...         ssl.Purpose.SERVER_AUTH)
...     sslctx.check_hostname = False
...     sslctx.verify_mode = ssl.CERT_NONE
...     con = await asyncpg.connect(user='postgres', ssl=sslctx)
...     await con.close()
>>> asyncio.run(main())
```

--------------------------------

### Custom asyncpg Record with Dot Notation

Source: https://magicstack.github.io/asyncpg/current/faq

This snippet shows how to create a custom `asyncpg.Record` class that allows accessing columns using dot notation. This is useful for cleaner code when working with query results. It achieves this by overriding the `__getattr__` method to delegate attribute access to dictionary-style item access.

```python
class MyRecord(asyncpg.Record):
    def __getattr__(self, name):
        return self[name]
```

--------------------------------

### Fetch Multiple Sets of Query Results

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates using `fetchmany` to execute a query for each sequence of arguments and collect all results into a single list of `Record` objects. This method is suitable for scenarios requiring multiple queries with varying parameters. Results can be customized with `record_class`.

```python
rows = await con.fetchmany('''
        INSERT INTO mytab (a, b) VALUES ($1, $2) RETURNING a;
    ''', [('x', 1), ('y', 2), ('z', 3)])
rows
[<Record row=('x',)>, <Record row=('y',)>, <Record row=('z',)>]
```

--------------------------------

### Copy Data From Table (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies data from a table to a file in CSV format using asyncpg. Requires the 'asyncpg' and 'asyncio' libraries. Takes table name, columns, output file path, and format as input. Returns the status string of the COPY command.

```python
import asyncpg
import asyncio
async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_from_table(
        'mytable', columns=('foo', 'bar'),
        output='file.csv', format='csv')
    print(result)

asyncio.run(run())
```

--------------------------------

### Asyncpg Logged Query Structure

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Defines a named tuple structure for logging executed database queries. It captures details such as the query itself, its arguments, timeout, execution time, any exceptions raised, and connection information.

```python
LoggedQuery = collections.namedtuple(
    'LoggedQuery',
    ['query', 'args', 'timeout', 'elapsed', 'exception', 'conn_addr',
     'conn_params'])
LoggedQuery.__doc__ = 'Log record of an executed query.'

```

--------------------------------

### Acquire Database Connection from Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Acquires a database connection from the pool, which can be used within an async with block or managed manually with release. Supports an optional timeout for acquiring the connection.

```python
def acquire(self, *, timeout=None):
        """Acquire a database connection from the pool.

        :param float timeout: A timeout for acquiring a Connection.
        :return: An instance of :class:`~asyncpg.connection.Connection`.

        Can be used in an ``await`` expression or with an ``async with`` block.

        .. code-block:: python

            async with pool.acquire() as con:
                await con.execute(...)

        Or:

        .. code-block:: python

            con = await pool.acquire()
            try:
                await con.execute(...)
            finally:
                await pool.release(con)
        """
        return PoolAcquireContext(self, timeout)
```

--------------------------------

### Type Codec Management

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

These methods allow for the registration, resetting, and aliasing of type codecs for scalar data types within the PostgreSQL database.

```APIDOC
## POST /connection/type_codec

### Description
Registers a custom codec for a given type name and schema. This method is used to associate Python encoding and decoding functions with a specific PostgreSQL data type.

### Method
POST

### Endpoint
/connection/type_codec

### Parameters
#### Query Parameters
- **typename** (string) - Required - Name of the data type the codec is for.
- **schema** (string) - Optional - Schema name of the data type the codec is for (defaults to 'public').
- **encoder** (function) - Required - Python function to encode Python objects to PostgreSQL bytes.
- **decoder** (function) - Required - Python function to decode PostgreSQL bytes to Python objects.
- **format** (string) - Optional - The format of the data ('text' or 'binary').

### Request Example
```json
{
  "typename": "my_custom_type",
  "schema": "myschema",
  "encoder": "encode_my_type",
  "decoder": "decode_my_type",
  "format": "text"
}
```

### Response
#### Success Response (200)
- **message** (string) - Indicates successful registration of the type codec.

#### Response Example
```json
{
  "message": "Type codec registered successfully."
}
```

## POST /connection/reset_type_codec

### Description
Resets the codec for a specified type name to its default implementation. This is useful if custom codecs are no longer needed or if there are issues with the current codec.

### Method
POST

### Endpoint
/connection/reset_type_codec

### Parameters
#### Query Parameters
- **typename** (string) - Required - Name of the data type the codec is for.
- **schema** (string) - Optional - Schema name of the data type the codec is for (defaults to 'public').

### Request Example
```json
{
  "typename": "my_custom_type",
  "schema": "myschema"
}
```

### Response
#### Success Response (200)
- **message** (string) - Indicates successful reset of the type codec.

#### Response Example
```json
{
  "message": "Type codec reset successfully."
}
```

## POST /connection/set_builtin_type_codec

### Description
Sets a builtin codec for a specified scalar data type. This can be used to register a builtin codec for an extension type or to declare that a type is wire-compatible with a builtin data type.

### Method
POST

### Endpoint
/connection/set_builtin_type_codec

### Parameters
#### Query Parameters
- **typename** (string) - Required - Name of the data type the codec is for.
- **schema** (string) - Optional - Schema name of the data type the codec is for (defaults to 'public').
- **codec_name** (string) - Required - The name of the builtin codec to use (e.g., 'int', 'pg_contrib.hstore').
- **format** (string) - Optional - The format to declare support for ('text' or 'binary'). If None, all supported formats are declared.

### Request Example
```json
{
  "typename": "hstore",
  "schema": "public",
  "codec_name": "pg_contrib.hstore",
  "format": "text"
}
```

### Response
#### Success Response (200)
- **message** (string) - Indicates successful setting of the builtin type codec.

#### Response Example
```json
{
  "message": "Builtin type codec set successfully."
}
```
```

--------------------------------

### Asynchronous Copy Out Operation in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Initiates an asynchronous COPY OUT operation to a specified output. Handles file path conversion and potential type errors.

```python
async def _copy_out(self, copy_stmt, output, timeout):
        try:
            path = os.fspath(output)
        except TypeError:

```

--------------------------------

### fetchrow

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a query and returns only the first row as a Record object. Returns None if no rows are found.

```APIDOC
## GET /fetchrow

### Description
Executes the statement and returns the first row.

### Method
GET

### Endpoint
/fetchrow

### Parameters
#### Query Parameters
- **query** (str) - Required - Query text
- **args** (tuple) - Required - Query arguments
- **timeout** (float) - Optional - Optional timeout value in seconds.

### Response
#### Success Response (200)
- **row** (Record) - The first row as a :class:`Record` instance.

#### Response Example
```json
{
  "column1": "value1",
  "column2": 123
}
```
```

--------------------------------

### Transaction Management API

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for managing database transactions, including setting isolation levels, read-only status, and deferrable status.

```APIDOC
## Connection Transaction Methods

### Description
Provides methods to control and inspect the current transaction context of a database connection.

### Methods

#### `transaction(...)`

##### Description
Begins a new transaction with specified isolation level, read-only, and deferrable options.

##### Parameters
- **isolation** (str) - Optional - Transaction isolation mode. Can be one of: `'serializable'`, `'repeatable_read'`, `'read_uncommitted'`, `'read_committed'`. Defaults to the server/session default (usually `'read_committed'`).
- **readonly** (bool) - Optional - Specifies whether the transaction is read-only.
- **deferrable** (bool) - Optional - Specifies whether the transaction is deferrable.

##### Returns
- `Transaction` - An object representing the transaction context.

#### `is_in_transaction()`

##### Description
Checks if the connection is currently within an active transaction.

##### Returns
- `bool` - `True` if inside a transaction, `False` otherwise.

### See Also
- `PostgreSQL documentation`_ for `SET TRANSACTION` statements: https://www.postgresql.org/docs/current/static/sql-set-transaction.html
```

--------------------------------

### Execute SQL Query with Arguments (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Executes an SQL command or multiple commands using asyncpg. Accepts query string, arguments, and an optional timeout. Can be used for various SQL operations. Returns a status string upon execution.

```python
async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.execute(
        'SELECT $1::text', 'world')
    print(result)
```

--------------------------------

### Python: PoolConnectionProxyMeta - Wrap Connection Methods

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This metaclass dynamically wraps methods of the base Connection class for use in a connection pool. It identifies coroutine functions and applies appropriate wrappers, ensuring that calls to proxied methods correctly target the underlying connection object or raise an error if the connection has been released.

```python
class PoolConnectionProxyMeta(type):

    def __new__(mcls, name, bases, dct, *, wrap=False):
        if wrap:
            for attrname in dir(connection.Connection):
                if attrname.startswith('_') or attrname in dct:
                    continue

                meth = getattr(connection.Connection, attrname)
                if not inspect.isfunction(meth):
                    continue

                iscoroutine = inspect.iscoroutinefunction(meth)
                wrapper = mcls._wrap_connection_method(attrname, iscoroutine)
                wrapper = functools.update_wrapper(wrapper, meth)
                dct[attrname] = wrapper

            if '__doc__' not in dct:
                dct['__doc__'] = connection.Connection.__doc__

        return super().__new__(mcls, name, bases, dct)

    @staticmethod
    def _wrap_connection_method(meth_name, iscoroutine):
        def call_con_method(self, *args, **kwargs):
            # This method will be owned by PoolConnectionProxy class.
            if self._con is None:
                raise exceptions.InterfaceError(
                    'cannot call Connection.{}(): '
                    'connection has been released back to the pool'.format(
                        meth_name))

            meth = getattr(self._con.__class__, meth_name)
            return meth(self._con, *args, **kwargs)

        if iscoroutine:
            compat.markcoroutinefunction(call_con_method)

        return call_con_method
```

--------------------------------

### Create Cursor Factory in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This function acts as a factory for creating cursor iterators for a given SQL query. It accepts query arguments, prefetch count, timeout, and an optional record class for customizing how rows are represented. It returns a cursor factory object.

```python
def cursor(
        self,
        query,
        *args,
        prefetch=None,
        timeout=None,
        record_class=None
    ):
        """Return a *cursor factory* for the specified query.

        :param args:
            Query arguments.
        :param int prefetch:
            The number of rows the *cursor iterator*
            will prefetch (defaults to ``50``.)
        :param float timeout:
            Optional timeout in seconds.
        """
        # The actual implementation would go here, likely returning a factory object
```

--------------------------------

### asyncpg.types Module Header

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

This snippet contains the header comments for the asyncpg.types module, including copyright information and licensing details. It serves as the introductory part of the module's source file.

```python
# Copyright (C) 2016-present the asyncpg authors and contributors
# <see AUTHORS file>
#
# This module is part of asyncpg and is released under

```

--------------------------------

### Create Transaction Object - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Initializes and returns a Transaction object, which can be used to manage database transactions. It accepts optional parameters for isolation level, readonly status, and deferrable status, corresponding to PostgreSQL transaction control.

```python
async with connection.transaction():
    # perform database operations here

async with connection.transaction(isolation='SERIALIZABLE', readonly=True):
    # perform read-only operations
```

--------------------------------

### Execute SQL Command with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Executes an SQL command using a connection from the asyncpg pool. This method behaves identically to Connection.execute(). Supports query arguments and an optional timeout.

```python
await pool.execute(query, *args, timeout=timeout)
```

--------------------------------

### fetchval

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a query and returns a single value from the first row. It allows specifying which column's value to retrieve.

```APIDOC
## GET /fetchval

### Description
Executes the statement and returns a value in the first row.

### Method
GET

### Endpoint
/fetchval

### Parameters
#### Query Parameters
- **args** (tuple) - Required - Query arguments.
- **column** (int) - Optional - Numeric index within the record of the value to return (defaults to 0).
- **timeout** (float) - Optional - Optional timeout value in seconds. If not specified, defaults to the value of ``command_timeout`` argument to the ``Connection`` instance constructor.

### Response
#### Success Response (200)
- **value** (any) - The value of the specified column of the first record.

#### Response Example
```json
"some_value"
```
```

--------------------------------

### Release Asyncpg Connection Holder

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Marks a connection holder as free, making the connection available for reuse by the pool. This is a core part of the connection management lifecycle.

```python
    def _release(self):
        """Release this connection holder."""
        if self._in_use is None:
```

--------------------------------

### BaseCursor Bind Operation (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Binds arguments to a prepared statement without immediate execution. It ensures a unique portal name is generated and checks for existing open portals.

```Python
    async def _bind(self, timeout):
        self._check_ready()

        if self._portal_name:
            raise exceptions.InterfaceError(
                'cursor already has an open portal')

        con = self._connection
        protocol = con._protocol

        self._portal_name = con._get_unique_id('portal')
        buffer = await protocol.bind(self._state, self._args,
                                     self._portal_name,
                                     timeout)
        return buffer
```

--------------------------------

### Connection Abort and Cleanup (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _abort method transitions the connection to an aborted state by invalidating its protocol handler. The _cleanup method handles the finalization of connection resources, notifying pools, marking statements as closed, clearing listeners, and cancelling any pending tasks associated with the connection.

```python
def _abort(self):
        # Put the connection into the aborted state.
        self._aborted = True
        self._protocol.abort()
        self._protocol = None

def _cleanup(self):
        self._call_termination_listeners()
        # Free the resources associated with this connection.
        # This must be called when a connection is terminated.

        if self._proxy is not None:
            # Connection is a member of a pool, so let the pool
            # know that this connection is dead.
            self._proxy._holder._release_on_close()

        self._mark_stmts_as_closed()
        self._listeners.clear()
        self._log_listeners.clear()
        self._query_loggers.clear()
        self._clean_tasks()
```

--------------------------------

### Release Database Connection (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Return a database connection to the asyncpg pool. This method accepts a connection object and an optional timeout for the release operation. The default timeout aligns with the `Pool.acquire()` method's timeout. The `timeout` parameter was added in version 0.14.0.

```python
asyncpg.Pool._async_release(_connection_, *_ , timeout=None)
```

--------------------------------

### copy_to_table

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies data from a source to a specified table. The source can be a file path, a file-like object, an asynchronous iterable yielding bytes, or an object supporting the buffer protocol.

```APIDOC
## POST /copy_to_table

### Description
Copies data from a source to a specified table. The source can be a file path, a file-like object, an asynchronous iterable yielding bytes, or an object supporting the buffer protocol. This method is essential for bulk data insertion into PostgreSQL tables.

### Method
POST

### Endpoint
/copy_to_table

### Parameters
#### Path Parameters
None

#### Query Parameters
* **table_name** (str) - Required - The name of the table to copy data into.
* **source** (path-like object, file-like object, async iterable, buffer protocol object) - Required - The data source to copy from.
* **columns** (list) - Optional - A list of column names to copy data into.
* **schema_name** (str) - Optional - The schema name for the target table.
* **where** (str) - Optional - An SQL expression to filter rows during the copy operation (requires PostgreSQL 12+).
* **timeout** (float) - Optional - A timeout value in seconds for the operation.
* **format** (str) - Optional - The format of the source data (e.g., 'csv', 'binary').
* **oids** (bool) - Optional - Include OIDs in the copy operation.
* **freeze** (bool) - Optional - Freeze the table during the copy operation.
* **delimiter** (str) - Optional - The delimiter to use for CSV format.
* **null** (str) - Optional - The string to represent NULL values in the source data.
* **header** (bool) - Optional - Indicates if the source data has a header row in CSV format.
* **quote** (str) - Optional - The character used for quoting in CSV format.
* **escape** (str) - Optional - The character used for escaping in CSV format.
* **force_quote** (list) - Optional - A list of column names to force quoting.
* **force_not_null** (list) - Optional - A list of columns to force NOT NULL constraint.
* **force_null** (list) - Optional - A list of columns to force NULL values.
* **encoding** (str) - Optional - The encoding of the source data.

#### Request Body
(Not applicable for this method, parameters are passed directly)

### Request Example
```py
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_to_table(
        'mytable',
        source='datafile.tbl'
    )
    print(result)

asyncio.run(run())
```

### Response
#### Success Response (200)
* **status** (str) - The status string of the COPY command (e.g., 'COPY 140000').

#### Response Example
```json
{
  "status": "COPY 140000"
}
```
```

--------------------------------

### Detect Asyncpg Server Capabilities

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Detects PostgreSQL server capabilities based on the server version and connection settings. It identifies specific behaviors for different database systems like Amazon Redshift, CockroachDB, and CrateDB, falling back to standard PostgreSQL behavior if none are matched. Returns a ServerCapabilities named tuple.

```python
def _detect_server_capabilities(server_version, connection_settings):
    if hasattr(connection_settings, 'padb_revision'):
        # Amazon Redshift detected.
        advisory_locks = False
        notifications = False
        plpgsql = False
        sql_reset = True
        sql_close_all = False
        jit = False
        sql_copy_from_where = False
    elif hasattr(connection_settings, 'crdb_version'):
        # CockroachDB detected.
        advisory_locks = False
        notifications = False
        plpgsql = False
        sql_reset = False
        sql_close_all = False
        jit = False
        sql_copy_from_where = False
    elif hasattr(connection_settings, 'crate_version'):
        # CrateDB detected.
        advisory_locks = False
        notifications = False
        plpgsql = False
        sql_reset = False
        sql_close_all = False
        jit = False
        sql_copy_from_where = False
    else:
        # Standard PostgreSQL server assumed.
        advisory_locks = True
        notifications = True
        plpgsql = True
        sql_reset = True
        sql_close_all = True
        jit = server_version >= (11, 0)
        sql_copy_from_where = server_version.major >= 12

    return ServerCapabilities(
        advisory_locks=advisory_locks,
        notifications=notifications,
        plpgsql=plpgsql,
        sql_reset=sql_reset,
        sql_close_all=sql_close_all,
        sql_copy_from_where=sql_copy_from_where,
        jit=jit,
    )

```

--------------------------------

### Execute SQL Commands for Multiple Arguments with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Executes an SQL command for each sequence of arguments in a list using a connection from the asyncpg pool. This is useful for batch operations and mirrors Connection.executemany().

```python
await pool.executemany(command, args, timeout=timeout)
```

--------------------------------

### Introspect Database Types in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This function introspects database types using a provided query, optionally handling JIT settings. It executes introspection queries and returns the results. It also manages the state of the JIT setting if it was modified.

```python
async def _introspect_types(self, typeoids, timeout):
        if self._server_caps.jit:
            try:
                cfgrow, _ = await self.__execute(
                    """
                    SELECT
                        current_setting('jit') AS cur,
                        set_config('jit', 'off', false) AS new
                    """,
                    (),
                    0,
                    timeout,
                    ignore_custom_codec=True,
                )
                jit_state = cfgrow[0]['cur']
            except exceptions.UndefinedObjectError:
                jit_state = 'off'
        else:
            jit_state = 'off'

        result = await self.__execute(
            self._intro_query,
            (list(typeoids),),
            0,
            timeout,
            ignore_custom_codec=True,
        )

        if jit_state != 'off':
            await self.__execute(
                """
                SELECT
                    set_config('jit', $1, false)
                """,
                (jit_state,),
                0,
                timeout,
                ignore_custom_codec=True,
            )

        return result
```

--------------------------------

### Manually Iterate and Fetch Rows with asyncpg Cursor

Source: https://magicstack.github.io/asyncpg/current/api/index

Shows how to manually control a cursor to iterate and fetch rows. This method allows fetching specific numbers of rows or skipping rows. It requires explicit creation of a `Cursor` object and manual calls to `fetchrow()`, `fetch()`, and `forward()`. Operations must be within a transaction.

```python
async def iterate(con: Connection):
    async with con.transaction():
        # Postgres requires non-scrollable cursors to be created
        # and used in a transaction.

        # Create a Cursor object
        cur = await con.cursor('SELECT generate_series(0, 100)')

        # Move the cursor 10 rows forward
        await cur.forward(10)

        # Fetch one row and print it
        print(await cur.fetchrow())

        # Fetch a list of 5 rows and print it
        print(await cur.fetch(5))

```

--------------------------------

### Fetch Single Row from Query (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Runs a query and returns the first row as a Record object. This operation is managed by a pool connection and matches the behavior of Connection.fetchrow(). It takes a query, arguments, and optional timeout and record class.

```python
async def fetchrow(self, query, *args, timeout=None, record_class=None):
        """Run a query and return the first row.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.fetchrow() <asyncpg.connection.Connection.fetchrow>`.

        .. versionadded:: 0.10.0
        """
        async with self.acquire() as con:
            return await con.fetchrow(
                query,
                *args,
                timeout=timeout,
                record_class=record_class
            )
```

--------------------------------

### Connection Reset

Source: https://magicstack.github.io/asyncpg/current/api/index

Reset the state of the current database connection.

```APIDOC
## POST /connection/reset

### Description
Resets the connection state to resemble that of a newly obtained connection. This includes rolling back any open transaction, closing cursors, removing LISTEN registrations, resetting session variables, and releasing advisory locks.

### Method
POST

### Endpoint
`/connection/reset`

### Parameters
#### Query Parameters
- **timeout** (float) - Optional - Timeout value in seconds for the reset operation.

### Request Example
None

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Connection state reset successfully."
}
```
```

--------------------------------

### Add Listener for Postgres Log Messages - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Registers a callback to receive asynchronous NoticeResponse messages from the PostgreSQL connection. These messages can include WARNING, NOTICE, DEBUG, INFO, or LOG. The callback receives the connection object and the log message.

```python
self.add_log_listener(my_log_handler)
self.add_log_listener(my_async_log_handler)
```

--------------------------------

### Copy Records to Table in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Copies a list of records to a specified table using binary COPY. Supports asynchronous iterables for records and optional WHERE clause filtering (requires PostgreSQL 12+).

```python
async def copy_records_to_table(self, table_name, *, records,
                                    columns=None, schema_name=None,
                                    timeout=None, where=None):
        """Copy a list of records to the specified table using binary COPY.

        :param str table_name:
            The name of the table to copy data to.

        :param records:
            An iterable returning row tuples to copy into the table.
            :term:`Asynchronous iterables <python:asynchronous iterable>`
            are also supported.

        :param list columns:
            An optional list of column names to copy.

        :param str schema_name:
            An optional schema name to qualify the table.

        :param str where:
            An optional SQL expression used to filter rows when copying.

            .. note::

                Usage of this parameter requires support for the
                ``COPY FROM ... WHERE`` syntax, introduced in
                PostgreSQL version 12.


        :param float timeout:
            Optional timeout value in seconds.

        :return: The status string of the COPY command.

        Example:

        .. code-block:: pycon

            >>> import asyncpg
            >>> import asyncio
            >>> async def run():
            ...     con = await asyncpg.connect(user='postgres')
            ...     result = await con.copy_records_to_table(
            ...         'mytable', records=[
            ...             (1, 'foo', 'bar'),
            ...             (2, 'ham', 'spam')])
            ...     print(result)
            ...
            >>> asyncio.run(run())
            'COPY 2'

        Asynchronous record iterables are also supported:

        .. code-block:: pycon

            >>> import asyncpg
            >>> import asyncio
            >>> async def run():
            ...     con = await asyncpg.connect(user='postgres')
            ...     async def record_gen(size):
            ...         for i in range(size):
            ...             yield (i,)
            ...     result = await con.copy_records_to_table(
            ...         'mytable', records=record_gen(100))
            ...     print(result)
            ...
            >>> asyncio.run(run())
            'COPY 100'

        .. versionadded:: 0.11.0

        .. versionchanged:: 0.24.0
            The ``records`` argument may be an asynchronous iterable.

        .. versionadded:: 0.29.0
            Added the *where* parameter.
        """
        tabname = utils._quote_ident(table_name)
        if schema_name:
            tabname = utils._quote_ident(schema_name) + '.' + tabname

        if columns:
            col_list = ', '.join(utils._quote_ident(c) for c in columns)
            cols = '({})'.format(col_list)
        else:
            col_list = '*'
            cols = ''

        intro_query = 'SELECT {cols} FROM {tab} LIMIT 1'.format(
            tab=tabname, cols=col_list)

        intro_ps = await self._prepare(intro_query, use_cache=True)

        cond = self._format_copy_where(where)
        opts = '(FORMAT binary)'

        copy_stmt = 'COPY {tab}{cols} FROM STDIN {opts} {cond}'.format(
            tab=tabname, cols=cols, opts=opts, cond=cond)

        return await self._protocol.copy_in(
            copy_stmt, None, None, records, intro_ps._state, timeout)

```

--------------------------------

### COPY RECORDS TO TABLE

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies a list of records to a specified table using binary COPY. Supports asynchronous iterables for records.

```APIDOC
## POST /copy_records_to_table

### Description
Copies a list of records (rows) to a specified table using the binary COPY protocol. This method is efficient for inserting multiple rows at once and supports asynchronous iterables for the `records` parameter.

### Method
POST

### Endpoint
/copy_records_to_table

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **table_name** (str) - Required - The name of the table to copy data to.
- **records** - Required - An iterable returning row tuples to copy into the table. Asynchronous iterables are also supported.
- **columns** (list) - Optional - A list of column names to copy.
- **schema_name** (str) - Optional - An optional schema name to qualify the table.
- **where** (str) - Optional - An optional SQL expression used to filter rows when copying. Requires PostgreSQL version 12 or higher.
- **timeout** (float) - Optional - Timeout value in seconds.

### Request Example
```json
{
  "table_name": "mytable",
  "records": [
    [1, "foo", "bar"],
    [2, "ham", "spam"]
  ]
}
```

### Response
#### Success Response (200)
- **status** (str) - The status string of the COPY command.

#### Response Example
```json
{
  "status": "COPY 2"
}
```
```

--------------------------------

### Execute Many SQL Commands with Asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This method is designed to execute a single SQL command multiple times with different sets of arguments using a connection from the asyncpg pool. It is intended to be used for bulk operations, but the specific implementation details for handling 'many' arguments are not fully provided in this snippet.

```python
    async def executemany(self, command: str, args, *, timeout: float=None):
```

--------------------------------

### Configure Interval Type Codec with Tuple Format in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This Python code demonstrates how to set a custom codec for the 'interval' PostgreSQL type using the 'tuple' format. It defines encoder and decoder functions to convert between Python's `relativedelta` objects and a tuple representation. This allows for custom handling of interval data when interacting with the database.

```pycon
>>> import asyncpg
>>> import asyncio
>>> import datetime
>>> from dateutil.relativedelta import relativedelta
>>> async def run():
...     con = await asyncpg.connect(user='postgres')
...     def encoder(delta):
...         ndelta = delta.normalized()
...         return (ndelta.years * 12 + ndelta.months,
...                 ndelta.days,
...                 ((ndelta.hours * 3600 +
...                    ndelta.minutes * 60 +
...                    ndelta.seconds) * 1000000 +
...                  ndelta.microseconds))
...     def decoder(tup):
...         return relativedelta(months=tup[0], days=tup[1],
...                              microseconds=tup[2])
...     await con.set_type_codec(
...         'interval', schema='pg_catalog', encoder=encoder,
...         decoder=decoder, format='tuple')
...     result = await con.fetchval(
...         "SELECT '2 years 3 mons 1 day'::interval")
...     print(result)
...     print(datetime.datetime(2002, 1, 1) + result)
... 
>>> asyncio.run(run())
relativedelta(years=+2, months=+3, days=+1)
2004-04-02 00:00:00
```

--------------------------------

### Copy Records to Table with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies a list of records to a specified table using binary COPY, via a connection from the asyncpg pool. This method mirrors Connection.copy_records_to_table(). Supports specifying columns and a WHERE clause.

```python
await pool.copy_records_to_table(table_name, records, *args, columns=None, schema_name=None, timeout=timeout, where=None)
```

--------------------------------

### Database Type Representation (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Shows how the asyncpg.types.Type class represents database data types. It includes the type's OID, name, kind (e.g., scalar, array), and schema.

```python
from asyncpg.types import Type

# Example of a scalar type
int4_type = Type(oid=23, name='int4', kind='scalar', schema='pg_catalog')
print(f"Type Name: {int4_type.name}")
print(f"Type OID: {int4_type.oid}")
print(f"Type Kind: {int4_type.kind}")
print(f"Schema: {int4_type.schema}")

# Example of an array type
text_array_type = Type(oid=1009, name='text[]', kind='array', schema='pg_catalog')
print(f"Array Type Name: {text_array_type.name}")
print(f"Array Type Kind: {text_array_type.kind}")
```

--------------------------------

### Iterate Over Query Results Asynchronously with asyncpg Connection

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates asynchronous iteration over query results using the `con.cursor()` method within a transaction. The cursor prefetches records for efficiency. Requires a `Connection` object and operates within a transaction block.

```python
async def iterate(con: Connection):
    async with con.transaction():
        # Postgres requires non-scrollable cursors to be created
        # and used in a transaction.
        async for record in con.cursor('SELECT generate_series(0, 100)'):
            print(record)

```

--------------------------------

### Fetch Many Rows from Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared statement and returns a list of Record objects, intended for retrieving multiple rows. Requires query arguments and an optional timeout.

```Python
    @connresource.guarded
    async def fetchmany(self, args, *, timeout=None):
        """Execute the statement and return a list of :class:`Record` objects.

        :param args: Query arguments.
        :param float timeout: Optional timeout value in seconds.

        :return: A list of :class:`Record` instances.

        .. versionadded:: 0.30.0
        """
        return await self.__do_execute(
            lambda protocol: protocol.bind_execute_many(
                self._state,
                args,
                portal_name='',
                timeout=timeout,
                return_rows=True,
            )
        )
```

--------------------------------

### Fetch Single Value Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a query and returns a single value from the first row and specified column. Accepts query text, arguments, column index, and timeout. Returns None if no records are found.

```python
async def fetchval(self, query, *args, column=0, timeout=None):
        """Run a query and return a value in the first row.

        :param str query: Query text.
        :param args: Query arguments.
        :param int column: Numeric index within the record of the value to
                           return (defaults to 0).
        :param float timeout: Optional timeout value in seconds.
                            If not specified, defaults to the value of
                            ``command_timeout`` argument to the ``Connection``
                            instance constructor.

        :return: The value of the specified column of the first record, or
                 None if no records were returned by the query.
        """
        self._check_open()
        data = await self._execute(query, args, 1, timeout)
        if not data:
            return None
        return data[0][column]
```

--------------------------------

### Import Data to Table with asyncpg copy_to_table

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The copy_to_table method imports data from a source into a specified table. The source can be a path-like object, file-like object, asynchronous iterable, or an object supporting the buffer protocol. It allows specifying columns, schema, and filtering with a WHERE clause (PostgreSQL 12+).

```python
import asyncpg
import asyncio

async def run():
    con = await asyncpg.connect(user='postgres')
    result = await con.copy_to_table(
        'mytable', source='datafile.tbl')
    print(result)

asyncio.run(run())
```

--------------------------------

### Internal Query Execution Logic (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Handles the core logic for executing a statement, including fetching it from cache or preparing it, managing timeouts, and implementing retry mechanisms for specific database errors like outdated schema or invalid statements.

```python
async def _do_execute(
        self,
        query,
        executor,
        timeout,
        retry=True,
        *,
        ignore_custom_codec=False,
        record_class=None
    ):
        if timeout is None:
            stmt = await self._get_statement(
                query,
                None,
                record_class=record_class,
                ignore_custom_codec=ignore_custom_codec,
            )
        else:
            before = time.monotonic()
            stmt = await self._get_statement(
                query,
                timeout,
                record_class=record_class,
                ignore_custom_codec=ignore_custom_codec,
            )
            after = time.monotonic()
            timeout -= after - before
            before = after

        try:
            if timeout is None:
                result = await executor(stmt, None)
            else:
                try:
                    result = await executor(stmt, timeout)
                finally:
                    after = time.monotonic()
                    timeout -= after - before

        except exceptions.OutdatedSchemaCacheError:
            # This exception is raised when we detect a difference between
            # cached type's info and incoming tuple from the DB (when a type is
            # changed by the ALTER TYPE).
            # It is not possible to recover (the statement is already done at
            # the server's side), the only way is to drop our caches and
            # reraise the exception to the caller.
            await self.reload_schema_state()
            raise
        except exceptions.InvalidCachedStatementError:
            # PostgreSQL will raise an exception when it detects
            # that the result type of the query has changed from
            # when the statement was prepared.  This may happen,
            # for example, after an ALTER TABLE or SET search_path.
            #
            # When this happens, and there is no transaction running,
            # we can simply re-prepare the statement and try once
            # again.  We deliberately retry only once as this is
            # supposed to be a rare occurrence.
            #
            # If the transaction _is_ running, this error will put it
            # into an error state, and we have no choice but to
            # re-raise the exception.
            #
            # In either case we clear the statement cache for this
            # connection and all other connections of the pool this
            # connection belongs to (if any).
            #
            # See https://github.com/MagicStack/asyncpg/issues/72
            # and https://github.com/MagicStack/asyncpg/issues/76
            # for discussion.
            #
            self._drop_global_statement_cache()
            if self._protocol.is_in_transaction() or not retry:
                raise
            else:
                return await self._do_execute(
                    query, executor, timeout, retry=False)

        return result, stmt
```

--------------------------------

### Copy Data to Table with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies data from a source to a specified table using a connection from the asyncpg pool. This method behaves identically to Connection.copy_to_table(). Supports numerous options for data format and handling.

```python
await pool.copy_to_table(table_name, source, *args, columns=None, schema_name=None, timeout=timeout, ...)
```

--------------------------------

### Fetch Single Row Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Executes a query and returns the first row of the result set. Supports query arguments, timeout, and custom record classes. If no record_class is specified, the per-connection default is used.

```python
async def fetchrow(
        self,
        query,
        *args,
        timeout=None,
        record_class=None
    ):
        """Run a query and return the first row.

        :param str query:
            Query text
        :param args:
            Query arguments
        :param float timeout:
            Optional timeout value in seconds.
        :param type record_class:
            If specified, the class to use for the value returned by this
            method.  Must be a subclass of :class:`~asyncpg.Record`.
            If not specified, a per-connection *record_class* is used.

        :return:

```

--------------------------------

### ServerVersion Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents the version of a PostgreSQL server.

```APIDOC
## ServerVersion Class

### Description
Provides a structured representation of a PostgreSQL server's version information, breaking it down into major, minor, and micro components, along with release level and serial number.

### Attributes
- **major** (int) - The major version number (e.g., 14).
- **minor** (int) - The minor version number (e.g., 5).
- **micro** (int) - The micro version number (e.g., 0).
- **releaselevel** (str) - The release level of the version (e.g., 'beta', 'stable').
- **serial** (int) - The serial number for the release.

### Example
```python
# Assuming 'server_version' is an instance of asyncpg.types.ServerVersion
print(f"Server Version: {server_version.major}.{server_version.minor}.{server_version.micro} ({server_version.releaselevel})")
```
```

--------------------------------

### Format COPY WHERE Clause in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Formats the WHERE clause for COPY commands. Raises UnsupportedServerFeatureError if the 'where' parameter is used with PostgreSQL versions older than 12.

```python
def _format_copy_where(self, where):
        if where and not self._server_caps.sql_copy_from_where:
            raise exceptions.UnsupportedServerFeatureError(
                'the `where` parameter requires PostgreSQL 12 or later')

        if where:
            where_clause = 'WHERE ' + where
        else:
            where_clause = ''

        return where_clause

```

--------------------------------

### COPY FROM TABLE

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies data from a file or iterable to a table. Supports various options for formatting and filtering.

```APIDOC
## POST /copy_from_table

### Description
Copies data from a specified source to a table. This method is versatile, accepting file paths, file-like objects, or asynchronous iterables as the data source.

### Method
POST

### Endpoint
/copy_from_table

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **table_name** (str) - Required - The name of the table to copy data to.
- **columns** (list) - Optional - A list of column names to copy.
- **schema_name** (str) - Optional - An optional schema name to qualify the table.
- **timeout** (float) - Optional - Timeout value in seconds.
- **source** - Required - A path-like object, or a file-like object, or an asynchronous iterable that returns `bytes`, or an object supporting the buffer protocol.
- **where** (str) - Optional - An optional SQL expression used to filter rows when copying. Requires PostgreSQL version 12 or higher.

*Additional keyword arguments are `COPY` statement options. Refer to PostgreSQL's COPY statement documentation for details.*

### Request Example
```json
{
  "table_name": "mytable",
  "columns": ["foo", "bar"],
  "source": "file.csv"
}
```

### Response
#### Success Response (200)
- **status** (str) - The status string of the COPY command.

#### Response Example
```json
{
  "status": "COPY 140000"
}
```
```

--------------------------------

### Add Query Logger Callback - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Registers a callback function or coroutine to be executed whenever a query is executed on the connection. The callback receives a LoggedQuery object containing details about the query execution.

```python
self.add_query_logger(my_query_log_callback)
self.add_query_logger(my_async_query_log_callback)
```

--------------------------------

### _StatementCache Clear and Cleanup Methods (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The `clear` method removes all entries from the cache, canceling any pending cleanup callbacks and invoking the `on_remove` callback for each statement. `_maybe_cleanup` ensures the cache size does not exceed `_max_size` by removing the oldest entries.

```python
    def clear(self):
        # Store entries for later.
        entries = tuple(self._entries.values())

        # Clear the entries dict.
        self._entries.clear()

        # Make sure that we cancel all scheduled callbacks
        # and call on_remove callback for each entry.
        for entry in entries:
            self._clear_entry_callback(entry)
            self._on_remove(entry._statement)

    def _maybe_cleanup(self):
        # Delete cache entries until the size of the cache is `max_size`.
        while len(self._entries) > self._max_size:
            old_query, old_entry = self._entries.popitem(last=False)
            self._clear_entry_callback(old_entry)

            # Let the connection know that the statement was removed
            # from the cache.
            self._on_remove(old_entry._statement)
```

--------------------------------

### executemany

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a single statement multiple times with different sets of arguments. This is efficient for bulk operations.

```APIDOC
## POST /executemany

### Description
Execute the statement for each sequence of arguments in *args*.

### Method
POST

### Endpoint
/executemany

### Parameters
#### Request Body
- **args** (iterable) - Required - An iterable containing sequences of arguments.
- **timeout** (float) - Optional - Optional timeout value in seconds.

### Response
#### Success Response (200)
- **message** (str) - Indicates successful execution. Results are discarded.

#### Response Example
```json
{
  "message": "Execution complete"
}
```
```

--------------------------------

### Nested Transaction Management with Async With (Python)

Source: https://magicstack.github.io/asyncpg/current/api/index

Demonstrates nested transactions using async with, which creates savepoints. The inner transaction is rolled back upon exception, while the outer transaction's state is preserved. Requires an active connection.

```python
async with connection.transaction():
    await connection.execute('CREATE TABLE mytab (a int)')

    try:
        # Create a nested transaction:
        async with connection.transaction():
            await connection.execute('INSERT INTO mytab (a) VALUES (1), (2)')
            # This nested transaction will be automatically rolled back:
            raise Exception
    except:
        # Ignore exception
        pass

    # Because the nested transaction was rolled back, there
    # will be nothing in `mytab`.
    assert await connection.fetch('SELECT a FROM mytab') == []
```

--------------------------------

### Prepare and Execute Statement with Type Introspection in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This function prepares a SQL statement, introspects necessary data types, and re-prepares the statement if needed. It handles potential race conditions during schema reloads and manages statement caching. It returns the prepared statement object.

```python
statement = await self._protocol.prepare(
            stmt_name,
            query,
            timeout,
            record_class=record_class,
            ignore_custom_codec=ignore_custom_codec,
        )
        need_reprepare = False
        types_with_missing_codecs = statement._init_types()
        tries = 0
        while types_with_missing_codecs:
            settings = self._protocol.get_settings()

            # Introspect newly seen types and populate the
            # codec cache.
            types, intro_stmt = await self._introspect_types(
                types_with_missing_codecs, timeout)

            settings.register_data_types(types)

            # The introspection query has used an anonymous statement,
            # which has blown away the anonymous statement we've prepared
            # for the query, so we need to re-prepare it.
            need_reprepare = not intro_stmt.name and not statement.name
            types_with_missing_codecs = statement._init_types()
            tries += 1
            if tries > 5:
                # In the vast majority of cases there will be only
                # one iteration.  In rare cases, there might be a race
                # with reload_schema_state(), which would cause a
                # second try.  More than five is clearly a bug.
                raise exceptions.InternalClientError(
                    'could not resolve query result and/or argument types '
                    'in {} attempts'.format(tries)
                )

        # Now that types have been resolved, populate the codec pipeline
        # for the statement.
        statement._init_codecs()

        if (
            need_reprepare
            or (not statement.name and not self._stmt_cache_enabled)
        ):
            # Mark this anonymous prepared statement as "unprepared",
            # causing it to get re-Parsed in next bind_execute.
            # We always do this when stmt_cache_size is set to 0 assuming
            # people are running PgBouncer which is mishandling implicit
            # transactions.
            statement.mark_unprepared()

        if use_cache:
            self._stmt_cache.put(
                (query, record_class, ignore_custom_codec), statement)

        # If we've just created a new statement object, check if there
        # are any statements for GC.
        if self._stmts_to_close:
            await self._cleanup_stmts()

        return statement
```

--------------------------------

### Default Connection Reset Query (SQL)

Source: https://magicstack.github.io/asyncpg/current/api/index

This SQL snippet represents the default query executed by asyncpg when resetting a connection before returning it to the pool. It ensures a clean state by unlocking advisory locks, closing cursors, and unlistening from notifications.

```sql
SELECT pg_advisory_unlock_all();
CLOSE ALL;
UNLISTEN *;
RESET ALL;
```

--------------------------------

### Copy Query Results to File with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies the results of a query to a file or file-like object using a connection from the asyncpg pool. This method behaves identically to Connection.copy_from_query(). Supports various copy options.

```python
await pool.copy_from_query(query, output, *args, timeout=timeout, format=format, ...)
```

--------------------------------

### _StatementCache Entry Creation and Callback Cancellation (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Creates a new cache entry with an associated timeout callback. `_clear_entry_callback` cancels the scheduled cleanup callback for a given entry if it exists.

```python
    def _new_entry(self, query, statement):
        entry = _StatementCacheEntry(self, query, statement)
        self._set_entry_timeout(entry)
        return entry

    def _clear_entry_callback(self, entry):
        if entry._cleanup_cb is not None:
            entry._cleanup_cb.cancel()
```

--------------------------------

### Fetch Single Row from Query with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Runs a query and returns the first row as a 'Record' object using a connection from the asyncpg pool. This method mirrors Connection.fetchrow(). Supports query arguments, timeout, and custom record classes.

```python
await pool.fetchrow(query, *args, timeout=timeout, record_class=record_class)
```

--------------------------------

### Asyncpg Pool Acquire Context Manager (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Defines a context manager (`PoolAcquireContext`) for acquiring and releasing connections from an asyncpg pool. It ensures that a connection is properly released back to the pool upon exiting the `async with` block, even if errors occur.

```python
class PoolAcquireContext:

    __slots__ = ('timeout', 'connection', 'done', 'pool')

    def __init__(self, pool, timeout):
        self.pool = pool
        self.timeout = timeout
        self.connection = None
        self.done = False

    async def __aenter__(self):
        if self.connection is not None or self.done:
            raise exceptions.InterfaceError('a connection is already acquired')
        self.connection = await self.pool._acquire(self.timeout)
        return self.connection

    async def __aexit__(self, *exc):
        self.done = True
        con = self.connection
        self.connection = None
        await self.pool.release(con)

    def __await__(self):
        self.done = True
```

--------------------------------

### Copy Table Contents to File with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Copies table contents to a file or file-like object using a connection from the asyncpg pool. This method is identical in behavior to Connection.copy_from_table(). Supports specifying columns and various copy options.

```python
await pool.copy_from_table(table_name, output, *args, columns=None, schema_name=None, timeout=timeout, ...)
```

--------------------------------

### Schema Management

Source: https://magicstack.github.io/asyncpg/current/api/index

Manually trigger a reload of the database schema cache.

```APIDOC
## POST /connection/schema/reload

### Description
Informs asyncpg that the database schema has changed and the internal schema cache should be reloaded. This is useful after performing schema modifications (e.g., `ALTER TYPE`, `ALTER TABLE`) to prevent potential `OutdatedSchemaCacheError` exceptions.

### Method
POST

### Endpoint
`/connection/schema/reload`

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **message** (string) - Confirmation message.

#### Response Example
```json
{
  "message": "Schema cache reload initiated."
}
```
```

--------------------------------

### BaseCursor Readiness Check (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Checks if the cursor is ready for operations. It ensures a prepared statement is associated, not closed, and executed within an active SQL transaction.

```Python
    def _check_ready(self):
        if self._state is None:
            raise exceptions.InterfaceError(
                'cursor: no associated prepared statement')

        if self._state.closed:
            raise exceptions.InterfaceError(
                'cursor: the prepared statement is closed')

        if not self._connection._top_xact:
            raise exceptions.NoActiveSQLTransactionError(
                'cursor cannot be created outside of a transaction')
```

--------------------------------

### Data Copy Operations

Source: https://magicstack.github.io/asyncpg/current/api/index

Methods for copying data to and from tables or query results, leveraging the pool's connections.

```APIDOC
## POST /copy_from_query

### Description
Copies the results of a query to a file or file-like object. The pool uses one of its connections for this operation and behaves identically to `Connection.copy_from_query()`.

### Method
POST

### Endpoint
/copy_from_query

### Parameters
#### Request Body
- **query** (str) - Required - The query whose results will be copied.
- **args** (list) - Optional - Arguments for the query.
- **output** (file-like object) - Required - The destination for the copied data.
- **timeout** (float) - Optional - Timeout for the operation.
- **format** (str) - Optional - The format for the copied data (e.g., 'TEXT', 'BINARY').
- **oids** (list) - Optional - OIDs for columns.
- **delimiter** (str) - Optional - Delimiter for text format.
- **null** (str) - Optional - String representation of NULL values.
- **header** (boolean) - Optional - Whether to include a header row.
- **quote** (str) - Optional - Quote character for text format.
- **escape** (str) - Optional - Escape character for text format.
- **force_quote** (list) - Optional - List of columns to force quoting.
- **encoding** (str) - Optional - Encoding of the data.

### Request Example
```python
with open('output.csv', 'w') as f:
    await pool.copy_from_query('SELECT * FROM users', output=f)
```

### Response
#### Success Response (200)
Indicates the data has been successfully copied.

## POST /copy_from_table

### Description
Copies table contents to a file or file-like object. The pool uses one of its connections for this operation and behaves identically to `Connection.copy_from_table()`.

### Method
POST

### Endpoint
/copy_from_table

### Parameters
#### Request Body
- **table_name** (str) - Required - The name of the table to copy from.
- **output** (file-like object) - Required - The destination for the copied data.
- **columns** (list) - Optional - List of column names to copy.
- **schema_name** (str) - Optional - The schema of the table.
- **timeout** (float) - Optional - Timeout for the operation.
- **format** (str) - Optional - The format for the copied data.
- **oids** (list) - Optional - OIDs for columns.
- **delimiter** (str) - Optional - Delimiter for text format.
- **null** (str) - Optional - String representation of NULL values.
- **header** (boolean) - Optional - Whether to include a header row.
- **quote** (str) - Optional - Quote character for text format.
- **escape** (str) - Optional - Escape character for text format.
- **force_quote** (list) - Optional - List of columns to force quoting.
- **encoding** (str) - Optional - Encoding of the data.

### Request Example
```python
with open('table_data.csv', 'w') as f:
    await pool.copy_from_table('users', output=f, columns=['id', 'name'])
```

### Response
#### Success Response (200)
Indicates the table data has been successfully copied.

## POST /copy_records_to_table

### Description
Copies a list of records to the specified table using binary COPY. The pool uses one of its connections for this operation and behaves identically to `Connection.copy_records_to_table()`.

### Method
POST

### Endpoint
/copy_records_to_table

### Parameters
#### Request Body
- **table_name** (str) - Required - The name of the table to copy to.
- **records** (list) - Required - A list of records to copy.
- **columns** (list) - Optional - List of column names.
- **schema_name** (str) - Optional - The schema of the table.
- **timeout** (float) - Optional - Timeout for the operation.
- **where** (str) - Optional - A WHERE clause for the COPY operation.

### Request Example
```python
records_to_insert = [('Alice', 30), ('Bob', 25)]
await pool.copy_records_to_table('users', records=records_to_insert, columns=['name', 'age'])
```

### Response
#### Success Response (200)
Indicates the records have been successfully copied to the table.

## POST /copy_to_table

### Description
Copies data to the specified table. The pool uses one of its connections for this operation and behaves identically to `Connection.copy_to_table()`.

### Method
POST

### Endpoint
/copy_to_table

### Parameters
#### Request Body
- **table_name** (str) - Required - The name of the table to copy to.
- **source** (file-like object or str) - Required - The source of the data to copy.
- **columns** (list) - Optional - List of column names.
- **schema_name** (str) - Optional - The schema of the table.
- **timeout** (float) - Optional - Timeout for the operation.
- **format** (str) - Optional - The format of the data (e.g., 'TEXT', 'BINARY').
- **oids** (list) - Optional - OIDs for columns.
- **freeze** (boolean) - Optional - Whether to freeze the data.
- **delimiter** (str) - Optional - Delimiter for text format.
- **null** (str) - Optional - String representation of NULL values.
- **header** (boolean) - Optional - Whether to include a header row.
- **quote** (str) - Optional - Quote character for text format.
- **escape** (str) - Optional - Escape character for text format.
- **force_quote** (list) - Optional - List of columns to force quoting.
- **force_not_null** (list) - Optional - List of columns to force NOT NULL.
- **force_null** (list) - Optional - List of columns to force NULL.
- **encoding** (str) - Optional - Encoding of the data.
- **where** (str) - Optional - A WHERE clause for the COPY operation.

### Request Example
```python
with open('data.csv', 'r') as f:
    await pool.copy_to_table('logs', source=f, format='CSV', delimiter=',')
```

### Response
#### Success Response (200)
Indicates the data has been successfully copied to the table.
```

--------------------------------

### Fetch Single Value from Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Executes a prepared statement and retrieves a specific value from the first row. Allows specifying the column index and timeout.

```Python
    @connresource.guarded
    async def fetchval(self, *args, column=0, timeout=None):
        """Execute the statement and return a value in the first row.

        :param args: Query arguments.
        :param int column: Numeric index within the record of the value to
                           return (defaults to 0).
        :param float timeout: Optional timeout value in seconds.
                            If not specified, defaults to the value of
                            ``command_timeout`` argument to the ``Connection``
                            instance constructor.

        :return: The value of the specified column of the first record.
        """
        data = await self.__bind_execute(args, 1, timeout)
        if not data:
            return None
        return data[0][column]
```

--------------------------------

### Iterate Over Prepared Statement Results Asynchronously with asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Illustrates iterating over query results generated from a prepared statement using `stmt.cursor()`. This approach is efficient for parameterized queries. The code prepares a statement, executes it with an argument, and then asynchronously iterates over the results within a transaction.

```python
async def iterate(con: Connection):
    # Create a prepared statement that will accept one argument
    stmt = await con.prepare('SELECT generate_series(0, $1)')

    async with con.transaction():
        # Postgres requires non-scrollable cursors to be created
        # and used in a transaction.

        # Execute the prepared statement passing `10` as the
        # argument -- that will generate a series or records
        # from 0..10.  Iterate over all of them and print every
        # record.
        async for record in stmt.cursor(10):
            print(record)

```

--------------------------------

### Internal Execution Logic (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Internal asynchronous method to execute a command via the protocol. Handles schema cache errors by reloading the state and re-raising the exception.

```Python
    async def __do_execute(self, executor):
        protocol = self._connection._protocol
        try:
            return await executor(protocol)
        except exceptions.OutdatedSchemaCacheError:
            await self._connection.reload_schema_state()
            # We can not find all manually created prepared statements, so just
            # drop known cached ones in the `self._connection`.
            # Other manually created prepared statements will fail and
            # invalidate themselves (unfortunately, clearing caches again).
            self._state.mark_closed()
            raise
```

--------------------------------

### Fetch Single Value from Query (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Executes a query and returns a single value from the first row and the specified column. This method uses a pool connection and is equivalent to Connection.fetchval(). It requires a query and optionally accepts arguments, column index, and timeout.

```python
async def fetchval(self, query, *args, column=0, timeout=None):
        """Run a query and return a value in the first row.

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        :meth:`Connection.fetchval() <asyncpg.connection.Connection.fetchval>`.

        .. versionadded:: 0.10.0
        """
        async with self.acquire() as con:
            return await con.fetchval(
                query, *args, column=column, timeout=timeout)
```

--------------------------------

### Pool Management

Source: https://magicstack.github.io/asyncpg/current/api/index

Methods for managing the lifecycle of the connection pool, including closing and expiring connections.

```APIDOC
## POST /close

### Description
Attempts to gracefully close all connections in the pool. This method waits until all pool connections are released before closing them and shutting down the pool. If any error occurs, the pool will terminate.

### Method
POST

### Endpoint
/close

### Parameters
None

### Request Example
```python
await pool.close()
```

### Response
#### Success Response (200)
Indicates the pool has been successfully closed.

## POST /expire_connections

### Description
Expires all currently open connections in the pool. The next `acquire()` call will result in a new connection being established.

### Method
POST

### Endpoint
/expire_connections

### Parameters
None

### Request Example
```python
await pool.expire_connections()
```

### Response
#### Success Response (200)
Indicates that all connections have been marked for expiration.
```

--------------------------------

### Connection Termination Listeners

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Methods for adding and removing callbacks that are executed when the connection is closed.

```APIDOC
## Connection Termination Listeners

### Description
Manages listeners that are called when the connection is closed. Callbacks can be regular functions or coroutine functions.

### Methods

#### `def add_termination_listener(self, callback)`

##### Description
Adds a listener to be called when the connection is closed.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None

#### `def remove_termination_listener(self, callback)`

##### Description
Removes a previously added connection termination listener.

##### Method
`def`

##### Endpoint
N/A (internal method)

##### Parameters

###### Path Parameters
None

###### Query Parameters
None

###### Request Body
None

##### Request Example
None

##### Response

###### Success Response (None)

###### Response Example
None
```

--------------------------------

### Python: PoolConnectionHolder - Manage Connection Lifecycle

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

PoolConnectionHolder is responsible for managing a single connection within the pool. It handles connection establishment, detects expired connections, and ensures the connection is ready for use. It also manages timeouts and callbacks related to connection inactivity.

```python
class PoolConnectionHolder:

    __slots__ = ('_con', '_pool', '_loop', '_proxy',
                 '_max_queries', '_setup',
                 '_max_inactive_time', '_in_use',
                 '_inactive_callback', '_timeout',
                 '_generation')

    def __init__(self, pool, *, max_queries, setup, max_inactive_time):

        self._pool = pool
        self._con = None
        self._proxy = None

        self._max_queries = max_queries
        self._max_inactive_time = max_inactive_time
        self._setup = setup
        self._inactive_callback = None
        self._in_use = None  # type: asyncio.Future
        self._timeout = None
        self._generation = None

    def is_connected(self):
        return self._con is not None and not self._con.is_closed()

    def is_idle(self):
        return not self._in_use

    async def connect(self):
        if self._con is not None:
            raise exceptions.InternalClientError(
                'PoolConnectionHolder.connect() called while another '
                'connection already exists')

        self._con = await self._pool._get_new_connection()
        self._generation = self._pool._generation
        self._maybe_cancel_inactive_callback()
        self._setup_inactive_callback()

    async def acquire(self) -> PoolConnectionProxy:
        if self._con is None or self._con.is_closed():
            self._con = None
            await self.connect()

        elif self._generation != self._pool._generation:
            # Connections have been expired, re-connect the holder.
            self._pool.loop.create_task(
                self._con.close(timeout=self._timeout))
            self._con = None
            await self.connect()

        self._maybe_cancel_inactive_callback()

        self._proxy = proxy = PoolConnectionProxy(self, self._con)

        if self._setup is not None:
            try:
                await self._setup(proxy)
            except (Exception, asyncio.CancelledError) as ex:
                # If a user-defined `setup` function fails, we don't
                # know if the connection is safe for re-use, hence

```

--------------------------------

### Rolling Back a Transaction in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

The `__rollback` method manages the rollback operation for a transaction. It validates the transaction state, nullifies the top transaction if necessary, constructs the correct SQL ('ROLLBACK TO' or 'ROLLBACK'), executes it, and sets the state to ROLLEDBACK on success or FAILED if an exception occurs.

```python
async def __rollback(self):
    self.__check_state('rollback')

    if self._connection._top_xact is self:
        self._connection._top_xact = None

    if self._nested:
        query = 'ROLLBACK TO {};'.format(self._id)
    else:
        query = 'ROLLBACK;'

    try:
        await self._connection.execute(query)
    except BaseException:
        self._state = TransactionState.FAILED
        raise
    else:
        self._state = TransactionState.ROLLEDBACK
```

--------------------------------

### Create Asyncpg Callback Wrapper

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Creates a wrapper for a callable, determining if it's an asynchronous coroutine function or a regular callable. Raises an InterfaceError if the input is not callable. This is used internally to handle different types of callbacks.

```python
class _Callback:
    is_async: bool

    @classmethod
    def from_callable(cls, cb: typing.Callable[..., None]) -> '_Callback':
        if inspect.iscoroutinefunction(cb):
            is_async = True
        elif callable(cb):
            is_async = False
        else:
            raise exceptions.InterfaceError(
                'expected a callable or an `async def` function,'
                'got {!r}'.format(cb)
            )

        return cls(cb, is_async)
```

--------------------------------

### Asyncpg Prepared Statement Garbage Collection Helper

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

A helper function designed to be used with weak references. When a weakly referenced object is garbage collected, this function is called to potentially clean up associated prepared statements by calling `_maybe_gc_stmt` on the object.

```python
def _weak_maybe_gc_stmt(weak_ref, stmt):
    self = weak_ref()
    if self is not None:
        self._maybe_gc_stmt(stmt)

```

--------------------------------

### Fetch a Single Row from a Query

Source: https://magicstack.github.io/asyncpg/current/api/index

Explains how to use the `fetchrow` method to execute a query and retrieve only the first resulting row as a `Record` object. If no rows are returned, it returns `None`. The `record_class` parameter allows for custom result types.

```python
await con.fetchrow("SELECT * FROM mytab WHERE a = $1", 200)
```

--------------------------------

### Reset Connection State (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The reset method restores the connection to a state similar to a newly established connection. It rolls back any open transactions, closes cursors, removes LISTEN registrations, resets session variables, and releases advisory locks. This ensures a clean slate for subsequent operations. It accepts an optional timeout parameter.

```python
async def reset(self, *, timeout=None):
        """Reset the connection state.

        Calling this will reset the connection session state to a state
        resembling that of a newly obtained connection.  Namely, an open
        transaction (if any) is rolled back, open cursors are closed,
        all `LISTEN <https://www.postgresql.org/docs/current/sql-listen.html>`_ 
        registrations are removed, all session configuration
        variables are reset to their default values, and all advisory locks
        are released.

        Note that the above describes the default query returned by
        :meth:`Connection.get_reset_query`.  If one overloads the method
        by subclassing ``Connection``, then this method will do whatever
        the overloaded method returns, except open transactions are always
        terminated and any callbacks registered by
        :meth:`Connection.add_listener` or :meth:`Connection.add_log_listener`
        are removed.

        :param float timeout:
            A timeout for resetting the connection.  If not specified, defaults
            to no timeout.
        """
        async with compat.timeout(timeout):
            await self._reset()
            reset_query = self.get_reset_query()
            if reset_query:
                await self.execute(reset_query)
```

--------------------------------

### _Callback Named Tuple Definition (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Defines a simple NamedTuple called _Callback, which is expected to hold a callable function `cb`.

```python
class _Callback(typing.NamedTuple):

    cb: typing.Callable[..., None]
```

--------------------------------

### Check Connection Validity for Prepared Statement (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Checks the validity of the connection for a prepared statement operation. It first checks if the statement is open and then calls the superclass method for further validation.

```Python
    def _check_conn_validity(self, meth_name):
        self._check_open(meth_name)
        super()._check_conn_validity(meth_name)
```

--------------------------------

### Connection.get_reset_query()

Source: https://magicstack.github.io/asyncpg/current/api/index

Retrieves the default query used to reset a connection. If the Connection class is subclassed, this method will return whatever the overloaded method returns, with the exception that open transactions are always terminated and any registered listeners are removed.

```APIDOC
## Connection.get_reset_query()

### Description
Retrieves the default query for resetting a connection. Overloaded methods will return their own results, but transactions will be closed and listeners removed.

### Method
*(Implicitly called, typically not directly invoked)*

### Endpoint
N/A

### Parameters
#### Query Parameters
- **timeout** (float) - Optional - A timeout for resetting the connection. Defaults to no timeout if not specified.
```

--------------------------------

### Release Connection Asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This code snippet defines the logic for releasing a connection back to the connection pool in asyncpg. It checks the connection status, resets the connection proxy, and places the connection back into the pool's queue. This ensures connections are properly managed and resources are freed.

```python
if self._proxy is not None:
    self._proxy._detach()
    self._proxy = None

# Put ourselves back to the pool queue.
self._pool._queue.put_nowait(self)
```

--------------------------------

### Release Database Connection to Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Releases a database connection back to the pool, making it available for reuse. An optional timeout can be specified for the release operation. If not provided, it defaults to the timeout used during acquisition.

```python
async def release(self, connection, *, timeout=None):
        """Release a database connection back to the pool.

        :param Connection connection:
            A :class:`~asyncpg.connection.Connection` object to release.
        :param float timeout:
            A timeout for releasing the connection.  If not specified, defaults
            to the timeout provided in the corresponding call to the
            :meth:`Pool.acquire() <asyncpg.pool.Pool.acquire>` method.

        .. versionchanged:: 0.14.0
            Added the *timeout* parameter.
        """
        if (type(connection) is not PoolConnectionProxy or
                connection._holder._pool is not self):
            raise exceptions.InterfaceError(

```

--------------------------------

### Asyncpg Atomic Operation Context Manager

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Provides a context manager for ensuring atomic operations. It prevents concurrent operations by raising an InterfaceError if another operation is already in progress. This is managed using an internal flag `_acquired`.

```python
class _Atomic:
    __slots__ = ('_acquired',)

    def __init__(self):
        self._acquired = 0

    def __enter__(self):
        if self._acquired:
            raise exceptions.InterfaceError(
                'cannot perform operation: another operation is in progress')
        self._acquired = 1

    def __exit__(self, t, e, tb):
        self._acquired = 0
```

--------------------------------

### Fetch Single Row as Record (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Fetches the first row of a query result as an asyncpg.Record instance. Returns None if no records are found. Allows specifying a custom record_class for the result type. This method is part of the connection object.

```python
await self._execute(
            query,
            args,
            1,
            timeout,
            record_class=record_class,
        )
```

--------------------------------

### CursorFactory Await Execution (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Handles the awaitable execution of a query using CursorFactory. It raises an InterfaceError if prefetch is specified, as prefetching is only for iterable cursors.

```Python
    @connresource.guarded
    def __await__(self):
        if self._prefetch is not None:
            raise exceptions.InterfaceError(
                'prefetch argument can only be specified for iterable cursor')
        cursor = Cursor(
            self._connection,
            self._query,
            self._state,
            self._args,
            self._record_class,
        )
        return cursor._init(self._timeout).__await__()
```

--------------------------------

### Connection Reset API

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Resets the connection session state to a clean state, similar to a new connection. This includes rolling back open transactions, closing cursors, removing LISTEN registrations, resetting session variables, and releasing advisory locks.

```APIDOC
## POST /connection/reset

### Description
Resets the connection session state to a clean state, similar to a new connection. This includes rolling back open transactions, closing cursors, removing LISTEN registrations, resetting session variables, and releasing advisory locks.

### Method
POST

### Endpoint
/connection/reset

### Parameters
#### Query Parameters
- **timeout** (float) - Optional - A timeout for resetting the connection. If not specified, defaults to no timeout.

### Request Body
This endpoint does not require a request body.

### Request Example
```json
{
  "message": "No request body needed for connection reset"
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates the success of the reset operation.
- **message** (string) - A confirmation message.

#### Response Example
```json
{
  "status": "success",
  "message": "Connection state has been successfully reset."
}
```
```

--------------------------------

### Fetch Single Value from Query with asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Runs a query and returns a single value from the first row using a connection from the asyncpg pool. This method is equivalent to Connection.fetchval(). Supports query arguments, column selection, and timeout.

```python
await pool.fetchval(query, *args, column=0, timeout=timeout)
```

--------------------------------

### Add Postgres Notification Listener

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Registers a callback function to receive Postgres notifications on a specified channel. The callback receives connection details, sender PID, channel name, and payload. Supports both regular callables and coroutine functions.

```python
async def add_listener(self, channel, callback):
        """Add a listener for Postgres notifications.

        :param str channel: Channel to listen on.

        :param callable callback:
            A callable or a coroutine function receiving the following
            arguments:
            **connection**: a Connection the callback is registered with;
            **pid**: PID of the Postgres server that sent the notification;
            **channel**: name of the channel the notification was sent to;
            **payload**: the payload.

        
```

--------------------------------

### Extract Asyncpg Stack Trace

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

A specialized function to extract stack traces, optimized for asyncio debug mode in asyncpg. It walks the call stack, filters out internal asyncpg frames, limits the depth, and formats the output as a string. This is a replacement for `traceback.extract_stack`.

```python
def _extract_stack(limit=10):
    """Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.
    """
    frame = sys._getframe().f_back
    try:
        stack = traceback.StackSummary.extract(
            traceback.walk_stack(frame), lookup_lines=False)
    finally:
        del frame

    apg_path = asyncpg.__path__[0]
    i = 0
    while i < len(stack) and stack[i][0].startswith(apg_path):
        i += 1
    stack = stack[i:i + limit]

    stack.reverse()
    return ''.join(traceback.format_list(stack))

```

--------------------------------

### Manage Connection State and Tasks (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _check_open method verifies if a connection is closed, raising an InterfaceError if it is. The _clean_tasks method cancels any remaining tasks associated with the connection, ensuring proper resource management.

```python
def _check_open(self):
        if self.is_closed():
            raise exceptions.InterfaceError('connection is closed')

def _clean_tasks(self):
        # Wrap-up any remaining tasks associated with this connection.
        if self._cancellations:
            for fut in self._cancellations:
                if not fut.done():
                    fut.cancel()
            self._cancellations.clear()
```

--------------------------------

### Add Listener for Channel Messages - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Adds a callback to listen for messages on a specific PostgreSQL channel. The callback can be a regular function or a coroutine. If the channel is not yet listened to, it will be subscribed to.

```python
await self.add_listener('my_channel', my_callback_function)
await self.add_listener('another_channel', my_async_callback_function)
```

--------------------------------

### BaseCursor Execute Operation (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Executes an existing portal with bound arguments. This method requires an open portal and updates the exhausted status based on the execution results.

```Python
    async def _exec(self, n, timeout):
        self._check_ready()

        if not self._portal_name:
            raise exceptions.InterfaceError(
                'cursor does not have an open portal')

        protocol = self._connection._protocol
        buffer, _, self._exhausted = await protocol.execute(
            self._state, self._portal_name, n, True, timeout)
        return buffer
```

--------------------------------

### Release Asyncpg Connection from Pool

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Handles the release of a connection back to the pool. It checks for connection limits, expiration, and performs necessary resets. If the reset operation fails, the connection is terminated to ensure stability.

```python
    async def release(self, timeout):
        if self._in_use is None:
            raise exceptions.InternalClientError(
                'PoolConnectionHolder.release() called on '
                'a free connection holder')

        if self._con.is_closed():
            # When closing, pool connections perform the necessary
            # cleanup, so we don't have to do anything else here.
            return

        self._timeout = None

        if self._con._protocol.queries_count >= self._max_queries:
            # The connection has reached its maximum utilization limit,
            # so close it.  Connection.close() will call _release().
            await self._con.close(timeout=timeout)
            return

        if self._generation != self._pool._generation:
            # The connection has expired because it belongs to
            # an older generation (Pool.expire_connections() has
            # been called.)
            await self._con.close(timeout=timeout)
            return

        try:
            budget = timeout

            if self._con._protocol._is_cancelling():
                # If the connection is in cancellation state,
                # wait for the cancellation
                started = time.monotonic()
                await compat.wait_for(
                    self._con._protocol._wait_for_cancellation(),
                    budget)
                if budget is not None:
                    budget -= time.monotonic() - started

            if self._pool._reset is not None:
                async with compat.timeout(budget):
                    await self._con._reset()
                    await self._pool._reset(self._con)
            else:
                await self._con.reset(timeout=budget)
        except (Exception, asyncio.CancelledError) as ex:
            # If the `reset` call failed, terminate the connection.
            # A new one will be created when `acquire` is called
            # again.
            try:
                # An exception in `reset` is most likely caused by
                # an IO error, so terminate the connection.
                self._con.terminate()
            finally:
                raise ex

        # Free this connection holder and invalidate the
        # connection proxy.
        self._release()

        # Rearm the connection inactivity timer.
        self._setup_inactive_callback()
```

--------------------------------

### Set Custom Type Codec (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Allows defining custom encoders and decoders for PostgreSQL data types within the Python application. This function specifies the data type, schema, and format ('text', 'binary', or 'tuple') for data exchange.

```Python
async def set_type_codec(self, typename, *, schema='public', encoder, decoder,
                             format='text'):
        """Set an encoder/decoder pair for the specified data type.

        :param typename:
            Name of the data type the codec is for.

        :param schema:
            Schema name of the data type the codec is for
            (defaults to ``'public'``)

        :param format:
            The type of the argument received by the *decoder* callback,
            and the type of the *encoder* callback return value.

            If *format* is ``'text'`` (the default), the exchange datum is a
            ``str`` instance containing valid text representation of the
            data type.

            If *format* is ``'binary'``, the exchange datum is a ``bytes``
            instance containing valid _binary_ representation of the
            data type.

            If *format* is ``'tuple'``, the exchange datum is a type-specific
            ``tuple`` of values.  The table below lists supported data
            types and their format for this mode.

            +-----------------+---------------------------------------------+
            |  Type           |                Tuple layout                 |
            +=================+=============================================+
            | ``interval``    | (``months``, ``days``, ``microseconds``)    |
            +-----------------+---------------------------------------------+
            | ``date``        | (``date ordinal relative to Jan 1 2000``,)  |
            |                 | ``-2^31`` for negative infinity timestamp   |
            |                 | ``2^31-1`` for positive infinity timestamp. |
            +-----------------+---------------------------------------------+
            | ``timestamp``   | (``microseconds relative to Jan 1 2000``,)  |
            |                 | ``-2^63`` for negative infinity timestamp   |
            |                 | ``2^63-1`` for positive infinity timestamp. |
            +-----------------+---------------------------------------------+
        """
```

--------------------------------

### Manage Prepared Statements Cache (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _mark_stmts_as_closed method iterates through cached and pending statements, marking them as closed to prevent further use. The _maybe_gc_stmt method handles the garbage collection of prepared statements that are no longer referenced and not in the cache, scheduling them for formal closure on the server.

```python
def _mark_stmts_as_closed(self):
        for stmt in self._stmt_cache.iter_statements():
            stmt.mark_closed()

        for stmt in self._stmts_to_close:
            stmt.mark_closed()

        self._stmt_cache.clear()
        self._stmts_to_close.clear()

def _maybe_gc_stmt(self, stmt):
        if (
            stmt.refs == 0
            and stmt.name
            and not self._stmt_cache.has(
                (stmt.query, stmt.record_class, stmt.ignore_custom_codec)
            )
        ):
            # If low-level `stmt` isn't referenced from any high-level
            # `PreparedStatement` object and is not in the `_stmt_cache`:
            #
            #  * mark it as closed, which will make it non-usable
            #    for any `PreparedStatement` or for methods like
            #    `Connection.fetch()`.
            #
            # * schedule it to be formally closed on the server.
            stmt.mark_closed()
            self._stmts_to_close.add(stmt)
```

--------------------------------

### Pool.expire_connections()

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Marks all currently open connections in the pool as expired. The next time a connection is acquired using `acquire()`, a new connection will be created to replace the expired one.

```APIDOC
## POST /_internal/pool/expire_connections

### Description
Marks all currently open connections in the pool for expiration. The next call to `acquire()` will create a new connection to replace the expired one.

### Method
POST

### Endpoint
/_internal/pool/expire_connections

### Parameters
None

### Request Example
```json
{
  "action": "expire_connections"
}
```

### Response
#### Success Response (200)
* **status** (string) - Indicates that connections have been marked for expiration.

#### Response Example
```json
{
  "status": "connections_expired"
}
```
```

--------------------------------

### Committing a Transaction in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

The `__commit` method handles the actual commit operation for a transaction. It checks the transaction state, releases savepoints if it's a nested transaction, executes the appropriate SQL command ('RELEASE SAVEPOINT' or 'COMMIT'), and updates the transaction state to COMMITTED on success or FAILED on exception.

```python
async def __commit(self):
    self.__check_state('commit')

    if self._connection._top_xact is self:
        self._connection._top_xact = None

    if self._nested:
        query = 'RELEASE SAVEPOINT {};'.format(self._id)
    else:
        query = 'COMMIT;'

    try:
        await self._connection.execute(query)
    except BaseException:
        self._state = TransactionState.FAILED
        raise
    else:
        self._state = TransactionState.COMMITTED
```

--------------------------------

### Release Connection to Pool (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Releases a connection back to the pool, ensuring it's properly handled even during cancellation. It utilizes asyncio.shield to guarantee the connection is returned. This method handles cases where the connection might already be released or its internal state is None.

```python
async def release(self, connection, timeout=None):
        """Release a connection back to the pool."""

        if connection._holder is not self._holders[connection._slot]:
            raise exceptions.InterfaceError(
                'Pool.release() received invalid connection: '
                '{connection!r} is not a member of this pool'.format(
                    connection=connection))

        if connection._con is None:
            # Already released, do nothing.
            return

        self._check_init()

        # Let the connection do its internal housekeeping when its released.
        connection._con._on_release()

        ch = connection._holder
        if timeout is None:
            timeout = ch._timeout

        # Use asyncio.shield() to guarantee that task cancellation
        # does not prevent the connection from being returned to the
        # pool properly.
        return await asyncio.shield(ch.release(timeout))
```

--------------------------------

### Cancel Server Operation (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _cancel method initiates a cancellation request to the PostgreSQL server for a specific backend process. It establishes a new connection to send the cancel request. It handles potential ConnectionResetError if the server resets the connection after the cancellation and also catches asyncio.CancelledError.

```python
async def _cancel(self, waiter):
        try:
            # Open new connection to the server
            await connect_utils._cancel(
                loop=self._loop, addr=self._addr, params=self._params,
                backend_pid=self._protocol.backend_pid,
                backend_secret=self._protocol.backend_secret)
        except ConnectionResetError as ex:
            # On some systems Postgres will reset the connection
            # after processing the cancellation command.
            if not waiter.done():
                waiter.set_exception(ex)
        except asyncio.CancelledError:
            # There are two scenarios in which the cancellation
```

--------------------------------

### Wait for Asyncpg Connection Release

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Provides a mechanism to wait until a connection is fully released back into the pool. This is useful in scenarios where subsequent operations depend on the connection being available.

```python
    async def wait_until_released(self):
        if self._in_use is None:
            return
        else:
            await self._in_use
```

--------------------------------

### Introspect Single Database Type by Name or OID in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

This function introspects a single database type, either by its OID (for built-in types) or by its name and schema. It handles mapping type names to OIDs for common PostgreSQL types and retrieves type information using specific SQL queries. It raises a ValueError if the type is unknown.

```python
async def _introspect_type(self, typename, schema):
        if (
            schema == 'pg_catalog'
            and typename.lower() in protocol.BUILTIN_TYPE_NAME_MAP
        ):
            typeoid = protocol.BUILTIN_TYPE_NAME_MAP[typename.lower()]
            rows = await self._execute(
                introspection.TYPE_BY_OID,
                [typeoid],
                limit=0,
                timeout=None,
                ignore_custom_codec=True,
            )
        else:
            rows = await self._execute(
                introspection.TYPE_BY_NAME,
                [typename, schema],
                limit=1,
                timeout=None,
                ignore_custom_codec=True,
            )

        if not rows:
            raise ValueError(
                'unknown type: {}.{}'.format(schema, typename))

        return rows[0]
```

--------------------------------

### CursorIterator Asynchronous Iteration (__anext__)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Implements asynchronous iteration for CursorIterator. It fetches statement data, binds and executes queries, and manages an internal buffer to yield results. Raises StopAsyncIteration when no more results are available.

```python
class CursorIterator(BaseCursor):

    __slots__ = ('_buffer', '_prefetch', '_timeout')

    def __init__(
        self,
        connection,
        query,
        state,
        args,
        record_class,
        prefetch,
        timeout
    ):
        super().__init__(connection, query, state, args, record_class)

        if prefetch <= 0:
            raise exceptions.InterfaceError(
                'prefetch argument must be greater than zero')

        self._buffer = collections.deque()
        self._prefetch = prefetch
        self._timeout = timeout

    @connresource.guarded
    def __aiter__(self):
        return self

    @connresource.guarded
    async def __anext__(self):
        if self._state is None:
            self._state = await self._connection._get_statement(
                self._query,
                self._timeout,
                named=True,
                record_class=self._record_class,
            )
            self._state.attach()

        if not self._portal_name and not self._exhausted:
            buffer = await self._bind_exec(self._prefetch, self._timeout)
            self._buffer.extend(buffer)

        if not self._buffer and not self._exhausted:
            buffer = await self._exec(self._prefetch, self._timeout)
            self._buffer.extend(buffer)

        if self._portal_name and self._exhausted:
            await self._close_portal(self._timeout)

        if self._buffer:
            return self._buffer.popleft()

        raise StopAsyncIteration
```

--------------------------------

### Fetch a Single Value from a Query

Source: https://magicstack.github.io/asyncpg/current/api/index

Details the `fetchval` method for executing a query and returning a specific value from the first row. It allows specifying the column index to retrieve. This is efficient for queries expected to return a single scalar value.

```python
await con.fetchval("SELECT a FROM mytab WHERE a = $1", 300)
```

--------------------------------

### Add Custom Type Codec in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Registers a custom codec for a PostgreSQL data type. It handles domain types, adds the codec to settings, and invalidates the statement cache due to codec changes. Dependencies include introspection utilities and exceptions.

```python
await self._introspect_type(typename, schema)
        settings.add_python_codec(
            oid, typename, schema, full_typeinfos, kind,
            encoder, decoder, format)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()
```

--------------------------------

### Reset Connection State

Source: https://magicstack.github.io/asyncpg/current/api/index

Resets the connection's session state to its initial configuration. This includes rolling back transactions, closing cursors, removing listeners, resetting session variables, and releasing locks.

```python
await con._async_reset(*, timeout: float | None = None)
```

--------------------------------

### Add Listener for Connection Termination - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Adds a callback that will be invoked when the connection to the PostgreSQL server is closed. The callback receives the connection object as an argument.

```python
self.add_termination_listener(my_conn_close_handler)
self.add_termination_listener(my_async_conn_close_handler)
```

--------------------------------

### Define PostgreSQL Server Version (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents the version of a PostgreSQL server using a NamedTuple. It includes major, minor, micro version numbers, release level, and serial number.

```python
[docs]
class ServerVersion(typing.NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int




ServerVersion.__doc__ = 'PostgreSQL server version tuple.'

```

--------------------------------

### Type Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents a PostgreSQL data type with its OID, name, kind, and schema.

```APIDOC
## Type Class

### Description
Represents a PostgreSQL data type, including its unique object identifier (OID), name, kind (e.g., scalar, array), and the schema it belongs to.

### Attributes
- **oid** (int) - The Object Identifier (OID) of the data type.
- **name** (str) - The name of the type, such as "int2" or "text".
- **kind** (str) - The classification of the type, which can be "scalar", "array", "composite", or "range".
- **schema** (str) - The name of the database schema where the type is defined.

### Example
```python
# Assuming 'type_info' is an instance of asyncpg.types.Type
print(f"OID: {type_info.oid}")
print(f"Name: {type_info.name}")
print(f"Kind: {type_info.kind}")
print(f"Schema: {type_info.schema}")
```
```

--------------------------------

### Transaction Representation in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

The `__repr__` method provides a developer-friendly string representation of a transaction object. It includes the transaction's state, isolation level, readonly status, deferrable status, and its memory address.

```python
def __repr__(self):
    attrs = []
    attrs.append('state:{}'.format(self._state.name.lower()))

    if self._isolation is not None:
        attrs.append(self._isolation)
    if self._readonly:
        attrs.append('readonly')
    if self._deferrable:
        attrs.append('deferrable')

    if self.__class__.__module__.startswith('asyncpg.'):
        mod = 'asyncpg'
    else:
        mod = self.__class__.__module__

    return '<{}.{} {} {:#x}>'.format(
        mod, self.__class__.__name__, ' '.join(attrs), id(self))
```

--------------------------------

### Cursor Fetch Single Row (fetchrow)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Fetches the next single row from the cursor results. It checks for readiness and exhaustion, executing the query if necessary. Returns a Record object or None if no more rows are available.

```python
    @connresource.guarded
    async def fetchrow(self, *, timeout=None):
        r"""Return the next row.

        :param float timeout: Optional timeout value in seconds.

        :return: A :class:`Record` instance.
        """
        self._check_ready()
        if self._exhausted:
            return None
        recs = await self._exec(1, timeout)
        if len(recs) < 1:
            self._exhausted = True
            return None
        return recs[0]
```

--------------------------------

### _StatementCache Timeout Management (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Manages the timeout for cache entries. `_set_entry_timeout` sets or resets the cleanup callback based on `_max_lifetime`. `_on_entry_expired` is the callback executed when an entry's lifetime expires, removing it from the cache if it's still present.

```python
    def _set_entry_timeout(self, entry):
        # Clear the existing timeout.
        self._clear_entry_callback(entry)

        # Set the new timeout if it's not 0.
        if self._max_lifetime:
            entry._cleanup_cb = self._loop.call_later(
                self._max_lifetime, self._on_entry_expired, entry)

    def _on_entry_expired(self, entry):
        # `call_later` callback, called when an entry stayed longer
        # than `self._max_lifetime`.
        if self._entries.get(entry._query) is entry:
            self._entries.pop(entry._query)
            self._on_remove(entry._statement)
```

--------------------------------

### Pool.release()

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Releases a connection back to the pool. This method should be called when a connection is no longer needed to make it available for subsequent acquire() calls. It handles internal housekeeping and ensures the connection is properly returned.

```APIDOC
## POST /_internal/pool/release

### Description
Releases a connection back to the pool, making it available for reuse. Handles internal bookkeeping and ensures the connection is properly returned to the pool.

### Method
POST

### Endpoint
/_internal/pool/release

### Parameters
#### Path Parameters
None

#### Query Parameters
* **timeout** (float | None) - Optional - The maximum time in seconds to wait for the connection to be released. If None, the pool's default timeout is used.

#### Request Body
* **connection** (Connection) - Required - The connection object to release.

### Request Example
```json
{
  "connection": "<connection_object>",
  "timeout": 5.0
}
```

### Response
#### Success Response (200)
* **status** (string) - Indicates the release was successful.

#### Response Example
```json
{
  "status": "released"
}
```
```

--------------------------------

### Cursor Fetch Rows (fetch)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Fetches the next 'n' rows from the cursor results. It checks if the cursor is ready, validates 'n', and handles exhausted results. Returns a list of Record objects or an empty list if exhausted.

```python
class Cursor(BaseCursor):
    """An open *portal* into the results of a query."""

    __slots__ = ()

    async def _init(self, timeout):
        if self._state is None:
            self._state = await self._connection._get_statement(
                self._query,
                timeout,
                named=True,
                record_class=self._record_class,
            )
            self._state.attach()
        self._check_ready()
        await self._bind(timeout)
        return self



    @connresource.guarded
    async def fetch(self, n, *, timeout=None):
        r"""Return the next *n* rows as a list of :class:`Record` objects.

        :param float timeout: Optional timeout value in seconds.

        :return: A list of :class:`Record` instances.
        """
        self._check_ready()
        if n <= 0:
            raise exceptions.InterfaceError('n must be greater than zero')
        if self._exhausted:
            return []
        recs = await self._exec(n, timeout)
        if len(recs) < n:
            self._exhausted = True
        return recs
```

--------------------------------

### _StatementCache Put Method (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Adds a new statement to the cache or updates an existing one. If the cache exceeds its maximum size after insertion, it triggers a cleanup process to remove the least recently used entries.

```python
    def put(self, query, statement):
        if not self._max_size:
            # The cache is disabled.
            return

        self._entries[query] = self._new_entry(query, statement)

        # Check if the cache is bigger than max_size and trim it
        # if necessary.
        self._maybe_cleanup()
```

--------------------------------

### Pool.terminate()

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Immediately terminates all connections in the pool without waiting for them to be released. This is a forceful shutdown and should be used when a graceful close is not possible or desired.

```APIDOC
## POST /_internal/pool/terminate

### Description
Terminates all connections in the pool immediately. This is a forceful shutdown and does not wait for connections to be released.

### Method
POST

### Endpoint
/_internal/pool/terminate

### Parameters
None

### Request Example
```json
{
  "action": "terminate_pool"
}
```

### Response
#### Success Response (200)
* **status** (string) - Indicates the pool has been terminated.

#### Response Example
```json
{
  "status": "terminated"
}
```
```

--------------------------------

### Connection.reset_type_codec()

Source: https://magicstack.github.io/asyncpg/current/api/index

Resets a specific type codec to its default implementation. This is useful for reverting custom codec configurations.

```APIDOC
## Connection.reset_type_codec()

### Description
Resets a specific type codec to its default implementation.

### Method
`async`

### Endpoint
N/A

### Parameters
#### Path Parameters
- **typename** (str) - Required - The name of the data type for which to reset the codec.
- **schema** (str) - Optional - The schema name of the data type. Defaults to 'public'.
```

--------------------------------

### Handle Cancelled Connections in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Handles exceptions, particularly asyncio.CancelledError, during connection operations. It ensures that waiter objects are properly set with exceptions or results, preventing unretrieved exception warnings when the connection or event loop is shutting down. This is crucial for robust asynchronous resource management.

```python
        except (Exception, asyncio.CancelledError) as ex:
            if not waiter.done():
                waiter.set_exception(ex)
        finally:
            self._cancellations.discard(
                asyncio.current_task(self._loop))
            if not waiter.done():
                waiter.set_result(None)
```

--------------------------------

### Asyncpg Transaction Creation

Source: https://magicstack.github.io/asyncpg/current/api/index

Creates a Transaction object in asyncpg, allowing control over transaction isolation, read-only status, and deferrability. Defaults to server-determined isolation if not specified.

```python
async with connection.transaction(isolation='serializable', readonly=True, deferrable=True):
    # Transactional operations here
```

--------------------------------

### Set Asyncpg Pool Connection Arguments

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method allows updating the connection arguments for an asyncpg pool, affecting all subsequent new connections. Existing connections are unaffected until they expire. It accepts a DSN string or keyword arguments for `asyncpg.connection.connect`.

```python
    def set_connect_args(self, dsn=None, **connect_kwargs):
        r"""Set the new connection arguments for this pool.

        The new connection arguments will be used for all subsequent
        new connection attempts.  Existing connections will remain until
        they expire. Use :meth:`Pool.expire_connections() 
        <asyncpg.pool.Pool.expire_connections>` to expedite the connection
        expiry.

        :param str dsn:
            Connection arguments specified using as a single string in
            the following format:
            ``postgres://user:pass@host:port/database?option=value``.

        :param \*\*connect_kwargs:
            Keyword arguments for the :func:`~asyncpg.connection.connect`
            function.

        .. versionadded:: 0.16.0
        """

        self._connect_args = [dsn]
        self._connect_kwargs = connect_kwargs
```

--------------------------------

### Close Prepared Statements (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _cleanup_stmts method is responsible for formally closing any prepared statements that have been marked for closure on the server. It iterates through the set of statements to close and sends the close_statement command via the protocol, ignoring any timeouts for this critical cleanup operation.

```python
async def _cleanup_stmts(self):
        # Called whenever we create a new prepared statement in
        # `Connection._get_statement()` and `_stmts_to_close` is
        # not empty.
        to_close = self._stmts_to_close
        self._stmts_to_close = set()
        for stmt in to_close:
            # It is imperative that statements are cleaned properly,
            # so we ignore the timeout.
            await self._protocol.close_statement(stmt, protocol.NO_TIMEOUT)
```

--------------------------------

### Set Connection Arguments (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Update the connection arguments for an asyncpg pool. These arguments will be used for all future connections. Existing connections remain unaffected until they expire. Use `Pool.expire_connections()` to force immediate expiry. Added in version 0.16.0.

```python
asyncpg.Pool.set_connect_args(dsn=None, **connect_kwargs)
```

--------------------------------

### Process Notification Listeners in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Processes incoming notifications from a specific channel, dispatching them to registered listeners. It handles both asynchronous and synchronous callback functions, ensuring that notifications are delivered correctly. If a channel has no listeners, the notification is ignored.

```python
    def _process_notification(self, pid, channel, payload):
        if channel not in self._listeners:
            return

        con_ref = self._unwrap()
        for cb in self._listeners[channel]:
            if cb.is_async:
                self._loop.create_task(cb.cb(con_ref, pid, channel, payload))
            else:
                self._loop.call_soon(cb.cb, con_ref, pid, channel, payload)
```

--------------------------------

### Public Commit Interface for asyncpg Transactions

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

The public `commit` method allows users to commit a transaction. It enforces that manual commits are not allowed within an `async with` block and then calls the internal `__commit` method.

```python
@connresource.guarded
async def commit(self):
    """Exit the transaction or savepoint block and commit changes."""
    if self._managed:
        raise apg_errors.InterfaceError(
            'cannot manually commit from within an `async with` block')
    await self.__commit()
```

--------------------------------

### Remove Query Logger Callback - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Removes a previously registered callback for query logging.

```python
self.remove_query_logger(my_query_log_callback)
self.remove_query_logger(my_async_query_log_callback)
```

--------------------------------

### Custom JSON Type Conversion with asyncpg in Python

Source: https://magicstack.github.io/asyncpg/current/usage

Illustrates how to configure asyncpg to automatically encode and decode JSON data using Python's `json` module. This involves setting a custom type codec for the 'json' type within the 'pg_catalog' schema. It requires 'asyncpg', 'json', and 'asyncio'.

```python
import asyncio
import asyncpg
import json


async def main():
    conn = await asyncpg.connect()

    try:
        await conn.set_type_codec(
            'json',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

        data = {'foo': 'bar', 'spam': 1}
        res = await conn.fetchval('SELECT $1::json', data)

    finally:
        await conn.close()

asyncio.run(main())

```

--------------------------------

### BaseCursor Representation (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Provides a string representation of the BaseCursor object, indicating its state, such as whether it is exhausted. It formats the representation based on the module.

```Python
    def __repr__(self):
        attrs = []
        if self._exhausted:
            attrs.append('exhausted')
        attrs.append('')  # to separate from id

        if self.__class__.__module__.startswith('asyncpg.'):
            mod = 'asyncpg'
        else:
            mod = self.__class__.__module__
```

--------------------------------

### Pool.close()

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Gracefully closes all connections in the pool. It waits for all connections to be released, then closes them and shuts down the pool. Any errors during this process will lead to immediate pool termination.

```APIDOC
## POST /_internal/pool/close

### Description
Attempts to gracefully close all connections in the pool. This involves waiting for all connections to be released, then closing each connection and shutting down the pool. If any exception occurs (including cancellation), the pool will be terminated immediately.

### Method
POST

### Endpoint
/_internal/pool/close

### Parameters
None

### Request Example
```json
{
  "action": "close_pool"
}
```

### Response
#### Success Response (200)
* **status** (string) - Indicates the pool closing process has started.

#### Response Example
```json
{
  "status": "closing"
}
```
```

--------------------------------

### Generate Unique IDs (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

The _get_unique_id method generates a unique identifier prefixed with a given string. This is typically used for internal naming conventions, such as for prepared statements or temporary objects.

```python
def _get_unique_id(self, prefix):
        global _uid
        _uid += 1
        return '__asyncpg_{}_{:x}__'.format(prefix, _uid)
```

--------------------------------

### Validate Asyncpg Record Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Validates that a provided `record_class` is a subclass of `asyncpg.Record` and does not redefine `__new__` or `__init__`. Raises an `InterfaceError` if the validation fails, ensuring that custom record classes adhere to asyncpg's requirements.

```python
def _check_record_class(record_class):
    if record_class is protocol.Record:
        pass
    elif (
        isinstance(record_class, type)
        and issubclass(record_class, protocol.Record)
    ):
        if (
            record_class.__new__ is not object.__new__
            or record_class.__init__ is not object.__init__
        ):
            raise exceptions.InterfaceError(
                'record_class must not redefine __new__ or __init__'
            )
    else:
        raise exceptions.InterfaceError(
            'record_class is expected to be a subclass of '
            'asyncpg.Record, got {!r}'.format(record_class)
        )

```

--------------------------------

### Set Builtin Type Codec in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Sets a builtin codec for a scalar PostgreSQL data type, used for extension types or aliasing user-defined types to wire-compatible builtins. It checks if the connection is open, introspects the type, and applies the codec settings. Raises InterfaceError for non-scalar types.

```python
self._check_open()
        typeinfo = await self._introspect_type(typename, schema)
        if not introspection.is_scalar_type(typeinfo):
            raise exceptions.InterfaceError(
                'cannot alias non-scalar type {}.{}'.format(
                    schema, typename))

        oid = typeinfo['oid']

        self._protocol.get_settings().set_builtin_type_codec(
            oid, typename, schema, 'scalar', codec_name, format)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()
```

--------------------------------

### Public Rollback Interface for asyncpg Transactions

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/transaction

The public `rollback` method provides an interface for users to roll back a transaction. It prevents manual rollbacks within `async with` blocks and delegates the operation to the internal `__rollback` method.

```python
@connresource.guarded
async def rollback(self):
    """Exit the transaction or savepoint block and rollback changes."""
    if self._managed:
        raise apg_errors.InterfaceError(
            'cannot manually rollback from within an `async with` block')
    await self.__rollback()
```

--------------------------------

### Terminate Asyncpg Connection

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Immediately terminates an asyncpg connection without graceful shutdown. This is typically used when a connection is found to be in an unusable state, such as after a failed reset operation, ensuring that a new connection is created upon the next acquisition.

```python
    def terminate(self):
        if self._con is not None:
            # Connection.terminate() will call _release_on_close() to
            # finish holder cleanup.
            self._con.terminate()
```

--------------------------------

### Expire Connections in asyncpg Pool

Source: https://magicstack.github.io/asyncpg/current/api/index

Forces all currently open connections in the asyncpg pool to be expired. The next 'acquire()' call will establish new connections, replacing the expired ones.

```python
await pool.expire_connections()
```

--------------------------------

### Attribute Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents an attribute of a database relation, including its name and data type.

```APIDOC
## Attribute Class

### Description
Represents a column or field within a PostgreSQL table or composite type. It holds the attribute's name and its associated data type.

### Attributes
- **name** (str) - The name of the attribute (e.g., column name).
- **type** (Type) - An instance of the `Type` class, describing the data type of the attribute.

### Example
```python
# Assuming 'attribute_info' is an instance of asyncpg.types.Attribute
print(f"Attribute Name: {attribute_info.name}")
print(f"Attribute Type: {attribute_info.type.name}")
```
```

--------------------------------

### Connection.set_type_codec()

Source: https://magicstack.github.io/asyncpg/current/api/index

Sets a custom encoder/decoder pair for a specified data type. This allows for custom data serialization and deserialization logic.

```APIDOC
## Connection.set_type_codec()

### Description
Sets a custom encoder/decoder pair for a specified data type, enabling custom data handling.

### Method
`async`

### Endpoint
N/A

### Parameters
#### Path Parameters
- **typename** (str) - Required - The name of the data type the codec is for.
- **schema** (str) - Optional - The schema name of the data type. Defaults to 'public'.
- **encoder** (callable) - Required - A callable that accepts a Python object and returns an encoded value.
- **decoder** (callable) - Required - A callable that accepts an encoded value and returns a decoded Python object.
- **format** (str) - Optional - The format for exchange ('text', 'binary', or 'tuple'). Defaults to 'text'.

### Request Example
```python
async def encoder(delta):
    ndelta = delta.normalized()
    return (
        ndelta.years * 12 + ndelta.months,
        ndelta.days,
        ((ndelta.hours * 3600 + ndelta.minutes * 60 + ndelta.seconds) * 1000000 + ndelta.microseconds)
    )

def decoder(tup):
    from dateutil.relativedelta import relativedelta
    return relativedelta(months=tup[0], days=tup[1], microseconds=tup[2])

await con.set_type_codec('interval', schema='pg_catalog', encoder=encoder, decoder=decoder, format='tuple')
```

### Response
#### Success Response (200)
This method does not return a value upon success.

#### Response Example
N/A
```

--------------------------------

### Set Built-in Type Codec in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Sets a built-in codec for a scalar data type, enabling the registration of codecs for extension types or declaring wire-compatibility with built-in types. Supports 'text' and 'binary' formats, defaulting to all supported formats if none is specified. Version 0.18.0 enhanced codec_name and added the format argument.

```python
_async _set_builtin_type_codec(_typename_ , _*_ , _schema ='public'_, _codec_name_ , _format =None_)[source]
```

--------------------------------

### Check Connection Status and Transaction State

Source: https://magicstack.github.io/asyncpg/current/api/index

Methods to determine if a database connection is closed or currently within a transaction. These are useful for controlling application flow based on the connection's state.

```python
con.is_closed()
con.is_in_transaction()
```

--------------------------------

### Reload Database Schema State in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Informs asyncpg to reload cached database schema information, preventing `OutdatedSchemaCacheError` after schema modifications. This is crucial for maintaining consistency between the application and the database. It clears both local and global caches for types and statements.

```python
self._drop_global_type_cache()
self._drop_global_statement_cache()
```

--------------------------------

### Remove Query Logger Callback

Source: https://magicstack.github.io/asyncpg/current/api/index

Removes a previously added query logger callback. The callback function must be the same one passed to `Connection.add_query_logger()`.

```python
con.remove_query_logger(callback)
```

--------------------------------

### Terminate Connection in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Terminates the asyncpg connection immediately without waiting for any pending data to be sent or received. This is a forceful disconnection that cleans up resources afterwards.

```python
if not self.is_closed():
            self._abort()
        self._cleanup()
```

--------------------------------

### Connection.set_builtin_type_codec()

Source: https://magicstack.github.io/asyncpg/current/api/index

Sets a built-in codec for a specified scalar data type. This can be used to register codecs for extension types without stable OIDs or to declare wire compatibility between types.

```APIDOC
## Connection.set_builtin_type_codec()

### Description
Sets a built-in codec for a specified scalar data type. Useful for extension types or declaring wire compatibility.

### Method
`async`

### Endpoint
N/A

### Parameters
#### Path Parameters
- **typename** (str) - Required - The name of the data type the codec is for.
- **schema** (str) - Optional - The schema name of the data type. Defaults to 'public'.
- **codec_name** (str) - Required - The name of the builtin codec (e.g., 'int', 'pg_contrib.hstore').
- **format** (str) - Optional - The format to support ('text', 'binary', or None for all supported formats). Defaults to None.
```

--------------------------------

### Terminate Asyncpg Pool Connections (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Terminates all connections currently held within the pool. This is a forceful action that ensures all connections are closed immediately. It's typically used as a fallback when graceful closure fails.

```python
def terminate(self):
        """Terminate all connections in the pool."""
        if self._closed:
            return
        self._check_init()
        for ch in self._holders:
            ch.terminate()
        self._closed = True
```

--------------------------------

### Prepared Statement Garbage Collection Hook (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

The __del__ method is called when the prepared statement object is about to be garbage collected. It detaches the statement state and potentially triggers garbage collection of the statement on the connection.

```Python
    def __del__(self):
        self._state.detach()
        self._connection._maybe_gc_stmt(self._state)
```

--------------------------------

### Range Class

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents an immutable PostgreSQL `range` type.

```APIDOC
## Range Class

### Description
An immutable representation of PostgreSQL's `range` data type. It allows for defining ranges with inclusive or exclusive bounds, and can represent empty ranges or infinite bounds.

### Initialization
```python
Range(lower: _RV | None = None, upper: _RV | None = None, *, lower_inc: bool = True, upper_inc: bool = False, empty: bool = False)
```

### Attributes
- **lower** (_RV | None) - The lower bound of the range. `None` if the range is empty or unbounded below.
- **lower_inc** (bool) - `True` if the lower bound is inclusive, `False` otherwise. Only relevant if `lower` is not `None`.
- **lower_inf** (bool) - `True` if the range is unbounded below (i.e., `lower` is `None` and the range is not empty).
- **upper** (_RV | None) - The upper bound of the range. `None` if the range is empty or unbounded above.
- **upper_inc** (bool) - `True` if the upper bound is inclusive, `False` otherwise. Only relevant if `upper` is not `None`.
- **upper_inf** (bool) - `True` if the range is unbounded above (i.e., `upper` is `None` and the range is not empty).
- **isempty** (bool) - `True` if the range is explicitly marked as empty, `False` otherwise.

### Methods
- **issubset(other: Self) -> bool**: Returns `True` if this range is a subset of another range.
- **issuperset(other: Self) -> bool**: Returns `True` if this range is a superset of another range.

### Example
```python
# Create a range from 1 to 10 (inclusive)
range1 = Range(lower=1, upper=10)

# Create a range from 5 (exclusive) to 15 (inclusive)
range2 = Range(lower=5, upper=15, lower_inc=False, upper_inc=True)

# Create an empty range
empty_range = Range(empty=True)

# Create an unbounded range above 100
unbounded_range = Range(lower=100, lower_inc=False)

print(range1.lower, range1.upper, range1.lower_inc, range1.upper_inc)
print(range2.lower, range2.upper, range2.lower_inc, range2.upper_inc)
print(empty_range.isempty)
print(unbounded_range.lower_inf)
```
```

--------------------------------

### Gracefully Close Connection in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Closes the asyncpg connection gracefully, attempting to send a close message and waiting for confirmation. It handles potential exceptions during closing by aborting the connection and cleaning up resources. An optional timeout can be provided.

```python
if not self.is_closed():
                await self._protocol.close(timeout)
        except (Exception, asyncio.CancelledError):
            # If we fail to close gracefully, abort the connection.
            self._abort()
            raise
        finally:
            self._cleanup()
```

--------------------------------

### Cursor Forward Rows (forward)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Skips over the next 'n' rows in the cursor results. It sends a 'MOVE FORWARD' command to the database and returns the number of rows actually skipped. Updates the cursor's exhausted status if fewer than 'n' rows were skipped.

```python
    @connresource.guarded
    async def forward(self, n, *, timeout=None) -> int:
        r"""Skip over the next *n* rows.

        :param float timeout: Optional timeout value in seconds.

        :return: A number of rows actually skipped over (<= *n*).
        """
        self._check_ready()
        if n <= 0:
            raise exceptions.InterfaceError('n must be greater than zero')

        protocol = self._connection._protocol
        status = await protocol.query('MOVE FORWARD {:d} {}'.format(
            n, self._portal_name), timeout)

        advanced = int(status.split()[1])
        if advanced < n:
            self._exhausted = True

        return advanced
```

--------------------------------

### Check for Active Listeners on Connection Release in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Checks if a connection has any active notification or log listeners before being released to the pool. If active listeners are found, it issues an InterfaceWarning to inform the user, helping to prevent potential resource leaks or unexpected behavior. This method is called internally during the connection release process.

```python
    def _check_listeners(self, listeners, listener_type):
        if listeners:
            count = len(listeners)

            w = exceptions.InterfaceWarning(
                '{conn!r} is being released to the pool but has {c} active '
                '{type} listener{s}'
                .format(
                    conn=self, c=count, type=listener_type,
                    s='s' if count > 1 else ''))

            warnings.warn(w)

    def _on_release(self, stacklevel=1):
        # Invalidate external references to the connection.
        self._pool_release_ctr += 1
        # Called when the connection is about to be released to the pool.
        # Let's check that the user has not left any listeners on it.
        self._check_listeners(
            list(itertools.chain.from_iterable(self._listeners.values())),
            'notification')
        self._check_listeners(
            self._log_listeners, 'log')
```

--------------------------------

### Check Prepared Statement Open Status (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/prepared_stmt

Helper method to check if a prepared statement is closed. Raises an InterfaceError if the method is called on a closed statement.

```Python
    def _check_open(self, meth_name):
        if self._state.closed:
            raise exceptions.InterfaceError(
                'cannot call PreparedStmt.{}(): ' 
                'the prepared statement is closed'.format(meth_name))
```

--------------------------------

### Gracefully Close Asyncpg Pool (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Attempts to gracefully close all connections in the pool. It waits for all connections to be released, closes them, and then shuts down the pool. Any error during this process leads to immediate pool termination. A 60-second warning callback is used to detect long-running close operations.

```python
async def close(self):
        """Attempt to gracefully close all connections in the pool.

        Wait until all pool connections are released, close them and
        shut down the pool.  If any error (including cancellation) occurs
        in ``close()`` the pool will terminate by calling
        :meth:`Pool.terminate() <pool.Pool.terminate>`.

        It is advisable to use :func:`python:asyncio.wait_for` to set
        a timeout.

        .. versionchanged:: 0.16.0
            ``close()`` now waits until all pool connections are released
            before closing them and the pool.  Errors raised in ``close()``
            will cause immediate pool termination.
        """
        if self._closed:
            return
        self._check_init()

        self._closing = True

        warning_callback = None
        try:
            warning_callback = self._loop.call_later(
                60, self._warn_on_long_close)

            release_coros = [
                ch.wait_until_released() for ch in self._holders]
            await asyncio.gather(*release_coros)

            close_coros = [
                ch.close() for ch in self._holders]
            await asyncio.gather(*close_coros)

        except (Exception, asyncio.CancelledError):
            self.terminate()
            raise

        finally:
            if warning_callback is not None:
                warning_callback.cancel()
            self._closed = True
            self._closing = False
```

--------------------------------

### Check Connection Status in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Determines if an asyncpg connection is closed. Returns True if the connection has been aborted or is no longer connected to the protocol, and False otherwise.

```python
return self._aborted or not self._protocol.is_connected()
```

--------------------------------

### Reloading Schema Cache in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Informs asyncpg to reload its cached database schema information. This is crucial after schema modifications to prevent `OutdatedSchemaCacheError` and ensure correct query processing.

```python
async def change_type(con):
    result = await con.fetch('SELECT id, info FROM tbl')
    await con.execute('ALTER TYPE custom DROP ATTRIBUTE y')
    await con.execute('ALTER TYPE custom ADD ATTRIBUTE y text')
    await con.reload_schema_state()
    for id_, info in result:
        new = (info['x'], str(info['y']))
        await con.execute(
            'UPDATE tbl SET info=$2 WHERE id=$1', id_, new)

async def run():
    con = await asyncpg.connect(user='postgres')
    async with con.transaction():
        await con.execute('LOCK TABLE tbl')
        await change_type(con)

asyncio.run(run())
```

--------------------------------

### Drop Local Statement Cache in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Clears the local statement cache for the current connection. This is typically called when a connection is about to be released or invalidated. Dropping the cache ensures that any prepared statements associated with this specific connection instance are removed, freeing up resources.

```python
    def _drop_local_statement_cache(self):
        self._stmt_cache.clear()
```

--------------------------------

### Asyncpg Connection Termination

Source: https://magicstack.github.io/asyncpg/current/api/index

Terminates an asyncpg connection immediately without waiting for any pending data to be processed. This is useful for forceful disconnection.

```python
await connection.terminate()
```

--------------------------------

### Release Asyncpg Connection on Close

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Performs the final cleanup when a connection is closed. It cancels any pending inactivity callbacks and releases the connection holder, ensuring all resources are properly freed.

```python
    def _release_on_close(self):
        self._maybe_cancel_inactive_callback()
        self._release()
        self._con = None
```

--------------------------------

### BaseCursor Close Portal (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

Closes an open portal associated with the cursor. It ensures a portal is open before attempting to close it and resets the portal name.

```Python
    async def _close_portal(self, timeout):
        self._check_ready()

        if not self._portal_name:
            raise exceptions.InterfaceError(
                'cursor does not have an open portal')

        protocol = self._connection._protocol
        await protocol.close_portal(self._portal_name, timeout)
        self._portal_name = None
```

--------------------------------

### Remove Listener for Postgres Log Messages - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Removes a previously added callback for PostgreSQL log messages.

```python
self.remove_log_listener(my_log_handler)
self.remove_log_listener(my_async_log_handler)
```

--------------------------------

### Set Custom Type Codec (Encoder/Decoder) in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Sets a custom encoder-decoder pair for a specified data type in a given schema. Supports 'text', 'binary', and 'tuple' formats, with specific tuple layouts defined for types like 'interval', 'date', and 'timestamp'. The encoder takes a Python object and returns an encoded value, while the decoder takes an encoded value and returns a Python object.

```python
_async _set_type_codec(_typename_ , _*_ , _schema ='public'_, _encoder_ , _decoder_ , _format ='text'_)[source]
```

```python
>>> import asyncpg
>>> import asyncio
>>> import datetime
>>> from dateutil.relativedelta import relativedelta
>>> async def run():
...     con = await asyncpg.connect(user='postgres')
...     def encoder(delta):
...         ndelta = delta.normalized()
...         return (ndelta.years * 12 + ndelta.months,
...                 ndelta.days,
...                 ((ndelta.hours * 3600 +
...                    ndelta.minutes * 60 +
...                    ndelta.seconds) * 1000000 +
...                  ndelta.microseconds))
...     def decoder(tup):
...         return relativedelta(months=tup[0], days=tup[1],
...                              microseconds=tup[2])
...     await con.set_type_codec(
...         'interval', schema='pg_catalog', encoder=encoder,
...         decoder=decoder, format='tuple')
...     result = await con.fetchval(
...         "SELECT '2 years 3 mons 1 day'::interval")
...     print(result)
...     print(datetime.datetime(2002, 1, 1) + result)
... 
>>> asyncio.run(run())
relativedelta(years=+2, months=+3, days=+1)
2004-04-02 00:00:00

```

--------------------------------

### Define PostgreSQL Data Type (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents a PostgreSQL data type with its OID, name, kind (scalar, array, composite, range), and schema. It's a NamedTuple for immutability.

```python
from __future__ import annotations

import typing

from asyncpg.pgproto.types import (
    BitString, Point, Path, Polygon,
    Box, Line, LineSegment, Circle,
)

if typing.TYPE_CHECKING:
    from typing_extensions import Self


__all__ = (
    'Type', 'Attribute', 'Range', 'BitString', 'Point', 'Path', 'Polygon',
    'Box', 'Line', 'LineSegment', 'Circle', 'ServerVersion',
)




[docs]
class Type(typing.NamedTuple):
    oid: int
    name: str
    kind: str
    schema: str




Type.__doc__ = 'Database data type.'
Type.oid.__doc__ = 'OID of the type.'
Type.name.__doc__ = 'Type name.  For example "int2".'
Type.kind.__doc__ = \
    'Type kind.  Can be "scalar", "array", "composite" or "range".'
Type.schema.__doc__ = 'Name of the database schema that defines the type.'

```

--------------------------------

### Expire Asyncpg Pool Connections (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Causes all currently open connections in the pool to be marked for expiration. The next time a connection is acquired using `acquire()`, a new connection will be created to replace the expired one. This is useful for refreshing connections without explicitly closing and reopening the pool.

```python
async def expire_connections(self):
        """Expire all currently open connections.

        Cause all currently open connections to get replaced on the
        next :meth:`~asyncpg.pool.Pool.acquire()` call.

        .. versionadded:: 0.16.0
        """
        self._generation += 1
```

--------------------------------

### Represent Range Object as String in Python

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

This Python code snippet defines how a range object is represented as a string. It handles lower and upper bounds, including inclusivity, and formats the output as '<Range {lower}, {upper}>'. It does not have external dependencies within this snippet.

```python
if self._lower is not None:
                lb += repr(self._lower)

            if self._upper is not None:
                ub = repr(self._upper)
            else:
                ub = ''

            if self._upper is None or not self._upper_inc:
                ub += ')'
            else:
                ub += ']'

            desc = '{}, {}'.format(lb, ub)

        return '<Range {}>'.format(desc)

    __str__ = __repr__
```

--------------------------------

### Reset Type Codec in asyncpg

Source: https://magicstack.github.io/asyncpg/current/api/index

Resets a specified data type's codec to its default implementation within the 'public' schema. This is useful for reverting custom codec changes. It does not affect open transactions or registered listeners.

```python
_async _reset_type_codec(_typename_ , _*_ , _schema ='public'_)[source]
```

--------------------------------

### Reset Type Codec in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Resets a specified data type's codec to its default implementation in asyncpg. This involves introspecting the type, removing the custom codec from the protocol settings, and clearing the local statement cache.

```python
typeinfo = await self._introspect_type(typename, schema)
        self._protocol.get_settings().remove_python_codec(
            typeinfo['oid'], typename, schema)

        # Statement cache is no longer valid due to codec changes.
        self._drop_local_statement_cache()
```

--------------------------------

### Remove Listener for Connection Termination - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Removes a previously added callback for connection termination events.

```python
self.remove_termination_listener(my_conn_close_handler)
self.remove_termination_listener(my_async_conn_close_handler)
```

--------------------------------

### Remove Listener for Channel Messages - asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Removes a previously added callback for a specific PostgreSQL channel. If the channel has no more listeners after removal, it will be unsubscribed from.

```python
self.remove_listener('my_channel', my_callback_function)
self.remove_listener('another_channel', my_async_callback_function)
```

--------------------------------

### Define PostgreSQL Range Type (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Provides an immutable representation for PostgreSQL's `range` type. It supports checking for emptiness, subset/superset relationships, and equality.

```python
class _RangeValue(typing.Protocol):
    def __eq__(self, __value: object) -> bool:
        ...

    def __lt__(self, __other: _RangeValue) -> bool:
        ...

    def __gt__(self, __other: _RangeValue) -> bool:
        ...


_RV = typing.TypeVar('_RV', bound=_RangeValue)




[docs]
class Range(typing.Generic[_RV]):
    """Immutable representation of PostgreSQL `range` type."""

    __slots__ = ('_lower', '_upper', '_lower_inc', '_upper_inc', '_empty')

    _lower: _RV | None
    _upper: _RV | None
    _lower_inc: bool
    _upper_inc: bool
    _empty: bool

    def __init__(
        self,
        lower: _RV | None = None,
        upper: _RV | None = None,
        *,
        lower_inc: bool = True,
        upper_inc: bool = False,
        empty: bool = False
    ) -> None:
        self._empty = empty
        if empty:
            self._lower = self._upper = None
            self._lower_inc = self._upper_inc = False
        else:
            self._lower = lower
            self._upper = upper
            self._lower_inc = lower is not None and lower_inc
            self._upper_inc = upper is not None and upper_inc

    @property
    def lower(self) -> _RV | None:
        return self._lower

    @property
    def lower_inc(self) -> bool:
        return self._lower_inc

    @property
    def lower_inf(self) -> bool:
        return self._lower is None and not self._empty

    @property
    def upper(self) -> _RV | None:
        return self._upper

    @property
    def upper_inc(self) -> bool:
        return self._upper_inc

    @property
    def upper_inf(self) -> bool:
        return self._upper is None and not self._empty

    @property
    def isempty(self) -> bool:
        return self._empty

    def _issubset_lower(self, other: Self) -> bool:
        if other._lower is None:
            return True
        if self._lower is None:
            return False

        return self._lower > other._lower or (
            self._lower == other._lower
            and (other._lower_inc or not self._lower_inc)
        )

    def _issubset_upper(self, other: Self) -> bool:
        if other._upper is None:
            return True
        if self._upper is None:
            return False

        return self._upper < other._upper or (
            self._upper == other._upper
            and (other._upper_inc or not self._upper_inc)
        )

    def issubset(self, other: Self) -> bool:
        if self._empty:
            return True
        if other._empty:
            return False

        return self._issubset_lower(other) and self._issubset_upper(other)

    def issuperset(self, other: Self) -> bool:
        return other.issubset(self)

    def __bool__(self) -> bool:
        return not self._empty

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range):
            return NotImplemented

        return (
            self._lower,
            self._upper,
            self._lower_inc,
            self._upper_inc,
            self._empty
        ) == (
            other._lower,  # pyright: ignore [reportUnknownMemberType]
            other._upper,  # pyright: ignore [reportUnknownMemberType]
            other._lower_inc,
            other._upper_inc,
            other._empty
        )

    def __hash__(self) -> int:
        return hash((
            self._lower,
            self._upper,
            self._lower_inc,
            self._upper_inc,
            self._empty
        ))

    def __repr__(self) -> str:
        if self._empty:
            desc = 'empty'
        else:
            if self._lower is None or not self._lower_inc:
                lb = '('
            else:
                lb = '['

```

--------------------------------

### Terminate All Connections (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Forcefully close all active connections within an asyncpg connection pool. This action immediately releases all resources held by the pool. This method is part of the pool management API.

```python
asyncpg.Pool.terminate()
```

--------------------------------

### CursorFactory Cleanup (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/cursor

The __del__ method handles the cleanup of the cursor's state when the object is garbage collected. It detaches the state and potentially garbage collects the statement if necessary.

```Python
    def __del__(self):
        if self._state is not None:
            self._state.detach()
            self._connection._maybe_gc_stmt(self._state)
```

--------------------------------

### Check Transaction Status with asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Checks if the current connection is inside an active transaction. Returns a boolean value.

```python
con.is_in_transaction()
```

--------------------------------

### Reset Connection State in asyncpg

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/connection

Resets the internal state of an asyncpg connection, clearing listeners and log listeners. It checks if the connection is open and handles cases where the connection might be in an ongoing transaction, ensuring managed transactions are properly exited.

```python
self._check_open()
        self._listeners.clear()
        self._log_listeners.clear()

        if self._protocol.is_in_transaction() or self._top_xact is not None:
            if self._top_xact is None or not self._top_xact._managed:
                # Managed transactions are guaranteed to __aexit__
                # correctly.
                self._loop.call_exception_handler({
                    'message': 'Resetting connection with an '
```

--------------------------------

### Close asyncpg Connection Pool Gracefully

Source: https://magicstack.github.io/asyncpg/current/api/index

Gracefully closes all connections in the asyncpg pool. It waits for all connections to be released before shutting down. Errors during closing will lead to immediate pool termination.

```python
await pool.close()
```

--------------------------------

### Deactivate Idle Asyncpg Connection

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Handles the deactivation of an idle connection that has exceeded its inactivity period. It terminates the connection and performs necessary cleanup, ensuring that the pool doesn't hold onto unused resources.

```python
    def _deactivate_inactive_connection(self):
        if self._in_use is not None:
            raise exceptions.InternalClientError(
                'attempting to deactivate an acquired connection')

        if self._con is not None:
            # The connection is idle and not in use, so it's fine to
            # use terminate() instead of close().
            self._con.terminate()
            # Must call clear_connection, because _deactivate_connection
            # is called when the connection is *not* checked out, and
            # so terminate() above will not call the below.
            self._release_on_close()
```

--------------------------------

### Define PostgreSQL Attribute (Python)

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/types

Represents an attribute within a PostgreSQL relation, storing its name and its data type. The type is linked to the `asyncpg.types.Type` class.

```python
[docs]
class Attribute(typing.NamedTuple):
    name: str
    type: Type




Attribute.__doc__ = 'Database relation attribute.'
Attribute.name.__doc__ = 'Attribute name.'
Attribute.type.__doc__ = 'Attribute data type :class:`asyncpg.types.Type`.'

```

--------------------------------

### Cancel Asyncpg Connection Inactivity Timer

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

Cancels the inactivity timer for a connection. This is called when a connection is actively used or released, preventing premature deactivation.

```python
    def _maybe_cancel_inactive_callback(self):
        if self._inactive_callback is not None:
            self._inactive_callback.cancel()
            self._inactive_callback = None
```

--------------------------------

### Check if Asyncpg Pool is Closing or Closed

Source: https://magicstack.github.io/asyncpg/current/_modules/asyncpg/pool

This Python method returns a boolean indicating whether the asyncpg pool is in the process of closing or has already been closed. It checks internal flags `_closed` and `_closing`.

```python
    def is_closing(self):
        """Return ``True`` if the pool is closing or is closed.

        .. versionadded:: 0.28.0
        """
        return self._closed or self._closing
```

--------------------------------

### Check Pool Closing Status (asyncpg)

Source: https://magicstack.github.io/asyncpg/current/api/index

Determine if an asyncpg connection pool is in the process of closing or has already been closed. This function is useful for preventing operations on a pool that is no longer available. Added in version 0.28.0.

```python
asyncpg.Pool.is_closing()
```

=== COMPLETE CONTENT === This response contains all available snippets from this library. No additional content exists. Do not make further requests.
