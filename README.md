# redditt

A command line python Reddit application for Linux.

## Getting Started

Setup redditt to use the Reddit API
* Requires [Reddit account](https://www.reddit.com/)
* Requires [OAuth for authentication](https://github.com/reddit/reddit/wiki/OAuth2)
* Edit praw.ini and fill in the `client_id`, `client_secret`, `username`, and `password` details generated from OAuth instructions
* Run `redditt`

### Prerequisites

* python 3.7

### Installing

Pip install:
```
pip install praw
pip install urwid
```

## Built With

* [Praw](https://praw.readthedocs.io/en/latest/) - The Python Reddit API Wrapper
* [urwid](http://urwid.org/) - Console user interface library for Python
