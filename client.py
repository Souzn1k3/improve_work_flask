import requests

base = "http://127.0.0.1:5000"

def show(label, response):
    try:
        body = response.json()
    except ValueError:
        body = response.text
    print(label, response.status_code, body)
    return body

note1 = show("POST ok", requests.post(f"{base}/notes", json={"author": "Аня", "text": "Привет"}))
note2 = show("POST second", requests.post(f"{base}/notes", json={"author": "Борис", "text": "Второй"}))
note3 = show("POST third", requests.post(f"{base}/notes", json={"author": "Аня", "text": "Третий"}))
show("POST no author", requests.post(f"{base}/notes", json={"text": "Без автора"}))
show("POST empty text", requests.post(f"{base}/notes", json={"author": "Аня", "text": "   "}))

show("GET list", requests.get(f"{base}/notes"))
show("GET filter", requests.get(f"{base}/notes", params={"author": "Аня"}))
show("GET sort likes desc", requests.get(f"{base}/notes", params={"sort": "likes", "order": "desc"}))
show("GET sort id asc", requests.get(f"{base}/notes", params={"sort": "id", "order": "asc"}))
show("GET bad sort", requests.get(f"{base}/notes", params={"sort": "text"}))
show("GET bad order", requests.get(f"{base}/notes", params={"order": "up"}))
show("GET page", requests.get(f"{base}/notes", params={"limit": 1, "offset": 1}))
show("GET bad limit", requests.get(f"{base}/notes", params={"limit": 0}))
show("GET bad offset", requests.get(f"{base}/notes", params={"offset": -1}))

show("POST like", requests.post(f"{base}/notes/{note1['id']}/like"))
show("POST like again", requests.post(f"{base}/notes/{note1['id']}/like"))
show("POST like second", requests.post(f"{base}/notes/{note2['id']}/like"))
show("POST like missing", requests.post(f"{base}/notes/999999/like"))

show("PATCH text", requests.patch(f"{base}/notes/{note2['id']}", json={"text": "Только текст"}))
show("PATCH author", requests.patch(f"{base}/notes/{note3['id']}", json={"author": "Вера"}))
show("PATCH bad body", requests.patch(f"{base}/notes/{note2['id']}", json={}))
show("PUT ok", requests.put(f"{base}/notes/{note2['id']}", json={"author": "Ира", "text": "Замена"}))
show("PUT bad body", requests.put(f"{base}/notes/{note2['id']}", json={"author": ""}))
show("PUT missing", requests.put(f"{base}/notes/999999", json={"author": "A", "text": "B"}))

show("GET authors", requests.get(f"{base}/authors"))
show("GET missing note", requests.get(f"{base}/notes/999999"))
show("GET sorted likes desc", requests.get(f"{base}/notes", params={"sort": "likes", "order": "desc"}))

show("DELETE by author", requests.delete(f"{base}/notes", params={"author": "Вера"}))
show("DELETE note", requests.delete(f"{base}/notes/{note1['id']}"))
show("DELETE note again", requests.delete(f"{base}/notes/{note1['id']}"))
show("DELETE without author", requests.delete(f"{base}/notes"))
show("DELETE unknown author", requests.delete(f"{base}/notes", params={"author": "Никто"}))
show("GET final authors", requests.get(f"{base}/authors"))
