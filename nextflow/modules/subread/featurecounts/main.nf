process SUBREAD_FEATURECOUNTS {
    label 'process_medium'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(bam)
    path(annotation)

    output:
    tuple val(sampleId), path("*featureCounts.txt")        , emit: counts
    tuple val(sampleId), path("*featureCounts.txt.summary"), emit: summary

    script:
    def timestamp = new java.util.Date().format( 'yyyy-MM-dd_HH-mm-ss')
    def strandedness = 0
    if (params.strandedness == 'forward') {
        strandedness = 1
    } else if (params.strandedness == 'reverse') {
        strandedness = 2
    }
    """
    featureCounts \\
        -p \\
        -T $task.cpus \\
        --countReadPairs \\
        -t transcript \\
        -g gene_id \\
        -a $annotation \\
        -s $strandedness \\
        -O \\
        --largestOverlap \\
        -o ${sampleId}.featureCounts.txt \\
        ${bam}
    """
}

process MERGE_FEATURECOUNTS {
    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    val(filePrefix)
    path(featureCounts)

    output:
    path("{filePrefix}_featureCounts.csv"), emit: counts

    script:
    """
    python merge_featureCounts.py -f ${featureCounts} -p ${filePrefix}
    """
}
