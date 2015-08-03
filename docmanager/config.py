#
# Copyright (c) 2014-2015 SUSE Linux GmbH
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

import os
import shlex
import subprocess
import sys
from configparser import ConfigParser
from docmanager.core import USER_CONFIG, CONFIG_NAME
from docmanager.exceptions import DMConfigFileNotFound
from docmanager.logmanager import log


def docmanagerconfig(cfgfiles=None, include_etc=True):
    """Read DocManager configuration files. The following files are
       searched for and its configuration is merged together
       (in this order, from lowest to highest):

       * /etc/docmanager/config
       * $XDG_CONFIG_HOME/docmanager/docmanager.config if not found, falls back
         to ~/.config/docmanager/docmanager.config
       * GIT_REPO_DIR/.git/docmanager.conf
         (GIT_REPO_DIR is retrieved by the command
         `git rev-parse --show-toplevel`)
       * DOCMANAGER_GIT_REPO/etc/config

      See the XDG Base Directory Specification:
      http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

      :param list cfgfiles: your own list of configfiles
      :param bool include_etc: Should the develop(!) 'etc/' directory included?
                               Only useful for development
      :return: merged configuration object
      :rtype: configparser.ConfigParser

    """
    # Start with the global ones
    configfiles = [os.path.join('/etc', CONFIG_NAME)]

    if cfgfiles is None:
        # We need to assemble our configuration file list
        #
        # Append user config; env variable XDG_CONFIG_HOME is used if set
        configfiles.append(USER_CONFIG)

        # Append config when a .git repo is found
        try:
            cmd = shlex.split("git rev-parse --show-toplevel")
            git = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            gitrepo = git.communicate()
            # Not a git repository?
            if git.returncode != 128:
                gitrepo = gitrepo[0].decode("utf-8").strip()
                configfiles.append(os.path.join(gitrepo,
                                                '.git/docmanager.conf'))
        except FileNotFoundError:
            # If we don't find the git command, we skip the local config file
            # alltogether
            pass
    else:
        log.debug("Using own config file %s", cfgfiles)
        # In case the user passes its own config file list, use it:
        configfiles = cfgfiles

    # Support pyvenv virtual environments; add it as a last item
    #
    # See http://stackoverflow.com/a/1883251
    if (cfgfiles is None) and include_etc and hasattr(sys, 'base_prefix'):
        log.debug("Running inside a virtual env.")
        dname = os.path.dirname(__file__)
        configfiles.append(os.path.join(dname, 'template/config'))

    config = ConfigParser()
    x = config.read(configfiles)

    if not x:
        raise DMConfigFileNotFound(x)

    log.debug("All configfiles %s", configfiles)
    log.debug("Used config file: %s", x)

    return config


def create_userconfig():
    """Copies template for user config to USER_CONFIG
       If user config already exists, do nothing

     :raise: FileNotFoundError
    """
    if os.path.exists(USER_CONFIG):
        return

    import shutil

    tmpldir = os.path.join(os.path.dirname(__file__), "template")
    cfgtmpl = os.path.join(tmpldir, "config")

    # From http://stackoverflow.com/a/600612
    try:
        os.makedirs(os.path.dirname(USER_CONFIG))
        log.debug("UserConfig: Created directory for %s", USER_CONFIG)
    except OSError as err:
        import errno
        if not(err.errno == errno.EEXIST and os.path.isdir(tmpldir)):
            raise

    shutil.copyfile(cfgtmpl, USER_CONFIG)
    log.debug("UserConfig: Copied template %s to %s", cfgtmpl, USER_CONFIG)
