[![Docker Repository on Quay](https://quay.io/repository/aelin/ngs-tools/status "Docker Repository on Quay")](https://quay.io/repository/aelin/ngs-tools)

# ngs-tools
This repo contains the Docker files needed to build the image `quay.io/aelin/ngs-tools`. This image is based on the ubuntu
image `quay.io/broadinstitute/viral-baseimage:0.1.15` and contains various tools for manipulating and checking quality of reads and unique molecular indices (UMIs).

 - file manipulation: samtools, seqtk, bamtools
 - read trimming and merging: trimmomatic, flash2
 - umi-specific utilities: umi-tools
 - QC: fastqc, multiqc

To build, run `docker build .` from within the directory containing the `Dockerfile`.