#!/usr/bin/env python3

import pstats
from pstats import SortKey
p = pstats.Stats('runstats.dat')
p.sort_stats(SortKey.CUMULATIVE).print_stats(30)
