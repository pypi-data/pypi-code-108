def os_to_sap_forces_col(col_results):
    # Στύλοι: -V1 -N1 M1 V2 N2 -M2
    return[-col_results[1], -col_results[0], col_results[2], col_results[4], col_results[3], -col_results[5]]

def os_to_sap_forces_beam(col_results):
    # Δοκοί: (±)N1 -V1 -M1 (±)N2 V2 M2
    # Για το αξονικό δεν το έλεγξα γιατί δεν υπήρχε στα παραδείγματα λόγω διαφράγματος
    return[col_results[0], -col_results[1], -col_results[2], col_results[3], col_results[4], col_results[5]]