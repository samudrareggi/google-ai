# ePlus AI Toolkit — Français

<!-- Source README.md git-blob: 2b8488a21c25e7b771f7a4014f8b945e182fe285 -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · **Français**

**Aperçu macOS :** la [version Mac](docs/MACOS-PREVIEW.md) implémente les étapes 0–5. Les étapes 2–5 peuvent entraîner de vrais frais et exigent une confirmation distincte ; la compatibilité des paiements avec un véritable Mac/MuMu reste non vérifiée.

> **Document de référence :** [README original en anglais](README.md). Cette version est rédigée en français pour faciliter la lecture, tout en conservant les commandes, les limites et les avertissements du projet. En cas de doute, reportez-vous au code et à la documentation d'origine.

**ePlus AI Toolkit** permet de consulter les offres Google AI Pro accessibles via Google One et Google Play sur un appareil Android. L'outil fonctionne sous **Windows et macOS** : vous le lancez depuis PowerShell sur Windows, ou Terminal (zsh/bash) sur Mac. L'interface Textual et les commandes utilisent le même moteur Python, ADB et Frida.

![Interface ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Outil non officiel ; des frais réels peuvent être facturés.** Les **étapes 2 à 5** peuvent ouvrir un véritable paiement Google Play et appuyer automatiquement sur **Subscribe (S'abonner)**. L'affichage d'une offre, d'un prix initial nul ou d'un message indiquant qu'un paiement a été demandé **ne prouve pas** l'éligibilité, la gratuité, l'activation ni la prolongation de l'abonnement. Avant toute opération, vérifiez dans Google Play le compte, le montant dû aujourd'hui, le prix de renouvellement et la date de facturation. Arrêter l'outil n'annule pas une transaction déjà envoyée.

> [!NOTE]
> **Prévoyez au moins 3 USD de solde disponible pour trois opérations distinctes de 1 USD, et non un seul débit de 3 USD.** Dans le parcours de **24 mois** signalé, l'étape 2 (12 mois initiaux), l'étape 3 (+6 mois) et l'étape 4 (+6 mois) correspondent à **trois opérations de vérification de carte ou de paiement de 1 USD chacune** : **3 × US$1 = US$3**. Une opération peut n'être qu'une préautorisation temporaire, et non un débit définitif ; le montant peut varier selon la banque, le compte et Google Play. **Les 3 USD représentent le solde minimal de cet exemple, pas des frais fixes ni une garantie d'obtenir 24 mois.** Une préautorisation peut réduire le solde disponible et est généralement levée sous **1 à 14 jours ouvrés**, selon la banque. Vérifiez après chaque étape l'opération et la date de renouvellement dans Google Play. L'étape 5 est facultative et **ne fait pas partie de ces trois opérations**. [Documentation officielle de Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Avertissement et responsabilité

Ce projet est **indépendant, sans affiliation, parrainage ni approbation officielle** de Google, Google One, Google Play, NetEase ou MuMuPlayer. Le logiciel est fourni **en l'état**, sans garantie concernant les offres, les résultats d'abonnement ou la compatibilité. Utilisez-le uniquement sur vos appareils et comptes ou avec autorisation, conformément aux lois et conditions des plateformes. Consultez la [décharge complète (anglais)](DISCLAIMER.md) et les [précautions de sécurité](SECURITY.md).

## 1. Préparer votre environnement

**Suivez les instructions correspondant à votre système.** Sur Mac, vous n'avez pas besoin d'installer PowerShell.

| Élément | Windows | macOS |
| --- | --- | --- |
| Terminal | **PowerShell 5.1 ou version ultérieure** | **Terminal**, avec zsh ou bash |
| Python | **3.10 ou version ultérieure** (commande `python`) | **3.10 ou version ultérieure** (`python3`) ; création d'un environnement local `.venv` |
| Git | Git pour Windows | Git via Xcode Command Line Tools ou Homebrew |
| Android | Appareil ou émulateur rooté avec ADB ; la procédure Windows prend en charge **MuMuPlayer** | Android rooté ou émulateur compatible ; **MuMuPlayer Pro pour Mac** est une option Apple Silicon, pas Intel |
| Applications | Google Play Store et Google One, connectés au compte à vérifier | Ces mêmes applications sur l'appareil Android choisi |
| ADB | L'outil peut localiser ou télécharger Android SDK Platform-Tools | Installation séparée, par exemple `brew install android-platform-tools` ; vérification avec `adb devices` |
| Frida | **16.5.9**, préparée si nécessaire sous Windows | **16.5.9** dans `.venv` ; compatibilité Android à vérifier |
| Démarrage | `.\run-all.ps1` | `sh run-macos.sh` ou `ePlus-AI-Toolkit.command` |

Les deux systèmes nécessitent un environnement Android correctement configuré et auquel vous avez le droit d'accéder. Le code macOS couvre les étapes 0–5, mais **aucun paiement réel sur Mac/MuMu n'a encore été validé**. Consultez les guides [Windows](docs/INSTALLATION.md) et [macOS](docs/MACOS-PREVIEW.md).

### Prérequis sous Windows

- Windows avec **PowerShell 5.1+** et **Python 3.10+**.
- MuMuPlayer installé séparément, avec root et débogage ADB activés.
- Google Play Store et Google One installés sur Android et connectés au compte concerné.
- Une liaison ADB et une installation compatible de **Frida 16.5.9**. Le programme peut préparer ces outils, mais **il n'installe pas MuMuPlayer**.

### Étape 1 — Installer MuMuPlayer

Téléchargez la version Windows depuis le [site officiel de MuMuPlayer (NetEase)](https://www.mumuplayer.com/download/). Évitez les sites de téléchargement non officiels.

Lancez l'émulateur, activez root et ADB, puis vérifiez la présence de Google Play Store et de Google One. Connectez-vous au compte Google que vous souhaitez vérifier.

Pour un parcours illustré, consultez le [guide d'installation sur le Wiki GitHub](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Télécharger et démarrer

Dans PowerShell :

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Pour une copie déjà téléchargée :

```powershell
git pull --ff-only
.\run-all.ps1
```

La commande **sans arguments** ouvre l'interface Textual ; elle ne lance aucun achat automatiquement. Le programme peut installer/préparer Textual, ADB ou Frida si nécessaire. Il n'est généralement **pas nécessaire** de lancer `setup_env.py` au préalable. La préparation peut modifier l'émulateur, le proxy ou des paramètres réseau.

Si ADB est dans le PATH, vérifiez la connexion :

```powershell
adb devices
```

L'appareil doit être en état `device`, pas `offline` ni `unauthorized`. Voir le [guide de dépannage](docs/DETAILED-GUIDE.md).

### Si la version actuelle ne fonctionne pas

Si l'exécution de la dernière version du dépôt provoque des erreurs, vous pouvez essayer une **version déjà publiée** depuis [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Lisez les notes de version et téléchargez un paquet Windows **s'il est joint**. Si seul le téléchargement automatique **Source code (zip)** de GitHub est disponible, téléchargez le ZIP, décompressez-le, ouvrez PowerShell dans le dossier extrait puis exécutez :

```powershell
.\run-all.ps1
```

**Source code (zip) n'est ni un `.exe` compilé ni un programme d'installation.** Conservez cette version dans un **dossier séparé** pour ne pas écraser votre copie actuelle. Une ancienne version peut ne pas inclure les derniers correctifs ; Windows, Python, MuMuPlayer, ADB/Frida et les précautions de paiement restent nécessaires. Si le problème persiste, consultez le [dépannage](docs/DETAILED-GUIDE.md) ou [ouvrez une issue](https://github.com/hoangsvit/google-ai/issues).

## macOS — Installation et démarrage

Sous macOS, installez **Git**, **Python 3.10+** et **Android SDK Platform-Tools (ADB)** (Homebrew : `brew install android-platform-tools`). Connectez un Android rooté avec Google Play Store et Google One, ou un émulateur compatible. **MuMuPlayer Pro sur Mac nécessite Apple Silicon** ; un Mac Intel demande un autre environnement Android compatible.

Ouvrez le **Terminal** et exécutez :

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` ouvre l'interface Textual avec les **étapes 0–5**. `--check` contrôle l'environnement (et peut modifier les réglages), `--list` consulte seulement les offres, et `--step 2` présélectionne l'étape **sans payer automatiquement**. Les étapes 2–5 peuvent entraîner de vrais frais et nécessitent une confirmation individuelle. **Les paiements sur un vrai Mac/MuMu restent non vérifiés.** Consultez le [guide Mac détaillé](docs/MACOS-PREVIEW.md).

## Vérifier la connexion Android et consulter les offres (Windows + macOS)

Le tableau de bord propose deux fonctions de vérification issues du parcours de configuration Android et de la liste d'offres du projet d'origine :

- **Diagnose Android connection — Diagnostic de connexion :** vérifie la présence d'ADB, affiche les appareils Android autorisés, relève leur architecture ABI et contrôle Google One ainsi que la version de Frida installée sur l'ordinateur. Les instructions s'adaptent à Windows (PowerShell, MuMu, Platform-Tools) ou macOS (Terminal, Homebrew). Cette fonction **n'installe aucun logiciel, ne connecte ni ne redémarre l'émulateur, ne lance pas Frida et ne déclenche aucun paiement**. La commande `adb devices` peut néanmoins démarrer le serveur ADB local.
- **Check Device & Offers (Step 1) — Appareil et offres :** interroge les offres à l'aide du moteur Android/Frida existant et les affiche dans **Offer Explorer**, sous Live Status. Seuls les identifiants du produit et de l'offre, la première période de facturation et le caractère nul ou non du prix initial sont affichés. Les jetons d'offre ou d'achat, les identifiants de compte non masqués et les données bancaires ne sont jamais présentés. Contrairement au diagnostic de connexion, **cette opération peut préparer l'environnement Android** et modifier certains réglages.

**Un premier prix à zéro ne garantit ni la gratuité ni une prolongation de l'abonnement.** En mode consultation uniquement, Step 1 interroge les produits `g1.2tb.ai.subs_variant`, `g1.play.2tb.ai` et `g1.2tb.ai`. Les étapes 2–5 conservent leurs requêtes propres. Comme le rapport Android ne donne pas tous les tarifs des périodes suivantes, Offer Explorer indique que les futurs prix sont **non vérifiés**. Vérifiez les tarifs et les conditions directement dans Google Play.

## 3. Interface Textual

Lorsqu'une étape est en cours, les commandes **Check Device & Offers**, **Run** et les sélecteurs de mode ou d'étape sont désactivés pour éviter les exécutions simultanées. L'étape 0 peut modifier la configuration locale ; l'étape 1 ne déclenche pas de paiement, mais peut préparer ADB et Frida. Vérifiez le résultat dans Google Play avant de poursuivre avec **Next**. **Arrêter ou fermer l'outil n'annule pas une transaction déjà transmise.**


**Check Device & Offers** exécute **Step 1 — Available offers**, pour consulter les offres **sans déclencher de paiement**. Surveillez **Live Status** et **Show technical details** ; l'absence de nouveaux journaux pendant 30 secondes ne signifie pas forcément que l'outil est bloqué.

Sous Windows, connectez-vous au compte voulu dans Google Play avant de consulter les offres. Si l’outil vérifie le compte et trouve l’offre de 12 mois dont le prix initial est nul, choisissez **Review 12-month checkout** pour vérifier les conditions et autoriser séparément le Step 2. Si Google Play vous le demande, saisissez les informations de paiement directement dans l’application. Vérifiez ensuite dans Google Play l’état de l’abonnement et sa date de renouvellement.

Sous Windows, **Prepare MuMu** permet de créer et d’ouvrir une nouvelle instance Android 15 en mode portrait. Saisissez l’adresse Google Play à détecter, puis connectez-vous dans MuMu et effectuez les vérifications demandées. Une fois le compte détecté, choisissez **Check Device & Offers** pour exécuter le Step 1 sur la nouvelle instance.

Dans **Advanced: Run by step** :

| Mode | Fonctionnement |
| --- | --- |
| **One step only** | Exécute uniquement l'étape 0 à 5 sélectionnée |
| **From selected step** | Lance une séquence guidée depuis l'étape 2 à 5 sélectionnée |
| **All: Steps 2–5** | Lance une séquence guidée à partir de l'étape 2 ; l'étape 5 est facultative |

| Étape | Fonction | Risque |
| --- | --- | --- |
| **0 — Environment** | Diagnostic/préparation d'Android, ADB et Frida | Aucun paiement ; peut modifier les paramètres |
| **1 — Available offers** | Consultation des offres Google Play | Aucun paiement ; la préparation peut modifier l'environnement |
| **2 — Pro 12 months** | Ancien processus d'offre de 12 mois | **Paiement réel possible** |
| **3 — Pro +6 months** | Mise à jour de l'abonnement d'origine | **Paiement réel possible** |
| **4 — Pro +6 months (second)** | Seconde mise à jour de l'abonnement | **Paiement réel possible** |
| **5 — Optional +6 months** | Mise à jour facultative | **Paiement réel possible** |

**Exemple signalé sur 24 mois (à vérifier dans Google Play) :**

| Étape | Durée si l'opération aboutit | Opération distincte |
| --- | --- | --- |
| **2 — Pro 12 months** | **12 mois** initiaux | **1 USD** (1re opération) |
| **3 — Pro +6 months** | **18 mois** au total | **1 USD** (2e opération) |
| **4 — Pro +6 months (second)** | **24 mois** au total | **1 USD** (3e opération) |
| **Total jusqu'à l'étape 4** | **24 mois après vérification** | **3 × US$1 = US$3**, et non un paiement unique de 3 USD |

**L'étape 5 est facultative et exclue de ces trois opérations.** Ni la durée affichée ni une préautorisation ne prouvent que l'abonnement a bien été prolongé ; contrôlez l'abonnement et sa date de renouvellement après chaque étape.

Les durées sont les **anciens noms des étapes** et ne garantissent aucune prolongation. Si vous avez déjà un abonnement actif, **ne relancez pas l'étape 2**.

Dans le TUI, **chaque étape de paiement exige une approbation distincte**. Même si un envoi de paiement est signalé, vérifiez le forfait actif, les frais et le renouvellement dans les [abonnements Google Play](https://play.google.com/store/account/subscriptions). Ne sélectionnez **Verified in Google Play → Next** que si vous avez confirmé personnellement la modification. L'outil **ne prouve pas à lui seul** l'activation.

**Arrêt/sortie :** Stop pour les étapes 0–1 demande l'arrêt du processus local. Pour les étapes 2–5, **Stop after this step** bloque les étapes suivantes, mais **n'interrompt pas de force un paiement en cours**. Pendant un paiement, **Q / Exit** attend la fin de l'étape actuelle. **D** affiche/masque le journal technique ; **R** lance le mode choisi.

## 4. Commandes PowerShell (utilisateurs avancés)

**Sous Windows uniquement.** Ces commandes utilisent PowerShell. Sur Mac, utilisez `run-macos.sh` et le [guide macOS](docs/MACOS-PREVIEW.md). Les paramètres explicites lancent le mode CLI à la place de l'interface Textual.

**Consultation/diagnostic, sans paiement :**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**Les commandes suivantes peuvent provoquer de vrais paiements :**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

Contrairement à l'interface Textual, l'exécution isolée de `-Step 2..5` **n'affiche pas de deuxième demande de validation dans PowerShell**. Exécutez ces commandes uniquement si vous souhaitez réellement tenter un paiement et avez vérifié les conditions.

Séquence guidée via CLI :

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

Choix CLI : **1 = Continue (continuer), 2 = End run (terminer), 0 = Stop (arrêter)**. Vérifiez Google Play après chaque étape. `-StartStep 3` ne prouve pas la réussite des étapes antérieures.

Paramètres facultatifs :

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Utilisez uniquement un identifiant de périphérique réellement affiché par ADB. Évitez `-Force` : il désactive la vérification de correspondance du compte, mais **ne contourne pas** les conditions d'éligibilité ni les protections de paiement de Google.

## 5. Résultats et résolution des problèmes

- **MuMu/ADB introuvable :** vérifiez l'émulateur, root, l'autorisation ADB et l'état du périphérique.
- **Erreur Frida :** vérifiez les journaux, la version **16.5.9** et la compatibilité Android.
- **Aucune offre :** ouvrez Google One/Play Store et relancez **Step 1**.
- **Mauvais compte :** vérifiez le profil Google Play sans contourner le contrôle.
- **Paiement demandé :** ne signifie pas que l'abonnement a été activé ou prolongé ; vérifiez Google Play avant de réessayer.
- **Erreur de sécurité du paiement (ex. OR-REH-04) :** arrêtez les étapes de paiement et suivez les procédures officielles.

Les journaux se trouvent dans `logs/` et les rapports dans `ultra0-report/`. **Ne partagez pas de données non masquées contenant comptes, jetons ou informations de paiement.** Les tests automatisés de la CI utilisent des simulations et **ne vérifient aucun achat réel**. La compatibilité de paiement sur Mac/MuMu réel n'a pas été vérifiée.

## Assistance communautaire et projets associés

Si vous rencontrez des problèmes pour installer ou utiliser ePlus AI Toolkit, vous pouvez contacter la communauté et échanger des conseils sur la [publication d'assistance et de discussion Telegram d'ePlus](https://t.me/eplus_news/29). Pour les bugs reproductibles, vous pouvez aussi [ouvrir une issue GitHub](https://github.com/hoangsvit/google-ai/issues). **Ne publiez jamais de mots de passe, de codes OTP/2FA, de jetons d'offre ou d'achat, de journaux non anonymisés ou de données bancaires.** Il ne s'agit pas du support officiel de Google.

**Vous n'êtes pas éligible à l'offre Google AI Pro ?** Vous pouvez découvrir un autre projet communautaire d'ePlus.DEV : [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), pour [rechercher ou partager des codes d'invitation Muse](https://muse.eplus.dev/). **Muse est un service distinct** : ses invitations **ne donnent pas accès à Google AI Pro et ne remplacent pas** un abonnement Google AI Pro. La disponibilité des codes et les conditions géographiques ou de compte peuvent varier.

## Organisation du dépôt

Les scripts de démarrage et les modules Python principaux restent à la racine du projet pour éviter de casser les instructions existantes. Sous Windows, utilisez `run-all.ps1` ; sur Mac, `run-macos.sh`.

| Fichier ou dossier | Utilité |
| --- | --- |
| `run-all.ps1` | Démarre l'interface Textual ou le mode CLI de Windows |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | Lance et pilote les étapes 0–5 sur Mac ; paiements réels non vérifiés |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Modules Python actuellement utilisés |
| [`tools/windows/`](tools/windows/README.md) | Configuration manuelle facultative sous Windows |
| [`legacy/windows/`](legacy/windows/README.md) | Anciens scripts .bat ; certains utilisent `--force` pour ignorer la vérification du compte et peuvent provoquer de **vrais frais** |
| `scripts/`, `assets/` | Utilitaires et ressources Android/Frida |
| `tests/`, `.github/workflows/`, `docs/` | Tests, GitHub Actions et documentation |

## Documentation et contribution

[README anglais](README.md) · [Wiki Install](https://github.com/hoangsvit/google-ai/wiki/Install) · [Guide détaillé](docs/DETAILED-GUIDE.md) · [Étapes d'origine](docs/ORIGINAL-STEPS.md) · [Décharge](DISCLAIMER.md) · [Sécurité](SECURITY.md) · [Contribuer](CONTRIBUTING.md) · [Mentions légales](THIRD_PARTY_NOTICES.md)

Voir aussi [structure et maintenance](docs/PROJECT.md), [utilisation et CLI](docs/USAGE.md), [sécurité des paiements](docs/SAFETY.md), [notes historiques](docs/AUTHOR-NOTES.md) et [consignes pour agents](AGENTS.md). GitHub Actions vérifie Python, PowerShell, Textual et Frida/Billing au moyen de simulations, **sans véritables paiements**. Des tests CI réussis ne garantissent ni la compatibilité avec votre appareil ni l'éligibilité de votre compte.

## Crédits

**Auteur d'origine :** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Maintenance :** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). Les mentions MIT de l'auteur initial sont conservées dans `THIRD_PARTY_NOTICES.md`.

[Centre de documentation](docs/README.md) · [Guide historique en français](docs/i18n/README.fr.md) · [Sécurité des paiements](docs/SAFETY.md)
