# TkYt : Youtube for TK

## Stuff

### Priority guidelines

  * Lowest priority value first
  *        0: interactive
  *       10: very high priority
  *      100: high priority
  *    1.000: good priority
  *   10.000: low priority
  *  100.000: lowest priority
  * 1000.000: won't do

Priority booster: 0-10:
0 : Do not
1-10: do with more priority, 10 will cross the above scale by one level.

## Feature requests

### Summary, by importance
  - Enhancement of UI
    - 3 oldest and newest instead of one
    - Data about video with threads
    - User image
  - Shadow banning check
  - DB speed enhancement


### A rewrite around message passing ?
A state table is preserved and updated with requests and state of completion.
Spinners are handling them.

That way we can have a fully isolated interface from implementation.

### Most recent has_me comment from an yid
Seems useful, but costly.

### Shadow banning check
Using another account and read each 0 scored whith_me threads and ensure it still evaluates to zero.

### DB access getting too slow.
Likely not removing as much as possible from useless threads, as it proves usefull.
Secondary Table (or just indexes?) with only relevant threads.
