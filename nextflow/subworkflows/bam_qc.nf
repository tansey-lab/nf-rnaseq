#!/usr/bin/env nextflow

include { SAMTOOLS_FLAGSTAT      } from '../modules/samtools/main.nf'
include	{ GET_BED                } from '../modules/rseqc/main.nf'
include { RSEQC_BAMSTAT          } from '../modules/rseqc/main.nf'
include { RSEQC_INFEREXP         } from '../modules/rseqc/main.nf'
include { RSEQC_READDUPLICATION  } from '../modules/rseqc/main.nf'
include { RSEQC_READDISTRIBUTION } from '../modules/rseqc/main.nf'
include { RUN_MULTIQC            } from '../modules/multiqc/main.nf'

workflow BAM_QC {
    take:
        bam       // file: /path/to/sample.bam

    main:
        GET_BED()
        SAMTOOLS_FLAGSTAT ( bam )
        RSEQC_BAMSTAT ( bam )
        RSEQC_INFEREXP ( bam, GET_BED.out.bed )
        RSEQC_READDUPLICATION ( bam )
        RSEQC_READDISTRIBUTION ( bam, GET_BED.out.bed )

    emit:
        flagstat = SAMTOOLS_FLAGSTAT.out.flagstat
        bamstat  = RSEQC_BAMSTAT.out.txt
        inferexp = RSEQC_INFEREXP.out.txt
        readdup  = RSEQC_READDUPLICATION.out.pos_xls
        readdist = RSEQC_READDISTRIBUTION.out.txt
}
