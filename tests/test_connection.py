# /tests/test_connection.py
# Quick smoke test: confirms EuriEmbedder and EuriChatModel can reach the EURI
# gateway and get back real responses, before trusting the full pipeline.

from rag.embedding import EuriEmbedder
# the embedding wrapper we want to test

from rag.chat_model import EuriChatModel
# the chat model wrapper we want to test


def test_embedding():
    # sends one short sentence and checks we get a real vector back
    embedder = EuriEmbedder()
    vector = embedder(["Stripe supports SEPA payments for EU merchants."])[0]
    print(f"embedding ok, vector length: {len(vector)}")
    # printing the length, not the vector itself, since a wall of numbers isn't useful to read


def test_chat_model():
    # sends one short instruction and checks we get a real reply back
    chat_model = EuriChatModel()
    reply = chat_model("You are a helpful assistant.", "Reply with just the word: working")
    print(f"chat model ok, reply: {reply}")


if __name__ == "__main__":
    test_embedding()
    test_chat_model()
    # so this file can be run directly: python -m tests.test_connection