"""A4 da Tato — Maria Eduarda Barbosa Oliveira, D1=5, D2=7, N=5.

Motor comum das três versões. As falhas das versões 1 e 3 são intencionais.
Execute pelos arquivos versao1.py, versao2.py ou versao3.py, em processos
independentes: threads bloqueadas da versão 3 terminam com o processo.
"""

import json
import threading
import time

N = 5
TOTAL = 20_000
LIMITE_SEM_CONSUMO = 1.0
ATRASO_INICIAL_CONSUMIDOR = 0.05


def executar(versao: int) -> dict:
    """Executa uma versão e retorna contagens e diagnóstico em um dicionário.

    Parâmetro versao: 1 (corrida), 2 (semáforos) ou 3 (ordem incorreta).
    O monitor observa 1 s sem consumo e solicita parada; não libera recursos
    das threads. A espera inicial do consumidor é igual nas três versões e
    permite observar o caso válido de o produtor preencher o buffer primeiro.
    """
    if versao not in (1, 2, 3):
        raise ValueError("A versão deve ser 1, 2 ou 3")

    buffer = [None] * N
    ocupadas = 0
    escrita = 0
    leitura = 0
    produzidas = 0
    recebidas = []
    vazio = threading.Semaphore(N)
    cheio = threading.Semaphore(0)
    mutex = threading.Semaphore(1)
    parar = threading.Event()
    concluiu = threading.Event()
    produtor_concluiu = threading.Event()
    inicio = time.monotonic()
    ultimo_consumo = inicio
    estado = {"produtor": "iniciando", "consumidor": "iniciando"}

    def produtor() -> None:
        """Sem parâmetros/retorno; publica IDs 0..19999 no buffer compartilhado.

        V1 separa leitura e escrita do contador por yield. V2 adquire vazio
        antes de mutex. V3 inverte somente essas duas aquisições.
        """
        nonlocal ocupadas, escrita, produzidas
        for amostra in range(TOTAL):
            if parar.is_set():
                break
            if versao == 1:
                estado["produtor"] = "espera ocupada por espaço"
                while ocupadas >= N and not parar.is_set():
                    time.sleep(0)
                if parar.is_set():
                    break
                buffer[escrita] = amostra
                escrita = (escrita + 1) % N
                anterior = ocupadas
                time.sleep(0)  # Interrupção entre ler e escrever o contador.
                ocupadas = anterior + 1
            else:
                if versao == 3:
                    estado["produtor"] = "aguarda mutex"
                    mutex.acquire()
                    estado["produtor"] = "aguarda vazio segurando mutex"
                    vazio.acquire()
                else:
                    estado["produtor"] = "aguarda vazio"
                    vazio.acquire()
                    estado["produtor"] = "aguarda mutex"
                    mutex.acquire()
                buffer[escrita] = amostra
                escrita = (escrita + 1) % N
                mutex.release()
                cheio.release()
            produzidas += 1
        estado["produtor"] = "finalizado"
        produtor_concluiu.set()

    def consumidor() -> None:
        """Sem parâmetros/retorno; registra leituras para auditoria dos IDs.

        Somente esta thread escreve recebidas e ultimo_consumo. Semáforos
        bloqueiam em V2/V3; V1 consulta o contador em espera ocupada com yield.
        Na V1, termina após ao menos TOTAL leituras e conclusão do produtor;
        assim, duplicatas não encerram a produção antes das 20.000 amostras.
        Na V2/V3, encerra depois de TOTAL leituras.
        """
        nonlocal ocupadas, leitura, ultimo_consumo
        time.sleep(ATRASO_INICIAL_CONSUMIDOR)
        while not parar.is_set():
            if len(recebidas) >= TOTAL and (versao != 1 or produtor_concluiu.is_set()):
                break
            if versao == 1:
                estado["consumidor"] = "espera ocupada por amostra"
                if ocupadas <= 0:
                    time.sleep(0)
                    continue
                amostra = buffer[leitura]
                leitura = (leitura + 1) % N
                anterior = ocupadas
                time.sleep(0)  # Mesma janela de corrida do produtor.
                ocupadas = anterior - 1
            else:
                estado["consumidor"] = "aguarda cheio"
                cheio.acquire()
                estado["consumidor"] = "aguarda mutex após cheio"
                mutex.acquire()
                amostra = buffer[leitura]
                leitura = (leitura + 1) % N
                mutex.release()
                vazio.release()
            recebidas.append(amostra)
            ultimo_consumo = time.monotonic()
        estado["consumidor"] = "finalizado"
        concluiu.set()

    threads = [threading.Thread(target=produtor, daemon=True),
               threading.Thread(target=consumidor, daemon=True)]
    for thread in threads:
        thread.start()
    travou = False
    while not concluiu.wait(0.005):
        if (time.monotonic() - ultimo_consumo >= LIMITE_SEM_CONSUMO
                and not concluiu.is_set()):
            travou = True
            break
    estados_no_encerramento = dict(estado)
    duracao = time.monotonic() - inicio
    parar.set()
    for thread in threads:
        thread.join(timeout=0.1)

    validas = [x for x in recebidas if isinstance(x, int) and 0 <= x < TOTAL]
    unicas = set(validas)
    return {
        "versao": versao, "n": N, "solicitadas": TOTAL,
        "produzidas": produzidas, "consumidas": len(recebidas),
        "unicas": len(unicas), "perdidas": TOTAL - len(unicas),
        "nao_produzidas": TOTAL - produzidas,
        "produzidas_nao_recebidas": produzidas - len(unicas),
        "duplicadas": len(validas) - len(unicas),
        "invalidas": len(recebidas) - len(validas),
        "sequencia_correta": recebidas == list(range(TOTAL)),
        "travou": travou, "duracao_s": round(duracao, 6),
        "estados": estados_no_encerramento,
        "threads_bloqueadas_ao_sair": sum(t.is_alive() for t in threads),
    }


def principal(versao: int) -> None:
    """Recebe a versão, executa e imprime JSON auditável; retorna None."""
    print(json.dumps(executar(versao), ensure_ascii=False, indent=2))
