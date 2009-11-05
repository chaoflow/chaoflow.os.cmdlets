from chaoflow.os.cmdlets import Cmdlet

class Git(Cmdlet):
    """A cmdlet preconfigured for git

        >>> git = Git()
        >>> git._cmdslice
        ['git', '--no-pager']
    """
    __cmdslice__ = ['git', '--no-pager']
