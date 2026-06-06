import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
import sys

from .window import SysSenseWindow


class SysSenseApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='br.com.syssense')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        window = SysSenseWindow(self)
        window.present()


def main(version=None):
    app = SysSenseApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    main()