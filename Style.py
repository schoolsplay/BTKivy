import os

__author__ = 'stas Zytkiewicz stas@childsplay.mobi'

# module to hold various constants which are used in the project
# to give designers a way to style the stuff as Kivy doesn't
# have theme support yet.
# Naming of the classes are Style<kivy widget name>
# Fontcolors must be in hex as they are used as markup.
# Colors for backgrounds and images must be tuples with floats 0-1
from textwrap import dedent


class StyleBase:
    # You can change this to a absolute path to use your own fonts.
    # For example: fontname = 'lib/SPData/fonts/Aldo.ttf'
    fontname = 'Roboto'
    fontname_mono = 'RobotoMono-Regular'
    fontcolor_list = (0.23, 0.24, 0.24, 1)
    fontcolor = "#3a3d3d"
    fontsize = 22
    backcolor = [0.94, 0.94, 0.94, 1]  # Provides a a bg to contrast with fontcolor

    # title font stuff
    titlecolor = '#b4b4b4'
    titlesize = 24
    titletexttags = "[font=%s][size=%s][color=%s]" % (
        fontname, titlesize, titlecolor)+ "%s[/color][/size][/font]"

    # Don't change this
    texttags = "[font=%s][size=%s][color=%s]" % (
        fontname, fontsize, fontcolor) + "%s[/color][/size][/font]"

    separator_color = (0.28, 0.47, 1, 0)

class MainMenuStyle(StyleBase):
    """
    Beware that this is a kv language class so some sizes and colors are in a
    different format then the super class.
    """
    def __init__(self):

        self.fontcolor = (0.23, 0.24, 0.24, 1)
        self.grey1 = (0.4, 0.4, 0.4, 1)
        self.fontsize = '18sp'



if __name__ == '__main__':
    SD = StyleBase
    print((dir(SD)))
