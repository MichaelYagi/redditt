#!/usr/bin/python
import urwid
import praw
from collections import OrderedDict
from datetime import datetime
import reddittmain as main

SUBMISSION_VIEW = "submissions"
COMMENT_VIEW = "comments"
COMMENT_SUBMISSION_VIEW = "commentSubmission"
AUTHOR_COMMENT_VIEW = "authorComments"

HEADER_PALETTE = "header"
FOOTER_PALETTE = "footer"
FOCUS_PALETTE = "reveal focus"
DATA_BODY_PALETTE = "data body"
DATA_INFO_PALETTE = "data info"
DATA_INFO_SELECT_PALETTE = "data info bold"
DATA_INFO_WARNING = "data info warning"
DIALOG_MESSAGE_PALETTE = "boxMessage"
DIALOG_ERROR_PALETTE = "boxError"
MENU_OPTION_PALETTE = "menu option"

DIALOG_USER_TITLE = "User"
DIALOG_SUBREDDIT_TITLE = "Subreddit"
DIALOG_REPLY_TITLE = "Reply"
DIALOG_COMMENT_TITLE = "Comment"

NSFW_TEXT = "NSFW"
SPOILERS_TEXT = "SPOILERS"
STICKIED_TEXT = "STICKIED"
SUBMISSION_SUBREDDIT_LJUST = 40
SUBMISSION_AUTHOR_LJUST = 24
SUBMISSION_POINTS_LJUST = 20

COMMENT_OFFSET = 3

# Dialog Window
class DialogComponents():
    def __init__(self):
        self.body = []
        self.message = urwid.Text("")
        self.error = urwid.Text("")
        self.form_fields = []
        self.content = []
        self.title = ""

    def create_form(self, title, form_fields, okbutton, cancelbutton):
        self.title = title
        self.form_fields.extend(form_fields)
        self.body.extend([urwid.Text(self.title), urwid.Divider()])
        self.body.extend(form_fields)
        message = urwid.AttrMap(self.message, DIALOG_MESSAGE_PALETTE)
        self.body.append(message)
        error = urwid.AttrMap(self.error, DIALOG_ERROR_PALETTE)
        self.body.append(error)
        self.body.append(okbutton)
        if cancelbutton is not None:
            self.body.append(cancelbutton)
        self.content = urwid.ListBox(urwid.SimpleFocusListWalker(self.body))
        return self.content

    def set_message(self, message):
        self.message.set_text(message)

    def set_error(self, message):
        self.error.set_text(message)

    def get_inputs(self):
        return self.form_fields

    def get_title(self):
        return self.title

# Appends dictionary elements and preserves order
class CustomOrderedDict(OrderedDict):
    def append(self, key, value):
        # root = self._OrderedDict__root
        # last = root[0]
 
        if key in self:
            raise KeyError
        else:
            # root[0] = last[1] = self._OrderedDict__map[key] = [last, root, key]
            # dict.__setitem__(self, key, value)
            self.update({key:value})
            self.move_to_end(key,last=True)

# Redditt class
class Redditt():
    def __init__(self):
        self.instance = praw.Reddit(
            'user',
            user_agent='reddit terminal:v2 (by /u/dipdip)'
        )
        
        self.username = self.instance.config.username
        self.submission = None
        self.comment = None

    def getRedditInstance(self):
        return self.instance

    # Get submissions by subreddit type
    def getSubList(self,subreddit,listLimit,type):
        sub = self.instance.subreddit(subreddit) 
        if type == "hot":
            sublist = sub.hot(limit=listLimit)
        elif type == "new":
            sublist = sub.new(limit=listLimit)
        elif type == "rising":
            sublist = sub.rising(limit=listLimit)
        elif type == "controversial":
            sublist = sub.controversial(time_filter="all",limit=listLimit)
        elif type == "top":
            sublist = sub.top(time_filter="all",limit=listLimit)
        else:
            sublist = sub.hot(limit=listLimit)

        return sublist

    def setSubmission(self, submissionId):
        self.submission = self.instance.submission(id=submissionId)

    def setComment(self, commentId):
        self.comment = self.instance.comment(id=commentId)

    def getSubmission(self):
        return self.submission

    def getComment(self):
        return self.comment

    def getUsername(self):
        return self.username

    def getSubmissionComments(self,sort):
        self.submission.comment_sort = sort
        return self.submission.comments

