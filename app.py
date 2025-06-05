from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import json
import tempfile
import re
import os

app = Flask(__name__)

def slugify(title):
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
    slug = slug.lower().strip().replace(' ', '-')
    slug = re.sub(r'-+', '-', slug)
    return slug

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded.", 400

        data = json.load(file)
        clean_data = []

        for item in data:
            blog_id = item.get('blog_id', '')
            category = item.get('category', '')
            content_html = item.get('content', '')
            crawl_at = item.get('crawl_at', '')
            created_at = item.get('created_at', '')
            updated_at = item.get('updated_at', '')
            is_hot = item.get('is_hot', 0)
            seo_description = item.get('seo_description', '')
            seo_keywords = item.get('seo_keywords', '')
            seo_title = item.get('seo_title', '')
            status = item.get('status', '')
            tags = item.get('tags', None)
            thumbnail = item.get('thumbnail', '')
            title = item.get('title', '')

            source_url = blog_id
            slug = slugify(title)

            soup = BeautifulSoup(content_html, 'lxml')

            for tag in soup(['script', 'style', 'ins', 'iframe']):
                tag.decompose()

            content_clean = str(soup)
            content_text = soup.get_text(separator='\n', strip=True)

            images = []
            for img_tag in soup.find_all('img'):
                src = img_tag.get('src') or img_tag.get('data-at-1366') or img_tag.get('data-at-1920')
                if src:
                    images.append(src)

            clean_item = {
                'blog_id': blog_id,
                'source_url': source_url,
                'slug': slug,
                'category': category,
                'title': title,
                'seo_title': seo_title,
                'seo_description': seo_description,
                'seo_keywords': seo_keywords,
                'thumbnail': thumbnail,
                'content_clean': content_clean,
                'content_text': content_text,
                'images': images,
                'status': status,
                'tags': tags,
                'created_at': created_at,
                'updated_at': updated_at,
                'is_hot': is_hot,
                'crawl_at': crawl_at
            }

            clean_data.append(clean_item)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        return send_file(temp_file.name, as_attachment=True, download_name='cleaned.json')

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
   app.run(debug=True, host='127.0.0.1', port=port)
