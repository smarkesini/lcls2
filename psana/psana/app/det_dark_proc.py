#!/usr/bin/env python
#----
import sys
from time import time
from psana.detector.Utils import info_parser_arguments
from psana.detector.UtilsAreaCalib import pedestals_calibration

import logging
logger = logging.getLogger(__name__)
DICT_NAME_TO_LEVEL = logging._nameToLevel

SCRNAME = sys.argv[0].rsplit('/')[-1]

USAGE = 'Usage:'\
      + '\n  %s -e <experiment> -d <detector> -r <run-number(s)>' % SCRNAME\
      + '\n     [-x <xtc-directory>] [-o <output-result-directory>] [-L <logging-mode>] [...]'\
      + '\nExamples:'\
      + '\n  %s -e tmoc00118 -d tmoopal -r123' % SCRNAME\
      + '\n  %s -e tmoc00118 -d tmoopal -r123 -o ./work -L DEBUG' % SCRNAME\
      + '\n  mpirun -n 5 %s -e tmoc00118 -d tmoopal -r123 -o ./work -L DEBUG' % SCRNAME\
      + '\n\n  Try: %s -h' % SCRNAME

#----

def do_main():

    t0_sec = time()

    parser = argument_parser()
    args = parser.parse_args()
    kwa = vars(args)
    #defs = vars(parser.parse_args([])) # dict of defaults only

    if len(sys.argv)<3: exit('\n%s\n' % USAGE)

    assert args.exp is not None, 'WARNING: option "-e <experiment>" MUST be specified.'
    assert args.det is not None, 'WARNING: option "-d <detector-name>" MUST be specified.'
    assert args.runs is not None, 'WARNING: option "-r <run-number(s)>" MUST be specified.'

    fmt = '[%(levelname).1s] %(name)s %(message)s' if args.logmode=='DEBUG' else '[%(levelname).1s] %(message)s'
    logging.basicConfig(format=fmt, level=DICT_NAME_TO_LEVEL[args.logmode])
    #logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(filename)s: %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    #logging.basicConfig(filename='log.txt', filemode='w', format=fmt, level=DICT_NAME_TO_LEVEL[args.logmode])

    logger.debug('%s\nIn epix10ka_pedestals_calibration' % (50*'_'))
    logger.debug('Command line:%s' % ' '.join(sys.argv))
    logger.info(info_parser_arguments(parser))

    pedestals_calibration(**kwa)

    logger.info('DONE, consumed time %.3f sec' % (time() - t0_sec))


