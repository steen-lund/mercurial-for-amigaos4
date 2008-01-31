# Command for sending a collection of Mercurial changesets as a series
# of patch emails.
#
# The series is started off with a "[PATCH 0 of N]" introduction,
# which describes the series as a whole.
#
# Each patch email has a Subject line of "[PATCH M of N] ...", using
# the first line of the changeset description as the subject text.
# The message contains two or three body parts:
#
#   The remainder of the changeset description.
#
#   [Optional] If the diffstat program is installed, the result of
#   running diffstat on the patch.
#
#   The patch itself, as generated by "hg export".
#
# Each message refers to all of its predecessors using the In-Reply-To
# and References headers, so they will show up as a sequence in
# threaded mail and news readers, and in mail archives.
#
# For each changeset, you will be prompted with a diffstat summary and
# the changeset summary, so you can be sure you are sending the right
# changes.
#
# To enable this extension:
#
#   [extensions]
#   hgext.patchbomb =
#
# To configure other defaults, add a section like this to your hgrc
# file:
#
#   [email]
#   from = My Name <my@email>
#   to = recipient1, recipient2, ...
#   cc = cc1, cc2, ...
#   bcc = bcc1, bcc2, ...
#
# Then you can use the "hg email" command to mail a series of changesets
# as a patchbomb.
#
# To avoid sending patches prematurely, it is a good idea to first run
# the "email" command with the "-n" option (test only).  You will be
# prompted for an email recipient address, a subject an an introductory
# message describing the patches of your patchbomb.  Then when all is
# done, patchbomb messages are displayed. If PAGER environment variable
# is set, your pager will be fired up once for each patchbomb message, so
# you can verify everything is alright.
#
# The "-m" (mbox) option is also very useful.  Instead of previewing
# each patchbomb message in a pager or sending the messages directly,
# it will create a UNIX mailbox file with the patch emails.  This
# mailbox file can be previewed with any mail user agent which supports
# UNIX mbox files, i.e. with mutt:
#
#   % mutt -R -f mbox
#
# When you are previewing the patchbomb messages, you can use `formail'
# (a utility that is commonly installed as part of the procmail package),
# to send each message out:
#
#  % formail -s sendmail -bm -t < mbox
#
# That should be all.  Now your patchbomb is on its way out.

import os, errno, socket, tempfile
import email.MIMEMultipart, email.MIMEText, email.MIMEBase
import email.Utils, email.Encoders
from mercurial import cmdutil, commands, hg, mail, ui, patch, util
from mercurial.i18n import _
from mercurial.node import *

