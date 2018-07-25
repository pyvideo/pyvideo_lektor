#!/usr/bin/env python3
# coding: utf-8
"""Copy pyvideo data in lektor format and vice versa"""

import argparse
import json
import logging
import pathlib
import re

import jinja2
import pyaml
import better_exceptions  # export BETTER_EXCEPTIONS=1
better_exceptions.MAX_LENGTH = None

JSON_FORMAT_KWARGS = {
    'indent': 2,
    'separators': (',', ': '),
    'sort_keys': True,
}

# Real path of this same script
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / 'templates'


class Repository:
    """Pyvideo repository"""
    def __init__(self):
        self.events = {}
        self.event_filter = []

    def add_event_filter(self, event_names):
        """Add the names of the events to read"""
        logging.debug('%s.add_event_filter events: %s',
                      type(self).__name__, event_names)
        self.event_filter = event_names

    def get_events(self):
        """Return all event objects in repo"""
        return self.events

    def add_events(self, events):
        """Add pre-loaded event objects"""
        self.events = events

    def read_events(self):
        """Read events from disk"""
        events = self.read_event_list()
        for name, path in events:
            event = self.read_event(name, path)
            if event:
                self.events[name] = event

    def __err_msg(self, func_name):
        """NotImplementedError message construction"""
        return "Class {} doesn't implement {}()".format(
            self.__class__.__name__, func_name)

    def read_event_list(self):
        """Interface: Read the list of all events from disk"""
        raise NotImplementedError(self.__err_msg("read_event_list"))

    def read_event(self, event_name, event_path):
        """Interface: Read event from disk"""
        raise NotImplementedError(self.__err_msg("read_event"))

    @staticmethod
    def save_file(path, text):
        """Create a file in `path` with content `text`"""
        dir_path = path.parents[0]
        dir_path.mkdir(parents=True, exist_ok=True)
        with path.open(mode='w') as f_stream:
            f_stream.write(text)

    def save(self):
        """Dump all events to disk"""
        for event in self.events.values():
            event_path, event_text = self.event_save_data(event)
            self.save_file(event_path, event_text)

            for video in event.get_videos().values():
                video_path, video_text = self.video_save_data(event_path,
                                                              video)
                self.save_file(video_path, video_text)

    def event_save_data(self, event):
        """Interface: Data needed to save an event (path, text)"""
        raise NotImplementedError(self.__err_msg("event_save_data"))

    def video_save_data(self, event_path, video):
        """Interface: Data needed to save a video (path, text)"""
        raise NotImplementedError(self.__err_msg("video_save_data"))


class PyvideoRepo(Repository):
    """Pyvideo json repository"""

    def __init__(self, path):
        self.path = path
        super().__init__()

    def read_event_list(self):
        """Read the list of all disk events (name and path)"""
        event_paths = self.path.glob('*/category.json')
        return [(event_path.parts[-2], event_path.parents[0])
                for event_path in event_paths
                # Exclude .schemas/category.json
                if not event_path.parts[-2].startswith('.')]

    def read_event(self, event_name, event_path):
        """Read event from disk"""
        if self.event_filter:
            if event_name not in self.event_filter:
                return
        event_data = self.get_json(event_path / 'category.json')
        logging.debug('< \t %s', event_name)
        event = Event(event_name, event_data)
        for video_path in event_path.glob('videos/*.json'):
            video_name = video_path.stem
            video_data = self.get_json(video_path)
            logging.debug('< \t %s', video_path)
            event.add_video(video_name, video_data)
        self.events[event_name] = event

    def event_save_data(self, event):
        """Data needed to save an event (path, text)"""
        path = self.path / event.name / 'category.json'
        text = event.to_json()
        logging.debug('> \t %s', path)
        return path, text

    def video_save_data(self, event_path, video):
        """Data needed to save a video (path, text)"""
        event_dir = event_path.parents[0]
        path = event_dir / 'videos' / '{}.json'.format(video.name)
        text = video.to_json()
        logging.debug('> \t %s', path)
        return path, text

    @staticmethod
    def get_json(file_path):
        """Get data of json file"""
        with file_path.open() as f_stream:
            try:
                data = json.load(f_stream)
            except ValueError:
                print('Json syntax error in file {}'.format(file_path))
                raise
        return data


