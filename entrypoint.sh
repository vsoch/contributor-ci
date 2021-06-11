#!/bin/bash

set -e

printf "Found files in workspace:\n"
ls

printf "Looking for Contributor CI install...\n"
which cci

COMMAND="cci"

# Add custom config file
if [ ! -z "${INPUT_CONFIG_FILE}" ]; then
    COMMAND="${COMMAND} --config-file ${INPUT_CONFIG_FILE}"
fi

# custom outdir
if [ ! -z "${INPUT_RESULTS_DIR}" ]; then
    COMMAND="${COMMAND} --out-dir ${INPUT_RESULTS_DIR}"
fi

# are we doing an extraction?
if [ ! -z "${INPUT_EXTRACT}" ]; then
    COMMAND="${COMMAND} extract ${INPUT_EXTRACT}"
fi

echo "${COMMAND}"

${COMMAND}
echo $?
