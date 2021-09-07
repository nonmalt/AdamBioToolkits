def country_to_subregion(data):
    m49 = {}
    
    iso_alpha3_code = [
        ['DZA', 'EGY', 'LBY', 'MAR', 'SDN', 'TUN', 'ESH'],
        ['IOT', 'BDI', 'COM', 'DJI', 'ERI', 'ETH', 'ATF', 'KEN', 'MDG', 'MWI', 'MUS', 'MYT', 'MOZ', 'REU', 'RWA',
         'SYC', 'SOM', 'SSD', 'UGA', 'TZA', 'ZMB', 'ZWE'],
        ['AGO', 'CMR', 'CAF', 'TCD', 'COG', 'COD', 'GNQ', 'GAB', 'STP'],
        ['BWA', 'SWZ', 'LSO', 'NAM', 'ZAF'],
        ['BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 'GNB', 'LBR', 'MLI', 'MRT', 'NER', 'MGA', 'SHN', 'SEN',
         'SLE', 'TGO'],
        ['AIA', 'ATG', 'ABW', 'BHS', 'BRB', 'BES', 'VGB', 'CYM', 'CUB', 'CUW', 'DMA', 'DOM', 'GRD', 'GLP', 'HTI',
         'JAM', 'MTQ', 'MSR', 'PRI', 'BLM', 'KNA', 'LCA', 'MAF', 'VCT', 'SXM', 'TTO', 'TCA', 'VIR'],
        ['BLZ', 'CRI', 'SLV', 'GTM', 'HND', 'MEX', 'NIC', 'PAN'],
        ['ARG', 'BOL', 'BVT', 'BRA', 'CHL', 'COL', 'ECU', 'FLK', 'GUF', 'GUY', 'PRY', 'PER', 'SGS', 'SUR', 'URY',
         'VEN'],
        ['BMU', 'CAN', 'GRL', 'SPM', 'USA'],
        ['ATA'],
        ['KAZ', 'KGZ', 'TJK', 'TKM', 'UZB'],
        ['CHN', 'HKG', 'MAC', 'PRK', 'JPN', 'MNG', 'KOR'],
        ['BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'TLS', 'VNM'],
        ['AFG', 'BGD', 'BTN', 'IND', 'IRN', 'MDV', 'NPL', 'PAK', 'LKA'],
        ['ARM', 'AZE', 'BHR', 'CYP', 'GEO', 'IRQ', 'ISR', 'JOR', 'KWT', 'LBN', 'OMN', 'QAT', 'SAU', 'PSE', 'SYR',
         'TUR', 'ARE', 'YEM'],
        ['BLR', 'BGR', 'CZE', 'HUN', 'POL', 'MDA', 'ROI', 'RUS', 'SVK', 'UKR'],
        ['ALA', 'GGY', 'JEY', 'Sark', 'DNK', 'EST', 'FRO', 'FIN', 'ISL', 'IRL', 'IMN', 'LVA', 'LTU', 'NOR', 'SJM',
         'SWE', 'GBR'],
        ['ALB', 'AND', 'BIH', 'HRV', 'GIB', 'GRC', 'VAT', 'ITA', 'MLT', 'MNE', 'MKD', 'PRT', 'SMR', 'SRB', 'SVN',
         'ESP'],
        ['AUT', 'BEL', 'FRA', 'DEU', 'LIE', 'LUX', 'MCO', 'NLD', 'CHE'],
        ['AUS', 'CXR', 'CCK', 'HMD', 'NZL', 'NFK'],
        ['FJI', 'NCL', 'PNG', 'SLB', 'VUT'],
        ['GUM', 'KIR', 'MHL', 'FSM', 'NRU', 'MNP', 'PLW', 'UMI'],
        ['ASM', 'COK', 'PYF', 'NIU', 'PCN', 'WSM', 'TKL', 'TON', 'TUV', 'WLF']
    ]
    
    subares = ['Northern Africa', 'Eastern Africa', 'Middle Africa', 'Southern Africa', 'Western Africa', 'Caribbean',
               'Central America', 'South America', 'Northern America', 'Antarctica', 'Central Asia', 'Eastern Asia',
               'South-eastern Asia', 'Southern Asia', 'Western Asia', 'Eastern Europe', 'Northern Europe', 
               'Southern Europe', 'Western Europe', 'Australia and New Zealand', 'Melanesia', 'Micronesia', 'Polynesia']
    
    for countries, region in zip(iso_alpha3_code, subares):
        for country in countries:
            m49[country] = region
    
    if isinstance(data, str):
        return m49[data]
    else:
        return [m49[i] for i in data]