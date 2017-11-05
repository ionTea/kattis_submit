#!/usr/bin/env python
import argparse
import os
import sys
from bs4 import BeautifulSoup
import requests
import time

from colorama import init, deinit

init()

# Python 2/3 compatibility
if sys.version_info[0] >= 3:
    import configparser
else:
    # Python 2, import modules with Python 3 names
    import ConfigParser as configparser


_HEADERS = {'User-Agent': 'kattis-cli-submit'}
_LANGUAGE_GUESS = {
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.c++': 'C++',
    '.py': 'Python',
    '.cs': 'C#',
    '.c#': 'C#',
    '.go': 'Go',
    '.m': 'Objective-C',
    '.hs': 'Haskell',
    '.pl': 'Prolog',
    '.js': 'JavaScript',
    '.php': 'PHP',
    '.kt': 'Kotlin',
    '.sc': 'Scala',
    '.rb': 'Ruby'
}
_GUESS_MAINCLASS = {'Java', 'Python'}
_PASSED_TEST_SIGN = u'\u2713'
if os.name == 'nt':
    _PASSED_TEST_SIGN = 'P'

parser = argparse.ArgumentParser(description='Submit a solution to Kattis')

parser.add_argument('-f', '--force', action='store_true',
               help='Confirm before submission')
parser.add_argument('-p', '--problem',
               help='Which problem to submit to.')
parser.add_argument('-m', '--mainclass',
               help='Sets mainclass.')
parser.add_argument('-l', '--language',
               help='Sets language.')
parser.add_argument('files', nargs='+')

args = parser.parse_args()
files = args.files

cfg = configparser.ConfigParser()

if not cfg.read([os.path.join(os.getenv('HOME'), '.kattisrc'),
                 os.path.join(os.path.dirname(sys.argv[0]), '.kattisrc')]):
    # TODO  move shit
    print('''\
            I failed to read in a config file from your home directory or from the
            same directory as this script. To download a .kattisrc file please visit
            https://<kattis>/download/kattisrc

            The file should look something like this:
            [user]
            username: yourusername
            token: *********

            [kattis]
            loginurl: https://<kattis>/login
            submissionurl: https://<kattis>/submit''')
    sys.exit(1)

# Get config options from .kattisrc
username = password = token = submission_url = login_url = base_url = None
try:
    username = cfg.get('user', 'username')
    token = cfg.get('user', 'token')
    submit_url = cfg.get('kattis', 'submissionurl')
    login_url = cfg.get('kattis', 'loginurl')
    base_url = login_url[0:login_url.rfind('/')]
except configparser.NoOptionError:
    # TODO
    print('Your kattisrc seems to be not compatible with life itself.')
    sys.exit(1)

login_args = {
    'user': username,
    'script': 'true',
    'token': token
    }

login_reply = None
try:
    login_reply = requests.post(login_url, data=login_args, headers=_HEADERS)
except Exception as e:
    print('Connection to {0} failed.'.format(login_url))
    sys.exit(1)

if login_reply.status_code != 200:
    print(login_reply.status_code)
    print('Could not authenticate')
    print(login_reply.content)
    sys.exit(1)

# Guess language and problem
problem, ext = os.path.splitext(os.path.basename(args.files[0]))
language = _LANGUAGE_GUESS.get(ext, None)
mainclass = problem if language in _GUESS_MAINCLASS else None

if args.problem:
    problem = args.problem
if args.language:
    language = args.language
elif language == 'Python':
    python_version = str(sys.version_info[0])
    language = 'Python ' + python_version

if language is None:
    print('I failed to guess the language and you didn\'t provide one for me. I\'m going back to bed')
    exit(1)

confirm_submission = not args.force

# Confirm or die
if confirm_submission:
    print('Problem:', problem)
    print('Language:', language)
    print('Files:', ', '.join(files))

    confirmation = input('Submit problem? (Y/y) ')

    if confirmation not in 'yY':
        exit()

# Submit

data = {'submit': 'true',
        'submit_ctr': 2,
        'language': language,
        'mainclass': mainclass,
        'problem': problem,
        'script': 'true'}

sub_files = []
for f in files:
    with open(f) as sub_file:
        sub_files.append(('sub_file[]',
                          (os.path.basename(f),
                           sub_file.read(),
                           'application/octet-stream')))
response = None
try:
    response = requests.post(submit_url, data=data,
        files=sub_files, cookies=login_reply.cookies,
        headers=_HEADERS)
except Exception as e:
    print('Connection to {0} failed.'.format(submit_url))
    sys.exit(1)

response_content = response.content.decode('utf-8').replace('<br />', '\n')
print(response_content)
submission_id = response_content.split()[4][:-1]
print(base_url + '/submissions/' + submission_id)
# Soup it up TODO improve
# if confirm_submission:
#     confirmation = input('Get results? (Y/y) ')
#     if confirmation not in 'Yy':
#         exit()

while True:
    try:
        login_reply = requests.post(login_url, data=login_args, headers=_HEADERS)
        response = requests.get(base_url + '/submissions/' + submission_id, cookies=login_reply.cookies,
            headers=_HEADERS)
    except Exception as e:
        print('Connection to {0} failed.'.format(submit_url))
        sys.exit(1)
    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')

    test_cases = list(soup.select('.testcases')[0].children)
    submission_status = soup.select('.status')[0]
    passed_tests = 0

    sys.stdout.write('[')

    for case in test_cases:
        classes = case.attrs.get('class', [])
        if 'accepted' in classes:
            passed_tests += 1
            sys.stdout.write('\033[92m')
            sys.stdout.write(_PASSED_TEST_SIGN + ' ')
        elif 'rejected' in classes:
            sys.stdout.write('\033[91m')
            sys.stdout.write('X ')
        else:
            sys.stdout.write('\033[39m')
            sys.stdout.write('O ')

    sys.stdout.write(' | ' + str(passed_tests) + '/' + str(len(test_cases)))
    sys.stdout.write('\033[39m] ' + str(submission_status.text))
    sys.stdout.flush()

    status = submission_status.attrs.get('class', [])
    if 'accepted' in status or 'rejected' in status:
        if 'rejected' in status:
            sys.stdout.write('\033[91m')
            print()
            print('Oh no! Your submission resulted in a', str(submission_status.text))
            sys.stdout.write('\033[39m')
            print()
            compileroutput = soup.select('.extrainfo')
            if compileroutput:
                print('Compiler output: ')
                print(compileroutput[0].find('pre').text)
                print()
        else:
            tottime = soup.select('.runtime.middle')[0].text
            print(' Time: ' + tottime)
        exit(1)
    sys.stdout.write('\r')
    time.sleep(1)

deinit()
