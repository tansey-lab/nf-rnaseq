process RUN_FASTQC {
    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(reads)

    output:
    path "${sampleId}", emit: logs

    script:
    """
    bash run_fastqc.sh "$sampleId" "$reads"
    """
}
