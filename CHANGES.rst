=========
 CHANGES
=========

5.0 (unreleased)
================

- Nothing changed yet.


4.1.0 (2020-11-11)
==================

- Add support for Python 3.7, 3.8, and 3.9.

- Drop support for Python 3.4 and 3.5.


4.0.0 (2017-11-15)
==================

- Add support for Python 3.4, 3.5, and 3.6.

- Add support for PyPy.


3.6.0 (2011-03-23)
==================

- Moved ``zope.app.server.zpasswd`` to ``zope.password.zpasswd``.


3.5.0 (2009-12-19)
==================

- Use ``zope.password`` instead of ``zope.app.authentication``

- Depend on new ``zope.processlifetime`` implementations instead of
  using BBB imports from ``zope.app.appsetup``.


3.4.2 (2008-08-18)
==================

- Moved a doctest into a unittest to fix failures in the KGS test suite
  (see LP #257954)


3.4.1 (2008-02-25)
==================

- Fixed restart so that the process exits with a non-zero exit status
  so it gets restarted by zdaemon, or an equivalent mechanism.

- Removed the use of ``ThreadedAsync``.


3.4.0 (2007-10-27)
==================

- Initial release independent of the main Zope tree.
