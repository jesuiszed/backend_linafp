"""initial schema

Revision ID: 20260328_0001
Revises:
Create Date: 2026-03-28 19:15:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260328_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "competitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_competitions_id"), "competitions", ["id"], unique=False)

    op.create_table(
        "clubs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("stadium", sa.String(length=120), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_clubs_id"), "clubs", ["id"], unique=False)

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(length=60), nullable=True),
        sa.Column("position", sa.String(length=40), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_players_id"), "players", ["id"], unique=False)

    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("competition_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("points_win", sa.Integer(), nullable=False),
        sa.Column("points_draw", sa.Integer(), nullable=False),
        sa.Column("points_loss", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["competition_id"], ["competitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("competition_id", "label", name="uq_season_competition_label"),
    )
    op.create_index(op.f("ix_seasons_id"), "seasons", ["id"], unique=False)

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("matchday", sa.Integer(), nullable=False),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stadium", sa.String(length=120), nullable=True),
        sa.Column("club_home_id", sa.Integer(), nullable=False),
        sa.Column("club_away_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("SCHEDULED", "LIVE", "FINISHED", "POSTPONED", "CANCELED", name="matchstatus"), nullable=False),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("home_score_ht", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("away_score_ht", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("home_score_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("away_score_ft", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("club_home_id <> club_away_id", name="ck_match_distinct_clubs"),
        sa.ForeignKeyConstraint(["club_away_id"], ["clubs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["club_home_id"], ["clubs.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "matchday", "club_home_id", "club_away_id", name="uq_match_schedule"),
    )
    op.create_index(op.f("ix_matches_id"), "matches", ["id"], unique=False)

    op.create_table(
        "squad_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("club_id", sa.Integer(), nullable=False),
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("shirt_number", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_squad_memberships_id"), "squad_memberships", ["id"], unique=False)

    op.create_table(
        "match_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("related_player_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.Enum("GOAL", "YELLOW_CARD", "RED_CARD", "SUBSTITUTION", name="matcheventtype"), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.CheckConstraint("minute >= 0 AND minute <= 130", name="ck_match_event_minute_range"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["related_player_id"], ["players.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["clubs.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_match_events_id"), "match_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_match_events_id"), table_name="match_events")
    op.drop_table("match_events")

    op.drop_index(op.f("ix_squad_memberships_id"), table_name="squad_memberships")
    op.drop_table("squad_memberships")

    op.drop_index(op.f("ix_matches_id"), table_name="matches")
    op.drop_table("matches")

    op.drop_index(op.f("ix_seasons_id"), table_name="seasons")
    op.drop_table("seasons")

    op.drop_index(op.f("ix_players_id"), table_name="players")
    op.drop_table("players")

    op.drop_index(op.f("ix_clubs_id"), table_name="clubs")
    op.drop_table("clubs")

    op.drop_index(op.f("ix_competitions_id"), table_name="competitions")
    op.drop_table("competitions")

    op.execute("DROP TYPE IF EXISTS matcheventtype")
    op.execute("DROP TYPE IF EXISTS matchstatus")
