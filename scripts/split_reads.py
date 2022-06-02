#!/usr/bin/env python
''' This script contains a number of utilities for splitting reads into
    separate files, primarily for skipping cycles or extracting UMIs.
    It uses a READ_STRUCTURE argument based on Broad Institute's Picard.
'''

__author__ = "aelin@princeton.edu"
__version__ = "0.1"

import argparse
import pysam as ps

elements = ["B", "M", "T", "S", "C"] # Picard-style read structure elements; plus "C" for cell barcode

def next_structure(read_structure):
    ''' Determines the next structure in a read structure string.
        Input: String containing a Picard-style read structure.
        Output: Tuple containing the next element (struct), the number of bases it applies to (num), and the remaining read structure (rem).
    '''
    struct = ""
    num = 0
    rem = ""

    # Find the first element in read_structure string
    idx = min((read_structure.index(x) for x in elements if x in read_structure))
    if idx is not False:
        struct = read_structure[idx:idx+1]
        num = int(read_structure[:idx])
        rem = read_structure[idx+1:]
    # If no element is found (i.e., an empty read_structure string), returns empty strings and 0
    return (struct, num, rem)


def parse_structure(read_structure):
    ''' Use pysam to read unmapped bam, store specific bases as read tags
        Creates a tab-separated file 'dsub-jobstatus.txt' that stores integer values corresponding to the job status of each sample and sample-seqrun (row) for each step of a pipeline (column).
        Also creates a file 'samples-total.txt' that stores the names of each sample-seqrun that will be used for steps of the pipeline.
        Integer values: 0 = not yet run or still running; 1 = "Success"; -1 = "Failure and do re-run". Manually set job status value to -2 = "Failure and/or don't re-run".
        Input: Name of the pipeline to be run. This will determine which steps (columns) are created in 'dsub-jobstatus.txt'.
        Additional input: 'flowcells.txt' must be in the current working directory.
        Output: Creates/overwrites 'dsub-jobstatus.txt' and 'samples-total.txt' in the current working directory.
    '''
    range_dict = {}
    start = 0
    end = 0

    rem = read_structure
    while rem != "":
        (struct, num, rem) = next_structure(rem)
        # Create tuple of ranges based on num
        start = end
        end += num
        r = (start, end)
        
        if struct != "S":
            # anything except a "Skip"
            # create list
            ranges = []
            if struct in range_dict:
                # update list
                ranges = range_dict.get(struct)
            ranges.append(r)
            range_dict[struct] = ranges

    return range_dict # dict of key,val pairs where key = struct, val = list of tuples containing start,end ranges to be concatenated


def split(args):
    ''' Use pysam to read unmapped bam, store specific bases as read tags
        Creates a tab-separated file 'dsub-jobstatus.txt' that stores integer values corresponding to the job status of each sample and sample-seqrun (row) for each step of a pipeline (column).
        Also creates a file 'samples-total.txt' that stores the names of each sample-seqrun that will be used for steps of the pipeline.
        Integer values: 0 = not yet run or still running; 1 = "Success"; -1 = "Failure and do re-run". Manually set job status value to -2 = "Failure and/or don't re-run".
        Input: Name of the pipeline to be run. This will determine which steps (columns) are created in 'dsub-jobstatus.txt'.
        Additional input: 'flowcells.txt' must be in the current working directory.
        Output: Creates/overwrites 'dsub-jobstatus.txt' and 'samples-total.txt' in the current working directory.
    '''

    bam_in = ps.AlignmentFile(args.bam_in, "rb", check_sq = False)
    bam_out = ps.AlignmentFile(args.bam_out, "wb", template=bam_in)
    handle_in = bam_in.fetch(until_eof = True)
    range_dict = parse_structure(args.read_structure) # dict of key,val pairs where key = struct, val = list of tuples containing start,end ranges to be concatenated

    for read in handle_in:
        # Aggregate B, M, T, and C seqs and QS from range_dict
        #print(read.query_squence)
        for struct in range_dict:
            ranges = range_dict[struct]
            seq = ""
            qs = ""
            for (start, end) in ranges:
                seq += read.query_sequence[start:end]
                qs += ''.join(map(lambda x: chr(x+33), read.query_qualities[start:end]))
            # Set B, M, and C tags first
            if struct == "B":
                read.set_tag("BC", seq, "Z")
                read.set_tag("QT", qs, "Z")
            elif struct == "M":
                read.set_tag("RX", seq, "Z")
                read.set_tag("QX", qs, "Z")
            elif struct == "C":
                read.set_tag("CR", seq, "Z")
                read.set_tag("CY", qs, "Z")
        # Reassign bases last
        # Note that assigning to seq will invalidate any quality scores. Thus, to in-place edit the sequence and quality scores, copies of the quality scores need to be taken.
        if "T" in range_dict:
            ranges = range_dict["T"]
            seq = ""
            qs = []
            for (start, end) in ranges:
                seq += read.query_sequence[start:end]
                qs.append(read.query_qualities[start:end])
            read.query_sequence = seq
            read.query_qualities = qs[0]
        # If no template bases were assigned in read_structure, leave the sequence and QS intact and only add tags
        bam_out.write(read)
    bam_in.close()
    bam_out.close()


