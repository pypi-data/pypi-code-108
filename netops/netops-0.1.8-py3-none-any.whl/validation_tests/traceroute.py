import os


def traceroute_tests(ips_list, ip_address):
    """ TODO translate to english
    
    Executa testes de traceroute contra os endereços da lista de IPs, verificando se o endereco
    IP de entrada esta contido no path.
    
    Recebe:
            ips_list - lista de enderecos IP para executar os testes
            ip_address - endereco IP a ser verificado no path
            
    Retorna:
            successfull_full_tests - variavel boleana que indica se os testes foram bem sucedidos
            ou nao"""
    print("Target IP addresses for traceroute tests: ", ips_list)
    print("IP address for path verification: ", ip_address)
    successfull_results = []
    responses = []
    for ip in ips_list:
        print("Tracing route to %s ..." % ip)
        trace_query = f"traceroute {ip} --icmp -m 10 -q 1 -n"
        response = os.popen(trace_query).read()
        responses.append(trace_query)
        responses.append(response)
        if f"{ip_address}" in response:
            successfull_results.append(True)
            print("%s traceroute tests were successfull" % ip)
        else:
            successfull_results.append(False)
            print("%s traceroute tests failed" % ip)
    
    if True in successfull_results:
        successfull_full_tests = True
    else:
        successfull_full_tests = False

    return successfull_full_tests, responses