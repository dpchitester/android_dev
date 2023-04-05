import os
import json
from functools import partial

from opbase import OpBaseEncoder

import config_vars as v
from config_funcs import *

addPre('FLAGS', os.environ['HOME'])
# print("FLAGS=" + str(ppre('FLAGS')))

v.edgepf = ppre('FLAGS') / 'edges.pp'
v.ldllsf = ppre('FLAGS') / 'ldlls.pp'
v.rdllsf = ppre('FLAGS') / 'rdlls.pp'
v.fmd5hf = ppre('FLAGS') / 'fmd5h.pp'
v.ldhpf = ppre('FLAGS') / 'ldhd.pp'
v.rdhpf = ppre('FLAGS') / 'rdhd.pp'
#print("pf's set now")
#for pf in [edgepf, ldllsf, rdllsf, fmd5hf, ldhpf, rdhpf]:
#    print(pf.name, str(pf))

from edge import addDep, addArc

import ldsv

ldsv.load_all()

from gitops import gitck1, gitck2, gitremoteck

from localcopy import LocalCopy
from gitops import GitOps
from cscopy import CSCopy
from csrestore import CSRestore
from mkzip import Mkzip

addPre('sd', '/sdcard')
addPre('proj', ppre('sd') / 'projects')
addPre('bkx', ppre('FLAGS') / '.bkx')
addPre('gd', 'GoogleDrive:')
addPre('dsblog', os.environ['FDB_PATH'])

addSrcDir('docs', ppre('sd') / 'Documents', False)
addSrcDir('blogds', ppre('dsblog'), False)
addSrcDir('backups', ppre('sd') / 'backups', False)
addSrcDir('home', ppre('FLAGS'), False)
addSrcDir('bin', pdir('home') / 'bin', False)

def f1():
    dl = getDL(ppre('proj'))
    for d in dl:
        addSrcDir(d.name, d, True)
        addDep('git_index', d.name)
        addDep('zips', d.name)
        addDep('proj', d.name)

f1()

addSrcDir('zips', ppre('sd') / 'zips', False)

v.worktree = ppre('sd') / 'projects'

v.srcs.add('git_index')
v.lckers['git_index'] = partial(gitck1, 'git_index', v.worktree)

addSrcDir('.git', ppre('proj') / '.git', False)
v.lckers['git'] = partial(gitck2, 'git', v.worktree)

v.tgts.add('bitbucket')
v.tgts.add('github')
# v.srcs.add('bitbucket')
v.rckers['bitbucket'] = partial(gitremoteck, 'bitbucket', v.worktree)
v.rckers['github'] = partial(gitremoteck, 'github', v.worktree)

addSrcDir('proj', ppre('proj'), False)

addTgtDir('home', ppre('FLAGS'))
addTgtDir('bin', tdir('home') / 'bin')
addTgtDir('sh', tdir('home') / 'bin/sh')
addTgtDir('pl', tdir('home') / 'bin/pl')
addTgtDir('backups', ppre('sd') / 'backups')
addTgtDir('zips', ppre('sd') / 'zips')
addTgtDir('blogds', ppre('dsblog'))
addTgtDir('blog', ppre('proj') / 'blog')
addTgtDir('termux-backup', ppre('sd') / 'backups' / 'termux-backup')
addTgtDir('bash', ppre('proj') / 'bash')
addTgtDir('plaid-node', ppre('proj') / 'plaid-node')


npl1 = ('bash', 'home')
op1 = LocalCopy(
    npl1, npl1, {
        'files': [
            '.termux/*', '.bashrc', '.bashrc0', '.swi*', '.profile', '.clang-format',
            'rsyncd.conf', '.config/rclone/*', '.plaid-cli/*',
            '.plaid-cli/data/*', '.plaidrc'
        ]
    })
#addArc(op1)

npl1 = ('home', 'bash')
op1 = LocalCopy(
    npl1, npl1, {
        'files': [
            '.termux/*', '.bashrc', '.bashrc0', '.swi*', '.profile', '.clang-format',
            'rsyncd.conf', '.config/rclone/*', '.plaid-cli/*',
            '.plaid-cli/data/*', '.plaidrc'
        ]
    })
addArc(op1)

npl1 = ('bin', 'bash')
op1 = LocalCopy(npl1, npl1, {
    'files': ['termux-*', 'pbu', 'rbu'],
    'exec': True
})
addArc(op1)

npl1 = ('bash', 'bin')
op1 = LocalCopy(npl1, npl1, {
    'files': ['termux-*', 'pbu', 'rbu'],
    'exec': False
})
addArc(op1)

npl1 = ('sh', 'bash')
op1 = LocalCopy(npl1, npl1, {'files': ['*.sh', '*.env'], 'exec': True})
addArc(op1)

npl1 = ('blogds', 'blog')
op1 = LocalCopy(npl1, npl1, {'files': ['blog.js']})
addArc(op1)

npl1 = ('blog', 'blogds')
op1 = LocalCopy(npl1, npl1, {'files': ['*.db', 'blog.js']})
addArc(op1)

npl1 = ('plaid-node', 'blogds')
op1 = LocalCopy(npl1, npl1, {'files': ['*.db']})
addArc(op1)

#npl1 = ('termux-backup', 'home')
#op1 = LocalCopy(npl1, npl1, {'files': ['**/*.*']})
#addArc(op1)

npl1 = ('backups', 'blogds')
op1 = LocalCopy(npl1, npl1, {'files': ['*.db']})
addArc(op1)

if 'NOGIT' not in os.environ:
    npl1 = ('git', 'git_index')
    op1 = GitOps(npl1, None, {'wt': v.worktree, 'add': True, 'commit': True})
    addArc(op1)

    npl1 = ('bitbucket', 'git')
    op1 = GitOps(npl1, None, {
        'wt': v.worktree,
        'rmt': 'bitbucket',
        'pull': True,
        'push': True
    })
    addArc(op1)
    
    npl1 = ('github', 'git')
    op1 = GitOps(npl1, None, {
        'wt': v.worktree,
        'rmt': 'github',
        'pull': True,
        'push': True
    })
    addArc(op1)

for si in v.codes:
    npl1 = ('zips', si)
    op1 = Mkzip(npl1, npl1, {'zipfile': si + '.zip'})
    addArc(op1)

for si in ('.git', ):
    npl1 = ('zips', si)
    op1 = Mkzip(npl1, npl1, {'zipfile': 'projects-git.zip'})
    addArc(op1)

for si in ('proj', 'zips'):
    p1 = pdir(si).relative_to(ppre('sd'))
    addTgtDir('gd_' + si, ppre('gd') / p1)
    npl1 = ('gd_' + si, si)
    #op1 = CSRestore(npl1, None, {})
    #addArc(op1)
    op1 = CSCopy(npl1, npl1, {'delete': False})
    addArc(op1)
