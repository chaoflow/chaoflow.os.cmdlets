import subprocess
from cStringIO import StringIO


def _exec(*cmdline,**kws):
    r"""Run cmdline, cmdline is passed on to subprocess.Popen

    return dict(
        stdout=StringIO(stdout),
        stderr=StringIO(stderr),
        returncode=returncode,
        )
    
    The following kws are recognized with default values:
        cwd=None, i.e. do not change working directory
        raw=None, if set, the raw string output of stdout/stderr is returned

    Passing other kws raises a RuntimeError

        >>> _exec('true',kw1=1,kw2=2)
        Traceback (most recent call last):
        ...
        RuntimeError: Got unknown keyword arguments: kw1, kw2.

        >>> _exec('true', raw=True)
        {'returncode': 0, 'stderr': '', 'stdout': ''}

        >>> _exec('echo','foo\nbar')['stdout'].readlines()
        ['foo\n', 'bar\n']

        >>> _exec('false')
        Traceback (most recent call last):
        ...
        RuntimeError: Error running 'false':
        return code: 1, stderr:
        <BLANKLINE>
        .

        XXX: test stderr

        XXX: test cwd
    """
    cwd = kws.pop('cwd', None)
    raw = kws.pop('raw', None)
    #XXX
    ignore_returncode = kws.pop('ignore_returncode', False)

    if kws:
        raise RuntimeError("Got unknown keyword arguments: %s." % \
                (', '.join(kws.keys())),)

    cmd = subprocess.Popen(cmdline,
            cwd = cwd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            )
    stdout, stderr = cmd.communicate()
    if not ignore_returncode and cmd.returncode != 0:
        raise RuntimeError("Error running '%s':\nreturn code: %s, stderr:\n%s\n." % \
                (' '.join(cmdline), cmd.returncode, stderr))
    if not raw:
        stdout = StringIO(stdout)
        stderr = StringIO(stderr)

    return dict(stdout=stdout, stderr=stderr, returncode=cmd.returncode)


