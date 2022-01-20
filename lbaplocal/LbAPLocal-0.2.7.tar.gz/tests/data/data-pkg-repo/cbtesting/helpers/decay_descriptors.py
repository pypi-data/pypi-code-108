# FILE CONTAINING ALL DECAY DESCRIPTORS

dict_rec = {
    'Lb2JpsiL_mm'  :'[Lambda_b0 ->   ^(J/psi(1S) -> ^mu+  ^mu-)   ^(Lambda0 -> ^p+ ^pi-)]CC',
    'Lb2JpsiL_ee'  :'[Lambda_b0 ->   ^(J/psi(1S) -> ^e+  ^e- )    ^(Lambda0 -> ^p+ ^pi-)]CC',
    'Lb2Lmm_SS'    :'[Lambda_b0 ->   ^(J/psi(1S) -> ^mu+  ^mu+)   ^(Lambda0 -> ^p+ ^pi-)]CC',
    'Lb2Lee_SS'    :'[Lambda_b0 ->   ^(J/psi(1S) -> ^e+  ^e+ )    ^(Lambda0 -> ^p+ ^pi-)]CC',
    'Lb2Lemu'      :"[Lambda_b0 -> [ ^(J/psi(1S) -> ^e+  ^mu-)]CC ^(Lambda0 -> ^p+ ^pi-)]CC",
    'Lb2Lemu_SS'   :"[Lambda_b0 -> [ ^(J/psi(1S) -> ^e+  ^mu-)]CC ^(Lambda0 -> ^p+ ^pi-)]CC",
    'Bd2JpsiKs_mm' :'        B0 ->   ^(J/psi(1S) -> ^mu+  ^mu-)   ^(KS0     -> ^pi+ ^pi-)   ',
    'Bd2JpsiKs_ee' :'        B0 ->   ^(J/psi(1S) -> ^e+  ^e- )    ^(KS0     -> ^pi+ ^pi-)   ',
    'Bd2Ksmm_SS'   :'        B0 ->   ^(J/psi(1S) -> ^mu+  ^mu+)   ^(KS0     -> ^pi+ ^pi-)   ',
    'Bd2Ksee_SS'   :'        B0 ->   ^(J/psi(1S) -> ^e+  ^e+ )    ^(KS0     -> ^pi+ ^pi-)   ',
    'Bd2Ksemu   '  :"        B0 -> [ ^(J/psi(1S) -> ^e+  ^mu-)]CC ^(KS0     -> ^pi+ ^pi-)   ",
    'Bd2Ksemu_SS'  :"        B0 -> [ ^(J/psi(1S) -> ^e+  ^mu+)]CC ^(KS0     -> ^pi+ ^pi-)   ",
    'Bu2JpsiK_mm'  :'[       B+ ->   ^(J/psi(1S) -> ^mu+  ^mu-)   ^K+                   ]CC',
    'Bu2JpsiK_ee'  :'[       B+ ->   ^(J/psi(1S) -> ^e+  ^e- )    ^K+                   ]CC',
    'Bu2Kmm_SS'    :'[       B+ ->   ^(J/psi(1S) -> ^mu+  ^mu+)   ^K+                   ]CC',
    'Bu2Kee_SS'    :'[       B+ ->   ^(J/psi(1S) -> ^e+  ^e+ )    ^K+                   ]CC',
    'Bu2Kemu   '   :"[       B+ -> [ ^(J/psi(1S) -> ^e+  ^mu-)]CC ^K+                   ]CC",
    'Bu2Kemu_SS'   :"[       B+ -> [ ^(J/psi(1S) -> ^e+  ^mu+)]CC ^K+                   ]CC",
}

dict_mc = {
    'Lb2LJpsmm'    :'[Lambda_b0 =>  ^(J/psi(1S) => ^mu+  ^mu-)    ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2LJpsee'    :'[Lambda_b0 =>  ^(J/psi(1S) => ^e+  ^e- )    ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2LPsimm'    :'[Lambda_b0 =>  ^(  psi(2S) => ^mu+  ^mu-)    ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2LPsiee'    :'[Lambda_b0 =>  ^(  psi(2S) => ^e+  ^e- )    ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2Lee'       :'[Lambda_b0 =>                 ^e+  ^e-      ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2Lmm'       :'[Lambda_b0 =>                 ^mu+  ^mu-     ^(Lambda0 => ^p+ ^pi-)]CC',
    'Lb2Lem'       :"([Lambda_b0 =>                 ^e+  ^mu-      ^(Lambda0 => ^p+ ^pi-)]CC) || ([Lambda_b0 =>  ^e-  ^mu+ ^(Lambda0 => ^p+ ^pi-)]CC)",
    'Bd2Ksmm'      :'    [B0]cc =>                 ^mu+  ^mu-     ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2Ksee'      :'    [B0]cc =>                 ^e+  ^e-      ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2KsJpsmm'   :'    [B0]cc =>  ^(J/psi(1S) => ^mu+  ^mu-)    ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2KsJpsee'   :'    [B0]cc =>  ^(J/psi(1S) => ^e+  ^e- )    ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2KsPsimm'   :'    [B0]cc =>  ^(  psi(2S) => ^mu+  ^mu-)    ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2KsPsiee'   :'    [B0]cc =>  ^(  psi(2S) => ^e+  ^e- )    ^(KS0     => ^pi+ ^pi-)   ',
    'Bd2Ksemu'     :"    [B0]cc =>                  ^e+  ^mu-      ^(KS0   => ^pi+ ^pi-)  ||      [B0]cc =>  ^e-  ^mu+ ^(KS0    => ^pi+ ^pi-)    ",
    'Bu2JpsiK_mm'  :'[       B+ =>  ^(J/psi(1S) => ^mu+  ^mu-)    ^K+                   ]CC',
    'Bu2JpsiK_ee'  :'[       B+ =>  ^(J/psi(1S) => ^e+  ^e- )    ^K+                   ]CC',
    'Bu2PsiK_mm'   :'[       B+ =>  ^(  psi(2S) => ^mu+  ^mu-)    ^K+                   ]CC',
    'Bu2PsiK_ee'   :'[       B+ =>  ^(  psi(2S) => ^e+  ^e- )    ^K+                   ]CC',
    'Bu2Kemu'      :"([      B+ =>                 ^e+  ^mu-     ^K+                   ]CC) || ([       B+ =>  ^e-  ^mu+ ^K+                   ]CC)",

}

