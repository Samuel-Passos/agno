import asyncio
import io
import random
from datetime import datetime, timedelta
from typing import Any, List

import requests
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.workflow.types import WorkflowExecutionInput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel
from pypdf import PdfReader


# --- Modelos de Resposta ---
class ScreeningResult(BaseModel):
    name: str
    email: str
    score: float
    feedback: str


class ScheduledCall(BaseModel):
    name: str
    email: str
    call_time: str
    url: str


class EmailContent(BaseModel):
    subject: str
    body: str


# --- Utilitário PDF ---
def extract_text_from_pdf(url: str) -> str:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"Erro ao extrair PDF de {url}: {e}")
        return ""


# --- Ferramentas de Simulação ---
def simulate_zoom_scheduling(
    agent: Agent, candidate_name: str, candidate_email: str
) -> str:
    """Simular agendamento de chamada Zoom"""
    # Gerar um horário futuro (1-7 dias a partir de agora, entre 10h-18h IST)
    base_time = datetime.now() + timedelta(days=random.randint(1, 7))
    hour = random.randint(10, 17)  # 10h às 17h
    scheduled_time = base_time.replace(hour=hour, minute=0, second=0, microsecond=0)

    # Gerar URL Zoom falsa
    meeting_id = random.randint(100000000, 999999999)
    zoom_url = f"https://zoom.us/j/{meeting_id}"

    result = "✅ Chamada Zoom agendada com sucesso!\n"
    result += f"📅 Horário: {scheduled_time.strftime('%Y-%m-%d %H:%M')} IST\n"
    result += f"🔗 URL da Reunião: {zoom_url}\n"
    result += f"👤 Participante: {candidate_name} ({candidate_email})"

    return result


def simulate_email_sending(agent: Agent, to_email: str, subject: str, body: str) -> str:
    """Simular envio de e-mail"""
    result = "📧 E-mail enviado com sucesso!\n"
    result += f"📮 Para: {to_email}\n"
    result += f"📝 Assunto: {subject}\n"
    result += f"✉️ Comprimento do corpo: {len(body)} caracteres\n"
    result += f"🕐 Enviado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return result


# --- Agentes ---
screening_agent = Agent(
    name="Screening Agent",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Triar candidato dado texto do currículo e descrição do trabalho.",
        "Fornecer uma pontuação de 0-10 com base em quão bem eles correspondem aos requisitos do trabalho.",
        "Dar feedback específico sobre pontos fortes e áreas de preocupação.",
        "Extrair o nome e e-mail do candidato do currículo se disponível.",
    ],
    output_schema=ScreeningResult,
)

scheduler_agent = Agent(
    name="Scheduler Agent",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        f"Você está agendando chamadas de entrevista. Hora atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST",
        "Agendar chamadas entre 10h-18h IST em dias úteis.",
        "Usar a ferramenta simulate_zoom_scheduling para criar a reunião.",
        "Fornecer datas e horários futuros realistas.",
    ],
    tools=[simulate_zoom_scheduling],
    output_schema=ScheduledCall,
)

email_writer_agent = Agent(
    name="Email Writer Agent",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Escrever e-mails de convite para entrevista profissionais e amigáveis.",
        "Incluir parabéns, detalhes da entrevista e próximos passos.",
        "Manter e-mails concisos mas calorosos e acolhedores.",
        "Assinar e-mails como 'John Doe, Senior Software Engineer' com e-mail john@agno.com",
    ],
    output_schema=EmailContent,
)

email_sender_agent = Agent(
    name="Email Sender Agent",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Você envia e-mails usando a ferramenta simulate_email_sending.",
        "Sempre confirmar entrega bem-sucedida com detalhes.",
    ],
    tools=[simulate_email_sending],
)


