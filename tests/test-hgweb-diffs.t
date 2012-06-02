  $ "$TESTDIR/hghave" serve execbit || exit 80
  $ chmod +x a
  $ hg rm b
  $ hg ci -Amb
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT '/rev/0'
  <h2><a href="/">test</a></h2>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
      <a id="diffstatexpand" href="javascript:showDiffstat()"/>[<tt>+</tt>]</a>
        <a href="javascript:hideDiffstat()"/>[<tt>-</tt>]</a>
        <table>  <tr class="parity0">
    <tr class="parity1">
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> <span class="minusline">--- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.2" id="l1.2">     1.2</a> <span class="plusline">+++ b/a	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="plusline">+a
  </span></pre></div><div class="source bottomline parity1"><pre><a href="#l2.1" id="l2.1">     2.1</a> <span class="minusline">--- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l2.2" id="l2.2">     2.2</a> <span class="plusline">+++ b/b	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l2.3" id="l2.3">     2.3</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l2.4" id="l2.4">     2.4</a> <span class="plusline">+b
  </span></pre></div>
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT '/raw-rev/0'
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT '/diff/tip/b'
  <h2><a href="/">test</a></h2>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
  
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> <span class="minusline">--- a/b	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.2" id="l1.2">     1.2</a> <span class="plusline">+++ /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="atline">@@ -1,1 +0,0 @@
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="minusline">-b
  </span></pre></div>
  $ "$TESTDIR/killdaemons.py"
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT '/rev/0'
  <h2><a href="/">test</a></h2>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
      <a id="diffstatexpand" href="javascript:showDiffstat()"/>[<tt>+</tt>]</a>
        <a href="javascript:hideDiffstat()"/>[<tt>-</tt>]</a>
        <table>  <tr class="parity0">
    <tr class="parity1">
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> new file mode 100644
  <a href="#l1.2" id="l1.2">     1.2</a> <span class="minusline">--- /dev/null
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="plusline">+++ b/a
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l1.5" id="l1.5">     1.5</a> <span class="plusline">+a
  </span></pre></div><div class="source bottomline parity1"><pre><a href="#l2.1" id="l2.1">     2.1</a> new file mode 100644
  <a href="#l2.2" id="l2.2">     2.2</a> <span class="minusline">--- /dev/null
  </span><a href="#l2.3" id="l2.3">     2.3</a> <span class="plusline">+++ b/b
  </span><a href="#l2.4" id="l2.4">     2.4</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l2.5" id="l2.5">     2.5</a> <span class="plusline">+b
  </span></pre></div>
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT '/raw-rev/0'