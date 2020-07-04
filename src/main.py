import joblib


pipeline = joblib.load("crf_pipeline.pkl")

offers = [
    "¡CDMX a Santiago 🇨🇱 + Patagonia 🐧 $10,309!",
    "¡CDMX a Ginebra, Suiza $13,832!",
    "¡CDMX a San José, Costa Rica $4,382! 🐸 (Por $1,987 agrega 4 noches de hotel con desayunos)",
]

tokens = pipeline.named_steps["tokeniser"].transform(offers)
labels = pipeline.predict(offers)


for (token, position), label in zip(tokens, labels):
    print(token)
    print(label)
    print()
