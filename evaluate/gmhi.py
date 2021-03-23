import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from multiprocessing import cpu_count

class GutMicrobiomeHealthIndex():
    def __init__(self, ThetaF=0, ThetaD=0, n_jobs=1, low_abundance=1e-5, MaxF=2, MaxD=1, step=0.1):
        self.ThetaF = ThetaF
        self.ThetaD = ThetaD
        self.low_abundance = low_abundance
        self.MaxF = MaxF
        self.MaxD = MaxD
        self.step = step
        
        if n_jobs == -1:
            self.n_jobs = cpu_count()
        else:
            self.n_jobs = n_jobs
        
        
    def __species_prevalence(self, sample, M):
        sample = sample.loc[:, M]
        return sample.sum() / sample.shape[0]
    
    def __collective_abundance(self, sample, M):
        richness = sample.copy()
        richness[richness > 0] = 1
        
        RichnessOfMSpeciesInSample = sample[M].sum()
        SizeOfM = len(M)
        
        IndexSetOfM = sample.copy()
        IndexSetOfM = IndexSetOfM[M]
        IndexSetOfM = IndexSetOfM[IndexSetOfM != 0]
        
        GeometricMean = np.abs(IndexSetOfM * np.log(IndexSetOfM)).sum()
        
        return RichnessOfMSpeciesInSample / SizeOfM * GeometricMean
        
        
    def __ratio_of_collective_abundance(self, cabH, cabN):
        if cabH == 0:
            cabH = 1e-10
        if cabN == 0:
            cabN = 1e-10
        return np.log10(cabH / cabN)
    
    def __get_mlist(self, health, nonhealth, ThetaF, ThetaD):
        Mh, Mn = [], []
        for i in health.columns:
            PMh = self.__collective_abundance(health, i)
            PMn = self.__collective_abundance(nonhealth, i)
            
            if PMh == 0:
                PMh = 1e-10
            if PMn == 0:
                PMn = 1e-10
            
            PrevalenceFoldChange = PMh / PMn
            PrevalenceDifferece = PMh - PMn
            
            if (PrevalenceFoldChange > ThetaF) and (PrevalenceDifferece > ThetaD):
                Mh.append(i)
            
            if ((1 / PrevalenceFoldChange) > ThetaF) and ((-PrevalenceDifferece) > ThetaD):
                Mn.append(i)
            
        return Mh, Mn
    
    def __proportions_of_samples_classified(self, health, nonhealth, Mh, Mn):
        NTrueHealth = 0
        for i in health.index:
            i = health.loc[i, :]
            cabH = self.__collective_abundance(i, Mh)
            cabN = self.__collective_abundance(i, Mn)
            hiMM = self.__ratio_of_collective_abundance(cabH, cabN)
            
            if hiMM > 0:
                NTrueHealth = NTrueHealth + 1
        
        NTrueNonHealth = 0
        for i in nonhealth.index:
            i = nonhealth.loc[i, :]
            cabH = self.__collective_abundance(i, Mh)
            cabN = self.__collective_abundance(i, Mn)
            hiMM = self.__ratio_of_collective_abundance(cabH, cabN)
            
            if hiMM < 0:
                NTrueNonHealth = NTrueNonHealth + 1
        
        return (NTrueHealth / health.shape[0] + NTrueNonHealth / nonhealth.shape[0]) / 2
    
    def xMM(self, health, nonhealth, ThetaF, ThetaD):
        Mh, Mn = self.__get_mlist(health, nonhealth, ThetaF, ThetaD)
        xMM = self.__proportions_of_samples_classified(health, nonhealth, Mh, Mn)
        return xMM
        
    def fit(self, health, nonhealth):
        # Filter
        health[health < self.low_abundance] = 0
        nonhealth[nonhealth < self.low_abundance] = 0
        
        # De-redundancy features
        health = health.loc[:, health.sum(axis=0) != 0]
        nonhealth = nonhealth.loc[:, nonhealth.sum(axis=0) != 0]
        features_col = set(list(health.columns) + list(nonhealth.columns))

        health = health.reindex(features_col, axis=1).fillna(0)
        nonhealth = nonhealth.reindex(features_col, axis=1).fillna(0)

        # params search
        if (self.ThetaF == 0) or (self.ThetaD == 0):
            RangeThetaF = np.arange(1+self.step, self.MaxF, self.step)
            RangeThetaD = np.arange(self.step, self.MaxD, self.step)
            
            RangeThetaFD = []
            for F in RangeThetaF:
                for D in RangeThetaD:
                    RangeThetaFD.append([F, D])
            
            ThetaSearch = Parallel(n_jobs=self.n_jobs)(delayed(self.xMM)(health, nonhealth, i[0], i[1]) for i in RangeThetaFD)
            OptimTheta = RangeThetaFD[np.argmax(ThetaSearch)]
            self.ThetaF = OptimTheta[0]
            self.ThetaD = OptimTheta[1]
            self.accuracy = max(ThetaSearch)

        # get species list
        self.Mh, self.Mn = self.__get_mlist(health, nonhealth, self.ThetaF, self.ThetaD)

    def transform(self, sample):
        if type(sample) == pd.core.series.Series:
            cabH = self.__collective_abundance(sample, self.Mh)
            cabN = self.__collective_abundance(sample, self.Mn)
            hiMM = self.__ratio_of_collective_abundance(cabH, cabN)
        
        elif type(sample) == pd.core.frame.DataFrame:
            hiMM = []
            for idx in sample.index:
                samp = sample.loc[idx, :]
                cabH = self.__collective_abundance(samp, self.Mh)
                cabN = self.__collective_abundance(samp, self.Mn)
                hiMMSingle = self.__ratio_of_collective_abundance(cabH, cabN)
                hiMM.append(hiMMSingle)
            
            hiMM = pd.DataFrame(hiMM, index=sample.index, columns=['GMHI'])   
        return hiMM