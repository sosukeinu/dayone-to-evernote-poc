Day One Journal to Evernote
========
###This is currently a *Proof-of-Concept*

You would think I could come up with a more clever name, but...no.

A python script I made for myself, and thought I'd share here, just in case someone else wanted to use it, or better yet, improve it.

**This is my *first-ever* python script, so be gentle.**

Wouldn’t be possible, or at least not as *pretty* without [markdown2](https://github.com/trentm/python-markdown2)

Why?
----------------------------
Because I'm tired of living a double life. Day One for my personal thoughts, and Evernote as my personal knowledge base. Why can't we all just get along?

Requirements
------------------
- Python 2.7 +
- Day One Journal (Duh)
- Evernote account, set to create entries from email. You can get your Evernote email address from your account page, under Account Summary.
- Gmail account to send your notes from. Why Gmail? because I use it, and I wrote this script for my own use. Don’t like it? Change it.

In a Nutshell
------------
- Open up your terminal to wherever you stuck this folder.
- type `python dayone_to_evernote_sync.py`
- follow the onscreen prompts to fill in your information, this is all stored in a simple XML file, so you don’t have to enter it time and time again.
- Your Gmail password, however, is not stored, so you will have to enter that each time


Limitations
------------
- **You can expect errors** I *think* I have all of the encoding errors out of the way, but the only way to be sure is to test it more. However, as long as I’m using Gmail, after a while of transferring, the SMTP connection closes.

    Traceback (most recent call last):
    File "dayone_to_evernote_sync.py", line 246, in <module>
    smtpserver.sendmail(gmailadd, enmail, msg.as_string())
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 700, in sendmail
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 441, in rset
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 366, in docmd
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/smtplib.py", line 343, in getreply
    smtplib.SMTPServerDisconnected: Connection unexpectedly closed
    
Until I’m told otherwise, I just restart it, and it seems to work.
    
    File "dayone_to_evernote_sync.py", line 139, in <module>
    result = plistlib.readPlist(filename)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/plistlib.py", line 78, in readPlist
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/plistlib.py", line 406, in parse
xml.parsers.expat.ExpatError: no element found: line 12, column 39

This comes from a bad Day One Journal entry. The file is probably truncated for some reason.

- You will probably hit Google’s outbound daily email limit. This is the biggest reason for integrating with Evernote’s API instead. But, this is just proof-of-concept.
- Doesn’t do photos right now. Sorry kids, I don’t use photos in Day One, so it wasn’t on my list of priorities.
- **Tags are only recognized as tags if they already exist in Evernote.** This is a limitation of creating Evernote entries through email instead of their API
- Not a  “true” sync, in that, if you update old entries, they won’t overwrite your entries in Evernote. There is basic checking so that the script won’t process files that have only been processed; it should only send new files.

Don't Call it a Roadmap
------------
- Eventually, I’d like to add support for photos
- integrate with [Evernote API](https://github.com/evernote/evernote-sdk-python), rather than using email
- add better unicode support.
- better error handling
- learn more about programming in python

That’s all I can think of right now. Enjoy!