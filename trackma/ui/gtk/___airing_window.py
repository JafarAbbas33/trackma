
import requests
import datetime
import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AiringWindow(Gtk.Window):
    def __init__(self, show_dict):
        
        Gtk.Window.__init__(self)
        sw = Gtk.ScrolledWindow()
        self.set_position(Gtk.WindowPosition.CENTER)

        self._showdict = show_dict
        self.showlist = AiringTreeView()
        self.showlist.get_selection().connect("changed", self._on_selection_changed)
        self.showlist.set_size_request(250, 350)
        self.showlist.show()

        # self.showlist.set_margin_start(30)
        # self.showlist.set_margin_end(30)
        # self.add(self.showlist)

        sw.set_min_content_height(600)
        sw.set_min_content_width(700)
        sw.add(self.showlist)
        self.add(sw)

        for _show in self._showdict.values():
            self.showlist.append(_show)
        # self.info = ShowInfoBox(orientation=Gtk.Orientation.VERTICAL)
        # self.info.set_size_request(200, 350)
        # self.info.show()

    def _on_selection_changed(self, selection):
        # Get selected show ID
        return
        (tree_model, tree_iter) = selection.get_selected()
        if not tree_iter:
            return

        self._selected_show = int(tree_model.get(tree_iter, 0)[0])
        if self._selected_show in self._showdict:
            self.info.load(self._showdict[self._selected_show])
            in_user_list = self._showdict[self._selected_show]['extra'][-1][1]
            if in_user_list == 'No':
                self.btn_add_show.set_sensitive(True)
            else:
                self.btn_add_show.set_sensitive(False)

class AiringTreeView(Gtk.TreeView):
    shows_viewport = Gtk.Template.Child()
    def __init__(self):
        Gtk.TreeView.__init__(self)

        self.cols = dict()
        i = 1
        for name in ('Title', 'Episode', 'Time left'):
            self.cols[name] = Gtk.TreeViewColumn(name)
            self.cols[name].set_sort_column_id(i)
            self.append_column(self.cols[name])
            i += 1

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


    def append_start(self):
        self.freeze_child_notify()
        self.store.clear()

    def append(self, show):
        # print(show)

        next_ep_number = '0'  
        time_left = 'None'
        title_str = show['title']
        if show.get('timeUntilAiring'):
            next_ep_time = show.get('timeUntilAiring')
            next_ep_number = show['nextAiringEpisode'] 
            if next_ep_time and next_ep_number:
                max_title_len = 50
                # if len(title_str) > max_title_len:
                #     title_str = title_str[:max_title_len-2] + '...'
                # time_diff = str(show.get('next_ep_time') - datetime.datetime.now())
                time_diff = str(next_ep_time)
                next_airing_status_str = f'[E{next_ep_number} in {":".join(time_diff.split(":")[:-1]) if time_diff.count(":") == 2 else time_diff}]'
                time_left = ":".join(time_diff.split(":")[:-1]) if time_diff.count(":") == 2 else time_diff
                # title_str =  f'{title_str} {next_airing_status_str}'

        row = [
            str(show['id']),
            str(title_str),
            # str(show['type']),
            str(next_ep_number),
            time_left,
            # str(show['total']),
            # next_airing_status_str,
            None]
        self.store.append(row)

    def append_finish(self):
        self.thaw_child_notify()
        self.store.set_sort_column_id(1, Gtk.SortType.ASCENDING)

def show():
    return {
        'id':           0,
        'title':        '',
        'url':          '',
        'aliases':      [],
        'my_id':        None,
        'my_progress':  0,
        'my_status':    1,
        'my_score':     0,
        'my_start_date':  None,
        'my_finish_date': None,
        'type':         0,
        'status':       0,
        'total':        0,
        'start_date':   None,
        'end_date':     None,
        'image':        '',
        'image_thumb':  '',
        'queued':       False,
    }


#     def fetch_list(self):
#         self.check_credentials()
#         self.msg.info('Downloading list...')

#         query = '''query ($id: Int!, $listType: MediaType) {
#   MediaListCollection (userId: $id, type: $listType) {
#     lists {
#       name
#       isCustomList
#       status
#       entries {
#         ... mediaListEntry
#       }
#     }
#     user {
#       mediaListOptions {
#         scoreFormat
#       }
#     }
#   }
# }

# fragment mediaListEntry on MediaList {
#   id
#   score
#   progress
#   startedAt { year month day }
#   completedAt { year month day }
#   media {
#     id
#     title { userPreferred romaji english native }
#     synonyms
#     coverImage { large medium }
#     format
#     status
#     chapters episodes
#     nextAiringEpisode { airingAt episode }
#     startDate { year month day }
#     endDate { year month day }
#     siteUrl
#   }
# }'''
#         variables = {'id': self.userid, 'listType': self.mediatype.upper()}
#         data = self._request(query, variables)['data']['MediaListCollection']

