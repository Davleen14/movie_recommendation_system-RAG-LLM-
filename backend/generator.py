from groq import Groq

client = Groq()


def converse_with_llm(prompt):

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a movie recommendation assistant."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return chat_completion.choices[0].message.content
