### Adam's Biotools : NCBI tools
### 1. Taxonomy tool
    get_ncbi_taxid :
        '''
            Transform species name to NCBI Taxid
        '''
        usage: get_ncbi_taxid(species_name, sep)
            species_name: The species which need get taxid, e.g. Atopobium_minutum
            sep: default '_' # disable

        return: a vector contain all taxon level NCBI Taxid, e.g. [2, 201174, 84998, 84999, 1643824, 1380, 1381]