#         showlist = {}

#         if not data['lists']:
#             # No lists returned so no need to continue
#             return showlist

#         # Handle different score formats provided by Anilist
#         self.scoreformat = data['user']['mediaListOptions']['scoreFormat']
#         self._apply_scoreformat(self.scoreformat)

#         self._set_userconfig('scoreformat_' + self.mediatype, self.scoreformat)
#         self._emit_signal('userconfig_changed')

#         for remotelist in data['lists']:
#             my_status = remotelist['status']

#             if my_status not in self.media_info()['statuses']:
#                 continue
#             if remotelist['isCustomList']:
#                 continue  # Maybe do something with this later
#             for item in remotelist['entries']:
#                 show = utils.show()
#                 media = item['media']
#                 showid = media['id']
#                 showdata = {
#                     'my_id': item['id'],
#                     'id': showid,
#                     'title': media['title']['userPreferred'],
#                     'aliases': self._get_aliases(media),
#                     'type': self._translate_type(media['format']),
#                     'status': self._translate_status(media['status']),
#                     'my_progress': self._c(item['progress']),
#                     'my_status': my_status,
#                     'my_score': self._c(item['score']),
#                     'total': self._c(media[self.total_str]),
#                     'image': media['coverImage']['large'],
#                     'image_thumb': media['coverImage']['medium'],
#                     'url': media['siteUrl'],
#                     'start_date': self._dict2date(media['startDate']),
#                     'end_date': self._dict2date(media['endDate']),
#                     'my_start_date': self._dict2date(item['startedAt']),
#                     'my_finish_date': self._dict2date(item['completedAt']),
#                 }
#                 if media['nextAiringEpisode']:
#                     showdata['next_ep_number'] = media['nextAiringEpisode']['episode']
#                     showdata['next_ep_time'] = self._int2date(
#                         media['nextAiringEpisode']['airingAt'])
#                 show.update({k: v for k, v in showdata.items() if v})
#                 showlist[showid] = show
#         return showlist

#     args_SaveMediaListEntry = {
#         'id': 'Int',                         # The list entry id, required for updating
#         'mediaId': 'Int',                    # The id of the media the entry is of
#         'status': 'MediaListStatus',         # The watching/reading status
#         'scoreRaw': 'Int',                   # The score of the media in 100 point
#         # The amount of episodes/chapters consumed by the user
#         'progress': 'Int',
#         'startedAt': 'FuzzyDateInput',       # When the entry was started by the user
#         'completedAt': 'FuzzyDateInput',     # When the entry was completed by the user
#     }

def _parse_info(item):
    info = show()
    showid = item['id']

    if item['media']['title'].get('english'):
        title = item['media']['title'].get('english')
    else:
        title = item['media']['title'].get('userPreferred')
    show_info = {
        'id': showid,
        'title': title,
        # 'image': item['coverImage']['large'],
        # 'image_thumb': item['coverImage']['medium'],
        # 'url': item['siteUrl'],
        'extra': [
            ('Synopsis',        item.get('description')),
            ('Type',            item.get('format')),
            ('Average score',   item.get('averageScore')),
            # ('Status',          item['status']),
        ]
    }
    # print('='*80)
    # print(item.get('timeUntilAiring'))
    if item.get('timeUntilAiring'):
        show_info['nextAiringEpisode'] = item.get('episode')
        show_info['timeUntilAiring'] = datetime.timedelta(seconds=item.get('timeUntilAiring'))
    info.update(show_info)
    return info


query = '''
query AiringScheduleQuery(
    $page: Int,
    $airingAtGreater: Int,
    $airingAtLesser: Int
) {
    Page(page: $page) {
        pageInfo {
            total
            perPage
            currentPage
            lastPage
            hasNextPage
        }
        airingSchedules(
            airingAt_greater: $airingAtGreater,
            airingAt_lesser: $airingAtLesser
        ) {
            id
            airingAt
            timeUntilAiring
            episode
            media {
                id
                title {
                    english,
                    userPreferred
                }
                season
                seasonYear
                bannerImage
                isAdult
                mediaListEntry {
                    status
                }
            }
        }
    }
}
'''

def gett():
    shows_list = []
    starting_point = int(datetime.datetime.now().timestamp() - datetime.timedelta(days=1).total_seconds())
    ending_point = int(datetime.datetime.now().timestamp() + datetime.timedelta(days=1).total_seconds())

    print('Starting point:', starting_point)
    print('Ending point:', ending_point)

    page = 1
    max_pages = 4
    has_next_page = True
    while has_next_page:
        if page > max_pages:
            print(f'Max pages exceeded! Allowed pages: {max_pages}')
            shows_list.extend([{'id': 0, 'media': {'title': {'english': f'Breaking because requests excceded! Allowed pages: {max_pages}'}}}])
            break
        variables = {
            'page': page,
            'airingAtGreater': starting_point,
            'airingAtLesser': ending_point
        }

        url = 'https://graphql.anilist.co'

        print('Getting page:', page)
        response = requests.post(url, json={'query': query, 'variables': variables})
        # print(response.text)
        json_response = json.loads(response.text)
        shows_list.extend(json_response['data']['Page']['airingSchedules'])
        if not json_response['data']['Page']['pageInfo']['hasNextPage']:
            break
        page += 1

    return shows_list

