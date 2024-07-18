# NextFlow workflow to run bulk RNA-seq pipeline

## Getting started

To run the pipeline on Iris use: `nextflow run main.nf -params-file params.json -profile iris`

It is recommended that each workflow in `main.nf` is run sequentially to allow for users to inspect intermediate QC results and select optimal parameters for downstream tasks:
- The first workflow runs `fastqc` on the raw fastq files and then `multiqc` on those results
  - To run this alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTQC_FASTQ`
- The second workflow runs `fastp` to trim adapters and/or poly-X or poly-A tails, followed by `fastq` and `multiqc`
  - To run this alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTP_FASTQ`
- The third workflow runs `star` on the adapter-trimmed fastq files followed by `samtools` indexing
  - To run this alone use: `nextflow run main.nf -params-file params.json -profile iris -entry STAR_FASTQ`
- The fourth workflow runs QC on the resulting BAM files (`samtools flagstat` and various `rseqc` modules), followed by `multiqc`
  - To run this alone use: `nextflow run main.nf -params-file params.json -profile iris -entry QC_BAM`

## Environment

Currently, this workflow assumes that a `conda` environment has been created with all necessary packages (TODO: add yml file).

## Contents of `params.json`

Generate own `params.json` file using the following parameters:
```
{
    "inputDir"      :       "TODO", # path
    "fastqFile"     :       "TODO", # fastq filename pattern
    "outDir"        :       "TODO",
    "condaEnv"      :       "TODO",
    "genomeDir"     :       "TODO",
    "adapterFASTA"  :       "TODO",
    "linkBED"       :       "TODO",
    "fileBED"       :       "TODO"
}
```

Below is a description of what each variable should contain. If variable is optional and not in use, do not create any entry in the `json` file.

| Variable     | Optional | Description                                                      |
| :------------| :------: | :----------------------------------------------------------------|
| inputDir     |    No    | Input directory where fastq files reside                         |
| fastq        |    No    | FASTQ file naming pattern with wildcards within inputDir         |
| outDir       |    No    | Output directory where results are saved                         |
| condaEnv     |    No    | Path to conda environment to use                                 |
| genomeDir    |    No    | Path to STAR genome directory to use for alignment               |
| adapterFASTA |    Yes   | FASTA file containing adapters to trim with FASTP                |
| linkBED      |    Yes   | Link to bed file to use; only necessary with some RSeqQC modules |
| fileBED      |    Yes   | Bed file name to use; only necessary with some RSeqQC modules    |
