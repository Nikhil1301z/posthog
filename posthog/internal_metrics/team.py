import json
import secrets
from functools import lru_cache
from typing import Dict, Optional

from django.conf import settings
from django.db import transaction
from sentry_sdk.api import capture_exception

from posthog.models.dashboard import Dashboard
from posthog.models.dashboard_item import DashboardItem

NAME = "Posthog Internal Metrics"
CLICKHOUSE_DASHBOARD = {
    "name": "Clickhouse internal dashboard",
    "items": [
        {
            "name": "Number of insights loaded vs failed",
            "filters": {
                "events": [
                    {
                        "id": "$$insight_load_time",
                        "name": "insights loaded",
                        "type": "events",
                        "order": 0,
                        "properties": [{"key": "success", "type": "event", "value": ["true"], "operator": "exact"}],
                    },
                    {
                        "id": "$$insight_load_time",
                        "name": "insights loaded",
                        "type": "events",
                        "order": 1,
                        "properties": [{"key": "success", "type": "event", "value": ["false"], "operator": "exact"}],
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Insight load time",
            "filters": {
                "events": [
                    {
                        "id": "$$insight_load_time",
                        "math": "avg",
                        "name": "Load time (avg)",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$insight_load_time",
                        "math": "p90",
                        "name": "Load time (p90)",
                        "type": "events",
                        "order": 1,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$insight_load_time",
                        "math": "p95",
                        "name": "Load time (p95)",
                        "type": "events",
                        "order": 2,
                        "properties": [],
                        "math_property": "value",
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Number of insights with timeout message",
            "filters": {
                "events": [
                    {
                        "id": "$$insight_timeout",
                        "name": "insight timeout",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Clickhouse total queries",
            "filters": {
                "events": [
                    {
                        "id": "$$clickhouse_sync_execution_time",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 0,
                        "math": "total",
                    }
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Requests: query time breakdown (ms)",
            "filters": {
                "events": [
                    {
                        "id": "$$clickhouse_sync_execution_time",
                        "math": "avg",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$clickhouse_sync_execution_time",
                        "math": "p90",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 1,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$clickhouse_sync_execution_time",
                        "math": "p95",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 2,
                        "properties": [],
                        "math_property": "value",
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [{"key": "kind", "type": "event", "value": ["request"], "operator": "exact"}],
            },
        },
        {
            "name": "Clickhouse: query time total breakdown (ms)",
            "filters": {
                "events": [
                    {
                        "id": "$$clickhouse_sync_execution_time",
                        "math": "sum",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                        "math_property": "value",
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "breakdown": "table",
                "breakdown_type": "event",
                "properties": [],
            },
        },
        {
            "name": "Clickhouse mutations count",
            "filters": {
                "events": [
                    {
                        "id": "$$posthog_celery_clickhouse_table_mutations_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_mutations_count",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_mutations_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_mutations_count",
                        "type": "events",
                        "order": 1,
                        "properties": [{"key": "table", "type": "events", "value": ["events"], "operator": "exact"}],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_mutations_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_mutations_count",
                        "type": "events",
                        "order": 1,
                        "properties": [{"key": "table", "type": "events", "value": ["person"], "operator": "exact"}],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_mutations_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_mutations_count",
                        "type": "events",
                        "order": 2,
                        "properties": [
                            {"key": "table", "type": "events", "value": ["person_distinct_id"], "operator": "exact"}
                        ],
                        "math_property": "value",
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Clickhouse tables part counts",
            "filters": {
                "events": [
                    {
                        "id": "$$posthog_celery_clickhouse_table_parts_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_parts_count",
                        "type": "events",
                        "order": 0,
                        "properties": [],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_parts_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_parts_count",
                        "type": "events",
                        "order": 1,
                        "properties": [{"key": "table", "type": "events", "value": ["events"], "operator": "exact"}],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_parts_count",
                        "math": "avg",
                        "name": "$$posthog_celery_clickhouse_table_parts_count",
                        "type": "events",
                        "order": 1,
                        "properties": [{"key": "table", "type": "events", "value": ["person"], "operator": "exact"}],
                        "math_property": "value",
                    },
                    {
                        "id": "$$posthog_celery_clickhouse_table_parts_count",
                        "math": "avg",
                        "name": "$$clickhouse_sync_execution_time",
                        "type": "events",
                        "order": 2,
                        "properties": [
                            {"key": "table", "type": "events", "value": ["person_distinct_id"], "operator": "exact"}
                        ],
                        "math_property": "value",
                    },
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
        {
            "name": "Clickhouse table lag (seconds)",
            "filters": {
                "events": [
                    {
                        "id": "$$posthog_celery_clickhouse__table_lag_seconds",
                        "name": "$$posthog_celery_clickhouse__table_lag_seconds",
                        "type": "events",
                        "order": 0,
                        "math": "avg",
                        "math_property": "value",
                    }
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "breakdown": "table",
                "breakdown_type": "event",
                "properties": [],
            },
        },
        {
            "name": "Clickhouse table row counts",
            "filters": {
                "events": [
                    {
                        "id": "$$posthog_celery_clickhouse_table_row_count",
                        "name": "$$posthog_celery_clickhouse_table_row_count",
                        "type": "events",
                        "order": 0,
                        "math": "avg",
                        "math_property": "value",
                    }
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "breakdown": "table",
                "breakdown_type": "event",
                "properties": [],
            },
        },
        {
            "name": "Celery queue depth",
            "filters": {
                "events": [
                    {
                        "id": "$$posthog_celery_queue_depth",
                        "name": "$$posthog_celery_queue_depth",
                        "type": "events",
                        "order": 0,
                        "math": "avg",
                        "math_property": "value",
                    }
                ],
                "display": "ActionsLineGraph",
                "insight": "TRENDS",
                "interval": "hour",
                "date_from": "-24h",
                "properties": [],
            },
        },
    ],
    "filters": {"interval": "hour", "date_from": "-24h",},
}


@lru_cache(maxsize=1)
def get_internal_metrics_team_id() -> Optional[int]:
    from posthog.models.organization import Organization
    from posthog.models.team import Team

    if not settings.CAPTURE_INTERNAL_METRICS:
        return None

    try:
        with transaction.atomic():
            team = Team.objects.filter(organization__for_internal_metrics=True).first()

            if team is None:
                organization = Organization.objects.create(name=NAME, for_internal_metrics=True)
                team = Team.objects.create(
                    name=NAME,
                    organization=organization,
                    ingested_event=True,
                    completed_snippet_onboarding=True,
                    is_demo=True,
                )

        return team.pk
    except:
        # Ignore errors during team finding/creation.
        capture_exception()

        return None


def get_internal_metrics_dashboards() -> Dict:
    team_id = get_internal_metrics_team_id()

    if team_id is None:
        return {}

    clickhouse_dashboard = get_or_create_dashboard(team_id, CLICKHOUSE_DASHBOARD)

    return {"clickhouse": {"id": clickhouse_dashboard.id, "share_token": clickhouse_dashboard.share_token}}


def get_or_create_dashboard(team_id: int, definition: Dict) -> Dashboard:
    "Get or create a dashboard matching definition. If definition has changed, a new dashboard is created."
    description = digest(definition)
    dashboard = Dashboard.objects.filter(team_id=team_id, name=definition["name"], description=description).first()

    if dashboard is None:
        Dashboard.objects.filter(team_id=team_id, name=definition["name"]).delete()
        dashboard = Dashboard.objects.create(
            name=definition["name"],
            filters=definition["filters"],
            description=description,
            team_id=team_id,
            share_token=secrets.token_urlsafe(22),
        )

        for index, item in enumerate(definition["items"]):
            DashboardItem.objects.create(team_id=team_id, dashboard=dashboard, order=index, **item)

    return dashboard


def digest(d: Dict) -> str:
    return str(hash(json.dumps(d, sort_keys=True)))