def patchbomb(ui, repo, *revs, **opts):
    '''send changesets by email

    By default, diffs are sent in the format generated by hg export,
    one per message.  The series starts with a "[PATCH 0 of N]"
    introduction, which describes the series as a whole.

    Each patch email has a Subject line of "[PATCH M of N] ...", using
    the first line of the changeset description as the subject text.
    The message contains two or three body parts.  First, the rest of
    the changeset description.  Next, (optionally) if the diffstat
    program is installed, the result of running diffstat on the patch.
    Finally, the patch itself, as generated by "hg export".

    With --outgoing, emails will be generated for patches not
    found in the destination repository (or only those which are
    ancestors of the specified revisions if any are provided)

    With --bundle, changesets are selected as for --outgoing,
    but a single email containing a binary Mercurial bundle as an
    attachment will be sent.

    Examples:

    hg email -r 3000          # send patch 3000 only
    hg email -r 3000 -r 3001  # send patches 3000 and 3001
    hg email -r 3000:3005     # send patches 3000 through 3005
    hg email 3000             # send patch 3000 (deprecated)

    hg email -o               # send all patches not in default
    hg email -o DEST          # send all patches not in DEST
    hg email -o -r 3000       # send all ancestors of 3000 not in default
    hg email -o -r 3000 DEST  # send all ancestors of 3000 not in DEST

    hg email -b               # send bundle of all patches not in default
    hg email -b DEST          # send bundle of all patches not in DEST
    hg email -b -r 3000       # bundle of all ancestors of 3000 not in default
    hg email -b -r 3000 DEST  # bundle of all ancestors of 3000 not in DEST

    Before using this command, you will need to enable email in your hgrc.
    See the [email] section in hgrc(5) for details.
    '''

    def prompt(prompt, default = None, rest = ': ', empty_ok = False):
        if not ui.interactive:
            return default
        if default:
            prompt += ' [%s]' % default
        prompt += rest
        while True:
            r = ui.prompt(prompt, default=default)
            if r:
                return r
            if default is not None:
                return default
            if empty_ok:
                return r
            ui.warn(_('Please enter a valid value.\n'))

    def confirm(s, denial):
        if not prompt(s, default = 'y', rest = '? ').lower().startswith('y'):
            raise util.Abort(denial)

    def cdiffstat(summary, patchlines):
        s = patch.diffstat(patchlines)
        if s:
            if summary:
                ui.write(summary, '\n')
                ui.write(s, '\n')
            confirm(_('Does the diffstat above look okay'),
                    _('diffstat rejected'))
        elif s is None:
            ui.warn(_('No diffstat information available.\n'))
            s = ''
        return s

    def makepatch(patch, idx, total):
        desc = []
        node = None
        body = ''
        for line in patch:
            if line.startswith('#'):
                if line.startswith('# Node ID'):
                    node = line.split()[-1]
                continue
            if line.startswith('diff -r') or line.startswith('diff --git'):
                break
            desc.append(line)
        if not node:
            raise ValueError

        if opts['attach']:
             body = ('\n'.join(desc[1:]).strip() or
                   'Patch subject is complete summary.')
             body += '\n\n\n'

        if opts.get('plain'):
            while patch and patch[0].startswith('# '):
                patch.pop(0)
            if patch:
                patch.pop(0)
            while patch and not patch[0].strip():
                patch.pop(0)
        if opts.get('diffstat'):
            body += cdiffstat('\n'.join(desc), patch) + '\n\n'
        if opts.get('attach') or opts.get('inline'):
            msg = email.MIMEMultipart.MIMEMultipart()
            if body:
                msg.attach(email.MIMEText.MIMEText(body, 'plain'))
            p = email.MIMEText.MIMEText('\n'.join(patch), 'x-patch')
            binnode = bin(node)
            # if node is mq patch, it will have patch file name as tag
            patchname = [t for t in repo.nodetags(binnode)
                         if t.endswith('.patch') or t.endswith('.diff')]
            if patchname:
                patchname = patchname[0]
            elif total > 1:
                patchname = cmdutil.make_filename(repo, '%b-%n.patch',
                                                  binnode, idx, total)
            else:
                patchname = cmdutil.make_filename(repo, '%b.patch', binnode)
            disposition = 'inline'
            if opts['attach']:
                disposition = 'attachment'
            p['Content-Disposition'] = disposition + '; filename=' + patchname
            msg.attach(p)
        else:
            body += '\n'.join(patch)
            msg = email.MIMEText.MIMEText(body)

        subj = desc[0].strip().rstrip('. ')
        if total == 1:
            subj = '[PATCH] ' + (opts.get('subject') or subj)
        else:
            tlen = len(str(total))
            subj = '[PATCH %0*d of %d] %s' % (tlen, idx, total, subj)
        msg['Subject'] = subj
        msg['X-Mercurial-Node'] = node
        return msg

    def outgoing(dest, revs):
        '''Return the revisions present locally but not in dest'''
        dest = ui.expandpath(dest or 'default-push', dest or 'default')
        revs = [repo.lookup(rev) for rev in revs]
        other = hg.repository(ui, dest)
        ui.status(_('comparing with %s\n') % dest)
        o = repo.findoutgoing(other)
        if not o:
            ui.status(_("no changes found\n"))
            return []
        o = repo.changelog.nodesbetween(o, revs or None)[0]
        return [str(repo.changelog.rev(r)) for r in o]

    def getbundle(dest):
        tmpdir = tempfile.mkdtemp(prefix='hg-email-bundle-')
        tmpfn = os.path.join(tmpdir, 'bundle')
        try:
            commands.bundle(ui, repo, tmpfn, dest, **opts)
            return open(tmpfn, 'rb').read()
        finally:
            try:
                os.unlink(tmpfn)
            except:
                pass
            os.rmdir(tmpdir)

    if not (opts.get('test') or opts.get('mbox')):
        # really sending
        mail.validateconfig(ui)

    if not (revs or opts.get('rev')
            or opts.get('outgoing') or opts.get('bundle')):
        raise util.Abort(_('specify at least one changeset with -r or -o'))

    cmdutil.setremoteconfig(ui, opts)
    if opts.get('outgoing') and opts.get('bundle'):
        raise util.Abort(_("--outgoing mode always on with --bundle;"
                           " do not re-specify --outgoing"))

    if opts.get('outgoing') or opts.get('bundle'):
        if len(revs) > 1:
            raise util.Abort(_("too many destinations"))
        dest = revs and revs[0] or None
        revs = []

    if opts.get('rev'):
        if revs:
            raise util.Abort(_('use only one form to specify the revision'))
        revs = opts.get('rev')

    if opts.get('outgoing'):
        revs = outgoing(dest, opts.get('rev'))
    if opts.get('bundle'):
        opts['revs'] = revs

    # start
    if opts.get('date'):
        start_time = util.parsedate(opts.get('date'))
    else:
        start_time = util.makedate()

    def genmsgid(id):
        return '<%s.%s@%s>' % (id[:20], int(start_time[0]), socket.getfqdn())

    def getdescription(body, sender):
        if opts.get('desc'):
            body = open(opts.get('desc')).read()
        else:
            ui.write(_('\nWrite the introductory message for the '
                       'patch series.\n\n'))
            body = ui.edit(body, sender)
        return body

    def getexportmsgs():
        patches = []

        class exportee:
            def __init__(self, container):
                self.lines = []
                self.container = container
                self.name = 'email'

            def write(self, data):
                self.lines.append(data)

            def close(self):
                self.container.append(''.join(self.lines).split('\n'))
                self.lines = []

        commands.export(ui, repo, *revs, **{'output': exportee(patches),
                                            'switch_parent': False,
                                            'text': None,
                                            'git': opts.get('git')})

        jumbo = []
        msgs = []

        ui.write(_('This patch series consists of %d patches.\n\n')
                 % len(patches))

        for p, i in zip(patches, xrange(len(patches))):
            jumbo.extend(p)
            msgs.append(makepatch(p, i + 1, len(patches)))

        if len(patches) > 1:
            tlen = len(str(len(patches)))

            subj = '[PATCH %0*d of %d] %s' % (
                tlen, 0, len(patches),
                opts.get('subject') or
                prompt('Subject:',
                       rest=' [PATCH %0*d of %d] ' % (tlen, 0, len(patches))))

            body = ''
            if opts.get('diffstat'):
                d = cdiffstat(_('Final summary:\n'), jumbo)
                if d:
                    body = '\n' + d

            body = getdescription(body, sender)
            msg = email.MIMEText.MIMEText(body)
            msg['Subject'] = subj

            msgs.insert(0, msg)
        return msgs

    def getbundlemsgs(bundle):
        subj = (opts.get('subject')
                or prompt('Subject:', default='A bundle for your repository'))

        body = getdescription('', sender)
        msg = email.MIMEMultipart.MIMEMultipart()
        if body:
            msg.attach(email.MIMEText.MIMEText(body, 'plain'))
        datapart = email.MIMEBase.MIMEBase('application', 'x-mercurial-bundle')
        datapart.set_payload(bundle)
        datapart.add_header('Content-Disposition', 'attachment',
                            filename='bundle.hg')
        email.Encoders.encode_base64(datapart)
        msg.attach(datapart)
        msg['Subject'] = subj
        return [msg]

    sender = (opts.get('from') or ui.config('email', 'from') or
              ui.config('patchbomb', 'from') or
              prompt('From', ui.username()))

    if opts.get('bundle'):
        msgs = getbundlemsgs(getbundle(dest))
    else:
        msgs = getexportmsgs()

    def getaddrs(opt, prpt, default = None):
        addrs = opts.get(opt) or (ui.config('email', opt) or
                                  ui.config('patchbomb', opt) or
                                  prompt(prpt, default = default)).split(',')
        return [a.strip() for a in addrs if a.strip()]

    to = getaddrs('to', 'To')
    cc = getaddrs('cc', 'Cc', '')

    bcc = opts.get('bcc') or (ui.config('email', 'bcc') or
                          ui.config('patchbomb', 'bcc') or '').split(',')
    bcc = [a.strip() for a in bcc if a.strip()]

    ui.write('\n')

    parent = None

    sender_addr = email.Utils.parseaddr(sender)[1]
    sendmail = None
    for m in msgs:
        try:
            m['Message-Id'] = genmsgid(m['X-Mercurial-Node'])
        except TypeError:
            m['Message-Id'] = genmsgid('patchbomb')
        if parent:
            m['In-Reply-To'] = parent
        else:
            parent = m['Message-Id']
        m['Date'] = util.datestr(date=start_time,
                                 format="%a, %d %b %Y %H:%M:%S", timezone=True)

        start_time = (start_time[0] + 1, start_time[1])
        m['From'] = sender
        m['To'] = ', '.join(to)
        if cc:
            m['Cc']  = ', '.join(cc)
        if bcc:
            m['Bcc'] = ', '.join(bcc)
        if opts.get('test'):
            ui.status('Displaying ', m['Subject'], ' ...\n')
            ui.flush()
            if 'PAGER' in os.environ:
                fp = os.popen(os.environ['PAGER'], 'w')
            else:
                fp = ui
            try:
                fp.write(m.as_string(0))
                fp.write('\n')
            except IOError, inst:
                if inst.errno != errno.EPIPE:
                    raise
            if fp is not ui:
                fp.close()
        elif opts.get('mbox'):
            ui.status('Writing ', m['Subject'], ' ...\n')
            fp = open(opts.get('mbox'), 'In-Reply-To' in m and 'ab+' or 'wb+')
            date = util.datestr(date=start_time,
                                format='%a %b %d %H:%M:%S %Y', timezone=False)
            fp.write('From %s %s\n' % (sender_addr, date))
            fp.write(m.as_string(0))
            fp.write('\n\n')
            fp.close()
        else:
            if not sendmail:
                sendmail = mail.connect(ui)
            ui.status('Sending ', m['Subject'], ' ...\n')
            # Exim does not remove the Bcc field
            del m['Bcc']
            sendmail(sender, to + bcc + cc, m.as_string(0))

