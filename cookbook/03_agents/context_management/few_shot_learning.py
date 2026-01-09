"""
Este exemplo demonstra como usar additional_input com um Agent
para ensinar padrões de resposta adequados através de aprendizado few-shot.
"""

from agno.agent import Agent
from agno.models.message import Message
from agno.models.openai.chat import OpenAIChat

# Exemplos few-shot mostrando bons padrões de suporte
support_examples = [
    # Exemplo 1: Resolução de problema simples
    Message(role="user", content="Esqueci minha senha e não consigo fazer login"),
    Message(
        role="assistant",
        content="""
    Vou ajudá-lo a redefinir sua senha imediatamente.

    **Passos para Redefinir Sua Senha:**
    . Ir para a página de login e clicar em "Esqueci a Senha"
    . Digitar seu endereço de email
    . Verificar seu email para o link de redefinição
    . Seguir o link para criar uma nova senha
    . Usar uma senha forte com maiúsculas, minúsculas, números e símbolos

    Se você não receber o email em 5 minutos, por favor verifique sua pasta de spam. Avise-me se precisar de ajuda com estes passos!
    """.strip(),
    ),
    # Exemplo 2: Padrão de problema de cobrança
    Message(
        role="user",
        content="Fui cobrado duas vezes pelo mesmo pedido e estou frustrado!",
    ),
    Message(
        role="assistant",
        content="""
    Peço sinceras desculpas pelo erro de cobrança e pela frustração que isso causou.

    **Plano de Ação Imediato:**
    1. Vou investigar sua conta para confirmar a cobrança duplicada
    2. Processar um reembolso completo para a transação duplicada
    3. Garantir que isso não aconteça novamente verificando as configurações do seu método de pagamento
    4. Fornecer um número de confirmação assim que o reembolso for processado

    O reembolso normalmente leva 3-5 dias úteis para aparecer em sua fatura. Como desculpa por este inconveniente, também gostaria de oferecer um desconto de 10% em seu próximo pedido.

    Há mais alguma coisa com que eu possa ajudá-lo em relação a este problema?
    """.strip(),
    ),
    # Exemplo 3: Padrão de suporte técnico
    Message(role="user", content="Seu aplicativo continua travando quando tento enviar fotos"),
    Message(
        role="assistant",
        content="""
    Sinto muito que você esteja enfrentando travamentos com o envio de fotos. Deixe-me ajudá-lo a solucionar este problema.

    **Passos de Solução de Problemas:**
    1. **Verificar Versão do App:** Certifique-se de ter a versão mais recente da loja de aplicativos
    2. **Reiniciar o App:** Fechar completamente e reabrir o aplicativo
    3. **Verificar Armazenamento:** Certifique-se de ter armazenamento suficiente no dispositivo (pelo menos 1GB livre)
    4. **Tamanho da Foto:** Tentar enviar fotos menores (menos de 10MB cada)
    5. **Conexão de Rede:** Certificar-se de ter uma conexão de internet estável

    **Se o problema persistir:**
    - Tentar enviar uma foto por vez em vez de múltiplas
    - Limpar o cache do app nas configurações do dispositivo
    - Reiniciar seu dispositivo

    Se nenhum destes passos resolver o problema, por favor me informe o tipo de dispositivo e versão do SO, e vou escalar isso para nossa equipe técnica para investigação adicional.
    """.strip(),
    ),
]

if __name__ == "__main__":
    # Criar agente com aprendizado few-shot
    agent = Agent(
        name="Customer Support Specialist",
        model=OpenAIChat(id="gpt-4o-mini"),
        add_name_to_context=True,
        additional_input=support_examples,  # exemplos de aprendizado few-shot
        instructions=[
            "Você é um especialista em suporte ao cliente.",
            "Sempre ser empático, profissional e orientado a soluções.",
            "Fornecer passos claros e acionáveis para resolver problemas do cliente.",
            "Seguir os padrões estabelecidos para suporte consistente e de alta qualidade.",
        ],
        markdown=True,
    )

    agent.print_response("Quero habilitar autenticação de dois fatores para minha conta.")
