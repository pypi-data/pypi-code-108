import pygame
import sys
import threading
import time
import os

pasta_do_projeto = os.path.dirname( os.path.abspath(__file__) )
pasta_das_imagens = pasta_do_projeto

pausado = False
pygame.init()
##O pygame.time.Clock().tick( frequência ) deve ser sempre usado em
##um loop infinito, se não o programa fica desincronizado e os objetos
##não se movem com a velocidade que deveriam

#Usado para parar as threadings
rodar_threading = True

#Lista com objetos que serão exibidos na tela
lista_de_objetos = []

#botoes que serao usados
lista_de_botoes = []

#lista de textos
lista_de_textos = []

tecla_apertada = pygame.key.get_pressed

#testa se uma tecla está sendo apertada
def esta_apertada( tecla ):
    return tecla_apertada()[tecla]

#definição de tecla.
#importante definir mais teclas

#letras
tecla_a = pygame.K_a
tecla_b = pygame.K_b
tecla_c = pygame.K_c
tecla_d = pygame.K_d
tecla_e = pygame.K_e
tecla_f = pygame.K_f
tecla_g = pygame.K_g
tecla_h = pygame.K_h
tecla_i = pygame.K_i
tecla_j = pygame.K_j
tecla_k = pygame.K_k
tecla_l = pygame.K_l
tecla_m = pygame.K_m
tecla_n = pygame.K_n
tecla_o = pygame.K_o
tecla_p = pygame.K_p
tecla_q = pygame.K_q
tecla_r = pygame.K_r
tecla_s = pygame.K_s
tecla_t = pygame.K_t
tecla_u = pygame.K_u
tecla_v = pygame.K_v
tecla_w = pygame.K_w
tecla_x = pygame.K_x
tecla_y = pygame.K_y
tecla_z = pygame.K_z

#numeros do centro do teclado
tecla_0 = pygame.K_0
tecla_1 = pygame.K_1
tecla_2 = pygame.K_2
tecla_3 = pygame.K_3
tecla_4 = pygame.K_4
tecla_5 = pygame.K_5
tecla_6 = pygame.K_6
tecla_7 = pygame.K_7
tecla_8 = pygame.K_8
tecla_9 = pygame.K_9

#números do teclado numérico
tecla_numero_0 = pygame.K_KP0
tecla_numero_1 = pygame.K_KP1
tecla_numero_2 = pygame.K_KP2
tecla_numero_3 = pygame.K_KP3
tecla_numero_4 = pygame.K_KP4
tecla_numero_5 = pygame.K_KP5
tecla_numero_6 = pygame.K_KP6
tecla_numero_7 = pygame.K_KP7
tecla_numero_8 = pygame.K_KP8
tecla_numero_9 = pygame.K_KP9

#setas
tecla_seta_para_esquerda = pygame.K_LEFT
tecla_seta_para_direita = pygame.K_RIGHT
tecla_seta_para_cima = pygame.K_UP
tecla_seta_para_baixo = pygame.K_DOWN

#teclas especiais
tecla_espaco = pygame.K_SPACE

#Define cor de fundo da tela
#Podemos criar algumas variávei para cores simples, como as cores primárias
#Permitindo assim que a cor seja mudada
maroon = pygame.color.THECOLORS['maroon4'] #[ 139, 28, 48 ]

vermelho = pygame.color.THECOLORS['red']
verde = pygame.color.THECOLORS['green']
azul = pygame.color.THECOLORS['blue']

azul_escuro = pygame.color.THECOLORS['darkblue']
verde_escuro = pygame.color.THECOLORS['darkgreen']

roxo = pygame.color.THECOLORS['purple']
amarelo = pygame.color.THECOLORS['yellow']
laranja = pygame.color.THECOLORS['orange']

rosa = pygame.color.THECOLORS['pink']
cinza = pygame.color.THECOLORS['gray']
marrom = pygame.color.THECOLORS['brown']

preto = pygame.color.THECOLORS['black']
branco = pygame.color.THECOLORS['white']