# Format UTC string
def datetime_from_utc_to_local(utc_datetime):
    return datetime.utcfromtimestamp(int(utc_datetime)).strftime('%Y-%m-%d %H:%M:%S')

# Creates a list of author comment texts used for display, keyed by submission ID
def createAuthorCommentList(author, submissionListLimit):
    subItems = CustomOrderedDict({})
    
    for index, comment in enumerate(author.comments.new(limit=submissionListLimit)):
        # Comment
        body = comment.body + "/n"

        # Points
        points = str(comment.score) + " point"
        if comment.score != 1:
            points +=  "s"

        # Comment time
        commentTime = datetime_from_utc_to_local(comment.created_utc)

        # Subreddit
        subreddit = comment.subreddit.display_name

        output =  [body + "\n",(DATA_INFO_PALETTE, points.ljust(20) + "r/" + subreddit.ljust(20) + commentTime + "\n")]
        subItems.append(comment.id, output)

    return subItems

# Creates a list of submission texts used for display, keyed by submission ID
def createSubmissionsList(submissions):
    subItems = CustomOrderedDict({})
    
    for index, submission in enumerate(submissions):
        title = submission.title + "\n"
        
        # Subreddit
        subreddit = "r/" + submission.subreddit.display_name
        nsfw = ""
        nsfwText = ""
        spoilers = ""
        spoilersText = ""
        stickied = ""
        stickiedText = ""
        upvote = ""
        downvote = ""
        if submission.stickied:
            stickiedText = " " + STICKIED_TEXT
            stickied = (DATA_INFO_SELECT_PALETTE, stickiedText)
        if submission.over_18:
            nsfwText = " " + NSFW_TEXT
            nsfw = (DATA_INFO_WARNING, nsfwText)
        if submission.spoiler:
            spoilersText = " " + SPOILERS_TEXT
            spoilers = (DATA_INFO_WARNING, spoilersText)
        if submission.likes is not None:
            if submission.likes:
                upvote = " " + u"\u2191"
            elif not submission.likes:
                downvote = " " + u"\u2193"
        leftJustification = SUBMISSION_SUBREDDIT_LJUST - len(subreddit+stickiedText+nsfwText+spoilersText+upvote+downvote)
        subreddit = [subreddit, stickied, nsfw, spoilers, upvote, downvote.ljust(leftJustification)]
                
        # Author
        author = ""
        if hasattr(submission.author, 'name'):
            author = "u/" + submission.author.name

        # Points
        pointString = " " + str(submission.score) + " point"
        if submission.score != 1:
            pointString += "s"
        
        # Comment count
        commentCount = " " + str(submission.num_comments) + " comment"
        if submission.num_comments != 1:
            commentCount += "s"

        footer = [subreddit, author.ljust(SUBMISSION_AUTHOR_LJUST), pointString.ljust(SUBMISSION_POINTS_LJUST), commentCount + "\n"]
        
        # highlighted focus color not fully transparent!!
        output = [title,(DATA_INFO_PALETTE, footer)]
        subItems.append(submission.id, output)

    return subItems