cmdtable = {
    "email":
        (patchbomb,
         [('a', 'attach', None, _('send patches as attachments')),
          ('i', 'inline', None, _('send patches as inline attachments')),
          ('', 'bcc', [], _('email addresses of blind copy recipients')),
          ('c', 'cc', [], _('email addresses of copy recipients')),
          ('d', 'diffstat', None, _('add diffstat output to messages')),
          ('', 'date', '', _('use the given date as the sending date')),
          ('', 'desc', '', _('use the given file as the series description')),
          ('g', 'git', None, _('use git extended diff format')),
          ('f', 'from', '', _('email address of sender')),
          ('', 'plain', None, _('omit hg patch header')),
          ('n', 'test', None, _('print messages that would be sent')),
          ('m', 'mbox', '',
           _('write messages to mbox file instead of sending them')),
          ('o', 'outgoing', None,
           _('send changes not found in the target repository')),
          ('b', 'bundle', None,
           _('send changes not in target as a binary bundle')),
          ('r', 'rev', [], _('a revision to send')),
          ('s', 'subject', '',
           _('subject of first message (intro or single patch)')),
          ('t', 'to', [], _('email addresses of recipients')),
          ('', 'force', None,
           _('run even when remote repository is unrelated (with -b)')),
          ('', 'base', [],
           _('a base changeset to specify instead of a destination (with -b)')),
         ] + commands.remoteopts,
         _('hg email [OPTION]... [DEST]...'))
}