#algumas direçoes
para_esquerda = [-1,0]
para_direita = [1,0]
para_cima = [0,-1]
para_baixo = [0,1]
direcao_nula = [0,0]

#define gravidade do programa e aplica nos objetos
gravidade = 10
def aplicar_gravidade():
    while rodar_threading:
        pygame.time.Clock().tick( 10 )
        for objeto in lista_de_objetos:
            if( objeto.cai and not objeto.pousou ):
                objeto._velocidade_de_queda += gravidade

t_aplicar_gravidade = threading.Thread( target = aplicar_gravidade )
t_aplicar_gravidade.start()

#Classe usada para definir objetos que aparecerão no programa
#Deve ser passada uma imagem para que o objeto seja criado
#Demais características devem ser alteradas após a criação do objeto
class Objeto():
    def __init__(self, nome_da_imagem = 'galinha'):
        #Para threading do objeto quando apagado
        self._existe = True
        #define imagem 
        self.nome_da_imagem = nome_da_imagem
        
        #define área da imagem
        self.area_da_imagem = self.imagem.get_rect()

        #usado quando o tamanho da imagem é alterado
        self.manter_proporcao = True

        #A velocidade define a taxa com que o objeto se move na tela
        #Pode ser lida como pixels por segundo
        self.velocidade = 100
        self.direcao = [0,0]

        #Permite deixar os objetos invisíveis
        self.visivel = True

        #Inicia teclas que movem o objeto como nenhuma tecla
        self.tecla_mover_para_esquerda = 0
        self.tecla_mover_para_direita = 0
        self.tecla_mover_para_cima = 0
        self.tecla_mover_para_baixo = 0

        #Inicia botoes
        self.botao_mover_para_esquerda = 0
        self.botao_mover_para_direita = 0
        self.botao_mover_para_cima = 0
        self.botao_mover_para_baixo = 0

        #manter ou não na tela
        self.manter_na_tela = True
        
        #usado para obter bordas através dos
        #métodos property
        #largura em pixels
        self.largura_da_borda = 5
        
        #Propriedades para tratar colisões
        self.solido = True
        self.estatico = False
        
        #define se thread deve parar
        self.rodar_thread = True
        #Define objeto usado para rodar a função mover em paralelo
        self.threading_mover = threading.Thread(target= self.mover)

        #Começa a rodar função mover em paralelo
        self.threading_mover.start()

        #Usados para a gravidade
        self.cai = False
        self._velocidade_de_queda = 0

        #Define objeto usado para rodar a função mover em paralelo
        self.threading_cair = threading.Thread(target= self._cair )

        #Começa a rodar função mover em paralelo
        self.threading_cair.start()

        #funcao com movimentos
        self.movimentos_paralelos = []

        #Acrescenta objeto à lista de objetos, fora da definição da classe
        #para que ele possa ser exibido na tela 
        lista_de_objetos.append(self )

    def apagar(self):
        if( self.existe ):
            self._existe = False
            lista_de_objetos.remove(self)
            self.area_da_imagem.width = 0
            self.area_da_imagem.height = 0
            self.direita = -10
            self.base = -10

    #nome da imagem
    @property
    def nome_da_imagem(self):
        return self._nome_da_imagem

    @nome_da_imagem.setter
    def nome_da_imagem(self, nome_da_imagem ):
        self._nome_da_imagem = nome_da_imagem
        if( '.' not in self._nome_da_imagem ):
            self._nome_da_imagem += '.png'
            self._nome_da_imagem = os.path.join( pasta_das_imagens, self._nome_da_imagem)
        self.imagem = pygame.image.load(self._nome_da_imagem)

    #mostra se objeto existe
    @property
    def existe(self ):
        return self._existe


    #colisões
    def realizar_colisoes(self):            
        if( self.solido ):
            for objeto in lista_de_objetos:
                if( objeto.solido ):
                    if( self.borda_direita.colliderect( objeto.borda_esquerda ) ):
                        self.direita = objeto.esquerda + 1
                    if( self.borda_esquerda.colliderect( objeto.borda_direita ) ):
                        self.esquerda = objeto.direita - 1
                    if( self.borda_superior.colliderect( objeto.borda_inferior ) ):
                        self.topo = objeto.base - 1
                    if( self.borda_inferior.colliderect( objeto.borda_superior ) ):
                        self.base = objeto.topo + 1

                    
        #manter na tela
        if(self.manter_na_tela):
            if( self.topo < 0 ):
                self.topo = -1
            if( self.esquerda < 0 ):
                self.esquerda = -1
            if( self.base > tela.altura ):
                self.base = tela.altura + 1
            if( self.direita > tela.largura):
                self.direita = tela.largura +1


    #Função que move o objeto criado na tela    
    def mover(self):
        global rodar_threading, tela
        while rodar_threading and self._existe:
            if(self.velocidade <= 0):
                pygame.time.Clock().tick(10)
                continue
            #Velocidade é usada como clock para que o objeto se mova
            #em 1px a cada 1/velocidade segundos
            pygame.time.Clock().tick(self.velocidade)

            #não mover se o objeto estiver
            #estático
            if( self.estatico ):
                continue
            
            #pausa jogo
            if( pausado):
                continue
            
            #Movimento atraves das teclas
            if( tecla_apertada()[self.tecla_mover_para_esquerda] ):
                self.area_da_imagem.move_ip(-1, 0)
            if( tecla_apertada()[self.tecla_mover_para_direita] ):
                self.area_da_imagem.move_ip(1, 0)
            if( tecla_apertada()[self.tecla_mover_para_cima] ):
                self.area_da_imagem.move_ip(0, -1)
            if( tecla_apertada()[self.tecla_mover_para_baixo] ):
                self.area_da_imagem.move_ip(0, 1)

            #Movimentação com botões
            if( self.esta_pressionado( self.botao_mover_para_esquerda ) ):
                self.area_da_imagem.move_ip(-1, 0)
            if( self.esta_pressionado( self.botao_mover_para_direita ) ):
                self.area_da_imagem.move_ip(1, 0)
            if( self.esta_pressionado( self.botao_mover_para_cima ) ):
                self.area_da_imagem.move_ip(0, -1)
            if( self.esta_pressionado( self.botao_mover_para_baixo ) ):
                self.area_da_imagem.move_ip(0, 1)
                
            #movimento através da direção definida
            self.area_da_imagem.move_ip( self.direcao[0], \
                                         self.direcao[1])

            #realiza colisões
            self.realizar_colisoes()
    
    def _pousar(self):
        global lista_de_objetos
        if( self.pousou ):
            self._velocidade_de_queda = 0

    @property
    def pousou(self):
        global lista_de_objetos
        
        esta_sobre_um_objeto = False
        for objeto in lista_de_objetos:
            esta_sobre_um_objeto = esta_sobre_um_objeto or self.tocou_em_cima( objeto ) 
        
        pousou =  ( self.base >= tela.altura or esta_sobre_um_objeto )
        return pousou
                

    def _cair(self):
        clock_padrao = 100
        while rodar_threading:
            if( not self.cai or pausado ):
                pygame.time.Clock().tick( clock_padrao )
                continue
            elif( self._velocidade_de_queda > 0 ):
                pygame.time.Clock().tick( self._velocidade_de_queda )
                self.y += 1

            elif( self._velocidade_de_queda == 0):
                pygame.time.Clock().tick( clock_padrao )
                continue
            else:
                pygame.time.Clock().tick( -self._velocidade_de_queda )
                self.y -= 1

            self._pousar()
            self.realizar_colisoes()

    def pular(self, velocidade_de_pulo=100, delay=0.1 ):
        self._velocidade_de_queda -= velocidade_de_pulo
        esperar(delay)

    #muda tamanho da imagem
    @property
    def largura(self):
        return self.area_da_imagem.width

    @largura.setter
    def largura(self, largura):
        if(self.manter_proporcao ):
            altura = int( self.altura*largura/self.largura)
            self.imagem= pygame.transform.scale( self.imagem,
                                                 [largura, altura] )
            self.area_da_imagem.width = largura
            self.area_da_imagem.height = altura
        else:
            self.imagem= pygame.transform.scale( self.imagem,
                                                 [largura, self.altura] )
            self.area_da_imagem.width = largura

    @property
    def altura(self):
        return self.area_da_imagem.height

    @altura.setter
    def altura(self, altura):
        if( self.manter_proporcao ):
            largura = int( self.largura*altura/self.altura)
            self.imagem= pygame.transform.scale( self.imagem, [largura, altura] )
            self.area_da_imagem.width = largura
            self.area_da_imagem.height = altura
        else:
            self.imagem= pygame.transform.scale( self.imagem,
                                                 [self.largura, altura] )
            self.area_da_imagem.height = altura
                    
    #mostra posição do objeto
    @property
    def posicao(self):
        area = self.area_da_imagem
        return [ area.left, area.top ]

    #Mover objeto para uma posição escolhida na tela
    #posicao deve ser uma lista
    @posicao.setter
    def posicao(self, posicao):
        self.area_da_imagem.left = posicao[0]
        self.area_da_imagem.top = posicao[1]

    #coordenadas do objeto separadas
    @property
    def x( self ):
        return self.posicao[0]
    
    @x.setter
    def x(self, x):
        self.posicao = [x, self.y]

    @property
    def y( self ):
        return self.posicao[1]
    
    @y.setter
    def y(self, y):
        self.posicao = [self.x,y]

    #extremidades do objeto
    @property
    def topo( self ):
        return self.area_da_imagem.top
    
    @topo.setter
    def topo(self, topo):
        self.area_da_imagem.top = topo

    @property
    def base( self ):
        return self.area_da_imagem.bottom
    
    @base.setter
    def base(self, base):
        self.area_da_imagem.bottom = base

    @property
    def esquerda( self ):
        return self.area_da_imagem.left
    
    @esquerda.setter
    def esquerda(self, esquerda):
        self.area_da_imagem.left = esquerda

    @property
    def direita( self ):
        return self.area_da_imagem.right
    
    @direita.setter
    def direita(self, direita):
        self.area_da_imagem.right = direita 

    @property
    def centro_x( self ):
        return self.area_da_imagem.centerx
    
    @centro_x.setter
    def centro_x(self, centro_x):
        self.area_da_imagem.centerx = centro_x
    
    @property
    def centro_y( self ):
        return self.area_da_imagem.centery
    
    @centro_y.setter
    def centro_y(self, centro_y):
        self.area_da_imagem.centery = centro_y
        
    
    @property
    def centro( self ):
        return self.area_da_imagem.center
    
    @centro.setter
    def centro(self, centro):
        self.area_da_imagem.center = centro
        
    #detecta se dois objetos colidiram
    def colidiu_com(self, objeto):
        return self.area_da_imagem.colliderect( objeto.area_da_imagem )
    
    def tocou_em_cima( self, objeto ):
        return self.borda_inferior.colliderect( objeto.borda_superior )
    
    def tocou_embaixo( self, objeto ):
        return self.borda_superior.colliderect( objeto.borda_inferior )
    
    def tocou_na_direita( self, objeto ):
        return self.borda_esquerda.colliderect( objeto.borda_direita )
    
    def tocou_na_esquerda( self, objeto ):
        return self.borda_direita.colliderect( objeto.borda_esquerda )

    #retorna objetos que colidiram com esse
    @property
    def colisoes(self):
        colisoes = []
        for i in lista_de_objetos:
            if( i != self and\
                self.area_da_imagem.colliderect( i.area_da_imagem ) ):                
                colisoes.append( i )
        return colisoes
    
    #bordas para realizar colisões
    #borda não incluem área próxima ao vértice que seriam em comum
    @property
    def borda_superior(self):
        borda_superior = self.area_da_imagem.copy()
        borda_superior.height = self.largura_da_borda
        borda_superior.width -= 2
        borda_superior.left = self.esquerda + 1
        return borda_superior
    
    @property
    def borda_inferior(self):
        borda_inferior = self.area_da_imagem.copy()
        borda_inferior.height = self.largura_da_borda
        borda_inferior.width -= 2
        borda_inferior.left = self.esquerda + 1
        borda_inferior.bottom = self.base
        return borda_inferior
    
    @property
    def borda_esquerda(self):
        borda_esquerda = self.area_da_imagem.copy()
        borda_esquerda.width = self.largura_da_borda
        borda_esquerda.height -= 2
        borda_esquerda.top = self.topo + 1
        return borda_esquerda
    
    @property
    def borda_direita(self):
        borda_direita = self.area_da_imagem.copy()
        borda_direita.width = self.largura_da_borda
        borda_direita.height -= 2
        borda_direita.top = self.topo + 1
        borda_direita.right = self.direita
        return borda_direita
    
    #adiciona movimento na lista movimentos e executa
    #em paralelo
    def adicionar_movimento(self, movimento ):
        def movimento_em_loop(): #tentar futuramente incluir numa lista
            global tela
            while rodar_threading and self._existe:
                pygame.time.Clock().tick( self.velocidade )
                movimento( self )
        
        #pode ser útil para reutilizar acoes futuramente
        #Talvez seja necessário, para não alterar o que a
        #thread atual está fazendo, ao adicionar outra acao 

        t_movimento_em_loop =\
             threading.Thread( target= movimento_em_loop )
        
        self.movimentos_paralelos.append( t_movimento_em_loop )
        self.movimentos_paralelos[-1].start()


    #testa se botao foi apertado
    def esta_pressionado(self, botao ):
        try:
            return botao.pressionado
        except:
            pass

    #espelha imagem
    #por padrão, espelha horizontalmente
    def espelhar(self, forma='horizontalmente' ):
        if( forma == "verticalmente" ):
            self.imagem = \
                pygame.transform.flip( self.imagem, False, True)
        else:
            self.imagem = \
                pygame.transform.flip( self.imagem, True, False)

    #permite andar com o objeto
    def andar(self, x, y ):
        self.area_da_imagem.move_ip( x, y )

