import sqlite3
import requests
import json

def create_database():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных и таблица 'posts' успешно созданы.")

def fetch_posts_from_api():
    url = "https://jsonplaceholder.typicode.com/posts"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        posts = response.json()
        print(f"Успешно получено {len(posts)} постов с сервера.")
        return posts
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []

def save_posts_to_db(posts):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM posts')
    
    for post in posts:
        cursor.execute('''
            INSERT INTO posts (id, userId, title, body)
            VALUES (?, ?, ?, ?)
        ''', (post['id'], post['userId'], post['title'], post['body']))
    
    conn.commit()
    conn.close()
    print(f"Успешно сохранено {len(posts)} постов в базу данных.")

def get_posts_by_user(user_id):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, body FROM posts WHERE userId = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        print(f"\nПосты пользователя с userId = {user_id}:")
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"Заголовок: {row[1]}")
            print(f"Содержание: {row[2]}")
            print("-" * 50)
    else:
        print(f"Посты для user_id = {userId} не найдены.")
    
    return rows

def main():
    create_database()
    
    posts = fetch_posts_from_api()
    if not posts:
        return
    
    save_posts_to_db(posts)
    
    print("\n" + "="*60)
    get_posts_by_user(1)

if __name__ == "__main__":
    main()
