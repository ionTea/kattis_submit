#!/usr/bin/env python
import ConfigParser
import optparse
import os
import os.path
import sys
import requests
import mimetypes
import re
import time
from bs4 import BeautifulSoup
from colorama import init, deinit, Fore

_VERSION = 'Version: $Version: $'

_KATTISRC_LOCATION = '/usr/local/etc/'
_KATTISRC_FILE = '.kattisrc'
_PASSED_TEST_SIGN = u"\u2713"

if os.name == "nt":
	_PASSED_TEST_SIGN = "P"

_LANGUAGE_GUESS = { '.java' : 'Java', '.c' : 'C', '.cpp' : 'C++', '.h' : 'C++', '.cc' : 'C++', '.cxx' : 'C++', '.c++' : 'C++', '.py' : 'Python', '.cs': 'C#', '.c#': 'C#', '.go': 'Go', '.m' : 'Objective-C', '.hs' : 'Haskell', '.pl' : 'Prolog', '.js': 'JavaScript', '.php': 'PHP', '.rb' : 'Ruby' }
_GUESS_MAINCLASS  = set(['Java', 'Python'])

_RC_HELP = \
'''Failed to read config file from your home directory or from the script directory.
Please go to your Kattis user page to download a .kattisrc file.

The file should look something like:
[user]
username: yourusername
token: *********

[kattis]
loginurl: https://<kattis>/login
submissionurl: https://<kattis>/submit
resulturl: https://<kattis>/submissions/
'''

def login(session, loginurl, username, method, token, debug=False):
	login = session.post(loginurl, data={'user': username, method: token, 'script': 'true'})
	if debug:
		print "Login headers"
		print login.request.headers
		print login.headers
	if not login.ok:
		if login.status_code == 403:
			print "Incorrect Username/Password (403)"
		elif login.status_code == 404:
			print "Incorrect login URL (404)"
		else:
			print 'Unknown error on login:', login.status_code, login.reason
		return False
	return True

def confirm_or_die(problem, language, files, mainclass, tag):
	print 'Problem:', problem
	print 'Language:', language
	print 'Files:', ', '.join(files)
	if mainclass:
		print 'Mainclass:', mainclass
	if tag:
		print 'Tag:', tag
	print 'Submit (y/N)?'
	if sys.stdin.readline().upper()[:-1] != 'Y':
		print 'Cancelling'
		sys.exit(1)