#Classe dos botões
class Botao():
    def __init__(self, x=0, y=0, largura=50, altura=50, cor=preto):
        self.rect = pygame.Rect( [x, y, largura, altura] )
        self.cor = cor
        self.visivel = True
        lista_de_botoes.append(self)

    #<bool>
    #Mostra se o botão está sendo pressionado.
    @property
    def pressionado(self):
        if( self.rect.collidepoint(pygame.mouse.get_pos()) and
            pygame.mouse.get_pressed()[0]):
            return True
        else:
            return False

#Faz texto
class Texto():
    def __init__(self, mensagem, cor=preto, x=0, y=0):
        self.mensagem = mensagem
        self.x = x
        self.y = y
        self.cor = cor
        self.tipo_de_fonte = None
        self.tamanho_da_fonte = 55
        self.visivel = True
        lista_de_textos.append(self)

    @property
    def posicao(self):
        return [self.x,self.y]
    @posicao.setter
    def posicao(self, posicao):
        self.x = posicao[0]
        self.y = posicao[1]
    
    @property
    def fonte(self):
        return pygame.font.Font(self.tipo_de_fonte,
                                self.tamanho_da_fonte)

    @property
    def texto(self):
        return self.fonte.render( str(self.mensagem), True, self.cor)

#Define o que será feito o iniciar a tela
class Tela():
    def __init__(self, largura, altura, cor, fps):
        self._largura = largura
        self._altura = altura
        self.cor = cor
        self.fps = fps
        self.atualizar = True

    @property
    def largura(self):
        return self._largura
        
    @property
    def altura(self):
        return self._altura

