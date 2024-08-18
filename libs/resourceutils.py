import os

from Qt import QtCore, QtGui

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


__icon_extensions__ = ('.png', '.ico', '.svg', '.bmp', '.cur')


def iterIcons():
    """
    Returns a generator that yields icons from the current resource environment.

    :rtype: Iterator[str]
    """

    # Iterate through resource paths
    #
    iterDirs = QtCore.QDirIterator(":", QtCore.QDirIterator.Subdirectories)

    while iterDirs.hasNext():

        # Check if this is an icon
        #
        resourcePath = iterDirs.next()
        filename = os.path.basename(resourcePath)

        name, extension = os.path.splitext(filename)

        if extension in __icon_extensions__:

            yield resourcePath

        else:

            continue
