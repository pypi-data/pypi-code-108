import os


def reachability_tests(ips_list, pkt_num):
    """ TODO translate to english
    
    Executa testes basicos de alcancabilidade contra uma lista de enderecos IP.
    
    Recebe:
            ips_list - lista de enderecos IP para executar os testes
            pkt_num - numero de pacotes a executar os testes
            
    Retorna:
            successfull_full_tests - variavel boleana que indica se os testes foram bem sucedidos
            ou nao"""
    print("Target IP addresses for reachability tests: ", ips_list)
    successfull_results = []
    results = {"successfull_reach_tests": []}
    for ip in ips_list:
        print("Pinging %s ..." % ip)
        response = os.popen(f"ping -c {pkt_num} -n -W 1 {ip}").read()
        if f"{pkt_num} received" in response:
            successfull_results.append(True)
            print("%s reachability tests were successfull" % ip)
            results["successfull_reach_tests"].append(ip)
        else:
            successfull_results.append(False)
            print("%s reachability tests failed" % ip)
    
    if True in successfull_results:
        successfull_full_tests = True
    else:
        successfull_full_tests = False
        results["successfull_reach_tests"].append("all tests failed")

    return successfull_full_tests, results