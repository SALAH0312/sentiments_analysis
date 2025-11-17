# Analyse de Sentiments (Texte & X/Twitter) - Projet PFE

Une application web complète développée avec Flask pour un projet de fin d'études (PFE). L'application analyse les sentiments (Positif ou Négatif) en temps réel à partir de deux sources : un texte libre saisi par l'utilisateur, ou les tweets les plus récents d'un compte X (Twitter) spécifié.

## 🚀 Fonctionnalités

  * **Double Entrée :** L'utilisateur peut choisir d'analyser soit un bloc de texte simple, soit un nom d'utilisateur X (Twitter).
  * **Analyse de Texte Simple :** Prédiction du sentiment (Positif ✅ ou Négatif ❌) d'une phrase ou d'un paragraphe.
  * **Intégration de l'API X (Twitter) :** Récupération automatique des derniers tweets (en excluant les retweets et les réponses) d'un compte utilisateur.
  * **Analyse de Tweets :** Application du modèle de sentiment sur chaque tweet récupéré.
  * **Tableau de Bord Statistique :** Génération d'un résumé visuel (graphique circulaire) et de statistiques (pourcentage de tweets positifs/négatifs) pour le compte analysé.
  * **Interface Moderne :** Une interface utilisateur propre, réactive et à fichier unique, construite avec HTML, CSS et un mode sombre.

## 🛠️ Technologies Utilisées

  * **Backend :** [Flask](https://flask.palletsprojects.com/) (Python)
  * **Frontend :** HTML5, CSS3 (intégré dans le fichier Flask)
  * **Machine Learning :** [Scikit-learn](https://scikit-learn.org/) (pour la Régression Logistique et la vectorisation TF-IDF)
  * **API Sociale :** [Tweepy](https://www.tweepy.org/) (pour l'interaction avec l'API X v2)
  * **Data Science & Graphiques :** [Pandas](https://pandas.pydata.org/) (pour l'entraînement), [Matplotlib](https://matplotlib.org/) (pour la génération des graphiques)
  * **Entraînement :** [Jupyter Notebook](https://jupyter.org/) (`train_model.ipynb`)

## 📂 Structure du Projet
```
X_Sentiments_analysis_application/
│
├── 📄 application_finale.py   # Le serveur Flask (backend + frontend + API)
│
├── 🧠 sentiment_model.pkl      # Le modèle de Régression Logistique entraîné
│
├── 📓 train_model.ipynb       # Notebook pour l'entraînement du modèle
│
├── 📁 dataset/                # Données utilisées pour l'entraînement ( Sentiment140)
│
└── 📄 README.md               
```

## ⚙️ Installation et Exécution Locale

Suivez ces étapes pour lancer le projet sur votre machine.

### 1\. Prérequis

  * Python 3.7+
  * Un compte développeur X (Twitter) et un **Bearer Token** valide.

### 2\. Cloner le Dépôt

```bash
git clone https://github.com/VOTRE-NOM-UTILISATEUR/VOTRE-PROJET.git
cd VOTRE-PROJET
```

### 3\. Installer les Dépendances

Il est recommandé d'utiliser un environnement virtuel.

```bash
# Créer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate

# Installer les librairies nécessaires
pip install flask tweepy pandas scikit-learn matplotlib
```

### 4\. Configurer l'API X (Twitter)

Ouvrez le fichier `application_finale.py` avec un éditeur de code. Trouvez la ligne suivante :

```python
# Collez votre Bearer Token ici
BEARER_TOKEN = "PASTE_YOUR_BEARER_TOKEN_HERE"
```

Remplacez la chaîne de caractères par votre propre **Bearer Token** de l'API X.

### 5\. Lancer l'Application

Assurez-vous que votre fichier `sentiment_model.pkl` se trouve dans le même dossier que `application_finale.py`.

```bash
python application_finale.py
```

L'application démarrera et sera accessible à l'adresse suivante dans votre navigateur :
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

## 🤖 À propos du Modèle

Le modèle de sentiment est une **Régression Logistique** entraînée sur le dataset [Sentiment140](http://help.sentiment140.com/for-students). Ce dataset contient 1.6 million de tweets étiquetés comme `0` (négatif) ou `4` (positif).

Le notebook `train_model.ipynb` contient toutes les étapes de :

1.  Chargement et nettoyage des données.
2.  Vectorisation du texte à l'aide de **TF-IDF**.
3.  Entraînement et évaluation du classificateur par Régression Logistique.
4.  Sauvegarde du modèle final dans `sentiment_model.pkl` à l'aide de `pickle`.

-----

*Développé pour un projet de fin d'études.*
