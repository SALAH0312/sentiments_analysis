from flask import Flask, request, render_template_string
import tweepy
import pickle
import re
import time

# --- Nouveaux imports pour la génération du graphique ---
import matplotlib

matplotlib.use('Agg')  # Utilise un backend non-interactif
import matplotlib.pyplot as plt
import io
import base64

# ----------- Interface HTML (Avec logos et design de tweets) --------------------
HTML_FORM_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyse de Sentiment Avancée</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #f8f9fa;
            --fg-color: #ffffff;
            --text-color: #212529;
            --primary-color: #007bff;
            --primary-color-hover: #0056b3;
            --success-color: #28a745;
            --error-color: #dc3545;
            --border-color: #dee2e6;
            --shadow-color: rgba(0, 0, 0, 0.05);
            --x-logo-color: #000000;
        }

        body.dark-mode {
            --bg-color: #121212;
            --fg-color: #1e1e1e;
            --text-color: #e9ecef;
            --border-color: #343a40;
            --shadow-color: rgba(255, 255, 255, 0.05);
            --x-logo-color: #ffffff;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Aligner en haut pour les longues listes */
            min-height: 100vh;
            box-sizing: border-box;
            transition: background-color 0.3s, color 0.3s;
        }

        .container {
            max-width: 700px;
            width: 100%;
            margin: auto;
            background-color: var(--fg-color);
            padding: 2.5rem 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px var(--shadow-color);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }

        .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        h1 { color: var(--primary-color); font-weight: 700; margin: 0; }
        .theme-switch-wrapper { display: flex; align-items: center; }
        .theme-switch { display: inline-block; height: 34px; position: relative; width: 60px; }
        .theme-switch input { display:none; }
        .slider { background-color: #ccc; bottom: 0; cursor: pointer; left: 0; position: absolute; right: 0; top: 0; transition: .4s; }
        .slider:before { background-color: white; bottom: 4px; content: ""; height: 26px; left: 4px; position: absolute; transition: .4s; width: 26px; }
        input:checked + .slider { background-color: var(--primary-color); }
        input:checked + .slider:before { transform: translateX(26px); }
        .slider.round { border-radius: 34px; }
        .slider.round:before { border-radius: 50%; content: '☀️'; text-align: center; line-height: 26px; font-size: 16px; }
        input:checked + .slider.round:before { content: '🌙'; }

        form { margin-bottom: 2rem; }
        label { display: block; font-weight: 500; margin-bottom: 0.75rem; font-size: 0.95rem; }
        .input-group { position: relative; margin-bottom: 1.5rem; }
        .input-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            display: inline-block;
        }
        /* --- NOUVEAU : Icône X de Twitter --- */
        .x-icon {
            background-color: var(--x-logo-color);
            mask-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227"><path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.163 519.284ZM569.165 687.828L521.697 619.934L144.011 79.6909H306.615L611.412 515.685L658.88 583.579L1055.08 1150.31H892.476L569.165 687.828Z"/></svg>');
            mask-repeat: no-repeat;
            mask-position: center;
        }

        textarea, input[type=text] {
            width: 100%; padding: 12px 12px 12px 45px; border-radius: 8px;
            border: 1px solid var(--border-color); background-color: var(--bg-color);
            color: var(--text-color); font-size: 1rem;
            transition: border-color 0.2s, box-shadow 0.2s, background-color 0.3s;
            box-sizing: border-box; font-family: 'Inter', sans-serif;
        }
        textarea:focus, input[type=text]:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.2); }
        button[type=submit] {
            background: linear-gradient(45deg, var(--primary-color), var(--primary-color-hover));
            color: white; border: none; padding: 14px 20px; font-size: 1.1rem; font-weight: 500;
            margin-top: 0.5rem; border-radius: 8px; width: 100%; cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2); font-family: 'Inter', sans-serif;
        }
        button[type=submit]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 123, 255, 0.3); }
        .divider { text-align: center; margin: 2rem 0; color: #aaa; font-weight: 500; }

        .result, .error { margin-top: 2rem; padding: 1.5rem; border-radius: 8px; animation: fadeIn 0.5s ease; }
        .result { background-color: transparent; border: none; padding: 0; }
        .error { background-color: rgba(220, 53, 69, 0.1); border-left: 5px solid var(--error-color); }

        /* --- NOUVEAU : Style pour les cartes de Tweet --- */
        .result ul { padding-left: 0; list-style: none; }
        .tweet-card {
            background-color: var(--fg-color);
            border: 1px solid var(--border-color);
            padding: 1rem 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            transition: background-color 0.3s, border-color 0.3s;
        }
        .tweet-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .tweet-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--x-logo-color);
            mask-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227"><path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.163 519.284ZM569.165 687.828L521.697 619.934L144.011 79.6909H306.615L611.412 515.685L658.88 583.579L1055.08 1150.31H892.476L569.165 687.828Z"/></svg>');
            margin-right: 10px;
        }
        .tweet-author {
            font-weight: 700;
            font-size: 1rem;
        }
        .tweet-text {
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1rem;
        }
        .sentiment-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 700;
            color: white;
        }
        .sentiment-badge.positive {
            background-color: var(--success-color);
        }
        .sentiment-badge.negative {
            background-color: var(--error-color);
        }
        /* --- Fin des styles de carte Tweet --- */

        .stats-container { margin-top: 2rem; padding: 1.5rem; background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; transition: background-color 0.3s; }
        .stats-container h4 { margin-top: 0; text-align: center; color: var(--primary-color); }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; align-items: center; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 8px; }
        .stats-details p { margin: 0.5rem 0; font-size: 1rem; }
        .stats-details .positive { color: var(--success-color); }
        .stats-details .negative { color: var(--error-color); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 600px) { .stats-grid { grid-template-columns: 1fr; } .header-container { flex-direction: column; gap: 1rem; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-container">
            <h1>Analyse de Sentiment</h1>
            <div class="theme-switch-wrapper">
                <label class="theme-switch" for="theme-toggle">
                    <input type="checkbox" id="theme-toggle" />
                    <div class="slider round"></div>
                </label>
            </div>
        </div>

        <form method="post" action="/predict">
            <label for="text_input">Analyser un texte</label>
            <div class="input-group">
                <span class="input-icon" style="font-size: 1.2em;">✍️</span>
                <textarea id="text_input" name="text_input" placeholder="Écrivez une phrase ou un paragraphe ici..." rows="4"></textarea>
            </div>
            <button type="submit">Analyser ce texte</button>
        </form>

        <div class="divider">OU</div>

        <form method="post" action="/predict">
            <label for="username_input">Analyser un compte X (Twitter)</label>
            <div class="input-group">
                 <span class="input-icon x-icon"></span>
                <input type="text" id="username_input" name="username_input" placeholder="ex: elonmusk, BillGates..." />
            </div>
            <button type="submit">Analyser les derniers tweets</button>
        </form>

        {% if results %}
            <div class="result">
                <h3>Analyse pour @{{ request.form.username_input }}</h3>
                <ul>
                {% for tweet in results %}
                    <li class="tweet-card">
                        <div class="tweet-header">
                            <div class="tweet-avatar"></div>
                            <span class="tweet-author">@{{ request.form.username_input }}</span>
                        </div>
                        <p class="tweet-text">{{ tweet.text }}</p>
                        {% if 'Positif' in tweet.sentiment %}
                            <span class="sentiment-badge positive">Positif ✅</span>
                        {% else %}
                             <span class="sentiment-badge negative">Négatif ❌</span>
                        {% endif %}
                    </li>
                {% endfor %}
                </ul>
            </div>

            {% if stats and chart_image %}
            <div class="stats-container">
                <h4>Résumé de l'analyse</h4>
                <div class="stats-grid">
                    <div class="stats-details">
                        <p><strong>Total des tweets analysés :</strong> {{ stats.total }}</p>
                        <p class="positive"><strong>Tweets positifs :</strong> {{ stats.positive_count }} ({{ '%.1f'|format(stats.positive_percentage) }}%)</p>
                        <p class="negative"><strong>Tweets négatifs :</strong> {{ stats.negative_count }} ({{ '%.1f'|format(stats.negative_percentage) }}%)</p>
                    </div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{{ chart_image }}" alt="Graphique circulaire des sentiments">
                    </div>
                </div>
            </div>
            {% endif %}

        {% elif result %}
             <div class="result" style="padding: 1.5rem; border-left: 5px solid var(--success-color); background-color: rgba(40, 167, 69, 0.1);">
                <strong>Texte analysé :</strong> {{ result.text }}<br>
                <strong>Sentiment détecté :</strong> {{ result.sentiment }}
            </div>
        {% elif error %}
            <div class="error"><strong>Erreur :</strong> {{ error }}</div>
        {% endif %}
    </div>

    <script>
        const themeToggle = document.getElementById('theme-toggle');
        const currentTheme = localStorage.getItem('theme');

        if (currentTheme) {
            document.body.classList.add(currentTheme);
            if (currentTheme === 'dark-mode') {
                themeToggle.checked = true;
            }
        } else {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                 document.body.classList.add('dark-mode');
                 themeToggle.checked = true;
            }
        }

        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light-mode');
            }
        });
    </script>