def argument_parser():
    from argparse import ArgumentParser

    d_fname   = None # '/cds/data/psdm/tmo/tmoc00118/xtc/tmoc00118-r0123-s000-c000.xtc2'
    d_exp     = None # 'tmoc00118'
    d_det     = None # 'tmoopal'
    d_runs    = None # 123 or 123,125-126
    d_nrecs   = 100  # number of records
    d_dirxtc  = None # '/cds/data/psdm/tmo/tmoc00118/xtc'
    d_dirrepo = './work' 
    d_usesmd  = True
    d_logmode = 'INFO'
    d_errskip = True
    d_stepnum    = None
    d_stepmax    = 5
    d_dirmode    = 0o777
    d_filemode   = 0o666
    d_int_lo     = 1       # lowest  intensity accepted for dark evaluation
    d_int_hi     = 16000   # highest intensity accepted for dark evaluation
    d_intnlo     = 6.0     # intensity ditribution number-of-sigmas low
    d_intnhi     = 6.0     # intensity ditribution number-of-sigmas high
    d_rms_lo     = 0.001   # rms ditribution low
    d_rms_hi     = 16000   # rms ditribution high
    d_rmsnlo     = 6.0     # rms ditribution number-of-sigmas low
    d_rmsnhi     = 6.0     # rms ditribution number-of-sigmas high
    d_fraclm     = 0.1     # allowed fraction limit
    d_nsigma     = 6.0     # number of sigmas for gated eveluation
    d_deploy  = False
    d_tstamp  = None # 20180910111049 or run number <10000
    d_version = 'V2021-01-21'
    d_run_end = 'end'
    d_comment = 'no comment'

    h_fname   = 'input xtc file name, default = %s' % d_fname
    h_exp     = 'experiment name, default = %s' % d_exp
    h_det     = 'detector name, default = %s' % d_det
    h_runs    = 'run number or list of runs e.g. 12,14-18, default = %s' % str(d_runs)
    h_nrecs   = 'number of records to calibrate pedestals, default = %s' % str(d_nrecs)
    h_dirxtc  = 'non-default xtc directory, default = %s' % d_dirxtc
    h_dirrepo = 'repository for calibration results, default = %s' % d_dirrepo
    h_usesmd  = 'add "smd" in dataset string, default = %s' % d_usesmd
    h_logmode = 'logging mode, one of %s, default = %s' % (' '.join(DICT_NAME_TO_LEVEL.keys()), d_logmode)
    h_errskip = 'flag to skip errors and keep processing, stop otherwise, default = %s' % d_errskip
    h_stepnum    = 'step number to process or None for all steps, default = %s' % str(d_stepnum)
    h_stepmax    = 'maximum number of steps to process, default = %s' % str(d_stepmax)
    h_dirmode    = 'directory access mode, default = %s' % oct(d_dirmode)
    h_filemode   = 'file access mode, default = %s' % oct(d_filemode)
    h_int_lo     = 'lowest  intensity accepted for dark evaluation, default = %d' % d_int_lo
    h_int_hi     = 'highest intensity accepted for dark evaluation, default = %d' % d_int_hi
    h_intnlo     = 'intensity ditribution number-of-sigmas low, default = %f' % d_intnlo
    h_intnhi     = 'intensity ditribution number-of-sigmas high, default = %f' % d_intnhi
    h_rms_lo     = 'rms ditribution low, default = %f' % d_rms_lo
    h_rms_hi     = 'rms ditribution high, default = %f' % d_rms_hi
    h_rmsnlo     = 'rms ditribution number-of-sigmas low, default = %f' % d_rmsnlo
    h_rmsnhi     = 'rms ditribution number-of-sigmas high, default = %f' % d_rmsnhi
    h_fraclm     = 'allowed fraction limit, default = %f' % d_fraclm
    h_nsigma     = 'number of sigmas for gated eveluation, default = %f' % d_nsigma
    h_deploy  = 'deploy constants to the calib dir, default = %s' % d_deploy
    h_tstamp  = 'non-default time stamp in format YYYYmmddHHMMSS or run number(<10000) for constants selection in repo. '\
                'By default run time is used, default = %s' % str(d_tstamp)
    h_version = 'constants version, default = %s' % str(d_version)
    h_run_end = 'last run for validity range, default = %s' % str(d_run_end)
    h_comment = 'comment added to constants metadata, default = %s' % str(d_comment)

    parser = ArgumentParser(description='Proceses dark run xtc data for epix10ka')
    parser.add_argument('-f', '--fname',   default=d_fname,      type=str,   help=h_fname)
    parser.add_argument('-e', '--exp',     default=d_exp,        type=str,   help=h_exp)
    parser.add_argument('-d', '--det',     default=d_det,        type=str,   help=h_det)
    parser.add_argument('-r', '--runs',    default=d_runs,       type=str,   help=h_runs)
    parser.add_argument('-n', '--nrecs',   default=d_nrecs,      type=int,   help=h_nrecs)
    parser.add_argument('-x', '--dirxtc',  default=d_dirxtc,     type=str,   help=h_dirxtc)
    parser.add_argument('-o', '--dirrepo', default=d_dirrepo,    type=str,   help=h_dirrepo)
    parser.add_argument('-S', '--usesmd',  default=d_usesmd,     type=bool,  help=h_usesmd)
    parser.add_argument('-L', '--logmode', default=d_logmode,    type=str,   help=h_logmode)
    parser.add_argument('-E', '--errskip', default=d_errskip,    type=bool,  help=h_errskip)
    parser.add_argument('--stepnum',       default=d_stepnum,    type=int,   help=h_stepnum)
    parser.add_argument('--stepmax',       default=d_stepmax,    type=int,   help=h_stepmax)
    parser.add_argument('--dirmode',       default=d_dirmode,    type=int,   help=h_dirmode)
    parser.add_argument('--filemode',      default=d_filemode,   type=int,   help=h_filemode)
    parser.add_argument('--int_lo',        default=d_int_lo,     type=int,   help=h_int_lo)
    parser.add_argument('--int_hi',        default=d_int_hi,     type=int,   help=h_int_hi)
    parser.add_argument('--intnlo',        default=d_intnlo,     type=float, help=h_intnlo)
    parser.add_argument('--intnhi',        default=d_intnhi,     type=float, help=h_intnhi)
    parser.add_argument('--rms_lo',        default=d_rms_lo,     type=float, help=h_rms_lo)
    parser.add_argument('--rms_hi',        default=d_rms_hi,     type=float, help=h_rms_hi)
    parser.add_argument('--rmsnlo',        default=d_rmsnlo,     type=float, help=h_rmsnlo)
    parser.add_argument('--rmsnhi',        default=d_rmsnhi,     type=float, help=h_rmsnhi)
    parser.add_argument('--fraclm',        default=d_fraclm,     type=float, help=h_fraclm)
    parser.add_argument('--nsigma',        default=d_nsigma,     type=float, help=h_nsigma)
    parser.add_argument('-D', '--deploy',  action='store_true', help=h_deploy)
    parser.add_argument('-t', '--tstamp',  default=d_tstamp,   type=int,   help=h_tstamp)
    parser.add_argument('-v', '--version', default=d_version,  type=str,   help=h_version)
    parser.add_argument('-R', '--run_end', default=d_run_end,  type=str,   help=h_run_end)
    parser.add_argument('-C', '--comment', default=d_comment,  type=str,   help=h_comment)

    return parser

#----

if __name__ == "__main__":
    do_main()
    exit('End of %s'%SCRNAME)

# EOF
