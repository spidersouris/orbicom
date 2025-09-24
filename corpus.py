import json
import os
import re

from sentence_splitter import split_text_into_sentences


def load_corpus(level, corpus_type, extract=False):
    if level not in ["ce1", "cm1"]:
        raise ValueError(f"level must be one of ['ce1', 'cm1'], got {level}")

    if corpus_type not in ["literature", "scientific"]:
        raise ValueError(
            f"corpus_type must be one of ['literature', 'scientific'], got {corpus_type}"
        )

    corpus_path = f"data/{level}/"
    corpus_data = {}

    pattern = r"^\d+_(\w+_)?lit" if corpus_type == "literature" else r"^\d+_(\w+_)?sci"

    for fl in os.listdir(corpus_path):
        if re.match(pattern, fl):
            with open(os.path.join(corpus_path, fl), "r") as f:
                if extract:
                    corpus_data[fl] = " ".join(
                        split_text_into_sentences(f.read(), language="fr")[0:2]
                    )
                else:
                    corpus_data[fl] = f.read()

    return corpus_data


def get_all_extracts():
    extracts = {
        "ce1_lit": get_extracts("ce1", "literature"),
        "cm1_lit": get_extracts("cm1", "literature"),
        "ce1_sci": get_extracts("ce1", "scientific"),
        "cm1_sci": get_extracts("cm1", "scientific"),
    }

    return extracts


def get_extracts(level, corpus_type):
    if level not in ["ce1", "cm1"]:
        raise ValueError(f"level must be one of ['ce1', 'cm1'], got {level}")

    if corpus_type not in ["literature", "scientific"]:
        raise ValueError(
            f"corpus_type must be one of ['literature', 'scientific'], got {corpus_type}"
        )

    extracts = load_corpus(level, corpus_type, extract=True)

    sorted_extracts = {
        key: value.replace("\t", "") for key, value in sorted(extracts.items())
    }

    return json.dumps(sorted_extracts, indent=2, ensure_ascii=False)


def get_examples(gen_type: str, text_type: str, level: str) -> list[str]:
    if text_type == "literature":
        return get_lit_examples(gen_type, level)
    elif text_type == "scientific":
        return get_sci_examples(gen_type, level)

    return []