def annotate_bam_from_bam(args):
    ''' Use pysam to read unmapped bam, store specific bases as read tags
        Creates a tab-separated file 'dsub-jobstatus.txt' that stores integer values corresponding to the job status of each sample and sample-seqrun (row) for each step of a pipeline (column).
        Also creates a file 'samples-total.txt' that stores the names of each sample-seqrun that will be used for steps of the pipeline.
        Integer values: 0 = not yet run or still running; 1 = "Success"; -1 = "Failure and do re-run". Manually set job status value to -2 = "Failure and/or don't re-run".
        Input: Name of the pipeline to be run. This will determine which steps (columns) are created in 'dsub-jobstatus.txt'.
        Additional input: 'flowcells.txt' must be in the current working directory.
        Output: Creates/overwrites 'dsub-jobstatus.txt' and 'samples-total.txt' in the current working directory.
        Both input bam files must be name-sorted
    '''
    bam_in = ps.AlignmentFile(args.bam_in, "rb", check_sq = False)
    bam_tags = ps.AlignmentFile(args.bam_tags, "rb", check_sq = False)
    bam_out = ps.AlignmentFile(args.bam_out, "wb", template=bam_in)
    handle_in = bam_in.fetch(until_eof = True)
    handle_tags = bam_tags.fetch(until_eof = True)

    # Load all tags into a dictionary
    dict_tags = dict()
    for read_tag in handle_tags:
        dict_tags[read_tag.query_name] = read_tag

    for read_in in handle_in:
        # Find the matching read in the dictionary
        read_tag_matched = dict_tags[read_in.query_name]
        # Loop through bam_in and annotate reads with tags from dictionary
        for tag in args.tags:
            (rtag, valtype) = read_tag_matched.get_tag(tag, with_value_type = True)
            read_in.set_tag(tag, rtag, valtype)
        bam_out.write(read_in)
    bam_in.close()
    bam_tags.close()
    bam_out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tool for editing bams to extract/annotate sample barcodes, cell barcodes, and UMIs in NGS reads.")
    subparsers = parser.add_subparsers()
    # Parser for split
    parser_split = subparsers.add_parser('split')
    parser_split.add_argument('--bam_in', required=True, help="Bam file to be split.")
    parser_split.add_argument('--bam_out', required=True, help="Output bam file.")
    parser_split.add_argument('--read_structure', required=True, help="Picard-style read structure: B for sample Barcode, M for unique Molecular index, T for Template, S for Skip, C for Cell barcode.")
    parser_split.set_defaults(func=split)
    # Parser for annotate_bam_from_bam
    parser_annBFB = subparsers.add_parser('annotate_bam_from_bam')
    parser_annBFB.add_argument('--bam_in', required=True, help="Bam file to be annotated.")
    parser_annBFB.add_argument('--bam_tags', required=True, help="Bam file to draw tags from.")
    parser_annBFB.add_argument('--tags', nargs='+', required=True, help="Tags to transfer.")
    parser_annBFB.add_argument('--bam_out', required=True, help="Output annotated bam file.")
    parser_annBFB.set_defaults(func=annotate_bam_from_bam)
    # Parse arguments
    args = parser.parse_args()
    args.func(args)
