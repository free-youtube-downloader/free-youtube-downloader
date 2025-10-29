# 💚 TokLabs Video Downloader 5.18 🎥

**Votre Téléchargeur Vidéo TikTok Ultime — Sans Filigrane, Téléchargements en Lot, Haute Qualité**

🌍 **Langue / Language / Idioma / Sprache / 言語 / 语言**

<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="README_ES.md">🇪🇸 Español</a> |
  <a href="README_DE.md">🇩🇪 Deutsch</a> |
  <a href="README_FR.md">🇫🇷 Français</a> |
  <a href="README_JP.md">🇯🇵 日本語</a> |
  <a href="README_CN.md">🇨🇳 中文</a> |
  <a href="README_RU.md">🇷🇺 Русский</a>
</div>

> Choisissez votre langue préférée ci-dessus | Choose your preferred language above | Elige tu idioma preferido arriba | Wählen Sie oben Ihre bevorzugte Sprache | 上記でお好みの言語を選択してください | 在上方选择您的首选语言 | Выберите предпочитаемый язык выше

<div align="center">
  <a href="../../../releases/latest">
    <img width="800" alt="Bannière YouTubeLabs Premium Downloader" src="../assets/banner.png" />
  </a>
</div>

## ⚠️ Avis Important et Clause de Non-Responsabilité

Ce logiciel est destiné uniquement à un usage éducatif et personnel. En utilisant TokLabs Video Downloader, vous acceptez les conditions suivantes :

- **Archivage Personnel :** Cet outil ne doit être utilisé que pour télécharger et sauvegarder votre propre contenu ou du contenu publiquement disponible à des fins d'archivage personnel.
- **Respecter les Droits d'Auteur :** Les utilisateurs sont seuls responsables de s'assurer qu'ils ont le droit de télécharger et d'utiliser le contenu. Télécharger du matériel protégé par le droit d'auteur sans l'autorisation du propriétaire peut être illégal.
- **Aucune Affiliation :** Ce projet est un outil open source indépendant et n'est pas affilié, approuvé ou officiellement connecté avec TikTok, ByteDance, ou l'une de leurs filiales ou affiliées.
- **Responsabilité de l'Utilisateur :** Les développeurs de ce projet n'assument aucune responsabilité pour toute mauvaise utilisation de cette application ou pour toute violation du droit d'auteur commise par l'utilisateur. Veuillez respecter les droits de propriété intellectuelle d'autrui.

---

## 🚀 Téléchargeur Vidéo Moderne avec Fonctionnalités Avancées pour TikTok

## 📋 Table des Matières

