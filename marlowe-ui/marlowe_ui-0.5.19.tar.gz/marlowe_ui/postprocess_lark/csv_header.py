# headers required for cascade data
cascade_index = ['Cascade', 'Group', 'Number']

cascade_detail_initial_defect_lattice = ['File', 'Site',
        'Location X', 'Location Y', 'Location Z', 'Paired Atom']

cascade_detail_initial_defect_atom = ['File', 'Atom', 'KARMA',
        'Initial Location X', 'Initial Location Y', 'Initial Location Z',
        'Reference Lattice Site X', 'Reference Lattice Site Y', 'Reference Lattice Site Z',
        'Site']

cascade_report_detail_1 = ['File', 'Atom', 'Karma',
        'Initial Time', 'Initial Energy',
        'Initial Location X', 'Initial Location Y', 'Initial Location Z',
        'Initial Location Site', 'Trak', 'Nseq']

cascade_report_detail_2 = ['File', 'Atom', 'Karma',
        'Final Time', 'Final Energy',
        'Final Direction Cosine X', 'Final Direction Cosine Y', 'Final Direction Cosine Z']

cascade_report_detail_3 = ['File', 'Atom', 'Karma',
        'Final Location X', 'Final Location Y', 'Final Location Z',
        'Reference Lattice Site X', 'Reference Lattice Site Y', 'Reference Lattice Site Z',
        'Reference Lattice Site']

# Detailed Description of the Cascade 1, 2, 3
cascade_report_detail_all = cascade_index +\
        cascade_report_detail_1 + cascade_report_detail_2[3:] + cascade_report_detail_3[3:]

# Location of Lattice Sites
cascade_report_lattice_sites = [
        'File', 'Lattice Site', 'Lattice Location X', 'Lattice Location Y',
        'Lattice Location Z', 'Paired Atom File']

cascade_report_lattice_sites_all = cascade_index + cascade_report_lattice_sites + [
        # reference to cascade data
        'Paired Atom', 'Paired Atom Final Location X', 'Paired Atom Final Location Y',
        'Paired Atom Final Location Z', 'Distance']

cascade_orgiv = [
        # distant I-V table
        'Pair Number', 'Vacancy Site', 'Vacancy File', 'Interstitial Atom',
        'Interstitial File', 'Distance']

cascade_orgiv_all = cascade_index + cascade_orgiv + [
        # reference to LatticeSite
        'Vacancy Lattice Location X', 'Vacancy Lattice Location Y',
        'Vacancy Lattice Location Z',
        # reference to cascade data
        'Interstitial Final Location X', 'Interstitial Final Location Y',
        'Interstitial Final Location Z']

cascade_ranger = ['Elem', 'Radial', 'Penetration', 'Spread', 'Total Path', 'Time (fs)']
cascade_ranger_all = cascade_index + cascade_ranger

final_rangex = ['Range of', 'Mean', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev', 'Error'] + ['Count']
final_slavex_number = ['Total number of', 'Mean', 'Variance', 'Skewness', 'Kurtosis', 'Std Dev', 'Error'] + ['Count']
