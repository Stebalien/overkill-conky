from overkill.sinks import PipeSink
from overkill.sources import Source
from collections import namedtuple

Variable = namedtuple("Variable", ['variable', 'required_args', 'optional_args'])

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
        self.conkyrc = tempfile.NamedTemporaryFile()
        self.conkyrc.write(
"""background no
out_to_console yes
update_interval 5.0
total_run_times 0
TEXT
""".encode('utf-8'))
        self.conkyrc.flush()
        self.cmd = ["conky", "-c", self.conkyrc.name]

    def on_stop(self):
        self.conkyrc.close()

    def on_subscribe(self, subscriber, subscription):
        if subscription not in self.exporting:
            self.conkyrc.write(("%s:${%s}\t" % (subscription, subscription)).encode("utf-8"))
            self.conkyrc.flush()
            if self._ready_to_signal:
                self.proc.send_signal(1)

    def handle_input(self, line):
        self._ready_to_signal = True;
        if not line:
            return
        line = line.strip('\t')
        try: 
            updates = dict(part.split(':', 1) for part in line.split('\t'))
        except ValueError:
            return
        self.push_updates(updates)

