import requests

# Базовый URL API
BASE_URL = "https://jsonplaceholder.typicode.com"

def main():
    print("=== Задание 1: GET-запрос с чётными ID ===\n")
    
    response = requests.get(f"{BASE_URL}/posts")
    
    if response.status_code == 200:
        posts = response.json()
        
        even_user_posts = [post for post in posts if post['userId'] % 2 == 0]
        
        print(f"Найдено постов с чётными userId: {len(even_user_posts)}\n")
        
        for post in even_user_posts:
            print(f"ID: {post['id']}, User ID: {post['userId']}")
            print(f"Заголовок: {post['title']}")
            print(f"Текст: {post['body']}")
            print("-" * 50)
    else:
        print(f"Ошибка при получении постов: {response.status_code}")

    print("\n=== Задание 2: POST-запрос (создание нового поста) ===\n")
    
    new_post = {
        "title": "Тест",
        "body": "Что-то тестовое",
        "userId": 1
    }
    
    post_response = requests.post(f"{BASE_URL}/posts", json=new_post)
    
    if post_response.status_code == 201:
        created_post = post_response.json()
        print("Пост успешно создан:")
        print(created_post)
        
        created_post_id = created_post['id']
    else:
        print(f"Ошибка при создании поста: {post_response.status_code}")
        return

    print("\n=== Задание 3: PUT-запрос (обновление поста) ===\n")
    
    updated_post = {
        "id": created_post_id,
        "title": "Обновлённый пост",
        "body": "Это обновлённое тело поста.",
        "userId": 1
    }
    
    put_response = requests.put(f"{BASE_URL}/posts/{created_post_id}", json=updated_post)
    
    if put_response.status_code == 200:
        updated_data = put_response.json()
        print("Пост успешно обновлён:")
        print(updated_data)
    else:
        print(f"Ошибка при обновлении поста: {put_response.status_code}")

if __name__ == "__main__":
    main()
