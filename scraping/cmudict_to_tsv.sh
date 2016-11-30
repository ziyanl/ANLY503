#!/bin/bash

# Determine where this file is being run from so that we can find the data directory
# The following courtesy of http://stackoverflow.com/questions/59895/can-a-bash-script-tell-which-directory-it-is-stored-in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check which operating system we are on so that the command runs correctly
if [[ `uname` = "Darwin" ]]; then
    # We have to use some extra steps here because OS X has limited sed regex
    grep -a -e "^[A-Z]" "$DIR/../data/cmudict-07.b" | sed -E 's/(\([0-9]+\))?[ ]+/\$\1\$/' | sed -E $'s/\$/\t/g' > "$DIR/../data/cmudict.tsv"
else
    grep -a -e "^[A-Z]" "$DIR/../data/cmudict-07.b" | sed -r 's/(\([0-9]+\))?\s\s/\t\1\t/' > "$DIR/../data/cmudict.tsv"
fi

# Strips off headers and non-word characters from the file.
# Passes the output to an editor which inserts tabs between the words, their repeat number
# and their pronunciation.
# Sends the TSV output to a file