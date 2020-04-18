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

        self.submissionItems = util.createSubmissionsList(self.submissions)
        self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex, self.submissionItems, self.SUBLIST_LIMIT)
        self.commentItems = util.CustomOrderedDict({})
        self.commentTextItems = util.CustomOrderedDict({})
        self.authorItems = util.CustomOrderedDict({})
        self.authorTextItems = util.CustomOrderedDict({})
        self.view = "submissions" # or comments
        self.lastView = "submissions"

        self.content = urwid.SimpleListWalker([
            urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
        ])

        self.listbox = urwid.ListBox(self.content)

        headText = util.getHeader(self.reddit.getUsername())
        self.head = urwid.Text(('header',[headText, ('header', (util.getMenuItems("submission")))]), wrap='clip')    
        
        footText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage 1/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
        self.foot = urwid.Text(('footer',footText), wrap='clip')

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

                if self.view != "authorComment":
                    if self.view == "submissions":
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
                                    urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
                                ])
                            
                        submissionIndex = 1 if self.currentSubmissionIndex == 0 else self.currentSubmissionIndex
                        footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int(((submissionIndex-1)+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                        self.foot.set_text(footerText)
                        self.listbox.set_focus(localIndex)
                    else:
                        if localIndex > 1:
                            localIndex -= 1
                            self.currentCommentsIndex -= 1
                        self.listbox.set_focus(localIndex)
                else:
                    if localIndex > 0:
                        localIndex -= 1    
                    self.listbox.set_focus(localIndex)
            elif key == 'down':
                focus_widget, localIndex = self.listbox.get_focus()

                if localIndex is None:
                    localIndex = self.SUBLIST_LIMIT-1

                if self.view != "authorComment":
                    if self.view == "submissions":
                        if self.currentSubmissionIndex < len(self.submissionItems):
                            self.currentSubmissionIndex += 1

                        if localIndex < self.SUBLIST_LIMIT-1:
                            localIndex += 1
                        else:
                            if self.currentSubmissionIndex < len(self.submissionItems):
                                localIndex = 0
                                self.submissionTextItems = main.getSubmissionTextList(self.currentSubmissionIndex, self.submissionItems, self.SUBLIST_LIMIT)
                                self.content[:] = urwid.SimpleListWalker([
                                    urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
                                ])
                        
                        if self.currentSubmissionIndex < len(self.submissionItems):
                            self.listbox.set_focus(localIndex)
                            footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int((self.currentSubmissionIndex+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                            self.foot.set_text(footerText)
                    else: # COMMENT
                        if localIndex < (len(self.commentTextItems.values())-1):
                            localIndex += 1
                            self.currentCommentsIndex += 1
                        self.listbox.set_focus(localIndex)
                else:
                    if localIndex < (len(self.authorTextItems.values())-1):
                        localIndex += 1
                    self.listbox.set_focus(localIndex)
            elif (key == 'enter' and self.view == "submissions"):
                self.__initComments("best", None)
            elif key == 'p' and (self.view == "comments" or self.lastView == "submissions"):
                headerText = util.getHeader(self.reddit.getUsername())
                self.head.set_text(('header',[headerText, ('header', util.getMenuItems("submission"))]))    

                footerText = "\nr/"+self.subreddit+" - "+self.subreddit_type+"\nPage "+str(int((self.currentSubmissionIndex+self.SUBLIST_LIMIT)/(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT)))+"/"+str(int(self.SUBMISSION_LIST_LIMIT/self.SUBLIST_LIMIT))
                self.foot.set_text(footerText)
                self.view = "submissions"

                self.content[:] = urwid.SimpleListWalker([
                    urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
                ])

                self.listbox.set_focus(int(repr(self.currentSubmissionIndex)[-1]))
            elif (key == 'p' and self.lastView == "comments"):
                self.__initComments("best", self.commentSubmissionId)
            elif (key == 'b' and self.view == "comments"):
                self.__initComments("best", self.commentSubmissionId)
            elif (key == 'n' and self.view == "comments"):
                self.__initComments("new", self.commentSubmissionId)
            elif (key == 't' and self.view == "comments"):
                self.__initComments("top", self.commentSubmissionId)
            elif (key == 'c' and self.view == "comments"):
                self.__initComments("controversial", self.commentSubmissionId)
            elif key == 'a':
                self.__initAuthor(None)
            elif key == 'h' and self.view == "submissions":
                self.__reinitSubmissions(self.subreddit,"hot")
            elif key == 'n' and self.view == "submissions":
                self.__reinitSubmissions(self.subreddit,"new")
            elif key == 'r' and self.view == "submissions":
                self.__reinitSubmissions(self.subreddit,"rising")
            elif key == 'c' and self.view == "submissions":  
                self.__reinitSubmissions(self.subreddit,"controversial")  
            elif key == 't' and self.view == "submissions":
                self.__reinitSubmissions(self.subreddit,"top")
            elif key == '/' and self.view == "submissions":
                self.create_box("Subreddit")
            elif key == 's' and self.view == "comments":
                self.listbox.set_focus(0)
                self.listbox.set_focus(1)
            elif key == 'l':
                self.create_box("User")
            elif key == 'm' and self.view == "comments":
                self.create_box("Comment")
            elif key == 'r' and self.view == "comments":
                self.create_box("Reply")
            elif key == 'u' and self.view == "submissions":
                submission = self.get_submission()
                submission.upvote()
                self.update_list(key)
            elif key == 'd' and self.view == "submissions":
                submission = self.get_submission()
                submission.downvote()
                self.update_list(key)
            elif key == 'v' and self.view == "submissions":
                submission = self.get_submission()
                submission.clear_vote()
                self.update_list(key)
            elif key == 'u' and self.view == "comments":
                comment = self.get_comment()
                comment.upvote()
                self.update_list(key)
            elif key == 'd' and self.view == "comments":
                comment = self.get_comment()
                comment.downvote()
                self.update_list(key)
            elif key == 'v' and self.view == "comments":
                comment = self.get_comment()
                comment.clear_vote()
                self.update_list(key)
        else:
            if key != 'enter' and key != 'esc':
                return super(ReddittApplication, self).keypress(size, key)
            elif key == 'esc':
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False

    # Update the list when voting
    def update_list(self, key):
        focus_widget, localIndex = self.listbox.get_focus()
        updatedStr = ""

        if self.view == "submissions":
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
                    if index == 0 or submissionInfoText == "NSFW" or submissionInfoText == "SPOILERS":
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
                updatedSubmissionInfo = submissionSubreddit.strip().ljust(35) + submissionAuthor.ljust(24) + submissionPoints.ljust(20) + submissionCommentCount

                updatedStr = submissionTitle + "\n" + updatedSubmissionInfo + "\n"
                    
                submissionId = list(self.submissionTextItems.keys())[localIndex]
                self.submissionTextItems[submissionId] = urwid.Text(updatedStr)
                self.content[:] = urwid.SimpleListWalker([
                    urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
                ])
        elif self.view == "comments":
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
                    urwid.AttrMap(w, None, 'reveal focus') for w in self.commentTextItems.values()
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

        if dialogComponents.get_title() == "Comment":
            try:
                comment = list(form_dictionary.values())[0]

                submissionId = list(self.submissionItems.keys())[self.currentSubmissionIndex]
                self.reddit.setSubmission(submissionId)
                submission = self.reddit.getSubmission()

                submission.reply(comment)
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False
            except:
                dialogComponents.set_error("Error submitting submission reply")
        elif dialogComponents.get_title() == "Reply":
            try:
                reply = list(form_dictionary.values())[0]

                commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                commentKeyArray = commentKey.split("|")
                commentId = commentKeyArray[0]
                self.reddit.setComment(commentId)
                comment = self.reddit.getComment()

                comment.reply(reply)
                self.original_widget = self.original_widget[0]
                self.dialogBoxOpen = False
            except:
                dialogComponents.set_error("Error submitting comment reply")
        elif dialogComponents.get_title() == "Subreddit":
            try:
                subreddit = list(form_dictionary.values())[0]

                self.__reinitSubmissions(subreddit,"hot")
            except:
                dialogComponents.set_error("Error getting subreddit")
        elif dialogComponents.get_title() == "User":
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
                self.__initAuthor(author)
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
    def __commentsToDictionary(self, comments, is_reply, depth, comTextItems):
        item = ""

        #from praw.models import MoreComments
        comments.replace_more(limit=0)
        for comment in comments:  # iterate over comments
            item = ""
            offset = 0

            if is_reply:
                offset = 2+depth
            else:
                offset = depth

            item += "u/" + str(comment.author)

            if comment.likes is not None:
                if comment.likes:
                    item += " " + u"\u2191"
                elif not comment.likes:
                    item += " " + u"\u2193"

            item += " " + str(comment.score) + " point"
            if comment.score != 1:
                item +=  "s"

            if comment.gilded > 0:
                item += " " + str(comment.gilded) + " gilded" 
            item += "\n"+comment.body.encode('ascii', 'ignore').decode('ascii') + "\n"

            content = main.SelectableText(item)
            comment_with_padding = urwid.Padding(content, 'left', 'pack', None, offset, 0)
            comTextItems.append(comment.id+"|"+str(offset), comment_with_padding)

            if len(comment.replies) > 0:
                depth = depth + 1
                comTextItems = self.__commentsToDictionary(comment.replies, True, depth, comTextItems)  # convert replies using the same function

            is_reply = False

        return comTextItems  # return all converted comments

    # Get comments
    def __initComments(self, sorting, submissionId):
        if submissionId == None:
            focus_widget, localIndex = self.listbox.get_focus()

            # Get the submission ID
            submissionId = list(self.submissionTextItems.keys())[localIndex]
            self.commentSubmissionId = submissionId

        self.reddit.setSubmission(submissionId)
        submission = self.reddit.getSubmission()
        comments = self.reddit.getSubmissionComments(sorting)

        comTextItems = util.CustomOrderedDict({})
        submissionText = str(submission.title)
        if len(submission.url) > 0:
            submissionText += "\n" + submission.url
        if len(submission.selftext) > 0:
            submissionText += "\n----------\n" + submission.selftext
        submissionText += "\n==========\n"
        comTextItems.append("comment_title", main.SelectableText(submissionText))
        self.commentTextItems = self.__commentsToDictionary(comments, False, 0, comTextItems)

        headerText = util.getHeader(self.reddit.getUsername())
        
        if len(comTextItems)-1 > 0:
            self.head.set_text(('header',[headerText, ('header', util.getMenuItems("comments"))]))    
        else:
            self.head.set_text(('header',[headerText, ('header', util.getMenuItems("submission"))]))    

        self.foot.set_text("\nr/" + str(submission.subreddit))

        self.view = "comments"

        self.content[:] = urwid.SimpleListWalker([
            urwid.AttrMap(w, None, 'reveal focus') for w in self.commentTextItems.values()
        ])

        self.currentCommentsIndex = 1
        if len(comments) > 0:
            # Go to top then shift down to be able see top level submission
            self.listbox.set_focus(0)
            self.listbox.set_focus(self.currentCommentsIndex)

    # Get author
    def __initAuthor(self, author):
        self.lastView = self.view
        if author == None:
            if self.view == "comments":
                commentKey = list(self.commentTextItems.keys())[self.currentCommentsIndex]
                commentKeyArray = commentKey.split("|")
                self.reddit.setComment(commentKeyArray[0])
                comment = self.reddit.getComment()
                self.commentSubmissionId = comment.submission.id
                author = comment.author
            elif self.view == "submissions":
                focus_widget, localIndex = self.listbox.get_focus()
                submissionId = list(self.submissionTextItems.keys())[localIndex]
                self.reddit.setSubmission(submissionId)
                submission = self.reddit.getSubmission()
                author = submission.author

        self.currentAuthorCommentIndex = 0
        self.authorCommentTextItems = util.createAuthorCommentList(author, self.SUBMISSION_LIST_LIMIT)
        self.authorTextItems = main.getAuthorCommentTextList(self.currentAuthorCommentIndex, self.authorCommentTextItems, self.SUBLIST_LIMIT)
        self.content[:] = urwid.SimpleListWalker([
            urwid.AttrMap(w, None, 'reveal focus') for w in self.authorTextItems.values()
        ])
        self.listbox.set_focus(0)

        # Change header
        headerText = util.getHeader(self.reddit.getUsername())
        self.head.set_text(('header',[headerText, ('header', util.getMenuItems("authorComments"))]))
        # Change footer
        self.foot.set_text("\nr/" + author.name)
        self.view = "authorComment"

    # Reloads the content body with subreddit by type
    def __reinitSubmissions(self, subreddit, type):
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
                urwid.AttrMap(w, None, 'reveal focus') for w in self.submissionTextItems.values()
            ])

            self.dialogBoxOpen = False
            self.original_widget = self.original_widget[0]

            self.listbox.set_focus(0)