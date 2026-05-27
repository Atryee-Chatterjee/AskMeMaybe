from app import get_llm
def test_get_llm():
    llm = get_llm()
    response = llm.invoke("What is the capital of France?")
    print(response.content)

test_get_llm()