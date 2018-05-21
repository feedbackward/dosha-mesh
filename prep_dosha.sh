#!/bin/bash

# Shell script for preparation of the landslide risk data.
# Author: Matthew J. Holland, Osaka University

TORUN="$@"

echo -n "$TORUN" | python "./prep_dosha.py"
