# -*- coding: utf-8 -*-

import vim
from ncm2 import Ncm2Source, getLogger
import re
from copy import deepcopy

logger = getLogger(__name__)


class Source(Ncm2Source):

    def on_complete(self, ctx):
        pat = re.compile(ctx['word_pattern'])
        lines = 1000

        lnum = ctx['lnum']
        ccol = ctx['ccol']
        b = ctx['base']

        bufnr = ctx['bufnr']
        buf = vim.buffers[bufnr]

        matches = []

        matcher = self.matcher_get(ctx['matcher'])

        matches = []
        seen = {}

        beginl = max(lnum - 1 - int(lines / 2), 0)
        endl = lnum - 1 + int(lines / 2)
        stepl = 1000
        for lidx in range(beginl, endl, stepl):
            lines = buf[lidx: min(lidx + stepl, endl)]
            # convert 0 base to 1 base
            for i, line in enumerate(lines):
                scan_lnum = lidx + i + 1
                if scan_lnum == lnum:
                    for word in pat.finditer(line):
                        span = word.span()
                        # filter-out the word at current cursor
                        if (ccol - 1 >= span[0]) and (ccol - 1 <= span[1]):
                            continue
                        w = word.group()
                        item = self.match_formalize(ctx, w)
                        if not matcher(b, item):
                            continue
                        if w not in seen:
                            seen[w] = item
                            item['user_data']['location'] = []
                            item['user_data']['word'] = w
                            matches.append(item)
                        ud = seen[w]['user_data']
                        ud['location'].append(
                            dict(lnum=scan_lnum,
                                 ccol=word.start() + 1,
                                 bufnr=bufnr))
                else:
                    for word in pat.finditer(line):
                        w = word.group()
                        item = self.match_formalize(ctx, w)
                        if not matcher(b, item):
                            continue
                        if w not in seen:
                            seen[w] = item
                            item['user_data']['location'] = []
                            item['user_data']['word'] = w
                            matches.append(item)
                        ud = seen[w]['user_data']
                        ud['location'].append(
                            dict(lnum=scan_lnum,
                                 ccol=word.start() + 1,
                                 bufnr=bufnr))

        self.complete(ctx, ctx['startccol'], matches)

    def on_completed(self, ctx, completed):
        ud = completed['user_data']
        word = ud['word']
        location = ud['location']

        pat = re.compile(ctx['word_pattern'])

        matches = []
        seen = {}

        for loc in location:
            bufnr = loc['bufnr']
            lnum = loc['lnum']
            # ignore for current line
            if bufnr == ctx['bufnr'] and lnum == ctx['lnum']:
                logger.info("ignore current line %s", loc)
                continue

            ccol = loc['ccol']
            buf = vim.buffers[bufnr]
            line = buf[lnum - 1]

            logger.debug("line [%s]", line)

            cur_word_end = ccol - 1 + len(word)
            cur_word = line[ccol - 1: cur_word_end]
            if word != cur_word:
                logger.debug('word [%s] != cur word [%s]', word, cur_word)
                continue

            searchstr = line[cur_word_end: ]
            for mat in pat.finditer(searchstr):
                w = searchstr[: mat.end()]
                item = {'user_data': {}}
                if w not in seen:
                    seen[w] = item
                    item['user_data']['location'] = []
                    item['user_data']['word'] = w
                    matches.append(item)
                item['word'] = w
                ud = seen[w]['user_data']
                new_loc = deepcopy(loc)
                new_loc['ccol'] = cur_word_end + 1
                ud['location'].append(new_loc)
                break

        self.complete(ctx, ctx['ccol'], matches)

source = Source(vim)

on_complete = source.on_complete
on_completed = source.on_completed
