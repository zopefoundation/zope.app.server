=================================
Zope 3 Application Server Support
=================================

This package is responsible for initializing and starting the servers that
will provide access to the Zope 3 application. This package is heavily
twisted-depedent, though some pieces can be reused to bring up the Zope 3
application server in other environemnts.


Server Types
------------

Zope 3 needs to support many server types -- HTTP, FTP, HTTP with postmortem
debugging, etc.  All of them are registered as ``IServerType`` utilities in
ZCML. This allows developers to easily develop and register new servers for
Zope 3.

``ServerType`` is an implementation of ``IServerType`` that is specific to the
standard Twisted servers..  The constructor of ``ServerType`` takes three
arguments: the factory that will create a Twisted ``IServerFactory`` object
and the default port and IP to which to bind the server.

The ``factory`` argument should be a callable expecting one argument, the ZODB
instance. It is up to the factory, to implement the necessary glue between the
server and the application:

  >>> class TwistedServerFactoryStub(object):
  ...     def doStart(self): pass

  >>> def factory(db):
  ...     print 'ZODB: %s' %db
  ...     return TwistedServerFactoryStub()

For the other two constructor arguments of ``ServerType``, the ``defaultPort``
argument specifies the default TCP port number for the server. The
``defaultIP`` argument specifies the network interface for listening on.  You
can specify the network interface IP address, or an empty string if you want
to listen on all interfaces.

We are now ready to instantiate the server type:

  >>> from zope.app.server.server import ServerType
  >>> st = ServerType(factory, defaultPort=8080)

and let's make sure it really implements the promised interface:

  >>> from zope.interface.verify import verifyObject
  >>> from zope.app.server.interfaces import IServerType
  >>> verifyObject(IServerType, st)
  True

A server type is then registered as a named utility.  These utilities are used
while interpreting ``<server>`` sections of `zope.conf` to create instances of
servers listening on a specific port.

When you create an instance of a server using the ``create()`` method of the
server type, you need to tell it an identifying name and a the ZODB database
object. The IP address, port and backlog count can be optionally passed to the
method. 

  >>> db = 'my database'
  >>> server = st.create('Example-HTTP', db, port=8080)
  ZODB: my database
  >>> server #doctest:+ELLIPSIS
  <zope.app.server.server.ZopeTCPServer instance at ...>

As you can see the server type creates a Zope-specific TCP server, which is
simply a standard ``twisted.internet.TCPServer`` that creates a log entry upon
startup.

  >>> server.startService()
  >>> print log.getvalue()
  -- Example-HTTP Server started.
     Hostname: localhost
     Port: 8080

You can, of course, create multiple instances of the same server type, and
bind them to different ports.

  >>> server2 = st.create('Example-HTTP-2', db, port=8081)
  ZODB: my database

  >>> server2.startService()
  >>> print log.getvalue()
  -- Example-HTTP Server started.
     Hostname: localhost
     Port: 8080
  -- Example-HTTP-2 Server started.
     Hostname: localhost
     Port: 8081

A special type of server type is the SSL server type; it requires some
additional information (private key path, certificate path, and TLS flag) to
start up the server. The setup will only work, if OpenSSL is installed:

  # >>> from zope.app.server.server import SSLServerType
  # >>> ssl_st = SSLServerType(factory, defaultPort=8443)
  # 
  # >>> ssl_server = ssl_st.create('Example-HTTPS', db,
  # ...                            'server.pem', 'server.pem')
  # ZODB: my database
  # >>> ssl_server #doctest:+ELLIPSIS
  # <zope.app.server.server.ZopeSSLServer instance at ...>


Server Factories
----------------

Now, of course we do not hardwire the setup of actual servers in
Python. Instead, we are using ZConfig to setup the servers. Unfortunately that
means that we need yet another abstraction layer to setup the
servers. ZConfig-based configuration code creates so called ``ServerFactory``
and ``SSLServerFactory`` objects that then use the server types to create the
servers.

  >>> from zope.interface import implements
  >>> from zope.app.server.interfaces import IServerType
  >>> class MyServerType:
  ...     implements(IServerType)
  ...     def create(self, name, db,
  ...                port='unknown', ip='', backlog=50):
  ...         if not ip:
  ...             ip = '*' # listen on all interfaces
  ...         return ('%s server on %s:%d, registered with %s, backlog %d'
  ...                 % (name, ip, port, db, backlog))

  >>> from zope.app.testing import ztapi
  >>> ztapi.provideUtility(IServerType, MyServerType(), name='HTTP')
  >>> ztapi.provideUtility(IServerType, MyServerType(), name='FTP')

``ServerFactory`` is used to hook into ZConfig and create instances of servers
specified in `zope.conf`.  It gets a `section` argument that contains settings
specified in a ZConfig ``<server>`` section.

    >>> class ServerSectionStub:
    ...     type = 'HTTP'
    ...     address = ('', 8080)
    ...     backlog = 30
    >>> my_section = ServerSectionStub()

    >>> from zope.app.server.server import ServerFactory
    >>> sf = ServerFactory(my_section)

The server factory object knows how to create a server, given a ZODB database
object.

    >>> db = 'my db'
    >>> print sf.create(db)
    HTTP server on *:8080, registered with my db, backlog 30

The settings should actually work with FTP as well. 

    >>> my_section.type = 'FTP'
    >>> my_section.address = ('127.0.0.1', 8021)
    >>> sf = ServerFactory(my_section)
    >>> print sf.create(db)
    FTP server on 127.0.0.1:8021, registered with my db, backlog 30

