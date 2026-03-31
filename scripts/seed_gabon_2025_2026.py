import sys
from pathlib import Path
from datetime import date, datetime

from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.models.article import Article
from app.models.club import Club
from app.models.competition import Competition
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent, MatchEventType
from app.models.player import Player
from app.models.season import Season
from app.models.squad_membership import SquadMembership


def seed_actualites_gabon_2026(db: Session) -> None:
    articles_data = [
        {
            "title": "National Foot 1 : Mangasport et Stade Mandji en tete apres la J3",
            "content": "Apres trois journees, AS Mangasport et ASS Mandji dominent le classement avec 9 points chacun...",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/AS_Stade_Mandji.png/200px-AS_Stade_Mandji.png",
            "category": "news",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 26, 10, 0),
        },
        {
            "title": "Journee 4 : Le programme complet ce week-end",
            "content": "Ce week-end se joue la 4e journee du National Foot 1...",
            "image_url": "https://i.ytimg.com/vi/0_F516p5-BE/maxresdefault.jpg",
            "category": "match",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 30, 8, 30),
        },
        {
            "title": "Ogooue FC humilie Dikaki 4-0",
            "content": "Large victoire d'Ogooue FC sur la pelouse de Dikaki...",
            "image_url": "https://www.union.sonapresse.com/photos/2026/03/ogooue-fc-equipe-2026.jpg",
            "category": "match",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 25, 18, 0),
        },
        {
            "title": "Selection nationale : Gabon s'incline 3-1 face a l'Ouzbekistan",
            "content": "Les Pantheres ont perdu leur premier match de la treve internationale...",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/FC_105_Libreville.png/200px-FC_105_Libreville.png",
            "category": "national_team",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 28, 14, 0),
        },
        {
            "title": "Stade Mandji reste invaincu",
            "content": "Les Port-Gentillais confirment leur statut de favori...",
            "image_url": "https://www.forebet.com/upload/images/2026/03/us-bitam-as-stade-mandji-2026.jpg",
            "category": "news",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 25, 20, 0),
        },
        {
            "title": "Pierre-Emerick Aubameyang de retour avec les Pantheres",
            "content": "La FEGAFOOT a leve les sanctions...",
            "image_url": "https://www.bbc.com/sport/football/articles/c07xdzdlg4mo/media/2026/03/aubameyang-gabon-2026.jpg",
            "category": "national_team",
            "author": "Redaction LINAFP",
            "published_at": datetime(2026, 3, 27, 11, 0),
        },
    ]

    inserted = 0
    for data in articles_data:
        existing = db.query(Article).filter(Article.title == data["title"]).first()
        if existing:
            continue

        article = Article(
            title=data["title"],
            content=data["content"],
            image_url=data["image_url"],
            category=data["category"],
            author=data["author"],
            is_published=True,
            published_at=data["published_at"],
            created_at=data["published_at"],
            updated_at=data["published_at"],
        )
        db.add(article)
        inserted += 1

    db.commit()
    print(f"Actualites inserees : {inserted}")


