# kattis_submit
A simple python script that submits files to Kattis
The original version of this script can be found at https://kth.kattis.com/help/submit
I modified the script, so you now get the result of a submission directly in the terminal.

# Setup
Download this script to your home folder, or wherever you want it to be.
Go to: https://kth.kattis.com/help/submit and download your config file, and place it in the same folder as the script.

I recommend creating an alias for your shell by modifying your .zshrc/.bashrc file, just add something like
alias kattis = "python ~/{PATH TO SCRIPT}"

To use the script, just write kattis and the available options will be printed

## From Kattis original script
## Running the client
The easiest way to run the client is if you have named your source code to problemid.suffix, where suffix is something suitable for the language (e.g., .java for Java, .c for C, .cc or .cpp for C++, .py for Python, .cs for C#, .go for Go). Let's assume you're solving the problem Hello World (with problem id "hello") and that your java solution is in the file Hello.java. Then you can simply run submit.py with Hello.java as command-line argument, and the client will make the correct guesses. You will always be prompted before a submission is sent.

## More advanced options
The submit client can handle multiple files in a submission. For such submissions, the filename and suffix of the first file listed on the command line is the basis of the guesses. It is ok to list a file multiple times, e.g. submit.py Hello.java *.java.
In case the client guesses wrong, you can correct it by specifying a command line option. Running submit.py -h will list all options. The options as of writing this page are:
-p <problem_id> - overrides problem guess
-m <mainclass> - overrides mainclass guess
-l <language> - overrides language guess
-f - forces submission (i.e. no prompt)

# Want to help?
Do you know how cookies and authentication works with python? Then feel free to fix my mistakes!
I am not a very good python developer, so if you think you could make the script better, please feel free!
