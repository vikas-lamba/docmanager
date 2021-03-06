#
# Copyright (c) 2015 SUSE Linux GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact SUSE LLC.
#
# To contact SUSE about this file by physical or electronic mail,
# you may find current contact information at www.suse.com

__author__="Rick Salevsky, Manuel Schnitzer, and Thomas Schraitle"
__version__="3.3.4"

import atexit
import sys
import time
from docmanager.action import Actions
from docmanager.cli import parsecli
from docmanager.core import ReturnCodes
from docmanager.display import getrenderer
from docmanager.exceptions import DMConfigFileNotFound
from docmanager.logmanager import log
# from xml.sax._exceptions import SAXParseException

def shutdown(start):
    end = int(round(time.time() * 1000))
    log.info("DocManager Runtime: %d seconds" % ((end-start)/1000))

def main(cliargs=None):
    """Entry point for the application script

    :param list cliargs: Arguments to parse or None (=use sys.argv)
    """

    atexit.register(shutdown, int(round(time.time() * 1000)))

    try:
        a = Actions(parsecli(cliargs))
        res = a.parse()
        renderer = None

        if hasattr(a.args, 'format') is False:
            renderer = getrenderer('default')
        else:
            renderer = getrenderer(a.args.format)

        sys.exit(renderer(res, args=a.args))
    except PermissionError as err: # noqa
        log.error("%s on file %r.", err.args[1], err.filename)
        sys.exit(ReturnCodes.E_PERMISSION_DENIED)
    except ValueError as err:
        log.error(err)
        sys.exit(ReturnCodes.E_INVALID_XML_DOCUMENT)
    except FileNotFoundError as err: # noqa
        log.error("Could not find file %r.", err.filename)
        sys.exit(ReturnCodes.E_FILE_NOT_FOUND)
    except DMConfigFileNotFound as err: #noqa
        log.error("Couldn't find config file '%s'", err)
        sys.exit(ReturnCodes.E_FILE_NOT_FOUND)
    except KeyboardInterrupt:
        sys.exit()
