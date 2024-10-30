from flask import Flask, request, send_file, render_template_string
import subprocess
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Load the HTML form as a string to render with Flask
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Background Remover</title>
</head>
<body>
    <h1>Upload an Image to Remove Background</h1>
    <form id="uploadForm" action="/remove-bg" method="post" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/png, image/jpeg" required>
        <button type="submit">Upload and Process</button>
    </form>
    <div id="result">
        <h2>Processed Image:</h2>
        <img id="outputImage" alt="Processed Image will appear here" style="display: none; max-width: 100%;">
    </div>

    <script>
        document.getElementById('uploadForm').onsubmit = async function(event) {
            event.preventDefault();
            
            const formData = new FormData();
            formData.append('image', document.querySelector('input[type="file"]').files[0]);
            
            try {
                const response = await fetch('/remove-bg', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const imgUrl = URL.createObjectURL(blob);
                    const outputImage = document.getElementById('outputImage');
                    outputImage.src = imgUrl;
                    outputImage.style.display = 'block';
                } else {
                    alert('Failed to process image');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error uploading or processing the image');
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def upload_form():
    return render_template_string(HTML_FORM)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    """
    Remove background from the uploaded image
    ---
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to process
    responses:
      200:
        description: Processed image with background removed
        content:
          image/png:
            schema:
              type: string
              format: binary
      400:
        description: Invalid input file
    """
    uploaded_file = request.files['image']
    input_path = "input.png"
    output_path = "output.png"
    uploaded_file.save(input_path)

    # Run rembg command
    subprocess.run([
        "rembg", "i", input_path, output_path,
        "--alpha-matting-foreground-threshold", "240",
        "--alpha-matting-background-threshold", "10",
        "--alpha-matting-erode-size", "10",
        "--bgcolor", "255", "255", "255", "255"
    ])

    return send_file(output_path, mimetype='image/png')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
