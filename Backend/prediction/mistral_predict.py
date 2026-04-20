import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def predict_disease(symptoms: str) -> str:

    prompt = f"""You are a smart medical assistant. A user has entered the following input: "{symptoms}"

Your job is to first understand what the user means:

- If the input describes a health-related issue (e.g. "i feel lazy", "my head hurts", "i am tired"), interpret it medically and respond with the most likely conditions and which type of doctor to consult. Keep the response short, 2 to 3 lines maximum.

- If the input is clearly not health-related (e.g. "i play cricket", "what are you doing", "hello"), politely tell the user that you are a medical assistant and can only help with health-related symptoms.

Do not follow any fixed format. Just respond naturally and intelligently based on what the user said."""

    print("Initializing communication with Mistral model...")
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    print("Successfully received prediction from Mistral model.")

    return response.choices[0].message.content.strip()