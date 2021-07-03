# version 3
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

''''
    Update:
    1.  Httpx used to replace requests
    2.  default sep change to '_'
    3. Fake useragent used
'''


import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def get_ncbi_taxid(species, sep='_'):
    # paras init
    species = str(species)
    ua = UserAgent(verify_ssl=False)
    headers = {'user-agent' : ua.random}
    print(species) # temp
    # def ncbi url
    ncbi_taxon = 'https://www.ncbi.nlm.nih.gov'
    
    # seerch target taxon
    req = httpx.get(ncbi_taxon + '/taxonomy/?term={}'.format(species), headers=headers).text
    soup = BeautifulSoup(req, 'lxml')
    
    taxid = soup.find_all(attrs={'href':re.compile('.*cgi\?id')})
    if len(taxid) == 0:
        return -np.ones((7))
    else:
        url = ncbi_taxon + taxid[0]['href']
    
    # search target species
    req = httpx.get(url, headers=headers).text
    soup = BeautifulSoup(req, 'lxml')
    try:
        url = 'https://www.ncbi.nlm.nih.gov//Taxonomy/Browser/' + soup.find(title='species')['href']
        req = httpx.get(url, headers=headers).text
        soup = BeautifulSoup(req, 'lxml')
    except:
        pass
    
    # get taxon id
    req = httpx.get(url, headers=headers).text
    soup = BeautifulSoup(req, 'lxml')
    
    taxon_lvl = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus']
    taxon_id = []
    for i in taxon_lvl:
        i = soup.find(attrs={'alt':i})
        try:
            taxon_id.append(int(i['href'].split('id=')[-1].split('&')[0]))
        except:
            taxon_id.append(-1)
            
    taxon_id.append(int(url.split('id=')[-1].split('&')[0]))
    return taxon_id