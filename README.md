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

### A rewrite around message passing ?
A state table is preserved and updated with requests and state of completion.
Spinners are handling them.

That way we can have a fully isolated interface from implementation.

### DB access getting too slow.
Removing as much as possible from useless threads: removing comments, content, etc.
Just keeping etags.