# Get menu items for header
def getMenuItems(viewType):
    if viewType == COMMENT_VIEW:
        return [
            (MENU_OPTION_PALETTE, '[b]'), 'est ',
            (MENU_OPTION_PALETTE, '[n]'), 'ew ',
            (MENU_OPTION_PALETTE, '[c]'), 'ontroversial ',
            (MENU_OPTION_PALETTE, '[t]'), 'op\n',
            (MENU_OPTION_PALETTE, '[u]'), 'pvote ',
            (MENU_OPTION_PALETTE, '[d]'), 'ownvote clear',
            (MENU_OPTION_PALETTE, '[v]'), 'ote co',
            (MENU_OPTION_PALETTE, '[m]'), 'ment ',
            (MENU_OPTION_PALETTE, '[r]'), 'eply ',
            (MENU_OPTION_PALETTE, '[a]'), 'uthor\n',
            (MENU_OPTION_PALETTE, '[s]'), 'croll top ',
            (MENU_OPTION_PALETTE, '[p]'), 'revious ne',
            (MENU_OPTION_PALETTE, '[x]'), 't bac',
            (MENU_OPTION_PALETTE, '[k]'), ' ',
            (MENU_OPTION_PALETTE, '[l]'), 'ookup user ',
            (MENU_OPTION_PALETTE, '[q]'), 'uit\n\n',
        ]
    elif viewType == COMMENT_SUBMISSION_VIEW:
        return [
            (MENU_OPTION_PALETTE, '[b]'), 'est ',
            (MENU_OPTION_PALETTE, '[n]'), 'ew ',
            (MENU_OPTION_PALETTE, '[c]'), 'ontroversial ',
            (MENU_OPTION_PALETTE, '[t]'), 'op\n',
            (MENU_OPTION_PALETTE, '[a]'), 'uthor\nne',
            (MENU_OPTION_PALETTE, '[x]'), 't bac',
            (MENU_OPTION_PALETTE, '[k]'), ' ',
            (MENU_OPTION_PALETTE, '[l]'), 'ookup user ',
            (MENU_OPTION_PALETTE, '[q]'), 'uit\n\n',
        ]
    elif viewType == SUBMISSION_VIEW:
        return [
            (MENU_OPTION_PALETTE, '[h]'), 'ot ',
            (MENU_OPTION_PALETTE, '[r]'), 'ising ',
            (MENU_OPTION_PALETTE, '[n]'), 'ew ',
            (MENU_OPTION_PALETTE, '[c]'), 'ontroversial ',
            (MENU_OPTION_PALETTE, '[t]'), 'op\n',
            (MENU_OPTION_PALETTE, '[u]'), 'pvote ',
            (MENU_OPTION_PALETTE, '[d]'), 'ownvote clear',
            (MENU_OPTION_PALETTE, '[v]'), 'ote ',
            (MENU_OPTION_PALETTE, '[a]'), 'uthor\n',
            (MENU_OPTION_PALETTE, '[/]'), 'subreddit ',
            (MENU_OPTION_PALETTE, '[l]'), 'ookup user ',
            (MENU_OPTION_PALETTE, '[enter]'), 'comments ',
            (MENU_OPTION_PALETTE, '[q]'), 'uit\n\n'
        ]
    elif viewType == AUTHOR_COMMENT_VIEW:
        return [
            (MENU_OPTION_PALETTE, ''), 'bac',
            (MENU_OPTION_PALETTE, '[k]'), ' ',
            (MENU_OPTION_PALETTE, '[q]'), 'uit\n\n'
        ]

# Get the banner text
def getHeader(username):
    userNameLine = "***  u/" + username
    headerText = "**********************************************\n"
    headerText += "***  Reddit for terminal                   ***\n"
    headerText += userNameLine.ljust(43) + "***\n"
    headerText += "**********************************************\n"
    
    return headerText

def getPalette():
    # Colour palette used for various attributes
    return [
        (HEADER_PALETTE, 'dark green', 'black'),
        (FOCUS_PALETTE, 'yellow', 'default', 'standout'),
        (DATA_BODY_PALETTE, 'light green', 'default'),
        (DATA_INFO_PALETTE, 'light gray', 'default', 'default'),
        (DATA_INFO_WARNING, 'light red', 'default', 'default'),
        (DATA_INFO_SELECT_PALETTE, 'light cyan', 'default', 'bold'),
        (DIALOG_MESSAGE_PALETTE, 'dark cyan', 'black'),
        (DIALOG_ERROR_PALETTE, 'dark red', 'black'),
        (MENU_OPTION_PALETTE, 'light green', 'black', 'standout')
    ]