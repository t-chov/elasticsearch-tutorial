import requests

from typing import Iterable
from colorama import init, Fore, Style
from retry import retry

init()


def info(text: str) -> str:
    return Fore.CYAN + text + Style.RESET_ALL


@retry(tries=3, delay=1)
def put_document(es_endpoint: str, docs: Iterable[str]):
    url = '{}/_bulk'.format(es_endpoint)
    header = {
        'Content-Type': 'application/json'
    }
    response = requests.put(url, data="\n".join(docs) + "\n", headers=header)
    response.raise_for_status()