class Event:
    """Pyvideo Event metadata"""

    lektor_template = 'event.lr.j2'

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.videos = {}

    def add_video(self, name, data):
        """Add video to the event"""
        self.videos[name] = Video(name, data)

    def get_videos(self):
        """Get all event videos"""
        return self.videos

    def to_json(self):
        """Return event data in json format"""
        return json.dumps(self.data, **JSON_FORMAT_KWARGS) + '\n'

    def to_lektor(self):
        """Return event data in lektor format"""

        template_data = {}
        other_data = {}
        for key, value in self.data.items():
            if key in ['title', 'description']:
                template_data[key] = value
            else:
                other_data[key] = value
        if other_data:
            template_data['others'] = pyaml.dump(other_data,
                                                 string_val_style='|')

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(self.lektor_template)
        result = template.render(data=template_data)
        return result


class Video:
    """Pyvideo video metadata"""

    lektor_template = 'video.lr.j2'

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def to_json(self):
        """Return video data in json format"""
        return json.dumps(self.data, **JSON_FORMAT_KWARGS) + '\n'

    def to_lektor(self):
        """Return video data in lektor format"""

        (string_data, flow_text_data, flow_url_data, flow_video_data,
            other_data) = ({}, {}, {}, {}, {})
        for field, value in self.data.items():
            if field in ['description', 'thumbnail_url', 'title', 'recorded',
                         'copyright_text', 'duration', 'language']:
                string_data[field] = value
                # TODO: description is rst must replace "^---" for "----"
            elif field in ['speakers', 'tags']:
                flow_text_data[field] = value
            elif field == 'videos':
                for item in value:
                    if 'length' not in item:
                        item['length'] = None
                flow_video_data['videos'] = value
            elif field == 'related_urls':
                flow_url_data[field] = []
                for item in value:
                    if isinstance(item, str):
                        flow_url_data[field].append({
                            'url': item,
                            'label': '',
                            })
                    else:
                        flow_url_data[field].append(item)
            else:
                other_data[field] = value
        if other_data:
            string_data['others'] = pyaml.dump(other_data,
                                               string_val_style='|')

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(self.lektor_template)
        result = template.render(
            string_data=string_data,
            flow_text_data=flow_text_data,
            flow_url_data=flow_url_data,
            flow_video_data=flow_video_data,
            )
        return result