def get_lit_examples(gen_type: str, level: str) -> list[str]:
    if gen_type == "continuation" and level == "cm1":
        return [
            """
    Extrait : « À l’occasion du baptême de la princesse, le roi et la reine organisent une fête somptueuse, invitant famille, amis et sept fées marraines (ou trois fées selon les versions) bienveillantes de l’enfant. »
    Suite : « Heureusement, une des jeunes fées marraines, qui s’était cachée pour parler en dernier, atténue la malédiction : « Au lieu d’en mourir, elle tombera seulement dans un profond sommeil qui durera cent ans, au terme desquels le fils d’un roi viendra la réveiller. »
    Pour protéger sa fille, le roi fait immédiatement interdire de filer au fuseau ou d’en posséder sous peine de mort. Pourtant, vers ses quinze ans, dans une partie reculée du château, la princesse découvre une vieille fileuse qui ne connaît pas l’interdiction. Elle se pique aussitôt au fuseau et s’endort, en même temps que tous les habitants du château.
    Au cours des ans, celui-ci est recouvert de végétation. Il n’est redécouvert qu’après cent ans, lorsqu’un fils de roi y pénètre et réveille la princesse. Deux ans plus tard, la princesse et le prince eurent deux enfants : Aurore et Jour. Malheureusement, le prince et le roi partirent à la guerre. La princesse resta donc au château avec la belle-reine, laquelle était issue d’une famille d’ogres. La reine demanda au maître d’hôtel de lui préparer le fils Jour en guise de déjeuner et la petite Aurore en guise de dîner. Mais le maître d’hôtel, homme de très bon cœur, cacha les enfants et servit de la viande animale à la belle-reine. »
    """,  # noqa: E501
            """
    Extrait : « Harry, sous le choc de la mort de son parrain Sirius, ne reste que 15 jours chez les Dursley. »
    Suite : « En effet, Dumbledore vient le chercher pour qu'il l'aide à convaincre Horace Slughorn, un ancien professeur de potions et directeur de la maison de Serpentard, de reprendre son poste d'enseignant à Poudlard. Slughorn, qui se cache car les Mangemorts le recherchent, est un peu vaniteux et aime s'entourer de personnes célèbres : il ne résiste pas à la tentation d'avoir Harry comme élève et accepte donc la proposition. Harry est ensuite emmené chez les Weasley pour y finir ses vacances. »
    """,  # noqa: E501
        ]
    elif gen_type == "generation" and level == "cm1":
        return [
            """
    Texte : À l’occasion du baptême de la princesse, le roi et la reine organisent une fête somptueuse, invitant famille, amis et sept fées marraines (ou trois fées selon les versions) bienveillantes de l’enfant. Chacune d’elles offre un don à la princesse : beauté, grâce, etc. Brusquement, une vieille fée, qui n’a pas été invitée, se présente et lance à la princesse un charme mortel : la princesse se piquera le doigt sur le fuseau d’un rouet et en mourra.
    Heureusement, une des jeunes fées marraines, qui s’était cachée pour parler en dernier, atténue la malédiction : « Au lieu d’en mourir, elle tombera seulement dans un profond sommeil qui durera cent ans, au terme desquels le fils d’un roi viendra la réveiller. »
    Pour protéger sa fille, le roi fait immédiatement interdire de filer au fuseau ou d’en posséder sous peine de mort. Pourtant, vers ses quinze ans, dans une partie reculée du château, la princesse découvre une vieille fileuse qui ne connaît pas l’interdiction. Elle se pique aussitôt au fuseau et s’endort, en même temps que tous les habitants du château.
    Au cours des ans, celui-ci est recouvert de végétation. Il n’est redécouvert qu’après cent ans, lorsqu’un fils de roi y pénètre et réveille la princesse. Deux ans plus tard, la princesse et le prince eurent deux enfants : Aurore et Jour. Malheureusement, le prince et le roi partirent à la guerre. La princesse resta donc au château avec la belle-reine, laquelle était issue d’une famille d’ogres. La reine demanda au maître d’hôtel de lui préparer le fils Jour en guise de déjeuner et la petite Aurore en guise de dîner. Mais le maître d’hôtel, homme de très bon cœur, cacha les enfants et servit de la viande animale à la belle-reine.
    """,  # noqa: E501
            """
    Texte : Harry, sous le choc de la mort de son parrain Sirius, ne reste que 15 jours chez les Dursley. En effet, Dumbledore vient le chercher pour qu'il l'aide à convaincre Horace Slughorn, un ancien professeur de potions et directeur de la maison de Serpentard, de reprendre son poste d'enseignant à Poudlard. Slughorn, qui se cache car les Mangemorts le recherchent, est un peu vaniteux et aime s'entourer de personnes célèbres : il ne résiste pas à la tentation d'avoir Harry comme élève et accepte donc la proposition. Harry est ensuite emmené chez les Weasley pour y finir ses vacances.
    """,  # noqa: E501
        ]

    elif gen_type == "continuation" and level == "ce1":
        return [
            """
    Extrait : « C’est l’histoire d’un Roi et d’une Reine qui voulaient un enfant car ils n’en avaient pas. »
    Suite : « Ils allaient à toutes les eaux du monde, vœux, pèlerinage, menues dévotions, tout fut mis en œuvre, mais rien n’y faisait. Mais un jour, la Reine devient grosse et elle accoucha d’une fille. On lui donna pour marraines toutes les fées du pays. Chacune des fées donna un don à la Princesse. La vieille fée lui jeta un mauvais sort, qu’elle se percerait la main d’un fuseau, et qu’elle en mourrait. Une jeune Fée modifia le mauvais don : la Princesse se percera la main d’un fuseau, mais au lieu d’en mourir elle dormira pendant cent ans. La Princesse se perça la main et tomba d’évanouissement. La Fée qui lui avait sauvé la vie en lui donnant le don de dormir cent ans réussit aussi à endormir tous les habitants du château.
    Cent ans plus tard, le Prince réveilla la Princesse qui était dans le château et toutes les autres personnes aussi. Le Prince et la Princesse eurent deux enfants dont la première Aurore et le second un fils qui se nomme Jour. Le Prince s’en alla à la guerre. La Reine Mère alla voir son Maître d’Hôtel et lui demanda pour le dîner la petite Aurore, le petit Jour et la Princesse. La Princesse, Aurore et Jour sont sous protection dans la loge du Maître d’Hôtel. Le Prince arriva dans la Cour et l’Ogresse, enragée, se jette dans la cuve. »
    """,  # noqa: E501
            """
    Extrait : « Le Premier Ministre Moldu s'apprête à rencontrer Cornelius Fudge (ministre de la Magie). »
    Suite : « Fudge explique au Premier Ministre que Voldemort est de retour et que tous les crimes et les accidents étranges du monde des Moldus sont liés à lui. Bellatrix Lestrange et Narcissa Malefoy se rendent chez Severus Rogue, à qui Narcissa raconte que le Seigneur des Ténèbres a confié une tâche à son fils Drago. Pensant qu'il ne peut accomplir ce travail seul, elle fait un Serment Inviolable avec Rogue : il doit promettre d'aider Drago et de faire la mission à sa place si celui-ci échoue.
    Harry Potter, lui, quitte Privet Drive avec Albus Dumbledore. Il remarque que le directeur a la main brûlée et noircie, mais Dumbledore refuse de lui expliquer pourquoi. Ils se rendent chez Horace Slughorn, un ancien professeur de potions, pour le convaincre de reprendre son poste. Après avoir parlé de Lily, la mère de Harry, à ce dernier, il accepte finalement de quitter sa retraite. Dumbledore emmène Harry au Terrier où il va passer la fin de l'été avec les Weasley.
    Avant la rentrée, Harry et les Weasley vont au Chemin de Traverse pour acheter des fournitures. Ils visitent le magasin de farces et attrapes des jumeaux Fred et George, puis Ron, Hermione et Harry aperçoivent Drago Malefoy qui se dirige vers la boutique de magie noire, Barjow et Beurk. Ils l'espionnent et entendent Malefoy demander à Barjow de ne pas vendre un certain objet, en le menaçant de quelque chose sur son bras, que Harry interprète comme la Marque des Ténèbres. Il conclut que Malefoy est un Mangemort, mais Ron et Hermione trouvent cette théorie impossible.
    Dans le Poudlard Express, Harry se glisse dans le compartiment de Malefoy et ses amis, sous sa cape d'invisibilité. Malefoy confie à ses amis que Lui (Voldemort) l'a choisi pour une mission à Poudlard. Manque de chance, Malefoy s'aperçoit de la présence de Harry dans le train et lui jette le maléfice du Saucisson. Heureusement, Nymphadora Tonks, qui a l'air très triste et qui a changé de Patronus, vient le libérer.
    À Poudlard, Harry devient brillant en cours de potions, à présent assurés par Slughorn (la Défense contre les Forces du Mal est reprise par Rogue). Harry a en fait déniché un livre de potions couvert de petites notes écrites à la main par le mystérieux Prince de Sang-Mêlé. Ces petites notes aident Harry à préparer des potions parfaites, ce qui lui permet de gagner un flacon de Felix Felicis, une potion qui porte chance. Harry découvre aussi ses sentiments envers Ginny Weasley, la sœur de Ron, car l'Amortentia (une potion qui prend l'odeur de ce qu'on aime le plus) a l'odeur du parfum de Ginny quand il la respire. »
    """,  # noqa: E501
        ]
    elif gen_type == "generation" and level == "ce1":
        return [
            """
    Texte : C’est l’histoire d’un Roi et d’une Reine qui voulaient un enfant car ils n’en avaient pas. Ils allaient à toutes les eaux du monde, vœux, pèlerinage, menues dévotions, tout fut mis en œuvre, mais rien n’y faisait. Mais un jour, la Reine devient grosse et elle accoucha d’une fille. On lui donna pour marraines toutes les fées du pays. Chacune des fées donna un don à la Princesse. La vieille fée lui jeta un mauvais sort, qu’elle se percerait la main d’un fuseau, et qu’elle en mourrait. Une jeune Fée modifia le mauvais don : la Princesse se percera la main d’un fuseau, mais au lieu d’en mourir elle dormira pendant cent ans. La Princesse se perça la main et tomba d’évanouissement. La Fée qui lui avait sauvé la vie en lui donnant le don de dormir cent ans réussit aussi à endormir tous les habitants du château.
    Cent ans plus tard, le Prince réveilla la Princesse qui était dans le château et toutes les autres personnes aussi. Le Prince et la Princesse eurent deux enfants dont la première Aurore et le second un fils qui se nomme Jour. Le Prince s’en alla à la guerre. La Reine Mère alla voir son Maître d’Hôtel et lui demanda pour le dîner la petite Aurore, le petit Jour et la Princesse. La Princesse, Aurore et Jour sont sous protection dans la loge du Maître d’Hôtel. Le Prince arriva dans la Cour et l’Ogresse, enragée, se jette dans la cuve.
    """,  # noqa: E501
            """
    Texte : Le Premier Ministre Moldu s'apprête à rencontrer Cornelius Fudge (ministre de la Magie). Fudge explique au Premier Ministre que Voldemort est de retour et que tous les crimes et les accidents étranges du monde des Moldus sont liés à lui. Bellatrix Lestrange et Narcissa Malefoy se rendent chez Severus Rogue, à qui Narcissa raconte que le Seigneur des Ténèbres a confié une tâche à son fils Drago. Pensant qu'il ne peut accomplir ce travail seul, elle fait un Serment Inviolable avec Rogue : il doit promettre d'aider Drago et de faire la mission à sa place si celui-ci échoue.
    Harry Potter, lui, quitte Privet Drive avec Albus Dumbledore. Il remarque que le directeur a la main brûlée et noircie, mais Dumbledore refuse de lui expliquer pourquoi. Ils se rendent chez Horace Slughorn, un ancien professeur de potions, pour le convaincre de reprendre son poste. Après avoir parlé de Lily, la mère de Harry, à ce dernier, il accepte finalement de quitter sa retraite. Dumbledore emmène Harry au Terrier où il va passer la fin de l'été avec les Weasley.
    Avant la rentrée, Harry et les Weasley vont au Chemin de Traverse pour acheter des fournitures. Ils visitent le magasin de farces et attrapes des jumeaux Fred et George, puis Ron, Hermione et Harry aperçoivent Drago Malefoy qui se dirige vers la boutique de magie noire, Barjow et Beurk. Ils l'espionnent et entendent Malefoy demander à Barjow de ne pas vendre un certain objet, en le menaçant de quelque chose sur son bras, que Harry interprète comme la Marque des Ténèbres. Il conclut que Malefoy est un Mangemort, mais Ron et Hermione trouvent cette théorie impossible.
    Dans le Poudlard Express, Harry se glisse dans le compartiment de Malefoy et ses amis, sous sa cape d'invisibilité. Malefoy confie à ses amis que Lui (Voldemort) l'a choisi pour une mission à Poudlard. Manque de chance, Malefoy s'aperçoit de la présence de Harry dans le train et lui jette le maléfice du Saucisson. Heureusement, Nymphadora Tonks, qui a l'air très triste et qui a changé de Patronus, vient le libérer.
    À Poudlard, Harry devient brillant en cours de potions, à présent assurés par Slughorn (la Défense contre les Forces du Mal est reprise par Rogue). Harry a en fait déniché un livre de potions couvert de petites notes écrites à la main par le mystérieux Prince de Sang-Mêlé. Ces petites notes aident Harry à préparer des potions parfaites, ce qui lui permet de gagner un flacon de Felix Felicis, une potion qui porte chance. Harry découvre aussi ses sentiments envers Ginny Weasley, la sœur de Ron, car l'Amortentia (une potion qui prend l'odeur de ce qu'on aime le plus) a l'odeur du parfum de Ginny quand il la respire.
    """,  # noqa: E501
        ]

    return []


