#!/usr/bin/python
import urwid
import rtv2util as util
import reddittmain as main

# Redditt Application
class ReddittApplication(urwid.WidgetPlaceholder):
    urwid.set_encoding("UTF-8")
    SUBMISSION_LIST_LIMIT = 100
    SUBLIST_LIMIT = 10
    submissionItems = None
    commentItems = None
    authorItems = None
    head = None
    foot = None

    # Initialize everything
    def __init__(self):
        self.reddit = util.Redditt()
        self.subreddit = "all"
        self.subreddit_type = "hot"
        self.submissions = self.reddit.getSubList(self.subreddit,self.SUBMISSION_LIST_LIMIT,self.subreddit_type)
        self.commentSubmissionId = None

        self.currentSubmissionIndex = 0
        self.currentCommentsIndex = 0
        self.currentAuthorCommentIndex = 0
        self.currentAuthorSubmissionIndex = 0

        self.author = None

        self.submissionItems = util.createSubmissionsList(self.submissions)
        self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex, self.submissionItems, self.SUBLIST_LIMIT)
        self.commentItems = util.CustomOrderedDict({})
        self.commentTextItems = util.CustomOrderedDict({})
        self.authorItems = util.CustomOrderedDict({})
        self.authorTextItems = util.CustomOrderedDict({})
        self.view = util.SUBMISSION_VIEW # or util.COMMENT_VIEW
        self.lastView = util.SUBMISSION_VIEW

        self.content = urwid.SimpleListWalker([
            urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
        ])

        self.listbox = urwid.ListBox(self.content)

        headText = util.getHeader(self.reddit.getUsername())
        self.head = urwid.Text((util.HEADER_PALETTE,[headText, (util.HEADER_PALETTE, (util.getMenuItems(util.SUBMISSION_VIEW)))]), wrap='clip')    
        
        footText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage 1/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
        self.foot = urwid.Text((util.FOOTER_PALETTE,footText), wrap='clip')

        self.frame = urwid.Frame(self.listbox, header=self.head, footer=self.foot)

        self.dialogBoxOpen = False

        super(ReddittApplication, self).__init__(self.frame)

    # Keypress actions
    def keypress(self, size, key):

        if self.dialogBoxOpen == False:
            if key == "q":
                raise urwid.ExitMainLoop()
            elif key == 'up':
                focus_widget, localIndex = self.listbox.get_focus()

                if self.view != util.AUTHOR_COMMENT_VIEW:
                    if self.view == util.SUBMISSION_VIEW:
                        self.currentSubmissionIndex -= 1
                        if self.currentSubmissionIndex < 0:
                            self.currentSubmissionIndex = 0

                        if localIndex > 0:
                            localIndex -= 1
                        else:
                            localIndex = 0
                            if self.currentSubmissionIndex > 0:
                                localIndex = self.SUBLIST_LIMIT-1
                                self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex-(self.SUBLIST_LIMIT-1), self.submissionItems, self.SUBLIST_LIMIT)
                                self.content[:] = urwid.SimpleListWalker([
                                    urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
                                ])
                            
                        submissionIndex = 1 if self.currentSubmissionIndex == 0 else self.currentSubmissionIndex
                        footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int(((submissionIndex-1)+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                        self.foot.set_text(footerText)
                        self.listbox.set_focus(localIndex)
                    # Comments
                    else:
                        if localIndex > 0:
                            localIndex -= 1
                            self.currentCommentsIndex -= 1
                            if localIndex == 0:
                                headText = util.getHeader(self.reddit.getUsername())
                                self.head.set_text((util.HEADER_PALETTE,[headText, (util.HEADER_PALETTE, (util.getMenuItems(util.COMMENT_SUBMISSION_VIEW)))]))
                                self.head.set_wrap_mode('clip')

                        self.listbox.set_focus(localIndex)
                else:
                    if (self.view == util.AUTHOR_COMMENT_VIEW and len(self.authorTextItems.values()) > 0) or (self.view == util.COMMENT_VIEW and len(self.commentTextItems.values()) > 0):
                        if localIndex > 0:
                            localIndex -= 1    
                        self.listbox.set_focus(localIndex)
            elif key == 'down':
                focus_widget, localIndex = self.listbox.get_focus()

                if localIndex is None:
                    localIndex = self.SUBLIST_LIMIT-1

                if self.view != util.AUTHOR_COMMENT_VIEW:
                    if self.view == util.SUBMISSION_VIEW:
                        if self.currentSubmissionIndex < len(self.submissionItems):
                            self.currentSubmissionIndex += 1

                        if localIndex < self.SUBLIST_LIMIT-1:
                            localIndex += 1
                        else:
                            if self.currentSubmissionIndex < len(self.submissionItems):
                                localIndex = 0
                                self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex, self.submissionItems, self.SUBLIST_LIMIT)
                                self.content[:] = urwid.SimpleListWalker([
                                    urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
                                ])
                        
                        if self.currentSubmissionIndex < len(self.submissionItems):
                            self.listbox.set_focus(localIndex)
                            footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int((self.currentSubmissionIndex+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                            self.foot.set_text(footerText)
                    else: # COMMENT
                        if localIndex < (len(self.commentTextItems.values())-1):
                            localIndex += 1
                            self.currentCommentsIndex += 1
                        if localIndex > 0:
                            headText = util.getHeader(self.reddit.getUsername())
                            self.head.set_text((util.HEADER_PALETTE,[headText, (util.HEADER_PALETTE, (util.getMenuItems(util.COMMENT_VIEW)))]))
                            self.head.set_wrap_mode('clip')
                        self.listbox.set_focus(localIndex)
                else:
                    if len(self.authorTextItems.values()) > 0:
                        if localIndex < (len(self.authorTextItems.values())-1):
                            localIndex += 1
                        self.listbox.set_focus(localIndex)
            elif (key == 'enter' and self.view == util.SUBMISSION_VIEW):
                self.__initComments("best", None)
            elif key == 'k' and (self.view == util.COMMENT_VIEW or self.lastView == util.SUBMISSION_VIEW):
                headerText = util.getHeader(self.reddit.getUsername())
                self.head.set_text((util.HEADER_PALETTE,[headerText, (util.HEADER_PALETTE, util.getMenuItems(util.SUBMISSION_VIEW))]))    

                footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int((self.currentSubmissionIndex+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                self.foot.set_text(footerText)
                self.view = util.SUBMISSION_VIEW

                self.content[:] = urwid.SimpleListWalker([
                    urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
                ])

                self.listbox.set_focus(int(repr(self.currentSubmissionIndex)[-1]))
            elif (key == 'k' and self.lastView == util.COMMENT_VIEW):
                self.__initComments("best", self.commentSubmissionId, key)
            elif (key == 'b' and self.view == util.COMMENT_VIEW):
                self.__initComments("best", self.commentSubmissionId)
            elif (key == 'n' and self.view == util.COMMENT_VIEW):
                self.__initComments("new", self.commentSubmissionId)
            elif (key == 't' and self.view == util.COMMENT_VIEW):
                self.__initComments("top", self.commentSubmissionId)
            elif (key == 'c' and self.view == util.COMMENT_VIEW):
                self.__initComments("controversial", self.commentSubmissionId)
            elif key == 'a' and (self.view == util.COMMENT_VIEW or self.view == util.SUBMISSION_VIEW):
                self.__initAuthor(None)
            elif key == 'c' and (self.view == util.AUTHOR_COMMENT_VIEW):
                self.__initAuthor(self.author, util.COMMENT_VIEW)
            elif key == 's' and (self.view == util.AUTHOR_COMMENT_VIEW):
                self.__initAuthor(self.author, util.SUBMISSION_VIEW)
            elif key == 'h' and self.view == util.SUBMISSION_VIEW:
                self.__initSubmissions(self.subreddit,"hot")
            elif key == 'n' and self.view == util.SUBMISSION_VIEW:
                self.__initSubmissions(self.subreddit,"new")
            elif key == 'r' and self.view == util.SUBMISSION_VIEW:
                self.__initSubmissions(self.subreddit,"rising")
            elif key == 'c' and self.view == util.SUBMISSION_VIEW:  
                self.__initSubmissions(self.subreddit,"controversial")  
            elif key == 't' and self.view == util.SUBMISSION_VIEW:
                self.__initSubmissions(self.subreddit,"top")
            elif key == '/' and self.view == util.SUBMISSION_VIEW:
                self.create_box(util.DIALOG_SUBREDDIT_TITLE)
            elif key == 's' and self.view == util.COMMENT_VIEW:
                self.currentCommentsIndex = 0
                self.listbox.set_focus(self.currentCommentsIndex)
                headText = util.getHeader(self.reddit.getUsername())
                self.head.set_text((util.HEADER_PALETTE,[headText, (util.HEADER_PALETTE, (util.getMenuItems(util.COMMENT_SUBMISSION_VIEW)))]))
                self.head.set_wrap_mode('clip')
            elif key == 'l':
                self.create_box(util.DIALOG_USER_TITLE)
            elif key == 'm' and self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                self.create_box(util.DIALOG_COMMENT_TITLE)
            elif key == 'r' and self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                self.create_box(util.DIALOG_REPLY_TITLE)
            elif key == 'u' and self.view == util.SUBMISSION_VIEW:
                submission = self.get_submission()
                submission.upvote()
                self.update_list_with_vote(key)
            elif key == 'd' and self.view == util.SUBMISSION_VIEW:
                submission = self.get_submission()
                submission.downvote()
                self.update_list_with_vote(key)
            elif key == 'v' and self.view == util.SUBMISSION_VIEW:
                submission = self.get_submission()
                submission.clear_vote()
                self.update_list_with_vote(key)
            elif key == 'u' and self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                comment = self.get_comment()
                comment.upvote()
                self.update_list_with_vote(key)
            elif key == 'd' and self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                comment = self.get_comment()
                comment.downvote()
                self.update_list_with_vote(key)
            elif key == 'v' and self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                comment = self.get_comment()
                comment.clear_vote()
                self.update_list_with_vote(key)
            elif key == 'p' and self.view == util.COMMENT_VIEW:
                # Previous parent comment
                self.find_comment_parent("previous")
            elif key == 'x' and self.view == util.COMMENT_VIEW:
                # Next parent comment
                self.find_comment_parent("next")
        else:
            if key != 'enter' and key != 'esc':
                return super(ReddittApplication, self).keypress(size, key)
            elif key == 'esc':
                self.dialogComponents = None
                self.dialogBoxOpen = False
                self.original_widget = self.original_widget[0]
            elif key == 'enter':
                self.process_inputs(self.dialogComponents, None)

    def find_comment_parent(self, type):
        parentFound = False

        commentsLength = len(self.commentTextItems)

        if commentsLength == 1:
            parentFound = True
        else:
            while parentFound == False:
                if type == "previous" and self.currentCommentsIndex > 1:
                    self.currentCommentsIndex = self.currentCommentsIndex - 1
                # next
                elif type == "next" and self.currentCommentsIndex < commentsLength-1:
                    self.currentCommentsIndex = self.currentCommentsIndex + 1
                    
                commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                
                if "comment_title" not in commentKey:
                    commentKeyArray = commentKey.split("|")
                    
                    depth = commentKeyArray[1]                
                    if int(depth) == 0:
                        parentFound = True

                if self.currentCommentsIndex == 1:
                    parentFound = True

            headText = util.getHeader(self.reddit.getUsername())
            self.head.set_text((util.HEADER_PALETTE,[headText, (util.HEADER_PALETTE, (util.getMenuItems(util.COMMENT_VIEW)))]))
            self.head.set_wrap_mode('clip')

            self.listbox.set_focus(self.currentCommentsIndex)

    # Update the list when voting
    def update_list_with_vote(self, key):
        focus_widget, localIndex = self.listbox.get_focus()
        updatedStr = ""

        if self.view == util.SUBMISSION_VIEW:
            submissionValue = list(self.submissionTextItems.values())[localIndex]
            submissionArray = submissionValue.get_text()[0].split("\n")
            submissionTitle = submissionArray[0]
            submissionInfo = submissionArray[1]
            submissionInfoArray = submissionInfo.split()

            if not (u"\u2191" in submissionInfo and key == "u") and not (u"\u2193" in submissionInfo and key == "d"):
                updatedSubmissionInfo = ""
                submissionSubreddit = ""
                submissionAuthor = ""
                submissionPoints = ""
                submissionCommentCount = ""

                for index, submissionInfoText in enumerate(submissionInfoArray):
                    # Subreddit
                    if index == 0 or submissionInfoText == util.NSFW_TEXT or submissionInfoText == util.SPOILERS_TEXT or submissionInfoText == util.STICKIED_TEXT:
                        submissionSubreddit += submissionInfoText + " "
                    # Author
                    elif submissionInfoText.startswith('u/'):
                        submissionAuthor = submissionInfoText
                    # Points
                    elif index >= len(submissionInfoArray)-4 and index <= len(submissionInfoArray)-3:
                        submissionPoints += " " + submissionInfoText
                    # Comment count
                    elif index >= len(submissionInfoArray)-2 and index <= len(submissionInfoArray)-1:
                        submissionCommentCount += " " + submissionInfoText

                if key == "u":
                    submissionSubreddit += u"\u2191"
                elif key == "d":
                    submissionSubreddit += u"\u2193"
                updatedSubmissionInfo = submissionSubreddit.strip().ljust(util.SUBMISSION_SUBREDDIT_LJUST) + submissionAuthor.ljust(util.SUBMISSION_AUTHOR_LJUST) + submissionPoints.ljust(util.SUBMISSION_POINTS_LJUST) + submissionCommentCount

                updatedStr = submissionTitle + "\n" + updatedSubmissionInfo + "\n"
                    
                submissionId = list(self.submissionTextItems.keys())[localIndex]
                self.submissionTextItems[submissionId] = urwid.Text(updatedStr)
                self.content[:] = urwid.SimpleListWalker([
                    urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
                ])
        elif self.view == util.COMMENT_VIEW:
            commentValue = list(self.commentTextItems.values())[localIndex]
            commentArray = commentValue.original_widget.get_text()[0].split("\n")
            commentTitle = commentArray[1]
            commentInfo = commentArray[0]
            commentInfoArray = commentInfo.split()
            commentKey = list(self.commentTextItems.keys())[localIndex]
            offset = int(commentKey.split("|")[1])
            voteIndex = 0

            if not (u"\u2191" in commentInfo and key == "u") and not (u"\u2193" in commentInfo and key == "d"):
        
                if u"\u2191" in commentInfo:
                    voteIndex = commentInfoArray.index(u"\u2191")
                elif u"\u2193" in commentInfo:
                    voteIndex = commentInfoArray.index(u"\u2193")

                updatedCommentInfo = ""
                for index, commentInfoText in enumerate(commentInfoArray):
                    spacer = ""
                    if index > 0:
                        spacer = " "
                    if index == voteIndex:
                        if commentInfoText != u"\u2191" and commentInfoText != u"\u2193":
                            updatedCommentInfo += commentInfoText + " "
                        
                        if key == "u":
                            updatedCommentInfo += spacer + u"\u2191"
                        elif key == "d":
                            updatedCommentInfo += spacer + u"\u2193"
                    else:
                        updatedCommentInfo += spacer + commentInfoText

                updatedStr = updatedCommentInfo + "\n" + commentTitle + "\n"
                updatedText = urwid.Text(updatedStr)
                updatedText = urwid.Padding(updatedText, 'left', 'pack', None, offset, 0)

                self.commentTextItems[commentKey] = updatedText
                self.content[:] = urwid.SimpleListWalker([
                    urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.commentTextItems.values()
                ])
        
        self.listbox.set_focus(localIndex)

    # get current submission object
    def get_submission(self):
        focus_widget, localIndex = self.listbox.get_focus()
        submissionId = list(self.submissionTextItems.keys())[localIndex]
        self.reddit.setSubmission(submissionId)
        return self.reddit.getSubmission()

    # Get current comment object
    def get_comment(self):
        commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
        commentKeyArray = commentKey.split("|")
        commentId = commentKeyArray[0]
        self.reddit.setComment(commentId)
        return self.reddit.getComment()

    # Process dialog window inputs
    def process_inputs(self, dialogComponents, button):
        form_inputs = dialogComponents.get_inputs()
        form_dictionary = {}
        for form_input in form_inputs:
            form_input_array = form_input.get_text()[0].split(": ")
            key = form_input_array[0]
            value = form_input.get_edit_text()
            form_dictionary[key] = value

        if dialogComponents.get_title() == util.DIALOG_COMMENT_TITLE:
            try:
                comment = list(form_dictionary.values())[0]

                submissionId = list(self.submissionItems.keys())[self.currentSubmissionIndex]
                self.reddit.setSubmission(submissionId)
                submission = self.reddit.getSubmission()

                submission.reply(comment)
                self.dialogComponents = None
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False
            except:
                dialogComponents.set_error("Error submitting submission reply")
        elif dialogComponents.get_title() == util.DIALOG_REPLY_TITLE:
            try:
                reply = list(form_dictionary.values())[0]

                commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                commentKeyArray = commentKey.split("|")
                commentId = commentKeyArray[0]
                self.reddit.setComment(commentId)
                comment = self.reddit.getComment()

                comment.reply(reply)
                self.dialogComponents = None
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False
            except:
                dialogComponents.set_error("Error submitting comment reply")
        elif dialogComponents.get_title() == util.DIALOG_SUBREDDIT_TITLE:
            exceptionRaised = False
            try:
                subreddit = list(form_dictionary.values())[0]

                self.__initSubmissions(subreddit,"hot")
            except:
                dialogComponents.set_error("Error getting subreddit")
                exceptionRaised = True

            if exceptionRaised == False:
                self.dialogBoxOpen = False
                self.dialogComponents = None
                self.original_widget = self.original_widget[0]
        elif dialogComponents.get_title() == util.DIALOG_USER_TITLE:
            exists = True
            try:
                authorName = list(form_dictionary.values())[0]
                author = self.reddit.getRedditInstance().redditor(authorName)

                try:
                    if author.id:
                        exists = True
                except:
                    dialogComponents.set_error("Error getting user")
                    exists = False
            except:
                dialogComponents.set_error("Error getting user")
                exists = False

            if exists == True:
                self.author = author
                self.__initAuthor(author)
                self.dialogComponents = None
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False

    # Exit the dialog window
    def exit_box(self, button):
        self.dialogComponents = None
        self.dialogBoxOpen = False
        self.original_widget = self.original_widget[0]

    # Open the dialog window
    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 40),
            valign='middle', height=('relative', 40),
            min_width=24, min_height=8,
            left=3,
            right=3,
            top=2,
            bottom=2
        )
        self.dialogBoxOpen = True

    # Create the dialog window
    def create_box(self, caption):
        self.dialogComponents = util.DialogComponents()

        label = caption + ": "
        entry = urwid.Edit(caption=label)
        formFields = [entry]

        okbutton = urwid.Button("OK")
        urwid.connect_signal(okbutton, 'click', self.process_inputs, weak_args=[self.dialogComponents])
        urwid.AttrMap(okbutton, None, focus_map='reversed')
        cancelbutton = urwid.Button("Cancel")
        urwid.connect_signal(cancelbutton, 'click', self.exit_box)
        urwid.AttrMap(cancelbutton, None, focus_map='reversed')

        box = self.dialogComponents.create_form(caption, formFields, okbutton, cancelbutton)

        self.open_box(box)

    # Recursively collect nested comments used for display, keyed by comment ID
    def __commentsToDictionary(self, comments, is_reply, depth, comTextItems, author):

        #from praw.models import MoreComments
        comments.replace_more(limit=0)
        for comment in comments:  # iterate over comments            
            comTextItems = self.process_comment(comment, author, comTextItems)

        return comTextItems  # return all converted comments

    def process_comment(self, comment, author, comTextItems, depth=0):
        head = ""
        offset = depth
        offset = offset * util.COMMENT_OFFSET

        # Test offset
        # head += " offset: " + str(offset) + " "

        authorText = ""
        if offset == 0:
            authorText += ":"

        authorText += "u/" + str(comment.author)
        attribute = util.DATA_INFO_PALETTE
        if author == str(comment.author):
            attribute = util.DATA_INFO_SELECT_PALETTE
        authorName = (attribute, authorText)            

        if comment.likes is not None:
            if comment.likes:
                head += " " + u"\u2191"
            elif not comment.likes:
                head += " " + u"\u2193"

        head += " " + str(comment.score) + " point"
        if comment.score != 1:
            head +=  "s"

        if comment.gilded > 0:
            head += " " + str(comment.gilded) + " gilded" 
        
        body = "\n"+util.encodeString(comment.body) + "\n"

        output = [authorName, (util.DATA_INFO_PALETTE, head), body]
        # content = urwid.LineBox(main.SelectableText(output), tlcorner='', tline='', lline='│', trcorner='', blcorner='└', rline='', bline='─', brcorner='')
        content = main.SelectableText(output)
        comment_with_padding = urwid.Padding(content, 'left', 'pack', None, offset, 0)
        comTextItems.append(comment.id+"|"+str(offset), comment_with_padding)

        for reply in comment.replies:
            comTextItems = self.process_comment(reply, author, comTextItems, depth + 1)

        return comTextItems

    # Get comments
    def __initComments(self, sorting, submissionId, key=None):
        if submissionId == None:
            focus_widget, localIndex = self.listbox.get_focus()

            # Get the submission ID
            submissionId = list(self.submissionTextItems.keys())[localIndex]
            self.commentSubmissionId = submissionId
        
        if key != 'k':
            self.currentCommentsIndex = 0

        self.reddit.setSubmission(submissionId)
        submission = self.reddit.getSubmission()
        comments = self.reddit.getSubmissionComments(sorting)

        comTextItems = util.CustomOrderedDict({})
        
        submissionLink = util.getCommentLink(submission.permalink)
        textList = [(util.DATA_INFO_PALETTE, "u/" + str(submission.author.name + " - " + submissionLink))]
        textList.append("\n" + util.encodeString(submission.title))

        if len(str(submission.url)) > 0:
            textList.append("\n" + str(submission.url))

        if len(submission.selftext) > 0:
            textList.append((util.HEADER_PALETTE, "\n\n" + util.encodeString(submission.selftext)))

        #textList.append(urwid.Divider(u'─', 0, 1))
        textList.append("\n" + ("─" * int(main.getScreen().get_cols_rows()[0])) + "\n")
        comTextItems.append(str(submissionId) + "|comment_title", main.SelectableText(textList))
        self.commentTextItems = self.__commentsToDictionary(comments, False, 0, comTextItems, str(submission.author.name))

        headerText = util.getHeader(self.reddit.getUsername())

        self.head.set_text((util.HEADER_PALETTE,[headerText, (util.HEADER_PALETTE, util.getMenuItems(util.COMMENT_SUBMISSION_VIEW))]))    

        self.foot.set_text("\nr/" + str(submission.subreddit))

        self.view = util.COMMENT_VIEW

        self.content[:] = urwid.SimpleListWalker([
            urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.commentTextItems.values()
        ])

        if len(comments) > 0:
            # Go to top then shift down to be able see top level submission
            self.listbox.set_focus(self.currentCommentsIndex)

    # Get author
    def __initAuthor(self, author, viewType=util.COMMENT_VIEW):
        if self.view != util.AUTHOR_COMMENT_VIEW:
            self.lastView = self.view

        if author == None:
            if self.view == util.COMMENT_VIEW and self.currentCommentsIndex > 0:
                commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                commentKeyArray = commentKey.split("|")
                self.reddit.setComment(commentKeyArray[0])
                comment = self.reddit.getComment()
                self.commentSubmissionId = comment.submission.id
                self.author = comment.author
            elif self.view == util.SUBMISSION_VIEW or (self.view == util.COMMENT_VIEW and self.currentCommentsIndex == 0):
                if self.view == util.SUBMISSION_VIEW:
                    focus_widget, localIndex = self.listbox.get_focus()
                    submissionId = list(self.submissionTextItems.keys())[localIndex]
                else:
                    commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                    commentKeyArray = commentKey.split("|")
                    submissionId = commentKeyArray[0]
                
                self.reddit.setSubmission(submissionId)
                submission = self.reddit.getSubmission()
                self.author = submission.author

        if viewType == util.COMMENT_VIEW:
            self.currentAuthorCommentIndex = 0
            self.authorCommentTextItems = util.createAuthorCommentList(self.author, self.SUBMISSION_LIST_LIMIT)
            self.authorTextItems = main.getAuthorCommentTextList(self.currentAuthorCommentIndex, self.authorCommentTextItems, self.SUBLIST_LIMIT)
        else:
            self.currentAuthorSubmissionIndex = 0
            self.authorSubmissionTextItems = util.createAuthorSubmissionList(self.author, self.SUBMISSION_LIST_LIMIT)
            self.authorTextItems = main.getAuthorSubmissionTextList(self.currentAuthorSubmissionIndex, self.authorSubmissionTextItems, self.SUBLIST_LIMIT)

        self.content[:] = urwid.SimpleListWalker([
            urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.authorTextItems.values()
        ])

        if len(self.authorTextItems) > 0:
            self.listbox.set_focus(0)

        # Change header
        headerText = util.getHeader(self.reddit.getUsername())
        self.head.set_text((util.HEADER_PALETTE,[headerText, (util.HEADER_PALETTE, util.getMenuItems(util.AUTHOR_COMMENT_VIEW))]))
        # Change footer
        footerText = "\nu/" + self.author.name
        if len(self.author.trophies()) > 0:
            footerText += "\n"
            for trophy in self.author.trophies():
                footerText += trophy.name + ", "
            footerText = footerText[:-2]

        self.foot.set_text(footerText)
        self.view = util.AUTHOR_COMMENT_VIEW

    # Reloads the content body with subreddit by type
    def __initSubmissions(self, subreddit, type):
        exists = True
        try:
            self.reddit.getRedditInstance().subreddits.search_by_name(subreddit, exact=True)
        except:
            exists = False
            raise

        if exists == True:
            self.submissions = self.reddit.getSubList(subreddit,self.SUBMISSION_LIST_LIMIT,type)

            self.subreddit_type = type
            self.subreddit = subreddit

            self.currentSubmissionIndex = 0
            self.currentCommentsIndex = 0

            self.submissionItems = util.createSubmissionsList(self.submissions)
            self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex, self.submissionItems, self.SUBLIST_LIMIT)
            self.commentItems = util.CustomOrderedDict({})
            self.commentTextItems = util.CustomOrderedDict({})
            self.authorItems = util.CustomOrderedDict({})
            self.authorTextItems = util.CustomOrderedDict({})

            footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage 1/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
            self.foot.set_text(footerText)

            self.content[:] = urwid.SimpleListWalker([
                urwid.AttrMap(w, util.DATA_BODY_PALETTE, util.FOCUS_PALETTE) for w in self.submissionTextItems.values()
            ])    

            self.listbox.set_focus(self.currentSubmissionIndex)