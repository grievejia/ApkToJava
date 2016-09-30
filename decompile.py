#!/usr/bin/env python3
"""
Android decompiler
"""
from argparse import ArgumentParser
import logging
from pathlib import Path
import sys
import subprocess
from tempfile import TemporaryDirectory

__author__ = 'Grievejia'
__version__ = '0.1'

def sanity_check(args):
	for filepath in args.files:
		if not filepath.exists():
			logging.error('File does not exist: %s', str(filepath))
			return False
		elif not filepath.is_file():
			logging.error('%s is not a file', str(filepath))
			return False
		elif filepath.suffix != '.apk':
			logging.error('%s is not an .apk file', str(filepath))
			return False

	if not args.output.exists():
		logging.error('Output direcory not exist: %s', str(args.output))
		return False
	elif not args.output.is_dir():
		logging.error('Output is not a directory: %s', str(args.output))
		return False
	return True

def main(args):
	script_path = Path(__file__).resolve().parent
	dex2jar_path = script_path.joinpath('dex2jar', 'd2j-dex2jar.sh')
	if not dex2jar_path.exists() or not dex2jar_path.is_file():
		logging.critical('dex2jar not found in %s', str(dex2jar_path))
		sys.exit(-1)
	cfr_path = script_path.joinpath('cfr.jar')
	if not cfr_path.exists() or not cfr_path.is_file():
		logging.critical('cfr not found in %s', str(cfr_path))
		sys.exit(-1)

	with TemporaryDirectory() as temp_dir:
		for filepath in args.files:
			print('Converting %s to jar...' % str(filepath))

			tmp_jar = '%s/%s.jar' % (temp_dir, filepath.stem)
			dex2jar_cmd = [str(dex2jar_path), str(filepath), '-o', tmp_jar]
			logging.info('dex2jar command: %s', ' '.join(dex2jar_cmd))
			try:
				subprocess.run(dex2jar_cmd)
			except subprocess.CalledProcessError:
				logging.error('dex2jar execution failed.', exc_info=True)
				system.exit(-1)

			print('Decompiling jar file...')

			cfr_cmd = ['/usr/bin/env', 'java', '-jar', str(cfr_path), tmp_jar, '--outputdir', str(args.output)]
			logging.info('cfr command: %s', ' '.join(cfr_cmd))
			try:
				subprocess.run(cfr_cmd)
			except subprocess.CalledProcessError:
				logging.error('cfr execution failed.', exc_info=True)
				system.exit(-1)

			print('Decompilation done. Output in %s' % str(args.output))

epilog = 'system (default) encoding: {}'.format(sys.getdefaultencoding())
parser = ArgumentParser(
    usage='%(prog)s [options] [FILE ...]',
    description=__doc__, epilog=epilog,
    prog=Path(sys.argv[0]).name
)

parser.add_argument('files', metavar='FILE', nargs='*', type=Path,
                    help='input apk file(s)')
parser.add_argument('--version', action='version', version=__version__)
parser.add_argument('--verbose', '-v', action='count', default=0,
                    help='increase log level [WARN]')
parser.add_argument('--quiet', '-q', action='count', default=0,
                    help='decrease log level [WARN]')
parser.add_argument('--logfile', metavar='FILE',
                    help='log to file instead of <STDERR>')
parser.add_argument('--output', '-o', type=Path, help='specify the dir of output', default=Path('.'))
args = parser.parse_args()

# Logging setup
log_adjust = max(min(args.quiet - args.verbose, 2), -2) * 10
logging.basicConfig(filename=args.logfile, level=logging.WARNING + log_adjust,
                    format='%(levelname)-8s %(module) 10s: %(funcName)s %(message)s')
logging.info('verbosity increased')
logging.debug('verbosity increased')

if not sanity_check(args):
	sys.exit(-1)

logging.debug('Input apks: %s', ' '.join([str(x) for x in args.files]))
logging.debug('Output dir: %s', str(args.output))

main(args)