dict_mc_noV0dec = {k : ( v if 'Bu' in k
                 else v.replace('=> ^pi+ ^pi-)','').replace('(KS0','KS0') if 'Bd' in k
                 else v.replace('=> ^p+ ^pi-)' ,'').replace('(Lam','Lam') )
                 for (k,v) in dict_mc.items() }
print dict_mc_noV0dec
for keys,vals in dict_mc_noV0dec.iteritems():
    print keys,vals

def tuple_branches(decay_desc_full):
    # Now add resonances for data/MC and different b hadrons
    tuple_branches = []
    particles      = []

    # Some configuration
    charm_resonances = ['J/psi(1S)','psi(2S)']
    V0_resonances    = ['Lambda0'  ,'KS0'    ]

    V0dec = ('pi' in decay_desc_full) # Needed to add branches

    Lb_decay = ('Lambda' in decay_desc_full)
    Bd_decay = ('B0'     in decay_desc_full)
    Bu_decay = ('B+'     in decay_desc_full)

    # First add the b and s hadrons
    if Lb_decay: 
        tuple_branches = ['Lb','L0']
        particles     += ['Lambda0']
    elif Bd_decay:
        tuple_branches = ['B','K0'] 
        particles     += ['KS0']
    elif Bu_decay: 
        tuple_branches = ['B','K']  
        particles     += ['K+']

    # take leptons from decay descriptor
    # decay descriptor has first lepton after first or second ^ 
    # ['e+ ','mu+)    '] is an example string
    first_lepton = 1 

    # Add Jpsi if needed and appropriate leptons
    for charm_resonance in ['J/psi(1S)','psi(2S)']:
        if charm_resonance in decay_desc_full: # FOR DecayTree or MCTree with Jpsi
            tuple_branches += ['JPs']
            particles += [charm_resonance]        
            first_lepton += 1

    # Format leptons for SS parsing
    leptons = decay_desc_full.split('^')[first_lepton:first_lepton+2]
    print ('leptons',leptons)
    leptons[0] = leptons[0].replace(' ','')
    leptons[1] = leptons[1].split(')')[0].replace(' ','')
    print ('leptons',leptons)

    # Add lepton branches
    tuple_branches += ['L1','L2']    
    particles += leptons

    # Check if SS tuple, used to add correct L2 matching
    SS_tuple = (leptons in [['e+','e+'],['e+','mu+'],['mu+','mu+']])

    # Add hadrons if the Lambda decays
    if V0dec:
        if Lb_decay:
            tuple_branches += ['P'  ,'Pi' ]
            particles += ['p+','pi-']
        elif Bd_decay:
            tuple_branches += ['Pi1','Pi2']
            particles += ['pi+','pi-']

    # Replace hats to get individual particles
    decay_desc = decay_desc_full.replace('^','') # remove hats because only one will be needed
    decay_desc_list = decay_desc.split('||') # TO DEAL WITH emu case: split e+mu- and e-mu+

    print particles
    print tuple_branches


    # add single hats
    branches = { tuple_branches[0] : decay_desc  }
    for i in range(len(tuple_branches)-1):
        print i
        part = particles[i]

        if part in charm_resonances or (part in V0_resonances and V0dec): 
            part = '('+part # To replace (Lambda for ex.

        # Run over separate decay_desc to deal with e+mu- and e-mu+ case
        decay_desc_replaced = []
        for j in range(len(decay_desc_list)): # For each separate list, replace
            if j == 0:
                decay_desc_replaced.append(decay_desc_list[j].replace(' '+part,'^'+part,1) )
                decay_desc_tot = decay_desc_replaced[j]
                print decay_desc_tot

            else:     
                if 'e' in part or 'mu' in part:
                    if '-' in part: part = part.replace('-','+')
                    else:           part = part.replace('+','-') # Swap charge for opposite charge lepton pair
                print part
                print decay_desc_list[j]
                decay_desc_replaced.append(decay_desc_list[j].replace(' '+part,'^'+part,1) )
                decay_desc_tot = "{0} || {1}".format(decay_desc_tot,decay_desc_replaced[j])

        branches[tuple_branches[i+1]] = decay_desc_tot

    if SS_tuple: #IF SAME SIGN IN TUPLE BRANCHES 
        # decay desc has ^e+   e+ twice
        print branches
        input_string  = '^{0}  {1}'.format(leptons[0],leptons[1])
        output_string = ' {0} ^{1}'.format(leptons[0],leptons[1])
        print input_string,output_string
        branches['L2'] = branches['L2'].replace(input_string,output_string)

    return branches,tuple_branches

