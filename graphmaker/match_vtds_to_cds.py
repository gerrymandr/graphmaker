import collections
import csv

from constants import fips_to_state_abbreviation

# The VTDs have GEOIDs of this form:
# {2-digit state FIPS}{3-digit county code}{>=2-digit VTD code}

# We can match VTDs to CDs like this:
# 1. Use the block-to-VTD file to find a tabulation block for each VTD.
# 2. Use the block-to-CD assignment file to find the CD that contains that block.

# The block assignment files are in this directory on my computer
# (at the same level as the outer graphmaker folder):
baf_path = "../../block_assignments/block_assignments/"

# The block assignment files are named like:
# "BlockAssign_ST{fips}_{2-digit state abbreviation}_{matched unit}
# For example, BlockAssign_ST26_MI_CD assigns blocks to CDs in Michigan.


def block_to_unit_filepath(fips, unit):
    """The units are all-caps: 'VTD' or 'CD'"""
    abbrev = fips_to_state_abbreviation[fips]
    return baf_path + fips + "/" + f"BlockAssign_ST{fips}_{abbrev}_{unit}.txt"

# Our objective will be to make a VTD-to-CD assignment CSV.


def match_blocks_to_cds(fips):
    matching = dict()
    with open(block_to_unit_filepath(fips, 'CD')) as f:
        next(f)
        for line in f:
            block, cd = line.strip().split(',')
            if not cd:
                print("cd was blank for " + block)
            else:
                matching[block] = cd
    return matching


def match_vtds_to_blocks(fips):
    matching = collections.defaultdict(list)
    with open(block_to_unit_filepath(fips, 'VTD')) as f:
        # ignore the column headers
        next(f)
        for line in f:
            block, county, vtd = line.strip().split(',')
            geoid = ''.join([fips, county, vtd])
            matching[geoid].append(block)
    return matching


def match_vtds_to_cds(fips):
    vtds_to_blocks = match_vtds_to_blocks(fips)
    blocks_to_cds = match_blocks_to_cds(fips)

    vtds_to_cds = dict()
    for vtd in vtds_to_blocks:
        for block in vtds_to_blocks[vtd]:
            if block in blocks_to_cds:
                vtds_to_cds[vtd] = blocks_to_cds[block]

    return vtds_to_cds


def write_matching_to_csv(matching, units, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        writer.writerow(units)
        writer.writerows(sorted(matching.items()))


def create_matching_for_state(fips, output_filepath):
    matching = match_vtds_to_cds(fips)
    write_matching_to_csv(matching, ['VTD', 'CD'], output_filepath)


def main():
    create_matching_for_state('26', './26.csv')


if __name__ == '__main__':
    main()