def get_sci_examples(gen_type: str, level: str) -> list[str]:
    if gen_type == "continuation" and level == "cm1":
        return [
            """
    Extrait : « Manchot est un nom vernaculaire désignant en français des oiseaux marins de l'hémisphère austral, incapables de voler à cause de leur adaptation à la vie aquatique. »
    Suite : « Ce terme désigne spécifiquement plusieurs espèces de la famille des Spheniscidae à laquelle appartiennent aussi les gorfous « manchots à aigrettes ».
    Les ailes des manchots, devenues inutilisables pour le vol, se seraient, par contre, merveilleusement adaptées à la nage et à la plongée : le Manchot papou peut atteindre 35 km/h à la nage (contre 9 km/h pour le meilleur nageur olympique) et le Manchot empereur peut plonger à plus de 520 m pour rechercher de la nourriture, soit le record absolu chez tous les oiseaux.
    Le cri des manchots est appelé braiement ou jabotement.
    Les différentes espèces de manchots sont souvent appelées par confusion « pingouins » dans le langage courant, à la fois à cause d'une ressemblance physique et à cause d'une ressemblance lexicale entre ce mot et la racine désignant Manchot dans la plupart des langues voisines du français.
    """,  # noqa: E501
            """
    Extrait : « L'Amazone (en espagnol Río Amazonas, en portugais Rio Amazonas) est un fleuve d'Amérique du Sud. Son débit moyen de 209 000 m3/s2 est de loin le plus élevé de tous les fleuves de la planète et équivaut au volume cumulé des six fleuves qui le suivent immédiatement dans l'ordre des débits. »
    Suite : « Avec environ 6 500 km, c'est le plus long fleuve de la Terre avec le Nil. L'Amazone est aussi le plus grand fleuve par l'immensité de son bassin. Il draine une surface de 6 112 000 km² (sans le Tocantins) soit 40 % de l'Amérique du Sud et l'équivalent d'une fois et demie la surface de l'Union européenne (le Congo, deuxième fleuve pour la superficie de son bassin atteint seulement 3,8 millions de km²). Le bassin  prend sa source dans les Andes et se jette dans l'océan Atlantique. Après avoir traversé le Pérou, la Colombie et le Brésil, il se jette dans l'océan Atlantique au niveau de l'équateur. Son réseau hydrographique compte plus de 1000 cours d'eau. L'Amazone est à lui seul à l'origine de 18% du volume total d'eau douce déversée dans les océans du monde. Ses deux principaux affluents, le Madeira et le Rio Negro font eux-mêmes partie des 10 plus importants cours d'eau du monde par leurs débits (32 000 et 29 300 m3/s), et le 3e (rio Japura, 18 600 m3/s) rivalise avec le Mississippi.
    La démesure de l'Amazone s'apprécie aussi en constatant qu'aucun pont ni barrage ne le franchit sur des milliers de kilomètres (la traversée se fait en bac ou ferry), et qu'il faut remonter très haut sur ses deux formateurs Marañón et Ucayali pour trouver de tels aménagements. Tout s'y oppose: la largeur du fleuve, sa profondeur, sa puissance, la multitude d'îles et de bras fluviaux, les berges inondées plusieurs mois par an et remodelées à chaque crue. La technique d'aujourd'hui ne permet pas de s'affranchir de telles difficultés. C'est pourquoi les actuels projets de barrages ne concernent que les affluents (rio Madeira, rio Xingu). S'ils se concrétisent, ils prendront néanmoins place parmi les plus grandes réalisations hydrauliques au monde en surpassant les barrages des Trois Gorges et d'Itaipu.
    Le fleuve est par contre navigable pour les vapeurs jusqu'à Iquitos, à 3 700 km de la mer, et pour les plus petits vaisseaux, sur encore 780 km jusqu'à Achual. Au-delà, les petits bateaux franchissent fréquemment le défilé du Pongo de Manse riche sur le Marañón. »
    """,  # noqa: E501
        ]
    elif gen_type == "generation" and level == "cm1":
        return [
            """
    Texte : Manchot est un nom vernaculaire désignant en français des oiseaux marins de l'hémisphère austral, incapables de voler à cause de leur adaptation à la vie aquatique. Ce terme désigne spécifiquement plusieurs espèces de la famille des Spheniscidae à laquelle appartiennent aussi les gorfous « manchots à aigrettes ».
    Les ailes des manchots, devenues inutilisables pour le vol, se seraient, par contre, merveilleusement adaptées à la nage et à la plongée : le Manchot papou peut atteindre 35 km/h à la nage (contre 9 km/h pour le meilleur nageur olympique) et le Manchot empereur peut plonger à plus de 520 m pour rechercher de la nourriture, soit le record absolu chez tous les oiseaux.
    Le cri des manchots est appelé braiement ou jabotement.
    Les différentes espèces de manchots sont souvent appelées par confusion « pingouins » dans le langage courant, à la fois à cause d'une ressemblance physique et à cause d'une ressemblance lexicale entre ce mot et la racine désignant Manchot dans la plupart des langues voisines du français.
    """,  # noqa: E501
            """
    Texte : L'Amazone (en espagnol Río Amazonas, en portugais Rio Amazonas) est un fleuve d'Amérique du Sud. Son débit moyen de 209 000 m3/s2 est de loin le plus élevé de tous les fleuves de la planète et équivaut au volume cumulé des six fleuves qui le suivent immédiatement dans l'ordre des débits. Avec environ 6 500 km, c'est le plus long fleuve de la Terre avec le Nil. L'Amazone est aussi le plus grand fleuve par l'immensité de son bassin. Il draine une surface de 6 112 000 km² (sans le Tocantins) soit 40 % de l'Amérique du Sud et l'équivalent d'une fois et demie la surface de l'Union européenne (le Congo, deuxième fleuve pour la superficie de son bassin atteint seulement 3,8 millions de km²). Le bassin  prend sa source dans les Andes et se jette dans l'océan Atlantique. Après avoir traversé le Pérou, la Colombie et le Brésil, il se jette dans l'océan Atlantique au niveau de l'équateur. Son réseau hydrographique compte plus de 1000 cours d'eau. L'Amazone est à lui seul à l'origine de 18% du volume total d'eau douce déversée dans les océans du monde. Ses deux principaux affluents, le Madeira et le Rio Negro font eux-mêmes partie des 10 plus importants cours d'eau du monde par leurs débits (32 000 et 29 300 m3/s), et le 3e (rio Japura, 18 600 m3/s) rivalise avec le Mississippi.
    La démesure de l'Amazone s'apprécie aussi en constatant qu'aucun pont ni barrage ne le franchit sur des milliers de kilomètres (la traversée se fait en bac ou ferry), et qu'il faut remonter très haut sur ses deux formateurs Marañón et Ucayali pour trouver de tels aménagements. Tout s'y oppose: la largeur du fleuve, sa profondeur, sa puissance, la multitude d'îles et de bras fluviaux, les berges inondées plusieurs mois par an et remodelées à chaque crue. La technique d'aujourd'hui ne permet pas de s'affranchir de telles difficultés. C'est pourquoi les actuels projets de barrages ne concernent que les affluents (rio Madeira, rio Xingu). S'ils se concrétisent, ils prendront néanmoins place parmi les plus grandes réalisations hydrauliques au monde en surpassant les barrages des Trois Gorges et d'Itaipu.
    Le fleuve est par contre navigable pour les vapeurs jusqu'à Iquitos, à 3 700 km de la mer, et pour les plus petits vaisseaux, sur encore 780 km jusqu'à Achual. Au-delà, les petits bateaux franchissent fréquemment le défilé du Pongo de Manse riche sur le Marañón.
    """,  # noqa: E501
        ]

    elif gen_type == "continuation" and level == "ce1":
        return [
            """
    Extrait : « Un manchot est un oiseau marin palmipède vivant dans l'hémisphère sud. »
    Suite : « Il est souvent confondu avec le pingouin (un pingouin sait voler). Cette confusion vient parfois d'une mauvaise traduction de l'anglais. Le mot penguin en anglais signifie manchot et non pingouin est ce qui s'appelle un faux-ami.
    Il mange du poisson, ne sait pas voler (il a des moignons d'ailes), mais peut nager dans les eaux gelées.
    Sur les dix-sept espèces de manchot existant sur notre planète, le manchot empereur est le plus grand. Comme chez tous les manchots, le plumage noir et blanc de l'empereur lui donne l'air d'être toujours habillé en smoking. Le manchot empereur se distingue facilement des autres espèces grâce à ses taches jaune vif sur la tête, le cou et le bec. »
    """,  # noqa: E501
            """
    Extrait : « L'Amazone est l'un des deux plus longs fleuves sur Terre (environ 7 000 km), avec le Nil en Afrique. Il se trouve en Amérique du Sud : il prend sa source dans la cordillère des Andes, près de la côte est, au Pérou, et se jette dans l'océan Atlantique, au nord du Brésil. »
    Suite : « Le nom Amazone lui a été donné par l'explorateur espagnol Orellana, qui vers 1540, a combattu sur les rives du fleuve, des Indiens aux cheveux longs (qu'il a assimilé aux Amazones, guerrières de l'Antiquité grecque).
    Alimentée par les pluies équatoriales et disposant du plus grand bassin hydrographique de tous les fleuves du monde, l'Amazone a le plus important débit (180 000 mètres cube par seconde à l'embouchure) de tous les fleuves. Elle transporte plus d'eau que le Mississippi, le Nil et le fleuve Chang Jiang réunis. L'Amazone est responsable de 18% du volume total d'eau douce déversée dans les océans du monde.
    L'Amazone andine est un torrent coupé de rapides et encaissé dans des gorges. Il doit descendre près de 4000 mètres de pente sur un trajet de 900 kilomètres. Dans la plaine l'importance de l'eau charriée et la faible pente obligent l'Amazone à créer des méandres qui souvent donnent des branches dérivées du fleuve. A certains endroits il atteint huit kilomètres de large. Il reçoit plus de 200 affluents au débit important mais dont les hautes eaux alternent au cours de l'année, ce qui maintient un débit considérable. L'Amazone charrie une masse considérable de débris organiques fournis par la forêt dense amazonienne. Des dépôts ont construit à l'embouchure l'île de Marajo dont la superficie est plus grande que celle de la Belgique.
    La marée atlantique remonte jusqu'à Obidos (à plus de 1000 kilomètres de l'embouchure). La vague de mascaret est redoutable à la nouvelle et à la pleine lune. L'Amazone, qui est très profonde, est navigable par de gros navires jusqu'à Manaus à 2000 kilomètres de son embouchure. L'Amazone se jette dans l'océan Atlantique par un estuaire de 300 kilomètres de large, encombré d'îles. Le débit est tel que l'eau douce pénètre jusqu'à 300 kilomètres dans l'océan. »
    """,  # noqa: E501
        ]
    elif gen_type == "generation" and level == "ce1":
        return [
            """
    Texte : Un manchot est un oiseau marin palmipède vivant dans l'hémisphère sud.
    Il est souvent confondu avec le pingouin (un pingouin sait voler). Cette confusion vient parfois d'une mauvaise traduction de l'anglais. Le mot penguin en anglais signifie manchot et non pingouin est ce qui s'appelle un faux-ami.
    Il mange du poisson, ne sait pas voler (il a des moignons d'ailes), mais peut nager dans les eaux gelées.
    Sur les dix-sept espèces de manchot existant sur notre planète, le manchot empereur est le plus grand. Comme chez tous les manchots, le plumage noir et blanc de l'empereur lui donne l'air d'être toujours habillé en smoking. Le manchot empereur se distingue facilement des autres espèces grâce à ses taches jaune vif sur la tête, le cou et le bec.
    """,  # noqa: E501
            """
    Texte : L'Amazone est l'un des deux plus longs fleuves sur Terre (environ 7 000 km), avec le Nil en Afrique. Il se trouve en Amérique du Sud : il prend sa source dans la cordillère des Andes, près de la côte est, au Pérou, et se jette dans l'océan Atlantique, au nord du Brésil. Le nom Amazone lui a été donné par l'explorateur espagnol Orellana, qui vers 1540, a combattu sur les rives du fleuve, des Indiens aux cheveux longs (qu'il a assimilé aux Amazones, guerrières de l'Antiquité grecque).
    Alimentée par les pluies équatoriales et disposant du plus grand bassin hydrographique de tous les fleuves du monde, l'Amazone a le plus important débit (180 000 mètres cube par seconde à l'embouchure) de tous les fleuves. Elle transporte plus d'eau que le Mississippi, le Nil et le fleuve Chang Jiang réunis. L'Amazone est responsable de 18% du volume total d'eau douce déversée dans les océans du monde.
    L'Amazone andine est un torrent coupé de rapides et encaissé dans des gorges. Il doit descendre près de 4000 mètres de pente sur un trajet de 900 kilomètres. Dans la plaine l'importance de l'eau charriée et la faible pente obligent l'Amazone à créer des méandres qui souvent donnent des branches dérivées du fleuve. A certains endroits il atteint huit kilomètres de large. Il reçoit plus de 200 affluents au débit important mais dont les hautes eaux alternent au cours de l'année, ce qui maintient un débit considérable. L'Amazone charrie une masse considérable de débris organiques fournis par la forêt dense amazonienne. Des dépôts ont construit à l'embouchure l'île de Marajo dont la superficie est plus grande que celle de la Belgique.
    La marée atlantique remonte jusqu'à Obidos (à plus de 1000 kilomètres de l'embouchure). La vague de mascaret est redoutable à la nouvelle et à la pleine lune. L'Amazone, qui est très profonde, est navigable par de gros navires jusqu'à Manaus à 2000 kilomètres de son embouchure. L'Amazone se jette dans l'océan Atlantique par un estuaire de 300 kilomètres de large, encombré d'îles. Le débit est tel que l'eau douce pénètre jusqu'à 300 kilomètres dans l'océan.
    """,  # noqa: E501
        ]

    return []


