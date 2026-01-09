from io import StringIO

import pandas as pd
import requests
from agno.utils.log import logger
from sqlalchemy import create_engine

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db_engine = create_engine(db_url)
s3_uri = "https://agno-public.s3.amazonaws.com/f1"

# Lista de arquivos e seus nomes de tabela correspondentes
files_to_tables = {
    f"{s3_uri}/constructors_championship_1958_2020.csv": "constructors_championship",
    f"{s3_uri}/drivers_championship_1950_2020.csv": "drivers_championship",
    f"{s3_uri}/fastest_laps_1950_to_2020.csv": "fastest_laps",
    f"{s3_uri}/race_results_1950_to_2020.csv": "race_results",
    f"{s3_uri}/race_wins_1950_to_2020.csv": "race_wins",
}


def load_f1_data():
    """Carregar dados de F1 no banco de dados"""

    logger.info("Carregando banco de dados.")
    # Carregar cada arquivo CSV na tabela PostgreSQL correspondente
    for file_path, table_name in files_to_tables.items():
        logger.info(f"Carregando {file_path} na tabela {table_name}.")
        # Baixar o arquivo usando requests
        response = requests.get(file_path, verify=False)
        response.raise_for_status()  # Levantar uma exceção para códigos de status ruins

        # Ler os dados CSV do conteúdo da resposta
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        df.to_sql(table_name, db_engine, if_exists="replace", index=False)
        logger.info(f"{file_path} carregado na tabela {table_name}.")

    logger.info("Banco de dados carregado.")


if __name__ == "__main__":
    # Desabilitar avisos de verificação SSL
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    load_f1_data()
