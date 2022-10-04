from tempfile import gettempdir
from os import path, unlink, getppid, mkdir, environ
from threading import Thread
from time import sleep
from math import log10, ceil
from functools import lru_cache
from subprocess import run

import numpy as np
from flask import (
    Flask, redirect, render_template, request, send_from_directory, url_for)
from markdown_it import MarkdownIt
# work around deprecated `from collections import Iterable` in savReaderWriter
import collections.abc
collections.Iterable = collections.abc.Iterable
import savReaderWriter                                              # noqa:E402

from . import data                                                  # noqa:E402


# *** global constants and variables ***


# default sample size
SIZE = 20

# sample ID's range
SID_RANGE = (111_111, 999_999)

# Study class instances for use by the application
STUDIES = {
    'levels':           data.Levels(),
    'simon':            data.Simon(),
    'twosample_null':   data.TwoSample(0),
    'twosample_medium': data.TwoSample(0.5)
}

# supported file formats and labels
FORMATS = {
    'csv':      'Comma-separated (csv)',
    'sav':      'SPSS (sav)',
    'dta':      'Stata (dta)',
    'xlsx':     'Excel (xlsx)'
}

# cache directory, unique to gunicorn invocation
cache = path.join(gettempdir(), f'tykhe-{getppid()}')
try:
    mkdir(cache)
except FileExistsError:
    # already created by another worker
    pass

# Markdown converter
md = MarkdownIt('commonmark', {'typographer': True})
md.enable('smartquotes')


# *** web application ***

app = Flask(__name__)


@app.route('/')
def root():
    return redirect('preselect')


@app.route('/preselect')
def preselect():
    return render_template(
        'preselect.html', studies=STUDIES, formats=FORMATS,
        sid_range=SID_RANGE)


@app.route('/request')
def request_sample():
    # If there are empty argument values, redirect to an URL from which they
    # are stripped. This is necessary to get around the limitation of form
    # submission in `preselect.html`, which includes undefined parameters as
    # ''. This way, a clean semantic URL can be shared.
    if '' in request.args.values():
        values = {k: v for k, v in request.args.items()
                  if v != ''}
        url = url_for('request_sample', **values)
        return redirect(url)
    # process arguments
    # `study` is required and gets forwarded to `/collect` through a
    #     hidden form field
    # `size` is optional and leads to the student needing to specify the sample
    #     size on this page
    # `format` is optional; if present, it gets forwarded to `/collect`
    #     through a hidden form field and is used there to pre-select an option
    # `sid` is optional; if not specified, a sample ID is generated randomly
    #     here. Either are forwarded to `/collect` through a hidden form
    # field.
    study = request.args.get('study')
    size = request.args.get('size')
    format = request.args.get('format')
    sid = request.args.get('sid')
    if sid is None:
        rng = np.random.default_rng()
        sid = rng.integers(low=SID_RANGE[0], high=SID_RANGE[1] + 1)
    # response
    return render_template(
        'request.html', study=study, size=size, format=format, sid=sid,
        study_object=STUDIES[study])


@app.route('/collect')
def collect_sample():
    # process arguments
    # `study`, `size`, and `sid` are required
    # `format` is optional and leads to the student needing to specify the
    #     file format on this page
    study = request.args.get('study')
    size = request.args.get('size')
    format = request.args.get('format')
    sid = request.args.get('sid')
    # trigger file / data creation, so it is ready for download later
    #     If `format` is not specified, the 'dummy' format is filled in, to be
    # able to call `get_data_file` (with `wait=False`), which runs
    # `create_data_file` in a separate Thread, which calls the memoized
    # `get_study_sample`.
    #     Though no file is written by `create_data_file`, the results of
    # `get_study_sample` are cached and therefore a subsequent call with a
    # proper file format to `/download` will complete faster.
    if format is None:
        format = 'dummy'
    get_data_file(study, size, format, sid, wait=False)
    # response
    return render_template(
        'collect.html', study=study, size=size, format=format, sid=sid,
        formats=FORMATS, study_object=STUDIES[study])


@app.route('/download')
def download():
    # process arguments
    study = request.args.get('study')
    size = request.args.get('size')
    format = request.args.get('format')
    sid = request.args.get('sid')
    # response is file for download
    filename = get_data_file(study, size, format, sid, wait=True)
    return send_from_directory(cache, filename, as_attachment=True)


@app.route('/about')
def about():
    return render_template('about.html', studies=STUDIES)


@app.route('/study')
def study():
    study = request.args.get('study')
    return render_template('study.html', study_object=STUDIES[study])


@app.route('/diag')
def diag():
    kwargs = dict(capture_output=True, encoding='utf-8', errors='ignore')
    ls_cache = run(['ls', '-l', cache], **kwargs)
    mem = run(['free', '-h'], **kwargs)
    disk = run(['df', '-h'], **kwargs)
    return render_template(
        'diag.html', ls_cache=ls_cache, mem=mem, disk=disk, env=environ)


