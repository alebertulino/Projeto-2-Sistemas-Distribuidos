'''Importando as bibliotecas'''
import socket
import sys
from datetime import datetime
import multiprocessing
import os
import time

'''Função para abrir o arquivo txt para guardar os processos e o tempo exato do processo'''
def abrir_txt(segundos):
    with open('arquivo.txt', 'a') as arquivo:
        horario = datetime.now()
        results = (str(os.getpid())+': '+datetime.strftime(horario, '%h:%m:%s.%f')+'\n')

        arquivo.write(results)
        time.sleep(segundos)
        arquivo.close()

'''Função para executar o processo, faz todo o processo de conexao de host e port e de enviar e receber mensagens''' 
def executar_processo(repeticoes, tempo):
    '''Conexão HOST E PORT'''
    HOST = 'localhost'
    PORT = 10000
    '''Conexão do socket com o HOST e PORT'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    print(f'\nConexão foi estabelecida!')

    '''Regiao que enviara e recebera mensagem atraves dos metodos GRANT, REQUEST E RELEASE'''
    while repeticoes > 0:
        sender = str('1|' + str(os.getpid()) + '|').ljust(10,'0')
        s.send(sender.encode('utf-8'))

        mensagem = s.recv(10).decode()
        if '2|' in mensagem[:2]:
            abrir_txt(tempo)

        sender = str('3|' + str(os.getpid()) + '|').ljust(10,'0')
        s.send(mensagem.encode('utf-8'))

        repeticoes -= 1
    print(f'\nProcesso finalizado.')
    s.close()

''' Main para enviar os processo e as trheads para o coordenador'''
if __name__ == '__main__':
    
    '''Enviar os numeros para fazer os processos de repetições, tempo de espera e num de processos'''
    N = 2       
    r = 10      
    k = 1       
    lista = []

    for i in range(N):
        processo = multiprocessing.Process(target=executar_processo, args=(r, k))
        processo.start()
        lista.append(processo)

    for processo in lista:
        processo.join()

    for processo in lista:
        processo.terminate()

    print("\nEncerrando os processos")
    sys.exit()
