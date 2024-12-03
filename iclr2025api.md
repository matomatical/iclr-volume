Structure of a submission:

(See also https://docs.openreview.net/reference/api-v2/entities/note/fields)

```python
Note(
# location
    domain:             'ICLR.cc/2025/Conference',
    forum:              str,        # unique hash used in URL
    number:             int,        # submission number (sequential)
# tree structure
    id:                 str,        # same as forum hash
    replyto:            None,       # empty for root post
# times
    cdate:              tstamp,     # creation date (paper or abstract created)
    mdate:              tstamp,     # modification date (paper or metadata)
    odate:              tstamp,     # online date (paper made public)
    pdate:              tstamp,     # publication date (paper marked accepted)
    ddate:              tstamp,     # soft deletion date
    tcdate:             tstamp,     # true creation date (can't be altered)
    tmdate:             tstamp,     # true modification date (can't be altered)
# permissions
    writers:            list[str]   # groups that can edit (usu. conf + auth)
    readers:            list[str]   # groups that can read (usu. ['everyone'])
    nonreaders:         list[str]   # groups that can't read this (usu. None)
    signatures:         list[str]   # who posted this (always one element)
    invitations:        list[str]   # tag for different phases of review process
    license:            'CC BY 4.0',
# content
    content: {
        'title':        Value[str],
        'TLDR':         Value[str],
        'abstract':     Value[str],
        'keywords':     Value[list[str]],
        'primary_area': Value[str],
        'pdf':          Value[str],
        '_bibtex':      Value[str],
        'venue':        Value['ICLR 2025 Conference Submission'],
        'venueid':      Value['ICLR.cc/2025/Conference/Submission'],
        # plus a few more standard disclaimer strings...
    },
# replies
    details: {'directReplies': list[{
    # location
        'domain':       'ICLR.cc/2025/Conference',        
        'forum':        str,        # same as above
        'number':       int,        # comment number (sequential within forum)
        'version':      int,        # iteration (1 + num edits)
    # tree structure
        'id':           str,        # id hashcode
        'replyto':      str,        # parent's id
    # times
        'cdate':        tstamp,     # creation time?
        'mdate':        tstamp,     # modification time?
        'tcdate':       tstamp,     # ???
        'tmdate':       tstamp,     # ???
    # permissions
        'writers':      list[str],
        'readers':      list[str],
        'nonreaders':   list[str],
        'signatures':   list[str],
        'invitations':  list[str],
        'license':      'CC BY 4.0',
    # content
        'content':      {
        # FOR A REVIEW
            'summary':                  Value[str],
            'soundness':                Value[int],
            'presentation':             Value[int],
            'contribution':             Value[int],
            'strengths':                Value[str],
            'weaknesses':               Value[str],
            'questions':                Value[str],
            'rating':                   Value[int],
            'confidence':               Value[int],
            # plus a few more standard disclaimer strings...
        # FOR AN OFFICIAL COMMENT
            'title':                    Value[str],
            'comment':                  Value[str],
        },
    }]},
)
```