# --- Função de Execução ---
async def recruitment_execution(
    session_state,
    execution_input: WorkflowExecutionInput,
    job_description: str,
    **kwargs: Any,
):
    """Executar o workflow completo de recrutamento"""

    # Obter entradas
    message: str = execution_input.input
    jd: str = job_description
    resumes: List[str] = kwargs.get("candidate_resume_urls", [])

    if not resumes:
        yield "❌ Nenhuma URL de currículo de candidato fornecida"

    if not jd:
        yield "❌ Nenhuma descrição do trabalho fornecida"

    print(f"🚀 Iniciando processo de recrutamento para {len(resumes)} candidatos")
    print(f"📋 Descrição do Trabalho: {jd[:100]}{'...' if len(jd) > 100 else ''}")

    selected_candidates: List[ScreeningResult] = []

    # Fase 1: Triagem
    print("\n📊 FASE 1: TRIAGEM DE CANDIDATOS")
    print("=" * 50)

    for i, url in enumerate(resumes, 1):
        print(f"\n🔍 Processando candidato {i}/{len(resumes)}")

        # Extrair texto do currículo (com cache)
        if url not in session_state:
            print(f"📄 Extraindo texto de: {url}")
            session_state[url] = extract_text_from_pdf(url)
        else:
            print("📋 Usando conteúdo de currículo em cache")

        resume_text = session_state[url]

        if not resume_text:
            print("❌ Não foi possível extrair texto do currículo")
            continue

        # Triar o candidato
        screening_prompt = f"""
        {message}
        Por favor, trie este candidato para a posição de trabalho.

        CURRÍCULO:
        {resume_text}

        DESCRIÇÃO DO TRABALHO:
        {jd}

        Avaliar quão bem este candidato corresponde aos requisitos do trabalho e fornecer uma pontuação de 0-10.
        """

        async for response in screening_agent.arun(
            screening_prompt, stream=True, stream_events=True
        ):
            if hasattr(response, "content") and response.content:
                candidate = response.content

        print(f"👤 Candidato: {candidate.name}")
        print(f"📧 E-mail: {candidate.email}")
        print(f"⭐ Pontuação: {candidate.score}/10")
        print(
            f"💭 Feedback: {candidate.feedback[:150]}{'...' if len(candidate.feedback) > 150 else ''}"
        )

        if candidate.score >= 5.0:
            selected_candidates.append(candidate)
            print("✅ SELECIONADO para entrevista!")
        else:
            print("❌ Não selecionado (pontuação abaixo de 5.0)")

    # Fase 2: Agendamento de Entrevista e Comunicação por E-mail
    if selected_candidates:
        print("\n📅 FASE 2: AGENDAMENTO DE ENTREVISTA")
        print("=" * 50)

        for i, candidate in enumerate(selected_candidates, 1):
            print(
                f"\n🗓️ Agendando entrevista {i}/{len(selected_candidates)} para {candidate.name}"
            )

            # Agendar entrevista
            schedule_prompt = f"""
            Agendar uma chamada de entrevista de 1 hora para:
            - Candidato: {candidate.name}
            - E-mail: {candidate.email}
            - Entrevistador: Dirk Brand (dirk@phidata.com)
            Usar a ferramenta simulate_zoom_scheduling para criar a reunião.
            """

            async for response in scheduler_agent.arun(
                schedule_prompt, stream=True, stream_events=True
            ):
                if hasattr(response, "content") and response.content:
                    scheduled_call = response.content

            print(f"📅 Agendado para: {scheduled_call.call_time}")
            print(f"🔗 URL da Reunião: {scheduled_call.url}")

            # Escrever e-mail de parabéns
            email_prompt = f"""
            Escrever um e-mail profissional de convite para entrevista para:
            - Candidato: {candidate.name} ({candidate.email})
            - Horário da entrevista: {scheduled_call.call_time}
            - URL da Reunião: {scheduled_call.url}
            - Parabenizá-los por serem selecionados
            - Incluir próximos passos e o que esperar
            """

            async for response in email_writer_agent.arun(
                email_prompt, stream=True, stream_events=True
            ):
                if hasattr(response, "content") and response.content:
                    email_content = response.content

            print(f"✏️ Assunto do e-mail: {email_content.subject}")

            # Enviar e-mail
            send_prompt = f"""
            Enviar o e-mail de convite para entrevista:
            - Para: {candidate.email}
            - Assunto: {email_content.subject}
            - Corpo: {email_content.body}
            Usar a ferramenta simulate_email_sending.
            """

            async for response in email_sender_agent.arun(
                send_prompt, stream=True, stream_events=True
            ):
                yield response


# --- Definição do Workflow ---
recruitment_workflow = Workflow(
    name="Employee Recruitment Workflow (Simulated)",
    description="Triagem automatizada de candidatos com agendamento e e-mail simulados",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/workflows.db",
    ),
    steps=recruitment_execution,
    session_state={},
)


if __name__ == "__main__":
    # Testar com dados de exemplo
    print("🧪 Testando Workflow de Recrutamento de Funcionários com Ferramentas Simuladas")
    print("=" * 60)

    asyncio.run(
        recruitment_workflow.aprint_response(
            input="Process candidates for backend engineer position",
            candidate_resume_urls=[
                "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/filters/cv_1.pdf",
                "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/filters/cv_2.pdf",
            ],
            job_description="""
        We are hiring for backend and systems engineers!
        Join our team building the future of agentic software

        Requirements:
        🧠 You know your way around Python, typescript, docker, and AWS.
        ⚙️ Love to build in public and contribute to open source.
        🚀 Are ok dealing with the pressure of an early-stage startup.
        🏆 Want to be a part of the biggest technological shift since the internet.
        🌟 Bonus: experience with infrastructure as code.
        🌟 Bonus: starred Agno repo.
        """,
            stream=True,
        )
    )
