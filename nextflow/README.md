# NextFlow workflow to run pipeline

To run the pipeline on Iris use: `nextflow run main.nf -params-file params.json -profile iris`

Generate own `params.json` file using the following parameters:
```
{
    "inputDir"      :       "TODO",
    "fastq"         :       "${params.inputDir}/TODO",
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
| fastq        |    No    | FASTQ file naming pattern with wildcards                         |
| outDir       |    No    | Output directory where results are saved                         |
| condaEnv     |    No    | Path to conda environment to use                                 |
| genomeDir    |    No    | Path to STAR genome directory to use for alignment               |
| adapterFASTA |    Yes   | FASTA file containing adapters to trim with FASTP                |
| linkBED      |    Yes   | Link to bed file to use; only necessary with some RSeqQC modules |
| fileBED      |    Yes   | Bed file name to use; only necessary with some RSeqQC modules    |
