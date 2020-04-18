#!/usr/bin/python
import urwid
import rtv2util as util
import reddittv2 as reditt

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
    ('reveal focus', 'white', 'dark blue', 'standout'),
    ('data body', 'white', 'default'),
    ('data info', 'light gray', 'default', 'bold'),
    ('boxMessage', 'dark cyan', 'black'),
    ('boxError', 'dark red', 'black'),
    ('menu option', 'light green', 'black', 'standout')
]

reddittApplication = reditt.ReddittApplication()

# Disable mouse input
loop = urwid.MainLoop(reddittApplication, palette, handle_mouse=False).run()