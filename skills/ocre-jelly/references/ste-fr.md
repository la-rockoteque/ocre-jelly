# Autorité rédactionnelle : français clair et rationalisé

Pour la prose en français, ocre-jelly suit ces règles. Elles reformulent dans nos mots trois sources : les principes de la norme ISO 24495-1:2023 (*Langage clair et simple*), l'approche du Français Rationalisé du GIFAS (le pendant français de STE100 pour la documentation technique) et les avis de l'OQLF (Banque de dépannage linguistique, Grand dictionnaire terminologique). Aucune de ces sources n'est reproduite. Comme pour l'anglais, les règles de préservation du SKILL.md l'emportent sur ce fichier : on ne change jamais un fait pour respecter une règle de style.

## Mots

- Employez le mot courant et concret, avec un seul sens : « utiliser », pas « faire usage de » ; « commencer », pas « procéder au démarrage de ».
- Gardez un seul terme par concept dans tout le texte. Ne passez pas de « réquisition » à « demande », puis à « commande », pour la même chose. Le glossaire du projet (colonne *Term* ou *UI label (fr-CA)*) fixe le terme.
- Les noms techniques (pièces, logiciels, unités, noms de code) sont permis tels quels. Ne les traduisez pas et ne les simplifiez pas.
- Remplacez les tournures lourdes par le mot simple :
  - « afin de » devient « pour » ;
  - « dans le cadre de » devient « pour » ou « dans » ;
  - « être en mesure de » devient « pouvoir » ;
  - « procéder à la vérification » devient « vérifier » ;
  - « de manière efficace » devient « efficacement ».
- Évitez les chaînes de noms : « la mise en place de la gestion des accès » devient « gérer les accès ».

## Verbes

- Préférez la voix active : « Le système envoie le courriel », pas « Le courriel est envoyé par le système ».
- Employez le verbe, pas le nom qui en dérive : « valider la ligne », pas « effectuer la validation de la ligne ».
- Temps simples : présent, passé composé, futur simple, impératif, infinitif.
- Limitez le participe présent, et surtout le participe présent en fin de phrase (« …, permettant ainsi de… »). Faites plutôt une deuxième phrase.

## Phrases

- Une idée par phrase.
- Une consigne fait au plus 20 mots. Une phrase descriptive fait au plus 25 mots. Le français est un peu plus long que l'anglais, donc un dépassement de quelques mots peut rester, mais au-delà, coupez.
- Ne supprimez pas les articles ni les verbes pour raccourcir : « Fermez la vanne », pas « Fermer vanne ».
- Faites une liste verticale quand une phrase aligne plusieurs éléments ou étapes.

## Consignes (procédures)

- Employez l'impératif (« Serrez le boulon. ») ou l'infinitif, selon la convention du document. N'alternez pas entre les deux.
- Une consigne par phrase. Mettez la condition avant l'action : « Si le voyant est rouge, arrêtez la pompe. »
- Un avertissement commence par l'ordre, puis donne le risque : « Coupez le courant. La haute tension peut tuer. »

## Descriptions

- Mettez l'information importante en premier.
- Un sujet par paragraphe, au plus six phrases.
- Reliez les phrases par des mots de liaison clairs (« donc », « car », « ensuite », « mais »), pas par des formules creuses (« Il convient de noter que », « Force est de constater que »).

## Variantes régionales

Le module de langue régional (`locales/fr-CA.py`, `fr-FR.py`, `fr-BE.py`, `fr-CH.py`) fixe le vocabulaire et la typographie. Tous les signalements régionaux sont souples (*soft*), car le registre et le public décident.
- **fr-CA** : l'usage de l'OQLF. Écrivez « courriel », « clavarder », « fin de semaine », « stationnement », « balado », « infonuagique », « téléverser ». Évitez les anglicismes critiqués : « céduler », « faire du sens », « à l'effet que », « adresser un problème », « en termes de ». Pour la typographie, mettez une espace avant le deux-points seulement.
- **fr-FR** : les recommandations de FranceTerme (« courriel », « mot-dièse », « informatique en nuage »). Mettez une espace insécable avant « ; : ! ? ».
- **fr-BE / fr-CH** : « septante », « nonante » (et « huitante » dans une partie de la Suisse romande).

## Chaînes d'interface (UI)

- Une chaîne d'interface suit les mêmes règles, avec une contrainte de plus : l'espace est limité. Gardez le libellé du glossaire (*UI label*) mot pour mot.
- Ne touchez jamais aux clés, aux variables (`{{count}}`, `{name}`, `%s`), aux balises ni à la ponctuation qui les entoure.
- Les boutons sont à l'infinitif (« Enregistrer », « Annuler »). Les messages disent quoi faire ensuite.

## À ne pas confondre avec une faute

- Un anglicisme accepté par l'OQLF (« réaliser » au sens de *se rendre compte*, « opportunité » au sens d'*occasion favorable*, « présentement ») n'est pas une faute.
- Une phrase longue mais claire peut rester en mode audit. Signalez-la ; coupez-la seulement en mode réécriture.
- Le texte cité, le code, les libellés entre « guillemets » et le texte attribué ne sont jamais réécrits.
