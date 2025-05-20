import requests

def generate_flashcards_with_ollama(context: str, num_flashcards: int = 5) -> list[dict]:
    
    prompt = f"""You are a helpful assistant that creates high-quality flashcards for learning.

Generate exactly {num_flashcards} flashcards based on the following context. Follow these strict rules:
- Each flashcard must start with "Q:" followed by a complete question.
- Each question must be followed by "Answer:" and then a complete answer.
- Do not include any numbering or labels like "Card 1" or "Flashcard 2".
- Only output flashcards in this format — if you feel it is required you can add small explanations.

Example:
Q: What is grit and how does it relate to success?
Answer: Grit is passion and perseverance for very long-term goals.

Q: What is the key characteristic that emerged as a significant predictor of success in various contexts studied by Dr. Joseph Geni?
A) Social intelligence B) Good looks C) Physical health D) Grit
Answer: D) Grit

Now create {num_flashcards} flashcards from the following context:

Context: {context}

Format each flashcard starting with 'Q:' and 'Answer:' as shown above."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            output = response.json()["response"]
            print("Raw model output:", output)
            flashcards = parse_flashcards(output)
            flashcards = [
                card for card in flashcards
                if isinstance(card, dict)
                and card.get("question")
                and card.get("answer")
                and isinstance(card["question"], str)
                and isinstance(card["answer"], str)
            ]
            return flashcards[:num_flashcards]  # Just in case model returns extra
        else:
            return [{"question": f"API Error: {response.status_code}", "answer": f"API Error: {response.status_code}"}]
    except Exception as e:
        return [{"question": f"Error: {e}", "answer": f"Error: {e}"}]

def parse_flashcards(text: str) -> list[dict]:
    # Split by 'Q:' and then parse Q/A pairs
    flashcards = []
    parts = text.split("\nQ:")
    for part in parts:
        if not part.strip():
            continue
        if part.startswith("Q:"):
            part = part[2:].strip()
        # Now part looks like "question text\nAnswer: answer text"
        if "Answer:" in part:
            question, answer = part.split("Answer:", 1)
            flashcards.append({
                "question": question.strip(),
                "answer": answer.strip()
            })
    return flashcards
