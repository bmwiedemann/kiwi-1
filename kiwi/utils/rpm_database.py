# Copyright (c) 2019 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import os
import re

# project
from kiwi.command import Command
from kiwi.path import Path
from kiwi.utils.rpm import Rpm


class RpmDataBase(object):
    """
    **Setup RPM database configuration**
    """
    def __init__(self, root_dir, macro_file=None):
        self.rpmdb_host = Rpm()
        self.rpmdb_image = Rpm(root_dir, macro_file)
        self.root_dir = root_dir

    def has_rpm(self):
        """
        Check if rpm binary was found in root_dir
        """
        rpm_search_env = {
            'PATH': os.sep.join([self.root_dir, 'usr', 'bin'])
        }
        rpm_bin = Path.which(
            'rpm', custom_env=rpm_search_env, access_mode=os.X_OK
        )
        if not rpm_bin:
            return False
        return True

    def rebuild_database(self):
        """
        Rebuild image rpm database taking current macro setup into account
        """
        Command.run([
            'chroot', self.root_dir, 'rpmdb', '--rebuilddb'
        ])

    def set_macro_from_string(self, setting):
        """
        Setup given macro setting in image rpm configuration.
        The following format for the setting is expected:

            macro_base_key_name%macro_value.

        If this expression is not matched the macro setup will be
        skipped. Please note the macro_base_key_name includes
        the name of the macro as rpm expects it exlcuding the
        leading '%' character.

        Also note macro defintions must happen before calling
        set_database_* methods in order to become effective

        :param string setting: macro key and value as one string
        """
        match = re.match('(.*)%(.*)', setting)
        if match:
            self.rpmdb_image.set_config_value(
                match.group(1), match.group(2)
            )

    def write_config(self):
        self.rpmdb_image.write_config()

    def set_database_to_host_path(self):
        """
        Setup dbpath to point to the host rpm dbpath configuration
        and write the configuration file
        """
        self.rpmdb_image.set_config_value(
            '_dbpath', self.rpmdb_host.get_query('_dbpath')
        )
        self.rpmdb_image.write_config()

    def set_database_to_image_path(self):
        """
        Setup dbpath to point to the image rpm dbpath configuration
        Rebuild the database such that it gets moved to the standard
        path and delete KIWI's custom macro setup
        """
        self.rpmdb_image.wipe_config()
        rpm_image_dbpath = self.rpmdb_image.expand_query('%_dbpath')
        if rpm_image_dbpath != self.rpmdb_host.expand_query('%_dbpath'):
            self.rpmdb_image.set_config_value(
                '_dbpath_rebuild', self.rpmdb_image.get_query('_dbpath')
            )
            Path.wipe(
                os.sep.join([self.root_dir, rpm_image_dbpath])
            )
            self.rpmdb_image.write_config()
            self.rebuild_database()
            self.rpmdb_image.wipe_config()