class Cmdlet(object):
    """
        A command line consists of cmdlets.

        Generally a cmdlet is translated into a string with the name of the
        cmdlet. A series of cmdlets forms a cmdline. Calling a cmdlet, execute
        the cmdline formed by the series up to this cmdlet (see below).

        As with ``ps.ax`` the ``ax`` is interpreted as the name for a cmdlet
        (see below) the normal attributes are named _<attr>. We could provide
        an adapter to access them as normal attributes, e.g.
        IRawCmdlet(cmdlet).<attr> = <value>. But its kind of unnecessary. Maybe
        not...
    """

    # internal
    __cmdslice__ = []
    __name__ = None
    __parent__ = None

    # public, _ is needed to distinguish from subcmdlets
    # further properties are defined below

    def __init__(self, name=None, parent=None, cmdslice=None):
        """
        An empty cmdlet is valid and generates an empty cmdline:
        XXX: is that good for Popen?

            >>> cmd = Cmdlet()
            >>> cmd.__name__ == cmd.__parent__ == None
            True
            >>> cmd._cmdline
            []

        The defaults are set in a way, that inheriting classed can override
        without defining a __init__ method:

            >>> cmdslice = ['some', 'cmd']
            >>> class SomeCmd(Cmdlet):
            ...     __cmdslice__ = cmdslice
            >>> s = SomeCmd()
            >>> s.__cmdslice__ is cmdslice
            True

        Set values during __init__:

            >>> name = 'name'
            >>> parent = 'parent'
            >>> cmd = Cmdlet(name=name,parent=parent)
            >>> cmd.__name__ == 'name'
            True
            >>> cmd.__parent__ == 'parent'
            True

        A cmdslice may be set independent of name

            >>> cmdslice = 'cmdslice'
            >>> cmd = Cmdlet(name=name,parent=parent,cmdslice=cmdslice)
            >>> cmd._cmdslice
            ['cmdslice']

        We have a childs dictionary

            >>> cmd._childs
            {}
        """
        if name is not None:
            self.__name__ = name
            if cmdslice is None:
                self._cmdslice = name
        if cmdslice is not None:
            self._cmdslice = cmdslice
        if parent is not None:
            self.__parent__ = parent
        self._childs = {}


    def _set_cmdslice(self, value):
        """
        A list is directly used, it is the same list you gave, i.e. you can
        change afterwards:

            >>> cmd = Cmdlet()
            >>> slice = ['list']
            >>> cmd._cmdslice = slice
            >>> cmd._cmdslice is slice
            True

        A string (str/unicode) is translated into a one-element list:

            >>> cmd._cmdslice = 'str'
            >>> cmd._cmdslice
            ['str']

            >>> cmd._cmdslice = u'unicode'
            >>> cmd._cmdslice
            [u'unicode']

        Everything else is translated into a list with list(value):

            >>> cmd._cmdslice = ('tuple',)
            >>> cmd._cmdslice
            ['tuple']

        Setting cmdslice to None clears it:

            >>> cmd._cmdslice = None
            >>> cmd._cmdslice
            []
        """
        if value is None:
            value = []
        elif type(value) in (str, unicode):
            value = [value]
        elif not type(value) is list:
            value = list(value)
        self.__cmdslice__ = value

    _cmdslice = property(
            lambda x: x.__cmdslice__,
            _set_cmdslice,
            )


    @property
    def _cmdline(self):
        """Return the cmdline that would be executed by cmd()

        The cmdline is given as a list of cmline elements:

            >>> cmd = Cmdlet('cmd')
            >>> cmd._cmdline
            ['cmd']

        A cmd uses its parent to form the cmdline.

            >>> subcmd = Cmdlet('subcmd',parent=cmd)
            >>> subcmd._cmdline
            ['cmd', 'subcmd']

            >>> subsubcmd = Cmdlet('subsubcmd',parent=subcmd)
            >>> subsubcmd._cmdline
            ['cmd', 'subcmd', 'subsubcmd']

        Empty elements are filtered out:

            >>> subcmd._cmdslice = ''
            >>> subsubcmd._cmdline
            ['cmd', 'subsubcmd']
        """
        try:
            cmdline = self.__parent__._cmdline + self._cmdslice
        except AttributeError:
            cmdline = self._cmdslice
        return filter(None, cmdline)


    def __call__(self, *args, **kws):
        """ WIP, needs format and workdir
        """
        res = _exec(*(self._cmdline+list(args)))
        self._res = res
        return [x.rstrip() for x in res['stdout'].readlines()]


    def __getattr__(self, name):
        """return cmdlet for name

        The cmdlet for subcmd is automatically created and returned

            >>> cmd = Cmdlet('cmd')
            >>> cmd.subcmd._cmdline
            ['cmd', 'subcmd']

        Once a cmdlet has been created, you'll always get the same one until
        you delete it:

            >>> cmd.subcmd == cmd.subcmd
            True

            >>> subcmd = cmd.subcmd
            >>> del cmd.subcmd
            >>> subcmd == cmd.subcmd
            False

        Attributes beginning with ``_`` still cause AttributeError, if
        non-existent:

            >>> getattr(cmd, '_a', 'not there')
            'not there'

        Setting an attribute beginning with ``_`` works:

            >>> cmd._a = 1
            >>> getattr(cmd, '_a', 'not there')
            1
        """
        if name[0] == '_':
            raise AttributeError(name)

        try:
            cmdlet = self._childs[name]
        except KeyError:
            cmdlet = self._childs[name] = Cmdlet(name, parent=self)
        return cmdlet


    def __delattr__(self, name):
        """Tested in __getattr__ doctest
        """
        del self._childs[name]


    def __setattr__(self, name, value):
        """
            >>> cmd = Cmdlet()
            >>> cmd.subcmd = 'subcmd'
            >>> cmd.subcmd._cmdline
            ['subcmd']
        """
        # Tested in __getattr__ doctest
        if name[0] == '_':
            object.__setattr__(self, name, value)
            return

        child = getattr(self, name)
        child._cmdslice = value
