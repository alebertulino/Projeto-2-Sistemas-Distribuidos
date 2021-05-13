import socket
import sys
import threading
import os

''' Função para fazer a contagem da lista de frequencia do processo'''
def contador(freq, cont_pid):

    if cont_pid in freq:
        freq[cont_pid] += 1
    else:
        freq[cont_pid] = 1

'''Função para fazer a conexão do processo'''
def conexao_de_socket(sock, processos, opcao, n_processos):

    print("\nAguardando conexao")
    sock.listen(n_processos)   

    while opcao != '3':
        s, endereco = sock.accept()
        print(f'\nConexãocom {endereco} foi estabelecida!')

        
        processos.add(s)
    sock.close()

'''Função para verificar o pid e retornar em uma mensagem'''
def verificar_pid(mensagem):
    inicio_cont = mensagem.find('1|') + len('1|')
    fim_cont = mensagem.find('|0')
    pid = mensagem[inicio_cont:fim_cont]

    return pid

'''Função da regiao critica para fazer a exclusao mutua'''
def exclusao_mutua(processos, exclusao, pid, freq, n_processos):

    '''Esperando os sockets fazerema conexão'''
    while len(processos) != n_processos:
        continue

    while True:
        s = processos.pop()
        processos.add(s)

        '''Faz o processo que não deixa thread esperando, ja que ela esta na fila da rc'''
        if s in exclusao and s != exclusao[0]:
            continue

        mensagem = s.recv(10).decode()

        if '1|' in mensagem[:2]:      
            cont_pid = verificar_pid(mensagem)

            '''Manda mensagem via GRANT se não tiver nenhuma thread na fila'''
            if not exclusao:
                sender = str('2|'+ str(os.getpid()) + ' |').ljust(10,'0')
                s.send(sender.encode('utf-8'))

                contador(freq, cont_pid)

            pid.append(cont_pid)
            exclusao.append(s)

        if '3|' in mensagem[:2]:        
            s = exclusao.pop(0)
            pid.pop(0)

        
            if exclusao:
                s = exclusao[0]
                sender = str('2|'+ str(os.getpid()) + ' |').ljust(10,'0')
                s.send(sender.encode('utf-8'))

                cont_pid = pid[0]
                contador(freq, cont_pid)

'''Função para criar o menu e fazer a interface'''
def comunicacao(pid, freq, menu):
    while True:
        '''Printa o menu, e pede para escolher o processo, enquanto não escolher a opcao 3, ele fica nesse menu'''
        print("\nI - Mostre fila de pedidos II - Mostre lista de frequencia III - Encerrar a conexao")
        menu = input('\nQual opção do menu: ')

        if menu == '1':
            print("\nEsta é a Fila de pedidos")
            print(pid)
        elif menu == '2':
            print("\nEsta é a Lista de frequências")
            print(freq)
        elif menu == '3':
            print("\n Encerrando a execução ")
            break
        else:
            print("Essa opcao não esta no menu!")

'''Main para criar e executar as threads do coordenador'''
if __name__ == '__main__':

    '''Conexão HOST E PORT'''
    HOST = 'localhost'
    PORT = 10000
    '''Criando o socket do Coordenador'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print("\nO socket do Coordenador foi criado!")

    '''Cria todas as funções para as threads'''
    processos = set()
    exclusao = []
    pid = []
    freq = {}
    menu = ''

    '''Vai fazer todo o processo das threads'''
    n = 2

    
    thread1 = threading.Thread(target=conexao_de_socket, args=(s, processos, menu, n))
    thread2 = threading.Thread(target=exclusao_mutua, args=(processos, exclusao, pid, freq, n))
    thread3 = threading.Thread(target=comunicacao, args=(pid, freq, menu))

    
    thread1.daemon=True
    thread2.daemon=True
    thread3.daemon=True

    
    thread1.start()
    thread2.start()

    while len(processos) != n:
        continue

    thread3.start()

    thread3.join()

    print('Conexão foi encerrada')
    sys.exit()