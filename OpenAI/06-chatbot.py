import openai
from colorama import Fore, Style, init

client = openai.Client()

# Inicializando o colorama

init(autoreset=True)

## 2) a função abaixo chama o chat gpt para obter a resposta
def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        temperature=0,
        max_tokens=1000,
        stream=True
    )
    print(f"{Fore.CYAN}Bot:", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            ## 3) Após obter a resposta, é exibido a ultima mensagem retornada pelo chat gpt
            ## que utiliza esse laço for para exibir a mensagem quebrada/formatada por linha
            print(texto, end="")
            texto_completo += texto
    print()
    ## 4) ao termino da exibição toda a mensagem é salva e agregada na variavel mensagens
    ## e retorna para o laço while la embaixo
    ## Quando é feita uma nova pergunta no laço while la embaixo, é enviado todo o historico
    ##para o modelo LLM através da variavel mensagens. LLM intepreta todo o historico e retorna
    ##também a resposta com a ultima pergunta. Através do [0] que selecionamos qual resposta
    ## que vamos retorna. Brinque depois com essa variavel[0] mudando para [1] e coloque também
    ## um print seco da variavel mensagem para entender melhor o funcionalmento.
    mensagens.append({"role":"assistant", "content": texto_completo})
    return mensagens

## 1) Essa é a função incial inicializados.
## Ao digitarmos a pergunta, a mesma é adicionada a variavel mensagens, e
## chamada a funcção geracao texto.

if __name__ == "__main__":
    print(f"{Fore.BLUE}Bem Vindo ao Chatbot🤖")
    mensagens = []
    while True:
        in_user = input(f"{Fore.Green}User: {Style.RESET_ALL} ")
        mensagens.append({"role": "user", "content": in_user})
        mensagens = geracao_texto(mensagens)
