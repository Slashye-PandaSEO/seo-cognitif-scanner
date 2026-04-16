#!/usr/bin/env python3
"""
Scanner SEO Cognitif V2 — Panda SEO
Analyse une page web à travers le prisme du marketing cognitif.
Score /100 avec recommandations actionnables.

V2 : PageSpeed API, Mobile check, SEO local, analyse émotionnelle,
     lisibilité cognitive, score de confiance, analyse concurrentielle.
"""

import re
import json
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
# CORS not needed on PythonAnywhere
from urllib.parse import urlparse

app = Flask(__name__)

# Links to Panda SEO articles for recommendations
PANDA_LINKS = {
    "vitesse": "https://panda-seo.fr/core-web-vitals-guide-complet/",
    "maillage": "https://panda-seo.fr/maillage-interne-seo/",
    "title": "https://panda-seo.fr/balise-title-seo/",
    "backlinks": "https://panda-seo.fr/backlinks-strategie/",
    "seo_local": "https://panda-seo.fr/seo-local-guide/",
    "schema": "https://panda-seo.fr/donnees-structurees-schema-org/",
    "audit": "https://panda-seo.fr/audit-seo-complet/",
    "contenu": "https://panda-seo.fr/redaction-seo-guide/",
    "cognitif": "https://panda-seo.fr/seo-cognitif/",
    "diagnostic": "https://lnkd.in/exZrBMYe",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# Google PageSpeed Insights (free, no key needed for basic)
PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeedInsights"


def fetch_page(url):
    if not url.startswith("http"):
        url = "https://" + url
    start = time.time()
    resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
    load_time = time.time() - start
    resp.raise_for_status()
    return resp.text, load_time, resp.url


def get_pagespeed_data(url):
    """Get real Core Web Vitals from Google PageSpeed Insights API."""
    try:
        resp = requests.get(PAGESPEED_API, params={
            "url": url,
            "strategy": "mobile",
            "category": "performance"
        }, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            lhr = data.get("lighthouseResult", {})
            audits = lhr.get("audits", {})
            perf_score = lhr.get("categories", {}).get("performance", {}).get("score", 0)

            # Extract Core Web Vitals
            lcp = audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
            cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0)
            fcp = audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000
            tbt = audits.get("total-blocking-time", {}).get("numericValue", 0)
            speed_index = audits.get("speed-index", {}).get("numericValue", 0) / 1000

            return {
                "score": int(perf_score * 100),
                "lcp": round(lcp, 1),
                "cls": round(cls, 3),
                "fcp": round(fcp, 1),
                "tbt": int(tbt),
                "speed_index": round(speed_index, 1),
                "available": True
            }
    except:
        pass
    return {"available": False}


def analyze_cognitive_seo(url):
    """Run full cognitive SEO analysis V2."""
    try:
        html, load_time, final_url = fetch_page(url)
    except Exception as e:
        return {"error": f"Impossible de charger la page : {str(e)}"}

    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(final_url).netloc
    page_text = soup.get_text().lower()
    body = soup.find("body")
    body_text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(body_text.split())

    results = {
        "url": final_url,
        "domain": domain,
        "score_total": 0,
        "grade": "",
        "categories": [],
        "quick_wins": [],
        "load_time": round(load_time, 2),
        "word_count": word_count,
        "version": "2.0",
    }

    categories = []

    # ================================================================
    # 1. VITESSE PERÇUE (Perte de contrôle) + PageSpeed API
    # ================================================================
    speed_score = 0
    speed_details = []
    speed_reco = []

    pagespeed = get_pagespeed_data(final_url)

    if pagespeed["available"]:
        ps_score = pagespeed["score"]
        speed_details.append(f"Score Google PageSpeed (mobile) : {ps_score}/100")
        speed_details.append(f"LCP : {pagespeed['lcp']}s | CLS : {pagespeed['cls']} | FCP : {pagespeed['fcp']}s")
        speed_details.append(f"TBT : {pagespeed['tbt']}ms | Speed Index : {pagespeed['speed_index']}s")

        if ps_score >= 90:
            speed_score = 10
            speed_details.append("✅ Performance excellente")
        elif ps_score >= 70:
            speed_score = 8
            speed_details.append("Bonne performance, quelques optimisations possibles")
        elif ps_score >= 50:
            speed_score = 5
            speed_reco.append(f"<strong>Problème :</strong> Score mobile {ps_score}/100 — ton site est perçu comme lent par le cerveau de tes visiteurs.")
            speed_reco.append(f"<strong>Pourquoi c'est critique :</strong> Au-delà de 3 secondes, le cerveau ressent une perte de contrôle. C'est biologique : comme quand une porte met trop de temps à s'ouvrir, tu fais demi-tour.")
            if pagespeed["lcp"] > 2.5:
                speed_reco.append(f"<strong>LCP à {pagespeed['lcp']}s — Comment corriger :</strong> 1) Compresse tes images en WebP (squoosh.app) 2) Mets les images sous la ligne de flottaison en lazy loading 3) Minimise le CSS critique")
            if pagespeed["cls"] > 0.1:
                speed_reco.append(f"<strong>CLS à {pagespeed['cls']} — Comment corriger :</strong> Les éléments bougent pendant le chargement. Le cerveau déteste l'instabilité. 1) Définis les dimensions width/height sur toutes tes images 2) Évite d'injecter du contenu dynamique au-dessus du fold")
        else:
            speed_score = 2
            speed_reco.append(f"<strong>🚨 URGENCE — Score mobile critique : {ps_score}/100</strong>")
            speed_reco.append("<strong>Ce qui se passe :</strong> Ton visiteur fuit avant même de voir ta page. Son cerveau perçoit la lenteur comme un signal de danger.")
            speed_reco.append("<strong>Comment corriger (par ordre de priorité) :</strong> 1) Compresse TOUTES tes images en WebP via squoosh.app 2) Supprime les plugins/scripts JavaScript non essentiels 3) Active la mise en cache navigateur 4) Active la compression GZIP côté serveur 5) Utilise un CDN (Cloudflare gratuit)")
            speed_reco.append(f'📖 <a href="{PANDA_LINKS["vitesse"]}" target="_blank">Lire le guide complet Core Web Vitals — Panda SEO</a>')
            results["quick_wins"].append(f"Vitesse mobile critique ({ps_score}/100) : le cerveau perçoit ton site comme une menace")
    else:
        # Fallback sur le temps de chargement mesuré
        speed_details.append(f"Temps de réponse serveur : {load_time:.1f}s")
        if load_time < 1.0:
            speed_score = 9
        elif load_time < 2.0:
            speed_score = 7
        elif load_time < 4.0:
            speed_score = 4
            speed_reco.append("Serveur lent. Vérifie ton hébergement.")
        else:
            speed_score = 2
            speed_reco.append("Temps de réponse critique. Change d'hébergeur ou active le cache.")
            results["quick_wins"].append("Serveur très lent : le cerveau abandonne")

    categories.append({
        "name": "Vitesse perçue",
        "icon": "⚡",
        "bias": "Perte de contrôle perçue",
        "bias_explain": "Au-delà de 3 secondes, le cerveau perçoit le site comme une menace. Comme quand t'attends trop au restaurant : tu te casses.",
        "score": speed_score,
        "max": 10,
        "details": speed_details,
        "recommendations": speed_reco,
    })

    # ================================================================
    # 2. TITRE H1 (Ancrage + Système 1)
    # ================================================================
    h1_score = 0
    h1_details = []
    h1_reco = []
    h1_tags = soup.find_all("h1")

    loss_words = ["erreur", "perdre", "éviter", "risque", "problème", "danger", "manquer", "sans", "ne pas", "stop", "arrête", "invisible", "coûter", "pire"]
    benefit_words = ["gratuit", "offert", "résultat", "augmenter", "booster", "gagner", "améliorer", "rapide", "simple", "facile", "meilleur", "guide", "comment"]

    if not h1_tags:
        h1_score = 0
        h1_details.append("❌ Aucun H1 trouvé")
        h1_reco.append("Le H1 est la première chose que le cerveau lit. Sans H1, pas d'ancrage.")
        results["quick_wins"].append("Pas de H1 : le cerveau sait pas de quoi parle ta page")
    elif len(h1_tags) > 1:
        h1_score = 4
        h1_details.append(f"⚠️ {len(h1_tags)} H1 trouvés — confusion cognitive")
        h1_reco.append("Plusieurs H1 = le cerveau sait pas quel est le sujet principal. Garde-en un seul.")
    else:
        h1_text = h1_tags[0].get_text(strip=True)
        h1_details.append(f"H1 : \"{h1_text}\"")
        h1_len = len(h1_text)

        if h1_len < 10:
            h1_score = 3
            h1_reco.append("H1 trop court. Le cerveau a besoin de contexte.")
        elif h1_len > 80:
            h1_score = 5
            h1_reco.append("H1 trop long. Le cerveau rapide lit en 3 secondes. Raccourcis.")
        else:
            h1_score = 7

        has_loss = any(w in h1_text.lower() for w in loss_words)
        has_benefit = any(w in h1_text.lower() for w in benefit_words)
        has_number = bool(re.search(r'\d+', h1_text))

        if has_loss:
            h1_score = min(h1_score + 2, 10)
            h1_details.append("✅ Active l'aversion à la perte")
        if has_benefit:
            h1_score = min(h1_score + 1, 10)
            h1_details.append("✅ Contient un bénéfice concret")
        if has_number:
            h1_score = min(h1_score + 1, 10)
            h1_details.append("✅ Contient un chiffre (effet d'ancrage)")
        if not has_loss and not has_benefit:
            h1_reco.append("<strong>Problème :</strong> Ton H1 est descriptif mais n'active aucune émotion. Le cerveau rapide (Système 1) décide en 3 secondes si ta page vaut le coup — et il se base sur le H1.")
            h1_reco.append(f"<strong>Comment corriger :</strong> Reformule ton H1 avec la formule : [Bénéfice concret] + [Pour qui] + [Preuve]. Ex : au lieu de \"{h1_text[:30]}...\", essaie quelque chose comme \"[Résultat] pour [ta cible] — [Preuve]\"")
            h1_reco.append("<strong>Astuce cognitive :</strong> Les mots de perte ('erreur', 'éviter', 'perdre', 'invisible') activent l'aversion à la perte — le cerveau réagit 2x plus fort que face à un bénéfice.")
            h1_reco.append(f'📖 <a href="{PANDA_LINKS["cognitif"]}" target="_blank">Comprendre le SEO cognitif — Panda SEO</a>')

    categories.append({
        "name": "Titre H1",
        "icon": "🎯",
        "bias": "Effet d'ancrage + Système 1",
        "bias_explain": "Le H1 est le premier message que le cerveau lit. Il ancre toute la perception de ta page.",
        "score": h1_score,
        "max": 10,
        "details": h1_details,
        "recommendations": h1_reco,
    })

    # ================================================================
    # 3. META TITLE (Aversion à la perte)
    # ================================================================
    title_score = 0
    title_details = []
    title_reco = []
    title_tag = soup.find("title")

    if not title_tag or not title_tag.string:
        title_score = 0
        title_details.append("❌ Aucun meta title")
        title_reco.append("Pas de title = Google choisit pour toi. Et il choisit mal.")
        results["quick_wins"].append("Pas de meta title : Google affiche n'importe quoi")
    else:
        title_text = title_tag.string.strip()
        title_details.append(f"Title : \"{title_text}\"")
        title_len = len(title_text)

        if title_len < 30:
            title_score = 4
            title_details.append(f"⚠️ {title_len} caractères — trop court")
            title_reco.append("Title trop court. Tu gaspilles de l'espace dans les résultats Google.")
        elif title_len > 65:
            title_score = 5
            title_details.append(f"⚠️ {title_len} caractères — sera tronqué")
            title_reco.append("Google va couper ton title. Le cerveau verra un message incomplet.")
        else:
            title_score = 7
            title_details.append(f"✅ {title_len} caractères — longueur optimale")

        has_loss = any(w in title_text.lower() for w in loss_words + ["invisible"])
        has_benefit = any(w in title_text.lower() for w in benefit_words)
        has_number = bool(re.search(r'\d+', title_text))
        has_brand = "|" in title_text or "—" in title_text or " - " in title_text

        if has_loss:
            title_score = min(title_score + 2, 10)
            title_details.append("✅ Active l'aversion à la perte")
        if has_benefit:
            title_score = min(title_score + 1, 10)
            title_details.append("✅ Contient un bénéfice")
        if has_number:
            title_score = min(title_score + 1, 10)
            title_details.append("✅ Contient un chiffre (ancrage)")
        if has_brand:
            title_details.append("✅ Marque présente")
        if not has_loss and not has_benefit:
            title_reco.append("<strong>Problème :</strong> Ton meta title est neutre. Il n'active aucune émotion dans les résultats Google. Le cerveau scrolle sans s'arrêter.")
            title_reco.append("<strong>Pourquoi :</strong> Le cerveau réagit 2x plus fort à la peur de perdre qu'à l'envie de gagner. 'Ne fais pas cette erreur' génère +34% de clics vs 'Voici nos conseils'.")
            title_reco.append(f"<strong>Comment corriger :</strong> Applique la formule [Mot-clé] + [Bénéfice ou Perte] + [Marque]. Ex : \"{title_text[:20]}\" → \"[Mot-clé] — Évite ces erreurs | [Ta marque]\"")
            title_reco.append(f'📖 <a href="{PANDA_LINKS["title"]}" target="_blank">Guide complet balise title SEO — Panda SEO</a>')

    categories.append({
        "name": "Meta Title",
        "icon": "📝",
        "bias": "Aversion à la perte",
        "bias_explain": "Le title est ton panneau d'autoroute. Le cerveau a 1 seconde pour décider s'il clique. 'Perdre' frappe plus fort que 'Gagner'.",
        "score": title_score,
        "max": 10,
        "details": title_details,
        "recommendations": title_reco,
    })

    # ================================================================
    # 4. META DESCRIPTION (Réciprocité + CTA)
    # ================================================================
    desc_score = 0
    desc_details = []
    desc_reco = []
    meta_desc = soup.find("meta", attrs={"name": "description"})

    if not meta_desc or not meta_desc.get("content"):
        desc_score = 0
        desc_details.append("❌ Aucune meta description")
        desc_reco.append("Sans description, Google prend un extrait random. Tu contrôles pas le message.")
        results["quick_wins"].append("Pas de meta description : Google décide ce qu'il montre")
    else:
        desc_text = meta_desc["content"].strip()
        desc_details.append(f"Description : \"{desc_text[:120]}{'...' if len(desc_text) > 120 else ''}\"")
        desc_len = len(desc_text)

        if desc_len < 70:
            desc_score = 4
        elif desc_len > 160:
            desc_score = 5
        else:
            desc_score = 7
        desc_details.append(f"Longueur : {desc_len} caractères {'✅' if 70 <= desc_len <= 160 else '⚠️'}")

        cta_words = ["découvrir", "essayer", "gratuit", "offert", "demander", "contacter", "réserver", "télécharger", "commencer", "profiter"]
        if any(w in desc_text.lower() for w in cta_words):
            desc_score = min(desc_score + 2, 10)
            desc_details.append("✅ Contient un appel à l'action")
        else:
            desc_reco.append("<strong>Problème :</strong> Pas de CTA dans ta meta description. Le cerveau a lu, mais il sait pas quoi faire ensuite.")
            desc_reco.append("<strong>Comment corriger :</strong> Ajoute un verbe d'action à la fin : 'Découvrez notre guide', 'Diagnostic gratuit', 'Essayez maintenant'. La réciprocité (offrir quelque chose) pousse le cerveau à cliquer.")
        if "?" in desc_text:
            desc_score = min(desc_score + 1, 10)
            desc_details.append("✅ Contient une question (engage le cerveau)")

    categories.append({
        "name": "Meta Description",
        "icon": "💬",
        "bias": "Réciprocité + CTA",
        "bias_explain": "La description doit donner envie. Une question engage le cerveau. Un CTA lui dit quoi faire.",
        "score": desc_score,
        "max": 10,
        "details": desc_details,
        "recommendations": desc_reco,
    })

    # ================================================================
    # 5. STRUCTURE COGNITIVE (Fluidité cognitive)
    # ================================================================
    struct_score = 0
    struct_details = []
    struct_reco = []

    h2_tags = soup.find_all("h2")
    h3_tags = soup.find_all("h3")

    if len(h2_tags) == 0:
        struct_score = 2
        struct_details.append("❌ Aucun H2 — pas de structure")
        struct_reco.append("<strong>Problème critique :</strong> Aucun sous-titre H2. Le cerveau voit un mur de texte et abandonne.")
        struct_reco.append("<strong>Pourquoi :</strong> Le cerveau scanne avant de lire. Il cherche des repères visuels (titres, listes, gras). Sans ça, c'est la surcharge cognitive — comme un supermarché sans panneaux.")
        struct_reco.append(f"<strong>Comment corriger :</strong> 1) Découpe ton contenu en sections logiques 2) Ajoute un H2 tous les 200-300 mots 3) Utilise des H3 pour les sous-points 4) Ajoute des listes à puces pour les énumérations")
        struct_reco.append(f'📖 <a href="{PANDA_LINKS["contenu"]}" target="_blank">Guide rédaction SEO cognitive — Panda SEO</a>')
        results["quick_wins"].append("Aucun H2 : contenu illisible pour le cerveau")
    elif len(h2_tags) < 3:
        struct_score = 5
        struct_details.append(f"{len(h2_tags)} H2 — structure légère")
        struct_reco.append("Le cerveau scanne avant de lire. Plus de sous-titres = meilleure navigation.")
    else:
        struct_score = 8
        struct_details.append(f"✅ {len(h2_tags)} H2 et {len(h3_tags)} H3 — bonne structure")

    struct_details.append(f"Contenu : ~{word_count} mots")
    if word_count < 300:
        struct_score = max(struct_score - 3, 0)
        struct_reco.append("Moins de 300 mots = pas crédible pour le cerveau.")
    elif word_count > 800:
        struct_score = min(struct_score + 1, 10)
        struct_details.append("✅ Contenu profond (autorité thématique)")

    # Readability: check paragraph length
    paragraphs = soup.find_all("p")
    long_p = [p for p in paragraphs if len(p.get_text(strip=True).split()) > 80]
    if long_p:
        struct_reco.append(f"{len(long_p)} paragraphe(s) trop longs. Les pavés créent une surcharge cognitive.")

    categories.append({
        "name": "Structure cognitive",
        "icon": "🧱",
        "bias": "Fluidité cognitive",
        "bias_explain": "Ce qui est facile à lire paraît plus crédible. Comme un supermarché bien rangé vs un bazar.",
        "score": struct_score,
        "max": 10,
        "details": struct_details,
        "recommendations": struct_reco,
    })

    # ================================================================
    # 6. PREUVE SOCIALE
    # ================================================================
    social_score = 0
    social_details = []
    social_reco = []

    review_signals = ["avis", "témoignage", "client", "étoile", "★", "⭐", "note", "recommand", "satisfaction", "confiance"]
    found_signals = [s for s in review_signals if s in page_text]

    if found_signals:
        social_score += 4
        social_details.append(f"✅ Signaux de preuve sociale : {', '.join(found_signals[:4])}")
    else:
        social_reco.append("<strong>Problème :</strong> Aucun signal de preuve sociale détecté sur la page. Le cerveau se dit : 'Personne fait confiance à ce site, pourquoi moi ?'")
        social_reco.append("<strong>Pourquoi c'est critique :</strong> La preuve sociale est le mécanisme le plus puissant du cerveau. C'est comme choisir un restaurant parce qu'il y a du monde dedans. Sans preuve, le cerveau hésite.")
        social_reco.append("<strong>Comment corriger :</strong> 1) Ajoute des témoignages clients avec prénom et photo 2) Affiche le nombre de clients/projets réalisés 3) Intègre des avis Google (plugin ou widget) 4) Ajoute des logos de partenaires/clients connus 5) Mets des étoiles/notes visibles")
        results["quick_wins"].append("Zéro preuve sociale visible")

    stats_pattern = re.compile(r'\d+\s*(%|\+|clients?|ans?|projets?|avis|entreprises?)', re.IGNORECASE)
    stats_found = stats_pattern.findall(body_text[:5000])
    if stats_found:
        social_score += 3
        social_details.append(f"✅ {len(stats_found)} chiffre(s) de crédibilité")
    else:
        social_reco.append("Aucun chiffre concret. Les chiffres ancrent la crédibilité.")

    img_alts = [img.get("alt", "").lower() for img in soup.find_all("img")]
    trust_words = ["logo", "partenaire", "certif", "badge", "client", "marque"]
    if any(any(tw in alt for tw in trust_words) for alt in img_alts):
        social_score += 3
        social_details.append("✅ Logos/badges de confiance détectés")

    social_score = min(social_score, 10)

    categories.append({
        "name": "Preuve sociale",
        "icon": "👥",
        "bias": "Preuve sociale",
        "bias_explain": "Si d'autres font confiance, le cerveau fait confiance. Comme choisir un restaurant parce qu'il y a du monde.",
        "score": social_score,
        "max": 10,
        "details": social_details,
        "recommendations": social_reco,
    })

    # ================================================================
    # 7. CTA (Réciprocité + Action)
    # ================================================================
    cta_score = 0
    cta_details = []
    cta_reco = []

    buttons = soup.find_all(["button", "a"])
    cta_keywords = ["contact", "devis", "gratuit", "essayer", "commencer", "réserver", "appeler",
                     "demander", "télécharger", "découvrir", "inscription", "acheter",
                     "commander", "diagnostic", "rdv", "rendez-vous", "audit"]

    cta_found = []
    for btn in buttons:
        btn_text = btn.get_text(strip=True).lower()
        if any(kw in btn_text for kw in cta_keywords):
            cta_found.append(btn_text[:50])

    if cta_found:
        cta_score = min(3 + len(cta_found) * 2, 10)
        cta_details.append(f"✅ {len(cta_found)} CTA : {', '.join(list(set(cta_found))[:4])}")
    else:
        cta_score = 1
        cta_details.append("❌ Aucun CTA clair")
        cta_reco.append("<strong>Problème :</strong> Aucun appel à l'action détecté. Le visiteur arrive sur ta page, lit... et ne sait pas quoi faire ensuite. Il part.")
        cta_reco.append("<strong>Pourquoi :</strong> Le cerveau a besoin d'un seul chemin clair. C'est le paradoxe du choix : trop d'options (ou zéro option) = paralysie.")
        cta_reco.append("<strong>Comment corriger :</strong> 1) Ajoute UN CTA principal visible en haut de page ('Demander un devis gratuit', 'Réserver un diagnostic') 2) Répète ce CTA en bas de page 3) Utilise un verbe d'action + un bénéfice ('Découvrir comment booster ton trafic') 4) Rends le bouton visuellement distinct (couleur contrastée)")
        results["quick_wins"].append("Pas de CTA : le visiteur sait pas quoi faire")

    if any(kw in page_text[:500] for kw in cta_keywords):
        cta_score = min(cta_score + 1, 10)
        cta_details.append("✅ CTA visible rapidement")
    elif cta_found:
        cta_reco.append("Ton CTA est trop bas. Le cerveau décide vite. Remonte-le.")

    categories.append({
        "name": "Appel à l'action",
        "icon": "🖱️",
        "bias": "Réciprocité + Paradoxe du choix",
        "bias_explain": "Le cerveau a besoin d'un seul chemin clair. Trop d'options = paralysie.",
        "score": cta_score,
        "max": 10,
        "details": cta_details,
        "recommendations": cta_reco,
    })

    # ================================================================
    # 8. IMAGES (Saillance visuelle)
    # ================================================================
    img_score = 0
    img_details = []
    img_reco = []
    images = soup.find_all("img")

    if not images:
        img_score = 2
        img_details.append("❌ Aucune image")
        img_reco.append("Le cerveau traite les images 60 000x plus vite que le texte.")
    else:
        img_score = 6
        img_details.append(f"{len(images)} image(s)")
        no_alt = [img for img in images if not img.get("alt", "").strip()]
        if no_alt:
            img_details.append(f"⚠️ {len(no_alt)} sans alt text")
            img_reco.append("Images sans alt = invisibles pour Google et les lecteurs d'écran.")
        else:
            img_score += 2
            img_details.append("✅ Toutes les images ont un alt text")
        if any(img.get("loading") == "lazy" for img in images):
            img_score = min(img_score + 2, 10)
            img_details.append("✅ Lazy loading actif")

    categories.append({
        "name": "Images",
        "icon": "🖼️",
        "bias": "Saillance visuelle",
        "bias_explain": "L'œil est attiré par ce qui se démarque. Les images captent l'attention avant le texte.",
        "score": img_score,
        "max": 10,
        "details": img_details,
        "recommendations": img_reco,
    })

    # ================================================================
    # 9. MAILLAGE INTERNE (Fluidité cognitive)
    # ================================================================
    link_score = 0
    link_details = []
    link_reco = []

    all_links = soup.find_all("a", href=True)
    internal_links = [a for a in all_links if domain in a.get("href", "") or (a.get("href", "").startswith("/") and not a.get("href", "").startswith("//"))]
    external_links = [a for a in all_links if a.get("href", "").startswith("http") and domain not in a.get("href", "")]

    content_areas = soup.find_all(["main", "article"])
    if not content_areas:
        content_areas = [div for div in soup.find_all("div") if div.find("p") and len(div.get_text(strip=True)) > 200]

    content_internal = 0
    if content_areas:
        for area in content_areas:
            area_links = [a for a in area.find_all("a", href=True) if domain in a.get("href", "") or (a.get("href", "").startswith("/") and not a.get("href", "").startswith("//"))]
            content_internal += len(area_links)

    total_internal = len(internal_links)
    link_details.append(f"{total_internal} lien(s) interne(s) au total")

    if total_internal == 0:
        link_score = 1
        link_reco.append("<strong>Problème :</strong> Aucun lien interne dans le contenu. Tes pages vivent en silo. Le cerveau du visiteur arrive, lit, et repart sans explorer.")
        link_reco.append("<strong>Pourquoi :</strong> Le cerveau fonctionne par associations. Quand il lit un sujet, il veut naturellement aller plus loin. Si tu proposes pas le chemin, il part. Google aussi a besoin de ces liens pour comprendre ta structure.")
        link_reco.append("<strong>Comment corriger :</strong> 1) Identifie tes 5 pages stratégiques (celles qui convertissent) 2) Dans chaque article/page, ajoute 3-5 liens vers ces pages 3) Utilise des ancres descriptives (pas 'cliquez ici' mais 'découvrir notre guide SEO local') 4) Crée des liens croisés entre articles du même thème")
        link_reco.append(f'📖 <a href="{PANDA_LINKS["maillage"]}" target="_blank">Guide complet maillage interne SEO — Panda SEO</a>')
        results["quick_wins"].append("Pas de maillage interne")
    elif total_internal < 5:
        link_score = 4
        link_reco.append("Très peu de liens internes. Ajoute des liens contextuels.")
    elif content_internal >= 3:
        link_score = 9
        link_details.append(f"✅ {content_internal} lien(s) dans le contenu principal")
    elif total_internal >= 10:
        link_score = 7
        link_details.append("✅ Bon maillage (navigation + contenu)")
    else:
        link_score = 5
        link_reco.append("Ajoute des liens dans tes textes, pas seulement dans le menu.")

    link_details.append(f"{len(external_links)} lien(s) externe(s)")

    categories.append({
        "name": "Maillage interne",
        "icon": "🔗",
        "bias": "Fluidité cognitive",
        "bias_explain": "Le cerveau fonctionne par associations. Quand il lit un sujet, il veut aller plus loin.",
        "score": link_score,
        "max": 10,
        "details": link_details,
        "recommendations": link_reco,
    })

    # ================================================================
    # 10. DONNÉES STRUCTURÉES (Saillance SERP)
    # ================================================================
    schema_score = 0
    schema_details = []
    schema_reco = []

    scripts = soup.find_all("script", type="application/ld+json")
    schema_types = []
    if scripts:
        schema_score = 7
        for s in scripts:
            try:
                data = json.loads(s.string)
                if isinstance(data, dict):
                    schema_types.append(data.get("@type", "?"))
                elif isinstance(data, list):
                    for item in data[:5]:
                        if isinstance(item, dict):
                            schema_types.append(item.get("@type", "?"))
            except:
                pass
        schema_details.append(f"✅ {len(scripts)} bloc(s) Schema.org : {', '.join(schema_types[:5])}")
    else:
        schema_score = 1
        schema_details.append("❌ Aucune donnée structurée")
        schema_reco.append("<strong>Problème :</strong> Aucune donnée structurée détectée. Ton résultat dans Google est basique — juste un titre et une description. Tu te fonds dans la masse.")
        schema_reco.append("<strong>Pourquoi :</strong> Les rich snippets (étoiles, FAQ, prix, horaires) font que ton résultat prend plus de place visuellement. L'œil est attiré par ce qui se démarque. Tu gagnes des clics sans changer de position.")
        schema_reco.append("<strong>Comment corriger :</strong> 1) Ajoute le schéma LocalBusiness si t'as un business local (adresse, tél, horaires) 2) Ajoute FAQPage si t'as une section FAQ 3) Ajoute Article pour tes articles de blog 4) Ajoute Product pour tes fiches produits 5) Teste sur search.google.com/test/rich-results")
        schema_reco.append(f'📖 <a href="{PANDA_LINKS["schema"]}" target="_blank">Guide complet données structurées — Panda SEO</a>')

    og_tags = soup.find_all("meta", property=re.compile(r"^og:"))
    if og_tags:
        schema_score = min(schema_score + 2, 10)
        schema_details.append(f"✅ {len(og_tags)} balises OpenGraph")
    else:
        schema_reco.append("Pas d'OpenGraph. Quand on partage ta page, elle s'affiche sans image.")

    # Check canonical
    canonical = soup.find("link", rel="canonical")
    if canonical:
        schema_details.append("✅ Canonical URL présente")
        schema_score = min(schema_score + 1, 10)

    categories.append({
        "name": "Données structurées",
        "icon": "🏷️",
        "bias": "Saillance visuelle SERP",
        "bias_explain": "Les rich snippets font que ton résultat prend plus de place. L'œil est attiré. Tu gagnes des clics sans changer de position.",
        "score": schema_score,
        "max": 10,
        "details": schema_details,
        "recommendations": schema_reco,
    })

    # ================================================================
    # 11. MOBILE (V2 NEW)
    # ================================================================
    mobile_score = 0
    mobile_details = []
    mobile_reco = []

    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        mobile_score += 5
        mobile_details.append("✅ Balise viewport présente")
    else:
        mobile_details.append("❌ Pas de balise viewport")
        mobile_reco.append("Sans viewport, ton site s'affiche mal sur mobile. 70% du trafic est mobile.")
        results["quick_wins"].append("Pas de viewport : ton site est cassé sur mobile")

    # Check responsive hints
    responsive_hints = soup.find_all("link", rel="stylesheet")
    media_queries = any("media" in str(link) for link in responsive_hints)

    # Check touch-friendly
    small_links = 0
    for a in soup.find_all("a"):
        style = a.get("style", "")
        if "font-size" in style and any(f"{n}px" in style for n in range(1, 12)):
            small_links += 1

    if viewport:
        mobile_score += 3
        mobile_details.append("✅ Site probablement responsive")

    if pagespeed.get("available") and pagespeed.get("score", 0) >= 50:
        mobile_score = min(mobile_score + 2, 10)
        mobile_details.append(f"✅ PageSpeed mobile : {pagespeed['score']}/100")
    elif pagespeed.get("available"):
        mobile_reco.append(f"Performance mobile faible ({pagespeed.get('score', 0)}/100). Le cerveau mobile est encore plus impatient.")

    categories.append({
        "name": "Mobile",
        "icon": "📱",
        "bias": "Impatience cognitive mobile",
        "bias_explain": "Sur mobile, le cerveau est encore plus impatient. 3 secondes c'est déjà trop. Et les pouces sont gros.",
        "score": mobile_score,
        "max": 10,
        "details": mobile_details,
        "recommendations": mobile_reco,
    })

    # ================================================================
    # 12. CONFIANCE ÉMOTIONNELLE (V2 NEW)
    # ================================================================
    trust_score = 0
    trust_details = []
    trust_reco = []

    # Check for contact info
    has_phone = bool(re.search(r'(\+33|0[1-9])[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}', page_text))
    has_email = bool(re.search(r'[\w.-]+@[\w.-]+\.\w+', page_text))
    has_address = any(w in page_text for w in ["adresse", "rue ", "avenue ", "boulevard ", "cedex", "besançon", "paris", "lyon", "marseille"])

    if has_phone:
        trust_score += 3
        trust_details.append("✅ Numéro de téléphone visible")
    else:
        trust_reco.append("<strong>Problème :</strong> Pas de numéro de téléphone visible. Le cerveau a besoin de savoir qu'un humain est derrière le site. Sans coordonnées, c'est perçu comme suspect.")
        trust_reco.append("<strong>Comment corriger :</strong> Affiche ton numéro dans le header ou le footer. Sur mobile, rends-le cliquable (lien tel:). Un téléphone visible augmente la confiance de +30%.")

    if has_email:
        trust_score += 2
        trust_details.append("✅ Email visible")

    if has_address:
        trust_score += 2
        trust_details.append("✅ Adresse/localisation mentionnée (biais de proximité)")
    else:
        trust_reco.append("Pas d'adresse visible. Le local rassure le cerveau.")

    # Check for HTTPS
    if final_url.startswith("https"):
        trust_score += 2
        trust_details.append("✅ HTTPS actif")
    else:
        trust_score = max(trust_score - 2, 0)
        trust_details.append("❌ Pas de HTTPS — signal de danger pour le cerveau")
        trust_reco.append("Sans HTTPS, le navigateur affiche 'Non sécurisé'. Le cerveau fuit immédiatement.")
        results["quick_wins"].append("Pas de HTTPS : ton site est marqué 'Non sécurisé'")

    # Check for legal pages
    legal_words = ["mention", "légal", "cgv", "cgu", "confidentialit", "rgpd", "cookie"]
    has_legal = any(w in page_text for w in legal_words)
    if has_legal:
        trust_score += 1
        trust_details.append("✅ Mentions légales/RGPD détectées")

    trust_score = min(trust_score, 10)

    categories.append({
        "name": "Confiance émotionnelle",
        "icon": "🛡️",
        "bias": "Biais de proximité + Confiance",
        "bias_explain": "Le cerveau cherche des signaux de confiance : un humain derrière le site, une adresse, un téléphone. Sans ça, il hésite.",
        "score": trust_score,
        "max": 10,
        "details": trust_details,
        "recommendations": trust_reco,
    })

    # ================================================================
    # 13. SCAN CTA AVANCÉ (V3 NEW)
    # ================================================================
    cta2_score = 0
    cta2_details = []
    cta2_reco = []

    # Find ALL clickable elements that look like CTAs
    all_buttons = soup.find_all("button")
    all_cta_links = []
    cta_kw = ["contact", "devis", "gratuit", "essayer", "commencer", "réserver", "appeler",
              "demander", "télécharger", "découvrir", "inscription", "acheter", "commander",
              "diagnostic", "rdv", "rendez-vous", "audit", "offert", "profiter", "tester",
              "s'inscrire", "en savoir", "voir", "consulter", "obtenir"]

    for el in soup.find_all(["a", "button"]):
        text = el.get_text(strip=True).lower()
        href = el.get("href", "")
        classes = " ".join(el.get("class", []))
        # Detect by text OR by class (btn, button, cta)
        is_btn_class = any(c in classes.lower() for c in ["btn", "button", "cta", "wp-block-button"])
        is_cta_text = any(kw in text for kw in cta_kw)
        if is_cta_text or (is_btn_class and len(text) > 2):
            all_cta_links.append({
                "text": text[:60],
                "href": href[:80],
                "tag": el.name,
                "is_button_style": is_btn_class,
            })

    cta2_details.append(f"{len(all_cta_links)} CTA détecté(s) sur la page")

    if len(all_cta_links) == 0:
        cta2_score = 1
        cta2_details.append("❌ Aucun CTA détecté")
        cta2_reco.append("<strong>Problème critique :</strong> Aucun bouton d'action sur ta page. Le visiteur lit mais ne sait pas quoi faire ensuite. Son cerveau a besoin d'un chemin clair.")
        cta2_reco.append("<strong>Comment corriger :</strong> 1) Ajoute UN CTA principal en haut de page 2) Répète-le en milieu et fin de page 3) Utilise un verbe d'action + bénéfice ('Obtenir mon diagnostic gratuit') 4) Fais-en un bouton visuellement distinct")
        results["quick_wins"].append("Aucun CTA : le visiteur ne sait pas quoi faire")
    else:
        # List CTAs found
        for i, cta in enumerate(all_cta_links[:5]):
            style = "bouton" if cta["is_button_style"] else "lien"
            cta2_details.append(f"   → [{style}] \"{cta['text']}\"")

        # Score based on quality
        has_btn_style = any(c["is_button_style"] for c in all_cta_links)
        has_action_verb = any(any(kw in c["text"] for kw in ["demander", "réserver", "obtenir", "télécharger", "diagnostic", "essayer"]) for c in all_cta_links)
        has_benefit = any(any(kw in c["text"] for kw in ["gratuit", "offert", "résultat", "guide"]) for c in all_cta_links)

        cta2_score = 4
        if has_btn_style:
            cta2_score += 2
            cta2_details.append("✅ Au moins un CTA stylisé en bouton")
        else:
            cta2_reco.append("<strong>Amélioration :</strong> Tes CTA sont des liens texte, pas des boutons. Un bouton visuellement distinct attire l'œil du cerveau. C'est la saillance visuelle.")

        if has_action_verb:
            cta2_score += 2
            cta2_details.append("✅ Verbe d'action dans le CTA")
        else:
            cta2_reco.append("<strong>Amélioration :</strong> Utilise un verbe d'action dans ton CTA ('Demander', 'Réserver', 'Obtenir'). Le cerveau a besoin qu'on lui dise QUOI faire, pas juste 'En savoir plus'.")

        if has_benefit:
            cta2_score += 2
            cta2_details.append("✅ Bénéfice dans le CTA (gratuit, offert)")
        else:
            cta2_reco.append("<strong>Amélioration :</strong> Ajoute un bénéfice dans ton CTA. 'Diagnostic gratuit' convertit mieux que 'Nous contacter'. La réciprocité : quand tu offres quelque chose, le cerveau se sent redevable.")

        # Check CTA position (above the fold = first 20% of content)
        body_str = str(soup.find("body") or "")
        total_len = len(body_str)
        first_cta_pos = None
        for cta in all_cta_links:
            pos = body_str.find(cta["text"][:20])
            if pos > 0 and (first_cta_pos is None or pos < first_cta_pos):
                first_cta_pos = pos

        if first_cta_pos and first_cta_pos < total_len * 0.25:
            cta2_details.append("✅ Premier CTA visible dans le premier quart de la page")
        elif first_cta_pos:
            cta2_reco.append("<strong>Amélioration :</strong> Ton premier CTA est trop bas. Le cerveau décide vite — s'il doit scroller pour trouver l'action, il part. Remonte un CTA en haut de page.")

        # Check number of different CTAs
        unique_texts = set(c["text"][:30] for c in all_cta_links)
        if len(unique_texts) > 4:
            cta2_reco.append(f"<strong>Attention :</strong> {len(unique_texts)} CTA différents détectés. Trop de choix = paralysie du cerveau. Concentre-toi sur 1-2 actions principales. (C'est le paradoxe du choix.)")

        cta2_score = min(cta2_score, 10)

    categories.append({
        "name": "Scan CTA avancé",
        "icon": "🎯",
        "bias": "Paradoxe du choix + Réciprocité",
        "bias_explain": "Le cerveau a besoin d'un chemin clair. Un seul CTA bien placé convertit mieux que 10 liens dispersés. Et offrir quelque chose (gratuit, guide) active la réciprocité.",
        "score": cta2_score,
        "max": 10,
        "details": cta2_details,
        "recommendations": cta2_reco,
    })

    # ================================================================
    # 14. SCAN BALISES COMPLET (V3 NEW)
    # ================================================================
    tag_score = 0
    tag_details = []
    tag_reco = []

    # Collect all heading tags
    all_h1 = soup.find_all("h1")
    all_h2 = soup.find_all("h2")
    all_h3 = soup.find_all("h3")
    all_h4 = soup.find_all("h4")
    all_h5 = soup.find_all("h5")
    all_h6 = soup.find_all("h6")

    tag_details.append(f"H1: {len(all_h1)} | H2: {len(all_h2)} | H3: {len(all_h3)} | H4: {len(all_h4)} | H5: {len(all_h5)} | H6: {len(all_h6)}")

    # --- H1 Analysis ---
    if len(all_h1) == 0:
        tag_score = 1
        tag_details.append("❌ Aucun H1")
        tag_reco.append("<strong>Problème critique :</strong> Pas de H1. Le cerveau et Google ne savent pas de quoi parle ta page. Le H1 est l'ancre cognitive de toute la page.")
        results["quick_wins"].append("Pas de H1 : ni le cerveau ni Google ne savent de quoi parle ta page")
    elif len(all_h1) > 1:
        tag_score = 4
        h1_texts = [h.get_text(strip=True)[:50] for h in all_h1]
        tag_details.append(f"⚠️ {len(all_h1)} H1 trouvés : {' | '.join(h1_texts)}")
        tag_reco.append(f"<strong>Problème :</strong> {len(all_h1)} H1 sur la page. Le cerveau a besoin d'UN sujet principal. Plusieurs H1 créent de la confusion cognitive. Garde-en un seul.")
    else:
        tag_score = 6
        h1_text = all_h1[0].get_text(strip=True)
        tag_details.append(f"✅ H1 unique : \"{h1_text[:60]}\"")

    # --- Hierarchy Check ---
    hierarchy_ok = True
    hierarchy_issues = []

    # Check if H3 exists without H2
    if len(all_h3) > 0 and len(all_h2) == 0:
        hierarchy_ok = False
        hierarchy_issues.append("H3 présents sans H2 parent — hiérarchie cassée")

    # Check if H4 exists without H3
    if len(all_h4) > 0 and len(all_h3) == 0:
        hierarchy_ok = False
        hierarchy_issues.append("H4 présents sans H3 parent — hiérarchie cassée")

    if hierarchy_ok and len(all_h2) >= 2:
        tag_score = min(tag_score + 2, 10)
        tag_details.append("✅ Hiérarchie des balises cohérente")
    elif not hierarchy_ok:
        tag_details.append("⚠️ Hiérarchie cassée")
        for issue in hierarchy_issues:
            tag_details.append(f"   → {issue}")
        tag_reco.append("<strong>Problème :</strong> La hiérarchie de tes balises est cassée (H3 sans H2, ou H4 sans H3). Le cerveau lit dans l'ordre : H1 → H2 → H3. Si tu sautes des niveaux, c'est comme un livre avec des chapitres dans le désordre.")
        tag_reco.append("<strong>Comment corriger :</strong> Restructure tes titres : H1 (sujet principal) → H2 (sections) → H3 (sous-sections). Ne saute jamais un niveau.")

    # --- Content in H2s ---
    if all_h2:
        h2_texts = []
        for h2 in all_h2:
            txt = h2.get_text(strip=True)
            if len(txt) > 3:
                h2_texts.append(txt[:50])
        if h2_texts:
            tag_details.append("📋 Tes H2 :")
            for t in h2_texts[:8]:
                tag_details.append(f"   → {t}")

            # Check for keyword richness in H2
            generic_h2 = [t for t in h2_texts if t.lower() in ["nos services", "à propos", "contact", "bienvenue", "accueil", "en savoir plus", "notre équipe", "nos valeurs"]]
            if generic_h2:
                tag_reco.append(f"<strong>Amélioration :</strong> {len(generic_h2)} H2 génériques détectés ({', '.join(generic_h2[:3])}). Tes H2 doivent contenir des mots-clés que tes clients tapent sur Google, pas des titres de menu.")

            # Check for emotional triggers in H2
            emotional_h2 = [t for t in h2_texts if any(w in t.lower() for w in ["comment", "pourquoi", "erreur", "éviter", "guide", "meilleur", "gratuit", "secret", "résultat"])]
            if emotional_h2:
                tag_score = min(tag_score + 1, 10)
                tag_details.append(f"✅ {len(emotional_h2)} H2 avec déclencheur cognitif")
            else:
                tag_reco.append("<strong>Amélioration :</strong> Tes H2 sont informatifs mais n'activent aucune émotion. Ajoute des mots déclencheurs : 'Comment', 'Pourquoi', 'Erreur à éviter', 'Guide complet'. Le cerveau est attiré par les questions et les promesses.")

    # --- Duplicate headings ---
    all_heading_texts = [h.get_text(strip=True).lower() for h in soup.find_all(["h1", "h2", "h3"])]
    duplicates = [t for t in set(all_heading_texts) if all_heading_texts.count(t) > 1 and len(t) > 5]
    if duplicates:
        tag_details.append(f"⚠️ {len(duplicates)} titre(s) dupliqué(s)")
        tag_reco.append(f"<strong>Problème :</strong> Titres dupliqués détectés : {', '.join(d[:30] for d in duplicates[:3])}. Chaque titre doit être unique. Les doublons créent de la confusion pour le cerveau et pour Google.")

    # --- Empty headings ---
    empty_headings = [h.name for h in soup.find_all(["h1", "h2", "h3", "h4"]) if not h.get_text(strip=True)]
    if empty_headings:
        tag_details.append(f"❌ {len(empty_headings)} balise(s) vide(s)")
        tag_reco.append(f"<strong>Problème :</strong> {len(empty_headings)} balise(s) titre vide(s). Une balise vide pollue le code et perturbe Google.")

    tag_score = min(tag_score, 10)

    categories.append({
        "name": "Scan balises complet",
        "icon": "🏗️",
        "bias": "Fluidité cognitive + Ancrage",
        "bias_explain": "Les balises titres sont la colonne vertébrale de ta page. Le cerveau les scanne en premier pour décider si le contenu vaut la peine d'être lu. Google aussi.",
        "score": tag_score,
        "max": 10,
        "details": tag_details,
        "recommendations": tag_reco,
    })

    # ================================================================
    # SCORE FINAL
    # ================================================================
    total = sum(c["score"] for c in categories)
    max_total = sum(c["max"] for c in categories)
    score_100 = int(total / max_total * 100)

    if score_100 >= 80:
        grade = "A"
        grade_text = "Excellent. Ton site parle au cerveau de tes visiteurs."
        grade_emoji = "🏆"
    elif score_100 >= 65:
        grade = "B"
        grade_text = "Correct. Quelques ajustements cognitifs et ça décolle."
        grade_emoji = "👍"
    elif score_100 >= 45:
        grade = "C"
        grade_text = "Moyen. Ton site a du potentiel, mais le cerveau hésite."
        grade_emoji = "⚠️"
    elif score_100 >= 25:
        grade = "D"
        grade_text = "Faible. Ton site ne parle pas au cerveau de tes clients."
        grade_emoji = "🔴"
    else:
        grade = "F"
        grade_text = "Critique. Ton site fait fuir le cerveau de tes visiteurs."
        grade_emoji = "🚨"

    results["score_total"] = score_100
    results["grade"] = grade
    results["grade_text"] = grade_text
    results["grade_emoji"] = grade_emoji
    results["categories"] = categories
    results["pagespeed"] = pagespeed

    if not results["quick_wins"]:
        results["quick_wins"] = ["Pas de problème critique. Optimise les catégories en orange."]

    return results


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL manquante"}), 400
    results = analyze_cognitive_seo(url)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
