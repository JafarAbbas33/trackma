# This file is part of Trackma.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import threading

from gi.repository import GLib, GObject, Gtk, Gdk

from trackma import utils, data
from trackma.ui.gtk import gtk_dir
from trackma.ui.gtk.showinfobox import ShowInfoBox


class SearchThread(threading.Thread):
    def __init__(self, engine, search_text, callback):
        threading.Thread.__init__(self)
        self._entries = []
        self._error = None
        self._engine = engine
        self._search_text = search_text
        self._callback = callback
        self._stop_request = threading.Event()

    def run(self):
        try:
            self._entries = self._engine.fetch_airing_schedule(self._search_text)
        except utils.TrackmaError as e:
            self._entries = []
            self._error = e

        if not self._stop_request.is_set():
            GLib.idle_add(self._callback, self._entries, self._error)

    def stop(self):
        self._stop_request.set()


@Gtk.Template.from_file(os.path.join(gtk_dir, 'data/airingwindow.ui'))
class AiringWindow(Gtk.Window):
    __gtype_name__ = 'AiringWindow'

    __gsignals__ = {
        'search-error': (GObject.SignalFlags.RUN_FIRST, None,
                         (str,))
    }

    btn_add_show = Gtk.Template.Child()
    search_paned = Gtk.Template.Child()
    shows_viewport = Gtk.Template.Child()
    show_info_container = Gtk.Template.Child()
    progress_spinner = Gtk.Template.Child()
    headerbar = Gtk.Template.Child()

    def __init__(self, engine, colors, current_status, transient_for=None):
        Gtk.Window.__init__(self, transient_for=transient_for)
        self.init_template()
        self._entries = []
        self._selected_show = None
        self._showdict = None

        self._engine = engine
        self._current_status = current_status
        self._search_thread = None

        self.showlist = SearchTreeView(colors)
        self.showlist.get_selection().connect("changed", self._on_selection_changed)
        self.showlist.set_size_request(400, 500)
        self.showlist.show()

        self.info = ShowInfoBox(engine, orientation=Gtk.Orientation.VERTICAL)
        self.info.set_size_request(400, 350)
        self.info.show()

        self.shows_viewport.add(self.showlist)
        self.show_info_container.pack_start(self.info, True, True, 0)
        self.search_paned.set_position(700)
        self.set_size_request(1200, 400)
        GLib.idle_add(self._search, '')

    # @Gtk.Template.Callback()
    # def _on_search_entry_search_changed(self, search_entry):
    #     search_text = search_entry.get_text().strip()
    #     self.progress_spinner.start()
    #     if search_text == "":
    #         if self._search_thread:
    #             self._search_thread.stop()
    #         self._search_finish()
    #     else:
    #         self._search(search_text)
    #         self.progress_spinner.start()

    def _search(self, text):
        if self._search_thread:
            self._search_thread.stop()

        # self.headerbar.set_subtitle("Searching: \"%s\"" % text)
        self.headerbar.set_subtitle('Retrieving airing schedule')
        self._search_thread = SearchThread(self._engine,
                                           text,
                                           self._search_finish_idle)
        self._search_thread.start()

    def _search_finish(self):
        self.headerbar.set_subtitle('Retrieved airing schedule')
        # self.progress_spinner.stop()

    def _search_finish_idle(self, entries, error):
        print('Total entries:', len(entries))

        self._entries = entries
        self._showdict = dict()
        self._search_finish()
        self.showlist.append_start()


        # print('='*80)
        # print('== Next In 000 ==')
        for res in self._entries:
            # print('fetch_airing_schedule', res)
            next_episode = '-'
            next_episode_in = '-'
            for extra in res['extra']:
                if 'Next Episode' == extra[0]:
                    next_episode = extra[1]
                elif 'Next Episode In' == extra[0]:
                    next_episode_in = extra[1]
            # print(next_episode_in)


        for show in entries:
            next_episode = '-'
            next_episode_in = '-'
            for extra in res['extra']:
                if 'Next Episode' == extra[0]:
                    next_episode = extra[1]
                elif 'Next Episode In' == extra[0]:
                    next_episode_in = extra[1]
            # print('_search_finish_idle', next_episode_in)

            self._showdict[show['id']] = show
            self.showlist.append(show)
        # print('='*80)

        self.showlist.append_finish()

        self.btn_add_show.set_sensitive(False)

        if error:
            self.emit('search-error', error)

    @Gtk.Template.Callback()
    def _on_btn_add_show_clicked(self, btn):
        show = self._get_full_selected_show()

        if show is not None:
            self._add_show(show)

    def _get_full_selected_show(self):
        for item in self._entries:
            if item['id'] == self._selected_show:
                return item

        return None

    def _add_show(self, show):
        try:
            self._engine.add_show(show, self._current_status)
        except utils.TrackmaError as e:
            self.emit('search-error', e)

    def _on_selection_changed(self, selection):
        # Get selected show ID
        (tree_model, tree_iter) = selection.get_selected()
        if not tree_iter:
            return

        self._selected_show = int(tree_model.get(tree_iter, 0)[0])
        if self._selected_show in self._showdict:
            self.info.load(self._showdict[self._selected_show])
            print('*'*80)
            print('Enabling...')
            in_user_list = self._showdict[self._selected_show]['extra'][0][1]
            print('in_user_list:', in_user_list)
            print('*'*80)
            if in_user_list == 'No':
                self.btn_add_show.set_sensitive(True)
            else:
                self.btn_add_show.set_sensitive(False)

