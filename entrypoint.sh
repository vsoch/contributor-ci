#!/bin/bash

set -e

printf "Found files in workspace:\n"
ls

printf "Looking for Contributor CI install...\n"
which cci

# A bot token with more permissions is required

if [ ! -z "${CCI_GITHUB_TOKEN}" ]; then
    printf "Please export a personal access token to CCI_GITHUB_TOKEN.\n"
    printf "You can use set the actions GITHUB_TOKEN to this variable,\n"
    printf "but not all extractors will work."
fi

COMMAND="cci"

# These arguments are shared between commands

# Add custom config file
if [ ! -z "${INPUT_CONFIG_FILE}" ]; then
    COMMAND="${COMMAND} --config-file ${INPUT_CONFIG_FILE}"
fi

# custom outdir
if [ ! -z "${INPUT_RESULTS_DIR}" ]; then
    COMMAND="${COMMAND} --out-dir ${INPUT_RESULTS_DIR}"
fi

# Case 1: update is set
if [ ! -z "${INPUT_UPDATE}" ]; then

    # Update CFA files?
    if [ ! -z "${INPUT_UPDATE_CFA}" ]; then
        COMMAND="${COMMAND} ui --cfa update"
    else
        COMMAND="${COMMAND} ui update"
    fi

    if [ ! -z "${INPUT_UPDATE_RANDOM}" ]; then
        COMMAND="${COMMAND} random:${INPUT_UPDATE_RANDOM}"
    fi

# Case 2: run cfa instead
elif [ ! -z "${INPUT_CFA}" ]; then

    COMMAND="${COMMAND} cfa ${INPUT_CFA}"

# Case 2: an extraction is desired
else
    # are we doing an extraction?
    if [ ! -z "${INPUT_EXTRACT}" ]; then
        COMMAND="${COMMAND} extract"
        if [ ! -z "${INPUT_EXTRACT_SAVE_FORMAT}" ]; then
            COMMAND="${COMMAND} --save-format ${INPUT_EXTRACT_SAVE_FORMAT}"
        fi
        COMMAND="${COMMAND} ${INPUT_EXTRACT}"
    fi
fi

echo "${COMMAND}"
${COMMAND}
echo $?
