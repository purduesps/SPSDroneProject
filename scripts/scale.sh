#!/bin/bash
echo "blah"
convert "rawframes2/*.jpg[960x]" -set filename:base "%[base]" "rawframes2/%[filename:base].jpg"
