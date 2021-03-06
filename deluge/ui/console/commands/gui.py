#
# status.py
#
# Copyright (C) 2011 Nick Lanham <nick@afternight.org>
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

from deluge.ui.console.main import BaseCommand
import deluge.common
import deluge.component as component
from deluge.ui.console.modes.alltorrents import AllTorrents

class Command(BaseCommand):
    """Exit this mode and go into the more 'gui' like mode"""
    usage = "Usage: gui"
    interactive_only = True
    def handle(self, *args, **options):
        console = component.get("ConsoleUI")
        try:
            at = component.get("AllTorrents")
        except KeyError:
            at = AllTorrents(console.stdscr,console.encoding)
        console.set_mode(at)
        at.resume()
