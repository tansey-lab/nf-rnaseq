process SAMTOOLS_INDEX {
    label 'process_low'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.bai") , emit: bai

    script:
    """
    samtools \\
        index \\
        -@ ${task.cpus-1} \\
        ${bam}
    """
}

process SAMTOOLS_FLAGSTAT {
    label 'process_single'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.flagstat") , emit: flagstat

    script:
    """
    samtools \\
        flagstat \\
        --threads ${task.cpus} \\
        ${bam} \\
        > ${sampleId}.flagstat
    """
}

process SAMTOOLS_CRAM {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    // NB: the global errorStrategy falls back to 'ignore', which would let a
    // failed losslessness check pass silently. A verification failure must stop
    // the run, so retry transient errors but never ignore a final failure.
    errorStrategy { task.attempt <= 2 ? 'retry' : 'finish' }

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.cram")       , emit: cram
    tuple val(sampleId), path("*.cram.md5")   , emit: md5
    path("*.cram_verify.tsv")                 , emit: verify

    script:
    """
    set -o pipefail

    samtools \\
        view \\
        --threads ${task.cpus} \\
        -C \\
        -T ${params.cramGenome} \\
        --output-fmt-option version=${params.cramVersion} \\
        -o ${sampleId}.cram \\
        ${bam}

    # Verify the conversion is lossless by comparing decoded records.
    # decode_md=0 suppresses the MD/NM tags samtools regenerates on CRAM decode
    # but which STAR never wrote - without it the streams differ by those two
    # tags even though no data has been lost.
    MD5_BAM=\$(samtools view --threads ${task.cpus} ${bam} | md5sum | cut -d' ' -f1)
    MD5_CRAM=\$(samtools view --threads ${task.cpus} --input-fmt-option decode_md=0 \\
        -T ${params.cramGenome} ${sampleId}.cram | md5sum | cut -d' ' -f1)

    if [ "\$MD5_BAM" != "\$MD5_CRAM" ]; then
        echo "ERROR: CRAM round trip is not lossless for ${sampleId}" >&2
        echo "  bam  record md5: \$MD5_BAM" >&2
        echo "  cram record md5: \$MD5_CRAM" >&2
        exit 1
    fi

    # resolve the real path - Nextflow stages inputs as symlinks, and the
    # manifest needs the true source location for the later deletion step
    SRC=\$(readlink -f ${bam})
    BAM_BYTES=\$(stat -Lc %s ${bam})
    CRAM_BYTES=\$(stat -c %s ${sampleId}.cram)

    echo "\$MD5_CRAM  ${sampleId}.cram" > ${sampleId}.cram.md5

    printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' \\
        "${sampleId}" "\$SRC" "\$BAM_BYTES" "\$CRAM_BYTES" "\$MD5_CRAM" "VERIFIED" \\
        > ${sampleId}.cram_verify.tsv
    """
}

process SAMTOOLS_CRAM_INDEX {
    label 'process_low'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(cram)

    output:
    tuple val(sampleId), path("*.crai") , emit: crai

    script:
    """
    samtools \\
        index \\
        -@ ${task.cpus-1} \\
        ${cram}
    """
}

process CRAM_MANIFEST {
    label 'process_single'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    path(verifyTSV)

    output:
    path("cram_verified_manifest.tsv") , emit: manifest

    script:
    """
    printf 'sampleId\\tsource_bam\\tbam_bytes\\tcram_bytes\\tcram_md5\\tstatus\\n' \\
        > cram_verified_manifest.tsv
    cat ${verifyTSV} | sort >> cram_verified_manifest.tsv

    awk -F'\\t' 'NR>1 {b+=\$3; c+=\$4; n++} END {
        if (n > 0) printf "# %d files verified: %.1f GiB BAM -> %.1f GiB CRAM (%.1f%% saved)\\n", \\
            n, b/1073741824, c/1073741824, 100-100*c/b
    }' cram_verified_manifest.tsv
    """
}
