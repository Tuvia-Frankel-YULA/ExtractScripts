import sys
from asyncio import Future
from tkinter import filedialog

from dbus_fast.aio import MessageBus

import util

match sys.platform:
    case 'linux':
        import dbus_fast
        from dbus_fast import message_bus, Variant

        global bus
        global desktop_introspection
        global desktop_proxy
        global file_chooser_interface


        async def init():
            global bus
            bus = await MessageBus().connect()

            global desktop_introspection
            desktop_introspection = await bus.introspect('org.freedesktop.portal.Desktop',
                                                         '/org/freedesktop/portal/desktop')

            global desktop_proxy
            desktop_proxy = bus.get_proxy_object('org.freedesktop.portal.Desktop',
                                                 '/org/freedesktop/portal/desktop',
                                                 desktop_introspection)

            global file_chooser_interface
            file_chooser_interface = desktop_proxy.get_interface('org.freedesktop.portal.FileChooser')


        util.run_sync(init())


        def show_open_file(title: str, filetypes: list[(str, str)], default_folder: str) -> str:
            return show_file_dialog(title, filetypes, False)

        def show_open_folder(title: str, default_folder: str) -> str:
            return show_file_dialog(title, [], True)


        def show_file_dialog(title: str, filetypes: list[(str, str)], is_folder: bool) -> str:
            filters = []

            for filetype in filetypes:
                filters.append([filetype[0], [[0, filetype[1]]]])

            async def do_async():
                handle = await file_chooser_interface.call_open_file('',
                                                                     title, {
                                                                         'filters': Variant('a(sa(us))', filters),
                                                                         'directory': Variant('b', is_folder)
                                                                     })
                response = await wait_for_response(handle)

                if response[0] == 0 and len(response[1]['uris'].value) > 0:
                    return util.uri_to_path(response[1]['uris'].value[0])
                else:
                    return ''

            return util.run_sync(do_async())


        async def wait_for_response(handle):
            response_future = Future()

            def response_notify(in_response, in_results):
                if in_response == 0:
                    response_future.set_result((in_response, in_results))
                else:
                    response_future.set_result((in_response, {}))

            response_introspection = await bus.introspect('org.freedesktop.portal.Desktop',
                                                          handle)
            response_proxy = bus.get_proxy_object('org.freedesktop.portal.Desktop',
                                                  handle,
                                                  response_introspection)
            response_interface = response_proxy.get_interface('org.freedesktop.portal.Request')

            response_interface.on_response(response_notify)

            value = await response_future

            response_interface.off_response(response_notify)

            return value

    case _:
        def show_open_file(title: str, filetypes: list[(str, str)], default_folder: str) -> str:
            return filedialog.askopenfilename(
                title=title,
                filetypes=filetypes,
                initialdir=default_folder)


        def show_open_folder(title: str, default_folder: str) -> str:
            return filedialog.askdirectory(
                title=title,
                initialdir=default_folder)
