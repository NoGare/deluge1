#
# config.py
#
# Copyright (C) 2008-2009 Ido Abramovich <ido.deluge@gmail.com>
# Copyright (C) 2009 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#

from twisted.internet import defer

from deluge.ui.console.main import BaseCommand
import deluge.ui.console.colors as colors
from deluge.ui.client import client
import deluge.component as component
from deluge.log import LOG as log

from optparse import make_option

torrent_options = {
    "max_download_speed": float,
    "max_upload_speed": float,
    "max_connections": int,
    "max_upload_slots": int,
    "private": bool,
    "prioritize_first_last": bool,
    "is_auto_managed": bool,
    "stop_at_ratio": bool,
    "stop_ratio": float,
    "remove_at_ratio": bool,
    "move_on_completed": bool,
    "move_on_completed_path": str
    }


class Command(BaseCommand):
    """Show and set per-torrent options"""

    option_list = BaseCommand.option_list + (
            make_option('-s', '--set', action='store', nargs=2, dest='set',
                        help='set value for key'),
    )
    usage = "Usage: torrent_option <torrent-id> [<key1> [<key2> ...]]\n"\
            "       torrent_option <torrent-id> --set <key> <value>"

    def handle(self, *args, **options):
        self.console = component.get("ConsoleUI")
        if options['set']:
            return self._set_option(*args, **options)
        else:
            return self._get_option(*args, **options)


    def _get_option(self, *args, **options):

        def on_torrents_status(status):
            for torrentid, data in status.items():
                self.console.write('')
                if 'name' in data:
                    self.console.write('{!info!}Name: {!input!}%s' % data.get('name'))
                self.console.write('{!info!}ID: {!input!}%s' % torrentid)
                for k, v in data.items():
                    if k != 'name':
                        self.console.write('{!info!}%s: {!input!}%s' % (k, v))

        def on_torrents_status_fail(reason):
            self.console.write('{!error!}Failed to get torrent data.')

        torrent_ids = []
        torrent_ids.extend(self.console.match_torrent(args[0]))

        request_options = []
        for opt in args[1:]:
            if opt not in torrent_options:
                self.console.write('{!error!}Unknown torrent option: %s' % opt)
                return
            request_options.append(opt)
        if not request_options:
            request_options = [ opt for opt in torrent_options.keys() ]
        request_options.append('name')

        d = client.core.get_torrents_status({"id": torrent_ids}, request_options)
        d.addCallback(on_torrents_status)
        d.addErrback(on_torrents_status_fail)
        return d


    def _set_option(self, *args, **options):
        deferred = defer.Deferred()
        torrent_ids = []
        torrent_ids.extend(self.console.match_torrent(args[0]))
        key = options["set"][0]
        val = options["set"][1] + " " .join(args[1:])

        if key not in torrent_options:
            self.console.write("{!error!}The key '%s' is invalid!" % key)
            return

        val = torrent_options[key](val)

        def on_set_config(result):
            self.console.write("{!success!}Torrent option successfully updated.")
            deferred.callback(True)

        self.console.write("Setting %s to %s for torrents %s.." % (key, val, torrent_ids))
        client.core.set_torrent_options(torrent_ids, {key: val}).addCallback(on_set_config)
        return deferred
