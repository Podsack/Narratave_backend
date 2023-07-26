import functools
import json
import os

from django.conf import settings

from Podsack.decorators.singleton import Singleton


class AppLanguageLoader(metaclass=Singleton):
    app_languages = None

    def __init__(self):
        if self.app_languages is None:
            path = os.path.join(settings.STATIC_ROOT, 'json', 'app_languages.json')
            with open(path) as app_lang_file:
                self.app_languages = json.load(app_lang_file)

    def get_app_language(self, country, state):
        current_langs = self.app_languages.get(country)
        set_priority_by_state = functools.partial(self.sort_by_state, state=state)

        list(map(set_priority_by_state, current_langs))
        sorted_app_langs = sorted(current_langs, key=lambda x: x['priority'])

        return list(map(self.map_to_response, sorted_app_langs))

    def sort_by_state(self, lang_config, state):
        if state.lower() in lang_config['states']:
            lang_config['priority'] = 1
        elif 'any' in lang_config['states']:
            lang_config['priority'] = 2
        else:
            lang_config['priority'] = 3

        return self.map_to_response(lang=lang_config)

    @staticmethod
    def map_to_response(lang):
        return {'localized_lang': lang.get('localizedLanguage'), 'code': lang.get('code')}
