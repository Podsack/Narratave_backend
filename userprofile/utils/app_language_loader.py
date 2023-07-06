import functools
import json

from django.templatetags.static import static
from functools import partial

from Podsack.decorators.singleton import singleton


# @singleton
class AppLanguageLoader:
    app_languages = None

    def __init__(self):
        if self.app_languages is None:
            path = static('json/app_languages.json')
            with open(path) as app_lang_file:
                self.app_languages = json.load(app_lang_file)

    def get_app_language(self, country, state):
        current_langs = self.app_languages.get(country)
        set_priority_by_state = functools.partial(self.assign_priority, state=state)

        list(map(set_priority_by_state, current_langs))
        sorted_app_langs = sorted(current_langs, key=lambda x: x['priority'])

        return [d['lang'] for d in sorted_app_langs]

    @classmethod
    def assign_priority(cls, lang_config, state):
        if state.lower() in lang_config['states']:
            lang_config['priority'] = 1
        elif 'any' in lang_config['states']:
            lang_config['priority'] = 2
        else:
            lang_config['priority'] = 3

        return lang_config
