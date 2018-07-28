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

        def add_match(bufnr, re_match, lnum):
            w = re_match.group()
            if w in seen:
                item = seen[w]
                ud = item['user_data']
            else:
                item = self.match_formalize(ctx, w)
                if not matcher(b, item):
                    return
                seen[w] = item
                ud = item['user_data']
                ud['location'] = []
                ud['word'] = w
                matches.append(item)
            ud['location'].append(dict(lnum=lnum,
                                       word=w,
                                       ccol=re_match.start() + 1,
                                       bufnr=bufnr))

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
                        add_match(bufnr, word, scan_lnum)
                else:
                    for word in pat.finditer(line):
                        add_match(bufnr, word, scan_lnum)

        self.complete(ctx, ctx['startccol'], matches)

    def on_completed(self, ctx, completed):
        ud = completed['user_data']
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
            lines = buf[lnum - 1: lnum - 1 + 2]
            line = lines[0]
            if len(lines) > 1:
                next_line = lines[1]
            else:
                next_line = ''

            logger.debug("line [%s]", line)

            word = loc['word']
            cur_word_end = ccol - 1 + len(word)
            cur_word = line[ccol - 1: cur_word_end]

            if word != cur_word:
                logger.debug('word [%s] != cur word [%s]', word, cur_word)
                continue

            if cur_word_end == len(line):
                search_text = next_line
                mat = pat.search(search_text)
                if mat is None:
                    continue
                w = search_text[: mat.end()]
                search_text = next_line
                new_loc = deepcopy(loc)
                new_loc['ccol'] = 1
                new_loc['lnum'] += 1
                new_loc['word'] = w
                w = ' ' + w
            else:
                search_text = line[cur_word_end:]
                mat = pat.search(search_text)
                if mat is None:
                    w = search_text
                else:
                    w = search_text[: mat.end()]
                new_loc = deepcopy(loc)
                new_loc['ccol'] = cur_word_end + 1
                new_loc['word'] = w

            item = {'user_data': {}}
            if w not in seen:
                seen[w] = item
                item['user_data']['location'] = []
                item['user_data']['word'] = w
                matches.append(item)
            item['word'] = w
            ud = seen[w]['user_data']
            ud['location'].append(new_loc)

        self.complete(ctx, ctx['ccol'], matches)


source = Source(vim)

on_complete = source.on_complete
on_completed = source.on_completed
