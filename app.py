import os
from flask import Flask, render_template, request, send_from_directory
from forms import ImageRotateForm
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'your-public-key'  # Получить на https://www.google.com/recaptcha
app.config['RECAPTCHA_PRIVATE_KEY'] = 'your-private-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'
app.config['PLOTS_FOLDER'] = 'static/plots'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs(app.config['PLOTS_FOLDER'], exist_ok=True)


def create_color_histogram(image_path, output_path):
    """Создает гистограмму распределения цветов изображения."""
    img = Image.open(image_path).convert('RGB')
    rgb = np.array(img)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    colors = ['red', 'green', 'blue']
    for i, color in enumerate(colors):
        axes[i].hist(rgb[:, :, i].ravel(), bins=256, color=color, alpha=0.7)
        axes[i].set_title(f'Канал {color}')
        axes[i].set_xlim([0, 256])

    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageRotateForm()
    if form.validate_on_submit():
        # Сохраняем загруженное изображение
        image = form.image.data
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filename)

        # Поворачиваем изображение
        angle = form.angle.data
        img = Image.open(filename)
        rotated = img.rotate(angle, expand=True)

        # Сохраняем результат
        processed_filename = f"rotated_{angle}_{image.filename}"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        rotated.save(processed_path)

        # Создаем гистограммы
        orig_hist = f"hist_orig_{image.filename}.png"
        rotated_hist = f"hist_rotated_{processed_filename}.png"

        create_color_histogram(filename, os.path.join(app.config['PLOTS_FOLDER'], orig_hist))
        create_color_histogram(processed_path, os.path.join(app.config['PLOTS_FOLDER'], rotated_hist))

        return render_template('result.html',
                               original=filename,
                               processed=processed_path,
                               orig_hist=f'plots/{orig_hist}',
                               rotated_hist=f'plots/{rotated_hist}')

    return render_template('index.html', form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


@app.route('/plots/<filename>')
def plot_file(filename):
    return send_from_directory(app.config['PLOTS_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)