# -*- coding: utf-8 -*-

import vim
from ncm2 import Ncm2Source
import re


class Source(Ncm2Source):

    def on_complete(self, ctx):
        pat = re.compile(ctx['word_pattern'])
        lines = 1000

        lnum = ctx['lnum']
        ccol = ctx['ccol']
        b = ctx['base']

        begin = max(lnum - 1 - int(lines / 2), 0)
        end = lnum - 1 + int(lines / 2)

        buf = vim.buffers[ctx['bufnr']]

        matches = []

        matcher = self.matcher_get(ctx['matcher'])

        seen = {}

        step = 1000
        for lidx in range(begin, end, step):
            lines = buf[lidx: min(lidx + step, end)]
            # convert 0 base to 1 base
            for i, line in enumerate(lines):
                if lidx + i + 1 == lnum:
                    for word in pat.finditer(line):
                        span = word.span()
                        # filter-out the word at current cursor
                        if (ccol - 1 >= span[0]) and (ccol - 1 <= span[1]):
                            continue
                        w = word.group()
                        m = self.match_formalize(ctx, w)
                        if w not in seen and matcher(b, m):
                            seen[w] = True
                            matches.append(m)
                else:
                    for word in pat.finditer(line):
                        w = word.group()
                        m = self.match_formalize(ctx, w)
                        if w not in seen and matcher(b, m):
                            seen[w] = True
                            matches.append(m)

        self.complete(ctx, ctx['startccol'], matches)


source = Source(vim)

on_complete = source.on_complete
