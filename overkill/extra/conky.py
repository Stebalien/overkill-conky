##
#    This file is part of Overkill-conky.
#
#    Overkill-conky is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Overkill-conky is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Overkill-conky.  If not, see <http://www.gnu.org/licenses/>.
##

from overkill.sinks import PipeSink
from overkill.sources import Source
from collections import namedtuple
import os

Variable = namedtuple("Variable", ['variable', 'required_args', 'optional_args'])

TEMPLATE = """
conky.config = {{
    background = false,
    out_to_console = true,
    out_to_x = false,
    no_buffers = true,
    update_interval = 5.0,
    total_run_times = 0,
}}
conky.text = [[
{}
]]
"""

class ConkySource(Source, PipeSink):
    restart = True
    publish_prefixes = {
        "cpu",
        "memperc",
        "acpitemp",
        "battery",
        "battery_short",
        "battery_percent",
        "upspeedf",
        "downspeedf"
    }

    def is_publishing(self, subscription):
        return subscription.split(' ', 1)[0] in self.publish_prefixes

    def __init__(self):
        self.exporting = set()
        self._ready_to_signal = False
        super().__init__()

    def on_start(self):
        import tempfile
        self.conkyrc = tempfile.NamedTemporaryFile(prefix="overkill-conky-", suffix=".lua")
        self.reconfigure()
        self.cmd = ["conky", "-c", self.conkyrc.name]

    def reconfigure(self):
        self.conkyrc.seek(0, os.SEEK_SET)
        self.conkyrc.write(TEMPLATE.format("\t".join(
            "%s:${%s}" % (sub, sub)
            for sub in self.exporting
        )).encode('utf-8'))
        self.conkyrc.truncate()
        self.conkyrc.flush()
        if self._ready_to_signal:
            self.proc.send_signal(1)

    def on_stop(self):
        self.conkyrc.close()

    def on_subscribe(self, subscriber, subscription):
        self.exporting.add(subscription)
        self.reconfigure()

    def handle_input(self, line):
        self._ready_to_signal = True
        if not line:
            return
        line = line.strip('\t')
        try:
            updates = dict(part.split(':', 1) for part in line.split('\t'))
        except ValueError:
            return
        self.push_updates(updates)

