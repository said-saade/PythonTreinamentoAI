import openai
from dotenv import load_dotenv
from colorama import Fore, Style, init

load_dotenv()

client = openai.Client()

# Inicializando o colorama

init(autoreset=True)

## 2) a função abaixo chama o chat gpt para obter a resposta
def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-4.1-mini",
        temperature=1,
        max_tokens=1000,
        stream=True
    )
    print(f"{Fore.CYAN}Bot:", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            ## 3) A resposta da API vem em stream. O for resposta_stream in resposta: itera sobre cada pedaço (chunk) 
            # dessa nova resposta, e a linha print(texto, end="") exibe cada pedaço em tempo real na tela. 
            # O end="" faz com que cada pedacinho seja impresso na mesma linha, sem pular para a próxima, 
            # criando o efeito de digitação.
            #A construção do texto_completo: Enquanto cada pedacinho da resposta é exibido (print(texto)), 
            # a linha texto_completo += texto vai concatenando esses pedaços que servira para enviar todo o historico
            # ao chat gpt. 
            print(texto, end="")
            texto_completo += texto
    print()
    ## 4) ao termino da exibição toda a mensagem é salva e agregada na variavel mensagens
    ## e retorna para o laço while la embaixo
    ## Quando é feita uma nova pergunta no laço while la embaixo, é enviado todo o historico
    ##para o modelo LLM através da variavel mensagens.A lógica de passar e atualizar a variável mensagens 
    # a cada iteração é a maneira correta de manter o histórico da conversa. 
    # Isso permite que o modelo de IA entenda o contexto das perguntas anteriores. 
    # LLM intepreta todo o historico e retorna também a resposta com a ultima pergunta. 

    mensagens.append({"role":"assistant", "content": texto_completo})
    return mensagens

## 1) Essa é a função incial inicializada.
## Ao digitarmos a pergunta, a mesma é adicionada a variavel mensagens, e
## chamada a função geracao texto.

if __name__ == "__main__":
    print(f"{Fore.BLUE}Bem Vindo ao Chatbot🤖")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN}User: {Style.RESET_ALL} ")
        mensagens.append({"role": "user", "content": in_user})
        mensagens = geracao_texto(mensagens)
        print (mensagens)