</body>
</html>
"""

# --------- Configuration de Flask ---------------------
app = Flask(__name__)

# --------- Chargement du Modèle -----------------------
try:
    with open("sentiment_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None

# --------- API Twitter ----------------------
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAFV62QEAAAAAqhFqrDrTBajg2%2Bh1W%2F7P42VCtSw%3DIBZruaD7GgALbASeVOf6mN9qcFmD7zgF6RZmfmgDP1MrNv5ZcR"
client = None
if BEARER_TOKEN and not BEARER_TOKEN.startswith("TON_"):
    try:
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
    except Exception as e:
        print(f"Erreur Client Twitter : {e}")


# --------- Nettoyage du Texte ---------------------
def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.lower().strip()


# --------- Fonction de Génération du Graphique ---------
def create_pie_chart(positive, negative, is_dark_mode):
    if positive == 0 and negative == 0:
        return None

    labels = 'Positif', 'Négatif'
    sizes = [positive, negative]
    colors = ['#28a745', '#dc3545']
    explode = (0.1, 0) if positive > negative else (0, 0.1)

    text_color = 'white' if is_dark_mode else 'black'

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=90,
           textprops={'color': text_color, 'weight': 'bold'})
    ax.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64


# --------- Routes Flask ---------------------
@app.route('/')
def home():
    return render_template_string(HTML_FORM_PAGE)


@app.route('/predict', methods=['POST'])
def predict():
    text_input = request.form.get("text_input")
    username_input = request.form.get("username_input")
    error, result, results = None, None, None
    stats, chart_image = None, None

    if not model:
        error = "⚠ Le modèle n'est pas chargé."
    elif text_input:
        cleaned = clean_text(text_input)
        prediction = model.predict([cleaned])[0]
        sentiment = "Positif ✅" if prediction == 4 else "Négatif ❌"
        result = {"text": text_input, "sentiment": sentiment}
    elif username_input:
        if not client:
            error = "⚠ API Twitter non disponible. Vérifiez le Bearer Token."
        else:
            try:
                user = client.get_user(username=username_input)
                if not user.data:
                    error = f"⚠ Aucun utilisateur trouvé avec le nom @{username_input}."
                else:
                    tweets = client.get_users_tweets(id=user.data.id, max_results=20, exclude=["retweets", "replies"])
                    if tweets.data:
                        results = []
                        positive_count = 0
                        negative_count = 0

                        for tw in tweets.data:
                            cleaned = clean_text(tw.text)
                            if not cleaned: continue
                            prediction = model.predict([cleaned])[0]
                            if prediction == 4:
                                sentiment = "Positif ✅"
                                positive_count += 1
                            else:
                                sentiment = "Négatif ❌"
                                negative_count += 1
                            results.append({"text": tw.text, "sentiment": sentiment})

                        total = positive_count + negative_count
                        if total > 0:
                            stats = {
                                "positive_count": positive_count,
                                "negative_count": negative_count,
                                "total": total,
                                "positive_percentage": (positive_count / total) * 100,
                                "negative_percentage": (negative_count / total) * 100,
                            }
                            chart_image = create_pie_chart(positive_count, negative_count, is_dark_mode=False)
                    else:
                        error = f"⚠ Aucun tweet trouvé pour le compte @{username_input}."
            except tweepy.errors.TooManyRequests:
                error = "⚠ Trop de requêtes envoyées à Twitter. Réessayez plus tard (erreur 429)."
            except Exception as e:
                error = f"⚠ Erreur Twitter : {str(e)}"
    else:
        error = "Veuillez remplir un des champs."

    return render_template_string(HTML_FORM_PAGE, result=result, results=results, error=error, stats=stats,
                                  chart_image=chart_image)


# --------- Lancer l'App ----------------------
if __name__ == '__main__':
    if not model:
        print("⚠ Modèle introuvable. Assurez-vous que 'sentiment_model.pkl' est présent.")
    if not client:
        print("⚠ Client Twitter non initialisé. Vérifiez votre Bearer Token.")
    print("🚀 Accédez à l'application : http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)