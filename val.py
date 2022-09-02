#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, subprocess
import multiprocessing.dummy

def usage():
    print('Usage:', file=sys.stderr)
    print(sys.argv[0], '[path_to_files.ll]', file=sys.stderr)
    print('Authors:\nWritten by Iliya Diyachkov, Andrey Tretyakov (Intel, 2022)', file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 1 or len(sys.argv) > 2:
    usage()
if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    usage()

# replace this path with yours or/and fix other paths
spirv_home = os.environ.get('SPIRV_HOME')
if not spirv_home:
    spirv_home = os.environ.get('HOME') + '/spirv'
#print(spirv_home)

BDir = spirv_home + '/LLVM-SPIRV-Backend'
TDir = spirv_home + '/spirv-tools'
BBld = BDir + '/build'
TBld = TDir + '/build'
llc_exe = BBld + '/bin/llc'
val_exe = TBld + '/tools/spirv-val'
if len(sys.argv) == 2:
    inputdir = sys.argv[1]
else:
    inputdir = BDir + '/llvm/test/CodeGen/SPIRV'

#print(llc_exe)
#print(val_exe)
#print(inputdir)

# Make a list of tests
Tests = {}
for path, subdirs, files in os.walk(inputdir):
    for name in files:
        if name[-3:] == '.ll':
            Tests[os.path.join(path, name)] = {'result': '', 'stderr': ''}

def ThreadProc(SrcFile):
    ObjFile = SrcFile + '.o'

    run_llc = [llc_exe, '-O0', SrcFile, '-o', ObjFile, '--filetype=obj']
    run_val = [val_exe, ObjFile]
    run_rm = ['rm', ObjFile]

    res_llc = subprocess.run(run_llc, capture_output=True)
    if res_llc.returncode == 0:
        res_val = subprocess.run(run_val, capture_output=True)
        if res_val.returncode == 0:
            result = 'PASS'
        else:
            result = 'VFAIL'
            Tests[SrcFile]['stderr'] = res_val.stderr
        subprocess.run(run_rm, capture_output=True)
    else:
        result = 'CFAIL'
    Tests[SrcFile]['result'] = result

#print(multiprocessing.cpu_count())
pool = multiprocessing.dummy.Pool()
pool.map(ThreadProc, Tests)
#print(Tests)

for Test in sorted(Tests):
    print(Test + '\t' + Tests[Test]['result'])
    stderr = Tests[Test]['stderr']
    if stderr:
        print(stderr)
