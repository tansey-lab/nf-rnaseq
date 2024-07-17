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
