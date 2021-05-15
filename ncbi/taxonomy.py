# version 2
def get_ncbi_taxid(species, sep=' '):
    species = str(species)
    
    # Up to level 6
    if ('unclassified' in species) or (species.split(sep)[1] == 'sp') or (species.split(sep)[1] == 'sp.'):
        tax_url = 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name={}'.format(species.split(sep)[0])
    
    else:
        taxon_lvl = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus']
        tax_url = 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?name={}+{}'.format(species.split(sep)[0], species.split(sep)[1])
    
    req = requests.get(tax_url).text
    soup = BeautifulSoup(req, 'lxml')
    
    if ('unclassified' in species) or (species.split(sep)[1] == 'sp') or (species.split(sep)[1] == 'sp.'):
        taxon_lvl = ['superkingdom', 'phylum', 'class', 'order', 'family']
        
        if 'Search results for complete name' in str(soup):
            tax_url_update = 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/' + soup.find(attrs={'href':re.compile('.*wwwtax\.cgi\?')})['href']
            soup = BeautifulSoup(requests.get(tax_url_update).text, 'lxml')
        
        # v2
        taxid= []
        for i in taxon_lvl:
            tid = soup.find(attrs={'alt':re.compile(i)})
            if tid != None:
                taxid.append(tid['href'].split('id=')[-1].split('&lvl')[0])
            else:
                taxid.append(-1)
        taxid.append(soup.find(attrs={'href':re.compile('lineage_toggle')})['href'].split('id=')[-1].split('&lvl')[0])
        taxid.append(-1)
    
    else:
        if 'No result found in the Taxonomy database for complete name' in str(soup):
            return -np.ones(7)
        
        taxid = []
        for i in taxon_lvl:
            if i != 'genus':
                ind_id = soup.find(attrs={'alt':re.compile(i)})
                
                if ind_id is None:
                    taxid.append(-1)
                else:
                    ind_id = ind_id['href'].split('id=')[-1].split('&lvl')[0]
                    taxid.append(ind_id)
            else:
                ind_id = soup.find_all(attrs={'alt':re.compile(i)})
                if len(ind_id) == 0:
                    ind_id = soup.find_all(attrs={'alt':re.compile('no rank')})[-1]['href'].split('id=')[-1].split('&lvl')[0]
                    taxid.append(ind_id)
                else:
                    ind_id = soup.find(attrs={'alt':re.compile(i)})['href'].split('id=')[-1].split('&lvl')[0]
                    taxid.append(ind_id)
        
        taxid.append(soup.find(attrs={'href':re.compile('lineage_toggle')})['href'].split('id=')[-1].split('&lvl')[0])
    
    taxid = np.array(taxid, dtype=int)
    return taxid