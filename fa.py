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

def capture(pv_list, samples=None, server=None, port=None, start_date=None,
            end_date=None, continuous=True, data_format=None, data_mask=None,
            extra_dimensions=False, utc=False, subtract_day=False,
            controller_info=False):
    """
    pv_list: list or string
        A list of ids or a string in formatted such as "1-9,30-35,41"
    samples: int or timedelta
        Amount of data to collect in number of samples to read or a
        length of time. Not required if start_date and end_date are
        specified.
    server: str, optional
        Address of server running fa-archiver.
    port: int, optional
        Port of server running fa-archiver.
    start_date: datetime, optional
        Earliest point of historical data to fetch.
        Not required for continuous capture.
    end_date: datetime
        Latest point of historical data to fetch.
        Not required for continuous capture or if samples is specified.
    continuous: bool
        Capture live data.
    data_format: one of {FULL_RATE, SINGLE_DECIMATED, DOUBLE_DECIMATED}, optional
    data_mask: one of {MEAN_MASK, MIN_MASK, MAX_MASK, STD_DEV_MASK}, optional
    extra_dimension: bool
        Keep extra dimensions.
    utc: bool
        Use UTC timestamps instead of local time.
    subtract_day: bool
        Subtract the day of the first timestamp from the timestamp vector.
    controller_info: bool
        Save the id0 communication controller timestamp information.
    """

    options = ['-q']
    if server:
        options += ['-S', server]
    if port:
        options += ['-p', port]
    s_option = None
    if start_date:
        continuous = False
        s_option = start_date.isoformat()
    if end_date:
        s_option += '~%s' % start_date.isoformat()
    elif not samples:
        raise(Error('samples or end_data must be specified'))
    if s_option:
        options += ['-a', '-s', s_option]
    if continuous:
        options += ['-C']
    if data_mask and not data_format:
        data_format = FULL_RATE
    if data_format:
        if data_mask:
            data_format += '%i' % data_mask
        options += ['-f', data_format]
    if extra_dimensions:
        options += ['-k']
    if utc:
        options += ['-Z']
    if subtract_day:
        options += ['-d']
    if controller_info:
        options += ['-T']

    command = ['fa-capture'] + options + [pv_list_to_str(pv_list)]
    if samples:
        if hasattr(samples, 'total_seconds'):
            command += ['%is' % samples.total_seconds()]
        else:
            command += ['%i' % samples]
    capture_process = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = capture_process.communicate()[0]

    with NamedTemporaryFile('wr+b', delete=False) as mat_file:
        mat_file.write(stdout)
    data = io.loadmat(mat_file.name)
    os.unlink(mat_file.name)

    return data
