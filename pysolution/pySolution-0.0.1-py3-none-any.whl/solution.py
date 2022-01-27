from activity.run_model import *
from activity.osmotic import *
from activity.density_script import *

class Solution:
    def activity_coefficient (df, target_ion, T = 298.15):
        return pitzer_activity_coefficient(df, target_ion, T)

    def osmotic_coefficient_ (df, T = 298.15):
        return osmotic_coefficient(df, T)
    
    def ionic_strength_(df, T = 298.15):
        density_ = density(df, T)
        molality = [x * (1/density_) for x in df['Concentration (mol/L)']]
        
        d = {'Component' : df['Component'],
            'Molality' : molality,
            'Charge' : df['Charge']
            }
        
        return ionic_strength(pd.DataFrame(data = d))
    
    def density_(df, T = 298.15):
        rho = density(df, T)
        return rho
    
    def activity_water(df, T = 298.15):
        return activity_h2o(df, T)
    
    def notable_constants(df, T = 298.15):
        #constant "A^(phi)"
        A_ = A_calc(T)
        
        density_ = density(df, T)
        molality = [x * (1/density_) for x in df['Concentration (mol/L)']]
        d = {'Component' : df['Component'],
            'Molality' : molality,
            'Charge' : df['Charge']
            }
        
        df_prime = pd.DataFrame(data = d) #df with molality instead of concentration
        
        #constant F
        F_ = F_calc(df_prime, A_)
        
        #dielectric constant
        epsilon = dielectric_constant(T)
        
        return A_, F_, epsilon