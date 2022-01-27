'''
Created on 23 May 2018

@author: mra003
'''
import numpy as np
from scipy.stats import norm
import  math
from scipy import  linalg

from sklearn.isotonic import IsotonicRegression

from dpcgeneration.nearest_correlation import nearcorr


class Copulafuncs(object):






    def rescale(self, b0,b1,n):
        s = b0 + b1
        r = n/s
        b0 = int(round(b0 * r))
        b1 = int(round(b1 * r))
        if b0+b1 == n:
            return b0,b1
        else:
            flag = True;
            while flag ==  True:
                s=b0+b1
                i = np.random.randint(0, 1)
                if s == n:
                    flag = False
                elif  s < n:
                    if i ==0 :
                        b0 += 1
                    else:
                        b1 += 1
                else:
                    if i ==0 :
                        b0 -= 1
                    else:
                        b1 -= 1
                        
        #print (b0,b1)                 
        return b0,b1
    
    
    
    def rescale2(self, m,n, sameMarginal):
        s = sum(m.values())
        #print ("1")
        #print (s,n,m)
        r=n/s
        #print (r)
        m2 = {"00":0, "01":0, "10":0, "11":0 }
        s2=0
        for key in m:
            #print (m[key], r ,m[key] * r )
            m2[key] =  round(m[key] * r)
            s2 += m2[key] 
        s=sum(m2.values())
        #print ("2")
        #print (s,s2, n,m2)
        if s==n:
            return m2
        else:
            flag = True
            while flag == True:
                k = np.random.choice(list(m2))
                if (sameMarginal== True and k == "11") :
                    print ("")
                else:
                    #print (k)
                    if s< n:
                        m2[k] += 1
                        s=sum(m2.values())
                    elif s>n:
                        m2[k] -= 1
                        s=sum(m2.values())
                    else:
                        flag = False
        #print ("3")
        #print (m,m2)
        return m2
    
    
    
    def samemargine(self, dic_col,i,j):
            if j<= i:
                print ("problem!!!!!!")
            
            for key in dic_col:
                intervalle = dic_col[key]
                if i >= intervalle[0] and i<= intervalle[1]:
                    if j <= intervalle[1]:
                        return True
                    else:
                        return False
            return False
    
    def getRto_Q(self, vali,j,mul,threshold, dic_border, dic_col):
        i= int(vali)
        #print (i)
        #if samemargine(dic_border, i, j):
        #    return -0.99999
        
        meani = threshold[i]
        meanj = threshold[j]
        #del(test_corr_coeff_array)
        test_corr_coeff_step = 0.01
        test_corr_coeff_array =  np.arange(-0.999,1.001,test_corr_coeff_step)#[-0.9999 -0.999:test_corr_coeff_step:0.999 0.9999]
        test_corr_coeff_array1 = np.append(-0.9999, test_corr_coeff_array)
        test_corr_coeff_array2 = np.append(test_corr_coeff_array1, 0.9999)
        test_corr_coeff_array = test_corr_coeff_array2
            #print (mul) 
        
        
            
            
       
    
        
        yi_array_step = 0.01
        yj_array_step = 0.01
        yi_array_in_integral = np.arange(-5,5+yi_array_step,yi_array_step)
        yj_array_in_integral = np.arange(-5,5+yi_array_step,yj_array_step)
        len_yj_array = len(yj_array_in_integral) 
        len(yi_array_in_integral), len (yj_array_in_integral)
        yi_matrix = np.tile(yi_array_in_integral, (len_yj_array, 1))
                #print (yi_matrix.shape)
        yj_matrix = yi_matrix .T
        type(yi_matrix.shape)
        yi_matrix[999,0]
                
        yj_matrix[0,999]
                
        normcdf_yi_matrix = norm.cdf(yi_matrix)
        normcdf_yj_matrix = norm.cdf(yj_matrix)
        Xi_matrix_check_forXiXj = self.getFminux(normcdf_yi_matrix,meani,  dic_col[i])#(normcdf_yi_matrix >= meani).astype(int)   #
                        #print ("Xi_matrix_check_forXiXj")
                        #print (meani)
        Xj_matrix_check_forXiXj = self.getFminux(normcdf_yj_matrix,meanj, dic_col[j])#  (normcdf_yj_matrix >= meanj).astype(int) #
                        
        
        if j < 100000:
        #for j in range (attribute_num):
            #print(i,j)
                #  perform the bisection algorithm
            left_test_corr_coeff = -0.9999
            right_test_corr_coeff = 0.9999
            mid_test_corr_coeff = (left_test_corr_coeff+right_test_corr_coeff)/2
                # set the falg of the bisection search to 0
            flag_bisection_search_termination = 0
            
                    
            while flag_bisection_search_termination == 0:
                test_corr_coeff_tmp_array = [left_test_corr_coeff,right_test_corr_coeff,mid_test_corr_coeff]
                test_cov_matrix_tmp_array = np.zeros( 3)
                
                for test_idx  in range(3):
                        test_corr_coeff = test_corr_coeff_tmp_array[test_idx]
                       
                        #get the testing joint normal distribution
                        test_joint_norm_pdf = 1/(2*np.pi)/(np.sqrt(1-test_corr_coeff**2)) * np.exp( -1 * (yi_matrix**2 + yj_matrix**2 - 2*test_corr_coeff * yi_matrix*yj_matrix) / (2*(1-test_corr_coeff**2)) )
                        
                        #sanity check (normalization criterion)
                        if abs(np.sum(test_joint_norm_pdf)*yi_array_step*yj_array_step - 1) > 1e-3:
                            print('something wrong with the joint normal pdf')
        
                        #print ("Xj_matrix_check_forXiXj")
                        #print (Xj_matrix_check_forXiXj)    
                        #test_cov_matrix{row_idx, col_idx}(test_corr_coeff_idx) = ...
                        #sum(sum(Xi_matrix_check_forXiXj{row_idx, col_idx} .* Xj_matrix_check_forXiXj{row_idx, col_idx} .* test_joint_norm_pdf, 1), 2)*yi_array_step*yj_array_step
                        test_cov_matrix_tmp_array[test_idx] = np.sum(Xi_matrix_check_forXiXj * Xj_matrix_check_forXiXj * test_joint_norm_pdf)*yi_array_step*yj_array_step
                        #print ('summm',np.sum(Xi_matrix_check_forXiXj * Xj_matrix_check_forXiXj * test_joint_norm_pdf))
                        #print ("********* test_cov_matrix_tmp_array**********", i, test_cov_matrix_tmp_array)
                        #exit()
                        
                #exit()
                #print (i,j, '!!!!test_cov_matrix_tmp_array', test_cov_matrix_tmp_array, mul)
                if test_cov_matrix_tmp_array[1] > test_cov_matrix_tmp_array[0] and test_cov_matrix_tmp_array[1] <= mul:
                        #print("extreme case") 
                        mid_test_corr_coeff = right_test_corr_coeff
                        test_cov_matrix_tmp_array[2] = test_cov_matrix_tmp_array[1]
                        flag_bisection_search_termination = 1
                elif test_cov_matrix_tmp_array[1] > test_cov_matrix_tmp_array[0] and test_cov_matrix_tmp_array[0] >= mul:
                        #print("extreme case2")
                        mid_test_corr_coeff = left_test_corr_coeff
                        test_cov_matrix_tmp_array[2] = test_cov_matrix_tmp_array[0]
                        flag_bisection_search_termination = 1
                elif test_cov_matrix_tmp_array[1] < test_cov_matrix_tmp_array[0] and test_cov_matrix_tmp_array[0] <= mul:
                        #print("extreme case3")
                        mid_test_corr_coeff = left_test_corr_coeff
                        test_cov_matrix_tmp_array[2] = test_cov_matrix_tmp_array[0]
                        flag_bisection_search_termination = 1
                elif test_cov_matrix_tmp_array[1] < test_cov_matrix_tmp_array[0] and test_cov_matrix_tmp_array[1] >= mul:
                        #print("extreme case4")
                        mid_test_corr_coeff = right_test_corr_coeff
                        test_cov_matrix_tmp_array[2] = test_cov_matrix_tmp_array[1]
                        flag_bisection_search_termination = 1
                elif abs(test_cov_matrix_tmp_array[2] - mul) < 1e-9:
                        #print(" find the solution")
                        flag_bisection_search_termination = 1
               
                else :
                    #print("normal cases")
                    if test_cov_matrix_tmp_array[2] >= test_cov_matrix_tmp_array[0] and test_cov_matrix_tmp_array[2] <= test_cov_matrix_tmp_array[1]:
                            
                        if test_cov_matrix_tmp_array[2] > mul:
                            #print("overestimation")
                            left_test_corr_coeff = left_test_corr_coeff
                            right_test_corr_coeff = mid_test_corr_coeff
                            mid_test_corr_coeff = (left_test_corr_coeff+right_test_corr_coeff)/2
                        else:
                            #print("underestimation")
                            #print(mul)
                            left_test_corr_coeff = mid_test_corr_coeff
                            right_test_corr_coeff = right_test_corr_coeff
                            mid_test_corr_coeff = (left_test_corr_coeff+right_test_corr_coeff)/2
                    elif test_cov_matrix_tmp_array[2] <= test_cov_matrix_tmp_array[0] and  test_cov_matrix_tmp_array[2] >= test_cov_matrix_tmp_array[1]:
                        if test_cov_matrix_tmp_array[2] > mul:
                            #print("overestimation 2")
                            left_test_corr_coeff = mid_test_corr_coeff
                            right_test_corr_coeff = right_test_corr_coeff
                            mid_test_corr_coeff = (left_test_corr_coeff+right_test_corr_coeff)/2
                        else:
                            #print("underestimation 2")
                            left_test_corr_coeff = left_test_corr_coeff
                            right_test_corr_coeff = mid_test_corr_coeff
                            mid_test_corr_coeff = (left_test_corr_coeff+right_test_corr_coeff)/2             
                    else:
                        mid_test_corr_coeff =   (i,j,mul,meani,meanj)
                        flag_bisection_search_termination = 1
                        #print('unknown case')
                            
            estimated = mid_test_corr_coeff
            #print (estimated_corr_coeff_matrix[j])
            
        
        
        return str(i),str(j),str(estimated)
    
    def file_len(self, fname):
        
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1
    
    
    
    
    
    
    def getFminux(self, mat, threshold, dict):
        
                #y = np.ones((mat.shape))*dict[0]
        #print (mat)
        #print ('getFminux', len(threshold), len(dict))
        y = np.zeros((mat.shape))
       
        for i in range(len(threshold)-1,0,-1):
            #print (i, 'getFminux threshold',threshold )
            #print (i, 'getFminux dict',dict )
            #print (threshold)
            #print ((threshold[i] > mat) & (mat >= threshold[i-1]))
            #print((mat >= threshold[i-1]).astype(int) * dict[i])
            y += (((threshold[i] > mat) & (mat >= threshold[i-1])).astype(int) * dict[i] )
            
            
        # y += (y == 0).astype(int) * dict[0]     
        
        y += ( threshold[0] > mat).astype(int)*dict[0] 
        
        
        
        return y
    
    def strictly_increasing(self, L):
        return all(x<y for x, y in zip(L, L[1:]))
    
    def strictly_decreasing(self, L):
        return all(x>y for x, y in zip(L, L[1:]))
    
    
    def bisectionalSearch(self, threshold_arrays, target_cov_value_matrix, colM,colS,  dic_col):
        result = math.inf
        limit1=-0.99999
        limit2=0.99999
        valeur_finale = target_cov_value_matrix#[colM,colS]
        step = 0.01#0.01
        loopi = np.arange(-5,5+step,step)
        i_matrix = np.tile(loopi, (len(loopi), 1))
       
        ij_matrix = [i_matrix, i_matrix .T]
        
        normcdf_matrix = [norm.cdf(i_matrix),norm.cdf(i_matrix .T)]
        #print(dic_col)
        threshold_arrays_col =[threshold_arrays[colM],threshold_arrays[colS]]
        dic_col_col =[dic_col[colM], dic_col[colS]]
        
        Xi_matrix_check_forXiXj = self.getFminux(normcdf_matrix[0],threshold_arrays_col[0], dic_col_col[0])# (normcdf_yi_matrix >= threshold_arrays[colM]).astype(int)   
        Xj_matrix_check_forXiXj = self.getFminux(normcdf_matrix[1],threshold_arrays_col[1], dic_col_col[1])# (normcdf_yj_matrix >= threshold_arrays[colS]).astype(int)   
        
        
        while abs(result-valeur_finale)> 1e-9 :
            #a = pd.Interval(left=limit1, right=limit2)
           
            step_research =abs(limit1-limit2)/10. 
            list_floats = np.arange(limit1, limit2+step_research, step_research)#[limit1,a.mid,limit2]#np.arange(limit1, limit2, step_research)#
            #print ('list_floats\n',list_floats)
            estim =np.zeros(len(list_floats))
            for i in range(len(list_floats)):#list_floats:
                estim[i] =  self.calculatePhi(list_floats[i], Xi_matrix_check_forXiXj,  Xj_matrix_check_forXiXj,ij_matrix, 0.01 )#calculatePhi(threshold_arrays, colM, colS, list_floats[i], dic_col)
                if np.isnan(estim[i]):
                    estim[i] = estim[i-1] 
            value =  min(estim, key=lambda x:abs(x-valeur_finale))#bisect.bisect(estim,valeur_finale)
            ind , = np.where(estim == value)#estim.index(val)
            ind = min(ind)
            #print ('start', colM, colS, 'estim', estim,  'valeur_finale', valeur_finale, 'indice', ind)
            if ind ==0 :
                #print (colM, colS, 'estim_0', estim,  'valeur_finale', valeur_finale)
                if estim[0] <= valeur_finale <= estim[1]:
                    limit1=list_floats[0]
                    limit2=list_floats[1]
                    ind=0
                elif valeur_finale<estim[0]:
                    limit2 = list_floats[ind]
                    limit1 = -0.99999999
                    ind=0
                    if limit1 == limit2 :
                        return (colM,colS, list_floats[0])
                else :
                    return (colM,colS, list_floats[0])
               
            elif ind == len(list_floats):
                if estim[len(list_floats)-1] <= valeur_finale <= estim[len(list_floats)]:
                    limit1=list_floats[ind-1]
                    limit2 = estim[len(list_floats)]
                    ind =len(estim)-1
                elif valeur_finale>estim[len(list_floats)]:
                    limit1=list_floats[ind]
                    limit2 =0.99999999
                    if limit1 == limit2 :
                        return (colM,colS, list_floats[len(list_floats)])
                else :
                    return (colM,colS, list_floats[len(list_floats)])
                
                #print ("****", valeur_finale, ind, estim[ind-1], 1)
            else:
                if estim[ind-1] <= valeur_finale <= estim[ind]:
                    limit1=list_floats[ind-1]
                    limit2 = list_floats[ind]
                elif ind+1 < len(list_floats) and  estim[ind] <= valeur_finale <= estim[ind+1]:
                    limit1=list_floats[ind]
                    limit2 = list_floats[ind+1]
                else :
                    return (colM,colS, list_floats[ind])
                #print ("****", valeur_finale, ind, estim[ind-1], estim[ind])
            
            #print (colM, colS, 'estim', estim,  'valeur_finale', valeur_finale, 'indice', ind)
            
            result=estim[ind]
            
            #print (result)
        '''    
        if  list_floats[ind] >= 1:
            list_floats[ind] = 0.99999999
        if  list_floats[ind] <= -1:
            list_floats[ind] = -0.99999999
            
         '''   
            
        
        return colM,colS, list_floats[ind]
    
    
    
    def calculatePhi(self, ro, Xi_matrix_check_forXiXj,  Xj_matrix_check_forXiXj,  ij_matrix, step ):
        
        total =0
        try: 
            
            phi = 1/(2*np.pi)/(np.sqrt(1-ro**2)) * np.exp( -1 * (ij_matrix[0]**2 + ij_matrix[1]**2 - 2*ro * ij_matrix[0]*ij_matrix[1]) / (2*(1-ro**2)) )
            #print ('phi', phi[0,0], phi[50,50], phi[100,100])
            #Xi_matrix_check_forXiXj = self.getFminux(normcdf_matrix[0],threshold_arrays_col[0], dic_col_col[0])# (normcdf_yi_matrix >= threshold_arrays[colM]).astype(int)   
            #print ('Xi_matrix_check_forXiXj',colM, threshold_arrays[colM],  Xi_matrix_check_forXiXj[0,0], Xi_matrix_check_forXiXj[50,50], Xi_matrix_check_forXiXj[100,100])
            #Xj_matrix_check_forXiXj = self.getFminux(normcdf_matrix[1],threshold_arrays_col[1], dic_col_col[1])# (normcdf_yj_matrix >= threshold_arrays[colS]).astype(int)   
            total = np.sum(Xi_matrix_check_forXiXj * Xj_matrix_check_forXiXj * phi)*step*step
         
            
        except ZeroDivisionError:
            print("calculatePhi ",ro)
        
        return total
      
    def getPearson_Q_NSPD_Ncorr(self,mat, attribute_num):
        #print (np.linalg.eigvalsh(mat))
        chol_decomp_matrix = linalg.cholesky(mat)
        mod_chol_decomp_matrix = chol_decomp_matrix / np.tile(np.sqrt(np.sum(chol_decomp_matrix**2,axis=0)), (attribute_num, 1))
        Pearson_Q_NSPD_Ncorr = mod_chol_decomp_matrix.T.dot(mod_chol_decomp_matrix)
        return Pearson_Q_NSPD_Ncorr
    
    def get_mat_len (self,mat) :
            size_mat= mat.shape
            record_num = size_mat[0]
            attribute_num = size_mat[1]
            return (record_num,attribute_num)
        
    
    
    def is_pos_def(self,x):
        return np.all(np.linalg.eigvals(x) > 0)
    
    
    def nearestSPD(self,A):
        '''
        r_num, a_num= get_mat_len(A)   
        if r_num ==1 :
            return np.spacing(1)
        # symmetrize A into B
        B = (A + A.T)/2
        
        # Compute the symmetric polar factor of B. Call it H.
        # Clearly H is itself SPD.
        U, Sigma, Vh = np.linalg.svd(B)
        V = Vh.T
        H = (V*Sigma).dot(V.T)
        # get Ahat in the above formula
        Ahat = (B+H)/2
        #  ensure symmetry
        Ahat = (Ahat + Ahat.T)/2
        #test that Ahat is in fact PD. if it is not so, then tweak it just a bit.
        p=1
        k=0
        
        while is_pos_def(Ahat) == False:
            k += 1
            t, t2= np.linalg.eigh(Ahat)
            #  Ahat failed the chol test. It must have been just a hair off,
            # due to floating point trash, so it is simplest now just to
            # tweak by adding a tiny multiple of an identity matrix.
            mineig = min(t)
            #print (min(t))
            Ahat = Ahat + (-mineig*(k**2) + np.spacing(mineig))*np.identity(A.shape[0]);
        
        return Ahat
        '''
        X = nearcorr(A,max_iterations=10000)
        if self.checkispositivedef(X) :
            return X
        else:
            
            min_eig = np.min(np.real(np.linalg.eigvals(X)))
            
            if min_eig < 0:
                X -= 10*min_eig * np.eye(*X.shape)
            
            return X
        
        
    def checkispositivedef(self,mat):
        if np.all(np.linalg.eigvals(mat) > 0):
            #print  ('Yes it''s positive definite ')
            return True
        else:
            #print  ('No it''s not positive definite' )
            return False
            
            
    
        
    
    
    def getRto_Q_alreadydone(self,attribute_num,path_fin, prefix):
        # mapping from R to Q in Apr. 2017 as follows
        #print (attribute_num)
        shape = (attribute_num, attribute_num)
        estimated_corr_coeff_matrix=np.zeros(shape)
        
        for i in range(attribute_num):
            #print (i)
            
            file_est = path_fin+prefix+'-estimate-'+str(i)+'.csv'
            colest= np.loadtxt(file_est)
            for j in range(i):
                estimated_corr_coeff_matrix[i,j]=estimated_corr_coeff_matrix[j,i]
            for j in range(i, attribute_num):
                estimated_corr_coeff_matrix[i,j]=colest[j]
                
                      
    
        
        
        return estimated_corr_coeff_matrix
    
    
    def generate_records(self,in_file_name, attribute_num, out_file, Pearson_Q_NSPD_Ncorr, Gauss_universe_threshold_array):
       
        nb_file=0
        record_num = self.file_len(in_file_name)
        with open(out_file, 'w') as f:
            
            
            while nb_file <= record_num : 
            
                Y = np.random.multivariate_normal(np.zeros( attribute_num), Pearson_Q_NSPD_Ncorr, 1000)  
                
                X_prime =np.zeros([1000, attribute_num])
                    #current_probability_array= np.zeros(params.attribute_num)
                
                for i in range(attribute_num):
                    X_prime[:, i] = np.single(Y[:, i] >= Gauss_universe_threshold_array[i])
                    
                
                #print (len(X_prime))   
            
            
            
                for i in range(1000):
                    #print (i)
                    ll=''
                    for j in range(attribute_num):
                        ll+= str(int(X_prime[i,j]))+ ","
                    f.write(ll + '\n')
                    nb_file += 1
                    if nb_file >= record_num:
                        break
              
    
    
              
    def calculEstimationOtherMethod (self,i,j,mul,meani,meanj):
        
        yi_array_step = 0.01
        yj_array_step = 0.01
        yi_array_in_integral = np.arange(-5,5+yi_array_step,yi_array_step)
        yj_array_in_integral = np.arange(-5,5+yi_array_step,yj_array_step)
    
        len_yj_array = len(yj_array_in_integral)
        len(yi_array_in_integral), len (yj_array_in_integral)
        yi_matrix = np.tile(yi_array_in_integral, (len_yj_array, 1))
        yj_matrix = yi_matrix .T
        type(yi_matrix.shape)
        yi_matrix[999,0]
        yj_matrix[0,999]
        #del(test_corr_coeff_array)
        test_corr_coeff_step = 0.005
        test_corr_coeff_array=np.arange(-0.999,1.001,test_corr_coeff_step) #[-0.9999 -0.999:test_corr_coeff_step:0.999 0.9999]
        test_corr_coeff_array1 = np.append(-0.9999, test_corr_coeff_array)
        test_corr_coeff_array2 = np.append(test_corr_coeff_array1, 0.9999)
        test_corr_coeff_array = test_corr_coeff_array2
        
        test_cov_matrix = np.empty(len(test_corr_coeff_array))
        test_cov_matrix[:] = np.NAN
        #print (test_cov_matrix)
        normcdf_yi_matrix = norm.cdf(yi_matrix)
        
        normcdf_yj_matrix = norm.cdf(yj_matrix)
        Xi_matrix_check_forXiXj = (normcdf_yi_matrix >= meani).astype(int)
        Xj_matrix_check_forXiXj = (normcdf_yj_matrix >= meanj).astype(int)   
        for test_corr_coeff_idx in range(len(test_corr_coeff_array)):
            test_corr_coeff = test_corr_coeff_array[test_corr_coeff_idx];
            test_joint_norm_pdf = 1/(2*np.pi)/(np.sqrt(1-test_corr_coeff**2)) * np.exp( -1 * (yi_matrix**2 + yj_matrix**2 - 2*test_corr_coeff * yi_matrix*yj_matrix) / (2*(1-test_corr_coeff**2)) )
            test_cov_matrix[test_corr_coeff_idx]   = np.sum(Xi_matrix_check_forXiXj * Xj_matrix_check_forXiXj * test_joint_norm_pdf)*yi_array_step*yj_array_step             
        
        a=abs(test_cov_matrix-mul)
        min_idx = a.argmin(0)
        estimated_corr_coeff_matrix = test_corr_coeff_array[min_idx]
        return estimated_corr_coeff_matrix
    
    
    #Using the Isotonic Regression, smooth the curve
    #https://scikit-learn.org/stable/auto_examples/plot_isotonic_regression.html
    def makesmooth(self, dcit):
        dictlist_cdf = np.cumsum(list(dcit.values()) )          
        x=np.arange(len(dictlist_cdf))
        ir=IsotonicRegression()
        smoothdictlistcdf = ir.fit_transform(x, dictlist_cdf)
        dict_smooth = {}
        idx=0
        nbidx=0
        for key in dcit:
            dict_smooth[key]= int(smoothdictlistcdf[idx])-nbidx
            nbidx+=dict_smooth[key]
            idx +=1
            
        
        return dict_smooth
        
        
    #Obsolete work
    def addNoiseAndRescale_propotionnellement(self, dictlist, scale, record_num):  #_propotionnellement
        dictlist_return = {}
        #print ( 'dictlist start!!!!!', dictlist)  
        for key in dictlist.keys():
            lap= np.random.laplace(0, scale, 1)
            dictlist_return[key]=round(float(max(0, dictlist[key]+lap)))
        #print (key, 'addNoiseAndRescale dico', dictlist_return)
      
        
        dictlist_return = self.makesmooth(dictlist_return)
        
        
        
        
        if (sum(dictlist_return.values())== record_num):
           
            #print ( 'dictlist_return!!!!!', dictlist_return)  
            return dictlist_return
        else:
            summ=sum(dictlist_return.values())
            if summ>0:
                for key in dictlist_return.keys():
                    #print (dictlist_return[key])
                    dictlist_return[key]=int (dictlist_return[key]*record_num/summ)
                            
            dictlist_return = self.makesmooth(dictlist_return)
            while True:
                for key in dictlist_return.keys():
                    diff = sum(dictlist_return.values())- record_num
                    if diff == 0:
                        #print ( 'dictlist_return!!!!!', dictlist_return)  
                        return dictlist_return
                    elif diff>0 :
                        dictlist_return[key]= max(0, dictlist_return[key]-1)
                    else:
                        dictlist_return[key]+=1
    
    
    
    # Add laplace noise to all values of one attribute and rescale
    def addNoiseAndRescale(self,attribute_name, dictlist, scale, record_num):  
        
        dictlist_return0, dictlist_return = {}, {}
        leskeys=dictlist.keys()
        
        
        #Step 1 : Add noise to all values  
          
        for key in leskeys:
            lap= np.random.laplace(0, scale, 1)

            if key in dictlist:
                dictlist_return0[key]=round(float(max(0, dictlist[key]+lap)))
            else:
                dictlist_return0[key]=round(float(max(0, lap)))
        
        #Step 2 After adding noise to all the values, Smooth the curve  
          
        dictlist_return = self.makesmooth(dictlist_return0)
        #Step 3 After smoothing, rescale to the right size 
        
        if (sum(dictlist_return.values())== record_num):
           return dictlist_return
        else:
            summ=sum(dictlist_return.values())
            
            #Step3.1 calculate proportionally how much I add or decrease each value 
            #print (summ)
            nb_positive = sum(x > 0 for x in dictlist_return.values())


            
            if summ>0:
                add = round((record_num - summ) / nb_positive)
                for key in dictlist_return.keys():
                    
                    dictlist_return[key]=max(int (dictlist_return[key]+ add),0)
            #summ=sum(dictlist_return.values())
            #Step3.2 add or remove 1 until I reach the right size  
            while True:
                
                #print (summ, record_num, record_num, '#element', len(dictlist_return.values()))
                for key in dictlist_return.keys():
                    
                    diff = sum(dictlist_return.values())- record_num
                    #print ('Start step3.2', diff, add, summ, record_num)  
                    if diff == 0:
                        #print ( 'dictlist_return!!!!!', dictlist_return)  
                        return dictlist_return
                    elif diff>0 :
                        dictlist_return[key]= max(0, dictlist_return[key]-1)
                    else:
                        dictlist_return[key]+=1
                
   
    def addNoiseAndRescale_Paul(self, dictlist, scale, record_num):
        dictlist_return = {}
        for key in dictlist.keys():
            lap= np.random.laplace(0, scale, 1)
            dictlist_return[key] = int((dictlist[key]+ lap)[0])
            
            
       
        dictlist4_tmp ={k:0 for k in dictlist_return.keys()}
        for k in dictlist_return.keys():
            s = sum(dictlist4_tmp.values())
            if dictlist_return[k] > 0 and s>record_num-dictlist_return[k]:
                dictlist4_tmp[k]=record_num-s
                #print ('end addNoiseAndRescale_Paul', dictlist4_tmp, sum(dictlist4_tmp.values()) )
                return dictlist4_tmp
            else:
                if dictlist_return[k] > 0:
                    dictlist4_tmp[k]= dictlist_return[k]
                    
        
        k = np.random.choice(list(dictlist4_tmp.keys()))
        diff=record_num - sum(dictlist4_tmp.values()) 
        dictlist4_tmp[k] += diff
        #print ('add diff=',diff, ' k=', k, ' record_num=',record_num, ' sum(dictlist4_tmp.values()=',sum(dictlist4_tmp.values() ))
        '''print (diff)
        for k in     dictlist4_tmp.keys():
           
            dictlist4_tmp[k] += 1
            print ('addNoiseAndRescale_Paul ', k, ' 4=', dictlist4_tmp[k], ' 3=', dictlist_return[k])
            diff -= 1
            if diff ==0 : 
                return dictlist4_tmp
        #print ('end2 addNoiseAndRescale_Paul', dictlist4_tmp, sum(dictlist4_tmp.values()) )
        '''
        return dictlist4_tmp
    
    
        '''while flag == True:
            
            
            s=sum(dictlist_return.values())
            if s == record_num:
                flag = False
            else:
                
                k = np.random.choice(list(dictlist_return.keys()))
                
                dictlist_return[k] += (record_num-s)
            
        print ('end addNoiseAndRescale_Paul', dictlist_return)       
        return dictlist_return
        '''
    
    # Calculate 2-way noisy marginals, Pearson R, target_cov
    def getPearson_R(self,i,j, coli_init,colj_init,  noise, scale, nb_row, nb_bin, names ):
       
        twoway ={}
        twoway_init={}
        #print ('start getPearson_R')
        
        # Step0 Concatenate Coli and Colj 
        colij_init = np.array(len(coli_init))
        colij_init = [str(coli_init[k])+'/'+str(colj_init[k])  for k in range(len(coli_init))]
        
        # Step1 Calculate 2way counts
        unique_init, counts_init = np.unique(colij_init, return_counts=True)
        dictlist_tmp_init = dict(zip(unique_init, counts_init))   
        
        
        if noise == True:
            
            #Add all the empty possiblilities
            valuesi = np.unique(coli_init)
            valuesj = np.unique(colj_init)
            for a in  valuesi:
                for b in  valuesj:
                    if not str(a)+'/'+str(b) in dictlist_tmp_init:
                        dictlist_tmp_init[str(a)+'/'+str(b)]=0
           
            
            '''
            Obsolete work
            colsij[i]=coli_init
            
            colsij[j]=colj_init
            
            
            valuesij = {}
            for l in [i,j]:
                more1M = sorted(n for n in colsij[l] if n >= 1000000)
                less1M = sorted(n for n in colsij[l] if n < -1000000)
                if names[l] in ['c_gender','ml_depend_child','c_sa4_id','c_occupation','sp_flag','c_birth_fy']:
                    valuesij[l] = np.unique(colsij[l])
                elif names[l] == 'i_salary_wage':
                    valuesij[l] = [0,1] + [tt for tt in range(1000,100000, 1000)] + [tt for tt in range(100000, 500000, 10000)] + [tt for tt in range(500000, 1000000, 100000)]+more1M
                elif names[l] == 'is_bus_pp' or names[l] == 'is_bus_npp':
                    valuesij[l] = less1M+ [tt for tt in range(-1000000,-100000, 100000)]+[tt for tt in range(-100000, -30000, 10000)]+ [tt for tt in range(-30000,-1, 1000)] 
                    valuesij[l] +=[-1,0,1] + [tt for tt in range(1000,30000, 1000)] + [tt for tt in range(30000, 100000, 10000)] + [tt for tt in range(100000, 1000000, 100000)]+more1M
                elif names[l] == 'divident' or names[l] == 'i_interest' or names[l] == 'dc_total_ded':    
                    valuesij[l] = [0,1] + [tt for tt in range(1000,10000, 1000)] + [tt for tt in range(10000, 100000, 10000)] + [tt for tt in range(100000, 1000000, 100000)]+more1M
                elif names[l] == 'i_gov_payments'  or names[l] == 'i_gov_pension'  :
                    valuesij[l] = [0,1] + [tt for tt in range(1000,22000, 1000)] + [22000] +more1M
                elif names[l] == 'Partnership&Trust':
                    valuesij[l] = less1M+ [tt for tt in range(-1000000,-100000, 100000)]+[tt for tt in range(-100000, -10000, 10000)]+[tt for tt in range(-10000, -1, 1000)]
                    valuesij[l] += [-1, 0,1] + [tt for tt in range(1000,10000, 1000)] + [tt for tt in range(10000, 100000, 10000)] + [tt for tt in range(100000, 1000000, 100000)]+more1M
            
            
            list_valuesij =[]
            for a in  valuesij[i]:
                for b in  valuesij[j]:
                    list_valuesij.append(str(a)+'/'+str(b))
            
            for valiouj in list_valuesij:
                if not valiouj in dictlist_tmp_init.keys():
                    dictlist_tmp_init[valiouj] =0
            '''
                        
            #Add noise and rescale the 2way
            dictlist_return_noisy = self.addNoiseAndRescale(str(i)+'_'+str(j), dictlist_tmp_init, scale, nb_row)
            #dictlist_return_noisy = self.addNoiseAndRescale_Paul(dictlist_tmp_init, scale, nb_row)
             
            
            
            #Create Now the new noisy columns from noisy counts
            coli, colj  = np.array([]),  np.array([])
            for key in dictlist_return_noisy.keys():
                
                coli_noisy =np.zeros(dictlist_return_noisy[key])
                colj_noisy = np.zeros(dictlist_return_noisy[key])
               
                tab = key.replace('.0','').split('/')
               
                #print (i,j,'dictlist_return_noisy', dictlist_return_noisy[key], 'key', key)
                
                res0 = int(float(tab[0]))
                
                
                for z in range(dictlist_return_noisy[key]):
                    
                    coli_noisy[z]=res0
                    colj_noisy[z] = int(tab[1]);
                    
                twoway_init[str(i)+'_'+tab[0]+'/'+str(j)+'_'+tab[1]]=dictlist_tmp_init[key]
                twoway[str(i)+'_'+tab[0]+'/'+str(j)+'_'+tab[1]]=dictlist_return_noisy[key]
                                    
                    
                coli = np.append( coli, (coli_noisy))
                colj = np.append( colj, (colj_noisy))
                
                                
                                
                            
                                
        else:
            coli = coli_init
            colj= colj_init
            
            for key in dictlist_tmp_init.keys():
                tab = key.replace('.0','').split('/')
                twoway_init[str(i)+'_'+tab[0]+'/'+str(j)+'_'+tab[1]]=dictlist_tmp_init[key]
                    
                twoway[str(i)+'_'+tab[0]+'/'+str(j)+'_'+tab[1]]=twoway_init[str(i)+'_'+tab[0]+'/'+str(j)+'_'+tab[1]]
                                
        
       
                  
        colij = [str((coli[k]))+'/'+str((colj[k]))  for k in range(len(coli))]
       
        #Step to check that everything is correct!
        unique, counts = np.unique(colij, return_counts=True)
        dictlist_tmp = dict(zip(unique, counts))
        '''print ('new dictlist_tmp', dictlist_tmp)
        print ('twoway_init', twoway_init)
        print ('twoway', twoway)
        '''
        #Step2 Calculate pearsonR                    
        res2 = np.corrcoef(coli,colj)
        R=res2[1,0]
        
        #Calculate noisy 1-way for each column
        unique, counts = np.unique(coli, return_counts=True)
        oneway1 =dict(zip(unique.astype(int), counts))
        unique, counts = np.unique(colj, return_counts=True)
        oneway2 =dict(zip(unique.astype(int), counts))
        
        
        oneway_inter={}
        oneway_inter[i] = oneway1
        oneway_inter[j] = oneway2
        
        #Step3 Calculate target covariance
        target_cov_value_matrix=np.mean(coli*colj)
        
        
        return i,j,R,target_cov_value_matrix, twoway, twoway_init, oneway_inter
