#!/usr/bin/env python
# coding: UTF-8
#
# Copyright © 2015, Stew Wilson <stew@zeropointinformation.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided this permission
# notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
A script to post entries to Dreamwidth, Livejournal, and similar sites based on
a directory of Ello posts backed up using the el-takeaway tool. Post files must be named 'post-*.md'. Posts beginning with the @ character are excluded. Where more than one post is available, they will be posted in reverse-chronological order.

To install, make this file executable, then place in a directory in your executables path (e.g. ~/bin).

Usage: el2dw backup_dir -s service
"""

import sys
import os
from el2atom import PostReader
import codecs
from livejournal import livejournal

def parse_dir(dirname, last, addressed=False):
    """
    Yield a sequence of datetime string/body pairs for all the files in a
    directory in reverse name order.
    
    If last is specified, only takes posts with higher id number.
    """
    for filename in sorted(os.listdir(dirname), reverse=True):
        if filename.startswith('post-') and filename.endswith('.md'):
            path = os.path.join(dirname, filename)
            basename = filename.split('.')[0]
            post_id = basename.split('-')[1]
            if (int(post_id) < last):
                continue
            with codecs.open(path, encoding='utf8') as post_file:
                reader = PostReader(post_file)
                if not reader.addressed or addressed:
                    yield reader.datetime, post_id, reader.parse_markdown()

def emit_lj(service, posts, user, password):
    """
    Iterate over the posts generator and post each one

    Record & return last id for tracking purposes.
    """
    lj = livejournal(service, user, password)
    try:
        post_datetime, post_id, post = next(posts)
        permalink = 'http://ello.co/api/v1/posts/{0}'.format(post_id)
        trail = ''.join(["<p><small>Originally posted at <a href=",
                permalink,
                         ">Ello</a></small></p>"])
        post += trail
        lj.post('',post,post_datetime)
    except StopIteration:
        return

def main(dirname):
    """
    Main entry point.
    
    Took too much of this from el2atom; need to set this up for its own config
    file (or args) going forward.

    TODO: Fix this first.
    """

    et_file = read_dot_et_file(dirname)
    service = et_file.get("service", None)
    if not (service):
        print "Service base url not provided (e.g. www.livejournal.com, www.dreamwidth.org)"
        sys.exit(8)
    last = et_file.get("last", 0)
    user = et_file.get("lj_user", None)
    password = et_file.get("lj_hpass", None)
    if not (user and password):
        print "Livejournal username and password not present in .et file"
        sys.exit(8)
    posts = parse_dir(dirname, int(last))
    emit_lj(service, posts, user, password)


if __name__ == "__main__":
    # Do argparse bits here.
    pass

