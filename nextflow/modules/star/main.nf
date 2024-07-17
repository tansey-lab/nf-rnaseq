process STAR_ALIGN {
    label 'process_high'

    conda "${params.condaEnv}"
    publishDir "${params.OUTPUT}", mode: 'copy', overwrite: true

    input:
    tuple val(sampleId), path(reads)

    output:
    tuple val(sampleId), path('*Log.final.out')                         , emit: log_final
    tuple val(sampleId), path('*Log.out')                               , emit: log_out
    tuple val(sampleId), path('*Log.progress.out')                      , emit: log_progress
    tuple val(sampleId), path('*d.out.bam')              , optional:true, emit: bam
    tuple val(sampleId), path('*sortedByCoord.out.bam')  , optional:true, emit: bam_sorted
    tuple val(sampleId), path('*toTranscriptome.out.bam'), optional:true, emit: bam_transcript
    tuple val(sampleId), path('*Aligned.unsort.out.bam') , optional:true, emit: bam_unsorted
    tuple val(sampleId), path('*fastq.gz')               , optional:true, emit: fastq
    tuple val(sampleId), path('*.tab')                   , optional:true, emit: tab
    tuple val(sampleId), path('*.SJ.out.tab')            , optional:true, emit: spl_junc_tab
    tuple val(sampleId), path('*.ReadsPerGene.out.tab')  , optional:true, emit: read_per_gene_tab
    tuple val(sampleId), path('*.out.junction')          , optional:true, emit: junction
    tuple val(sampleId), path('*.out.sam')               , optional:true, emit: sam
    tuple val(sampleId), path('*.wig')                   , optional:true, emit: wig
    tuple val(sampleId), path('*.bg')                    , optional:true, emit: bedgraph

    script:
    """
    STAR \\
        --genomeDir ${params.genomeDir} \\
        --readFilesIn ${reads[0]} ${reads[1]} \\
        --runThreadN $task.cpus \\
        --outFileNamePrefix ${sampleId}. \\
        --readFilesCommand zcat \\
        --twopassMode Basic \\
        --sjdbOverhang 100 \\
        --outFilterType BySJout \\
        --outFilterMultimapNmax 20 \\
        --alignSJoverhangMin 8 \\
        --alignSJDBoverhangMin 1 \\
        --outFilterMismatchNmax 999 \\
        --outFilterMismatchNoverReadLmax 0.04 \\
        --alignIntronMin 20 \\
        --alignIntronMax 1000000 \\
        --alignMatesGapMax 1000000 \\
        --outSAMtype BAM SortedByCoordinate
    """
}