def get_prompt(gen_type: str, text_type: str, level: str, text: str) -> str:
    if gen_type not in ["continuation", "generation"]:
        raise ValueError(
            f"gen_type must be one of ['continuation', 'generation'], got {gen_type}"
        )

    if text_type not in ["literature", "scientific"]:
        raise ValueError(
            f"text_type must be one of ['literature', 'scientific'], got {text_type}"
        )

    if level not in ["ce1", "cm1"]:
        raise ValueError(f"level must be one of ['ce1', 'cm1'], got {level}")

    is_cont = gen_type == "continuation"
    text_type_prompt = "littéraire" if text_type == "literature" else "scientifique"
    instr = (
        "Écris la suite de l'extrait."
        if is_cont
        else "Écris un texte similaire en termes de contenu et de longueur."
    )
    examples = get_examples(gen_type, text_type, level)

    prompt = f"""
  Voici un {"extrait de " if is_cont else ""}texte {text_type_prompt} destiné à des enfants de niveau {level.upper()}. {instr}

  Veille à ce que le texte généré soit simple et compréhensible pour des enfants de niveau {level.upper()}.

  Génère uniquement le texte et rien d'autre.

  <example>
  {examples[0]}
  </example>

  <example>
  {examples[1]}
  </example>

  ___

  {"Extrait :" if is_cont else "Texte :"} {text} \n {"Suite :" if is_cont else ""}
  """  # noqa: E501

    return prompt
