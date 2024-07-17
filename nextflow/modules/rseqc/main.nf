process GET_BED {
    publishDir "${params.outDir}", mode: 'copy', overwrite: true

    output:
    path '*.bed*', emit: bed

    shell:
    """
    wget -O "!{params.fileBED}" "!{params.linkBED}"
    """
}

process RSEQC_BAMSTAT {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*.bam_stat.txt"), emit: txt

    script:
    """
    bam_stat.py \\
        -i ${bam} \\
        > ${sampleId}.bam_stat.txt
    """
}

process RSEQC_INFEREXP {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)
    path bed

    output:
    tuple val(sampleId), path("*.infer_experiment.txt"), emit: txt

    script:
    """
    infer_experiment.py \\
        -i ${bam} \\
        -r ${bed} \\
        > ${sampleId}.infer_experiment.txt
    """
}

process RSEQC_READDISTRIBUTION {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)
    path bed

    output:
    tuple val(sampleId), path("*.read_distribution.txt"), emit: txt

    script:
    """
    read_distribution.py \\
        -i ${bam} \\
        -r ${bed} \\
        > ${sampleId}.read_distribution.txt
    """
}

process RSEQC_READDUPLICATION {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)

    output:
    tuple val(sampleId), path("*seq.DupRate.xls"), emit: seq_xls
    tuple val(sampleId), path("*pos.DupRate.xls"), emit: pos_xls
    tuple val(sampleId), path("*.pdf")           , emit: pdf
    tuple val(sampleId), path("*.r")             , emit: rscript

    script:
    """
    read_duplication.py \\
        -i ${bam} \\
        -o ${sampleId}
    """
}
