
class InvoiceStruct():
    def __init__(self):
        '''
        Lista de referencia dos valores previstor, realizados e antecipações
        - Atualiza valores previstos
            - 02 - Inclusão
            - 03 - Exclusão
            - 12 - Desconto (decréscimo)
            - 13 - Acréscimo
            - 14 - Estorno desconto (decréscimo)
            - 15 - Estorno acréscimo
        - Atualiza os valores realizados
            - 06 - Baixa
            - 17 - Estorno de Baixa
            - 97 - Baixa de Saldo
            - 98 - Estorno de Baixa de Saldo
        - Não geram efeito de atualização nos valores dos títulos
            - 90 - Transferência
            - 91 - Estorno de transferência
            - 95 - Transferência de borderô
            - 96 - Estorno de transferência de borderô
        '''
        self.struct = {}
        self.predicted_codes = ['02','03', '12', '13', '14', '15']
        self.accomplished_codes = ['06', '17', '97', '98']
        self.anticipation = ['90', '91', '95', '96']
    
    
    def add_organization(self, org_id):
        if org_id not in self.struct.keys():
            self.struct.update({org_id:{}})
    
    
    def add_invoice(self, org_id, invoice_id):
        self.add_organization(org_id)
        
        if invoice_id not in self.struct[org_id].keys():
            self.struct[org_id].update({invoice_id:{}})
        
        
    def add_installment(self, org_id, invoice_id, installment_id):
        self.add_invoice(org_id, invoice_id)
        
        if installment_id not in self.struct[org_id][invoice_id].keys():
            self.struct[org_id][invoice_id].update({installment_id:{'value':0,
                                                            'balance':0,
                                                            'anticipated':False,
                                                            'duedate':None,
                                                            'paymentdate':None,
                                                            'late_days':None,
                                                            'sequence_code':None,
                                                            'discount':False,
                                                            'docissue':None,
                                                            'anticipation_date':None,
                                                            'anticipation_value':0,
                                                            'days_to_receive':0,
                                                            'docreference':None,
                                                            'doctype':None,
                                                            'paid_value':0,
                                                            'federalid':None,
                                                            'erp_id_installment':None,
                                                            'paymentsreference':None,
                                                            'transactiontype':None,
                                                            'excluded':False}})
    
    
    def add_payment(self, org_id, invoice_id, installment_id, value, code, sequence_code,
                    docissue, duedate, paymentdate, issuedate, docreference, doctype, federalid, erp_id_installment,
                    paymentsreference,transactiontype):
        
        self.add_installment(org_id, invoice_id, installment_id)
        
        # Para manter aderencia a LGPD o CPF do cliente é anonimizado
        if doctype == 'CPF':
            docreference = docreference[0:3]+'*****'+docreference[-3:]
        
        # Se o título já está excluído, não permito mais nenhuma atualização de saldo ou de valor previsto.
        # Isso foi adicionado para contornar um problema nos mapeamentos da Carol que incluiam eventos em títulos
        # excluidos, provocando divergencias nos valores de saldo.
        if not self.struct[org_id][invoice_id][installment_id]['excluded']:
            
            # Atualizo os installments com os valores previstos
            if code in self.predicted_codes:
                actual_value = self.struct[org_id][invoice_id][installment_id]['value']
                actual_value += value

                actual_balance = self.struct[org_id][invoice_id][installment_id]['balance']
                actual_balance += value

                discount = self.struct[org_id][invoice_id][installment_id]['discount']

                # Verifico se foi dado desconto
                if code == '12':
                    discount = True
                elif code == '14':
                    discount = False

                # Verifico se o título possui evento de exclusão
                excluded = False
                
                if code == '03':
                    excluded = True

                self.struct[org_id][invoice_id][installment_id].update({'value':actual_value,
                                                                'balance':actual_balance,
                                                                'duedate':duedate,
                                                                'sequence_code':sequence_code,
                                                                'discount':discount,
                                                                'docissue':docissue,
                                                                'docreference':docreference,
                                                                'doctype':doctype,
                                                                'federalid':federalid,
                                                                'erp_id_installment':erp_id_installment,
                                                                'paymentsreference':paymentsreference,
                                                                'transactiontype':transactiontype,
                                                                'excluded':excluded})

            # Atualizo os installments com os valores realizados
            elif code in self.accomplished_codes:

                # Os valores de baixa são sempre negativos e os valores de estorno positivos.
                # Somando todos esses valores temos o saldo do título
                actual_balance = self.struct[org_id][invoice_id][installment_id]['balance']
                actual_balance += value

                # Para saber o valor pago temos que inverter o sinal
                paid_value = self.struct[org_id][invoice_id][installment_id]['paid_value']
                paid_value += (value * -1)

                late_days = (paymentdate - duedate).days

                if late_days < 0:
                    late_days = 0
                self.struct[org_id][invoice_id][installment_id].update({'balance':actual_balance,#add .round(2)
                                                                'paymentdate':paymentdate,
                                                                'late_days':late_days,
                                                                'sequence_code':sequence_code,
                                                                'docissue':docissue,
                                                                'paid_value':paid_value})# .round(2)

            # Atualizo os installments com as antecipações
            elif code in self.anticipation:
                if code in ['90', '95']:
                    days_to_receive = (duedate - issuedate).days
                    self.struct[org_id][invoice_id][installment_id].update({'anticipated':True, 'anticipation_date':issuedate, 'days_to_receive':days_to_receive})

                    if code == '90':
                        self.struct[org_id][invoice_id][installment_id].update({'anticipation_value':value})

                elif code in ['91', '96']:
                    self.struct[org_id][invoice_id][installment_id].update({'anticipated':False,
                                                                            'anticipation_date':None,
                                                                            'anticipation_value':0,
                                                                            'days_to_receive':0})
                    
                    
            