class SearchTreeView(Gtk.TreeView):
    def __init__(self, colors):
        Gtk.TreeView.__init__(self)

        self.cols = dict()
        i = 1
        for name in ('Title', 'Episode', 'Time left'):
            self.cols[name] = Gtk.TreeViewColumn(name)
            self.cols[name].set_sort_column_id(i)
            self.append_column(self.cols[name])
            i += 1

        # renderer_id = Gtk.CellRendererText()
        # self.cols['ID'].pack_start(renderer_id, False)
        # self.cols['ID'].add_attribute(renderer_id, 'text', 0)

        renderer_title = Gtk.CellRendererText()
        self.cols['Title'].pack_start(renderer_title, False)
        self.cols['Title'].set_resizable(True)
        self.cols['Title'].set_expand(False)
        self.cols['Title'].add_attribute(renderer_title, 'text', 1)
        self.cols['Title'].add_attribute(renderer_title, 'foreground', 4)

        renderer_type = Gtk.CellRendererText()
        self.cols['Episode'].pack_start(renderer_type, False)
        self.cols['Episode'].add_attribute(renderer_type, 'text', 2)

        renderer_total = Gtk.CellRendererText()
        self.cols['Time left'].pack_start(renderer_total, False)
        self.cols['Time left'].add_attribute(renderer_total, 'text', 3)

        self.store = Gtk.ListStore(str, str, str, str, str)
        self.set_model(self.store)

        self.colors = colors

    def append_start(self):
        self.freeze_child_notify()
        self.store.clear()

    def append(self, show):
        # print('append', show)
        if show['status'] == 1:
            color = self.colors['is_airing']
        elif show['status'] == 3:
            color = self.colors['not_aired']
        else:
            color = None

        next_episode = '-'
        next_episode_in = '-'
        for extra in show['extra']:
            if 'Next Episode' == extra[0]:
                next_episode = extra[1]
            elif 'Next Episode In' == extra[0]:
                next_episode_in = extra[1]
        title_str = show['title']
        max_title_len = 50
        if len(title_str) > max_title_len:
            title_str = title_str[:max_title_len-2] + '...'
        row = [
            str(show['id']),
            str(title_str),
            str(next_episode),
            str(next_episode_in),
            color]
        # print('append', next_episode_in)
        self.store.append(row)

    def refresh_tree(self):
        print('thaw_child_notify')
        self.append_column(Gtk.TreeViewColumn(''))
        # self.freeze_child_notify()
        # self.thaw_child_notify()
        # self.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR))
        # self.get_window().set_cursor(None)

    def append_finish(self):
        self.thaw_child_notify()
        GLib.idle_add(self.refresh_tree)

        # self.store.set_sort_column_id(1, Gtk.SortType.ASCENDING)