def atualizar_tela():
    global rodar_threading, tela
    while rodar_threading:
        pygame.time.Clock().tick( tela.fps )
        tela.atualizar = True

def verificar_eventos():
    global rodar_threading, tela
    tela._tela = pygame.display.set_mode( [tela.largura, tela.altura] ) 
    while rodar_threading:
        pygame.time.Clock().tick( 200 )

        if( tela.atualizar == True and not tela._tela.get_locked() ):
                    
            #preenche teala com cor de fundo
            tela._tela.fill(tela.cor )
            
            #exibe objetos
            for objeto in lista_de_objetos:
                if( objeto.visivel and not objeto.imagem.get_locked() ):
                    tela._tela.blit( objeto.imagem, objeto.area_da_imagem )

            #exibe textos        
            for texto in lista_de_textos:
                if( texto.visivel and not texto.texto.get_locked() ):
                    tela._tela.blit(texto.texto, texto.posicao)

            #exibe botões
            for botao in lista_de_botoes:
                if( botao.visivel ):
                    pygame.draw.rect( tela._tela, botao.cor, botao.rect )

            pygame.display.flip()

            tela.atualizar = False
            
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #faz threadings fecharem
                    rodar_threading = False
                    #espera threadings fecharem dos objetos
                    for objeto in lista_de_objetos:
                        objeto.threading_mover.join()
                        for movimento in objeto.movimentos_paralelos:
                            movimento.join()
                    #espera acoes pararem
                    for acao in acoes_paralelas:
                        acao.join()
                    #espera threading da tela
                    #t_atualizar_tela.join()
                    pygame.display.quit()
                    #fecha a tela
                    pygame.quit()
                    #sai do programa
                    sys.exit()

