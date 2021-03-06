from json import JSONDecodeError
import jstyleson as json
from pathlib import Path
import os
import shutil
import sys

settings_filn = os.path.join(Path.home(), 'sublimeless_zk-settings.json')

def base_dir():
    if getattr(sys, 'frozen', False):
        # frozen
        base_dir = os.path.dirname(sys.executable)
    else:
        # unfrozen
        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    return base_dir


default_settings = json.loads(open(os.path.join(base_dir(), 'sublimeless_zk-settings.json'), mode='r', encoding='utf-8', errors='ignore').read())


def get_settings(raw=False, on_error=None):
    if not os.path.exists(settings_filn):
        # copy template
        src_path = os.path.join(base_dir(), 'sublimeless_zk-settings.json')
        shutil.copy2(src_path, settings_filn)
    with open(settings_filn,
              mode='r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
        if raw:
            return txt
        else:
            try:
                ret = json.loads(txt)
            except JSONDecodeError as e:
                ret = default_settings
                if on_error:
                    e.lineno = get_real_error_lineno(txt, e.lineno)
                    on_error(editor=None, jsonerror=e)
            return ret


def get_real_error_lineno(txt, lineno):
    logical_line_no = 1
    if lineno == 1:
        return 1
    line_index = 0   # just to be safe against the invariant
    for line_index, line in enumerate(txt.split('\n')):
        if line.strip().startswith('//'):
            continue
        logical_line_no += 1
        if logical_line_no == lineno:
            break
    return line_index + 1


def get_pandoc():
    settings = get_settings()
    guesses = [settings.get('path_to_pandoc', 'pandoc')]
    guesses.extend(['pandoc', '/usr/local/bin/pandoc', '/usr/bin/pandoc'])
    for attempt in guesses:
        if os.system(f'{attempt} --help') == 0:
            return attempt
    return None


# todo make QObject that emits settings changed / slot interface for eg Project class
