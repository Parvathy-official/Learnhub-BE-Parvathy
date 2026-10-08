import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserBackend.settings')
django.setup()

from django.test import Client

client = Client()
res = client.get('/api/courses/')
print('Courses Count:', res.json().get('count'))
for c in res.json().get('results', []):
    print(f"ID: {c['id']} | Slug: {c['slug']} | Title: {c['title']} | Price: INR {c['price']}")

res1 = client.get('/api/courses/1/')
c1_data = res1.json()
print('Course 1 Status:', res1.status_code, '| Title:', c1_data.get('title'), '| Modules:', len(c1_data.get('modules', [])), '| Lessons:', sum(len(m.get('lessons', [])) for m in c1_data.get('modules', [])))

res2 = client.get('/api/courses/performance-marketing-meta-ads-blueprint/')
c2_data = res2.json()
print('Course 2 Slug Status:', res2.status_code, '| Title:', c2_data.get('title'), '| Modules:', len(c2_data.get('modules', [])), '| Lessons:', sum(len(m.get('lessons', [])) for m in c2_data.get('modules', [])))

res3 = client.get('/api/courses/fullstack-ai-nextjs-python/')
c3_data = res3.json()
print('Course 3 Slug Status:', res3.status_code, '| Title:', c3_data.get('title'), '| Modules:', len(c3_data.get('modules', [])), '| Lessons:', sum(len(m.get('lessons', [])) for m in c3_data.get('modules', [])))

res4 = client.get('/api/courses/high-ticket-client-acquisition-agency/')
c4_data = res4.json()
print('Course 4 Slug Status:', res4.status_code, '| Title:', c4_data.get('title'), '| Modules:', len(c4_data.get('modules', [])), '| Lessons:', sum(len(m.get('lessons', [])) for m in c4_data.get('modules', [])))
