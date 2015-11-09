# kattis_submit
A simple python script that submits files to Kattis.
The original version of this script can be found at https://kth.kattis.com/help/submit
I modified the script, so you now get the result of a submission directly in the terminal.

## Setup
Dependencies are python 2.7 with the modules colorama and lxml. Easily installed with

`pip install -r requirements.txt`

There can arise problems when installing lxml under OSX, see issue#4.

To use this script you need to download a kattisrc config file which can be found at: https://kth.kattis.com/help/submit
It can be placed in your user folder or the folder where the script resides.

I recommend creating an alias for your shell by modifying your .zshrc/.bashrc file, just add something like
`alias kattis = "python ~/{PATH TO SCRIPT}"`

## Running the client
The easiest way to run the client is if you have named your source code to problemid.suffix, where suffix is something suitable for the language (e.g., .java for Java, .c for C, .cc or .cpp for C++, .py for Python, .cs for C#, .go for Go).

Let's assume you're solving the problem Hello World (with problem id "hello") and that your java solution is in the file Hello.java. Then you can simply run `python submit.py Hello.java`, and the client will make the correct guesses. You will always be prompted before a submission is sent.

## More advanced options
The submit client can handle multiple files in a submission. For such submissions, the filename and suffix of the first file listed on the command line is the basis of the guesses. It is ok to list a file multiple times, e.g. `python submit.py Hello.java *.java`.
In case the client guesses wrong, you can correct it by specifying a command line option. Running the script without arguments will list all options. The options are:

-p problem - overrides problem guess

-m main_class - overrides main class guess

-l language - overrides language guess

-f - forces submission (i.e. no prompt)

## Want to help?
Do you know how cookies and authentication works with python? Then feel free to fix any mistakes!
