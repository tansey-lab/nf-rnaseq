#!/usr/bin/env bash

sample_id="$1"
reads="$2"

mkdir -p ${sample_id}
fastqc -o ${sample_id} -f fastq -q ${reads}
