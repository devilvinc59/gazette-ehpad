# 📰 Gazette EHPAD - Créateur de gazette mensuelle

Application Streamlit pour créer facilement des gazettes mensuelles pour votre EHPAD, avec génération de texte par IA (Claude).

## ✨ Fonctionnalités

- **4 sections éditables** : Couverture/Éditorial, Activités, Planning/Actualités, Chronique Mémoire
- **Génération de texte par IA** : Décrivez ce que vous voulez, Claude rédige pour vous
- **Upload de photos** : Ajoutez les photos de vos activités
- **Export PDF** : Générez un PDF prêt à imprimer
- **Interface intuitive** : Simple et accessible

## 🚀 Déploiement sur Streamlit Cloud (Gratuit)

### Étape 1 : Créer un compte GitHub
1. Allez sur [github.com](https://github.com)
2. Créez un compte gratuit si vous n'en avez pas

### Étape 2 : Créer un nouveau repository
1. Cliquez sur "New repository"
2. Nommez-le `gazette-ehpad`
3. Cochez "Public"
4. Cliquez sur "Create repository"

### Étape 3 : Uploader les fichiers
1. Cliquez sur "uploading an existing file"
2. Glissez-déposez les 3 fichiers :
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Cliquez sur "Commit changes"

### Étape 4 : Déployer sur Streamlit Cloud
1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez-vous avec votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez votre repository `gazette-ehpad`
5. Main file path : `app.py`
6. Cliquez sur "Deploy!"

### Étape 5 : Obtenir votre clé API Anthropic
1. Allez sur [console.anthropic.com](https://console.anthropic.com)
2. Créez un compte
3. Allez dans "API Keys"
4. Créez une nouvelle clé
5. Copiez-la et gardez-la précieusement

## 💡 Utilisation

1. Ouvrez votre application (URL fournie par Streamlit Cloud)
2. Entrez votre clé API Anthropic dans la barre latérale
3. Naviguez entre les sections
4. Remplissez les champs et cliquez sur "Générer" pour créer les textes
5. Modifiez les textes si nécessaire
6. Exportez en PDF quand vous êtes satisfait

## 💰 Coûts

- **Streamlit Cloud** : Gratuit
- **GitHub** : Gratuit
- **API Anthropic** : ~0.003€ par génération de texte (très économique)
  - Une gazette complète coûte environ 0.02€

## 🔒 Sécurité

Votre clé API n'est jamais stockée. Elle reste dans votre session de navigateur uniquement.

## 📞 Support

Pour toute question, n'hésitez pas à demander de l'aide !