@app.template_filter('markdown')
def markdown(s):
    return md.render(s)


# *** data creation and caching ***

# Data files delivered by the application are written as actual files to
# temporary storage (`cache` directory), partially because some of the used
# writing functions don't support in-memory 'files'. The written files are left
# in temporary storage so they do not have to be regenerated.
#
# Data file creation needs to be threadsafe, because the same file may be
# requested from different clients and processed by different workers.
# Moreover, data generation and data file creation are handled by
# `create_data_file` in its own thread, so that `get_data_file` can return
# quickly (if `wait=False`).
#
# Three states of data file creation are managed by `get_data_file` and
# `create_data_file`:
#   <nothing>: file does not exist
#   <underway>: file does not yet exist, but a creation thread is running
#   <exists>: data file creation has finished
# To detect the <underway> state for a specific data file, an empty file with
# 'creating-' prepended to the data file's name is created.
#
# In addition to the disk-based data file cache, the function generating the
# actual data is memoized.

def get_data_file(study, size, format, sid, wait):
    filename = f'tykhe_{study}_{size}_{sid}.{format}'
    signalpath = path.join(cache, 'creating-' + filename)
    pathname = path.join(cache, filename)
    print('▶ get_data_file:', pathname)
    try:    # threadsafe version of `if not path.isfile(signalpath):`
        with open(signalpath, 'x'):
            pass
        # not <underway>
        if path.isfile(pathname):
            # <exists>
            # no need to create data file, remove signal file
            unlink(signalpath)
            return filename
        else:
            # <nothing>
            # create data file in separate thread
            args = (study, int(size), format, int(sid), pathname, signalpath)
            thread = Thread(target=create_data_file, args=args)
            thread.start()
            if wait:
                thread.join()
            return filename
    except FileExistsError:
        # <underway>
        # wait for creation to finish
        if wait:
            while path.isfile(signalpath):
                sleep(0.1)
        return filename


def create_data_file(study, size, format, sid, pathname, signalname):
    print('▷ create_data_file:', pathname)
    # create data
    df = get_study_sample(study, size, sid)
    # save to file
    if format == 'csv':
        df_to_csv(df, pathname)
    if format == 'xlsx':
        # needs translation of ordinals
        df_to_xlsx(df, pathname)
    if format == 'dta':
        df.to_stata(pathname)
    if format == 'sav':
        # needs a lot
        df_to_sav(df, pathname)
    # signal <exists>
    unlink(signalname)
    print('◁ create_data_file:', pathname)


@lru_cache(maxsize=300)
def get_study_sample(study, size, sid):
    print(f'▶ get_study_sample({study}, {size}, {sid})')
    rng = np.random.default_rng(sid)
    return STUDIES[study].get_sample(size, rng)


def df_to_csv(df, pathname):
    # prepare data
    varNames = list(df.columns)     # names of variables
    for varName in varNames:
        if df[varName].dtype == 'category' and df[varName].cat.ordered:
            # ordered categorical (ordinal) stored as integers
            df[varName] = df[varName].cat.codes
    # write CSV file
    df.to_csv(pathname, index=False)


def df_to_xlsx(df, pathname):
    # prepare data
    varNames = list(df.columns)     # names of variables
    for varName in varNames:
        if df[varName].dtype == 'category' and df[varName].cat.ordered:
            # ordered categorical (ordinal) stored as integers
            df[varName] = df[varName].cat.codes
    # write Excel file
    df.to_excel(pathname, index=False)


def df_to_sav(df, pathname):
    # prepare data and collect information
    varNames = list(df.columns)     # names of variables
    varTypes = {}                   # varName → numerical or string
    measureLevels = {}              # varName → measurement level
    formats = {}                    # varName → display format
    valueLabels = {}                # varName → (value → label)
    for varName in varNames:
        if df[varName].dtype != 'category':
            # numerical
            varTypes[varName] = 0  # numerical
            measureLevels[varName] = 'scale'
        else:
            if df[varName].cat.ordered:
                # ordered categorical (ordinal)
                varTypes[varName] = 0  # numerical
                measureLevels[varName] = 'ordinal'
                # stored as integers, with `valueLabels` mapping to strings
                values = df[varName].cat.codes
                labels = list(df[varName].cat.categories)
                df[varName] = values
                valueLabels[varName] = {value: labels[value]
                                        for value in values}
                # display format to avoid decimals on integers
                formats[varName] = f'F{ceil(log10(len(labels)))}.0'
            else:
                # unordered categorical (nominal)
                varTypes[varName] = max(df[varName].apply(len))  # max str len
                measureLevels[varName] = 'nominal'
                # stored as strings
                df[varName] = df[varName].astype('str')
    # write SPSS file
    with savReaderWriter.SavWriter(
            pathname, varNames, varTypes, valueLabels=valueLabels,
            measureLevels=measureLevels, formats=formats, ioUtf8=True
            ) as writer:
        for _, row in df.iterrows():
            writer.writerow([row[vn] for vn in list(row.index)])
