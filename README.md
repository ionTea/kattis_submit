# kattis_submit
A simple python script that submits files to Kattis.
The original version of this script can be found at https://kth.kattis.com/help/submit.

## Setup
`pip install git+https://github.com/ionTea/kattis_submit.git`

To use this script you need to download a kattisrc config file which can be found at https://kth.kattis.com/download/kattisrc.

It can be placed in your user folder or the folder where the script resides.

## Usage
`kattis <file>`

The easiest way to run the client is if you have named your source code to problemid.suffix, where suffix is something suitable for the language (e.g., .java for Java, .c for C, .cc or .cpp for C++, .py for Python, .cs for C#, .go for Go).

Let's assume you're solving the problem Hello World (with problem id "hello") and that your C++ solution is in the file hello.cpp.
Then you can run

`kattis hello.cpp`

and the client will make the correct guess.

## Advanced options
The client can handle multiple files in a submission. For such submissions, the filename and suffix of the first file listed on the command line is the basis of the guesses.
In case the client guesses wrong, you can correct it by specifying problem/main_class/language.
Running the script without arguments will list all options.

-p problem - overrides problem guess

-m main_class - overrides main class guess

-l language - overrides language guess

-f - forces submission (i.e. no prompt)