def main():
    # json_response = json.loads('''{"data":{"Page":{"pageInfo":{"total":32,"perPage":50,"currentPage":1,"lastPage":1,"hasNextPage":false},"airingSchedules":[{"id":346999,"airingAt":1677310200,"timeUntilAiring":-81223,"episode":1170,"media":{"id":966,"title":{"userPreferred":"Crayon Shin-chan"},"season":"SPRING","seasonYear":1992,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/966-J5CwLLTBs4OO.jpg","isAdult":false,"mediaListEntry":null}},{"id":346649,"airingAt":1677313800,"timeUntilAiring":-77623,"episode":21,"media":{"id":139630,"title":{"userPreferred":"Boku no Hero Academia 6"},"season":"FALL","seasonYear":2022,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/139630-XLc90c6CJjZv.jpg","isAdult":false,"mediaListEntry":null}},{"id":346115,"airingAt":1677315600,"timeUntilAiring":-75823,"episode":1075,"media":{"id":235,"title":{"userPreferred":"Meitantei Conan"},"season":"WINTER","seasonYear":1996,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/235-MTmiz0uB0fMd.jpg","isAdult":false,"mediaListEntry":null}},{"id":351170,"airingAt":1677317100,"timeUntilAiring":-74323,"episode":20,"media":{"id":139092,"title":{"userPreferred":"Mairimashita! Iruma-kun 3"},"season":"FALL","seasonYear":2022,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/139092-gcuDazzfT0uC.jpg","isAdult":false,"mediaListEntry":null}},{"id":342929,"airingAt":1677330000,"timeUntilAiring":-61423,"episode":8,"media":{"id":152523,"title":{"userPreferred":"Kaiko sareta Ankoku Heishi (30-dai) no Slow na Second Life"},"season":"WINTER","seasonYear":2023,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":343310,"airingAt":1677331800,"timeUntilAiring":-59623,"episode":7,"media":{"id":125869,"title":{"userPreferred":"Hikari no Ou"},"season":"WINTER","seasonYear":2023,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":344248,"airingAt":1677331800,"timeUntilAiring":-59623,"episode":8,"media":{"id":143338,"title":{"userPreferred":"Otonari no Tenshi-sama ni Itsunomanika Dame Ningen ni Sareteita Ken"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/143338-d0AqJzRUQCgk.jpg","isAdult":false,"mediaListEntry":null}},{"id":343763,"airingAt":1677333600,"timeUntilAiring":-57823,"episode":8,"media":{"id":151040,"title":{"userPreferred":"TRIGUN STAMPEDE"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/151040-1auPdaGqDGYd.jpg","isAdult":false,"mediaListEntry":null}},{"id":349866,"airingAt":1677335400,"timeUntilAiring":-56023,"episode":6,"media":{"id":154969,"title":{"userPreferred":"UniteUp!"},"season":"WINTER","seasonYear":2023,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":349892,"airingAt":1677337200,"timeUntilAiring":-54223,"episode":20,"media":{"id":142481,"title":{"userPreferred":"Yowamushi Pedal: LIMIT BREAK"},"season":"FALL","seasonYear":2022,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/142481-bmz1tYLZOJ9u.jpg","isAdult":false,"mediaListEntry":null}},{"id":350895,"airingAt":1677337200,"timeUntilAiring":-54223,"episode":5,"media":{"id":145665,"title":{"userPreferred":"NieR:Automata Ver1.1a"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/145665-pbXoaav2n51N.jpg","isAdult":false,"mediaListEntry":null}},{"id":349571,"airingAt":1677340800,"timeUntilAiring":-50623,"episode":9,"media":{"id":140596,"title":{"userPreferred":"Ijiranaide, Nagatoro-san 2nd Attack"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/140596-4aOdEfE8FMHj.jpg","isAdult":false,"mediaListEntry":null}},{"id":346397,"airingAt":1677342600,"timeUntilAiring":-48823,"episode":20,"media":{"id":137822,"title":{"userPreferred":"Blue Lock"},"season":"FALL","seasonYear":2022,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/137822-oevspckMGLuY.jpg","isAdult":false,"mediaListEntry":null}},{"id":349849,"airingAt":1677342600,"timeUntilAiring":-48823,"episode":8,"media":{"id":144553,"title":{"userPreferred":"Saikyou Onmyouji no Isekai Tenseiki"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/144553-V8iUimFSq5mO.jpg","isAdult":false,"mediaListEntry":null}},{"id":343669,"airingAt":1677344400,"timeUntilAiring":-47023,"episode":8,"media":{"id":152765,"title":{"userPreferred":"Rougo ni Sonaete Isekai de 8-manmai no Kinka wo Tamemasu"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/152765-tMtUutoAagX7.jpg","isAdult":false,"mediaListEntry":null}},{"id":349360,"airingAt":1677344880,"timeUntilAiring":-46543,"episode":8,"media":{"id":142853,"title":{"userPreferred":"Tokyo Revengers: Seiya Kessen-hen"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/142853-65n3FTeSiyA6.jpg","isAdult":false,"mediaListEntry":null}},{"id":347381,"airingAt":1677364200,"timeUntilAiring":-27223,"episode":47,"media":{"id":142842,"title":{"userPreferred":"Yu\u2606Gi\u2606Oh! Go Rush!!"},"season":"SPRING","seasonYear":2022,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":347700,"airingAt":1677367800,"timeUntilAiring":-23623,"episode":25,"media":{"id":153412,"title":{"userPreferred":"Duel Masters WIN"},"season":"SUMMER","seasonYear":2022,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/153412-JqIScKJh2gZ3.jpg","isAdult":false,"mediaListEntry":null}},{"id":349369,"airingAt":1677367800,"timeUntilAiring":-23623,"episode":4,"media":{"id":157883,"title":{"userPreferred":"Hirogaru Sky! Precure"},"season":"WINTER","seasonYear":2023,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/157883-u3gE5LKKXwb3.jpg","isAdult":false,"mediaListEntry":null}},{"id":350602,"airingAt":1677369600,"timeUntilAiring":-21823,"episode":65,"media":{"id":137309,"title":{"userPreferred":"Digimon Ghost Game"},"season":"FALL","seasonYear":2021,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/137309-FY8EoCpLsbHJ.jpg","isAdult":false,"mediaListEntry":null}},{"id":346436,"airingAt":1677371400,"timeUntilAiring":-20023,"episode":1053,"media":{"id":21,"title":{"userPreferred":"ONE PIECE"},"season":"FALL","seasonYear":1999,"bannerImage":"https:\/\/s4.anilist.co\/file\/anilistcdn\/media\/anime\/banner\/21-wf37VakJmZqs.jpg","isAdult":false,"mediaListEntry":null}},{"id":347640,"airingAt":1677371400,"timeUntilAiring":-20023,"episode":47,"media":{"id":145968,"title":{"userPreferred":"Cap Kakumei Bottleman DX"},"season":"SPRING","seasonYear":2022,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":347814,"airingAt":1677372300,"timeUntilAiring":-19123,"episode":21,"media":{"id":155526,"title":{"userPreferred":"Punirunes"},"season":"FALL","seasonYear":2022,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":328071,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":248,"media":{"id":122521,"title":{"userPreferred":"Jueshi Wu Hun"},"season":"FALL","seasonYear":2020,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":336097,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":33,"media":{"id":137728,"title":{"userPreferred":"Dou Po Cangqiong: Nian Fan"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":342805,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":30,"media":{"id":157181,"title":{"userPreferred":"Wan Jie Zhizun"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":344712,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":38,"media":{"id":155723,"title":{"userPreferred":"Wushen Zhuzai: Da Wei Pian"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":345626,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":92,"media":{"id":146541,"title":{"userPreferred":"Xinghe Zhizun 2"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":348542,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":21,"media":{"id":159453,"title":{"userPreferred":"Fangyu Quan Kai"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":348894,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":18,"media":{"id":153492,"title":{"userPreferred":"Sanguo Yanyi 3"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":349314,"airingAt":1677376800,"timeUntilAiring":-14623,"episode":14,"media":{"id":147133,"title":{"userPreferred":"Jian Yu Chuanqi 2"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}},{"id":348961,"airingAt":1677380400,"timeUntilAiring":-11023,"episode":5,"media":{"id":159599,"title":{"userPreferred":"Fanren Xiu Xian Zhuan: Fanren Feng Qi Tian Nan Chongzhi Ban"},"season":null,"seasonYear":null,"bannerImage":null,"isAdult":false,"mediaListEntry":null}}]}}}''')
    # episode_list = json_response['data']['Page']['airingSchedules']
    episode_list = gett()

    print('Total episodes:', len(episode_list))
    # print(json.dumps(json_response, indent=4))
    show_dict = {}
    for _show in episode_list:
        parsed_show = _parse_info(_show)
        # win.showlist.append(parsed_show)
        show_dict[parsed_show['id']] = parsed_show


    win = AiringWindow(show_dict)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
