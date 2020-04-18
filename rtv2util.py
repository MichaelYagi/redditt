#!/usr/bin/python
import urwid
import praw
from collections import OrderedDict
from datetime import datetime

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
        message = urwid.AttrMap(self.message, 'boxMessage')
        self.body.append(message)
        error = urwid.AttrMap(self.error, 'boxError')
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

# Get menu items for header
def getMenuItems(viewType):
    if viewType == "comments":
        return [('menu option', '[b]'),'est ',
            ('menu option', '[p]'), 'revious ',
            ('menu option', '[c]'), 'omment ',
            ('menu option', '[r]'), 'eply ',
            ('menu option', '[l]'), 'ookup user ',
            ('menu option', '[q]'), 'uit\n',
            ('menu option', '[u]'), 'pvote ',
            ('menu option', '[d]'), 'ownvote clear',
            ('menu option', '[v]'), 'ote ',
            ('menu option', '[a]'), 'uthor scroll',
            ('menu option', '[t]'), 'op\n\n'
        ]
    elif viewType == "submission":
        return [('menu option', '[h]'),'ot ',
            ('menu option', '[n]'), 'ew ',
            ('menu option', '[r]'), 'ising ',
            ('menu option', '[c]'), 'ontroversial ',
            ('menu option', '[t]'), 'op ',
            ('menu option', '[/]'), 'subreddit ',
            ('menu option', '[l]'), 'ookup user ',
            ('menu option', '[enter]'), ' ',
            ('menu option', '[q]'), 'uit\n',
            ('menu option', '[u]'), 'pvote ',
            ('menu option', '[d]'), 'ownvote clear',
            ('menu option', '[v]'), 'ote ',
            ('menu option', '[a]'), 'uthor\n\n'
        ]
    elif viewType == "authorComments":
        return [('menu option', '[p]'), 'revious \n\n']

# Get the banner text
def getHeader(username):
    userNameLine = "***  u/" + username
    headerText = "**********************************************\n"
    headerText += "***  Reddit for terminal                   ***\n"
    headerText += userNameLine.ljust(43) + "***\n"
    headerText += "**********************************************\n"
    
    return headerText

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

        output = body + "\n"
        output += points.ljust(20)
        output += "r/" + subreddit.ljust(20)
        output += commentTime + "\n"

        subItems.append(comment.id, output)

    return subItems

# Creates a list of submission texts used for display, keyed by submission ID
def createSubmissionsList(submissions):
    subItems = CustomOrderedDict({})
    
    for index, submission in enumerate(submissions):
        title = submission.title + "\n"
        
        # Subreddit
        pre_output = "r/" + submission.subreddit.display_name
        if submission.over_18:
            pre_output += " NSFW"
        if submission.spoiler:
            pre_output += " SPOILERS"
        if submission.likes is not None:
            if submission.likes:
                pre_output += " " + u"\u2191"
            elif not submission.likes:
                pre_output += " " + u"\u2193"
                
        footer = pre_output.ljust(35)

        # Author
        if hasattr(submission.author, 'name'):
            author = "u/" + submission.author.name
            footer += author.ljust(24)

        # Points
        pointString = " " + str(submission.score) + " point"
        if submission.score != 1:
            pointString += "s"
        footer += pointString.ljust(20)
        
        # Comment count
        numCommentString = " " + str(submission.num_comments) + " comment"
        if submission.num_comments != 1:
            numCommentString += "s"
        footer += numCommentString + "\n"
        
        output = [title,footer]
        subItems.append(submission.id, output)

    return subItems