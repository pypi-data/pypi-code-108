class Cliente:

    def __init__(self, codigo_referencia, nome, razao_social,
                 cpf, rg, data_nascimento, cnpj, sexo,
                 email, orgao, RegistroEstadual, TelefoneResidencial,
                 TelefoneCelular, Endereco, EnderecoEntrega):
        self.codigo = codigo_referencia
        self.nome = nome
        self.razao_social = razao_social
        self.cpf = cpf
        self.rg = rg
        self.data_nascimento = data_nascimento
        self.cnpj = cnpj
        self.sexo = sexo
        self.email = email
        self.orgao = orgao
        self.RegistroEstadual = RegistroEstadual
        self.TelefoneResidencial = TelefoneResidencial
        self.TelefoneCelular = TelefoneCelular

        if Endereco is not None:
            self.Endereco = EnderecoCliente(**Endereco)

        if EnderecoEntrega is not None:
            self.EnderecoEntrega = EnderecoCliente(**EnderecoEntrega)


class EnderecoCliente:

    def __init__(self, cep, logradouro, numero,
                 complemento, bairro, cidade, estado,
                 pais, referencia, descricao, tipo_logradouro):
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.pais = pais
        self.referencia = referencia
        self.descricao = descricao
        self.tipo_logradouro = tipo_logradouro

    def get_sql(self):
        sql = '''INSERT INTO lojasinfinity_openkuget.usuario
                        (id, loja_id, client_id, processado,
                        datapedido, valor, valor_frete,
                        status_canal_id, status, canal_venda_id,
                        data_criacao, forma_envio)
                VALUES (null, 1, 147, 1, '''
        + self.cep + ','
        + self.logradouro + ','
        + self.numero + ','
        + self.complemento + ','
        + self.bairro + ','
        + self.cidade + ','
        + self.estado + ','
        + self.tipo_logradouro
        + ')'
        return sql
