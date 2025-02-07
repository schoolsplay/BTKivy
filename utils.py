import builtins
import gettext
import locale
import logging
import os

LOCALEDIR = 'locale'
# These will be changed by a call to set_locale in main.py
LANG = 'en'
LOCALE_RTL = None

module_logger = logging.getLogger("bt.utils")

def set_locale(lang=None):
    """Used by the core to set the locale.
    """
    module_logger.debug(f"set_locale called with {lang}")
    global LOCALE_RTL, LANG
    txt = ""
    try:
        if not lang or lang == 'system':
            try:
                lang, enc = locale.getdefaultlocale()
                lang = "%s.%s" % (lang, enc.upper())
            except ValueError as info:
                module_logger.error(f"set_locale: {info}")
                lang = 'en_US.utf8'
        languages = [lang]
        lang, enc = lang.split('.')
        lang = f"{lang}.{enc.lower()}"
        locale.setlocale(locale.LC_ALL, (lang.split('.')))
        module_logger.info(f"set_locale: Setting btkivy locale to '{lang}' modir: {LOCALEDIR}")
        gettext.textdomain('btkivy')
        lang_trans = gettext.translation('btkivy',
                                         localedir=LOCALEDIR,
                                         languages=languages)
        gettext.install('btkivy', LOCALEDIR)
        os.environ['LANG'] = lang
        builtins.__dict__['_'] = lang_trans.gettext
    except Exception as info:
        txt = f"Cannot set language to '{lang}' \n switching to English"
        module_logger.error(f"set_locale: {info}, {txt}")
        builtins.__dict__['_'] = lambda x: x
        lang = 'en_US.utf8'
    else:
        lang = lang.split('@')[0]

    # This is to signal that we running under a RTL locale like Hebrew or Arabic
    # Only Hebrew and Arabic is supported until now
    if lang[:2] in ['he', 'ar']:
        LOCALE_RTL = True
    else:
        LOCALE_RTL = False
    LANG = lang
    module_logger.info("set_locale: Locale set to %s, RTL set to %s" % (LANG, LOCALE_RTL))
    return lang, LOCALE_RTL
