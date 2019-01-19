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

        matcher = self.matcher_get(ctx)

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
                ud['word'] = w
                matches.append(item)

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


source = Source(vim)

on_complete = source.on_complete
