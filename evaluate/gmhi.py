import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from multiprocessing import cpu_count

class GutMicrobiomeHealthIndex():
    '''
        Update: 2021/09/23
        New:
            Rewrite & Imporve performance
    '''
    def __init__(self, ThetaF=0, ThetaD=0, low_abundance=1e-5, MaxF=2, MaxD=1, step=0.1, n_jobs=1):
        self.ThetaF = ThetaF
        self.ThetaD = ThetaD
        self.low_abundance = low_abundance
        self.MaxF = MaxF + step
        self.MaxD = MaxD + step
        self.step = step
        self.n_jobs = n_jobs
    
    def __get_Mlist(self, Hea, NonHea, ThetaF, ThetaD):
        self.Mh, self.Mn = [], []
        
        PMh = (Hea > self.low_abundance).sum(axis=0) / Hea.shape[0]
        PMh = PMh.mask(PMh == 0, 1e-10)
        PMn = (NonHea > self.low_abundance).sum(axis=0) / NonHea.shape[0]
        PMn = PMn.mask(PMn == 0, 1e-10)

        PrevalenceFoldChange = PMh / PMn
        PrevalenceDifferent = PMh - PMn
        
        self.Mh = np.intersect1d(PrevalenceFoldChange.index[PrevalenceFoldChange > ThetaF],
                                 PrevalenceDifferent.index[PrevalenceDifferent > ThetaD])
        self.Mn = np.intersect1d(PrevalenceFoldChange.index[1/PrevalenceFoldChange > ThetaF],
                                 PrevalenceDifferent.index[-PrevalenceDifferent > ThetaD])
    
    def __collective_abundance(self, df, M):
        if M.shape[0] > 0:
            RichnessRel = (df.reindex(M, axis=1) > 0).sum(axis=1) / M.shape[0]

            dfm = df.reindex(M, axis=1)
            PsiM = (dfm[dfm>0]) * np.log(dfm[dfm>0]) # Shannon index
            return RichnessRel * PsiM.sum(axis=1) * -1
        else:
            return None
        
    def __scoring(self, df):
        PsiMh = self.__collective_abundance(df, self.Mh)
        PsiMh = PsiMh if PsiMh is not None else 0

        PsiMn = self.__collective_abundance(df, self.Mn)
        return np.log10((PsiMh+1e-5)/(PsiMn+1e-5)) if PsiMn is not None else None
    
    def __balanced_accuracy(self, Hea, NonHea):
        Hacc = (self.__scoring(Hea) > 0).sum() / Hea.shape[0] if self.__scoring(Hea) is not None else 0
        Nacc = (self.__scoring(NonHea) < 0).sum() / NonHea.shape[0] if self.__scoring(NonHea) is not None else 0
        return (Hacc + Nacc) / 2
    
    def _parallel_fitting(self, Hea, NonHea, ThetaF, ThetaD):
        self.__get_Mlist(Hea, NonHea, ThetaF, ThetaD)
        return self.__balanced_accuracy(Hea, NonHea)
        
    def fit(self, Hea, NonHea):
        if (self.ThetaF == 0) or (self.ThetaD == 0):
            RangeThetaFD = []
            for F in np.arange(1+self.step, self.MaxF, self.step):
                for D in np.arange(self.step, self.MaxD, self.step):
                    RangeThetaFD.append([F, D])
        
            ThetaSearch = Parallel(n_jobs=self.n_jobs)(delayed(self._parallel_fitting)(Hea, NonHea, *i) for i in RangeThetaFD)
    
            self.ThetaF, self.ThetaD = RangeThetaFD[np.argmax(ThetaSearch)]
            self.accuracy = max(ThetaSearch)
        
        self.__get_Mlist(Hea, NonHea, self.ThetaF, self.ThetaD)
    
    def predict(self, df):
        pred = self.predict_proba(df)
        for i in pred.index:
            if pred.loc[i, 'GHMI'] > 0:
                pred.loc[i, 'GHMI'] = 'Healthy'
            elif pred.loc[i, 'GHMI']  < 0:
                pred.loc[i, 'GHMI'] = 'NonHealthy'
        return pred
    
    def predict_proba(self, df):
        return pd.DataFrame(self.__scoring(df), columns=['GHMI'])