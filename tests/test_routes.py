def test_index(client):
    response = client.get("/")
    assert b"<title>Home</title>" in response.data


def test_about(client):
    response = client.get("/about")
    assert b"<title>About</title>" in response.data
