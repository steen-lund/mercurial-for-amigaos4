# Construct the following history tree:
#
# @  5:e1bb631146ca  b1
# |
# o  4:a4fdb3b883c4 0:b608b9236435  b1
# |
# | o  3:4b57d2520816 1:44592833ba9f
# | |
# | | o  2:063f31070f65
# | |/
# | o  1:44592833ba9f
# |/
# o  0:b608b9236435

  $ hg init
  $ echo foo > foo
  $ echo zero > a
  $ hg init sub
  $ echo suba > sub/suba
  $ hg --cwd sub ci -Am addsuba
  adding suba
  $ echo 'sub = sub' > .hgsub
  $ hg ci -qAm0
  $ echo one > a ; hg ci -m1
  $ echo two > a ; hg ci -m2
  $ hg up -q 1
  $ echo three > a ; hg ci -qm3
  $ hg up -q 0
  $ hg branch -q b1
  $ echo four > a ; hg ci -qm4
  $ echo five > a ; hg ci -qm5

Initial repo state:

  $ hg --config 'extensions.graphlog=' \
  >    glog --template '{rev}:{node|short} {parents} {branches}\n'
  @  5:ff252e8273df  b1
  |
  o  4:d047485b3896 0:60829823a42a  b1
  |
  | o  3:6efa171f091b 1:0786582aa4b1
  | |
  | | o  2:bd10386d478c
  | |/
  | o  1:0786582aa4b1
  |/
  o  0:60829823a42a
  

Test helper functions:

  $ revtest () {
  >     msg=$1
  >     dirtyflag=$2   # 'clean', 'dirty' or 'dirtysub'
  >     startrev=$3
  >     targetrev=$4
  >     opt=$5
  >     hg up -qC $startrev
  >     test $dirtyflag = dirty && echo dirty > foo
  >     test $dirtyflag = dirtysub && echo dirty > sub/suba
  >     hg up $opt $targetrev
  >     hg parent --template 'parent={rev}\n'
  >     hg stat -S
  > }

  $ norevtest () {
  >     msg=$1
  >     dirtyflag=$2   # 'clean', 'dirty' or 'dirtysub'
  >     startrev=$3
  >     opt=$4
  >     hg up -qC $startrev
  >     test $dirtyflag = dirty && echo dirty > foo
  >     test $dirtyflag = dirtysub && echo dirty > sub/suba
  >     hg up $opt
  >     hg parent --template 'parent={rev}\n'
  >     hg stat -S
  > }

Test cases are documented in a table in the update function of merge.py.
Cases are run as shown in that table, row by row.

  $ norevtest 'none clean linear' clean 4
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=5

  $ norevtest 'none clean same'   clean 2
  abort: crosses branches (merge branches or update --check to force update)
  parent=2


  $ revtest 'none clean linear' clean 1 2
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=2

  $ revtest 'none clean same'   clean 2 3
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=3

  $ revtest 'none clean cross'  clean 3 4
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=4


  $ revtest 'none dirty linear' dirty 1 2
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=2
  M foo

  $ revtest 'none dirtysub linear' dirtysub 1 2
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=2
  M sub/suba

  $ revtest 'none dirty same'   dirty 2 3
  abort: crosses branches (merge branches or use --clean to discard changes)
  parent=2
  M foo

  $ revtest 'none dirtysub same'   dirtysub 2 3
  abort: crosses branches (merge branches or use --clean to discard changes)
  parent=2
  M sub/suba

  $ revtest 'none dirty cross'  dirty 3 4
  abort: crosses branches (merge branches or use --clean to discard changes)
  parent=3
  M foo

  $ revtest 'none dirtysub cross'  dirtysub 3 4
  abort: crosses branches (merge branches or use --clean to discard changes)
  parent=3
  M sub/suba

  $ revtest '-C dirty linear'   dirty 1 2 -C
  2 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=2

  $ revtest '-c dirty linear'   dirty 1 2 -c
  abort: uncommitted local changes
  parent=1
  M foo

  $ revtest '-c dirtysub linear'   dirtysub 1 2 -c
  abort: uncommitted local changes
  parent=1
  M sub/suba

  $ norevtest '-c clean same'   clean 2 -c
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  parent=3

  $ revtest '-cC dirty linear'  dirty 1 2 -cC
  abort: cannot specify both -c/--check and -C/--clean
  parent=1
  M foo

