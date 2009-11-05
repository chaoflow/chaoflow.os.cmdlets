Introduction
============

The purpose of chaoflow.os.cmdlets is to make creation and execution of
cmdlines easy, pain- and noise-free.

	>>> from chaoflow.os.cmdlets import Cmdlet
	>>> ls = Cmdlet('ls')
	>>> ls('-a1')	
	['.', '..']

- alias






    A cmdlet has a readonly name which is set during __init__:
    XXX: why readonly, why a name at all?!

        >>> cmdlet1 = Cmdlet('cmd')
        >>> cmdlet1._name
        'cmd'
        >>> cmdlet1._cmdslice
        ['cmd']
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

        >>> cmdlet1.alias = ['much', 'longer', 'subcommand']
        >>> cmdlet1.alias._cmdline
        ['cmd', 'much', 'longer', 'subcommand']

    A cmdlet without footprint on the cmdline:

        >>> cmdlet = Cmdlet('nocmd', cmdslice=[])
        >>> cmdlet._cmdline
        []

    or also without name - XXX: still not sure why it has a name:

        >>> cmdlet = Cmdlet()
        >>> cmdlet._cmdline
        []

    It is convenient to define a root element without footprint on the cmdline:

        >>> sh = Cmdlet('sh', cmdslice='')
        >>> sh.ps.ax._cmdline
        ['ps', 'ax']

    You can execute cmds:

        >>> sh.ps.ax()[0].split()[0]
        'PID'

        >>> sh.echo('foo\nbar')
        ['foo', 'bar']
