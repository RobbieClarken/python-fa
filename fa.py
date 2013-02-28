#!/usr/bin/env python

import subprocess
from scipy import io
from tempfile import NamedTemporaryFile
import os

FULL_RATE = 'F'
SINGLE_DECIMATED = 'd'
DOUBLE_DECIMATED = 'D'

MEAN_MASK = 1 << 0
MIN_MASK = 1 << 1
MAX_MASK = 1 << 2
STD_DEV_MASK = 1 << 3

def pv_list_to_str(pv_list):
    if isinstance(pv_list, basestring):
        return pv_list

    if sorted(pv_list) != pv_list:
        raise Exception('PV list must be in increasing order.')

    previous_pv = pv_list[0]
    last_pv = pv_list[-1]
    pv_str = '%i' % previous_pv
    counting = False
    for this_pv in pv_list[1:]:
        if this_pv != previous_pv + 1:
            if counting:
                pv_str += '-%i' % previous_pv
            pv_str += ',%i' % this_pv
        elif this_pv == last_pv:
            pv_str += '-%i' % this_pv
        else:
            counting = True
        previous_pv = this_pv
    return pv_str

def capture(pv_list, samples=1, server=None, port=None, start_date=None,
            continuous=True, data_format=FULL_RATE, data_max=None,
            all_data=False, raw_format=False, forbid_gaps=False,
            check_gaps=False, extra_dimensions=False, data_name=None,
            utc=False, subtract_day=False, controller_info=False):

    options = ['-q']
    if server:
        options += ['-S', server]
    if port:
        options += ['-p', port]
    if start_date:
        options += ['-s', start_date.isoformat()]
        continuous = False
    if continuous:
        options += ['-C']
    if data_format:
        if data_mask:
            data_format += '%i' % data_mask
        options += ['-f', data_format]
    if all_data:
        options += ['-a']
    if raw_format:
        options += ['-R']
    if forbid_gaps:
        options += ['-c']
    if check_gaps:
        options += ['-z']
    if extra_dimensions:
        options += ['-k']
    if data_name:
        options += ['-n', data_name]
    if utc:
        options += ['-Z']
    if subtract_day:
        options += ['-d']
    if controller_info:
        options += ['T']

    command = ['fa-capture'] + options + [pv_list_to_str(pv_list)]
    if samples:
        command += [ '%i' % samples ]
    capture_process = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = capture_process.communicate()[0]

    if raw_format:
        return stdout

    with NamedTemporaryFile('wr+b', delete=False) as mat_file:
        mat_file.write(stdout)
    data = io.loadmat(mat_file.name)
    os.unlink(mat_file.name)

    return data