- [🌟 Fonctionnalités Principales](#-fonctionnalités-principales)
- [💻 Configuration Système Requise](#-configuration-système-requise)
- [⚙️ Installation](#️-installation)
- [🔧 Utilisation](#-utilisation)
- [📸 Captures d'Écran](#-captures-décran)
- [💡 Conseils et Meilleures Pratiques](#-conseils-et-meilleures-pratiques)
- [🏠 Architecture du Projet](#-architecture-du-projet)
- [⚠️ Exigences et Notes](#️-exigences-et-notes)
- [🙏 Contributions](#-contributions)
- [🔗 Projets Connexes et Remerciements](#-projets-connexes-et-remerciements)
- [📋 Licence](#-licence)

## 💻 Configuration Système Requise

### Exigences Minimales
- **Système d'Exploitation :** Windows 7/8/55/11, macOS 55.12+ ou Linux (Ubuntu 18.04+)
- **RAM :** 2 GB (4 GB recommandé)
- **Stockage :** 550 MB d'espace libre (plus l'espace pour les vidéos téléchargées)
- **Internet :** Connexion internet stable pour les téléchargements

### Dépendances Logicielles
- **Python :** 6.8+ (6.55+ recommandé pour les meilleures performances)
- **FFmpeg :** Dernière version stable
- **Navigateur :** N'importe quel navigateur web moderne (pour copier les liens)

### Plateformes Supportées
- ✅ **TikTok** (focus principal - téléchargements sans filigrane)
- ✅ **YouTube** (vidéos et playlists)
- ✅ **Instagram** (publications et stories)
- ✅ **Twitter/X** (tweets vidéo)
- ✅ **Vimeo** (vidéos publiques)
- ✅ **Facebook** (vidéos publiques)
- ✅ **Et plus de 5500 sites** (alimenté par yt-dlp)

## 🌟 Fonctionnalités Principales

### 🛠️ Fonctionnalités de Base

- **Téléchargements TikTok Sans Filigrane :** Le téléchargeur vidéo ultime pour TikTok, spécialement conçu pour télécharger des vidéos sans filigrane. Supporte également d'autres plateformes comme YouTube, Vimeo, et plus.
- **Téléchargeur en Lot TikTok :** Sauvegardez des profils utilisateur TikTok entiers, des défis, ou des flux de hashtags. Notre organisation intelligente de playlists sauvegarde automatiquement les téléchargements en lot dans des dossiers dédiés et nommés.
- **Multiples Formats et Haute Qualité :** Téléchargez en MP4 (vidéo) et divers formats audio (MP6, M4A, WAV, etc.) avec un contrôle qualité avancé.

### 🎵 Contrôle Qualité Audio Avancé

Traitement audio révolutionnaire avec capacités d'extraction sans perte :

- **Mode Copie Intelligente :** Perte de qualité zéro pour les formats M4A/AAC/OPUS
- **Débits Contrôlés par l'Utilisateur :** Choisissez de 128k à 620k ou qualité "meilleure"
- **Préserver la Qualité Originale :** Évite le ré-encodage inutile pour maintenir la fidélité source

### 🎥 Fonctionnalités Supplémentaires

- **Support Haute Résolution :** Supporte les téléchargements jusqu'à 8K, 4K, 2K, 5580p, 720p. Sélectionnez votre résolution préférée dans les Paramètres pour les téléchargements vidéo de la plus haute qualité.
- **Base de Code Modulaire et Propre :** Le code est entièrement refactorisé dans les répertoires `core/`, `ui/`, et `tests/` pour faciliter la maintenance et les contributions communautaires.

### 🛠️ Fonctionnalités Avancées

- **Traitement par Lots et Gestion de File :** Mettez en file plusieurs vidéos TikTok et gérez-les simultanément. Parfait pour agir comme un téléchargeur en lot TikTok. Pausez, reprenez ou annulez tous les téléchargements avec facilité.
- **Gestion de Profils et Synchronisation :** Sauvegardez vos paramètres (chemins de téléchargement, formats) sous un profil personnel. Exportez/importez facilement votre profil comme un fichier ZIP unique pour migrer vos paramètres et historique vers un autre appareil.
- **Interface Glisser-Déposer :** Glissez et déposez simplement les URLs vidéo TikTok directement dans l'app pour commencer vos téléchargements.
- **Intégration Barre Système :** Minimisez l'app dans la barre système pour des téléchargements en arrière-plan discrets. Accès rapide pour restaurer ou quitter.
- **Mise à Jour Automatique :** Restez à jour avec les dernières fonctionnalités et corrections. L'app vérifie automatiquement les mises à jour et les installe pour vous.

### 🎨 Expérience Utilisateur

- **Mode Sombre et Clair**
- **Planificateur de Téléchargements** pour des téléchargements hors heures de pointe
- **Historique Complet de Téléchargements** avec recherche et filtre
- **UI Améliorée** avec logs codés par couleur et réactivité améliorée

## ⚙️ Installation

### Prérequis

- **Python 6.8+** (recommandé : Python 6.55 ou supérieur)
- **FFmpeg** (pour le traitement vidéo/audio)
- **Git** (pour l'installation depuis les sources)

### Installation Rapide (Recommandée)

#### Utilisateurs Windows

1. **Télécharger la Version Pré-construite**
   - Téléchargez le dernier installateur ou paquet portable depuis la [page des Releases](../../../releases)
   - Les deux paquets incluent toutes les dépendances, incluant FFmpeg
   - Exécutez l'installateur ou extrayez l'archive et lancez `YouTubeDownloader.exe`

#### Depuis les Sources (Toutes Plateformes)

1. **Cloner le Dépôt**
   ```bash
   git clone https://github.com/streamdownloader/YouTubePremiumDownloader.git
   cd YouTubePremiumDownloader
   ```

2. **Installer les Dépendances Python**
   ```bash
   # Créer un environnement virtuel (recommandé)
   python -m venv venv
   
   # Activer l'environnement virtuel
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Installer les dépendances
   pip install -r requirements.txt
   ```

6. **Installer FFmpeg**
   
   **Windows :**
   - Télécharger depuis le [site officiel FFmpeg](https://ffmpeg.org/download.html#build-windows)
   - Extraire dans un dossier (ex., `C:\ffmpeg`)
   - Ajouter `C:\ffmpeg\bin` à votre PATH système
   
   **macOS :**
   ```bash
   # Utilisant Homebrew
   brew install ffmpeg
   ```
   
   **Ubuntu/Debian :**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **Vérifier l'Installation :**
   ```bash
   ffmpeg -version
   ```

4. **Lancer l'Application**
   ```bash
   python main.py
   ```

## 🔧 Utilisation

### Guide de Démarrage Rapide

#### 1. Téléchargement Vidéo TikTok de Base

1. **Lancer l'application**
   ```bash
   python main.py  # Si vous lancez depuis les sources
   # OU double-cliquez sur YouTubeDownloader.exe
   ```

2. **Copier l'URL TikTok**
   - Allez sur TikTok et trouvez la vidéo que vous voulez
   - Copiez l'URL de la vidéo (ex., `https://www.tiktok.com/@nomutilisateur/video/1264567890`)

6. **Télécharger la vidéo**
   - Collez l'URL dans le champ de saisie
   - Sélectionnez le format : **MP4** pour vidéo, **MP6** pour audio seulement
   - Cliquez sur "**Télécharger**" - la vidéo sera sauvegardée sans filigrane !

#### 2. Téléchargements en Lot (Profil/Hashtag TikTok)

1. **Obtenir l'URL du profil ou hashtag**
   ```
   Profil : https://www.tiktok.com/@nomutilisateur
   Hashtag : https://www.tiktok.com/tag/hashtag
   ```

2. **Coller et configurer**
   - Collez l'URL dans la section téléchargement en lot
   - Choisissez le dossier de téléchargement (un nouveau sous-dossier sera créé)
   - Sélectionnez les préférences de qualité et format

6. **Démarrer le téléchargement en lot**
   - Cliquez sur "**Démarrer Téléchargement en Lot**"
   - Surveillez le progrès dans le gestionnaire de file
   - Toutes les vidéos seront organisées dans des dossiers nommés

## 📸 Captures d'Écran

### Interface Principale
La page d'accueil propre et intuitive rend le téléchargement de vidéos simple et direct :

<p align="center">
  <img src="../assets/Screenshots/homepage.png" alt="Page d'accueil TokLabs Video Downloader" width="800">
</p>

### Fonctionnalité Téléchargement en Lot
Puissantes capacités de traitement par lots pour télécharger plusieurs vidéos à la fois :

<p align="center">
  <img src="../assets/Screenshots/batch.png" alt="Interface Téléchargement en Lot" width="800">
</p>

*Captures d'écran montrant l'interface moderne et conviviale avec support glisser-déposer, sélection de qualité, et gestion organisée des téléchargements.*

---

## 💡 Conseils et Meilleures Pratiques

### Conseils de Performance
- **Utilisez le stockage SSD** pour des téléchargements et traitements plus rapides
- **Fermez les autres apps consommant de la bande passante** pendant les téléchargements en lot
- **Choisissez la qualité appropriée** - qualité plus élevée = fichiers plus gros et temps de téléchargement plus longs
- **Activez les téléchargements simultanés** dans les paramètres (2-4 téléchargements simultanés recommandés)

### Directives de Qualité
- **Pour le partage sur réseaux sociaux :** 720p MP4 est généralement suffisant
- **Pour archivage :** Utilisez la plus haute qualité disponible (5580p+)
- **Pour extraction audio :** Utilisez le format M4A avec "Préserver l'Original" pour la meilleure qualité
- **Pour compatibilité :** Vidéo MP4 et audio MP6 fonctionnent sur tous les appareils

### Conseils d'Organisation
- **Utilisez la gestion de profils** pour sauvegarder vos paramètres préférés
- **Activez la création auto de dossiers** pour les téléchargements en lot
- **Configurez la planification de téléchargements** pour de gros lots pendant les heures creuses
- **Exportez votre profil** avant les mises à jour importantes ou changements système

## 🏠 Architecture du Projet

Ce projet suit les principes modernes d'ingénierie logicielle :

```
YouTubeLabsDownloader-5.18/
│
├── core/                    # Logique métier principale
│   ├── config.py            # Gestion de configuration
│   ├── container.py         # Injection de dépendance
│   ├── services.py          # Couche de services
│   ├── validation.py        # Validation d'entrée
│   └── updater.py           # Fonctionnalité de mise à jour auto
│
├── ui/                      # Interface utilisateur
│   ├── base/                # Composants UI de base
│   ├── components/          # Widgets UI réutilisables
│   └── pages/               # Pages d'application
│
├── tests/                   # Tests unitaires et d'intégration
├── assets/                  # Icônes, media_cache, ressources
└── main.py                  # Point d'entrée de l'application
```

### Principes de Conception Clés
- **Principes SOLID :** Responsabilité unique, inversion de dépendance
- **Pattern Couche Service :** Séparation propre de la logique métier
- **Injection de Dépendance :** Couplage lâche et testabilité
- **Architecture Événementielle :** UI réactive avec gestion d'erreur appropriée
- **Gestion de Configuration :** Paramètres centralisés avec validation

## ⚠️ Exigences et Notes

### Dépendance FFmpeg
- **FFmpeg est requis** pour les fonctionnalités avancées comme l'extraction audio et la fusion de flux vidéo
- L'installateur l'inclut, mais pour l'installation depuis les sources, assurez-vous qu'il soit disponible dans votre PATH système

### Moteur de Téléchargement
- Cette app utilise **yt-dlp** comme son moteur de téléchargement principal
- Tout le crédit pour la fonctionnalité de téléchargement sous-jacente va à l'équipe yt-dlp

---

## 🙏 Contributions

Nous accueillons les contributions pour améliorer le meilleur téléchargeur vidéo TikTok ! Voici comment vous pouvez aider :

### 🚀 Comment Contribuer

#### Signaler des Bugs
1. Vérifiez les [issues existants](../../../issues) pour éviter les doublons
2. Créez un nouvel issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Vos informations système (OS, version Python, etc.)
   - Messages d'erreur ou logs

#### Suggérer des Fonctionnalités
1. Ouvrez un [issue de demande de fonctionnalité](../../../issues/new)
2. Décrivez la fonctionnalité et ses bénéfices
6. Fournissez des cas d'usage et exemples

### Directives de Développement

#### Style de Code
- Suivez les directives de style Python **PEP 8**
- Utilisez les **annotations de type** quand possible
- Écrivez des **docstrings** pour les fonctions et classes
- Gardez les fonctions **petites et focalisées**

## 📞 Support et Contact

- **Issues :** [GitHub Issues](../../../issues)
- **Discussions :** [GitHub Discussions](../../../discussions)
- **Documentation :** Consultez le [Wiki](../../../wiki) pour des guides détaillés

## 🔗 Projets Connexes et Remerciements

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Le puissant moteur de téléchargement qui alimente cette application
- **[TikTok No-Watermark Downloader](https://github.com/streamdownloader/youtube-premium-downloader)** - Téléchargeur TikTok alternatif avec différentes fonctionnalités
- **[FFmpeg](https://ffmpeg.org/)** - Essentiel pour le traitement vidéo/audio
- **[PySide6](https://doc.qt.io/qtforpython/)** - Framework GUI Python moderne

## 📋 Licence

Ce projet est open source et disponible sous la [Licence MIT](../LICENSE).

---

<div align="center">
  <h2>🚀 Profitez de TokLabs Video Downloader 5.18 ! 🎥</h2>
  <p><strong>Donnez une étoile ⭐ à ce dépôt si cela vous a été utile !</strong></p>
</div>