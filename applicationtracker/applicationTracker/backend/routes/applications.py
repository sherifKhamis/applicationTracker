import os
import html
import json
import time
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from extensions import db
from models.application import Application

bp = Blueprint('applications', __name__, url_prefix='/api/applications')

ALLOWED_STATUSES = {'Applied', 'Interviewing', 'Offer', 'Rejected'}


def _sanitize_html_element(element):
    for tag in element.find_all(True):
        attrs_to_keep = {}
        if 'href' in tag.attrs:
            attrs_to_keep['href'] = tag.attrs['href']
        if 'src' in tag.attrs:
            attrs_to_keep['src'] = tag.attrs['src']
        tag.attrs = attrs_to_keep
    return str(element)


def _preserve_formatted_html(element):
    for tag in element.find_all(['script', 'style', 'noscript']):
        tag.decompose()
    return str(element)


def _text_to_formatted_html(text):
    if not text:
        return '<p>No content found.</p>'

    normalized_lines = [line.strip() for line in html.unescape(text).splitlines()]
    blocks = []
    current_paragraph = []
    list_items = []
    list_type = None

    def flush_paragraph():
        nonlocal current_paragraph
        if current_paragraph:
            blocks.append(f"<p>{' '.join(current_paragraph)}</p>")
            current_paragraph = []

    def flush_list():
        nonlocal list_items, list_type
        if list_items:
            tag_name = 'ol' if list_type == 'ol' else 'ul'
            blocks.append(f"<{tag_name}>" + ''.join(f'<li>{item}</li>' for item in list_items) + f"</{tag_name}>")
            list_items = []
            list_type = None

        def looks_like_heading(line):
            if not line:
                return False
            if line.endswith((':', ' –', ' -')):
                return True
            if line.endswith(('.', '!', '?')):
                return False
            if len(line) > 80:
                return False
            words = line.split()
            if not 2 <= len(words) <= 10:
                return False
            return line[0].isupper() and not line.startswith(('•', '-', '*'))

    for line in normalized_lines:
        if not line:
            flush_paragraph()
            flush_list()
            continue

        if line.startswith(('• ', '- ', '* ')):
            flush_paragraph()
            list_type = 'ul'
            list_items.append(line[2:].strip())
            continue

        if len(line) > 2 and line[0].isdigit() and line[1] in {'.', ')'} and line[2:].strip():
            flush_paragraph()
            list_type = 'ol'
            list_items.append(line[2:].strip())
            continue

        if list_items:
            flush_list()

            if looks_like_heading(line):
                flush_paragraph()
                blocks.append(f'<h2>{html.escape(line)}</h2>')
                continue

        current_paragraph.append(line)

    flush_paragraph()
    flush_list()

    if not blocks:
        escaped_text = html.escape(text.strip()).replace('\n', '<br>')
        return f'<p>{escaped_text}</p>'

    enhanced_blocks = []
    for block in blocks:
        if block.startswith('<p>') and len(block) > 220 and '. ' in block:
            paragraph_text = block[3:-4]
            sentence_chunks = [chunk.strip() for chunk in paragraph_text.split('. ') if chunk.strip()]
            if len(sentence_chunks) > 1:
                enhanced_blocks.extend(f'<p>{chunk.rstrip(".") if chunk.endswith(".") else chunk}.</p>' for chunk in sentence_chunks)
                continue
        enhanced_blocks.append(block)

    return ''.join(enhanced_blocks)


def _extract_workday_api_content(url):
    parsed_url = urlparse(url)
    host_parts = parsed_url.netloc.split('.')
    tenant = host_parts[0] if host_parts else ''

    path_parts = [part for part in parsed_url.path.split('/') if part]
    if len(path_parts) < 3:
        return None

    site_name = path_parts[1]
    job_slug = path_parts[-1]
    api_url = f"{parsed_url.scheme}://{parsed_url.netloc}/wday/cxs/{tenant}/{site_name}/job/{job_slug}"

    response = requests.get(
        api_url,
        headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'},
        timeout=10,
    )
    response.raise_for_status()

    payload = response.json()
    job_posting = payload.get('jobPostingInfo', {})
    job_description = job_posting.get('jobDescription', '')

    if not job_description:
        return None

    return {
        'title': job_posting.get('title') or '',
        'description': '',
        'content': f"<div class='job-description'>{job_description}</div>"
    }


def _extract_job_posting_from_json_ld(soup):
    for script in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        raw_json = script.string or script.get_text(strip=True)
        if not raw_json:
            continue

        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            continue

        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = item.get('@type')
            is_job_posting = item_type == 'JobPosting' or (
                isinstance(item_type, list) and 'JobPosting' in item_type
            )
            if not is_job_posting:
                continue

            return {
                'title': item.get('title') or item.get('name') or '',
                'description': item.get('description') or ''
            }

    return None


def _extract_workday_content(soup):
    structured_job = _extract_job_posting_from_json_ld(soup)
    if structured_job and structured_job['description']:
        title = structured_job['title'] or (soup.title.string if soup.title else 'No Title')
        return {
            'title': title,
            'description': '',
            'content': f"<div class='job-description'>{_text_to_formatted_html(structured_job['description'])}</div>"
        }

    workday_selectors = [
        '[data-automation-id="jobPostingDescription"]',
        '[data-automation-id="jobDescription"]',
        '[data-automation-id="jobPostingHeader"]',
    ]

    for selector in workday_selectors:
        element = soup.select_one(selector)
        if element and element.get_text(strip=True):
            title = soup.title.string if soup.title else 'No Title'
            if selector == '[data-automation-id="jobPostingHeader"]':
                header = element.find(['h1', 'h2'])
                if header and header.get_text(strip=True):
                    title = header.get_text(strip=True)
            content_html = _preserve_formatted_html(element)
            if '<' not in content_html:
                plain_text = element.get_text('\n', strip=True)
                content_html = f"<div class='job-description'>{_text_to_formatted_html(plain_text)}</div>"
            return {
                'title': title,
                'description': '',
                'content': content_html
            }

    return None

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

        workday_content = None
        normalized_url = url.lower()
        if 'workday.com' in normalized_url or 'myworkdayjobs.com' in normalized_url:
            try:
                workday_content = _extract_workday_api_content(url)
            except Exception:
                workday_content = _extract_workday_content(soup)

        if workday_content:
            return {
                'title': workday_content['title'] or title,
                'description': description,
                'content': workday_content['content']
            }
        
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


@bp.route('/<int:id>', methods=['PATCH'])
def update_application(id):
    app_to_update = db.session.get(Application, id)
    if not app_to_update:
        return jsonify({'error': 'Application not found'}), 404

    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400

    if status not in ALLOWED_STATUSES:
        return jsonify({'error': 'Invalid status'}), 400

    app_to_update.status = status
    db.session.commit()

    return jsonify(app_to_update.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
def delete_application(id):
    app_to_delete = db.session.get(Application, id)
    if not app_to_delete:
        return jsonify({'error': 'Application not found'}), 404
        
    db.session.delete(app_to_delete)
    db.session.commit()
    return jsonify({'message': 'Application deleted successfully'}), 200