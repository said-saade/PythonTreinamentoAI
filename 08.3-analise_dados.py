##
"""Já nos Assistants trabalhando com threads, o que garante o armazenado do histórico 
dentro da OPENAi ou o modelo que esta sendo utilizado. 
Voce não precisa submeter o histórico da conversa a todo momento."""
import openai
import time
import pandas as pd
from transformers import pipeline
import gradio as gd
from dotenv import load_dotenv
load_dotenv()

client = openai.Client()

file = client.files.create(
    file=open("data_upload.txt", "rb"),
    purpose="assistants"
)


assistant = client.beta.assistants.create(
    name="Analista de Dados",
    instructions="Você é um analista que analisa dados sobre vendas.",
    tools=[{"type":"code_interpreter"}],
    tool_resources={"code_interpreter":{"file_ids":[file.id]}},
    model="gpt-4o-mini"
)


#pergunta = "Qual o rating médio das vendas do supermercado"
#pergunta = "Gere um grafico de vendas por linha de produtos"
pergunta = """Act as an expert in advanced English conversation design. Your task is to generate a list of exactly 15 distinct and complex factual 
    questions intended for advanced English speakers.

**Constraints:**
1.  **Quantity:** Generate precisely 15 questions.
2.  **Difficulty:** Questions must be suitable for advanced conversational practice (C1/C2 level) requiring daily basis talks.
3.  **Thematic Exclusion:** Strictly avoid the following common themes: Artificial Intelligence (AI) Health Wellness Personal Lifestyle and general well-being.
4.  **Thematic Focus:** Focus exclusively on day by day subjects Examples include: 
"Como Novak Dkokovic derrotou Roger Federer em Winblendon?", "Por que o povo Americano votou em Donald Trump?"
5.  **Uniqueness:** Ensure that each of the 15 questions addresses a completely unique subtopic and theme to prevent repetition.
6.  **Contextual Exclusion:** Absolutely do NOT use any information themes or content derived from the document currently being processed or read by the program.
7.  **Formatting:** The final output must be a single block of text where each question is separated only by a line break and **contains no commas** within the question text itself.

**Output Format:** 15 questions in a list format with no commas but include que question marks at the end of the questions. The
   Questions must be in English. Don't enumerate the questions."
"""


# Criação da Thread
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=pergunta)

#Executa a thread
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Nome de usuário premium"
)

# Aguarda a thread rodar
while run.status in ["queued", "in_progress", "cancelling"]:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
        
    )
    print(run.status)

    # Verifica a resposta quando tivermos a resposta da thread
if run.status == "completed":
    mensagens = client.beta.threads.messages.list(
        thread_id=thread.id
    )    
    print(mensagens.data[0].content[0].text.value)
else:
    print(f"Erro {run.status}")


    # Extrai o texto da resposta/texto
texto_resposta = mensagens.data[0].content[0].text.value

# Extrai perguntas (linhas que começam com "-")
perguntas = [linha.strip("-").strip() for linha in texto_resposta.splitlines() if linha.strip().startswith("")]
# Grava perguntas novas no final do arquivo
if perguntas:
    with open("data_upload.txt", "a", encoding="utf-8") as f:
        for pergunta in perguntas:
            print(pergunta)
            f.write(pergunta + "\n")


#analisando a logica/passos do modelo para chegar na resposta
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)

for step in run_steps.data[::-1]:
    print(f"\n===Step {step.step_details.type}")
    if step.step_details.type == "tool_calls":
        for tool_call in step.step_details.tool_calls:
            print("-" * 10)
            print(tool_call.code_interpreter.input)
            print("-" * 10)
    if step.step_details.type == "message_creation":
        message = client.beta.threads.messages.retrieve(
        thread_id=thread.id,
        message_id=step.step_details.message_creation.message_id
    )

# print(message.content[0].text.value)
# comentado acim apara quando a geração do output é grafico e não texto(conforme a pergunta)


#condicional adaptado para quando a pergunta solicita texto ou grafico
#Função: Verifica se a resposta é texto ou imagem. Se for imagem, salva localmente.
if message.content[0].type == "text":
    print(message.content[0].text.value)
if message.content[0].type == "image_file":
    file_id = message.content[0].image_file.file_id
    image_data = client.files.content(file_id)
    with open(f"files/{file.id}.png", "wb") as f:
        f.write(image_data.read())
    print(f"Imagem {file_id} salva")


df_questions = pd.read_csv("data_upload.txt")
#df_questions

def question_answer(question):
    context=df_questions.tail(15)[df_questions["question"]==question]
     #para retornar o 1° indice da resposta que esta dentro do arquivo
    return context["question"].values[0]
    #para retornar a resposta com base no modelo e nao em um arquivo estatico(caracteristicas de chat bot)
    result=model_qa(question=question, context=context("question").values[0])
    return result["question"]


def question_answer_static(question):
        
    # 1. Filtra o DataFrame para encontrar a linha correspondente à pergunta
    context = df_questions[df_questions["question"] == question]
    # Usando 'answer' como exemplo:
    resposta = context["question"].values[0] 
    return resposta


app = gd.Interface(
    fn=question_answer_static,
#   inputs=gd.DataFrame(choices=list(df_questions.tail(15)["question"]), label="Selecione a Pergunta"),
    inputs=gd.Dataframe(
        value=df_questions.tail(15)[["question"]], 
        headers=["Perguntas"], 
        label="Selecione a Pergunta",
        interactive=True),
    outputs=None,
    title="Choose the Question",
    description=None
)

app.launch(share=True)