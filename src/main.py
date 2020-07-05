from tagger import Tagger

tagger = Tagger("crf_pipeline.pkl")

offers = [
    "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
    "¡CDMX a Ginebra, Suiza $13,832!",
    "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
]


aaa = tagger.tag(offers)