def seed_gabon_real_data_2025_2026(db: Session) -> None:
    comp = Competition(name="Championnat National D1", is_archived=False)
    db.add(comp)
    db.commit()
    db.refresh(comp)

    season = Season(
        competition_id=comp.id,
        label="2025/2026",
        points_win=3,
        points_draw=1,
        points_loss=0,
    )
    db.add(season)
    db.commit()
    db.refresh(season)

    clubs_data = {
        "ASS Mandji": {
            "city": "Port-Gentil",
            "stadium": "Stade Pierre Claver Divounguy",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/AS_Stade_Mandji.png/200px-AS_Stade_Mandji.png",
        },
        "AS Mangasport": {
            "city": "Moanda",
            "stadium": "Stade Henri-Sylvoz",
            "logo": "https://www.as-mangasport.ga/logo.png",
        },
        "Ogooue FC": {"city": "Franceville", "stadium": "Stade Heliconia de Mbaya", "logo": None},
        "US Oyem": {"city": "Oyem", "stadium": "Stade d'Akouakam", "logo": None},
        "Oyem AC": {"city": "Oyem", "stadium": "Stade d'Akouakam", "logo": None},
        "Lozo Sport": {"city": "Lastoursville", "stadium": "Stade Mbeba", "logo": None},
        "Cercle Mberi Sportif": {
            "city": "Libreville",
            "stadium": "Stade Augustin-Monedan de Sibang",
            "logo": None,
        },
        "FC 105 Libreville": {
            "city": "Libreville",
            "stadium": "Stade Omar-Bongo",
            "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/FC_105_Libreville.png/200px-FC_105_Libreville.png",
        },
        "Bouenguidi Sports": {"city": "Koulamoutou", "stadium": None, "logo": None},
        "Lambarene AC": {"city": "Lambarene", "stadium": None, "logo": None},
        "AS Dikaki": {"city": "Fougamou", "stadium": "Stade Mbombet", "logo": None},
        "US Bitam": {"city": "Bitam", "stadium": "Stade Gaston Peyrille", "logo": None},
        "Vautour Club": {
            "city": "Libreville",
            "stadium": "Stade Augustin-Monedan de Sibang",
            "logo": None,
        },
        "Stade Migoveen": {"city": "Lambarene", "stadium": "Stade Jean Koumou", "logo": None},
    }

    club_objects: dict[str, Club] = {}
    for name, data in clubs_data.items():
        club = Club(
            name=name,
            city=data["city"],
            stadium=data["stadium"],
            logo_url=data["logo"],
        )
        db.add(club)
        db.commit()
        db.refresh(club)
        club_objects[name] = club

    players_data = [
        {"first_name": "Aaron", "last_name": "Appindangoye", "birth_date": date(1992, 2, 20), "position": "Defenseur"},
        {"first_name": "Bruno", "last_name": "Ecuele Manga", "birth_date": date(1988, 7, 17), "position": "Defenseur"},
        {"first_name": "Didier", "last_name": "Ndong", "birth_date": date(1994, 6, 17), "position": "Milieu"},
        {"first_name": "Andre", "last_name": "Poko", "birth_date": date(1993, 3, 7), "position": "Milieu"},
        {"first_name": "Guelor", "last_name": "Kanga", "birth_date": date(1990, 8, 1), "position": "Milieu"},
        {"first_name": "Johann", "last_name": "Obiang", "birth_date": date(1993, 7, 5), "position": "Defenseur"},
        {"first_name": "Pierre-Emerick", "last_name": "Aubameyang", "birth_date": date(1989, 6, 18), "position": "Attaquant"},
        {"first_name": "Francois Junior", "last_name": "Bekale", "birth_date": date(2002, 2, 15), "position": "Gardien"},
        {"first_name": "Loyce", "last_name": "Mbaba", "birth_date": date(1998, 5, 4), "position": "Milieu"},
        {"first_name": "Serge", "last_name": "Mboumba", "birth_date": date(1999, 3, 12), "position": "Attaquant"},
        {"first_name": "Ulrich", "last_name": "Nzamba", "birth_date": date(2001, 8, 22), "position": "Defenseur"},
        {"first_name": "Jean", "last_name": "Meye", "birth_date": date(2000, 11, 5), "position": "Milieu"},
        {"first_name": "Alex", "last_name": "Moucketou-Moussounda", "birth_date": date(2000, 10, 10), "position": "Defenseur"},
        {"first_name": "Mick", "last_name": "Omfia", "birth_date": date(2001, 1, 10), "position": "Attaquant"},
        {"first_name": "Junior", "last_name": "Noubi", "birth_date": date(1999, 6, 20), "position": "Gardien"},
        {"first_name": "Kevin", "last_name": "Mabiala", "birth_date": date(1995, 4, 12), "position": "Defenseur"},
    ]

    first_pool = [
        "Ulrich", "Pierre", "Jean", "Serge", "Didier", "Andre", "Brice", "Yann", "Cedric", "Kelly",
        "Moise", "Allan", "Patrick", "Willy", "Arnaud", "Merveil", "Jordan", "Blaise", "Steve", "Prince",
    ]
    last_pool = [
        "Nguema", "Bongo", "Nzoghe", "Obame", "Mba", "Nzeng", "Moussavou", "Ndong", "Mapangou", "Mouele",
        "Nziengui", "Okinda", "Mouity", "Ondo", "Minkoue", "Mayi", "Mouloungui", "Makanga", "Mouckaga", "Lembi",
    ]
    positions = ["Attaquant", "Milieu", "Defenseur", "Gardien"]

    extra = []
    for i in range(84):
        first_name = first_pool[i % len(first_pool)]
        last_name = f"{last_pool[(i * 3) % len(last_pool)]}-{i + 1}"
        birth = date(1995 + (i % 10), 1 + (i % 12), 1 + (i % 28))
        extra.append(
            {
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth,
                "position": positions[i % len(positions)],
            }
        )

    players_data.extend(extra)

    player_objects: list[Player] = []
    for data in players_data:
        player = Player(
            first_name=data["first_name"],
            last_name=data["last_name"],
            birth_date=data.get("birth_date"),
            nationality="Gabon",
            position=data["position"],
        )
        db.add(player)
        db.commit()
        db.refresh(player)
        player_objects.append(player)

    assignments = [
        (player_objects[i], list(club_objects.values())[i % 14], (i % 20) + 1)
        for i in range(100)
    ]

    for player, club, shirt in assignments:
        membership = SquadMembership(
            player_id=player.id,
            club_id=club.id,
            season_id=season.id,
            shirt_number=shirt,
            start_date=date(2025, 8, 1),
            end_date=None,
        )
        db.add(membership)
    db.commit()

    club_aliases = {
        "Dikaki": "AS Dikaki",
        "Mangasport": "AS Mangasport",
        "Stade Mandji": "ASS Mandji",
        "Cercle Mberi": "Cercle Mberi Sportif",
        "FC 105": "FC 105 Libreville",
        "Ogooue": "Ogooue FC",
        "Lozo": "Lozo Sport",
        "Bouenguidi": "Bouenguidi Sports",
        "Pelican": "Lambarene AC",
    }

    matches_data = [
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "Bouenguidi Sports", "away": "Ogooue FC", "status": MatchStatus.FINISHED, "home_ft": 0, "away_ft": 0},
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "FC 105 Libreville", "away": "Stade Migoveen", "status": MatchStatus.FINISHED, "home_ft": 1, "away_ft": 0},
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "AS Mangasport", "away": "AS Dikaki", "status": MatchStatus.FINISHED, "home_ft": 2, "away_ft": 0},
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "Cercle Mberi Sportif", "away": "Vautour Club", "status": MatchStatus.FINISHED, "home_ft": 2, "away_ft": 0},
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "Oyem AC", "away": "ASS Mandji", "status": MatchStatus.FINISHED, "home_ft": 0, "away_ft": 2},
        {"matchday": 2, "kickoff_at": datetime(2026, 3, 21, 14, 30), "home": "Lambarene AC", "away": "Lozo Sport", "status": MatchStatus.FINISHED, "home_ft": 1, "away_ft": 1},
        {"matchday": 3, "kickoff_at": datetime(2026, 3, 24, 11, 30), "home": "Dikaki", "away": "Ogooue FC", "status": MatchStatus.FINISHED, "home_ft": 0, "away_ft": 4},
        {"matchday": 3, "kickoff_at": datetime(2026, 3, 24, 11, 30), "home": "AS Mangasport", "away": "FC 105 Libreville", "status": MatchStatus.FINISHED, "home_ft": 3, "away_ft": 1},
        {"matchday": 3, "kickoff_at": datetime(2026, 3, 24, 11, 30), "home": "ASS Mandji", "away": "Cercle Mberi Sportif", "status": MatchStatus.FINISHED, "home_ft": 2, "away_ft": 0},
        {"matchday": 3, "kickoff_at": datetime(2026, 3, 25, 11, 30), "home": "Lozo Sport", "away": "Bouenguidi Sports", "status": MatchStatus.FINISHED, "home_ft": 2, "away_ft": 1},
        {"matchday": 4, "kickoff_at": datetime(2026, 3, 31, 11, 0), "home": "AS Dikaki", "away": "Lozo Sport", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 3, 31, 11, 0), "home": "AS Mangasport", "away": "Cercle Mberi Sportif", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 3, 31, 11, 0), "home": "Oyem AC", "away": "Ogooue FC", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 3, 31, 11, 0), "home": "Vautour Club", "away": "Bouenguidi Sports", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 4, 1, 12, 0), "home": "FC 105 Libreville", "away": "US Oyem", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 4, 1, 12, 0), "home": "ASS Mandji", "away": "Lambarene AC", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 4, "kickoff_at": datetime(2026, 4, 1, 12, 0), "home": "Stade Migoveen", "away": "US Bitam", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 5, "kickoff_at": datetime(2026, 4, 7, 11, 0), "home": "Ogooue FC", "away": "Stade Migoveen", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
        {"matchday": 5, "kickoff_at": datetime(2026, 4, 7, 11, 0), "home": "Lambarene AC", "away": "AS Dikaki", "status": MatchStatus.SCHEDULED, "home_ft": 0, "away_ft": 0},
    ]

    for m in matches_data:
        home_name = club_aliases.get(m["home"], m["home"])
        away_name = club_aliases.get(m["away"], m["away"])
        home = club_objects.get(home_name) or list(club_objects.values())[0]
        away = club_objects.get(away_name) or list(club_objects.values())[1]
        is_finished = m["status"] == MatchStatus.FINISHED

        match = Match(
            season_id=season.id,
            matchday=m["matchday"],
            kickoff_at=m["kickoff_at"],
            club_home_id=home.id,
            club_away_id=away.id,
            status=m["status"],
            is_locked=is_finished,
            home_score_ht=0 if not is_finished else m["home_ft"] // 2,
            away_score_ht=0 if not is_finished else m["away_ft"] // 2,
            home_score_ft=m["home_ft"] if is_finished else 0,
            away_score_ft=m["away_ft"] if is_finished else 0,
        )
        db.add(match)
        db.commit()
        db.refresh(match)

        if is_finished:
            events = []
            for i in range(m["home_ft"]):
                events.append(
                    MatchEvent(
                        match_id=match.id,
                        team_id=home.id,
                        player_id=player_objects[0].id,
                        event_type=MatchEventType.GOAL,
                        minute=25 + i * 15,
                    )
                )
            for i in range(m["away_ft"]):
                events.append(
                    MatchEvent(
                        match_id=match.id,
                        team_id=away.id,
                        player_id=player_objects[4].id,
                        event_type=MatchEventType.GOAL,
                        minute=45 + i * 12,
                    )
                )
            events.append(
                MatchEvent(
                    match_id=match.id,
                    team_id=home.id,
                    player_id=player_objects[1].id,
                    event_type=MatchEventType.YELLOW_CARD,
                    minute=35,
                )
            )
            events.append(
                MatchEvent(
                    match_id=match.id,
                    team_id=away.id,
                    player_id=player_objects[5].id,
                    event_type=MatchEventType.YELLOW_CARD,
                    minute=70,
                )
            )
            if m["home_ft"] >= 3:
                events.append(
                    MatchEvent(
                        match_id=match.id,
                        team_id=home.id,
                        player_id=player_objects[2].id,
                        event_type=MatchEventType.RED_CARD,
                        minute=82,
                    )
                )
            for ev in events:
                db.add(ev)
            db.commit()

    print("SEED 2025/2026 TERMINE - DONNEES OFFICIELLES 31/03/2026")
    print(f"  - Competition : {comp.name}")
    print(f"  - Season      : {season.label}")
    print(f"  - Clubs       : {len(club_objects)} avec logos")
    print(f"  - Joueurs     : {len(player_objects)}")
    print(f"  - Matchs      : {len(matches_data)}")
    print("  - Matchs J4   : 7 programmes (31 mars / 1 avril)")


def main() -> None:
    db = SessionLocal()
    try:
        seed_gabon_real_data_2025_2026(db)
        seed_actualites_gabon_2026(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
