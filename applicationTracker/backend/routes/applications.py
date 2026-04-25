import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.application import Application

bp = Blueprint('applications', __name__, url_prefix='/api/applications')

def fetch_url_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title = soup.title.string if soup.title else 'No Title'
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ''
        
        # Clean up unwanted tags to get clean HTML
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form", "iframe", "aside", "img", "picture"]):
            element.extract()
            
        # Find main content container
        main_content = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.body
        
        if main_content:
            # Strip all attributes except href and src to preserve layout but not break our app's CSS
            for tag in main_content.find_all(True):
                attrs_to_keep = {}
                if 'href' in tag.attrs:
                    attrs_to_keep['href'] = tag.attrs['href']
                if 'src' in tag.attrs:
                    attrs_to_keep['src'] = tag.attrs['src']
                tag.attrs = attrs_to_keep
                
            page_html = str(main_content)
        else:
            page_html = "<p>No content found.</p>"
        
        return {
            "title": title,
            "description": description,
            "content": page_html
        }
    except Exception as e:
        return {
            "title": "Error",
            "description": f"Failed to fetch content from {url}",
            "content": f"Error: {str(e)}"
        }

@bp.route('/', methods=['GET'])
def get_applications():
    apps = Application.query.order_by(Application.date_applied.desc()).all()
    return jsonify([app.to_dict() for app in apps]), 200

@bp.route('/', methods=['POST'])
def add_application():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    if not data or not data.get('company') or not data.get('position'):
        return jsonify({'error': 'Company and Position are required'}), 400

    url = data.get('url', '')
    notes = data.get('notes', '')
    page_content = None
    
    # Download link formatting
    if url:
        link_info = fetch_url_content(url)
        notes = f"{notes}\n\nLink Title: {link_info['title']}\nLink Description: {link_info['description']}".strip()
        page_content = link_info['content']

    # File upload for screenshot
    screenshot_path = None
    if 'screenshot' in request.files:
        file = request.files['screenshot']
        if file.filename != '':
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            unique_filename = f"{timestamp}_{filename}"
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'screenshots')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, unique_filename))
            screenshot_path = f"screenshots/{unique_filename}"
            
    # File upload for cover letter
    cover_letter_path = None
    if 'cover_letter' in request.files:
        file = request.files['cover_letter']
        if file.filename != '':
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            unique_filename = f"{timestamp}_{filename}"
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cover_letters')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, unique_filename))
            cover_letter_path = f"cover_letters/{unique_filename}"
        
    new_app = Application(
        company=data.get('company'),
        position=data.get('position'),
        status=data.get('status', 'Applied'),
        notes=notes,
        url=url,
        screenshot_path=screenshot_path,
        cover_letter_path=cover_letter_path,
        page_content=page_content
    )
    
    db.session.add(new_app)
    db.session.commit()
    
    return jsonify(new_app.to_dict()), 201

@bp.route('/<int:id>', methods=['DELETE'])
def delete_application(id):
    app_to_delete = db.session.get(Application, id)
    if not app_to_delete:
        return jsonify({'error': 'Application not found'}), 404
        
    db.session.delete(app_to_delete)
    db.session.commit()
    return jsonify({'message': 'Application deleted successfully'}), 200