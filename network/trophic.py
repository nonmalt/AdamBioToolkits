import numpy as np
import pandas as pd

from pkgutil import get_data
from io import StringIO

from adamlearn.universal import format_check_np_ndarray
from scipy.optimize import minimize, rosen, rosen_der

# db load
net_db = get_data(__package__, 'netdb_v210909.csv')
net_db=str(net_db,'utf-8')
net_db = StringIO(net_db) 
net_db = pd.read_csv(net_db)

class TrophicNetEstimater:
    def __init__(self, f, n_levels, intake_id, net=net_db):
        self.f = f
        self.n_levels = n_levels
        
        if isinstance(intake_id, list):
            intake_id = np.array(intake_id)
        self.intake_id = intake_id
        self.net = net
        
    def _get_id(self, species_df):
        species_id = np.intersect1d(species_df.columns, self.net.species)
        
        metabolites_id = [self.net.loc[self.net.species == i,].metabolite.values for i in species_id] + [self.intake_id]
        metabolites_id = np.unique(np.concatenate(metabolites_id))

        return species_id, metabolites_id
        
    def _get_usage_matrix(self, species_id, metabolites_id, species_value):     
        import_matrix = np.zeros((species_id.shape[0], metabolites_id.shape[0]))
        import_matrix = pd.DataFrame(import_matrix, index=species_id, columns=metabolites_id)
        export_matrix = import_matrix.copy()
        
        for i in species_id:
            nodes = self.net.loc[self.net.species == i,]
            in_nodes = nodes.loc[nodes.activity.str.match('.*Consumption.*'),].metabolite.values
            out_nodes = nodes.loc[nodes.activity.str.match('.*Production.*'),].metabolite.values
            
            import_matrix.loc[i, in_nodes] = 1
            export_matrix.loc[i, out_nodes] = 1
        
        import_matrix = import_matrix * species_value.reshape(-1,1)
        in_degree = import_matrix.sum(axis=0).values.reshape(1,-1)
        in_degree[in_degree == 0] = 1
        import_matrix = import_matrix / in_degree
                
        out_degree = export_matrix.sum(axis=1).values.reshape(-1,1)
        out_degree[out_degree == 0] = 1
        export_matrix = export_matrix / out_degree
            
        return import_matrix, export_matrix
    
    def _multiple_trophic_net(self, species, intakes, f, n_levels, import_matrix, export_matrix):
        f_vector = np.ones((import_matrix.shape[0], 1)) * f
        f_vector = pd.DataFrame(f_vector, index=import_matrix.index, columns=['f'])
        
        selfish_node = export_matrix.index[export_matrix.sum(axis=1) == 0]
        f_vector.loc[selfish_node,:] = 0

        pred_microbes = np.zeros((1, species.shape[1]))
        pred_unused = np.zeros((1, import_matrix.shape[1]))
        pred_metabolites = intakes.copy().values.reshape(1,-1)
        
        unused_id = import_matrix.columns[import_matrix.sum(axis=0) == 0]
        unused_id = [list(import_matrix.columns).index(i) for i in unused_id]
        
        for n in range(self.n_levels):
            pred_used = np.dot(pred_metabolites, import_matrix.T)
            
            pred_biomass = pred_used * (1 - f_vector.values.reshape(1,-1))
            pred_microbes += pred_biomass
            
            if n != self.n_levels - 1:
                pred_unused[:, unused_id] += pred_metabolites[:, unused_id]
                pred_metabolites = pred_used * f_vector.values.reshape(1,-1)
                pred_metabolites = np.dot(pred_metabolites, export_matrix)
        
        pred_metabolites += pred_unused
        pred_metabolites = pd.DataFrame(pred_metabolites, columns=import_matrix.columns)
        pred_microbes = pd.DataFrame(pred_microbes, columns=import_matrix.index)
        return pred_microbes, pred_metabolites
    
    def _loss_function(self, intake_init, species, f, n_levels, import_matrix, export_matrix):
        intakes = np.zeros((import_matrix.shape[1],1))
        intakes = pd.DataFrame(intakes, index=import_matrix.columns)

        intakes.loc[self.intake_id,0] = intake_init
                
        pred_abundance = self._multiple_trophic_net(species, intakes, f, n_levels, import_matrix, export_matrix)[0].values

        pred_loss = (np.log10(pred_abundance + 1e-6) - np.log10(species.values.reshape(1, -1) + 1e-6))
        pred_loss = pred_loss / np.log10(species.values.reshape(1, -1) + 1e-6)
        pred_loss = np.sqrt(np.dot(pred_loss, pred_loss.T))
        return pred_loss.ravel()[0]
    
    def _fit_intake(self, species, f, n_levels, import_matrix, export_matrix):
        loss_fn = lambda intakes: self._loss_function(intakes, species, f, n_levels, import_matrix, export_matrix)
        limits = ((0, 100), ) * len(self.intake_id)
        intake_init = np.ones((self.intake_id.shape[0],)) / self.intake_id.shape[0]

        fitted = minimize(loss_fn, intake_init, method='SLSQP', bounds=limits, options={'disp':False, 'maxiter':1e3}, tol=1e-3)
        return fitted
        
    def estimate(self, sp_relab):
        # get id
        species_id, metabolites_id = self._get_id(sp_relab)
        
        # format species matrix
        species_lite = sp_relab.reindex(species_id, axis=1)
        species_norm = species_lite / species_lite.sum(axis=1).values.reshape(-1,1)
        
        # get in / out matrix
        import_matrix, export_matrix = self._get_usage_matrix(species_id, metabolites_id, species_norm.iloc[0,:].values)
    
        # fit & format intakes
        intakes_fit = self._fit_intake(species_norm, self.f, self.n_levels, import_matrix, export_matrix).x
        intakes = np.zeros((import_matrix.shape[1],1))
        intakes = pd.DataFrame(intakes, index=import_matrix.columns)
        intakes.loc[self.intake_id,0] = intakes_fit
        
        preds = self._multiple_trophic_net(species_norm, intakes, self.f, self.n_levels, import_matrix, export_matrix)
        return preds