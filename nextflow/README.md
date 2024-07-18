# NextFlow workflow to run bulk RNA-seq pipeline

## Getting started

To run the pipeline on Iris use: `nextflow run main.nf -params-file params.json -profile iris`

It is recommended that each workflow in `main.nf` is run sequentially to allow for users to inspect intermediate QC results and select optimal parameters for downstream tasks:

1. **Initial QC**: The first workflow runs [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on the raw fastq files and then [`MultiQC`](http://multiqc.info/) on those results
  - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTQC_FASTQ`

2. **Trimming and QC**: The second workflow runs [`fastp`](https://github.com/OpenGene/fastp) to trim adapters and/or poly-X or poly-A tails, followed by [`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [`MultiQC`](http://multiqc.info/)
  - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry FASTP_FASTQ`

3. **Alignment and indexing**: The third workflow runs [`STAR`](https://github.com/alexdobin/STAR) on the adapter-trimmed fastq files followed by [`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) indexing
  - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry STAR_FASTQ`

4. **Post-alignment QC**: The fourth workflow runs QC on the resulting BAM files ([`SAMtools`](https://sourceforge.net/projects/samtools/files/samtools/) `flagstat` and various [`RSeQC`](http://rseqc.sourceforge.net/) modules), followed by [`MultiQC`](http://multiqc.info/) on those results
  - To run this workflow alone use: `nextflow run main.nf -params-file params.json -profile iris -entry QC_BAM`

## Environment

Currently, this workflow assumes that a `conda` environment has been created with all necessary packages (TODO: add yml file).

## Contents of `params.json`

Generate own `params.json` file using the following parameters:
```
{
    "inputDir"     : "TODO",
    "fastqFile"    : "TODO",
    "outDir"       : "TODO",
    "condaEnv"     : "TODO",
    "genomeDir"    : "TODO",
    "adapterFASTA" : "TODO",
    "linkBED"      : "TODO",
    "fileBED"      : "TODO"
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
