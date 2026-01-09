"""Exemplo mostrando como usar um logger personalizado com Agno."""

import logging

from agno.agent import Agent
from agno.utils.log import configure_agno_logging, log_info


def get_custom_logger():
    """Retornar um exemplo de logger personalizado."""
    custom_logger = logging.getLogger("custom_logger")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[CUSTOM_LOGGER] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    custom_logger.addHandler(handler)
    custom_logger.setLevel(logging.INFO)  # Definir nível para INFO para mostrar mensagens de info
    custom_logger.propagate = False
    return custom_logger


# Obter o logger personalizado que usaremos para o exemplo.
custom_logger = get_custom_logger()

# Configurar Agno para usar nosso logger personalizado. Ele será usado para todo o logging.
configure_agno_logging(custom_default_logger=custom_logger)

# Cada uso da função de logging em agno.utils.log agora usará nosso logger personalizado.
log_info("Isso está usando nosso logger personalizado!")

# Agora vamos configurar um Agent e executá-lo.
# Todo o logging vindo do Agent usará nosso logger personalizado.
agent = Agent()
agent.print_response("O que posso fazer para melhorar meu sono?")