#Abre a tela em paralelo, usando threading
#Isso permite adicionar objetos depois
def abrir_tela(largura=800, altura=600, cor = roxo, fps= 60):
    global tela, t_atualizar_tela
    tela = Tela(largura, altura, cor, fps)
    t_atualizar_tela = threading.Thread( target= atualizar_tela )
    t_atualizar_tela.start()

    t_verificar_eventos = threading.Thread( target= verificar_eventos )
    t_verificar_eventos.start()
    return tela


#Permite programar açoes para os objetos

#Quando o while True é usado no programa principal, para definir
#as acoes de um objeto, sem usar uma threading,
#o programa demora para abrir
acoes_paralelas = []

#É iniciada na função abrir tela, para evitar erros

#Acao deve ser criada por uma funcao e após isso
#a acao é adicionada usando esta função
def adicionar_acao( acao, frequencia = 5000 ):
    global acoes_paralelas, tela
    def acao_em_loop(): #tentar futuramente incluir numa lista
        while rodar_threading:
            pygame.time.Clock().tick( frequencia )
            acao()
    
    #pode ser útil para reutilizar acoes futuramente
    #Talvez seja necessário, para não alterar o que a
    #thread atual está fazendo, ao adicionar outra acao

    t_acao_em_loop = threading.Thread( target= acao_em_loop )
    acoes_paralelas.append( t_acao_em_loop ) 
    acoes_paralelas[-1].start()
    

#pausar e despauzar jogo
def despausar():
    global pausado
    pausado = False
    
def pausar(tempo=False):
    global pausado
    pausado = True

    #texta se tempo é float ou int
    if( isinstance( tempo, (int, float) ) ):
        time.sleep(tempo)
        despausar()
        
#usado quando uma ação precisa de um intervalo entre uma
#execução e outra
#o usuário deve escolher entre usar a função de período ou
#frequência
esperar = time.sleep
definir_frequencia = pygame.time.Clock().tick
def definir_periodo( periodo ): 
    pygame.time.Clock().tick( 1/periodo )


#roda ação em paralelo
def rodar_em_paralelo( funcao, argumentos = [] ):
    if( argumentos == [] ):
        threading.Thread( target= funcao ).start()
    else:
        threading.Thread( target= funcao, args = argumentos ).start()

#verifica estado do jogo
def obter_estado_do_jogo():
    if( rodar_threading == True ):
        return "rodando"
    else:
        return "fechado"