class LektorContent(Repository):
    """Pyvideo Lektor web contents"""

    def __init__(self, path):
        self.path = path
        super().__init__()

    def read_event_list(self):
        """Read the list of all events from disk"""
        event_paths = self.path.glob('content/events/*/contents.lr')
        return [(event_path.parts[-2], event_path.parents[0])
                for event_path in event_paths]

    def read_event(self, event_name, event_path):
        """Read event from disk"""
        if self.event_filter:
            if event_name not in self.event_filter:
                return
        event_data = self.get_lektor(event_path / 'contents.lr')
        logging.debug('< \t %s', event_name)
        event = Event(event_name, event_data)
        for video_path in event_path.glob('*/contents.lr'):
            video_name = video_path.parts[-2]
            video_data = self.get_lektor(video_path)
            logging.debug('< \t %s', video_path)
            event.add_video(video_name, video_data)
        self.events[event_name] = event

    def event_save_data(self, event):
        """Data needed to save an event (path, text)"""
        path = self.path / 'content' / 'events' / event.name / 'contents.lr'
        text = event.to_lektor()
        logging.debug('> \t %s', path)
        return path, text

    def video_save_data(self, event_path, video):
        """Data needed to save a video (path, text)"""
        event_dir = event_path.parents[0]
        path = event_dir / video.name / 'contents.lr'
        text = video.to_lektor()
        logging.debug('> \t %s', path)
        return path, text

    @staticmethod
    def get_lektor(file_path):
        """Get data of lektor file"""
        text = file_path.read_text()

        def _to_dict(text, level=3):
            pattern = r'(?:\r?\n|\A){}\r?\n\b'.format('-' * level)
            chunks = re.split(pattern, text)
            result = dict([
                re.split(r'\s*:\s*', chunk, maxsplit=1)
                for chunk
                in chunks
                if not chunk.startswith('_')])
            return result

        def _fix_data(lektor_data):
            def _to_int(text):
                if isinstance(text, str):
                    if text in ['None', '']:
                        return None
                    else:
                        return int(text)
                else:
                    return text

            if 'duration' in lektor_data and lektor_data['duration']:
                lektor_data['duration'] = _to_int(lektor_data['duration'])
            if 'videos' in lektor_data and lektor_data['videos']:
                for video in lektor_data['videos']:
                    if 'length' in video and video['length']:
                        if video['length'] == 'None':
                            del video['length']
                        else:
                            video['length'] = _to_int(video['length'])
            if 'related_urls' in lektor_data:
                for num, url_data in enumerate(lektor_data['related_urls']):
                    if url_data['label'] == '':
                        lektor_data['related_urls'][num] = url_data['url']
                    # ~ else:
                    # ~     url_data['label'] = url_data['text']
                    # ~     del url_data['text']
            for list_var in ['tags', 'speakers', 'related_urls']:
                if list_var in lektor_data:
                    if lektor_data[list_var] == "":
                        lektor_data[list_var] = []
            if 'others' in lektor_data:
                other_data = pyaml.yaml.safe_load(lektor_data['others'])
                lektor_data.update(other_data)
                del lektor_data['others']
            return lektor_data

        main_data = _to_dict(text)
        for k, v in main_data.items():
            if v.startswith('####'):
                pattern = r'(?:\r?\n|\A){}\r?\n\b'.format('#### .* ####')
                chunks = re.split(pattern, v)[1:]
                if '----' in v:  # FIX edge case text with dashes
                    main_data[k] = [_to_dict(chunk, level=4)
                                    for chunk in chunks]
                else:
                    main_data[k] = [re.split(r'\s*:\s*', chunk, maxsplit=1)[1]
                                    for chunk in chunks]
            elif v == 'None':
                main_data[k] = None

        result = _fix_data(main_data)
        return result


def main():
    """Convert pyvideo json file(s) to lektor and vice versa"""
    parser = argparse.ArgumentParser()
    parser.add_argument("pyvideo_path", help="path to pyvideo data repository")
    parser.add_argument(
        "lektor_path", help="path to pyvideo in lektor directory")
    parser.add_argument(
        "-e",
        "--events",
        default='',
        help="event directory names (split by commas)")
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action='store_true',
        help="increase output verbosity")
    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action='store_true',
        help="stop script for debugging")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pyvideo_to_lektor", action="store_true")
    group.add_argument("--lektor_to_pyvideo", action="store_true")

    args = parser.parse_args()
    if args.debug:
        import ipdb
        ipdb.set_trace()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    pyvideo_path = pathlib.Path(args.pyvideo_path)
    pyvideo = PyvideoRepo(pyvideo_path)

    lektor_path = pathlib.Path(args.lektor_path)
    lektor = LektorContent(lektor_path)

    event_filter = [event.strip() for event in args.events.split(',')]

    if args.pyvideo_to_lektor:
        origin, destination = pyvideo, lektor
    if args.lektor_to_pyvideo:
        origin, destination = lektor, pyvideo

    if args.events:
        origin.add_event_filter(event_filter)
    origin.read_events()
    destination.add_events(origin.get_events())
    destination.save()


if __name__ == '__main__':
    main()
