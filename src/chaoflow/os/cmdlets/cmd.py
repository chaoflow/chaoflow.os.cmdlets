#!/usr/bin/env python

import subprocess
from cStringIO import StringIO


class CmdError(Exception):
    pass

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
    r"""
        A command line consists of cmdlets.

        Generally a cmdlet is translated into a string with the name of the
        cmdlet.

    A cmdlet has a readonly name which is set during __init__:

        >>> cmdlet1 = Cmdlet('cmd')
        >>> cmdlet1._name
        'cmd'

    XXX: not good

        >>> cmdlet1._cmdstr
        'cmd'
        >>> cmdlet1._cmdline
        ['cmd']
        >>> cmdlet1._parent is None
        True

    All real attributes are prefixed with an underscore. Without underscore is
    interpreted as the name for the next cmdlet.

        >>> cmdlet1.subcmd._cmdline
        ['cmd', 'subcmd']

    After once using a cmdlet, you always get the same cmdlet

        >>> cmdlet1.subcmd._marked = True
        >>> cmdlet1.subcmd._marked
        True

    You can define aliases:

        >>> cmdlet1.alias = 'much longer subcommand'
        >>> cmdlet1.alias._cmdline
        ['cmd', 'much longer subcommand']

    XXX: not good, needs to be list elements, not space separated

    It is convenient to define a root element without cmdstr:

        >>> sh = Cmdlet('sh', cmdstr='')
        >>> sh.ps.ax._cmdline
        ['ps', 'ax']

    You can execute cmds:

        >>> sh.ps.ax()[0].split()[0]
        'PID'

        >>> sh.echo('foo\nbar')
        ['foo', 'bar']
    """
    _name = property(lambda x: x.__name__)
    _parent = property(lambda x: x.__parent__)
    

    def __init__(self, name, parent=None, cmdstr=None):
        self.__name__ = name
        self.__parent__ = parent
        self._childs = {}
        if cmdstr is None:
            self._cmdstr = name
        else:
            self._cmdstr = cmdstr


    @property
    def _cmdline(self):
        # cmdline up to this node 
        try:
            cmdline = self.__parent__._cmdline + [self._cmdstr]
        except AttributeError:
            cmdline = [self._cmdstr]
        return filter(None, cmdline)


    def __call__(self, *args, **kws):
        fmt = kws.pop('fmt', 'stdout')
        res = _exec(*(self._cmdline+list(args)))
        self._res = res
        return [x.rstrip() for x in res['stdout'].readlines()]


    def __getattr__(self, name):
        """return cmdlet for name
        """
        # cmdlet names may not begin with an underscore
        # use the _cmdstr attribute to achieve output with leading underscore
        if name[0] == '_':
            raise AttributeError(name)

        try:
            cmdlet = self._childs[name]
        except KeyError:
            cmdlet = self._childs[name] = Cmdlet(name, parent=self)
        return cmdlet


    def __setattr__(self, name, value):
        # cmdlet names may not begin with an underscore
        if name[0] == '_':
            object.__setattr__(self, name, value)
            return

        # generate and get the child cmdlet and assign cmdstr
        child = getattr(self, name)
        child._cmdstr = value
