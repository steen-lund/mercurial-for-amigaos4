  $ hg init repo
  $ cd repo
#if execbit
  $ hg rollback -q
#else
  $ hg tip -q
  1:ab199dc869b5
#endif
Copy and removing x bit:
  $ hg import -f -d "1000000 0" -mcopy - <<EOF
  $ test -f copy
#if execbit
  $ test ! -x copy
  $ test -x copyx
  $ hg tip -q
  2:21dfaae65c71
#else
  2:0efdaa8e3bf3
#endif

  $ hg up -qCr1
  $ hg rollback -q

Copy (like above but independent of execbit):

  $ hg import -d "1000000 0" -mcopy - <<EOF
  > diff --git a/new b/copy
  > similarity index 100%
  > copy from new
  > copy to copy
  > diff --git a/new b/copyx
  > similarity index 100%
  > copy from new
  > copy to copyx
  > EOF
  applying patch from stdin
  $ hg tip -q
  2:0efdaa8e3bf3
  $ test -f copy
  3:b1f57753fad2
  4:1bd1da94b9b2
  5:46fe99cb3035
  6:ffeb3197c12d
  7:401aede9e6bb
  8:2ef727e684e8
  8 rename2 rename3 rename3-2 / rename3 (rename2)rename3-2 (rename2)
  10:27377172366e
  11:18b73a84b4ab
  $ sed 's,EOL$,,g' <<EOF | hg import -d "1000000 0" -m spaces -
  > +++ b/foo bar	EOL
  12:47500ce1614e
  13:6757efb07ea9
  $ hg st --copies --change .

Invalid base85 content

  $ hg rollback
  repository tip rolled back to revision 14 (undo import)
  working directory now based on revision 14
  $ hg revert -aq
  $ hg import -d "1000000 0" -m invalid-binary - <<"EOF"
  > diff --git a/text2 b/binary2
  > rename from text2
  > rename to binary2
  > index 78981922613b2afb6025042ff6bd878ac1994e85..10efcb362e9f3b3420fcfbfc0e37f3dc16e29757
  > GIT binary patch
  > literal 5
  > Mc$`b*O.$Pw00T?_*Z=?k
  > 
  > EOF
  applying patch from stdin
  abort: could not decode "binary2" binary patch: bad base85 character at position 6
  [255]

  $ hg revert -aq
  $ hg import -d "1000000 0" -m rename-as-binary - <<"EOF"
  > diff --git a/text2 b/binary2
  > rename from text2
  > rename to binary2
  > index 78981922613b2afb6025042ff6bd878ac1994e85..10efcb362e9f3b3420fcfbfc0e37f3dc16e29757
  > GIT binary patch
  > literal 6
  > Mc$`b*O5$Pw00T?_*Z=?k
  > 
  > EOF
  applying patch from stdin
  abort: "binary2" length is 5 bytes, should be 6
  [255]

  $ hg revert -aq
  $ hg import -d "1000000 0" -m rename-as-binary - <<"EOF"
  > diff --git a/text2 b/binary2
  > rename from text2
  > rename to binary2
  > index 78981922613b2afb6025042ff6bd878ac1994e85..10efcb362e9f3b3420fcfbfc0e37f3dc16e29757
  > GIT binary patch
  > Mc$`b*O5$Pw00T?_*Z=?k
  > 
  > EOF
  applying patch from stdin
  abort: could not extract "binary2" binary data
  [255]

Simulate a copy/paste turning LF into CRLF (issue2870)

  $ hg revert -aq
  $ cat > binary.diff <<"EOF"
  > diff --git a/text2 b/binary2
  > rename from text2
  > rename to binary2
  > index 78981922613b2afb6025042ff6bd878ac1994e85..10efcb362e9f3b3420fcfbfc0e37f3dc16e29757
  > GIT binary patch
  > literal 5
  > Mc$`b*O5$Pw00T?_*Z=?k
  > 
  > EOF
  >>> fp = file('binary.diff', 'rb')
  >>> data = fp.read()
  >>> fp.close()
  >>> file('binary.diff', 'wb').write(data.replace('\n', '\r\n'))
  $ rm binary2
  $ hg import --no-commit binary.diff
  applying binary.diff

#if symlink

#endif

Test corner case involving copies and multiple hunks (issue3384)

  $ hg revert -qa
  $ hg import --no-commit - <<EOF
  > diff --git a/a b/c
  > copy from a
  > copy to c
  > --- a/a
  > +++ b/c
  > @@ -1,1 +1,2 @@
  >  a
  > +a
  > @@ -2,1 +2,2 @@
  >  a
  > +a
  > diff --git a/a b/a
  > --- a/a
  > +++ b/a
  > @@ -1,1 +1,2 @@
  >  a
  > +b
  > EOF
  applying patch from stdin
