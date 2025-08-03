import json
import boto3 # type: ignore 
import logging
from datetime import datetime
from botocore.exceptions import ClientError  # type: ignore

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def get_environment_variables():
    """Get required environment variables"""
    import os
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME')
    
    if not bucket_name or not table_name:
        raise ValueError("Required environment variables not set")
    
    return bucket_name, table_name

def get_image_url(image_id, backup_check=True):
    """Generate Art Institute image URL with fallback"""
    if not image_id:
        return None
    
    # Primary image URL
    primary_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    
    # Alternative smaller size that might be more reliable
    fallback_url = f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg"
    
    return primary_url, fallback_url

def validate_artwork_data(artwork):
    """Enhanced artwork validation"""
    # Ensure required fields exist
    artwork['title'] = artwork.get('title', 'Untitled').strip()
    artwork['artist'] = artwork.get('artist', 'Unknown Artist').strip()
    artwork['date'] = artwork.get('date', 'Unknown Date').strip()
    
    # Clean up empty or very short titles
    if len(artwork['title']) < 2:
        artwork['title'] = 'Untitled'
    
    return artwork

def generate_html_content(artworks):
    """Generate complete HTML content for the gallery"""
    
    current_date = datetime.utcnow().strftime('%B %d, %Y')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Gallery - Daily Art Collection</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .gallery-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .artwork-grid {{
            display: none;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .artwork-grid.active {{
            display: grid;
        }}
        
        .artwork-card {{
            background: #f8f9fa;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .artwork-card:hover {{
            transform: translateY(-5px);
        }}
        
        .artwork-image {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            background: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-style: italic;
        }}
        
        .artwork-info {{
            padding: 20px;
        }}
        
        .artwork-title {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        
        .artwork-artist {{
            color: #7f8c8d;
            margin-bottom: 5px;
            font-size: 1rem;
        }}
        
        .artwork-date {{
            color: #95a5a6;
            font-size: 0.9rem;
        }}
        
        .controls {{
            text-align: center;
            margin-top: 30px;
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        .btn:disabled {{
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
        }}
        
        .page-indicator {{
            margin: 20px 0;
            color: #7f8c8d;
            font-size: 1.1rem;
        }}
        
        .completion-message {{
            display: none;
            text-align: center;
            padding: 30px;
            background: #e8f5e8;
            border-radius: 10px;
            margin-top: 20px;
        }}
        
        .completion-message h3 {{
            color: #27ae60;
            margin-bottom: 15px;
        }}
        
        .random-btn {{
            background: #e74c3c;
            margin-top: 15px;
        }}
        
        .random-btn:hover {{
            background: #c0392b;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .artwork-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Cloud Gallery</h1>
            <p>Daily Art Collection - {current_date}</p>
        </div>
        
        <div class="gallery-container">
            <div class="controls">
                <div class="page-indicator">
                    <span id="currentPage">1</span> of <span id="totalPages">3</span>
                </div>
            </div>
"""

    # Generate artwork grids (3 artworks per page)
    for page in range(3):
        start_idx = page * 3
        end_idx = min(start_idx + 3, len(artworks))
        page_artworks = artworks[start_idx:end_idx]
        
        active_class = "active" if page == 0 else ""
        
        html_content += f"""
            <div class="artwork-grid {active_class}" id="page{page + 1}">
"""
        
        for artwork in page_artworks:
            # Validate and clean artwork data
            artwork = validate_artwork_data(artwork)
            
            image_urls = get_image_url(artwork.get('image_id'))
            
            if image_urls:
                primary_url, fallback_url = image_urls
                # Create image with fallback
                image_html = f'''
                    <img src="{primary_url}" 
                         alt="{artwork['title']}" 
                         class="artwork-image"
                         onerror="this.onerror=null; this.src='{fallback_url}'; if(this.src==='{fallback_url}' && this.complete && this.naturalWidth===0) {{this.style.display='none'; this.nextElementSibling.style.display='flex';}}"
                    >
                    <div class="artwork-image" style="display:none;">Image not available</div>
                '''
            else:
                image_html = '<div class="artwork-image">Image not available</div>'
            
            html_content += f"""
                <div class="artwork-card">
                    {image_html}
                    <div class="artwork-info">
                        <div class="artwork-title">{artwork['title']}</div>
                        <div class="artwork-artist">{artwork['artist']}</div>
                        <div class="artwork-date">{artwork['date']}</div>
                    </div>
                </div>
"""
        
        html_content += "</div>"

    # Add JavaScript and completion message
    html_content += f"""
            <div class="controls">
                <button class="btn" id="prevBtn" onclick="changePage(-1)" disabled>Previous</button>
                <button class="btn" id="nextBtn" onclick="changePage(1)">Next</button>
            </div>
            
            <div class="completion-message" id="completionMessage">
                <h3>🎉 You've viewed all today's artworks!</h3>
                <p>Come back tomorrow for new art, or explore our collection of previous days.</p>
                <button class="btn random-btn" onclick="showRandomArt()">View Random Art from Collection</button>
            </div>
        </div>
    </div>

    <script>
        let currentPage = 1;
        const totalPages = 3;
        
        function changePage(direction) {{
            // Hide current page
            document.getElementById(`page${{currentPage}}`).classList.remove('active');
            
            // Update page number
            currentPage += direction;
            
            // Show new page
            document.getElementById(`page${{currentPage}}`).classList.add('active');
            
            // Update page indicator
            document.getElementById('currentPage').textContent = currentPage;
            
            // Update button states
            document.getElementById('prevBtn').disabled = (currentPage === 1);
            document.getElementById('nextBtn').disabled = (currentPage === totalPages);
            
            // Show completion message if on last page
            if (currentPage === totalPages) {{
                setTimeout(() => {{
                    document.getElementById('completionMessage').style.display = 'block';
                }}, 1000);
            }} else {{
                document.getElementById('completionMessage').style.display = 'none';
            }}
        }}
        
        function showRandomArt() {{
            alert('Random art feature coming soon! This would query DynamoDB for previous artworks.');
            // Future: Implement AJAX call to get random artworks from DynamoDB
        }}
    </script>
</body>
</html>
"""
    
    return html_content

def upload_to_s3(bucket_name, html_content):
    """Upload HTML content to S3 bucket"""
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=html_content,
            ContentType='text/html',
            CacheControl='no-cache'
        )
        logger.info(f"Successfully uploaded HTML to S3 bucket: {bucket_name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        return False

def lambda_handler(event, context):
    """
    Generate HTML gallery and upload to S3
    """
    logger.info("Starting HTML generation and S3 upload")
    
    try:
        # Get environment variables
        bucket_name, table_name = get_environment_variables()
        
        # Get artworks from previous step
        if 'body' in event and 'artworks' in event['body']:
            artworks = event['body']['artworks']
        else:
            raise ValueError("No artworks found in event data")
        
        logger.info(f"Generating HTML for {len(artworks)} artworks")
        
        # Validate we have artworks
        if not artworks:
            raise ValueError("No artworks to display")
        
        # Generate HTML content
        html_content = generate_html_content(artworks)
        
        # Upload to S3
        upload_success = upload_to_s3(bucket_name, html_content)
        
        if not upload_success:
            raise Exception("Failed to upload HTML to S3")
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Successfully generated and uploaded HTML gallery',
                'artworks_count': len(artworks),
                'bucket_name': bucket_name,
                'url': f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating HTML: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Failed to generate HTML gallery'
            }
        }