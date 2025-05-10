from nixtla import NixtlaClient

API_KEY = "nixak-jsNhpCMbb57LXMig3cRT4Kjddj11ncuh1pQvNiMyg2wqRfIQDdQmC9XQ3sPtdsr6mlu1bnTBfAD1aBa3"

# Inicializa el cliente con tu API key de TimeGPT
nixtla_client = NixtlaClient(
    api_key=API_KEY
)
# Verifica que la clave funcione
assert nixtla_client.validate_api_key() 