def guess_mime(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def submit(session, submissionurl, problem, language, files, force=True, mainclass=None, tag=None, debug=False):
	if debug:
		print problem, language, files, force, mainclass, tag, debug

	if not force:
		confirm_or_die(problem, language, files, mainclass, tag)

	submission = session.post(submissionurl,
		data={
			'submit': 'true',
			'submit_ctr': '2',
			'language': language,
			'mainclass': mainclass,
			'problem': problem,
			'tag': tag,
			'script': 'true'
		},
		files=[('sub_file[]', (filename, open(filename, 'rb'), guess_mime(filename))) for filename in files]
		)

	if debug:
		print "Submission headers"
		print submission.request.headers
		print submission.headers

	if submission.ok:
		result = submission.text.replace("<br />", "\n")
		print result
		if result.find("ID") != -1: # Make sure there is a submission id.
			return result.split()[4][:-3]
		else:
			return False
	else:
		print "Unknown error on submission:", submission.status_code, submission.reason
		return False

def scrape_and_print(htmlDoc):
	soup  = BeautifulSoup(htmlDoc, 'html.parser')
	table = soup.find(id="judge_table").tbody

	num_tests    = len(table.div)
	num_accepted = len(table.div("span", "accepted"))
	num_failed   = len(table.div("span", "rejected"))

	status  = table.find("td", "status")
	runtime = table.find("td", "runtime")

	status_class = status.get("class")
	status_colored = status.text
	if "accepted" in status_class:
		status_colored = Fore.GREEN + status_colored + Fore.RESET
	elif "rejected" in status_class:
		status_colored = Fore.RED + status_colored + Fore.RESET

	sys.stdout.write(
		u"\r[{}{}{}{}{}] | {}/{} | {}".format(
			Fore.GREEN,
			u"\u2713"*num_accepted,
			Fore.RED,
			"X"*num_failed,
			Fore.RESET,
			num_accepted,
			num_tests,
			status_colored,
		)
	)
	sys.stdout.flush()

	if "accepted" in status_class:
		print "\nTime:", runtime.text
		return True
	elif "rejected" in status_class:
		print "\nOh no! Your submission resulted in a", status_colored
		for info in soup.find_all("div", "extrainfo"):
			print info.h3.text + ":"
			print re.sub("(Error|error|Warning|warning)", lambda match: Fore.RED + match.group(1) + Fore.RESET, info.pre.text)
		return True
	return False

def watch(session, resulturl, submission_id, debug=False):
	done = False
	resulturl = "%s/%s" % (resulturl, submission_id)
	print "Running tests...", resulturl
	while not done:
		result = session.get(resulturl)
		if debug:
			print "Result url:", resulturl
			print "Result headers"
			print result.request.headers
			print result.headers
		if not result.ok:
			print "Unknown error on results:", result.status_code, result.reason
			return

		done = scrape_and_print(result.text)
		time.sleep(1)

def get_url(cfg, option, default):
	if cfg.has_option('kattis', option):
		return cfg.get('kattis', option)
	elif cfg.has_option('kattis', 'hostname'):
		return 'https://%s/%s' % (cfg.get('kattis', 'hostname'), default)
	else:
		print "Your .kattisrc file is missing a url."
		sys.exit(1)

def main():
	if os.name == "nt":
		init(convert=True)

	opt = optparse.OptionParser()
	opt.add_option('-p', '--problem', dest='problem', metavar='PROBLEM', help='Submit to problem PROBLEM. Overrides default guess (first part of first filename)', default=None)
	opt.add_option('-m', '--mainclass', dest='mainclass', metavar='CLASS', help='Sets mainclass to CLASS. Overrides default guess (first part of first filename)', default=None)
	opt.add_option('-l', '--language', dest='language', metavar='LANGUAGE', help='Sets language to LANGUAGE. Overrides default guess (based on suffix of first filename)', default=None)
	opt.add_option('-t', '--tag', dest='tag', metavar='TAG', help=optparse.SUPPRESS_HELP, default="")
	opt.add_option('-f', '--force', dest='force', help='Force, no confirmation prompt before submission', action="store_true", default=False)
	opt.add_option('-d', '--debug', dest='debug', help='Print debug info while running', action="store_true", default=False)

	opts, args = opt.parse_args()

	if not args: # No args, nothing to upload.
		opt.print_help()
		sys.exit(1)

	seen = set()
	files = []
	for a in args:
		if not os.path.exists(a):
			print 'File not found:', a
			sys.exit(1)
		if a not in seen:
			files.append(a)
		seen.add(a)

	problem, ext = os.path.splitext(os.path.basename(args[0]))
	language = _LANGUAGE_GUESS.get(ext, None)
	mainclass = problem if language in _GUESS_MAINCLASS else None
	tag = opts.tag
	debug = opts.debug

	if opts.problem:
		problem = opts.problem
	if opts.mainclass is not None:
		mainclass = opts.mainclass
	if opts.language:
		language = opts.language

	if language == None:
		print 'No language specified, and I failed to guess language from filename extension "%s"' % (ext)
		sys.exit(1)

	cfg = ConfigParser.ConfigParser()
	if not cfg.read([os.path.join(os.path.dirname(sys.argv[0]), _KATTISRC_FILE),
					os.path.join(_KATTISRC_LOCATION, _KATTISRC_FILE),
					os.path.join(os.path.expanduser('~'), _KATTISRC_FILE)]):
		print _RC_HELP
		sys.exit(1)

	if cfg.has_option('user', 'username'):
		user = cfg.get('user', 'username')
	else:
		print "Your .kattisrc file apperars corrupted. It must provide a username.\nPlease download a new .kattisrc file\n"

	if cfg.has_option('user', 'token'):
		token = cfg.get('user', 'token')
		method = 'token'
	elif cfg.has_option('user', 'password'):
		token = cfg.get('user', 'password')
		method = 'password'
	else:
		print "Your .kattisrc file appears corrupted. It must provide a token (or a KATTIS password).\nPlease download a new .kattisrc file\n"
		sys.exit(1)

	with requests.Session() as session:
		loginurl = get_url(cfg, 'loginurl', 'login')
		if login(session, loginurl, user, method, token, debug=debug):
			submissionurl = get_url(cfg, 'submissionurl', 'judge_upload')
			submission_id = submit(session, submissionurl, problem, language, files, opts.force, mainclass, tag, debug=debug)
			if submission_id and login(session, loginurl, user, method, token, debug=debug):
				# Second login required becuase server logs out user after submisison.
				resulturl = get_url(cfg, 'resulturl', 'submissions')
				watch(session, resulturl, submission_id, debug=debug)

	if os.name == "nt":
		deinit()

if __name__ == '__main__':
	main()
