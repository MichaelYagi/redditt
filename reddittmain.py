#!/usr/bin/python
import urwid
import re
import platform
import rtv2util as util
import reddittv2 as reditt

class Screen(urwid.raw_display.Screen):

    def write(self, data):
        if "Microsoft" in platform.platform():
            # replace urwid's SI/SO, which produce artifacts under WSL.
            # https://github.com/urwid/urwid/issues/264#issuecomment-358633735
            # Above link describes the change.
            data = re.sub("[\x0e\x0f]", "", data)
        super().write(data)

# Make ListBox elements selectable with window resize
class SelectableText(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        return reddittApplication.keypress(size,key)

# Gets a subset of the Submission List used for pagination
def getSubmissionTextList(currentIndex, submissionItems, sublistLimit):
    textList = util.CustomOrderedDict({})

    for index,(submissionId,output) in enumerate(submissionItems.items()):
        if index >= currentIndex and index < (currentIndex+sublistLimit):
            
            textList.append(submissionId,SelectableText(output))
        elif index >= (currentIndex+sublistLimit):
            break

    return textList

# Gets a subset of the Author Comment List used for pagination
def getAuthorCommentTextList(currentIndex, commentItems, sublistLimit):
    textList = util.CustomOrderedDict({})

    for index,(commentId,output) in enumerate(commentItems.items()):
        if index >= currentIndex and index < (currentIndex+sublistLimit):
            
            textList.append(commentId,SelectableText(output))
        elif index >= (currentIndex+sublistLimit):
            break

    return textList

# Colour palette used for various attributes
palette = [
    ('header', 'dark green', 'black'),
    ('reveal focus', 'yellow', 'default', 'standout'),
    ('data body', 'dark green', 'default'),
    ('data info', 'light gray', 'default', 'bold'),
    ('boxMessage', 'dark cyan', 'black'),
    ('boxError', 'dark red', 'black'),
    ('menu option', 'light green', 'black', 'standout')
]

reddittApplication = reditt.ReddittApplication()

screen = Screen()

# Disable mouse input
loop = urwid.MainLoop(reddittApplication, palette, screen=screen, handle_mouse=False).run()